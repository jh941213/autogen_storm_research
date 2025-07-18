#!/bin/bash

# AutoGen DeepResearch 전체 시스템 실행 스크립트

echo "🌟 AutoGen DeepResearch 전체 시스템 시작 중..."
echo "================================================="

# 함수 정의
cleanup() {
    echo ""
    echo "🛑 시스템 종료 중..."
    
    # stop-all.sh 스크립트 호출
    ./stop-all.sh
    
    exit 0
}

# Ctrl+C 시그널 핸들러
trap cleanup SIGINT SIGTERM

# 현재 디렉토리 확인
if [[ ! -f "start.sh" ]] || [[ ! -f "stop.sh" ]]; then
    echo "❌ 백엔드 스크립트를 찾을 수 없습니다. storm-research 폴더에서 실행해주세요."
    exit 1
fi

if [[ ! -f "frontend/start.sh" ]] || [[ ! -f "frontend/stop.sh" ]]; then
    echo "❌ 프론트엔드 스크립트를 찾을 수 없습니다. frontend 폴더를 확인해주세요."
    exit 1
fi

echo "📋 시스템 구성:"
echo "   - 백엔드: FastAPI 인터랙티브 서버 (포트 8002)"
echo "   - 프론트엔드: Next.js 개발 서버 (포트 3001)"
echo "   - WebSocket: 실시간 통신 지원"
echo ""

# 환경 변수 확인
echo "🔧 환경 변수 확인 중..."
if [[ -f ".env" ]]; then
    echo "✅ 백엔드 .env 파일을 찾았습니다."
else
    echo "⚠️  백엔드 .env 파일이 없습니다."
    echo "   필요한 환경 변수를 설정해주세요."
fi

if [[ -f "frontend/.env.local" ]]; then
    echo "✅ 프론트엔드 .env.local 파일을 찾았습니다."
else
    echo "⚠️  프론트엔드 .env.local 파일이 없습니다."
fi

echo ""

# 1. 백엔드 서버 시작
echo "🚀 1단계: 백엔드 서버 시작 중..."
./start.sh
if [[ $? -ne 0 ]]; then
    echo "❌ 백엔드 서버 시작에 실패했습니다."
    exit 1
fi

# 백엔드 서버 시작 대기
echo "⏳ 백엔드 서버 시작 대기 중..."
for i in {1..30}; do
    if curl -s http://localhost:8002/health > /dev/null 2>&1; then
        echo "✅ 백엔드 서버가 시작되었습니다 (http://localhost:8002)"
        break
    fi
    if [[ $i -eq 30 ]]; then
        echo "❌ 백엔드 서버 시작 타임아웃"
        exit 1
    fi
    sleep 1
    echo -n "."
done

echo ""

# 2. 프론트엔드 서버 시작
echo "🚀 2단계: 프론트엔드 서버 시작 중..."
cd frontend
PORT=3001 ./start.sh --background
if [[ $? -ne 0 ]]; then
    echo "❌ 프론트엔드 서버 시작에 실패했습니다."
    cd ..
    exit 1
fi
cd ..

# 프론트엔드 서버 시작 대기
echo "⏳ 프론트엔드 서버 시작 대기 중..."
for i in {1..30}; do
    if curl -s http://localhost:3001 > /dev/null 2>&1; then
        echo "✅ 프론트엔드 서버가 시작되었습니다 (http://localhost:3001)"
        break
    fi
    if [[ $i -eq 30 ]]; then
        echo "❌ 프론트엔드 서버 시작 타임아웃"
        exit 1
    fi
    sleep 1
    echo -n "."
done

echo ""
echo "🎉 AutoGen DeepResearch 시스템이 성공적으로 시작되었습니다!"
echo "================================================="
echo ""
echo "🌐 접속 URL:"
echo "   - 메인 애플리케이션: http://localhost:3001"
echo "   - 백엔드 API: http://localhost:8002"
echo "   - API 문서: http://localhost:8002/docs"
echo ""
echo "📊 시스템 상태:"
echo "   - 백엔드: 실행 중 (PID: $(cat server.pid 2>/dev/null || echo 'N/A'))"
echo "   - 프론트엔드: 실행 중 (PID: $(cat frontend/frontend.pid 2>/dev/null || echo 'N/A'))"
echo ""
echo "🔄 관리 명령어:"
echo "   - 전체 중지: ./stop-all.sh"
echo "   - 백엔드만 중지: ./stop.sh"
echo "   - 프론트엔드만 중지: cd frontend && ./stop.sh"
echo "   - 로그 확인: tail -f server.log frontend/frontend.log"
echo ""
echo "💡 사용 방법:"
echo "   1. 브라우저에서 http://localhost:3001 접속"
echo "   2. 연구 주제 입력 후 '연구 시작하기' 클릭"
echo "   3. 실시간으로 연구 진행 상황 확인"
echo "   4. 인터랙티브 피드백 제공"
echo "   5. 최종 연구 결과 확인"
echo ""
echo "중지하려면 Ctrl+C를 누르거나 ./stop-all.sh를 실행하세요."
echo ""

# 무한 대기 (사용자가 Ctrl+C로 종료할 때까지)
while true; do
    sleep 1
done