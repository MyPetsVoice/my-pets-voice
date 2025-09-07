from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_text_splitters import RecursiveJsonSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from config import Config
from typing import List, Dict, Any
import json
from pathlib import Path
import os
import re
import logging

logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self):
        self.documents_path = Config.DOCUMENTS_PATH
        self.vector_db = Config.VECTOR_DB
        self.collection_name = Config.COLLECTION_NAME
        self.store = None
        self.embedding = OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY)


    def initialize_vector_db(self):
        if not os.path.exists(self.vector_db):
            os.makedirs(self.vector_db, exist_ok=True)
            logger.info("벡터 DB 디렉토리가 없어서 새로 생성합니다.")
            return self.create_vector_db()
        
        # 기존 컬렉션이 있는지 확인
        try:
            self.store = Chroma(collection_name=self.collection_name, 
                               embedding_function=self.embedding, 
                               persist_directory=self.vector_db)
            
            # 컬렉션이 비어있는지 확인
            collection_count = self.store._collection.count()
            if collection_count == 0:
                logger.info("기존 벡터 DB가 비어있어서 새로 생성합니다.")
                return self.create_vector_db()
            else:
                logger.info(f"기존 벡터 DB를 로딩했습니다. (문서 수: {collection_count})")
                return self.store
                
        except Exception as e:
            logger.warning(f"기존 벡터 DB 로딩 중 오류 발생: {e}")
            logger.info("새로운 벡터 DB를 생성합니다.")
            return self.create_vector_db()

    def create_vector_db(self):
        logger.info("새로운 벡터 DB 생성을 시작합니다.")
        
        # 문서로딩 및 청킹
        logger.info("문서들을 로딩하고 청킹합니다.")
        all_documents = self.load_documents()
        logger.info(f"총 {len(all_documents)}개의 문서 청크를 로딩했습니다.")

        # 임베딩 및 벡터 DB 생성
        logger.info("임베딩을 생성하고 벡터 DB에 저장합니다.")
        self.store = Chroma.from_documents(all_documents, 
                                           embedding_function=self.embedding, 
                                           collection_name=self.collection_name, 
                                           persist_directory=self.vector_db)
        
        logger.info("벡터 DB 생성이 완료되었습니다.")
        return self.store
    
    def load_documents(self):
        # 해당 경로에 있는 각  폴더의 각 문서 리스트 싹 다 가져오기
        documents_path = Path(self.documents_path)
        all_documents = []

        # 각 문서 타입별로 구분하기 json, markdown
        md_files = documents_path.glob('**/*.md')
        json_files = documents_path.glob('**/*.json')

        # 각 문서 타입별로 청킹하기
        for md_file in md_files:
            docs = self.load_markdown(md_file) # 하나의 파일을 분할한 리스트
            all_documents.extend(docs)

        for json_file in json_files:
            docs = self.load_json(json_file)
            all_documents.extend(docs)

        return all_documents

    def load_markdown(self, file_path: Path):        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 문서 레벨 메타데이터 추출
        doc_metadata = self.extract_document_metadata(content)

        headers_to_split_on = [
            ("#", "title"),
            ("##", "subtitle")
        ]

        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)

        # 헤더 기준으로 섹션 분할
        md_header_splits = markdown_splitter(content)

        for section in md_header_splits:
            # YAML 메타데이터 블록 제거 후 벡터화할 콘텐츠 정리
            section.page_content = self.remove_metadata_blocks(section.page_content)
            section.metadata.update(doc_metadata)
            section.metadata.update({'source_file': file_path.name,
                                     'file_path': str(file_path)})

        return md_header_splits
        
    def extract_document_metadata(self, content):
        metadata = {}

        # YAML 프론트매터 추출
        yaml_pattern = r'^---\s*\nmetadata:\s*\n(.*?)\n---'
        match = re.search(yaml_pattern, content, re.MULTILINE | re.DOTALL)

        if match:
            yaml_content = match.group(1)
            # 파싱
            for line in yaml_content.split('\n'):
                line = line.strip()
                if ':' in line and not line.startswith('-'):
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'') # 양쪽 공백, 따옴표 제거

                    if key == 'categories':
                        value = self.parse_yaml_list(value)

                    metadata[key] = value
        
        return metadata
    

    def parse_yaml_list(self, value: str) -> List[str]:
        if value.startswith('[') and value.endswith(']'):
            items = value[1:-1].split(',')
            return [item.strip().strip('"\'') for item in items]
        return [value]
    

    def load_json(self, file_path: Path):        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        documents = []
        
        json_splitter = RecursiveJsonSplitter(max_chunk_size=1000)
        
        # 의약품 데이터 구조 처리
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'text' in item:
                    # text 필드를 주요 콘텐츠로 사용
                    content = item.get('text', '')
                    
                    # 메타데이터 구성
                    metadata = {
                        'file_path': str(file_path),
                        'data_type': 'medication',
                        "source_url": "https://medi.qia.go.kr/searchMedicine",
                        "source_title": "동물용의약품ㆍ의약외품 정보검색",
                        "publisher": "농림축산검역본부 동물용의약품 아지(AZ)트"
                    }
                    
                    # 기존 메타데이터가 있으면 병합
                    if 'metadata' in item:
                        item_metadata = item['metadata']
                        if isinstance(item_metadata, dict):
                            metadata.update(item_metadata)
                    
                    # id가 있으면 추가
                    if 'id' in item:
                        metadata['document_id'] = item['id']
                    
                    # Document 객체 생성
                    doc = json_splitter.create_document(chunk=content, metadata=metadata)
                    documents.append(doc)
        
        return documents

    def remove_metadata_blocks(self, content: str) -> str:
        """YAML 메타데이터 블록을 제거하고 깨끗한 콘텐츠만 반환"""
        # YAML 프론트매터 제거
        yaml_pattern = r'^---\s*\nmetadata:\s*\n.*?\n---\s*\n'
        cleaned_content = re.sub(yaml_pattern, '', content, flags=re.MULTILINE | re.DOTALL)
        
        # 추가적인 정리 (빈 줄 정리 등)
        cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_content)
        cleaned_content = cleaned_content.strip()
        
        return cleaned_content





# 테스트용 - Flask 앱에서는 create_app()에서 초기화됨
# if __name__ == '__main__':
#     service = VectorStoreService()
#     service.initialize_vector_db()








  