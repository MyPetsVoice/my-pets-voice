#!/bin/bash

# EC2 퍼블릭 IP로 환경변수 자동 업데이트 스크립트

# EC2 퍼블릭 IP 가져오기
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com/)

if [ -z "$PUBLIC_IP" ]; then
    echo "❌ 퍼블릭 IP를 가져올 수 없습니다."
    exit 1
fi

echo "🌐 감지된 퍼블릭 IP: $PUBLIC_IP"

# .env.production 파일에서 KAKAO_REDIRECT_URI 업데이트
if [ -f ".env.production" ]; then
    sed -i "s|KAKAO_REDIRECT_URI=.*|KAKAO_REDIRECT_URI=http://$PUBLIC_IP/auth/kakao/callback|" .env.production
    echo "✅ .env.production 파일이 업데이트되었습니다."
    echo "📝 카카오 개발자 콘솔에서 다음 URI를 등록하세요:"
    echo "   http://$PUBLIC_IP/auth/kakao/callback"
else
    echo "❌ .env.production 파일을 찾을 수 없습니다."
    exit 1
fi