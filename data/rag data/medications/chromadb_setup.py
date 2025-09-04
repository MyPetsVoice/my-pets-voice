#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromaDB Setup for Pet Medicine RAG System
의약품 RAG 시스템용 ChromaDB 구축 스크립트
"""

import json
import os
import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from langchain.embeddings import OpenAIEmbeddings
import ast

class MedicineChromaDB:
    """의약품 데이터를 위한 ChromaDB 구축 클래스"""
    
    def __init__(self, persist_directory: str = "medicine_chromadb", embedding_model: str = "text-embedding-ada-002"):
        """
        Args:
            persist_directory: ChromaDB 저장 디렉토리
            embedding_model: 사용할 임베딩 모델
        """
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        
        # ChromaDB 클라이언트 초기화
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # 컬렉션 생성 (제품용, 성분용 분리)
        self.product_collection = self.client.get_or_create_collection(
            name="medicine_products",
            metadata={"description": "반려동물 의약품 제품 정보"}
        )
        
        self.ingredient_collection = self.client.get_or_create_collection(
            name="medicine_ingredients", 
            metadata={"description": "의약품 성분 정보"}
        )
        
        print(f"ChromaDB 초기화 완료: {persist_directory}")
    
    def load_json_documents(self, json_file: str) -> List[Dict]:
        """JSON 파일에서 문서 로드"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"문서 로드 완료: {len(data)}개")
        return data
    
    def extract_metadata_from_content(self, content: str, doc_type: str) -> Dict[str, Any]:
        """문서 내용에서 메타데이터 추출"""
        metadata = {"doc_type": doc_type}
        
        lines = content.split('\n')
        
        if doc_type == 'product':
            for line in lines:
                line = line.strip()
                if line.startswith('제품명:'):
                    metadata['product_name'] = line.split(':', 1)[1].strip()
                elif line.startswith('영문명:'):
                    metadata['english_name'] = line.split(':', 1)[1].strip()
                elif line.startswith('제조업체:'):
                    metadata['company'] = line.split(':', 1)[1].strip()
                elif line.startswith('허가일자:'):
                    metadata['approval_date'] = line.split(':', 1)[1].strip()
                elif line.startswith('제형:'):
                    metadata['form_type'] = line.split(':', 1)[1].strip()
            
            # 성분 추출
            ingredients = []
            in_ingredients_section = False
            for line in lines:
                if '주요 성분 및 함량:' in line:
                    in_ingredients_section = True
                    continue
                elif line.startswith('저장방법:'):
                    break
                elif in_ingredients_section and line.strip().startswith('-'):
                    ingredient = line.strip()[1:].strip()
                    if ':' in ingredient:
                        ingredient_name = ingredient.split(':')[0].strip()
                        ingredients.append(ingredient_name)
            
            metadata['ingredients'] = ingredients
            metadata['ingredient_count'] = len(ingredients)
            
        elif doc_type == 'ingredient':
            for line in lines:
                line = line.strip()
                if line.startswith('성분명:'):
                    metadata['ingredient_name'] = line.split(':', 1)[1].strip()
                elif line.startswith('함유제품:'):
                    metadata['product_name'] = line.split(':', 1)[1].strip()
                elif line.startswith('제조업체:'):
                    metadata['company'] = line.split(':', 1)[1].strip()
                elif line.startswith('함량:'):
                    dosage_info = line.split(':', 1)[1].strip()
                    metadata['dosage'] = dosage_info
                    
                    # 단위 추출
                    if 'MG' in dosage_info.upper():
                        metadata['unit'] = 'MG'
                    elif 'IU' in dosage_info.upper():
                        metadata['unit'] = 'IU'
                    elif 'MCG' in dosage_info.upper():
                        metadata['unit'] = 'MCG'
        
        return metadata
    
    def add_products_to_chromadb(self, data: List[Dict]):
        """제품 데이터를 ChromaDB에 추가"""
        product_documents = [item for item in data if item.get('type') == 'product']
        
        if not product_documents:
            print("제품 문서가 없습니다.")
            return
        
        print(f"제품 문서 처리 중: {len(product_documents)}개")
        
        # 배치 처리용 리스트
        batch_size = 100
        
        for i in range(0, len(product_documents), batch_size):
            batch = product_documents[i:i + batch_size]
            
            documents = []
            metadatas = []
            ids = []
            
            for item in batch:
                content = item['content']
                doc_id = item['id']
                
                # 메타데이터 추출
                metadata = self.extract_metadata_from_content(content, 'product')
                
                documents.append(content)
                metadatas.append(metadata)
                ids.append(doc_id)
            
            # ChromaDB에 추가
            self.product_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"제품 배치 처리 완료: {i + len(batch)}/{len(product_documents)}")
        
        print("모든 제품 문서 추가 완료")
    
    def add_ingredients_to_chromadb(self, data: List[Dict]):
        """성분 데이터를 ChromaDB에 추가"""
        ingredient_documents = [item for item in data if item.get('type') == 'ingredient']
        
        if not ingredient_documents:
            print("성분 문서가 없습니다.")
            return
        
        print(f"성분 문서 처리 중: {len(ingredient_documents)}개")
        
        # 배치 처리
        batch_size = 500  # 성분 문서는 작아서 배치 크기 증가
        
        for i in range(0, len(ingredient_documents), batch_size):
            batch = ingredient_documents[i:i + batch_size]
            
            documents = []
            metadatas = []
            ids = []
            
            for item in batch:
                content = item['content']
                doc_id = item['id']
                
                # 메타데이터 추출
                metadata = self.extract_metadata_from_content(content, 'ingredient')
                
                documents.append(content)
                metadatas.append(metadata)
                ids.append(doc_id)
            
            # ChromaDB에 추가
            self.ingredient_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"성분 배치 처리 완료: {i + len(batch)}/{len(ingredient_documents)}")
        
        print("모든 성분 문서 추가 완료")

