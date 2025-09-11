#!/bin/bash

# 서버 초기 설정 스크립트
# EC2 서버에서 한 번만 실행하면 됩니다

set -e

echo "🚀 MyPetsVoice 서버 초기 설정 시작..."

# 1. 필요한 디렉터리 생성
echo "📁 디렉터리 구조 생성..."
mkdir -p ~/my-pets-voice/{uploads,logs,vector_db,ssl}
cd ~/my-pets-voice

# 2. 환경 설정
echo "⚙️ 환경 설정..."

# Docker와 Docker Compose 설치 확인
if ! command -v docker &> /dev/null; then
    echo "🐳 Docker 설치 중..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

if ! command -v docker compose &> /dev/null; then
    echo "🐙 Docker Compose 설치 중..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 3. Nginx 설정 다운로드 (필요시)
echo "🌐 Nginx 설정 확인..."
if [ ! -f "nginx.prod.conf" ]; then
    echo "⚠️  nginx.prod.conf 파일을 수동으로 추가해주세요"
fi

# 4. SSL 인증서 설정 안내
echo "🔒 SSL 인증서 설정..."
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    echo "⚠️  SSL 인증서가 없습니다. Let's Encrypt를 사용하려면:"
    echo "   sudo apt-get update && sudo apt-get install -y certbot"
    echo "   sudo certbot certonly --standalone -d your-domain.com"
    echo "   그 후 인증서를 ssl/ 디렉터리로 복사하세요"
fi

# 5. 데이터 디렉터리 설정
echo "📚 RAG 데이터 디렉터리 설정..."
if [ ! -d "data" ]; then
    echo "⚠️  data 디렉터리에 RAG 데이터를 업로드해주세요"
    echo "   예상 구조:"
    echo "   data/"
    echo "   ├── rag data/"
    echo "   │   ├── general_knowledge/"
    echo "   │   ├── breeds/"
    echo "   │   └── processed_medications/"
fi

# 6. 권한 설정
echo "🔧 권한 설정..."
sudo chown -R $USER:$USER ~/my-pets-voice
chmod -R 755 ~/my-pets-voice

echo "✅ 서버 초기 설정 완료!"
echo ""
echo "다음 단계:"
echo "1. GitHub에서 필요한 Secrets 설정:"
echo "   - DOCKERHUB_USERNAME"
echo "   - DOCKERHUB_TOKEN"
echo "   - DATABASE_URL"
echo "   - SESSION_SECRET_KEY"
echo "   - OPENAI_API_KEY"
echo "   - KAKAO_* 설정들"
echo "   - LANGCHAIN_API_KEY"
echo ""
echo "2. 필요시 nginx.prod.conf와 SSL 인증서 설정"
echo ""
echo "3. data 디렉터리에 RAG 데이터 업로드"
echo ""
echo "4. GitHub Actions를 통한 자동 배포 활성화"
echo ""
echo "🌐 설정이 완료되면 http://$(curl -s http://checkip.amazonaws.com/) 에서 접속 가능합니다"