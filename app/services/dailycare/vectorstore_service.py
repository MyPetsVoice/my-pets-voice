import os
import re
import json
import time
import pickle
import hashlib
import logging
from flask import current_app as app

import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import tiktoken
from collections import Counter
import numpy as np

from config import Config


logger = logging.getLogger(__name__)

class CachedOpenAIEmbeddings(Embeddings):
    """캐시를 지원하는 OpenAI 임베딩 래퍼"""
    
    def __init__(self, openai_embeddings: OpenAIEmbeddings, cache_dir: str):
        self.openai_embeddings = openai_embeddings
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_key(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()
    
    def load_cache(self, text: str) -> Optional[List[float]]:
        cache_file = os.path.join(self.cache_dir, f"{self.get_cache_key(text)}.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"임베딩 캐시 로드 실패: {e}")
        return None
    
    def save_cache(self, text: str, embedding: List[float]):
        cache_file = os.path.join(self.cache_dir, f"{self.get_cache_key(text)}.pkl")
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(embedding, f)
        except Exception as e:
            logger.warning(f"임베딩 캐시 저장 실패: {e}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """문서들을 임베딩 (캐시 활용)"""
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        # 캐시에서 로드 시도
        for i, text in enumerate(texts):
            cached_embedding = self.load_cache(text)
            if cached_embedding is not None:
                embeddings.append(cached_embedding)
                logger.debug(f"캐시에서 임베딩 로드: {text[:50]}...")
            else:
                embeddings.append(None)  # 플레이스홀더
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # 캐시에 없는 텍스트들만 OpenAI API 호출
        if uncached_texts:
            logger.info(f"새로운 임베딩 생성: {len(uncached_texts)}개 텍스트")
            new_embeddings = self.openai_embeddings.embed_documents(uncached_texts)
            
            # 새 임베딩을 결과에 삽입하고 캐시에 저장
            for idx, new_embedding in zip(uncached_indices, new_embeddings):
                embeddings[idx] = new_embedding
                self.save_cache(texts[idx], new_embedding)
        
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """쿼리를 임베딩 (캐시 활용)"""
        cached_embedding = self.load_cache(text)
        if cached_embedding is not None:
            logger.debug(f"캐시에서 쿼리 임베딩 로드: {text[:50]}...")
            return cached_embedding
        
        logger.debug(f"새 쿼리 임베딩 생성: {text[:50]}...")
        embedding = self.openai_embeddings.embed_query(text)
        self.save_cache(text, embedding)
        return embedding

class VectorStoreService:
    def __init__(self, persist_directory: str = "./vector_db"):
        self.documents_path = Path(Config.DOCUMENTS_PATH)
        self.vector_db = Path(Config.VECTOR_DB)
        self.persist_directory = persist_directory
        
        # 멀티 콜렉션 설정
        self.collections = {
            'general_guides': 'mypetsvoice_general_guides',    # 일반 가이드
            'medications': 'mypetsvoice_medications'           # 의약품 정보
        }
        
        # 각 콜렉션별 스토어
        self.stores: Dict[str, Optional[Chroma]] = {
            'general_guides': None,
            'medications': None
        }
        
        # 캐시를 지원하는 임베딩 래퍼 생성
        openai_embeddings = OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY)
        self.cache_dir = os.path.join(os.path.dirname(str(self.vector_db)), "embedding_cache")
        self.embedding = CachedOpenAIEmbeddings(openai_embeddings, self.cache_dir)

        logger.info(f"VectorStoreService initialized. documents_path={self.documents_path}, vector_db={self.vector_db}")

    # -------------------------
    # Public: initialize DB
    # -------------------------
    def initialize_vector_db(self) -> Dict[str, Optional[Chroma]]:
        """
        멀티 콜렉션 벡터 DB 초기화
        """
        logger.info("멀티 콜렉션 벡터 스토어 초기화 시작...")
        logger.info(f"문서 경로: {self.documents_path}")
        logger.info(f"벡터 DB 경로: {self.vector_db}")
        
        # 문서 경로 검증
        if not self.documents_path.exists():
            logger.error(f"문서 경로가 존재하지 않습니다: {self.documents_path}")
            return self.stores
        
        try:
            # ensure vector_db exists
            if not self.vector_db.exists():
                self.vector_db.mkdir(parents=True, exist_ok=True)
                logger.info("벡터 DB 디렉토리 생성")
            
            # 각 콜렉션별 초기화
            for collection_type, collection_name in self.collections.items():
                logger.info(f"{collection_type} 콜렉션 초기화 중...")
                
                try:
                    # 기존 콜렉션 로드 시도
                    store = Chroma(
                        collection_name=collection_name,
                        embedding_function=self.embedding,
                        persist_directory=str(self.vector_db),
                    )
                    
                    # 건강 체크
                    count = store._collection.count()
                    if count == 0:
                        logger.info(f"{collection_type} 콜렉션이 비어있어서 새로 생성합니다.")
                        store = self.create_collection_vector_db(collection_type)
                    else:
                        logger.info(f"{collection_type} 콜렉션 로딩 성공 (문서 수: {count})")
                    
                    self.stores[collection_type] = store
                    
                except Exception as e:
                    logger.warning(f"{collection_type} 콜렉션 로딩 실패: {e}")
                    logger.info(f"{collection_type} 콜렉션을 새로 생성합니다.")
                    self.stores[collection_type] = self.create_collection_vector_db(collection_type)

            return self.stores

        except Exception as e:
            logger.error(f"멀티 콜렉션 초기화 중 치명적 오류: {e}", exc_info=True)
            return self.stores

    def create_collection_vector_db(self, collection_type: str) -> Optional[Chroma]:
        """
        특정 타입의 콜렉션을 생성
        """
        logger.info(f"{collection_type} 콜렉션 생성 시작...")
        
        if collection_type == 'general_guides':
            documents = self.load_general_guide_documents()
        elif collection_type == 'medications':
            documents = self.load_medication_documents()
        else:
            logger.error(f"알 수 없는 콜렉션 타입: {collection_type}")
            return None
        
        if not documents:
            logger.error(f"{collection_type}에 해당하는 문서가 없습니다.")
            return None
        
        return self._create_chroma_store(documents, self.collections[collection_type])

    def load_general_guide_documents(self) -> List[Document]:
        """일반 가이드 문서들만 로드 (.md 파일)"""
        documents: List[Document] = []
        
        md_files = list(self.documents_path.glob("**/*.md"))
        logger.info(f"일반 가이드 Markdown 파일 수: {len(md_files)}")
        
        for md_file in md_files:
            try:
                docs = self.load_markdown(md_file)
                # 메타데이터에 컬렉션 타입 추가
                for doc in docs:
                    doc.metadata['collection_type'] = 'general_guide'
                documents.extend(docs)
            except Exception as e:
                logger.warning(f"일반 가이드 파일 처리 실패 ({md_file}): {e}")
        
        logger.info(f"일반 가이드 총 {len(documents)}개 문서 청크 로딩 완료")
        return documents

    def load_medication_documents(self) -> List[Document]:
        """의약품 문서들만 로드 (.json 파일)"""
        documents: List[Document] = []
        
        json_files = list(self.documents_path.glob("**/*.json"))
        logger.info(f"의약품 JSON 파일 수: {len(json_files)}")
        
        for json_file in json_files:
            try:
                docs = self.load_json(json_file)
                # 메타데이터에 컬렉션 타입 추가
                for doc in docs:
                    doc.metadata['collection_type'] = 'medication'
                documents.extend(docs)
            except Exception as e:
                logger.warning(f"의약품 파일 처리 실패 ({json_file}): {e}")
        
        logger.info(f"의약품 총 {len(documents)}개 문서 청크 로딩 완료")
        return documents

    def _create_chroma_store(self, documents: List[Document], collection_name: str) -> Optional[Chroma]:
        """공통 Chroma 스토어 생성 함수"""
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        BATCH_SIZE = 50   # 배치 크기 감소 (rate limiting 대응)
        MAX_TOKENS_PER_BATCH = 50_000  # 토큰 수 감소
        DELAY_BETWEEN_BATCHES = 2  # 배치 간 2초 대기
        encoder = tiktoken.get_encoding("cl100k_base")

        store = None
        batch_texts, batch_metadatas = [], []
        token_count = 0

        for i, (text, metadata) in enumerate(zip(texts, metadatas)):
            text_tokens = len(encoder.encode(text))
            
            if token_count + text_tokens > MAX_TOKENS_PER_BATCH or len(batch_texts) >= BATCH_SIZE:
                try:
                    if store is None:
                        logger.info(f"{collection_name} 첫 배치({i-len(batch_texts)}~{i})로 생성")
                        store = Chroma.from_texts(
                            texts=batch_texts,
                            embedding=self.embedding,
                            metadatas=batch_metadatas,
                            persist_directory=str(self.vector_db),
                            collection_name=collection_name
                        )
                    else:
                        logger.info(f"{collection_name} 추가 배치({i-len(batch_texts)}~{i}) 저장")
                        store.add_texts(
                            texts=batch_texts,
                            metadatas=batch_metadatas,
                        )
                    
                    batch_texts, batch_metadatas = [], []
                    token_count = 0
                    
                    # Rate limiting 대응을 위한 대기
                    time.sleep(DELAY_BETWEEN_BATCHES)
                    
                except Exception as e:
                    logger.error(f"{collection_name} 배치 {i//BATCH_SIZE} 임베딩 실패: {e}")
                    batch_texts, batch_metadatas = [], []
                    token_count = 0
                    continue

            batch_texts.append(text)
            batch_metadatas.append(metadata)
            token_count += text_tokens

        # 남은 배치 처리
        if batch_texts:
            try:
                if store is None:
                    logger.info(f"{collection_name} 마지막 배치로 생성")
                    store = Chroma.from_texts(
                        texts=batch_texts,
                        embedding=self.embedding,
                        metadatas=batch_metadatas,
                        persist_directory=str(self.vector_db),
                        collection_name=collection_name
                    )
                else:
                    logger.info(f"{collection_name} 마지막 배치 저장")
                    store.add_texts(
                        texts=batch_texts,
                        metadatas=batch_metadatas,
                    )
                    
            except Exception as e:
                logger.error(f"{collection_name} 마지막 배치 임베딩 실패: {e}")

        if store:
            logger.info(f"{collection_name} 콜렉션 생성 완료 (총 {len(documents)}개 문서)")
        else:
            logger.error(f"{collection_name} 콜렉션 생성 실패")

        return store

    def create_vector_db(self):
        all_documents = self.load_documents()
        if not all_documents:
            logger.error("문서가 없어 벡터 DB를 생성할 수 없습니다.")
            return None

        texts = [doc.page_content for doc in all_documents]
        metadatas = [doc.metadata for doc in all_documents]

        BATCH_SIZE = 50   # 배치 크기 감소 (rate limiting 대응)
        MAX_TOKENS_PER_BATCH = 50_000  # 토큰 수 감소
        DELAY_BETWEEN_BATCHES = 2  # 배치 간 2초 대기
        encoder = tiktoken.get_encoding("cl100k_base")

        self.store = None
        batch_texts, batch_metadatas = [], []
        token_count = 0

        for i, (text, metadata) in enumerate(zip(texts, metadatas)):
            text_tokens = len(encoder.encode(text))
            # 토큰 수 또는 배열 길이 초과 시 현재 배치 전송
            if token_count + text_tokens > MAX_TOKENS_PER_BATCH or len(batch_texts) >= BATCH_SIZE:
                try:
                    if self.store is None:
                        logger.info(f"첫 배치({i-len(batch_texts)}~{i})로 벡터 DB 생성")
                        self.store = Chroma.from_texts(
                            texts=batch_texts,
                            embedding=self.embedding,
                            metadatas=batch_metadatas,
                            persist_directory=str(self.vector_db),
                            collection_name=self.collection_name
                        )
                    else:
                        logger.info(f"추가 배치({i-len(batch_texts)}~{i}) 저장")
                        self.store.add_texts(
                            texts=batch_texts,
                            metadatas=batch_metadatas,
                            collection_name=self.collection_name, 
                            persist_directory=str(self.vector_db),
                        )
                    # 배치 초기화
                    batch_texts, batch_metadatas = [], []
                    token_count = 0
                    
                    # Rate limiting 대응을 위한 대기
                    time.sleep(DELAY_BETWEEN_BATCHES)
                except Exception as e:
                    logger.error(f"배치 {i//BATCH_SIZE} Embedding 실패: {e}")
                    batch_texts, batch_metadatas = [], []
                    token_count = 0
                    continue

            batch_texts.append(text)
            batch_metadatas.append(metadata)
            token_count += text_tokens

        # 남은 배치 처리
        if batch_texts:
            try:
                if self.store is None:
                    logger.info(f"마지막 배치({len(all_documents)-len(batch_texts)}~{len(all_documents)})로 벡터 DB 생성")
                    self.store = Chroma.from_texts(
                        texts=batch_texts,
                        embedding=self.embedding,
                        metadatas=batch_metadatas,
                        persist_directory=self.persist_directory,
                        collection_name=self.collection_name, 
                        #colloection_name,persi..설정해야 DB찾을 수 있음!
                    )
                else:
                    logger.info(f"마지막 배치({len(all_documents)-len(batch_texts)}~{len(all_documents)}) 저장")
                    self.store.add_texts(
                        texts=batch_texts,
                        metadatas=batch_metadatas,
                        persist_directory=str(self.vector_db),        # ✅ 수정
                        collection_name=self.collection_name, 
                    )
            except Exception as e:
                logger.error(f"마지막 배치 Embedding 실패: {e}")

        if self.store:
            logger.info(f"총 {len(all_documents)}개 문서를 벡터 DB에 저장 완료")
        else:
            logger.error("벡터 DB 생성 실패")

        return self.store

    # -------------------------
    # Multi-Collection Search Methods
    # -------------------------
    def search_multi_collections(self, query: str, collection_types: List[str], k: int = 5) -> List[Document]:
        """
        여러 콜렉션에서 검색하여 결과 통합
        """
        all_results = []
        
        for collection_type in collection_types:
            if collection_type not in self.stores or not self.stores[collection_type]:
                logger.warning(f"{collection_type} 콜렉션이 초기화되지 않았습니다.")
                continue
                
            try:
                # 각 콜렉션에서 검색
                results = self.stores[collection_type].similarity_search_with_score(query, k=k)
                
                # 점수와 함께 결과 저장 (콜렉션 정보 포함)
                for doc, score in results:
                    doc.metadata['search_score'] = score
                    doc.metadata['source_collection'] = collection_type
                    all_results.append((doc, score))
                    
                logger.info(f"{collection_type} 콜렉션에서 {len(results)}개 결과 검색")
                
            except Exception as e:
                logger.error(f"{collection_type} 콜렉션 검색 실패: {e}")
        
        # 점수순 정렬 후 상위 k개 반환
        all_results.sort(key=lambda x: x[1])  # 거리가 작을수록 유사도 높음
        return [doc for doc, _ in all_results[:k]]

    def get_collection_by_query_type(self, query: str, pet_records: dict = None) -> List[str]:
        """
        질문 유형에 따라 검색할 콜렉션 결정
        """
        query_lower = query.lower()
        collections_to_search = []
        
        # 의약품 관련 키워드
        medication_keywords = ['약', '치료', '병', '질병', '아파', '증상', '부작용', 'medication', 'treatment', '처방']
        
        # 일반 관리 관련 키워드  
        general_keywords = ['건강관리', '사료', '운동', '산책', '관리', '키우기', '예방접종', '백신', '목욕', '훈련']
        
        # 질문 내용 분석
        has_medication_intent = any(keyword in query_lower for keyword in medication_keywords)
        has_general_intent = any(keyword in query_lower for keyword in general_keywords)
        
        # 반려동물의 질병/알러지 정보 확인
        has_medical_history = False
        if pet_records:
            diseases = pet_records.get("disease", [])
            medications = pet_records.get("medication", [])
            if diseases or medications:
                has_medical_history = True
        
        # 콜렉션 선택 로직
        if has_medication_intent or (has_medical_history and not has_general_intent):
            # 의약품 관련 질문이면 의약품 우선, 일반 가이드 보조
            collections_to_search = ['medications', 'general_guides']
            logger.info("의약품 관련 질문으로 판단 - 의약품 콜렉션 우선 검색")
        else:
            # 일반 관리 질문이면 일반 가이드 우선
            collections_to_search = ['general_guides']
            logger.info("일반 관리 질문으로 판단 - 일반 가이드 콜렉션만 검색")
            
        return collections_to_search

    # -------------------------
    # Load documents (md + json)
    # -------------------------
    def load_documents(self) -> List[Document]:
        if not self.documents_path.exists():
            logger.error(f"문서 경로가 존재하지 않습니다: {self.documents_path}")
            return []

        all_documents: List[Document] = []

        md_files = list(self.documents_path.glob("**/*.md"))
        json_files = list(self.documents_path.glob("**/*.json"))

        logger.info(f"Markdown 파일 수: {len(md_files)}, JSON 파일 수: {len(json_files)}")

        for md_file in md_files:
            try:
                docs = self.load_markdown(md_file)
                all_documents.extend(docs)
            except Exception as e:
                logger.warning(f"Markdown 파일 처리 실패 ({md_file}): {e}")

        for json_file in json_files:
            try:
                docs = self.load_json(json_file)
                all_documents.extend(docs)
            except Exception as e:
                logger.warning(f"JSON 파일 처리 실패 ({json_file}): {e}")

        logger.info(f"총 {len(all_documents)}개 문서 청크 로딩 완료")
        return all_documents

    # -------------------------
    # Markdown loader
    # -------------------------
    def load_markdown(self, file_path: Path) -> List[Document]:
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Markdown 파일 읽기 실패 ({file_path}): {e}")
            return []

        meta = self.extract_document_metadata(text)
        splitter = MarkdownHeaderTextSplitter([("#", "title"), ("##", "subtitle")])

        try:
            sections = splitter.split_text(text)
        except Exception as e:
            logger.warning(f"Markdown 분할 실패({file_path}), 전체를 하나로 처리: {e}")
            sections = [text]

        docs: List[Document] = []
        for i, sec in enumerate(sections):
            if isinstance(sec, Document):
                content = sec.page_content
                sec_meta = sec.metadata or {}
            else:
                content = str(sec)
                sec_meta = {}

            clean = self.remove_metadata_blocks(content)
            if not clean.strip():
                continue

            metadata = {**meta, **sec_meta, "source_file": file_path.name, "file_path": str(file_path), "section_index": i}
            metadata = self._sanitize_metadata(metadata)
            docs.append(Document(page_content=clean, metadata=metadata))

        return docs

    # -------------------------
    # JSON loader (robust)
    # -------------------------
    def load_json(self, file_path: Path) -> List[Document]:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"JSON 파일 읽기 실패 ({file_path}): {e}")
            return []

        docs: List[Document] = []

        # If data is a list of items (common in your medication files)
        if isinstance(data, list):
            for idx, item in enumerate(data):
                try:
                    if isinstance(item, dict):
                        # prefer 'text' if present and non-empty
                        content = item.get("text") if isinstance(item.get("text"), str) and item.get("text").strip() else None
                        if content is None:
                            # fallback: serialize entire item
                            content = json.dumps(item, ensure_ascii=False, indent=2)
                        metadata = {
                            "file_path": str(file_path),
                            "data_type": "medication",
                            "item_index": idx,
                        }
                        # merge item metadata if present
                        if "metadata" in item and isinstance(item["metadata"], dict):
                            metadata.update(item["metadata"])
                        if "id" in item:
                            metadata["document_id"] = item["id"]

                    else:
                        # non-dict item -> stringify
                        content = json.dumps(item, ensure_ascii=False)
                        metadata = {"file_path": str(file_path), "data_type": "medication", "item_index": idx}

                    # safe chunking (avoids RecursiveJsonSplitter crashes)
                    chunks = self._safe_chunk_text(content, max_chunk_size=1000)
                    for c_i, chunk in enumerate(chunks):
                        meta_copy = dict(metadata)
                        meta_copy.update({"chunk_index": c_i, "total_chunks": len(chunks)})
                        docs.append(Document(page_content=chunk, metadata=self._sanitize_metadata(meta_copy)))

                except Exception as item_e:
                    logger.warning(f"JSON item 처리 실패 ({file_path}, index={idx}): {item_e}")
                    continue

        elif isinstance(data, dict):
            # single JSON object: serialize and chunk
            content = json.dumps(data, ensure_ascii=False, indent=2)
            chunks = self._safe_chunk_text(content, max_chunk_size=1000)
            for c_i, chunk in enumerate(chunks):
                meta = {"file_path": str(file_path), "data_type": "medication", "chunk_index": c_i, "total_chunks": len(chunks)}
                docs.append(Document(page_content=chunk, metadata=self._sanitize_metadata(meta)))
        else:
            # fallback: stringify whole file
            content = str(data)
            chunks = self._safe_chunk_text(content, max_chunk_size=1000)
            for c_i, chunk in enumerate(chunks):
                meta = {"file_path": str(file_path), "data_type": "medication", "chunk_index": c_i, "total_chunks": len(chunks)}
                docs.append(Document(page_content=chunk, metadata=self._sanitize_metadata(meta)))

        return docs

    # -------------------------
    # Utilities
    # -------------------------
    def _safe_chunk_text(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        """
        Split text into chunks of <= max_chunk_size by sentence boundaries (best-effort).
        """
        if not text:
            return []

        text = text.strip()
        if len(text) <= max_chunk_size:
            return [text]

        # Split into sentences (preserve punctuation)
        sentences = re.split(r'(?<=[\.\?\!\n])\s+', text)
        chunks = []
        current = ""
        for sent in sentences:
            if not sent:
                continue
            if len(current) + len(sent) + 1 <= max_chunk_size:
                current += (sent if current == "" else " " + sent)
            else:
                if current:
                    chunks.append(current.strip())
                # if single sentence itself too long, break by characters
                if len(sent) > max_chunk_size:
                    for i in range(0, len(sent), max_chunk_size):
                        part = sent[i:i + max_chunk_size].strip()
                        if part:
                            chunks.append(part)
                    current = ""
                else:
                    current = sent
        if current:
            chunks.append(current.strip())
        return chunks

    def extract_document_metadata(self, content: str) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {}
        yaml_pattern = r"^---\s*\nmetadata:\s*\n(.*?)\n---"
        match = re.search(yaml_pattern, content, flags=re.MULTILINE | re.DOTALL)
        if not match:
            return metadata

        yaml_content = match.group(1)
        for line in yaml_content.splitlines():
            line = line.strip()
            if ":" in line and not line.startswith("-"):
                key, val = line.split(":", 1)
                key = key.strip()
                value = val.strip().strip('"\'')
                if key == "categories":
                    metadata[key] = self.parse_yaml_list(value)
                else:
                    metadata[key] = value
        return metadata

    def parse_yaml_list(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(v).strip().strip('"\'') for v in value]
        if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            items = value[1:-1].split(",")
            return [item.strip().strip('"\'') for item in items]
        return [str(value).strip().strip('"\'')]

    def remove_metadata_blocks(self, content: str) -> str:
        yaml_pattern = r"^---\s*\nmetadata:\s*\n.*?\n---\s*\n"
        cleaned = re.sub(yaml_pattern, "", content, flags=re.MULTILINE | re.DOTALL)
        cleaned = re.sub(r"\n\s*\n\s*\n", "\n\n", cleaned)
        return cleaned.strip()

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert metadata values to primitives (str/int/float/bool). Lists/dicts -> JSON string.
        """
        safe: Dict[str, Any] = {}
        for k, v in (metadata or {}).items():
            if isinstance(v, (str, int, float, bool)) or v is None:
                safe[k] = v
            else:
                try:
                    safe[k] = json.dumps(v, ensure_ascii=False) if not isinstance(v, (str, int, float, bool)) else v
                except Exception:
                    safe[k] = str(v)
        return safe

    # -------------------------
    # Keyword Search Methods
    # -------------------------
    def keyword_search(self, query: str, k: int = 5, collection_type: str = 'general_guides') -> List[Tuple[Document, float]]:
        """키워드 기반 검색 (TF-IDF 스코어링)"""
        if collection_type not in self.stores or not self.stores[collection_type]:
            logger.warning(f"{collection_type} 콜렉션이 초기화되지 않았습니다.")
            return []
        
        store = self.stores[collection_type]
        
        try:
            # 해당 콜렉션의 모든 문서 가져오기
            all_docs = self._get_all_documents_from_store(store)
            if not all_docs:
                return []
            
            # 키워드 전처리
            query_keywords = self._preprocess_keywords(query)
            if not query_keywords:
                return []
            
            # TF-IDF 계산
            scored_docs = []
            for doc in all_docs:
                score = self._calculate_keyword_score(doc.page_content, query_keywords)
                if score > 0:
                    scored_docs.append((doc, score))
            
            # 점수순 정렬 후 상위 k개 반환
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            return scored_docs[:k]
            
        except Exception as e:
            logger.error(f"키워드 검색 중 오류 발생: {e}")
            return []

    def _get_all_documents(self) -> List[Document]:
        """벡터 스토어에서 모든 문서 가져오기 (하위 호환성)"""
        # 첫 번째 사용 가능한 스토어에서 문서 가져오기
        for store in self.stores.values():
            if store:
                return self._get_all_documents_from_store(store)
        return []

    def _get_all_documents_from_store(self, store) -> List[Document]:
        """특정 스토어에서 모든 문서 가져오기"""
        try:
            # Chroma에서 모든 문서 ID 가져오기
            collection = store._collection
            all_data = collection.get()
            
            documents = []
            if all_data and 'documents' in all_data and 'metadatas' in all_data:
                for i, (content, metadata) in enumerate(zip(all_data['documents'], all_data['metadatas'])):
                    doc = Document(page_content=content, metadata=metadata or {})
                    documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"모든 문서 가져오기 실패: {e}")
            return []

    def _preprocess_keywords(self, query: str) -> List[str]:
        """키워드 전처리 (한국어/영어 지원)"""
        # 소문자 변환 및 특수문자 제거
        query = re.sub(r'[^\w\s가-힣]', ' ', query.lower())
        
        # 단어 분리 및 불용어 제거
        stop_words = {'은', '는', '이', '가', '을', '를', '에', '의', '와', '과', '도', '로', '으로', 
                     'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        
        keywords = [word.strip() for word in query.split() if len(word.strip()) > 1 and word.strip() not in stop_words]
        return keywords

    def _calculate_keyword_score(self, content: str, keywords: List[str]) -> float:
        """TF-IDF 기반 키워드 스코어 계산"""
        if not content or not keywords:
            return 0.0
        
        content_lower = content.lower()
        score = 0.0
        
        for keyword in keywords:
            # 단순 TF 계산 (빈도)
            tf = content_lower.count(keyword.lower())
            if tf > 0:
                # 키워드 길이에 따른 가중치 (긴 키워드에 더 높은 점수)
                weight = len(keyword) / 10.0 + 1.0
                score += tf * weight
        
        return score

    # -------------------------
    # Hybrid Search Methods
    # -------------------------
    def hybrid_search(self, query: str, k: int = 5, vector_weight: float = 0.5, keyword_weight: float = 0.5, collection_type: str = 'general_guides') -> List[Document]:
        """하이브리드 검색 (벡터 + 키워드) - 단일 콜렉션"""
        if collection_type not in self.stores or not self.stores[collection_type]:
            logger.warning(f"{collection_type} 콜렉션이 초기화되지 않았습니다.")
            return []
            
        store = self.stores[collection_type]
        
        try:
            # 벡터 검색 결과
            vector_results = []
            try:
                vector_docs = store.similarity_search_with_score(query, k=k*2)
                # 점수 정규화 (유사도를 0-1 범위로)
                if vector_docs:
                    max_score = max(score for _, score in vector_docs)
                    min_score = min(score for _, score in vector_docs)
                    score_range = max_score - min_score if max_score > min_score else 1
                    
                    for doc, score in vector_docs:
                        # 거리를 유사도로 변환 (거리가 작을수록 유사도가 높음)
                        normalized_score = 1 - ((score - min_score) / score_range)
                        vector_results.append((doc, normalized_score))
            except Exception as e:
                logger.warning(f"벡터 검색 실패: {e}")
            
            # 키워드 검색 결과
            keyword_results = self.keyword_search(query, k=k*2, collection_type=collection_type)
            
            # 키워드 검색 점수 정규화
            if keyword_results:
                max_kw_score = max(score for _, score in keyword_results)
                min_kw_score = min(score for _, score in keyword_results)
                kw_score_range = max_kw_score - min_kw_score if max_kw_score > min_kw_score else 1
                
                normalized_kw_results = []
                for doc, score in keyword_results:
                    normalized_score = (score - min_kw_score) / kw_score_range if kw_score_range > 0 else 0
                    normalized_kw_results.append((doc, normalized_score))
                keyword_results = normalized_kw_results
            
            # 문서별 점수 통합
            doc_scores = {}
            
            # 벡터 검색 점수 추가
            for doc, score in vector_results:
                doc_key = self._get_doc_key(doc)
                doc_scores[doc_key] = doc_scores.get(doc_key, {'doc': doc, 'vector_score': 0, 'keyword_score': 0})
                doc_scores[doc_key]['vector_score'] = score
            
            # 키워드 검색 점수 추가
            for doc, score in keyword_results:
                doc_key = self._get_doc_key(doc)
                if doc_key not in doc_scores:
                    doc_scores[doc_key] = {'doc': doc, 'vector_score': 0, 'keyword_score': 0}
                doc_scores[doc_key]['keyword_score'] = score
            
            # 최종 점수 계산 및 정렬
            final_results = []
            for doc_key, data in doc_scores.items():
                final_score = (data['vector_score'] * vector_weight + 
                             data['keyword_score'] * keyword_weight)
                final_results.append((data['doc'], final_score))
            
            # 점수순 정렬
            final_results.sort(key=lambda x: x[1], reverse=True)
            
            # 상위 k개 문서만 반환
            return [doc for doc, _ in final_results[:k]]
            
        except Exception as e:
            logger.error(f"하이브리드 검색 중 오류 발생: {e}")
            # 실패 시 벡터 검색만 사용
            try:
                if store:
                    return store.similarity_search(query, k=k)
            except:
                pass
            return []

    def _get_doc_key(self, doc: Document) -> str:
        """문서의 고유 키 생성"""
        content_hash = hashlib.md5(doc.page_content.encode('utf-8')).hexdigest()
        metadata_str = json.dumps(doc.metadata, sort_keys=True) if doc.metadata else ""
        metadata_hash = hashlib.md5(metadata_str.encode('utf-8')).hexdigest()
        return f"{content_hash}_{metadata_hash}"

    # 캐시 기능은 CachedOpenAIEmbeddings 클래스로 이동됨
