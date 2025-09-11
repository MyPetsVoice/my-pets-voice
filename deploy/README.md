# 🚀 MyPet's Voice 배포 가이드

이 디렉토리는 MyPet's Voice 프로젝트의 배포 관련 파일들을 담고 있습니다.

## 📁 디렉토리 구조

```
deploy/
├── docker/                     # Docker 관련 파일
│   ├── dockerfile              # 프로덕션 Dockerfile
│   ├── .dockerignore           # Docker 빌드 제외 파일
│   ├── docker-compose.prod.yml # 프로덕션 Docker Compose
│   ├── docker-compose.aws.yml  # AWS 배포용 (레거시)
│   └── docker-compose.vector-init.yml # 벡터 DB 초기화용
├── nginx/                      # Nginx 설정
│   └── nginx.prod.conf         # 프로덕션 Nginx 설정
├── scripts/                    # 배포 스크립트
│   ├── setup-server.sh         # 서버 초기 설정
│   ├── deploy-aws.sh           # AWS 배포 스크립트 (레거시)
│   ├── update-ip.sh            # IP 업데이트 스크립트
│   ├── health-check.sh         # 헬스체크 스크립트
│   └── init_vector_db.py       # 벡터 DB 초기화 스크립트
├── workflows/                  # GitHub Actions 워크플로우
│   ├── docker-deploy.yml       # Docker Hub 기반 배포
│   └── deploy-legacy.yml       # 기존 직접 배포 방식
└── README.md                   # 이 파일
```

## 🐳 Docker Hub 배포 (권장)

### 1. GitHub Secrets 설정

Repository Settings > Secrets and variables > Actions에서 다음 변수들을 설정하세요:

#### Docker Hub 설정
```
DOCKERHUB_USERNAME=your-dockerhub-username
DOCKERHUB_TOKEN=your-dockerhub-access-token
```

#### 서버 연결 정보
```
EC2_HOST=your-server-ip
EC2_USER=your-server-username
EC2_SSH_KEY=your-private-ssh-key
```

#### 애플리케이션 환경 변수
```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SESSION_SECRET_KEY=your-session-secret
OPENAI_API_KEY=your-openai-api-key

KAKAO_REST_API_KEY=your-kakao-api-key
KAKAO_CLIENT_SECRET=your-kakao-client-secret
KAKAO_REDIRECT_URI=http://your-domain.com/auth/kakao/callback
KAKAO_LOGOUT_REDIRECT_URI=http://your-domain.com
KAPI_HOST=https://kapi.kakao.com
KAUTH_HOST=https://kauth.kakao.com

LANGCHAIN_API_KEY=your-langsmith-api-key
LANGSMITH_PROJECT=mypetsvoice
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_TRACING=true
```

### 2. 서버 초기 설정

서버에서 다음 스크립트를 실행하여 초기 설정을 완료하세요:

```bash
# 스크립트 다운로드 및 실행
wget https://raw.githubusercontent.com/MyPetsVoice/my-pets-voice/main/deploy/scripts/setup-server.sh
chmod +x setup-server.sh
./setup-server.sh
```

### 3. 자동 배포

`main` 브랜치에 푸시하면 GitHub Actions가 자동으로:

1. **테스트 실행** - pytest를 통한 코드 검증
2. **Docker 이미지 빌드** - 멀티 아키텍처 지원
3. **Docker Hub 푸시** - latest 및 커밋 해시 태그
4. **서버 배포** - 무중단 배포 수행

## ⚙️ 수동 배포

### Docker Compose 사용

```bash
# 프로젝트 루트에서 실행
cd ~/my-pets-voice

# 환경 변수 설정 (최초 1회)
cp .env.example .env.production
# .env.production 파일을 편집하여 환경 변수 설정

# Docker Hub에서 최신 이미지 pull
export DOCKERHUB_USERNAME=your-username
docker pull $DOCKERHUB_USERNAME/mypetsvoice:latest

# 서비스 시작
docker compose -f deploy/docker/docker-compose.prod.yml up -d

# 로그 확인
docker compose -f deploy/docker/docker-compose.prod.yml logs -f web
```

