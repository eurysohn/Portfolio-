#!/bin/bash
# Fly.io 직접 배포 (권한 문제 우회)

echo "🚀 Fly.io 배포를 시작합니다..."
echo ""

cd /Users/eurysohn/Desktop/coding/Portfolio-/enterprise-text-to-sql-agent

# 먼저 API 키를 환경 변수로 설정 (secrets 대신)
echo "🔑 환경 변수 설정 중..."
echo ""
echo "다음 명령어를 터미널에서 직접 실행해주세요:"
echo ""
echo "export FLYCTL_INSTALL=/opt/homebrew"
echo "export PATH=\"/opt/homebrew/bin:\$PATH\""
echo ""
echo "그 다음:"
echo ""
echo "fly secrets set OPENAI_API_KEY='your-openai-api-key-here' --app enterprise-text-to-sql-agent"
echo ""
echo "fly deploy --app enterprise-text-to-sql-agent"
echo ""
