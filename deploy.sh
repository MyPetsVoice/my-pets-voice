#!/bin/bash

# MyPet's Voice 배포 스크립트

set -e

echo "🚀 MyPet's Voice 배포를 시작합니다..."

# 환경 변수 확인
if [ ! -f ".env.production" ]; then
    echo "❌ .env.production 파일이 없습니다. 생성해주세요."
    exit 1
fi

# Docker 및 Docker Compose 설치 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되어 있지 않습니다."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose가 설치되어 있지 않습니다."
    exit 1
fi

# 기존 컨테이너 정리 (옵션)
echo "🧹 기존 컨테이너를 정리합니다..."
docker compose -f docker-compose.prod.yml down || true

# 이미지 빌드
echo "🔨 Docker 이미지를 빌드합니다..."
docker compose -f docker-compose.prod.yml build --no-cache

# 컨테이너 실행
echo "▶️ 애플리케이션을 시작합니다..."
docker compose -f docker-compose.prod.yml up -d

# 헬스 체크
echo "🏥 애플리케이션 상태를 확인합니다..."
sleep 30

if curl -f http://localhost/ > /dev/null 2>&1; then
    echo "✅ 배포가 성공적으로 완료되었습니다!"
    echo "🌐 애플리케이션이 http://localhost에서 실행 중입니다."
else
    echo "❌ 헬스 체크 실패. 로그를 확인해주세요."
    docker compose -f docker-compose.prod.yml logs
    exit 1
fi

# 실행 중인 컨테이너 확인
echo "📋 실행 중인 컨테이너:"
docker compose -f docker-compose.prod.yml ps

echo "🎉 배포 완료!"