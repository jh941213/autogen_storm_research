#!/bin/bash

# STORM Research Assistant 인터랙티브 서버 중지 스크립트

echo "🛑 STORM Research Assistant 서버 중지 중..."

# PID 파일 확인
if [ ! -f server.pid ]; then
    echo "❌ server.pid 파일이 없습니다."
    echo "   서버가 실행되고 있지 않거나 ./start.sh로 시작되지 않았습니다."
    
    # 프로세스 이름으로 찾아서 종료 시도
    echo "🔍 Python 프로세스 중 app_interactive.py 찾는 중..."
    PIDS=$(ps aux | grep "app_interactive.py" | grep -v grep | awk '{print $2}')
    
    if [ -n "$PIDS" ]; then
        echo "📋 발견된 프로세스들:"
        ps aux | grep "app_interactive.py" | grep -v grep
        echo ""
        echo "❓ 이 프로세스들을 종료하시겠습니까? (y/N)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo $PIDS | xargs kill -TERM
            echo "✅ 프로세스 종료 완료"
        else
            echo "❌ 취소됨"
        fi
    else
        echo "❌ 실행 중인 app_interactive.py 프로세스를 찾을 수 없습니다."
    fi
    
    exit 1
fi

# PID 읽기
PID=$(cat server.pid)
echo "📋 서버 PID: $PID"

# 프로세스 존재 확인
if ! kill -0 $PID 2>/dev/null; then
    echo "❌ PID $PID 프로세스가 존재하지 않습니다."
    rm -f server.pid
    exit 1
fi

# 프로세스 정보 표시
echo "📋 종료할 프로세스:"
ps -p $PID -o pid,ppid,cmd

# 서버 종료
echo "🔄 서버 종료 중..."
kill -TERM $PID

# 종료 확인 (최대 10초 대기)
echo "⏳ 서버 종료 대기 중..."
for i in {1..10}; do
    if ! kill -0 $PID 2>/dev/null; then
        echo "✅ 서버가 정상적으로 종료되었습니다."
        rm -f server.pid
        exit 0
    fi
    sleep 1
    echo -n "."
done

echo ""
echo "⚠️  서버가 정상적으로 종료되지 않았습니다. 강제 종료합니다."
kill -KILL $PID

# 재확인
if ! kill -0 $PID 2>/dev/null; then
    echo "✅ 서버가 강제 종료되었습니다."
    rm -f server.pid
else
    echo "❌ 서버 종료 실패"
    exit 1
fi

echo "🧹 로그 파일 정리 중..."
if [ -f "server.log" ]; then
    echo "   server.log 파일이 남아있습니다. 로그를 확인하려면:"
    echo "   tail -n 20 server.log"
fi

echo "✅ 종료 완료"