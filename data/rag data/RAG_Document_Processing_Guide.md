# MyPetsVoice RAG 시스템 문서 처리 가이드

## 📚 개요

이 가이드는 MyPetsVoice RAG 시스템에서 반려동물 관련 문서들을 효율적으로 처리하고 벡터 DB에 저장하기 위한 완전한 워크플로우를 제공합니다.

## 🗂️ 현재 데이터 구조 분석

### 데이터 현황
```
data/rag data/
├── 📁 breeds/dog_breed/           # 견종별 건강관리 (JSON, MD)
├── 📁 disease/                    # 질병 정보 (JSON, MD)  
├── 📁 emergency/                  # 응급상황 가이드 (MD)
├── 📁 general_knowledge/          # 일반 지식 (MD)
├── 📁 healthcare/                 # 건강관리 가이드 (MD)
├── 📁 medications/                # 의약품 원본 데이터 (CSV)
├── 📁 processed_medications/      # 처리된 의약품 (JSON)
├── 📄 동물등록제.pdf              # 정부 정책 문서
├── 📄 반려생활 길잡이.pdf         # 반려생활 가이드
└── 📄 소유자준수사항.pdf          # 소유자 의무사항
```

### 파일 형식별 분포
- **JSON**: 8개 파일 (품종별 정보, 질병 정보, 의약품 데이터)
- **Markdown**: 6개 파일 (가이드, 응급상황, 건강관리)
- **CSV**: 3개 파일 (의약품 원본 데이터)
- **PDF**: 3개 파일 (정부 정책 문서)

## 🎯 Chunking 전략

### 1. 통합 텍스트 변환 전략

모든 문서를 일관된 형식으로 변환하여 검색 효율성을 극대화합니다.

#### 변환 형식 예시

**JSON → 통합 텍스트**
```
문서: maltese_healthcare | 유형: dog_health | ID: maltese_puppy_healthcare | 키워드: 말티즈, 퍼피, 예방접종

말티즈 퍼피 플랜 (~1세 미만) 건강관리:

예방접종 일정:
• 1차 (종합백신+코로나 장염): 생후 6-8주
• 2차 (종합백신+코로나 장염): 생후 8-10주
...
```

**Markdown → 통합 텍스트**
```
문서: 반려동물_재난_대응_가이드라인 | 유형: emergency | 상위 섹션: 재난 발생 전 준비사항 | 제목: 대피 계획 세우기 | 키워드: 대피 계획, 재난 준비

## 1. 대피 계획 세우기
- **대피시설 파악**: 재난 발생 시 반려동물과 함께 입장할 수 있는...
```

### 2. 파일 타입별 처리 전략

#### JSON 파일
- **청킹 단위**: 각 JSON 객체의 `content` 필드
- **크기 제한**: 512-1024 토큰
- **컨텍스트 보존**: `id`, `type` 메타데이터 활용
- **키워드 추출**: 정규표현식으로 키워드 섹션 파싱

#### Markdown 파일
- **청킹 단위**: 헤더(`##`, `###`) 기준 섹션
- **계층 구조**: 상위 헤더 정보를 컨텍스트로 포함
- **대형 섹션**: 문장 단위로 추가 분할 (512+ 토큰 시)
- **메타데이터**: 제목, 레벨, 상위 섹션 정보

#### CSV 파일 (의약품 데이터)
- **전처리**: 이미 JSON으로 변환된 데이터 활용
- **구조화**: 의약품별로 개별 청크 생성
- **메타데이터**: 제품명, 제조업체, 허가일, 출처 URL

## 🏗️ 메타데이터 스키마

### 필수 메타데이터
```json
{
  "source_file": "maltese_healthcare.json",
  "source_type": "json",
  "chunk_type": "dog_health", 
  "file_path": "/data/rag data/breeds/dog_breed/maltese_healthcare.json",
  "processed_date": "2024-09-05T14:30:00.000Z"
}
```

### 선택적 메타데이터
```json
{
  "id": "maltese_puppy_healthcare",
  "title": "말티즈 퍼피 건강관리",
  "keywords": ["말티즈", "퍼피", "예방접종"],
  "source_url": "https://medi.qia.go.kr/searchMedicine",
  "publisher": "농림축산검역본부",
  "token_count": 256,
  "quality_score": 0.9
}
```

### Chunk 타입 분류
- `dog_health`: 반려견 건강관리
- `cat_health`: 반려묘 건강관리  
- `medicine`: 동물용 의약품 정보
- `disease`: 질병 정보
- `emergency`: 응급상황 대응
- `registration`: 동물등록제
- `lifestyle`: 반려생활 가이드
- `owner_obligation`: 소유자 의무사항

## 💻 구현 가이드

### 1. 환경 설정

```bash
# 필요한 패키지 설치
pip install chromadb sentence-transformers pandas markdown

# 프로젝트 구조
project/
├── data/
│   └── rag data/          # 원본 데이터
├── processed/             # 처리된 데이터
├── vector_db/            # 벡터 DB 저장소
└── scripts/
    ├── rag_chunking_strategy.py
    └── vector_db_manager.py
```

