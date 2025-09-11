#!/usr/bin/env python3
"""
벡터 DB 초기화 스크립트
- 별도 컨테이너에서 실행하여 메인 앱 시작을 방해하지 않음
- 볼륨 마운트를 통해 영구 저장
"""

import os
import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.dailycare.vectorstore_service import VectorStoreService
from config import Config

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('/app/logs/vector_init.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

def main():
    """벡터 DB 초기화 메인 함수"""
    logger = setup_logging()
    logger.info("=== 벡터 DB 초기화 시작 ===")
    
    try:
        # 환경 변수 확인
        required_vars = ['OPENAI_API_KEY', 'DOCUMENTS_PATH', 'VECTOR_DB']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"필수 환경 변수가 누락되었습니다: {missing_vars}")
            return 1
        
        # 벡터 스토어 서비스 초기화
        vector_service = VectorStoreService()
        
        # 기존 벡터 DB 확인
        vector_db_path = Path(Config.VECTOR_DB)
        if vector_db_path.exists() and any(vector_db_path.iterdir()):
            logger.info(f"기존 벡터 DB가 발견되었습니다: {vector_db_path}")
            logger.info("기존 벡터 DB를 로드합니다...")
            
            # 기존 DB 로드 시도
            stores = vector_service.initialize_vector_db()
            
            # 각 컬렉션 상태 확인
            for collection_name, store in stores.items():
                if store:
                    try:
                        count = store._collection.count()
                        logger.info(f"{collection_name} 컬렉션: {count}개 문서")
                    except Exception as e:
                        logger.warning(f"{collection_name} 컬렉션 상태 확인 실패: {e}")
                else:
                    logger.warning(f"{collection_name} 컬렉션이 로드되지 않았습니다")
            
        else:
            logger.info("새로운 벡터 DB를 생성합니다...")
            
            # 새 벡터 DB 생성
            stores = vector_service.initialize_vector_db()
            
            if all(store is not None for store in stores.values()):
                logger.info("✅ 벡터 DB 초기화가 성공적으로 완료되었습니다!")
            else:
                logger.error("❌ 일부 컬렉션 초기화에 실패했습니다.")
                return 1
        
        logger.info("=== 벡터 DB 초기화 완료 ===")
        return 0
        
    except Exception as e:
        logger.error(f"벡터 DB 초기화 중 오류 발생: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)