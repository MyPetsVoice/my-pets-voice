# 의약품 RAG 벡터 DB 구축 가이드

## 핵심 전략

### 1. 스마트 청킹 전략 🎯

#### 제품 문서 청킹 (4단계 분할)
```
제품 1개 → 4개의 청크로 분할
├── basic_info: 제품명, 업체, 허가일, 제형
├── ingredients: 성분 정보만 별도 청크
├── usage_storage: 저장방법, 용법, 주의사항
└── summary: 전체 요약 (검색 최적화용)
```

#### 성분 문서 청킹
```
성분 문서 → 그대로 유지 (이미 최적 크기)
└── 성분별 단일 청크 (평균 100-200자)
```

### 2. 메타데이터 설계 📋

각 청크마다 다음 메타데이터 포함:
```json
{
  "doc_id": "product_0_basic",
  "doc_type": "product",
  "section": "basic_info",
  "product_name": "골든 유니온C",
  "company": "(주)우성양행",
  "source": "product_basic"
}
```

### 3. 벡터 DB 옵션 비교

| DB 타입 | 장점 | 단점 | 추천 용도 |
|---------|------|------|----------|
| **FAISS** | 빠른 검색, 로컬 저장 | 스케일링 제한 | 프로토타입, 중소규모 |
| **ChromaDB** | 메타데이터 필터링 우수 | 메모리 사용량 높음 | 개발/테스트 환경 |
| **Pinecone** | 프로덕션 최적화 | 유료, 클라우드 의존 | 상용 서비스 |

## 사용법

### 1. 환경 설정
```bash
pip install langchain faiss-cpu chromadb openai
export OPENAI_API_KEY="your-api-key"
```

### 2. 벡터 DB 구축
```python
# 벡터 DB 구축 실행
python vector_db_setup.py
```

### 3. 검색 예시
```python
from vector_db_setup import MedicineSearchEngine
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

# 벡터스토어 로드
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.load_local("medicine_faiss_db", embeddings)
search_engine = MedicineSearchEngine(vectorstore)

# 1. 제품명 검색
results = search_engine.search_by_product("골든 유니온C")

# 2. 성분 검색
results = search_engine.search_by_ingredient("비타민 C")

# 3. 업체 검색
results = search_engine.search_by_company("우성양행")

# 4. 자연어 쿼리
results = search_engine.hybrid_search("강아지 비타민 보충제")
```

## 검색 최적화 전략

### 1. 하이브리드 검색 📊
- **벡터 검색**: 의미 유사도 기반
- **키워드 검색**: 정확한 제품명/성분명 매칭
- **점수 부스팅**: 매칭 타입별 가중치 적용

### 2. 필터링 옵션
```python
# 메타데이터 필터링
results = vectorstore.similarity_search(
    "비타민 C",
    filter={
        "doc_type": "product",        # 제품 문서만
        "company": "(주)우성양행"     # 특정 업체만
    }
)
```

### 3. 검색 타입별 최적화

#### A. 제품 정보 검색
```python
# 제품명 → basic_info 청크 우선
# 성분 문의 → ingredients 청크 우선
# 사용법 문의 → usage_storage 청크 우선
```

#### B. 성분 검색
```python
# 성분명 → ingredient 타입 문서 우선
# 함유 제품 찾기 → 성분 문서에서 제품명 추출
```

#### C. 추천 시스템
```python
# 유사 성분 제품 → 벡터 유사도 활용
# 같은 업체 제품 → 메타데이터 필터링
```

## 성능 최적화 팁 🚀

### 1. 인덱스 구조
```
medicine_faiss_db/
├── index.faiss          # 벡터 인덱스
├── index.pkl           # 메타데이터
└── search_indexes.json # 키워드 인덱스
```

### 2. 메모리 최적화
- **배치 임베딩**: 1000개씩 나누어 처리
- **인덱스 캐싱**: 자주 사용하는 검색어 캐시
- **지연 로딩**: 필요시에만 전체 문서 로드

### 3. 검색 성능 향상
```python
# 1단계: 빠른 키워드 검색으로 후보군 필터링
# 2단계: 필터링된 결과에 벡터 검색 적용
# 3단계: 하이브리드 점수로 최종 랭킹
```

## 실제 사용 시나리오

### 시나리오 1: "강아지 설사에 좋은 약"
```python
query = "강아지 설사 치료"
results = search_engine.hybrid_search(query, k=5)

# 결과: 설사 관련 성분(예: 프로바이오틱스) 함유 제품들
```

### 시나리오 2: "비타민 C 함유 제품 전체"
```python
results = search_engine.search_by_ingredient("비타민 C", k=20)

# 결과: 비타민 C가 포함된 모든 제품 리스트
```

### 시나리오 3: "우성양행 제품 중 비타민 계열"
```python
results = vectorstore.similarity_search(
    "비타민",
    filter={"company": "(주)우성양행"},
    k=10
)
```

## 확장 가능성 🔮

1. **다국어 지원**: 영문 제품명 임베딩 추가
2. **이미지 검색**: 제품 이미지 벡터화
3. **리뷰 데이터**: 사용자 리뷰 통합
4. **실시간 업데이트**: 새 제품 자동 인덱싱
5. **개인화**: 사용자별 추천 시스템

## 모니터링 및 평가

### 검색 품질 측정
```python
# 정확도: 상위 K개 결과 중 관련 문서 비율
# 다양성: 서로 다른 제품/업체 결과 포함도
# 응답 시간: 평균 검색 소요 시간
```

### A/B 테스트
- 벡터 검색 vs 하이브리드 검색
- 청킹 전략별 성능 비교
- 임베딩 모델별 품질 비교