### 벡터 DB 초기화

처음 배포 시 또는 데이터 업데이트 시:

```bash
# 벡터 DB 초기화 (별도 컨테이너에서 실행)
docker compose -f deploy/docker/docker-compose.vector-init.yml up

# 완료 후 정리
docker compose -f deploy/docker/docker-compose.vector-init.yml down
```

## 🔧 개발 환경 설정

### 로컬 Docker 빌드

```bash
# 프로젝트 루트에서
docker build -f deploy/docker/dockerfile -t mypetsvoice:dev .

# 개발용 실행
docker run -p 5000:5000 --env-file .env mypetsvoice:dev
```

### Nginx 설정 수정

프로덕션 환경에서 Nginx 설정을 수정하려면:

```bash
# 설정 파일 편집
nano deploy/nginx/nginx.prod.conf

# 컨테이너 재시작
docker compose -f deploy/docker/docker-compose.prod.yml restart nginx
```

## 📊 모니터링 및 로그

### 컨테이너 상태 확인

```bash
# 컨테이너 상태
docker compose -f deploy/docker/docker-compose.prod.yml ps

# 실시간 로그
docker compose -f deploy/docker/docker-compose.prod.yml logs -f

# 특정 서비스 로그
docker compose -f deploy/docker/docker-compose.prod.yml logs -f web
docker compose -f deploy/docker/docker-compose.prod.yml logs -f nginx
```

### 헬스체크

```bash
# 애플리케이션 헬스체크
curl -f http://localhost/health

# 상세 헬스체크 (스크립트 사용)
./deploy/scripts/health-check.sh
```

## 🚨 트러블슈팅

### 일반적인 문제들

#### 1. 컨테이너가 시작되지 않는 경우
```bash
# 로그 확인
docker compose -f deploy/docker/docker-compose.prod.yml logs web

# 환경 변수 확인
docker compose -f deploy/docker/docker-compose.prod.yml config
```

#### 2. 벡터 DB 초기화 실패
```bash
# 수동 벡터 DB 초기화
docker run --rm \
  --env-file .env.production \
  -v $(pwd)/vector_db:/app/vector_db \
  -v $(pwd)/data:/app/data:ro \
  your-dockerhub-username/mypetsvoice:latest \
  python deploy/scripts/init_vector_db.py
```

#### 3. 권한 문제
```bash
# 업로드 디렉토리 권한 수정
sudo chown -R $USER:$USER uploads/ vector_db/ logs/
chmod -R 755 uploads/ vector_db/ logs/
```

### 로그 위치

- **애플리케이션 로그**: `logs/app.log`
- **Docker 로그**: `docker compose logs` 명령어로 확인
- **Nginx 로그**: Docker 컨테이너 내 `/var/log/nginx/`

## 🔄 롤백

배포에 문제가 발생했을 때:

```bash
# 이전 이미지로 롤백 (특정 커밋 해시 사용)
export COMMIT_HASH=previous-working-commit
docker pull your-dockerhub-username/mypetsvoice:$COMMIT_HASH

# docker-compose.prod.yml에서 이미지 태그 수정 후 재시작
docker compose -f deploy/docker/docker-compose.prod.yml down
# 이미지 태그 수정
docker compose -f deploy/docker/docker-compose.prod.yml up -d
```

## 📞 지원

배포 관련 문제가 있을 경우:

- **GitHub Issues**: [이슈 등록](https://github.com/MyPetsVoice/my-pets-voice/issues)
- **문서**: [프로젝트 위키](https://github.com/MyPetsVoice/my-pets-voice/wiki)

---

💡 **팁**: 프로덕션 배포 전에 항상 스테이징 환경에서 테스트를 진행하세요!