#!/bin/bash

# GitHub에서 MyPet's Voice 배포 스크립트
# EC2에서 실행

set -e

REPO_URL="https://github.com/MyPetsVoice/my-pets-voice.git"
APP_DIR="my-pets-voice"

echo "🚀 GitHub에서 MyPet's Voice 배포를 시작합니다..."

# 기존 디렉토리 정리
if [ -d "$APP_DIR" ]; then
    echo "🧹 기존 디렉토리를 정리합니다..."
    sudo docker compose -f $APP_DIR/docker-compose.aws.yml down || true
    rm -rf $APP_DIR
fi

# GitHub에서 클론
echo "📥 GitHub에서 소스코드를 다운로드합니다..."
git clone $REPO_URL
cd $APP_DIR

# 환경변수 파일 확인
if [ ! -f ".env.production" ]; then
    echo "⚠️  .env.production 파일이 없습니다."
    echo "📝 템플릿을 복사합니다. 실제 값을 입력해주세요."
    cp .env.production.template .env.production
    echo "❌ .env.production 파일을 수정한 후 다시 실행해주세요."
    echo "   nano .env.production"
    exit 1
fi

# IP 자동 업데이트
echo "🌐 퍼블릭 IP를 업데이트합니다..."
chmod +x update-ip.sh
./update-ip.sh

# 배포 실행
echo "🚀 애플리케이션을 배포합니다..."
chmod +x deploy-aws.sh
sudo ./deploy-aws.sh

echo "✅ GitHub 배포 완료!"
echo "🌐 애플리케이션 URL: http://$(curl -s http://checkip.amazonaws.com/)"