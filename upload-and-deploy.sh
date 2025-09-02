#!/bin/bash

# 로컬 소스코드를 EC2에 업로드하고 배포하는 스크립트
# 사용법: ./upload-and-deploy.sh your-key.pem ubuntu@your-ec2-ip

set -e

if [ $# -ne 2 ]; then
    echo "사용법: $0 <key-file> <user@ec2-ip>"
    echo "예시: $0 my-key.pem ubuntu@1.2.3.4"
    exit 1
fi

KEY_FILE=$1
EC2_HOST=$2

echo "🚀 로컬 소스코드를 EC2에 업로드하고 배포합니다..."

# 소스코드 동기화 (.env.production 포함)
echo "📤 소스코드를 업로드합니다..."
rsync -avz -e "ssh -i $KEY_FILE" \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='venv' \
  --exclude='node_modules' \
  --exclude='logs' \
  --include='.env.production' \
  ./ $EC2_HOST:~/my-pets-voice/

# EC2에서 배포 실행
echo "🔧 EC2에서 배포를 실행합니다..."
ssh -i $KEY_FILE $EC2_HOST << 'EOF'
cd ~/my-pets-voice
chmod +x update-ip.sh deploy-aws.sh
./update-ip.sh
sudo ./deploy-aws.sh
EOF

echo "✅ 업로드 및 배포 완료!"
echo "🌐 애플리케이션 확인: http://$(ssh -i $KEY_FILE $EC2_HOST 'curl -s http://checkip.amazonaws.com/')"