### 2. 기본 사용법

```python
from rag_chunking_strategy import UnifiedDocumentProcessor, RAGChunkProcessor

# 문서 처리기 초기화
processor = UnifiedDocumentProcessor(
    chunk_size=512,
    overlap=50,
    min_chunk_size=100
)

# 청크 후처리기
chunk_processor = RAGChunkProcessor()

# 모든 문서 처리
all_chunks = []
for file_path in document_files:
    chunks = processor.process_document(file_path)
    all_chunks.extend(chunks)

# 중복 제거 및 품질 향상
unique_chunks = chunk_processor.remove_duplicates(all_chunks)
vector_data = chunk_processor.prepare_for_vectorization(unique_chunks)
```

### 3. 벡터 DB 저장

```python
import chromadb
from sentence_transformers import SentenceTransformer

# ChromaDB 클라이언트 초기화
client = chromadb.PersistentClient(path="./vector_db")
collection = client.get_or_create_collection("pet_healthcare")

# 임베딩 모델 (한국어 지원)
model = SentenceTransformer('jhgan/ko-sroberta-multitask')

# 벡터 DB에 저장
for chunk in vector_data:
    embedding = model.encode(chunk['text'])
    
    collection.add(
        ids=[chunk['id']],
        embeddings=[embedding.tolist()],
        documents=[chunk['text']],
        metadatas=[chunk['metadata']]
    )
```

## 🔍 검색 최적화 전략

### 1. 하이브리드 검색

```python
def hybrid_search(query: str, collection, n_results: int = 5):
    """키워드 + 벡터 유사도 기반 하이브리드 검색"""
    
    # 1. 벡터 유사도 검색
    vector_results = collection.query(
        query_texts=[query],
        n_results=n_results * 2,  # 더 많은 후보 가져오기
        include=['documents', 'metadatas', 'distances']
    )
    
    # 2. 메타데이터 필터링
    filtered_results = []
    for doc, metadata, distance in zip(
        vector_results['documents'][0],
        vector_results['metadatas'][0], 
        vector_results['distances'][0]
    ):
        # 키워드 매칭 점수 계산
        keyword_score = calculate_keyword_match(query, metadata.get('keywords', []))
        
        # 종합 점수 = 벡터 유사도 + 키워드 매칭
        final_score = (1 - distance) * 0.7 + keyword_score * 0.3
        
        filtered_results.append({
            'document': doc,
            'metadata': metadata,
            'score': final_score
        })
    
    # 점수순 정렬 후 상위 결과 반환
    filtered_results.sort(key=lambda x: x['score'], reverse=True)
    return filtered_results[:n_results]
```

### 2. 컨텍스트 보강 검색

```python
def contextual_search(query: str, collection):
    """컨텍스트 정보를 활용한 검색"""
    
    results = hybrid_search(query, collection)
    
    # 결과에 컨텍스트 정보 추가
    enriched_results = []
    for result in results:
        metadata = result['metadata']
        
        # 상위 섹션 정보 추가 (Markdown)
        context_info = ""
        if metadata.get('parent_titles'):
            context_path = ' > '.join(metadata['parent_titles'])
            context_info = f"섹션: {context_path} > {metadata.get('title', '')}"
        
        # 출처 정보 추가
        source_info = f"출처: {metadata.get('publisher', metadata.get('source_file', ''))}"
        
        enriched_results.append({
            'content': result['document'],
            'context': context_info,
            'source': source_info,
            'chunk_type': metadata.get('chunk_type'),
            'keywords': metadata.get('keywords', []),
            'score': result['score']
        })
    
    return enriched_results
```

## 📊 품질 관리

### 1. 자동 품질 평가

```python
def calculate_quality_score(chunk: DocumentChunk) -> float:
    """청크 품질 점수 계산"""
    score = 1.0
    
    # 길이 검증 (너무 짧거나 긴 청크 페널티)
    if len(chunk.text) < 50:
        score *= 0.5
    elif len(chunk.text) > 2000:
        score *= 0.8
    
    # 키워드 존재 여부
    if chunk.metadata.get('keywords'):
        score *= 1.1
    
    # 출처 정보 완성도
    if chunk.metadata.get('source_url'):
        score *= 1.05
    
    # 구조적 정보 완성도 (제목, 섹션 등)
    if chunk.metadata.get('title'):
        score *= 1.05
    
    return min(score, 1.0)
```

### 2. 중복 제거 전략

```python
def semantic_deduplication(chunks: List[DocumentChunk], threshold: float = 0.95) -> List[DocumentChunk]:
    """의미적 유사도 기반 중복 제거"""
    
    # 임베딩 생성
    texts = [chunk.text for chunk in chunks]
    embeddings = model.encode(texts)
    
    # 유사도 매트릭스 계산
    similarity_matrix = cosine_similarity(embeddings)
    
    # 중복 제거
    keep_indices = []
    for i, chunk in enumerate(chunks):
        is_duplicate = False
        for j in keep_indices:
            if similarity_matrix[i][j] > threshold:
                # 품질이 더 높은 청크 선택
                if calculate_quality_score(chunk) <= calculate_quality_score(chunks[j]):
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            keep_indices.append(i)
    
    return [chunks[i] for i in keep_indices]
```

