#!/bin/bash

# AutoGen DeepResearch 프론트엔드 시작 스크립트

echo "🌟 AutoGen DeepResearch 프론트엔드 시작 중..."

# 현재 디렉토리 확인
if [[ ! -f "package.json" ]]; then
    echo "❌ package.json이 없습니다. frontend 폴더에서 실행해주세요."
    exit 1
fi

# 프로젝트 정보 확인
if [[ -f "package.json" ]]; then
    PROJECT_NAME=$(node -p "require('./package.json').name" 2>/dev/null || echo "Unknown")
    echo "📦 프로젝트: $PROJECT_NAME"
fi

# 환경 변수 확인
echo "🔧 환경 변수 확인 중..."
if [[ -f ".env.local" ]]; then
    echo "✅ .env.local 파일을 찾았습니다."
    echo "   백엔드 API URL: ${NEXT_PUBLIC_API_URL:-http://localhost:8002}"
else
    echo "⚠️  .env.local 파일이 없습니다. 기본값을 사용합니다."
    echo "   백엔드 API URL: http://localhost:8002"
    echo ""
    echo "💡 환경 변수 설정을 위해 .env.local 파일을 생성하세요:"
    echo "   echo 'NEXT_PUBLIC_API_URL=http://localhost:8002' > .env.local"
fi

# 의존성 확인
echo "📋 의존성 확인 중..."
if [[ ! -d "node_modules" ]]; then
    echo "📦 node_modules가 없습니다. 패키지 설치 중..."
    npm install
    if [[ $? -ne 0 ]]; then
        echo "❌ 패키지 설치에 실패했습니다."
        exit 1
    fi
    echo "✅ 패키지 설치 완료"
fi

# 백엔드 서버 상태 확인
echo "🔍 백엔드 서버 상태 확인 중..."
BACKEND_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8002}"
if curl -s "${BACKEND_URL}/health" > /dev/null 2>&1; then
    echo "✅ 백엔드 서버가 실행 중입니다 (${BACKEND_URL})"
else
    echo "⚠️  백엔드 서버에 연결할 수 없습니다 (${BACKEND_URL})"
    echo "   백엔드 서버를 먼저 시작해주세요:"
    echo "   cd .. && ./start.sh"
    echo ""
    echo "❓ 백엔드 없이 프론트엔드만 실행하시겠습니까? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "❌ 취소됨"
        exit 1
    fi
fi

# 포트 확인
PORT=${PORT:-3001}
echo "🔍 포트 $PORT 확인 중..."
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "⚠️  포트 $PORT가 이미 사용 중입니다."
    echo "   사용 중인 프로세스:"
    lsof -ti:$PORT | xargs ps -p
    echo ""
    echo "❓ 기존 프로세스를 종료하고 계속하시겠습니까? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "🔄 기존 프로세스 종료 중..."
        lsof -ti:$PORT | xargs kill -9
        sleep 2
    else
        echo "💡 다른 포트를 사용하려면: PORT=3002 ./start.sh"
        exit 1
    fi
fi

# 개발 서버 시작
echo "🚀 개발 서버 시작 중... (포트: $PORT)"
echo "   - 프론트엔드: http://localhost:$PORT"
echo "   - 백엔드 API: $BACKEND_URL"
echo "   - 중지하려면 Ctrl+C 또는 ./stop.sh 실행"
echo ""
echo "🌐 브라우저에서 http://localhost:$PORT 를 열어보세요!"
echo ""

# 개발 서버 시작 (포그라운드에서 실행)
if [[ "$1" == "--background" ]] || [[ "$1" == "-b" ]]; then
    echo "🔄 백그라운드 모드로 실행 중..."
    nohup sh -c "PORT=$PORT npm run dev" > frontend.log 2>&1 &
    echo $! > frontend.pid
    echo "✅ 백그라운드에서 시작되었습니다."
    echo "   PID: $(cat frontend.pid)"
    echo "   로그: tail -f frontend.log"
    echo "   중지: ./stop.sh"
else
    PORT=$PORT npm run dev
fi