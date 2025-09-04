#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vector DB Setup for Pet Medicine RAG System
의약품 RAG 시스템용 벡터 DB 구축 스크립트
"""

import json
import os
from typing import List, Dict, Any
import pandas as pd
from langchain.document_loaders import TextLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.vectorstores import FAISS, Chroma
from langchain.embeddings import OpenAIEmbeddings
import chromadb

class MedicineVectorDB:
    """의약품 데이터를 위한 벡터 DB 구축 클래스"""
    
    def __init__(self, embedding_model="text-embedding-ada-002"):
        """
        Args:
            embedding_model: 사용할 임베딩 모델
        """
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self.documents = []
        
    def load_json_documents(self, json_file: str):
        """JSON 파일에서 문서 로드"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"JSON 문서 로드: {len(data)}개")
        return data
    
    def create_chunked_documents(self, data: List[Dict]) -> List[Document]:
        """
        의약품 데이터 특성에 맞는 청킹 전략
        
        1. 제품 문서: 전체 제품 정보를 하나의 청크로 유지
        2. 성분 문서: 성분별로 별도 청크 생성
        3. 추가 청킹: 긴 텍스트는 의미 단위로 분할
        """
        documents = []
        
        for item in data:
            doc_type = item.get('type', 'unknown')
            content = item['content']
            doc_id = item['id']
            
            if doc_type == 'product':
                # 제품 문서: 전체 정보 유지하되 섹션별로 분할
                sections = self._split_product_document(content, doc_id)
                documents.extend(sections)
                
            elif doc_type == 'ingredient':
                # 성분 문서: 그대로 유지 (이미 최적 크기)
                metadata = {
                    'doc_id': doc_id,
                    'doc_type': doc_type,
                    'source': 'ingredient_info'
                }
                documents.append(Document(page_content=content, metadata=metadata))
        
        print(f"청킹 완료: {len(documents)}개 문서")
        return documents
    
    def _split_product_document(self, content: str, doc_id: str) -> List[Document]:
        """제품 문서를 의미있는 섹션으로 분할"""
        documents = []
        lines = content.split('\n')
        
        # 기본 제품 정보 추출
        basic_info = []
        ingredients = []
        storage_info = []
        usage_info = []
        keywords = []
        
        current_section = 'basic'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if '주요 성분 및 함량:' in line:
                current_section = 'ingredients'
                continue
            elif '저장방법:' in line:
                current_section = 'storage'
            elif '효능효과:' in line or '용법용량:' in line or '주의사항:' in line:
                current_section = 'usage'
            elif '--- 검색 키워드 ---' in line:
                current_section = 'keywords'
                continue
                
            if current_section == 'basic' and ('제품명:' in line or '영문명:' in line or '제조업체:' in line or '허가일자:' in line or '제형:' in line):
                basic_info.append(line)
            elif current_section == 'ingredients' and line.startswith('-'):
                ingredients.append(line)
            elif current_section == 'storage':
                storage_info.append(line)
            elif current_section == 'usage':
                usage_info.append(line)
            elif current_section == 'keywords':
                keywords.append(line)
        
        # 제품명과 업체명 추출 (메타데이터용)
        product_name = ""
        company = ""
        for info in basic_info:
            if info.startswith('제품명:'):
                product_name = info.split(':', 1)[1].strip()
            elif info.startswith('제조업체:'):
                company = info.split(':', 1)[1].strip()
        
        # 1. 기본 제품 정보 청크
        basic_content = '\n'.join(basic_info)
        if basic_content:
            metadata = {
                'doc_id': f"{doc_id}_basic",
                'doc_type': 'product',
                'section': 'basic_info',
                'product_name': product_name,
                'company': company,
                'source': 'product_basic'
            }
            documents.append(Document(page_content=basic_content, metadata=metadata))
        
        # 2. 성분 정보 청크
        ingredients_content = '주요 성분 및 함량:\n' + '\n'.join(ingredients)
        if ingredients:
            metadata = {
                'doc_id': f"{doc_id}_ingredients",
                'doc_type': 'product',
                'section': 'ingredients',
                'product_name': product_name,
                'company': company,
                'source': 'product_ingredients'
            }
            documents.append(Document(page_content=ingredients_content, metadata=metadata))
        
        # 3. 저장 및 사용법 청크
        usage_content = '\n'.join(storage_info + usage_info)
        if usage_content:
            metadata = {
                'doc_id': f"{doc_id}_usage",
                'doc_type': 'product',
                'section': 'usage_storage',
                'product_name': product_name,
                'company': company,
                'source': 'product_usage'
            }
            documents.append(Document(page_content=usage_content, metadata=metadata))
        
        # 4. 전체 제품 요약 청크 (검색용)
        summary_content = f"{basic_content}\n\n성분 요약:\n" + '\n'.join(ingredients[:5])  # 주요 성분 5개만
        metadata = {
            'doc_id': f"{doc_id}_summary",
            'doc_type': 'product',
            'section': 'summary',
            'product_name': product_name,
            'company': company,
            'source': 'product_summary'
        }
        documents.append(Document(page_content=summary_content, metadata=metadata))
        
        return documents
    
    def create_faiss_vectorstore(self, documents: List[Document], save_path: str = "medicine_faiss_db"):
        """FAISS 벡터스토어 생성"""
        print("FAISS 벡터스토어 생성 중...")
        
        vectorstore = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        # 로컬에 저장
        vectorstore.save_local(save_path)
        print(f"FAISS DB 저장 완료: {save_path}")
        
        return vectorstore
    
    def create_chroma_vectorstore(self, documents: List[Document], collection_name: str = "medicine_db", persist_dir: str = "chroma_db"):
        """ChromaDB 벡터스토어 생성"""
        print("ChromaDB 벡터스토어 생성 중...")
        
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=collection_name,
            persist_directory=persist_dir
        )
        
        print(f"ChromaDB 저장 완료: {persist_dir}")
        return vectorstore
    
    def setup_hybrid_search(self, documents: List[Document]):
        """하이브리드 검색을 위한 추가 인덱스 생성"""
        # 키워드 기반 검색을 위한 제품명, 성분명 인덱스
        product_index = {}
        ingredient_index = {}
        company_index = {}
        
        for doc in documents:
            metadata = doc.metadata
            content = doc.page_content.lower()
            
            # 제품명 인덱스
            if 'product_name' in metadata:
                product_name = metadata['product_name'].lower()
                if product_name not in product_index:
                    product_index[product_name] = []
                product_index[product_name].append(metadata['doc_id'])
            
            # 업체명 인덱스
            if 'company' in metadata:
                company = metadata['company'].lower()
                if company not in company_index:
                    company_index[company] = []
                company_index[company].append(metadata['doc_id'])
            
            # 성분명 인덱스 (성분 문서에서)
            if metadata.get('doc_type') == 'ingredient' and '성분명:' in content:
                ingredient_name = content.split('성분명:')[1].split('\n')[0].strip().lower()
                if ingredient_name not in ingredient_index:
                    ingredient_index[ingredient_name] = []
                ingredient_index[ingredient_name].append(metadata['doc_id'])
        
        # 인덱스 저장
        indexes = {
            'products': product_index,
            'ingredients': ingredient_index,
            'companies': company_index
        }
        
        with open('search_indexes.json', 'w', encoding='utf-8') as f:
            json.dump(indexes, f, ensure_ascii=False, indent=2)
        
        print("하이브리드 검색 인덱스 생성 완료")
        return indexes

