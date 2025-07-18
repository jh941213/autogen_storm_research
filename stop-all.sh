#!/bin/bash

# AutoGen DeepResearch 전체 시스템 중지 스크립트

echo "🛑 AutoGen DeepResearch 전체 시스템 중지 중..."
echo "================================================="

# run-all.sh에서 호출되었는지 확인
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    echo "   (run-all.sh에서 호출됨)"
fi

# 에러 상태 추적
exit_code=0

# 1. 프론트엔드 중지
echo "🔄 1단계: 프론트엔드 서버 중지 중..."
if [[ -f "frontend/stop.sh" ]]; then
    cd frontend
    ./stop.sh
    if [[ $? -ne 0 ]]; then
        echo "⚠️  프론트엔드 중지 중 일부 오류가 발생했습니다."
        exit_code=1
    fi
    cd ..
else
    echo "❌ 프론트엔드 중지 스크립트를 찾을 수 없습니다."
    exit_code=1
fi

echo ""

# 2. 백엔드 중지
echo "🔄 2단계: 백엔드 서버 중지 중..."
if [[ -f "stop.sh" ]]; then
    ./stop.sh
    if [[ $? -ne 0 ]]; then
        echo "⚠️  백엔드 중지 중 일부 오류가 발생했습니다."
        exit_code=1
    fi
else
    echo "❌ 백엔드 중지 스크립트를 찾을 수 없습니다."
    exit_code=1
fi

echo ""

# 3. 포트 확인 및 정리
echo "🔍 3단계: 포트 사용 상태 확인 중..."

# 포트 8002 (백엔드) 확인
if lsof -ti:8002 > /dev/null 2>&1; then
    echo "⚠️  포트 8002가 여전히 사용 중입니다."
    echo "   사용 중인 프로세스:"
    lsof -ti:8002 | xargs ps -p
    echo ""
    echo "❓ 포트 8002의 프로세스를 강제 종료하시겠습니까? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        lsof -ti:8002 | xargs kill -9
        echo "✅ 포트 8002 프로세스 강제 종료 완료"
    fi
else
    echo "✅ 포트 8002: 사용 중인 프로세스 없음"
fi

# 포트 3000 (프론트엔드) 확인
if lsof -ti:3000 > /dev/null 2>&1; then
    echo "⚠️  포트 3000이 여전히 사용 중입니다."
    echo "   사용 중인 프로세스:"
    lsof -ti:3000 | xargs ps -p
    echo ""
    echo "❓ 포트 3000의 프로세스를 강제 종료하시겠습니까? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        lsof -ti:3000 | xargs kill -9
        echo "✅ 포트 3000 프로세스 강제 종료 완료"
    fi
else
    echo "✅ 포트 3000: 사용 중인 프로세스 없음"
fi

echo ""

# 4. 임시 파일 정리
echo "🧹 4단계: 임시 파일 정리 중..."

# PID 파일 정리
if [[ -f "server.pid" ]]; then
    rm -f server.pid
    echo "✅ 백엔드 PID 파일 삭제"
fi

if [[ -f "frontend/frontend.pid" ]]; then
    rm -f frontend/frontend.pid
    echo "✅ 프론트엔드 PID 파일 삭제"
fi

# 로그 파일 정리 옵션
if [[ -f "server.log" ]] || [[ -f "frontend/frontend.log" ]]; then
    echo ""
    echo "📋 로그 파일이 발견되었습니다:"
    [[ -f "server.log" ]] && echo "   - server.log"
    [[ -f "frontend/frontend.log" ]] && echo "   - frontend/frontend.log"
    echo ""
    echo "❓ 로그 파일을 삭제하시겠습니까? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        [[ -f "server.log" ]] && rm -f server.log && echo "✅ 백엔드 로그 파일 삭제"
        [[ -f "frontend/frontend.log" ]] && rm -f frontend/frontend.log && echo "✅ 프론트엔드 로그 파일 삭제"
    else
        echo "💡 로그 파일 확인 명령어:"
        [[ -f "server.log" ]] && echo "   tail -f server.log"
        [[ -f "frontend/frontend.log" ]] && echo "   tail -f frontend/frontend.log"
    fi
fi

echo ""

# 5. 최종 상태 확인
echo "🔍 5단계: 최종 상태 확인 중..."

# 서버 상태 확인
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "⚠️  백엔드 서버가 여전히 응답합니다."
    exit_code=1
else
    echo "✅ 백엔드 서버: 정상 종료됨"
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "⚠️  프론트엔드 서버가 여전히 응답합니다."
    exit_code=1
else
    echo "✅ 프론트엔드 서버: 정상 종료됨"
fi

echo ""
echo "================================================="

if [[ $exit_code -eq 0 ]]; then
    echo "🎉 AutoGen DeepResearch 시스템이 성공적으로 종료되었습니다!"
    echo ""
    echo "💡 시스템 재시작 방법:"
    echo "   ./run-all.sh"
else
    echo "⚠️  시스템 종료 중 일부 오류가 발생했습니다."
    echo "   수동으로 프로세스를 확인하고 정리해주세요."
    echo ""
    echo "🔍 문제 해결 방법:"
    echo "   1. 실행 중인 프로세스 확인: ps aux | grep -E '(python|node|next)'"
    echo "   2. 포트 사용 상태 확인: lsof -i :8002 -i :3000"
    echo "   3. 수동 프로세스 종료: kill -9 <PID>"
fi

echo ""
echo "✅ 시스템 중지 완료"

exit $exit_code