#!/bin/bash

# EC2 환경 설정 및 배포 통합 스크립트

set -e

echo "🚀 EC2 환경 설정 및 MyPet's Voice 배포를 시작합니다..."

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    echo "🐳 Docker를 설치합니다..."
    sudo apt update
    sudo apt install -y docker.io docker-compose-plugin
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo "✅ Docker 설치 완료"
fi

# 프로젝트 클론
echo "📥 GitHub에서 프로젝트를 클론합니다..."
if [ -d "my-pets-voice" ]; then
    rm -rf my-pets-voice
fi
git clone https://github.com/MyPetsVoice/my-pets-voice.git
cd my-pets-voice

# 환경변수 설정
if [ ! -f ".env.production" ]; then
    echo "📝 환경변수 파일을 생성합니다..."
    cp .env.production.template .env.production
    echo "❌ .env.production 파일을 수정한 후 다시 실행해주세요:"
    echo "   cd my-pets-voice && nano .env.production"
    exit 1
fi

# IP 업데이트 및 배포
echo "🌐 IP를 업데이트하고 배포합니다..."
chmod +x update-ip.sh deploy-aws.sh
./update-ip.sh
sudo -E docker compose -f docker-compose.aws.yml up -d --build

echo "🎉 배포 완료!"
echo "🌐 애플리케이션 URL: http://$(curl -s http://checkip.amazonaws.com/)"