"""
RAG 시스템을 위한 통합 문서 처리 및 청킹 전략

이 모듈은 다양한 형식의 반려동물 관련 문서들을 
일관된 방식으로 처리하여 벡터 DB에 저장할 수 있는 
형태로 변환합니다.
"""

import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import markdown
from datetime import datetime


@dataclass
class DocumentChunk:
    """문서 청크 데이터 클래스"""
    id: str
    text: str
    metadata: Dict[str, Any]
    chunk_index: int = 0
    token_count: Optional[int] = None


class UnifiedDocumentProcessor:
    """통합 문서 처리기"""
    
    def __init__(self, 
                 chunk_size: int = 512,
                 overlap: int = 50,
                 min_chunk_size: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size
        
        # 키워드 추출을 위한 패턴
        self.keyword_patterns = [
            r'키워드[:\s]*([^\n]+)',
            r'검색 키워드[:\s]*([^\n]+)',
            r'--- 검색 키워드 ---\s*([^\n]+)',
        ]
        
    def process_document(self, file_path: Union[str, Path]) -> List[DocumentChunk]:
        """문서 파일을 처리하여 청크 리스트 반환"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
        
        if file_path.suffix.lower() == '.json':
            return self._process_json_file(file_path)
        elif file_path.suffix.lower() == '.md':
            return self._process_markdown_file(file_path)
        elif file_path.suffix.lower() == '.csv':
            return self._process_csv_file(file_path)
        else:
            # 일반 텍스트 파일로 처리
            return self._process_text_file(file_path)
    
    def _process_json_file(self, file_path: Path) -> List[DocumentChunk]:
        """JSON 파일 처리"""
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 단일 객체인지 리스트인지 확인
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                # 다른 구조라면 처리 불가
                return []
            
            for idx, item in enumerate(data):
                chunk = self._process_json_item(item, file_path, idx)
                if chunk:
                    chunks.append(chunk)
                    
        except Exception as e:
            print(f"JSON 파일 처리 중 오류: {file_path}, {e}")
            
        return chunks
    
    def _process_json_item(self, item: Dict, file_path: Path, index: int) -> Optional[DocumentChunk]:
        """개별 JSON 항목 처리"""
        if not isinstance(item, dict):
            return None
            
        # 텍스트 추출 - 다양한 키 이름 대응
        content_keys = ['content', 'text', 'description', 'details']
        content = ""
        
        for key in content_keys:
            if key in item and item[key]:
                content = str(item[key])
                break
        
        if not content.strip():
            return None
        
        # 메타데이터 추출
        metadata = self._extract_json_metadata(item, file_path)
        
        # 키워드 추출
        keywords = self._extract_keywords(content)
        if keywords:
            metadata['keywords'] = keywords
        
        # 통합된 텍스트 형식으로 변환
        unified_text = self._create_unified_text(content, metadata)
        
        # ID 생성
        chunk_id = self._generate_chunk_id(file_path, item.get('id', f'item_{index}'), index)
        
        return DocumentChunk(
            id=chunk_id,
            text=unified_text,
            metadata=metadata,
            chunk_index=index
        )
    
    def _process_markdown_file(self, file_path: Path) -> List[DocumentChunk]:
        """Markdown 파일 처리"""
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 헤더별로 섹션 분할
            sections = self._split_markdown_by_headers(content)
            
            for idx, section in enumerate(sections):
                if section['content'].strip():
                    chunk = self._create_markdown_chunk(section, file_path, idx)
                    if chunk:
                        chunks.append(chunk)
                        
        except Exception as e:
            print(f"Markdown 파일 처리 중 오류: {file_path}, {e}")
            
        return chunks
    
    def _split_markdown_by_headers(self, content: str) -> List[Dict]:
        """헤더 기준으로 Markdown 섹션 분할"""
        sections = []
        lines = content.split('\n')
        
        current_section = {
            'title': '',
            'level': 0,
            'parent_titles': [],
            'content': '',
            'line_start': 0
        }
        
        header_stack = []  # 헤더 계층 추적
        
        for line_num, line in enumerate(lines):
            header_match = re.match(r'^(#{1,6})\s+(.+)', line)
            
            if header_match:
                # 이전 섹션 저장
                if current_section['content'].strip():
                    sections.append(current_section.copy())
                
                # 새 섹션 시작
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                
                # 헤더 스택 업데이트
                header_stack = header_stack[:level-1]  # 현재 레벨 이하 제거
                if len(header_stack) == level - 1:
                    header_stack.append(title)
                
                current_section = {
                    'title': title,
                    'level': level,
                    'parent_titles': header_stack[:-1].copy(),
                    'content': line + '\n',
                    'line_start': line_num
                }
            else:
                current_section['content'] += line + '\n'
        
        # 마지막 섹션 추가
        if current_section['content'].strip():
            sections.append(current_section)
        
        return sections
    
    def _create_markdown_chunk(self, section: Dict, file_path: Path, index: int) -> Optional[DocumentChunk]:
        """Markdown 섹션으로부터 청크 생성"""
        content = section['content'].strip()
        if not content:
            return None
        
        # 너무 긴 섹션은 문장 단위로 추가 분할
        if len(content) > self.chunk_size * 2:
            return self._split_large_section(section, file_path, index)
        
        # 메타데이터 생성
        metadata = {
            'source_file': file_path.name,
            'source_type': 'markdown',
            'chunk_type': 'markdown_section',
            'title': section['title'],
            'level': section['level'],
            'parent_titles': section['parent_titles'],
            'file_path': str(file_path),
            'processed_date': datetime.now().isoformat()
        }
        
        # 키워드 추출
        keywords = self._extract_keywords(content)
        if keywords:
            metadata['keywords'] = keywords
        
        # 출처 URL 추출 (있다면)
        url = self._extract_url_from_content(content)
        if url:
            metadata['source_url'] = url
        
        # 통합된 텍스트 형식으로 변환
        unified_text = self._create_unified_text_markdown(content, metadata)
        
        # ID 생성
        chunk_id = self._generate_chunk_id(file_path, section['title'], index)
        
        return DocumentChunk(
            id=chunk_id,
            text=unified_text,
            metadata=metadata,
            chunk_index=index
        )
    
    def _split_large_section(self, section: Dict, file_path: Path, base_index: int) -> List[DocumentChunk]:
        """큰 섹션을 문장 단위로 분할"""
        chunks = []
        content = section['content']
        
        # 문장 단위로 분할 (한국어 고려)
        sentences = re.split(r'[.!?]\s+|[。！？]\s*', content)
        
        current_chunk = ""
        chunk_index = 0
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            temp_chunk = current_chunk + sentence + ". "
            
            if len(temp_chunk) > self.chunk_size and current_chunk:
                # 현재 청크 저장
                chunk = self._create_split_chunk(
                    current_chunk.strip(), section, file_path, 
                    f"{base_index}_{chunk_index}"
                )
                if chunk:
                    chunks.append(chunk)
                
                # 새 청크 시작
                current_chunk = sentence + ". "
                chunk_index += 1
            else:
                current_chunk = temp_chunk
        
        # 마지막 청크
        if current_chunk.strip():
            chunk = self._create_split_chunk(
                current_chunk.strip(), section, file_path,
                f"{base_index}_{chunk_index}"
            )
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def _create_split_chunk(self, content: str, section: Dict, file_path: Path, chunk_id: str) -> Optional[DocumentChunk]:
        """분할된 청크 생성"""
        if len(content) < self.min_chunk_size:
            return None
        
        metadata = {
            'source_file': file_path.name,
            'source_type': 'markdown',
            'chunk_type': 'markdown_subsection',
            'title': section['title'],
            'level': section['level'],
            'parent_titles': section['parent_titles'],
            'file_path': str(file_path),
            'is_split': True,
            'processed_date': datetime.now().isoformat()
        }
        
        keywords = self._extract_keywords(content)
        if keywords:
            metadata['keywords'] = keywords
        
        unified_text = self._create_unified_text_markdown(content, metadata)
        
        return DocumentChunk(
            id=self._generate_chunk_id(file_path, chunk_id),
            text=unified_text,
            metadata=metadata
        )
    
    def _extract_json_metadata(self, item: Dict, file_path: Path) -> Dict[str, Any]:
        """JSON 항목에서 메타데이터 추출"""
        metadata = {
            'source_file': file_path.name,
            'source_type': 'json',
            'file_path': str(file_path),
            'processed_date': datetime.now().isoformat()
        }
        
        # 일반적인 메타데이터 필드들
        meta_fields = ['id', 'type', 'category', 'source_url', 'source_title', 'publisher']
        
        for field in meta_fields:
            if field in item and item[field]:
                metadata[field] = item[field]
        
        # chunk_type 설정
        if 'type' in item:
            metadata['chunk_type'] = item['type']
        elif 'category' in item:
            metadata['chunk_type'] = item['category']
        else:
            metadata['chunk_type'] = 'unknown'
        
        return metadata
    
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        keywords = []
        
        # 패턴 기반 키워드 추출
        for pattern in self.keyword_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # 쉼표나 기타 구분자로 분할
                kws = re.split(r'[,，;；\|]\s*', match)
                keywords.extend([kw.strip() for kw in kws if kw.strip()])
        
        # 중복 제거 및 정리
        keywords = list(set(keywords))
        keywords = [kw for kw in keywords if len(kw) > 1]  # 너무 짧은 키워드 제외
        
        return keywords[:10]  # 최대 10개로 제한
    
    def _extract_url_from_content(self, content: str) -> Optional[str]:
        """텍스트에서 URL 추출"""
        url_pattern = r'https?://[^\s)]+|www\.[^\s)]+'
        match = re.search(url_pattern, content)
        return match.group(0) if match else None
    
    def _create_unified_text(self, content: str, metadata: Dict[str, Any]) -> str:
        """JSON 항목을 통합된 텍스트 형식으로 변환"""
        header_parts = []
        
        # 문서 기본 정보
        header_parts.append(f"문서: {metadata.get('source_file', 'unknown')}")
        
        if metadata.get('chunk_type'):
            header_parts.append(f"유형: {metadata['chunk_type']}")
        
        if metadata.get('id'):
            header_parts.append(f"ID: {metadata['id']}")
        
        # 키워드 추가
        if metadata.get('keywords'):
            keywords_str = ', '.join(metadata['keywords'])
            header_parts.append(f"키워드: {keywords_str}")
        
        # 헤더 생성
        header = ' | '.join(header_parts)
        
        # 최종 텍스트
        return f"{header}\n\n{content}"
    
    def _create_unified_text_markdown(self, content: str, metadata: Dict[str, Any]) -> str:
        """Markdown 섹션을 통합된 텍스트 형식으로 변환"""
        header_parts = []
        
        # 문서 기본 정보
        header_parts.append(f"문서: {metadata.get('source_file', 'unknown').replace('.md', '')}")
        header_parts.append(f"유형: {metadata.get('chunk_type', 'markdown')}")
        
        # 섹션 정보
        if metadata.get('parent_titles'):
            parent_path = ' > '.join(metadata['parent_titles'])
            header_parts.append(f"상위 섹션: {parent_path}")
        
        if metadata.get('title'):
            header_parts.append(f"제목: {metadata['title']}")
        
        # 키워드 추가
        if metadata.get('keywords'):
            keywords_str = ', '.join(metadata['keywords'])
            header_parts.append(f"키워드: {keywords_str}")
        
        # 헤더 생성
        header = ' | '.join(header_parts)
        
        return f"{header}\n\n{content}"
    
    def _generate_chunk_id(self, file_path: Path, item_id: str, index: int = 0) -> str:
        """고유한 청크 ID 생성"""
        base_name = file_path.stem
        clean_id = re.sub(r'[^\w\-]', '_', str(item_id))
        
        id_string = f"{base_name}_{clean_id}_{index}"
        
        # 너무 긴 ID는 해시로 축약
        if len(id_string) > 100:
            hash_suffix = hashlib.md5(id_string.encode()).hexdigest()[:8]
            id_string = f"{base_name}_{hash_suffix}"
        
        return id_string
    
    def _process_csv_file(self, file_path: Path) -> List[DocumentChunk]:
        """CSV 파일 처리 (이미 처리된 medication 데이터용)"""
        # CSV는 이미 처리된 JSON 형태가 있으므로 해당 JSON 파일을 찾아서 처리
        json_files = list(file_path.parent.glob(f"*{file_path.stem}*.json"))
        
        chunks = []
        for json_file in json_files:
            try:
                chunks.extend(self._process_json_file(json_file))
            except Exception as e:
                print(f"연결된 JSON 파일 처리 중 오류: {json_file}, {e}")
        
        return chunks
    
    def _process_text_file(self, file_path: Path) -> List[DocumentChunk]:
        """일반 텍스트 파일 처리"""
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 간단한 청킹 - 문단 단위
            paragraphs = content.split('\n\n')
            
            for idx, paragraph in enumerate(paragraphs):
                if paragraph.strip() and len(paragraph.strip()) > self.min_chunk_size:
                    metadata = {
                        'source_file': file_path.name,
                        'source_type': 'text',
                        'chunk_type': 'text_paragraph',
                        'file_path': str(file_path),
                        'processed_date': datetime.now().isoformat()
                    }
                    
                    keywords = self._extract_keywords(paragraph)
                    if keywords:
                        metadata['keywords'] = keywords
                    
                    chunk_id = self._generate_chunk_id(file_path, f"paragraph_{idx}", idx)
                    
                    chunks.append(DocumentChunk(
                        id=chunk_id,
                        text=self._create_unified_text(paragraph, metadata),
                        metadata=metadata,
                        chunk_index=idx
                    ))
                    
        except Exception as e:
            print(f"텍스트 파일 처리 중 오류: {file_path}, {e}")
            
        return chunks


class RAGChunkProcessor:
    """RAG 시스템용 청크 후처리기"""
    
    def __init__(self):
        self.similarity_threshold = 0.9  # 중복 제거 임계값
    
    def prepare_for_vectorization(self, chunks: List[DocumentChunk]) -> List[Dict[str, Any]]:
        """벡터 DB 저장을 위한 데이터 준비"""
        prepared_data = []
        
        for chunk in chunks:
            prepared_data.append({
                'id': chunk.id,
                'text': chunk.text,
                'metadata': chunk.metadata,
                'token_count': self._estimate_token_count(chunk.text)
            })
        
        return prepared_data
    
    def remove_duplicates(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """중복 청크 제거"""
        unique_chunks = []
        seen_hashes = set()
        
        for chunk in chunks:
            # 텍스트 해시 생성
            text_hash = hashlib.md5(chunk.text.encode()).hexdigest()
            
            if text_hash not in seen_hashes:
                seen_hashes.add(text_hash)
                unique_chunks.append(chunk)
        
        return unique_chunks
    
    def _estimate_token_count(self, text: str) -> int:
        """토큰 수 추정 (한국어 고려)"""
        # 한국어: 대략 1.5자 = 1토큰, 영어: 4자 = 1토큰
        korean_chars = len(re.findall(r'[가-힣]', text))
        other_chars = len(text) - korean_chars
        
        estimated_tokens = (korean_chars / 1.5) + (other_chars / 4)
        return int(estimated_tokens)


def create_metadata_schema() -> Dict[str, Any]:
    """표준 메타데이터 스키마 정의"""
    return {
        # 필수 필드
        'source_file': str,      # 원본 파일명
        'source_type': str,      # json, markdown, csv, text
        'chunk_type': str,       # 청크 유형 (dog_health, cat_health, medicine 등)
        'file_path': str,        # 전체 파일 경로
        'processed_date': str,   # 처리 날짜 (ISO format)
        
        # 선택적 필드
        'id': str,              # 원본 ID (JSON의 경우)
        'type': str,            # 원본 type 필드
        'title': str,           # 제목 (Markdown의 경우)
        'level': int,           # 헤더 레벨 (Markdown의 경우)
        'parent_titles': list,   # 상위 제목들 (Markdown의 경우)
        'keywords': list,        # 추출된 키워드들
        'source_url': str,       # 출처 URL
        'source_title': str,     # 출처 문서 제목
        'publisher': str,        # 발행처
        'is_split': bool,       # 큰 섹션에서 분할된 것인지
        'token_count': int,     # 추정 토큰 수
    }


# 사용 예시
if __name__ == "__main__":
    # 문서 처리기 초기화
    processor = UnifiedDocumentProcessor(chunk_size=512, overlap=50)
    chunk_processor = RAGChunkProcessor()
    
    # 처리할 파일들
    rag_data_path = Path("./data/rag data")
    document_files = []
    
    # 모든 문서 파일 수집
    for pattern in ["**/*.json", "**/*.md", "**/*.txt"]:
        document_files.extend(rag_data_path.glob(pattern))
    
    # 모든 문서 처리
    all_chunks = []
    for file_path in document_files:
        try:
            chunks = processor.process_document(file_path)
            all_chunks.extend(chunks)
            print(f"처리 완료: {file_path} ({len(chunks)}개 청크)")
        except Exception as e:
            print(f"처리 실패: {file_path}, 오류: {e}")
    
    # 중복 제거
    unique_chunks = chunk_processor.remove_duplicates(all_chunks)
    
    # 벡터화 준비
    vector_data = chunk_processor.prepare_for_vectorization(unique_chunks)
    
    print(f"\n처리 완료: {len(all_chunks)}개 청크 -> {len(unique_chunks)}개 고유 청크")
    print(f"벡터 DB 저장 준비 완료: {len(vector_data)}개 항목")