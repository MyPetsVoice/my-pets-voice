#!/bin/bash

# 빠른 배포 스크립트 (.env.production 포함)
# 사용법: ./quick-deploy.sh your-key.pem ubuntu@your-ec2-ip

KEY_FILE=$1
EC2_HOST=$2

if [ $# -ne 2 ]; then
    echo "사용법: $0 <key-file> <user@ec2-ip>"
    exit 1
fi

echo "🚀 .env.production 포함 배포 시작..."

# 압축 및 업로드
tar -czf temp-deploy.tar.gz --exclude='.git' --exclude='venv' --exclude='__pycache__' .
scp -i $KEY_FILE temp-deploy.tar.gz $EC2_HOST:~/

# EC2에서 배포
ssh -i $KEY_FILE $EC2_HOST << 'EOF'
rm -rf my-pets-voice
mkdir my-pets-voice
tar -xzf temp-deploy.tar.gz -C my-pets-voice
cd my-pets-voice
chmod +x deploy-aws.sh
sudo ./deploy-aws.sh
rm ~/temp-deploy.tar.gz
EOF

rm temp-deploy.tar.gz
echo "✅ 배포 완료!"