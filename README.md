# 🐾 MyPet's Voice

반려동물과의 특별한 소통을 위한 AI 플랫폼

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)

## 📖 프로젝트 소개

MyPet's Voice는 AI 기술을 활용하여 반려동물의 마음을 이해하고 소통할 수 있도록 돕는 웹 애플리케이션입니다. 반려동물의 성격과 특성을 분석하여 개성 있는 페르소나를 생성하고, 일상 관리부터 건강 케어까지 종합적인 반려동물 관리 서비스를 제공합니다.

### ✨ 주요 기능

- **🤖 AI 페르소나 생성**: 반려동물의 성격과 특성을 기반으로 한 개성 있는 AI 페르소나
- **💬 실시간 채팅**: 반려동물의 관점에서 대화하는 AI 채팅 시스템
- **📖 반려동물 일기**: 사용자와 AI가 함께 작성하는 반려동물 일기
- **🏥 데일리 케어**: 건강 기록, 의료 정보, 일정 관리
- **📊 건강 분석 및 상담**: AI 기반 건강 상태 분석 및 조언
- **👤 마이페이지**: 반려동물 프로필 및 페르소나 관리

## 🛠 기술 스택

### Backend
- **Framework**: Flask 2.3+
- **Database**: SQLite (개발) / PostgreSQL (프로덕션)
- **ORM**: SQLAlchemy
- **Authentication**: Kakao OAuth 2.0
- **AI Integration**: OpenAI GPT API, LangChain

### Frontend
- **Template Engine**: Jinja2
- **Styling**: Tailwind CSS
- **JavaScript**: Vanilla JS, Socket.IO
- **Icons**: Font Awesome

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx
- **Deployment**: AWS EC2, RDS
- **Process Management**: Gunicorn

## 🚀 빠른 시작

### 사전 요구사항

- Python 3.11+
- Docker & Docker Compose (선택사항)
- PostgreSQL (프로덕션용)

### 로컬 개발 환경 설정

1. **저장소 클론**
   ```bash
   git clone https://github.com/MyPetsVoice/my-pets-voice.git
   cd my-pets-voice
   ```

2. **가상 환경 생성 및 활성화**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **환경 변수 설정**
   ```bash
   cp .env.example .env
   # .env 파일을 열어서 실제 API 키들을 입력하세요
   ```

5. **데이터베이스 초기화**
   ```bash
   python -c "from app import create_app; from app.models import init_db; app, _ = create_app(); init_db(app)"
   ```

6. **애플리케이션 실행**
   ```bash
   python run.py
   ```

7. **브라우저에서 확인**
   ```
   http://localhost:5000
   ```

## 🐳 Docker를 사용한 배포

### 개발 환경
```bash
docker-compose up -d
```

### 프로덕션 환경
```bash
# 환경 변수 설정
cp .env.example .env.production
# .env.production 파일 수정

# 배포 스크립트 실행
chmod +x deploy.sh
./deploy.sh
```

## 📁 프로젝트 구조

```
my-pets-voice/
├── app/
│   ├── models/           # 데이터베이스 모델
│   ├── routes/           # 라우트 및 블루프린트
│   ├── services/         # 비즈니스 로직
│   ├── static/           # 정적 파일 (CSS, JS, 이미지)
│   ├── templates/        # HTML 템플릿
│   └── __init__.py       # Flask 앱 팩토리
├── config.py             # 설정 파일
├── run.py               # 애플리케이션 진입점
├── requirements.txt      # Python 패키지 의존성
├── Dockerfile           # Docker 이미지 설정
├── docker-compose.yml   # Docker Compose 설정
└── README.md           # 프로젝트 문서
```

## 🔧 주요 설정

### 환경 변수

| 변수명 | 설명 | 필수 |
|--------|------|------|
| `FLASK_ENV` | Flask 환경 (development/production) | ✅ |
| `SESSION_SECRET_KEY` | 세션 암호화 키 | ✅ |
| `DATABASE_URL` | 데이터베이스 연결 URL | ✅ |
| `OPENAI_API_KEY` | OpenAI API 키 | ✅ |
| `KAKAO_REST_API_KEY` | 카카오 REST API 키 | ✅ |
| `KAKAO_CLIENT_SECRET` | 카카오 클라이언트 시크릿 | ✅ |
| `KAKAO_REDIRECT_URI` | 카카오 리다이렉트 URI | ✅ |

### API 키 설정 방법

