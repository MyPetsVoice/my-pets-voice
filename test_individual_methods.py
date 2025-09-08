#!/usr/bin/env python3
"""
개별 메서드 테스트 스크립트
"""
import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.services.dailycare.vectorstore_service import VectorStoreService

def test_metadata_extraction():
    """메타데이터 추출만 테스트"""
    print("=== 메타데이터 추출 테스트 ===")
    
    service = VectorStoreService()
    
    sample_content = """---
metadata:
  title: "반려동물 건강 가이드"
  categories: ["pet", "health"] 
  author: "veterinarian"
---

# 반려동물 건강관리
반려동물의 건강을 위한 기본 가이드입니다."""
    
    metadata = service.extract_document_metadata(sample_content)
    print(f"추출된 메타데이터: {metadata}")
    
    cleaned_content = service.remove_metadata_blocks(sample_content)
    print(f"정리된 내용:\n{cleaned_content}")

def test_document_loading():
    """문서 로딩만 테스트"""
    print("\n=== 문서 로딩 테스트 ===")
    
    service = VectorStoreService()
    
    try:
        documents = service.load_documents()
        print(f"로딩된 문서 수: {len(documents)}")
        
        if documents:
            print("\n첫 번째 문서:")
            print(f"내용: {documents[0].page_content[:200]}...")
            print(f"메타데이터: {documents[0].metadata}")
            
    except Exception as e:
        print(f"문서 로딩 실패: {e}")

if __name__ == "__main__":
    test_metadata_extraction()
    test_document_loading()