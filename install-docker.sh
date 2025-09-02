#!/bin/bash

# EC2 Ubuntu에 Docker 설치 스크립트

set -e

echo "🐳 Docker 설치를 시작합니다..."

# 시스템 업데이트
echo "📦 시스템 패키지를 업데이트합니다..."
sudo apt update

# 필요한 패키지 설치
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Docker GPG 키 추가
echo "🔑 Docker GPG 키를 추가합니다..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Docker 저장소 추가
echo "📋 Docker 저장소를 추가합니다..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 패키지 목록 업데이트
sudo apt update

# Docker 설치
echo "🐳 Docker를 설치합니다..."
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Docker 서비스 시작 및 활성화
echo "▶️ Docker 서비스를 시작합니다..."
sudo systemctl start docker
sudo systemctl enable docker

# 현재 사용자를 docker 그룹에 추가
echo "👤 사용자를 docker 그룹에 추가합니다..."
sudo usermod -aG docker $USER

# Docker 설치 확인
echo "✅ Docker 설치를 확인합니다..."
sudo docker --version
sudo docker compose version

echo "🎉 Docker 설치 완료!"
echo "⚠️  변경사항을 적용하려면 로그아웃 후 다시 로그인하거나 다음 명령어를 실행하세요:"
echo "   newgrp docker"