## 🚀 배포 및 모니터링

### 1. 배치 처리 스크립트

```python
# batch_process.py
import logging
from pathlib import Path
from rag_chunking_strategy import UnifiedDocumentProcessor

def batch_process_documents():
    """모든 문서를 배치로 처리"""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    processor = UnifiedDocumentProcessor()
    rag_data_path = Path("./data/rag data")
    
    # 처리할 파일 수집
    files_to_process = []
    for pattern in ["**/*.json", "**/*.md", "**/*.txt"]:
        files_to_process.extend(rag_data_path.glob(pattern))
    
    logger.info(f"총 {len(files_to_process)}개 파일 처리 시작")
    
    processed_chunks = []
    failed_files = []
    
    for file_path in files_to_process:
        try:
            chunks = processor.process_document(file_path)
            processed_chunks.extend(chunks)
            logger.info(f"✅ {file_path.name}: {len(chunks)}개 청크 생성")
        
        except Exception as e:
            logger.error(f"❌ {file_path.name}: {str(e)}")
            failed_files.append((file_path, str(e)))
    
    logger.info(f"처리 완료: {len(processed_chunks)}개 청크 생성")
    logger.info(f"실패한 파일: {len(failed_files)}개")
    
    return processed_chunks, failed_files

if __name__ == "__main__":
    chunks, failed = batch_process_documents()
```

### 2. 모니터링 대시보드

```python
def generate_processing_report(chunks: List[DocumentChunk]) -> dict:
    """처리 결과 리포트 생성"""
    
    report = {
        'total_chunks': len(chunks),
        'by_source_type': {},
        'by_chunk_type': {},
        'average_token_count': 0,
        'quality_distribution': {'high': 0, 'medium': 0, 'low': 0}
    }
    
    # 통계 계산
    token_counts = []
    for chunk in chunks:
        # 소스 타입별
        source_type = chunk.metadata.get('source_type', 'unknown')
        report['by_source_type'][source_type] = report['by_source_type'].get(source_type, 0) + 1
        
        # 청크 타입별  
        chunk_type = chunk.metadata.get('chunk_type', 'unknown')
        report['by_chunk_type'][chunk_type] = report['by_chunk_type'].get(chunk_type, 0) + 1
        
        # 토큰 수
        if chunk.token_count:
            token_counts.append(chunk.token_count)
        
        # 품질 분포
        quality = chunk.metadata.get('quality_score', 0.5)
        if quality >= 0.8:
            report['quality_distribution']['high'] += 1
        elif quality >= 0.6:
            report['quality_distribution']['medium'] += 1
        else:
            report['quality_distribution']['low'] += 1
    
    if token_counts:
        report['average_token_count'] = sum(token_counts) / len(token_counts)
    
    return report
```

## 🔧 트러블슈팅

### 일반적인 문제들

#### 1. JSON 구조 불일치
**문제**: 서로 다른 JSON 스키마
**해결책**: `_extract_json_metadata()` 함수의 flexible key handling 활용

#### 2. 한글 인코딩 문제  
**문제**: PDF 파일명 인식 실패
**해결책**: UTF-8 인코딩 명시, 파일명 정규화

#### 3. 청크 크기 불균형
**문제**: 너무 크거나 작은 청크
**해결책**: 동적 크기 조정, `min_chunk_size` 설정

#### 4. 중복 콘텐츠
**문제**: 같은 내용의 중복 저장
**해결책**: `semantic_deduplication()` 함수 사용

### 성능 최적화

```python
# 대용량 처리를 위한 최적화
def process_large_dataset(file_paths: List[Path], batch_size: int = 100):
    """대용량 데이터셋 배치 처리"""
    
    processor = UnifiedDocumentProcessor()
    
    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i:i + batch_size]
        
        batch_chunks = []
        for file_path in batch:
            chunks = processor.process_document(file_path)
            batch_chunks.extend(chunks)
        
        # 배치별로 벡터 DB 저장
        save_to_vector_db(batch_chunks)
        
        print(f"배치 {i//batch_size + 1}/{(len(file_paths)-1)//batch_size + 1} 완료")
```

## 📋 체크리스트

### 구현 전 확인사항
- [ ] 모든 의존성 패키지 설치 완료
- [ ] 원본 데이터 백업 완료  
- [ ] 벡터 DB 저장소 경로 설정
- [ ] 임베딩 모델 다운로드 완료

### 처리 후 검증사항
- [ ] 모든 파일이 성공적으로 처리되었는지 확인
- [ ] 청크 품질 점수 분포 확인
- [ ] 중복 제거 결과 검토
- [ ] 메타데이터 완성도 검증
- [ ] 검색 성능 테스트 완료

---

이 가이드를 따라 구현하면 MyPetsVoice RAG 시스템에서 모든 반려동물 관련 문서를 효율적으로 처리하고 활용할 수 있습니다.