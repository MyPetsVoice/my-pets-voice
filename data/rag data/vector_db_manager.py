"""
벡터 DB 관리 및 검색 최적화 모듈

ChromaDB를 활용한 RAG 시스템의 벡터 저장 및 검색 기능을 제공합니다.
"""

import chromadb
import json
import re
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
import logging
from datetime import datetime

from rag_chunking_strategy import DocumentChunk, UnifiedDocumentProcessor, RAGChunkProcessor


class VectorDBManager:
    """벡터 DB 관리 클래스"""
    
    def __init__(self, 
                 db_path: str = "./vector_db",
                 collection_name: str = "pet_healthcare",
                 embedding_model: str = "jhgan/ko-sroberta-multitask"):
        
        self.db_path = db_path
        self.collection_name = collection_name
        
        # ChromaDB 클라이언트 초기화
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # 임베딩 모델 로드 (한국어 지원)
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # 로깅 설정
        self.logger = logging.getLogger(__name__)
        
    def add_documents(self, chunks: List[DocumentChunk], batch_size: int = 100):
        """문서 청크를 벡터 DB에 추가"""
        
        total_chunks = len(chunks)
        self.logger.info(f"벡터 DB에 {total_chunks}개 청크 추가 시작")
        
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i + batch_size]
            
            # 배치별 처리
            ids = [chunk.id for chunk in batch]
            texts = [chunk.text for chunk in batch]
            metadatas = [chunk.metadata for chunk in batch]
            
            # 임베딩 생성
            embeddings = self.embedding_model.encode(texts).tolist()
            
            try:
                # ChromaDB에 추가
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas
                )
                
                self.logger.info(f"배치 {i//batch_size + 1}/{(total_chunks-1)//batch_size + 1} 완료 ({len(batch)}개 청크)")
                
            except Exception as e:
                self.logger.error(f"배치 추가 실패: {e}")
                # 개별적으로 다시 시도
                for j, chunk in enumerate(batch):
                    try:
                        self.collection.add(
                            ids=[ids[j]],
                            embeddings=[embeddings[j]], 
                            documents=[texts[j]],
                            metadatas=[metadatas[j]]
                        )
                    except Exception as e2:
                        self.logger.error(f"청크 {ids[j]} 추가 실패: {e2}")
        
        self.logger.info(f"벡터 DB 추가 완료: {total_chunks}개 청크")
    
    def search(self, 
               query: str, 
               n_results: int = 5,
               filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """기본 벡터 유사도 검색"""
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filters,
                include=['documents', 'metadatas', 'distances']
            )
            
            # 결과 포맷팅
            formatted_results = []
            for doc, metadata, distance in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ):
                formatted_results.append({
                    'content': doc,
                    'metadata': metadata,
                    'score': 1 - distance,  # 거리를 점수로 변환
                    'distance': distance
                })
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"검색 실패: {e}")
            return []
    
    def hybrid_search(self, 
                     query: str, 
                     n_results: int = 5,
                     keyword_weight: float = 0.3,
                     semantic_weight: float = 0.7,
                     filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """키워드 + 의미적 유사도 하이브리드 검색"""
        
        # 더 많은 후보를 가져와서 재랭킹
        candidate_count = min(n_results * 3, 50)
        
        candidates = self.search(query, candidate_count, filters)
        
        if not candidates:
            return []
        
        # 키워드 매칭 점수 계산
        query_keywords = self._extract_query_keywords(query)
        
        for result in candidates:
            # 의미적 유사도 점수
            semantic_score = result['score']
            
            # 키워드 매칭 점수
            keyword_score = self._calculate_keyword_score(
                query_keywords, 
                result['metadata'].get('keywords', [])
            )
            
            # 제목 매칭 점수
            title_score = self._calculate_title_score(
                query, 
                result['metadata'].get('title', '')
            )
            
            # chunk_type 매칭 점수
            type_score = self._calculate_type_score(
                query, 
                result['metadata'].get('chunk_type', '')
            )
            
            # 최종 점수 계산
            final_score = (
                semantic_score * semantic_weight +
                keyword_score * keyword_weight +
                title_score * 0.1 +
                type_score * 0.1
            )
            
            result['final_score'] = final_score
            result['keyword_score'] = keyword_score
            result['title_score'] = title_score
            result['type_score'] = type_score
        
        # 최종 점수로 정렬
        candidates.sort(key=lambda x: x['final_score'], reverse=True)
        
        return candidates[:n_results]
    
    def contextual_search(self, 
                         query: str, 
                         n_results: int = 5,
                         include_context: bool = True) -> List[Dict[str, Any]]:
        """컨텍스트 정보가 강화된 검색"""
        
        results = self.hybrid_search(query, n_results)
        
        if not include_context:
            return results
        
        # 결과에 컨텍스트 정보 추가
        enriched_results = []
        
        for result in results:
            metadata = result['metadata']
            
            # 컨텍스트 정보 생성
            context_parts = []
            
            # 문서 출처
            if metadata.get('publisher'):
                context_parts.append(f"출처: {metadata['publisher']}")
            elif metadata.get('source_file'):
                context_parts.append(f"파일: {metadata['source_file']}")
            
            # 섹션 경로 (Markdown)
            if metadata.get('parent_titles'):
                section_path = ' > '.join(metadata['parent_titles'])
                if metadata.get('title'):
                    section_path += f" > {metadata['title']}"
                context_parts.append(f"섹션: {section_path}")
            elif metadata.get('title'):
                context_parts.append(f"제목: {metadata['title']}")
            
            # 문서 타입
            chunk_type = metadata.get('chunk_type', '')
            type_description = self._get_type_description(chunk_type)
            if type_description:
                context_parts.append(f"분류: {type_description}")
            
            enriched_result = {
                'content': result['content'],
                'context': ' | '.join(context_parts),
                'metadata': metadata,
                'score': result['final_score'],
                'keyword_match': result.get('keyword_score', 0),
                'relevance_breakdown': {
                    'semantic': result.get('score', 0),
                    'keyword': result.get('keyword_score', 0),
                    'title': result.get('title_score', 0),
                    'type': result.get('type_score', 0)
                }
            }
            
            enriched_results.append(enriched_result)
        
        return enriched_results
    
    def filtered_search(self, 
                       query: str,
                       chunk_types: Optional[List[str]] = None,
                       source_types: Optional[List[str]] = None,
                       publishers: Optional[List[str]] = None,
                       n_results: int = 5) -> List[Dict[str, Any]]:
        """필터 기반 검색"""
        
        # 필터 조건 구성
        filters = {}
        
        if chunk_types:
            if len(chunk_types) == 1:
                filters['chunk_type'] = chunk_types[0]
            else:
                filters['chunk_type'] = {"$in": chunk_types}
        
        if source_types:
            if len(source_types) == 1:
                filters['source_type'] = source_types[0]
            else:
                filters['source_type'] = {"$in": source_types}
        
        if publishers:
            if len(publishers) == 1:
                filters['publisher'] = publishers[0]
            else:
                filters['publisher'] = {"$in": publishers}
        
        return self.contextual_search(query, n_results, filters)
    
    def get_similar_chunks(self, 
                          chunk_id: str, 
                          n_results: int = 5,
                          exclude_same_document: bool = True) -> List[Dict[str, Any]]:
        """특정 청크와 유사한 청크 찾기"""
        
        try:
            # 기준 청크 가져오기
            base_chunk = self.collection.get(ids=[chunk_id], include=['embeddings', 'metadatas'])
            
            if not base_chunk['embeddings']:
                return []
            
            base_embedding = base_chunk['embeddings'][0]
            base_metadata = base_chunk['metadatas'][0]
            
            # 유사한 청크 검색
            results = self.collection.query(
                query_embeddings=[base_embedding],
                n_results=n_results + 1,  # 자기 자신 제외를 위해 +1
                include=['documents', 'metadatas', 'distances']
            )
            
            similar_chunks = []
            for doc, metadata, distance in zip(
                results['documents'][0],
                results['metadatas'][0], 
                results['distances'][0]
            ):
                # 자기 자신 제외
                if metadata.get('id') == chunk_id:
                    continue
                
                # 같은 문서 제외 (옵션)
                if exclude_same_document:
                    if metadata.get('source_file') == base_metadata.get('source_file'):
                        continue
                
                similar_chunks.append({
                    'content': doc,
                    'metadata': metadata,
                    'similarity': 1 - distance
                })
            
            return similar_chunks[:n_results]
            
        except Exception as e:
            self.logger.error(f"유사 청크 검색 실패: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """컬렉션 통계 정보"""
        
        try:
            # 전체 데이터 가져오기 (메타데이터만)
            all_data = self.collection.get(include=['metadatas'])
            metadatas = all_data['metadatas']
            
            stats = {
                'total_documents': len(metadatas),
                'by_chunk_type': {},
                'by_source_type': {},
                'by_publisher': {},
                'by_source_file': {}
            }
            
            for metadata in metadatas:
                # chunk_type별 통계
                chunk_type = metadata.get('chunk_type', 'unknown')
                stats['by_chunk_type'][chunk_type] = stats['by_chunk_type'].get(chunk_type, 0) + 1
                
                # source_type별 통계
                source_type = metadata.get('source_type', 'unknown')  
                stats['by_source_type'][source_type] = stats['by_source_type'].get(source_type, 0) + 1
                
                # publisher별 통계
                publisher = metadata.get('publisher', 'unknown')
                stats['by_publisher'][publisher] = stats['by_publisher'].get(publisher, 0) + 1
                
                # source_file별 통계
                source_file = metadata.get('source_file', 'unknown')
                stats['by_source_file'][source_file] = stats['by_source_file'].get(source_file, 0) + 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"통계 정보 수집 실패: {e}")
            return {}
    
    def _extract_query_keywords(self, query: str) -> List[str]:
        """쿼리에서 키워드 추출"""
        # 한국어 단어 추출 (2글자 이상)
        korean_words = re.findall(r'[가-힣]{2,}', query)
        
        # 영어 단어 추출 (3글자 이상)
        english_words = re.findall(r'[a-zA-Z]{3,}', query)
        
        # 숫자 포함 단어
        numeric_words = re.findall(r'[0-9]+[가-힣a-zA-Z]*|[가-힣a-zA-Z]*[0-9]+', query)
        
        keywords = korean_words + english_words + numeric_words
        
        # 중복 제거 및 소문자 변환
        keywords = list(set([kw.lower() for kw in keywords]))
        
        return keywords
    
    def _calculate_keyword_score(self, query_keywords: List[str], doc_keywords: List[str]) -> float:
        """키워드 매칭 점수 계산"""
        if not query_keywords or not doc_keywords:
            return 0.0
        
        # 소문자로 변환
        query_kws = [kw.lower() for kw in query_keywords]
        doc_kws = [kw.lower() for kw in doc_keywords]
        
        # 교집합 계산
        intersection = set(query_kws) & set(doc_kws)
        
        if not intersection:
            return 0.0
        
        # Jaccard 유사도 계산
        union = set(query_kws) | set(doc_kws)
        jaccard_score = len(intersection) / len(union)
        
        return jaccard_score
    
    def _calculate_title_score(self, query: str, title: str) -> float:
        """제목 매칭 점수 계산"""
        if not title:
            return 0.0
        
        query_lower = query.lower()
        title_lower = title.lower()
        
        # 부분 문자열 매칭
        if query_lower in title_lower or title_lower in query_lower:
            return 1.0
        
        # 키워드 매칭
        query_words = query_lower.split()
        title_words = title_lower.split()
        
        matches = sum(1 for word in query_words if word in title_lower)
        if matches > 0:
            return matches / len(query_words)
        
        return 0.0
    
    def _calculate_type_score(self, query: str, chunk_type: str) -> float:
        """chunk_type 매칭 점수 계산"""
        if not chunk_type:
            return 0.0
        
        # 타입별 키워드 매핑
        type_keywords = {
            'dog_health': ['강아지', '개', '반려견', '개의', '강아지의'],
            'cat_health': ['고양이', '냥이', '반려묘', '고양이의', '묘'],
            'medicine': ['약', '의약품', '치료제', '약물', '처방'],
            'disease': ['질병', '병', '증상', '진단', '감염'],
            'emergency': ['응급', '재난', '사고', '응급처치', '위험'],
            'nutrition': ['사료', '먹이', '영양', '음식', '급여'],
            'registration': ['등록', '신고', '허가', '법', '규정']
        }
        
        keywords = type_keywords.get(chunk_type, [])
        
        for keyword in keywords:
            if keyword in query:
                return 1.0
        
        return 0.0
    
    def _get_type_description(self, chunk_type: str) -> str:
        """chunk_type 한국어 설명"""
        descriptions = {
            'dog_health': '반려견 건강관리',
            'cat_health': '반려묘 건강관리', 
            'pet_general': '반려동물 일반정보',
            'medicine': '동물용 의약품',
            'disease': '질병 정보',
            'emergency': '응급상황 대응',
            'nutrition': '사료/영양 관리',
            'symptoms': '증상 가이드',
            'breed_info': '품종 정보',
            'registration': '동물등록제',
            'lifestyle': '반려생활 가이드',
            'owner_obligation': '소유자 의무사항'
        }
        
        return descriptions.get(chunk_type, chunk_type)
    
    def delete_collection(self):
        """컬렉션 삭제"""
        try:
            self.client.delete_collection(self.collection_name)
            self.logger.info(f"컬렉션 '{self.collection_name}' 삭제 완료")
        except Exception as e:
            self.logger.error(f"컬렉션 삭제 실패: {e}")
    
    def update_document(self, chunk: DocumentChunk):
        """문서 업데이트"""
        try:
            # 임베딩 생성
            embedding = self.embedding_model.encode(chunk.text).tolist()
            
            # 업데이트
            self.collection.upsert(
                ids=[chunk.id],
                embeddings=[embedding],
                documents=[chunk.text], 
                metadatas=[chunk.metadata]
            )
            
            self.logger.info(f"문서 업데이트 완료: {chunk.id}")
            
        except Exception as e:
            self.logger.error(f"문서 업데이트 실패 {chunk.id}: {e}")


def initialize_vector_db(data_path: str = "./data/rag data") -> VectorDBManager:
    """벡터 DB 초기화 및 데이터 로드"""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 벡터 DB 관리자 초기화
    db_manager = VectorDBManager()
    
    # 문서 처리기 초기화
    processor = UnifiedDocumentProcessor()
    chunk_processor = RAGChunkProcessor()
    
    # 데이터 경로 설정
    data_path = Path(data_path)
    
    # 처리할 파일 수집
    file_patterns = ["**/*.json", "**/*.md", "**/*.txt"]
    all_files = []
    
    for pattern in file_patterns:
        files = list(data_path.glob(pattern))
        all_files.extend(files)
    
    logger.info(f"총 {len(all_files)}개 파일 처리 시작")
    
    # 모든 문서 처리
    all_chunks = []
    
    for file_path in all_files:
        try:
            chunks = processor.process_document(file_path)
            all_chunks.extend(chunks)
            logger.info(f"✅ {file_path.name}: {len(chunks)}개 청크 생성")
            
        except Exception as e:
            logger.error(f"❌ {file_path.name}: {e}")
    
    # 품질 향상 및 중복 제거
    logger.info("중복 제거 및 품질 향상 처리 중...")
    unique_chunks = chunk_processor.remove_duplicates(all_chunks)
    
    logger.info(f"처리 완료: {len(all_chunks)} -> {len(unique_chunks)}개 고유 청크")
    
    # 벡터 DB에 추가
    if unique_chunks:
        db_manager.add_documents(unique_chunks)
        
        # 통계 정보 출력
        stats = db_manager.get_collection_stats()
        logger.info(f"벡터 DB 구축 완료: {stats}")
    
    return db_manager


# 사용 예시
if __name__ == "__main__":
    # 벡터 DB 초기화 및 데이터 로드
    db_manager = initialize_vector_db()
    
    # 검색 테스트
    query = "말티즈 건강관리"
    results = db_manager.contextual_search(query, n_results=3)
    
    print(f"\n검색 결과: '{query}'")
    print("=" * 50)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['context']}")
        print(f"점수: {result['score']:.3f}")
        print(f"내용: {result['content'][:100]}...")