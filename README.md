# 🐾 MyPet's Voice

반려동물과의 특별한 소통을 위한 AI 플랫폼

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)](https://openai.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-purple.svg)](https://langchain.com/)

## 📖 프로젝트 소개

**MyPet's Voice**는 최신 AI 기술을 활용하여 반려동물과의 소통을 혁신하는 웹 애플리케이션입니다. 반려동물의 고유한 성격과 특성을 기반으로 개성 있는 AI 페르소나를 생성하고, 실시간 채팅부터 건강 관리, 일기 작성까지 종합적인 반려동물 케어 서비스를 제공합니다.

### ✨ 주요 기능

#### 🤖 **AI 페르소나 & 실시간 채팅**
- **개성 있는 페르소나**: 반려동물의 성격, 말투, 선호도를 반영한 고유한 AI 캐릭터
- **실시간 대화**: SocketIO 기반 실시간 채팅으로 자연스러운 소통
- **음성 지원**: OpenAI TTS를 통한 반려동물 목소리로 음성 대화
- **대화 기록**: LangChain을 활용한 대화 맥락 유지 및 학습

#### 📖 **반려동물 일기 시스템**
- **AI 일기 변환**: 사용자가 작성한 일기를 반려동물 관점으로 자동 변환
- **사진 업로드**: 일기와 함께 추억을 담은 사진 첨부
- **감정 분석**: 기분과 날씨 정보를 포함한 감성적 일기 작성
- **페이지네이션**: 효율적인 일기 목록 관리

#### 🏥 **스마트 헬스케어**
- **종합 건강 기록**: 의료 기록, 예방접종, 알레르기, 복용 약물 관리
- **AI 건강 상담**: GPT 기반 건강 조언 및 응급 상황 대응 가이드
- **벡터 검색**: ChromaDB를 활용한 전문 의료 정보 검색
- **할일 관리**: 건강 관련 투두리스트 및 알림 시스템

#### 👤 **마이페이지 & 프로필 관리**
- **다중 펫 관리**: 여러 마리의 반려동물 정보 통합 관리
- **상세 프로필**: 종류, 품종, 나이, 성별, 중성화 여부 등 세부 정보
- **사진 관리**: 프로필 사진 업로드 및 갤러리 기능

## 🛠 기술 스택

### **Backend Framework**
- **Flask 3.0.0**: 모듈러 구조의 웹 프레임워크
- **Flask-SocketIO 5.3.6**: 실시간 양방향 통신
- **SQLAlchemy 2.0.42**: 현대적인 ORM 및 데이터베이스 관리
- **PostgreSQL**: 확장성 있는 관계형 데이터베이스

### **AI/ML Stack**
- **OpenAI GPT-4o-mini**: 대화형 AI 및 자연어 처리
- **OpenAI TTS**: 고품질 음성 합성
- **LangChain**: AI 워크플로우 오케스트레이션 및 RAG 구현
- **ChromaDB**: 벡터 데이터베이스 및 의미 검색
- **LangSmith**: AI 성능 모니터링 및 추적

### **Authentication & Integration**
- **Kakao OAuth 2.0**: 소셜 로그인 및 사용자 인증
- **Session Management**: 보안 세션 관리

### **Development & Monitoring**
- **Environment Configuration**: 다중 환경 지원
- **Comprehensive Logging**: 전사 로깅 시스템
- **Error Handling**: 강력한 예외 처리 및 복구

## 🚀 빠른 시작

### 사전 요구사항

- Python 3.11+
- PostgreSQL 데이터베이스
- OpenAI API 키
- Kakao Developers 앱 등록

### 설치 및 실행

1. **저장소 클론**
   ```bash
   git clone https://github.com/MyPetsVoice/my-pets-voice.git
   cd my-pets-voice
   ```

2. **가상 환경 설정**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **환경 변수 설정**
   ```bash
   cp .env.example .env
   # .env 파일에서 다음 값들을 설정하세요:
   # - SESSION_SECRET_KEY
   # - DATABASE_URL
   # - OPENAI_API_KEY
   # - KAKAO_REST_API_KEY
   # - KAKAO_CLIENT_SECRET
   # - KAKAO_REDIRECT_URI
   ```

5. **데이터베이스 초기화**
   ```bash
   python -c "from app import create_app; from app.models import init_db; app, _ = create_app(); init_db(app)"
   ```

6. **벡터 데이터베이스 준비**
   ```bash
   # RAG용 문서 데이터를 data/ 폴더에 준비
   mkdir -p data/rag_data
   # 펫 케어 관련 문서들을 data/rag_data/ 에 배치
   ```

7. **애플리케이션 실행**
   ```bash
   python run.py
   ```

8. **브라우저에서 확인**
   ```
   http://localhost:5000
   ```

## 📁 프로젝트 구조

```
my-pets-voice/
├── app/
│   ├── models/                    # 데이터베이스 모델
│   │   ├── user.py               # 사용자 모델
│   │   ├── pet.py                # 펫 정보 모델
│   │   ├── pet_persona.py        # AI 페르소나 모델
│   │   ├── diary.py              # 일기 모델
│   │   ├── chat_history.py       # 채팅 기록 모델
│   │   └── dailycare/            # 건강관리 모델들
│   ├── routes/                   # API 엔드포인트
│   │   ├── auth/                 # 인증 관련 라우트
│   │   ├── chat/                 # 채팅 API
│   │   ├── diary/                # 일기 API
│   │   ├── dailycare/            # 건강관리 API
│   │   ├── mypage/               # 마이페이지 API
│   │   └── weather/              # 날씨 API
│   ├── services/                 # 비즈니스 로직
│   │   ├── chat/                 # AI 채팅 서비스
│   │   ├── dailycare/            # 건강관리 AI 서비스
│   │   ├── diary/                # 일기 처리 서비스
│   │   ├── persona/              # 페르소나 관리
│   │   └── common/               # 공통 유틸리티
│   ├── static/                   # 정적 파일
│   │   ├── css/                  # 스타일시트
│   │   ├── js/                   # JavaScript
│   │   ├── images/               # 이미지 파일
│   │   └── uploads/              # 업로드된 파일
│   └── templates/                # HTML 템플릿
├── data/                         # RAG용 데이터
│   └── rag_data/                # 벡터 검색용 문서들
├── config.py                     # 애플리케이션 설정
├── requirements.txt              # Python 의존성
└── run.py                       # 애플리케이션 엔트리포인트
```

## 🎯 핵심 기능 상세

### AI 채팅 시스템
- **LangChain 기반**: RunnableWithMessageHistory를 활용한 대화 맥락 유지
- **페르소나 적용**: 각 펫의 고유한 성격과 말투를 반영한 응답 생성
- **실시간 통신**: SocketIO를 통한 끊김 없는 대화 경험
- **TTS 통합**: 음성으로 듣는 반려동물의 목소리

### RAG 기반 건강 상담
- **벡터 검색**: ChromaDB와 OpenAI 임베딩을 활용한 의미 기반 검색
- **전문 지식**: 수의학 정보와 펫 케어 가이드 데이터베이스
- **개인화**: 각 펫의 건강 기록을 고려한 맞춤형 조언

### 스마트 일기 시스템
- **AI 변환**: 사용자 관점의 일기를 펫 관점으로 자연스럽게 변환
- **멀티미디어**: 텍스트와 이미지를 함께 저장
- **감정 분석**: 일기 내용의 감정 상태 파악 및 분류

## 🔧 환경 설정

### 필수 환경 변수

```env
# Flask 설정
FLASK_ENV=development
SESSION_SECRET_KEY=your-secret-key

# 데이터베이스
DATABASE_URL=postgresql://user:password@localhost:5432/mypetsvoice

# OpenAI API
OPENAI_API_KEY=your-openai-api-key

# Kakao OAuth
KAKAO_REST_API_KEY=your-kakao-rest-api-key
KAKAO_CLIENT_SECRET=your-kakao-client-secret
KAKAO_REDIRECT_URI=http://localhost:5000/auth/kakao/callback

# LangSmith (선택사항)
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGSMITH_PROJECT=mypetsvoice
LANGSMITH_TRACING=true

# 벡터DB 및 문서 경로
VECTOR_DB=./vector_db
COLLECTION_NAME=mypetsvoice_docs
DOCUMENTS_PATH=./data

# 로깅
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### API 키 발급 방법

1. **OpenAI API**: [OpenAI Platform](https://platform.openai.com/)에서 발급
2. **Kakao OAuth**: [Kakao Developers](https://developers.kakao.com/)에서 앱 생성 후 발급
3. **LangSmith**: [LangSmith](https://smith.langchain.com/)에서 프로젝트 생성 후 발급

## 🧪 개발 및 테스트

### 로컬 개발 환경
```bash
# 개발 모드로 실행 (자동 리로드)
FLASK_ENV=development python run.py

# 디버그 모드
FLASK_DEBUG=true python run.py
```

### 로깅 확인
```bash
# 실시간 로그 모니터링
tail -f logs/app.log

# 에러 로그만 필터링
grep ERROR logs/app.log
```

## 🔒 보안 고려사항

- **OAuth 인증**: 카카오 소셜 로그인으로 안전한 사용자 인증
- **세션 보안**: Flask 세션을 통한 상태 관리
- **API 키 보호**: 환경 변수를 통한 민감 정보 관리
- **입력 검증**: 사용자 입력에 대한 철저한 검증 및 필터링
- **파일 업로드**: 안전한 파일 확장자 및 크기 제한

## 🤝 기여하기

1. **Fork** 이 저장소
2. **Feature Branch** 생성 (`git checkout -b feature/새기능`)
3. **변경사항 커밋** (`git commit -m 'feat: 새로운 기능 추가'`)
4. **브랜치에 Push** (`git push origin feature/새기능`)
5. **Pull Request** 생성

### 개발 가이드라인
- **코드 스타일**: PEP 8 준수
- **커밋 메시지**: Conventional Commits 형식 사용
- **문서화**: 새로운 기능에 대한 문서 업데이트 필수
- **테스트**: 기능 추가 시 적절한 테스트 코드 작성

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 👥 개발팀

- **김태민**: Project Lead & Full-stack Development
- **신준형**: Product Planning & UX Design  
- **현지윤**: AI Model Development & Integration

## 📞 지원 및 문의

- **GitHub Issues**: [이슈 제보](https://github.com/MyPetsVoice/my-pets-voice/issues)
- **이메일**: contact@mypetsvoice.com
- **문서**: [프로젝트 위키](https://github.com/MyPetsVoice/my-pets-voice/wiki)

---

<div align="center">

**🐾 소중한 반려동물과의 특별한 소통, MyPet's Voice와 함께하세요! 🐾**

[⭐ 스타 주기](https://github.com/MyPetsVoice/my-pets-voice) • [🐛 버그 신고](https://github.com/MyPetsVoice/my-pets-voice/issues) • [💡 기능 제안](https://github.com/MyPetsVoice/my-pets-voice/discussions)

</div>