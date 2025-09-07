import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.dailycare.vectorstore_service import VectorStoreService

class TestVectorStoreService:
    
    @pytest.fixture
    def mock_config(self):
        """Config 모킹"""
        with patch('app.services.dailycare.vectorstore_service.Config') as mock_config:
            mock_config.DOCUMENTS_PATH = "test_documents"
            mock_config.VECTOR_DB = "test_vectordb" 
            mock_config.COLLECTION_NAME = "test_collection"
            mock_config.OPENAI_API_KEY = "test_api_key"
            yield mock_config
    
    @pytest.fixture
    def service(self, mock_config):
        """VectorStoreService 인스턴스"""
        with patch('app.services.dailycare.vectorstore_service.OpenAIEmbeddings'):
            return VectorStoreService()
    
    def test_init(self, service, mock_config):
        """초기화 테스트"""
        assert service.documents_path == "test_documents"
        assert service.vector_db == "test_vectordb"
        assert service.collection_name == "test_collection"
        assert service.store is None
    
    @patch('app.services.dailycare.vectorstore_service.os.path.exists')
    @patch('app.services.dailycare.vectorstore_service.os.makedirs')
    def test_initialize_vector_db_new(self, mock_makedirs, mock_exists, service):
        """새 벡터DB 생성 테스트"""
        mock_exists.return_value = False
        
        with patch.object(service, 'create_vector_db') as mock_create:
            mock_create.return_value = Mock()
            result = service.initialize_vector_db()
            
            mock_makedirs.assert_called_once()
            mock_create.assert_called_once()
            assert result is not None
    
    def test_remove_metadata_blocks(self, service):
        """메타데이터 블록 제거 테스트"""
        content = """---
metadata:
  title: "테스트"
  categories: ["pet", "health"]
---

# 제목
실제 내용입니다."""
        
        cleaned = service.remove_metadata_blocks(content)
        assert "metadata:" not in cleaned
        assert "# 제목" in cleaned
        assert "실제 내용입니다." in cleaned
    
    def test_parse_yaml_list(self, service):
        """YAML 리스트 파싱 테스트"""
        # 리스트 형태
        result1 = service.parse_yaml_list('["pet", "health", "care"]')
        assert result1 == ["pet", "health", "care"]
        
        # 단일 값
        result2 = service.parse_yaml_list('single_value')
        assert result2 == ["single_value"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])