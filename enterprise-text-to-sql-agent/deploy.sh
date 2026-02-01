#!/bin/bash
# 간단한 배포 스크립트 - PATH 문제 해결용

echo "🚀 Enterprise Text-to-SQL Agent 배포 중..."
echo ""

# Docker가 실행 중인지 확인
if ! /usr/local/bin/docker info >/dev/null 2>&1; then
    echo "❌ Docker가 실행되지 않습니다. Docker Desktop을 시작하세요."
    exit 1
fi

echo "✅ Docker 실행 중"
echo ""

# Fly.io로 배포
echo "📦 Fly.io에 배포 중..."
cd /Users/eurysohn/Desktop/coding/Portfolio-/enterprise-text-to-sql-agent

# 환경 변수를 secret으로 설정 (한번만 실행하면 됨)
echo "🔑 OpenAI API 키 설정 중..."
# /opt/homebrew/bin/fly secrets set OPENAI_API_KEY=your-openai-api-key-here

echo ""  
echo "🚢 앱 배포 중..."
/opt/homebrew/bin/fly deploy

echo ""
echo "✅ 배포 완료!"
echo ""
echo "테스트:"
echo "  curl https://enterprise-text-to-sql-agent.fly.dev/health"