1. **OpenAI API**
   - [OpenAI Platform](https://platform.openai.com/)에서 API 키 발급
   - `.env` 파일에 `OPENAI_API_KEY` 설정

2. **Kakao OAuth**
   - [Kakao Developers](https://developers.kakao.com/)에서 앱 생성
   - REST API 키 및 클라이언트 시크릿 발급
   - 리다이렉트 URI 설정: `http://localhost:5000/auth/kakao/callback`

## 🎯 주요 기능 상세

### 페르소나 생성 시스템
- 반려동물의 기본 정보 (종류, 품종, 나이, 성격)를 기반으로 AI 페르소나 생성
- 말투, 성격, 선호도 등을 세밀하게 설정 가능
- 실제 반려동물의 행동 패턴을 학습하여 더욱 현실적인 대화 구현

### AI 채팅 시스템
- LangChain과 OpenAI GPT를 활용한 자연스러운 대화
- 반려동물의 페르소나에 맞는 말투와 반응
- 실시간 WebSocket 통신으로 끊김 없는 대화 경험

### 건강 관리 시스템
- 일일 건강 기록 (식사량, 급수량, 배변 상태, 체중, 운동량)
- 의료 정보 관리 (알레르기, 질병, 수술, 예방접종, 복용약물)
- AI 기반 건강 상담 및 조언

### 일기 시스템
- 사용자가 작성한 일기를 AI가 반려동물 관점으로 재작성
- 감정 분석 및 기분 태그 자동 생성
- 사진 업로드 및 관리 기능

## 🧪 테스트

```bash
# 단위 테스트 실행
python -m pytest test/

# 특정 테스트 파일 실행
python -m pytest test/test_pet_models.py -v
```

## 📈 성능 최적화

- **데이터베이스**: SQLAlchemy ORM 최적화, 연결 풀링
- **캐싱**: Flask-Caching을 통한 API 응답 캐싱
- **정적 파일**: Nginx를 통한 정적 파일 서빙 및 압축
- **비동기 처리**: Celery를 통한 백그라운드 작업 처리 (예정)

## 🔒 보안

- **인증**: Kakao OAuth 2.0을 통한 안전한 로그인
- **세션 관리**: Flask-Session을 통한 보안 세션 관리
- **데이터 검증**: WTForms를 통한 입력 데이터 검증
- **SQL 인젝션 방지**: SQLAlchemy ORM 사용
- **HTTPS**: 프로덕션 환경에서 SSL/TLS 적용

## 🚀 배포 가이드

### AWS EC2 배포

1. **EC2 인스턴스 설정**
   - Ubuntu 20.04+ 추천
   - 최소 t3.small (2GB RAM) 인스턴스
   - 보안 그룹에서 80, 443 포트 오픈

2. **환경 설정**
   ```bash
   # Docker 설치
   sudo apt update
   sudo apt install docker.io docker-compose
   
   # 프로젝트 클론
   git clone https://github.com/MyPetsVoice/my-pets-voice.git
   cd my-pets-voice
   
   # 환경 변수 설정
   cp .env.example .env.production
   vi .env.production  # 실제 값으로 수정
   
   # SSL 인증서 설정 (Let's Encrypt 사용)
   sudo apt install certbot
   sudo certbot certonly --standalone -d your-domain.com
   ```

3. **배포 실행**
   ```bash
   chmod +x deploy.sh
   sudo ./deploy.sh
   ```

### Docker Hub 배포

```bash
# 이미지 빌드
docker build -t mypetsvoice/app:latest .

# Docker Hub에 푸시
docker push mypetsvoice/app:latest
```

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 개발 가이드라인

- 코드 스타일: PEP 8 준수
- 커밋 메시지: [Conventional Commits](https://www.conventionalcommits.org/) 형식
- 테스트: 새로운 기능에 대한 테스트 코드 작성 필수

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 👥 팀

- **김태민(팀장)**: Full-stack Development
- **신준형**: Product Planning & UX Design
- **현지윤**: AI Model Development & Integration

## 📞 지원 및 문의

- **이슈 리포트**: [GitHub Issues](https://github.com/MyPetsVoice/my-pets-voice/issues)
- **이메일**: contact@mypetsvoice.com
- **문서**: [위키](https://github.com/MyPetsVoice/my-pets-voice/wiki)

## 🏆 로드맵

### v1.0 (현재)
- ✅ 기본 페르소나 생성
- ✅ AI 채팅 시스템
- ✅ 건강 관리 기능
- ✅ 일기 시스템

---

<div align="center">

**🐾 소중한 반려동물과의 특별한 소통, MyPet's Voice와 함께하세요! 🐾**

[⭐ 스타 주기](https://github.com/MyPetsVoice/my-pets-voice) • [🐛 버그 신고](https://github.com/MyPetsVoice/my-pets-voice/issues) • [💡 기능 제안](https://github.com/MyPetsVoice/my-pets-voice/discussions)

</div>