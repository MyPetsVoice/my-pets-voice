#!/bin/bash

# 원격에서 GitHub 배포 실행 스크립트
# 사용법: ./remote-github-deploy.sh your-key.pem ubuntu@your-ec2-ip

KEY_FILE=$1
EC2_HOST=$2

if [ $# -ne 2 ]; then
    echo "사용법: $0 <key-file> <user@ec2-ip>"
    echo "예시: $0 my-key.pem ubuntu@1.2.3.4"
    exit 1
fi

echo "🚀 EC2에서 GitHub 배포를 시작합니다..."

# github-deploy.sh 스크립트를 EC2에 업로드
scp -i $KEY_FILE github-deploy.sh $EC2_HOST:~/

# EC2에서 GitHub 배포 실행
ssh -i $KEY_FILE $EC2_HOST << 'EOF'
chmod +x github-deploy.sh
./github-deploy.sh
EOF

echo "✅ 원격 GitHub 배포 완료!"