class MedicineSearchEngine:
    """의약품 검색 엔진"""
    
    def __init__(self, vectorstore, indexes_file: str = "search_indexes.json"):
        self.vectorstore = vectorstore
        self.indexes = self._load_indexes(indexes_file)
    
    def _load_indexes(self, file_path: str):
        """검색 인덱스 로드"""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def search_by_product(self, product_name: str, k: int = 5):
        """제품명으로 검색"""
        # 벡터 검색
        vector_results = self.vectorstore.similarity_search(
            f"제품명 {product_name}",
            k=k,
            filter={'doc_type': 'product'}
        )
        
        # 키워드 매칭
        keyword_results = []
        product_lower = product_name.lower()
        for indexed_product, doc_ids in self.indexes.get('products', {}).items():
            if product_lower in indexed_product:
                keyword_results.extend(doc_ids)
        
        return {
            'vector_search': vector_results,
            'keyword_match': keyword_results
        }
    
    def search_by_ingredient(self, ingredient_name: str, k: int = 10):
        """성분명으로 검색"""
        vector_results = self.vectorstore.similarity_search(
            f"성분 {ingredient_name}",
            k=k,
            filter={'doc_type': 'ingredient'}
        )
        
        return vector_results
    
    def search_by_company(self, company_name: str, k: int = 10):
        """업체명으로 검색"""
        vector_results = self.vectorstore.similarity_search(
            f"제조업체 {company_name}",
            k=k,
            filter={'company': company_name}
        )
        
        return vector_results
    
    def hybrid_search(self, query: str, k: int = 10):
        """하이브리드 검색 (벡터 + 키워드)"""
        # 벡터 검색
        vector_results = self.vectorstore.similarity_search(query, k=k)
        
        # 키워드 기반 부스팅
        boosted_results = []
        query_lower = query.lower()
        
        for doc in vector_results:
            score_boost = 0
            metadata = doc.metadata
            
            # 제품명 매칭 시 점수 부스팅
            if 'product_name' in metadata and query_lower in metadata['product_name'].lower():
                score_boost += 0.3
            
            # 업체명 매칭 시 점수 부스팅
            if 'company' in metadata and query_lower in metadata['company'].lower():
                score_boost += 0.2
            
            # 성분명 매칭 시 점수 부스팅
            if '성분명:' in doc.page_content.lower() and query_lower in doc.page_content.lower():
                score_boost += 0.4
            
            boosted_results.append({
                'document': doc,
                'boost_score': score_boost
            })
        
        # 부스팅 점수로 정렬
        boosted_results.sort(key=lambda x: x['boost_score'], reverse=True)
        
        return [item['document'] for item in boosted_results]

