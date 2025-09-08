#!/usr/bin/env python3
"""
VectorStoreService 단위 테스트 스크립트
"""
import sys
import os

# 프로젝트 루트를 Python path에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 이제 config와 app 모듈들을 import 할 수 있음
from app.services.dailycare.vectorstore_service import VectorStoreService

def test_vectorstore_service():
    print("=== VectorStoreService 테스트 시작 ===")
    
    try:
        # 서비스 인스턴스 생성
        print("1. VectorStoreService 인스턴스 생성...")
        service = VectorStoreService()
        print("   ✅ 성공")
        
        # 벡터 DB 초기화
        print("2. 벡터 DB 초기화...")
        store = service.initialize_vector_db()
        print("   ✅ 성공")
        
        # 문서 로딩 테스트
        print("3. 문서 로딩 테스트...")
        documents = service.load_documents()
        print(f"   ✅ 총 {len(documents)}개 문서 청크 로딩 완료")
        
        # 검색 테스트
        if store and len(documents) > 0:
            print("4. 유사도 검색 테스트...")
            results = store.similarity_search("반려동물 건강", k=3)
            print(f"   ✅ {len(results)}개 검색 결과 반환")
            
            for i, doc in enumerate(results):
                print(f"   - 결과 {i+1}: {doc.page_content[:100]}...")
                print(f"     메타데이터: {doc.metadata}")
        
        print("\n=== 모든 테스트 완료 ===")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vectorstore_service()