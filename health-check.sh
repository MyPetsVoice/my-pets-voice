#!/bin/bash

# MyPet's Voice 헬스체크 및 모니터링 스크립트

set -e

echo "🏥 MyPet's Voice 헬스체크를 시작합니다..."

# 컨테이너 상태 확인
echo "📊 컨테이너 상태:"
docker compose -f docker-compose.aws.yml ps

# 애플리케이션 헬스체크
echo "🌐 애플리케이션 헬스체크:"
if curl -f http://localhost/ > /dev/null 2>&1; then
    echo "✅ 웹 애플리케이션이 정상 작동 중입니다"
else
    echo "❌ 웹 애플리케이션에 접근할 수 없습니다"
    echo "📋 최근 로그:"
    docker compose -f docker-compose.aws.yml logs --tail=10 web
    exit 1
fi

# 디스크 사용량 확인
echo "💾 디스크 사용량:"
df -h /

# 메모리 사용량 확인
echo "🧠 메모리 사용량:"
free -h

# Docker 리소스 정리 (필요시)
echo "🧹 Docker 리소스 정리 (미사용 이미지/컨테이너):"
docker system prune -f --volumes

echo "✅ 헬스체크 완료!"