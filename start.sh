#!/bin/bash

# STORM Research Assistant 인터랙티브 서버 시작 스크립트

echo "🌟 STORM Research Assistant 인터랙티브 서버 시작 중..."

# 환경 변수 확인
if [ ! -f .env ]; then
    echo "❌ .env 파일이 없습니다. 환경 변수를 설정해주세요."
    exit 1
fi

# 필요한 환경 변수 확인
echo "📋 환경 변수 확인 중..."
if [ -z "$AZURE_OPENAI_ENDPOINT" ] || [ -z "$AZURE_OPENAI_DEPLOYMENT" ]; then
    echo "⚠️  Azure OpenAI 환경 변수가 설정되지 않았습니다."
    echo "   AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT 등을 확인해주세요."
fi

if [ -z "$TAVILY_API_KEY" ]; then
    echo "⚠️  TAVILY_API_KEY가 설정되지 않았습니다."
fi

# uv 환경 확인 및 의존성 동기화
echo "🔧 uv 환경 확인 중..."
if command -v uv &> /dev/null; then
    echo "✅ uv 패키지 매니저를 사용합니다."
    # uv sync를 통해 의존성 동기화 (조용히)
    uv sync --quiet
else
    echo "⚠️  uv가 설치되지 않았습니다. 가상환경을 사용합니다."
    # 가상환경 활성화 (선택사항)
    if [ -d "venv" ]; then
        echo "🔧 가상환경 활성화 중..."
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        echo "🔧 가상환경 활성화 중..."
        source .venv/bin/activate
    fi
fi

# 서버 시작
echo "🚀 서버 시작 중... (포트: 8002)"
echo "   - 인터랙티브 모드: http://localhost:8002"
echo "   - WebSocket 연결: ws://localhost:8002/ws/{session_id}"
echo "   - 중지하려면 Ctrl+C 또는 ./stop.sh 실행"
echo ""

# 백그라운드에서 서버 실행하고 PID 저장
if command -v uv &> /dev/null; then
    nohup uv run uvicorn app_interactive:app --host 0.0.0.0 --port 8002 > server.log 2>&1 &
else
    nohup python app_interactive.py > server.log 2>&1 &
fi
echo $! > server.pid

echo "✅ 서버가 백그라운드에서 시작되었습니다."
echo "   PID: $(cat server.pid)"
echo "   로그: tail -f server.log"
echo "   중지: ./stop.sh"
echo ""
echo "🌐 브라우저에서 http://localhost:8002 접속해보세요!"