class MedicineChromaSearch:
    """ChromaDB 기반 의약품 검색 엔진"""
    
    def __init__(self, db_path: str = "medicine_chromadb"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.product_collection = self.client.get_collection("medicine_products")
        self.ingredient_collection = self.client.get_collection("medicine_ingredients")
    
    def search_products(self, query: str, n_results: int = 10, where: Optional[Dict] = None) -> Dict:
        """제품 검색"""
        results = self.product_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        return self._format_results(results)
    
    def search_ingredients(self, query: str, n_results: int = 10, where: Optional[Dict] = None) -> Dict:
        """성분 검색"""
        results = self.ingredient_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        return self._format_results(results)
    
    def search_by_company(self, company_name: str, n_results: int = 10) -> Dict:
        """업체별 제품 검색"""
        return self.search_products(
            query=f"{company_name} 제품",
            n_results=n_results,
            where={"company": company_name}
        )
    
    def search_by_ingredient_name(self, ingredient_name: str, n_results: int = 20) -> Dict:
        """특정 성분을 포함한 제품 찾기"""
        # 먼저 성분으로 검색
        ingredient_results = self.search_ingredients(
            query=ingredient_name,
            n_results=n_results,
            where={"ingredient_name": {"$contains": ingredient_name}}
        )
        
        # 해당 성분을 포함한 제품들 찾기
        product_names = []
        if ingredient_results['results']:
            for result in ingredient_results['results']:
                product_name = result['metadata'].get('product_name')
                if product_name and product_name not in product_names:
                    product_names.append(product_name)
        
        # 제품 상세 정보 검색
        product_results = []
        for product_name in product_names[:10]:  # 상위 10개 제품만
            results = self.search_products(
                query=product_name,
                n_results=1,
                where={"product_name": product_name}
            )
            if results['results']:
                product_results.extend(results['results'])
        
        return {
            'ingredient_info': ingredient_results,
            'related_products': product_results,
            'summary': {
                'ingredient_matches': len(ingredient_results.get('results', [])),
                'related_products_count': len(product_results)
            }
        }
    
    def advanced_search(self, query: str, filters: Dict = None, n_results: int = 10) -> Dict:
        """고급 검색 (복합 조건)"""
        filters = filters or {}
        
        # 제품과 성분 모두에서 검색
        product_results = self.search_products(query, n_results, filters.get('product'))
        ingredient_results = self.search_ingredients(query, n_results, filters.get('ingredient'))
        
        return {
            'products': product_results,
            'ingredients': ingredient_results,
            'combined_score': len(product_results.get('results', [])) + len(ingredient_results.get('results', []))
        }
    
    def get_collection_stats(self) -> Dict:
        """컬렉션 통계 정보"""
        product_count = self.product_collection.count()
        ingredient_count = self.ingredient_collection.count()
        
        return {
            'product_count': product_count,
            'ingredient_count': ingredient_count,
            'total_documents': product_count + ingredient_count
        }
    
    def _format_results(self, results: Dict) -> Dict:
        """검색 결과 포맷팅"""
        if not results['documents'] or not results['documents'][0]:
            return {'results': []}
        
        formatted_results = []
        documents = results['documents'][0]
        metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(documents)
        distances = results['distances'][0] if results['distances'] else [0] * len(documents)
        
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            formatted_results.append({
                'rank': i + 1,
                'content': doc,
                'metadata': metadata,
                'similarity_score': 1 - distance,  # 유사도 점수로 변환
                'distance': distance
            })
        
        return {'results': formatted_results}

def main():
    """메인 실행 함수"""
    print("=== ChromaDB 의약품 RAG 시스템 구축 ===")
    
    # JSON 데이터 로드
    json_file = "rag_documents/all_documents.json"
    if not os.path.exists(json_file):
        print(f"파일을 찾을 수 없습니다: {json_file}")
        print("먼저 csv_to_rag_converter.py를 실행하세요.")
        return
    
    # ChromaDB 초기화
    chroma_db = MedicineChromaDB()
    
    # 데이터 로드
    data = chroma_db.load_json_documents(json_file)
    
    # 제품 문서 추가
    chroma_db.add_products_to_chromadb(data)
    
    # 성분 문서 추가
    chroma_db.add_ingredients_to_chromadb(data)
    
    print("\n=== ChromaDB 구축 완료 ===")
    
    # 검색 엔진 테스트
    search_engine = MedicineChromaSearch()
    stats = search_engine.get_collection_stats()
    
    print(f"제품 문서: {stats['product_count']:,}개")
    print(f"성분 문서: {stats['ingredient_count']:,}개")
    print(f"총 문서: {stats['total_documents']:,}개")
    
    # 검색 테스트
    print("\n=== 검색 테스트 ===")
    
    # 1. 제품 검색
    print("\n1. 제품 검색: '비타민'")
    results = search_engine.search_products("비타민", n_results=3)
    for result in results['results']:
        print(f"- {result['metadata'].get('product_name', '제품명 없음')} (유사도: {result['similarity_score']:.3f})")
    
    # 2. 성분별 제품 찾기
    print("\n2. 성분별 제품 찾기: '비타민 C'")
    results = search_engine.search_by_ingredient_name("비타민 C")
    print(f"관련 제품 {results['summary']['related_products_count']}개 발견")
    
    # 3. 업체별 검색
    print("\n3. 업체별 검색: '우성양행'")
    results = search_engine.search_by_company("(주)우성양행")
    print(f"우성양행 제품 {len(results['results'])}개 발견")

if __name__ == "__main__":
    main()