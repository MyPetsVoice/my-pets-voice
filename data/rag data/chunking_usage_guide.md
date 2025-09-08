# RAG Chunking 전략 가이드

## 📋 현재 상황 분석

### 문제점
- **JSON 파일**: 키가 일관되지 않음 (`maltese_healthcare.json` vs `dog_diseases_comprehensive.json`)
- **혼합 형식**: JSON과 Markdown이 공존
- **불규칙한 구조**: 각 JSON 객체마다 다른 스키마

### 해결해야 할 과제
1. 일관된 chunking 전략 필요
2. 컨텍스트 유지하면서 의미 단위로 분할
3. 검색 효율성 최적화

---

## 🎯 권장 Chunking 전략

### **전략 1: 통합 텍스트 변환 (★★★ 추천)**

#### 장점
- **일관성**: JSON과 Markdown을 동일한 형태로 처리
- **검색 최적화**: 구조화된 컨텍스트로 검색 정확도 향상
- **유지보수성**: 단일 처리 파이프라인

#### 구현 방식
```python
# JSON 객체 변환 예시
{
  "id": "maltese_puppy_healthcare",
  "type": "dog_health",
  "content": "말티즈 퍼피 플랜 (~1세 미만) 건강관리:..."
}

# 변환 결과
"""
문서: maltese_healthcare | 유형: dog_health | ID: maltese_puppy_healthcare
분류: dog_health | 키워드: 말티즈 퍼피, 새끼 말티즈, 예방접종

말티즈 퍼피 플랜 (~1세 미만) 건강관리:

예방접종 일정:
• 1차 (종합백신+코로나 장염): 생후 6-8주
• 2차 (종합백신+코로나 장염): 생후 8-10주
...
"""
```

### **전략 2: 의미 단위 기반 Chunking**

#### JSON 처리
- **기본 단위**: 각 JSON 객체의 `content` 필드
- **크기 제한**: 512-1024 토큰
- **컨텍스트 보존**: 메타데이터(`id`, `type`) 활용

#### Markdown 처리
- **기본 단위**: 헤더(`##`, `###`) 기준 섹션
- **계층 구조**: 상위 헤더 정보를 컨텍스트로 포함
- **큰 섹션**: 문장 단위로 추가 분할

### **전략 3: 하이브리드 메타데이터 보강**

#### 메타데이터 구조
```python
metadata = {
    # 공통 정보
    'source_file': 'maltese_healthcare.json',
    'source_type': 'json',  # 또는 'markdown'
    'chunk_type': 'dog_health',
    
    # JSON 전용
    'id': 'maltese_puppy_healthcare',
    'type': 'dog_health',
    
    # Markdown 전용
    'title': '예방접종 일정',
    'level': 3,
    'parent_titles': ['건강관리 필수사항', '예방접종'],
    
    # 키워드
    'keywords': ['말티즈', '퍼피', '예방접종', '건강검진']
}
```

---

## 💻 구체적 구현 방법

### 1. 파일 처리 파이프라인

```python
from rag_chunking_strategy import UnifiedDocumentProcessor, RAGChunkProcessor

# 초기화
processor = UnifiedDocumentProcessor(chunk_size=512, overlap=50)
chunk_processor = RAGChunkProcessor()

# 모든 문서 처리
all_chunks = []
for file_path in document_files:
    chunks = processor.process_document(file_path)
    all_chunks.extend(chunks)

# 벡터화 데이터 준비
vector_data = chunk_processor.prepare_for_vectorization(all_chunks)
```

### 2. 벡터DB 저장 형식

```python
# ChromaDB 예시
import chromadb

client = chromadb.Client()
collection = client.create_collection("pet_healthcare")

for chunk in vector_data:
    collection.add(
        ids=[chunk['id']],
        documents=[chunk['text']],
        metadatas=[chunk['metadata']]
    )
```

### 3. 검색 최적화

```python
# 컨텍스트가 풍부한 검색
def search_with_context(query, collection, n_results=5):
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=['documents', 'metadatas', 'distances']
    )
    
    # 결과에 컨텍스트 정보 포함
    enriched_results = []
    for doc, metadata, distance in zip(
        results['documents'][0], 
        results['metadatas'][0], 
        results['distances'][0]
    ):
        enriched_results.append({
            'content': doc,
            'source': metadata['source_file'],
            'type': metadata['chunk_type'],
            'keywords': metadata.get('keywords', []),
            'relevance': 1 - distance
        })
    
    return enriched_results
```

---

## 🔧 실제 적용 예시

### 현재 데이터 변환 예시

#### JSON 데이터 (maltese_healthcare.json)
```json
{
  "id": "maltese_puppy_healthcare",
  "type": "dog_health",
  "content": "말티즈 퍼피 플랜 (~1세 미만) 건강관리:\n\n예방접종 일정:\n• 1차 (종합백신+코로나 장염): 생후 6-8주..."
}
```

#### 변환된 벡터화 텍스트
```
문서: maltese_healthcare | 유형: dog_health | ID: maltese_puppy_healthcare | 분류: dog_health | 키워드: 말티즈 퍼피, 새끼 말티즈, 예방접종, 중성화수술, 말티즈 건강검사

말티즈 퍼피 플랜 (~1세 미만) 건강관리:

예방접종 일정:
• 1차 (종합백신+코로나 장염): 생후 6-8주
• 2차 (종합백신+코로나 장염): 생후 8-10주
...
```

#### Markdown 데이터 (반려동물_재난_대응_가이드라인.md)
```markdown
## 재난 발생 전 준비사항
### 1. 대피 계획 세우기
- **대피시설 파악**: 재난 발생 시 반려동물과 함께 입장할 수 있는...
```

#### 변환된 벡터화 텍스트
```
문서: 반려동물_재난_대응_가이드라인 | 유형: markdown_section | 상위 섹션: 재난 발생 전 준비사항 | 제목: 1. 대피 계획 세우기 | 키워드: 1. 대피 계획 세우기, 재난 발생 전 준비사항

## 1. 대피 계획 세우기
- **대피시설 파악**: 재난 발생 시 반려동물과 함께 입장할 수 있는 집에서 가까운 대피 시설(임시주거시설) 목록을 만들어놓고...
```

---

## 🚀 구현 순서

### Phase 1: 기본 Chunking
1. `UnifiedDocumentProcessor` 구현
2. JSON과 Markdown 파일 일괄 처리
3. 기본 메타데이터 추출

### Phase 2: 고급 최적화
1. 키워드 자동 추출 (TF-IDF, 정규표현식)
2. 중복 제거 및 유사도 기반 병합
3. 동적 chunk 크기 조정

### Phase 3: 검색 최적화
1. 컨텍스트 기반 검색 구현
2. 메타데이터 필터링
3. 하이브리드 검색 (키워드 + 벡터)

---

## ✅ 권장사항

### 즉시 적용 가능한 해결책
1. **통합 처리기 사용**: `rag_chunking_strategy.py` 활용
2. **일관된 형식**: 모든 문서를 동일한 형태로 변환
3. **풍부한 메타데이터**: 검색 정확도 향상을 위한 컨텍스트 정보 포함

### 장기적 개선 방향
1. **자동화**: 새 문서 추가 시 자동 처리
2. **품질 관리**: 중복 제거 및 품질 검증
3. **성능 최적화**: 청크 크기 및 overlap 동적 조정

이 전략을 사용하면 현재의 불일치한 JSON 구조와 Markdown 혼재 문제를 해결하면서도 RAG 시스템의 검색 성능을 크게 향상시킬 수 있습니다.