def main():
    """메인 실행 함수"""
    print("=== 의약품 벡터 DB 구축 시작 ===")
    
    # 벡터 DB 구축
    vector_db = MedicineVectorDB()
    
    # JSON 문서 로드
    json_file = "rag_documents/all_documents.json"
    if not os.path.exists(json_file):
        print(f"파일이 없습니다: {json_file}")
        return
    
    data = vector_db.load_json_documents(json_file)
    
    # 청킹된 문서 생성
    documents = vector_db.create_chunked_documents(data)
    
    # FAISS 벡터스토어 생성
    faiss_vectorstore = vector_db.create_faiss_vectorstore(documents)
    
    # ChromaDB 벡터스토어 생성 (선택사항)
    # chroma_vectorstore = vector_db.create_chroma_vectorstore(documents)
    
    # 하이브리드 검색 인덱스 생성
    vector_db.setup_hybrid_search(documents)
    
    print("\n=== 벡터 DB 구축 완료 ===")
    print(f"총 문서 수: {len(documents)}")
    print("검색 가능:")
    print("1. 제품명으로 검색")
    print("2. 성분명으로 검색") 
    print("3. 업체명으로 검색")
    print("4. 자연어 쿼리 검색")
    
    # 검색 엔진 테스트
    search_engine = MedicineSearchEngine(faiss_vectorstore)
    
    # 예시 검색
    print("\n=== 검색 테스트 ===")
    results = search_engine.hybrid_search("비타민 C", k=3)
    for i, doc in enumerate(results):
        print(f"\n결과 {i+1}:")
        print(f"타입: {doc.metadata.get('doc_type', 'unknown')}")
        print(f"내용: {doc.page_content[:200]}...")

if __name__ == "__main__":
    main()