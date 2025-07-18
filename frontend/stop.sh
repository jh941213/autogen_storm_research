#!/bin/bash

# AutoGen DeepResearch 프론트엔드 중지 스크립트

echo "🛑 AutoGen DeepResearch 프론트엔드 중지 중..."

# PID 파일 확인
if [[ -f "frontend.pid" ]]; then
    PID=$(cat frontend.pid)
    echo "📋 프론트엔드 PID: $PID"
    
    # 프로세스 존재 확인
    if kill -0 $PID 2>/dev/null; then
        echo "📋 종료할 프로세스:"
        ps -p $PID -o pid,ppid,cmd
        
        # 프로세스 종료
        echo "🔄 프론트엔드 종료 중..."
        kill -TERM $PID
        
        # 종료 확인 (최대 10초 대기)
        echo "⏳ 프론트엔드 종료 대기 중..."
        for i in {1..10}; do
            if ! kill -0 $PID 2>/dev/null; then
                echo "✅ 프론트엔드가 정상적으로 종료되었습니다."
                rm -f frontend.pid
                break
            fi
            sleep 1
            echo -n "."
        done
        
        # 여전히 실행 중이면 강제 종료
        if kill -0 $PID 2>/dev/null; then
            echo ""
            echo "⚠️  프론트엔드가 정상적으로 종료되지 않았습니다. 강제 종료합니다."
            kill -KILL $PID
            if ! kill -0 $PID 2>/dev/null; then
                echo "✅ 프론트엔드가 강제 종료되었습니다."
                rm -f frontend.pid
            else
                echo "❌ 프론트엔드 종료 실패"
                exit 1
            fi
        fi
    else
        echo "❌ PID $PID 프로세스가 존재하지 않습니다."
        rm -f frontend.pid
    fi
else
    echo "❌ frontend.pid 파일이 없습니다."
    echo "   프론트엔드가 백그라운드에서 실행되고 있지 않거나 ./start.sh -b로 시작되지 않았습니다."
    
    # 프로세스 이름으로 찾아서 종료 시도
    echo "🔍 Next.js 개발 서버 프로세스 찾는 중..."
    PIDS=$(ps aux | grep "next.*dev" | grep -v grep | awk '{print $2}')
    
    if [[ -n "$PIDS" ]]; then
        echo "📋 발견된 Next.js 프로세스들:"
        ps aux | grep "next.*dev" | grep -v grep
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
        echo "❌ 실행 중인 Next.js 개발 서버를 찾을 수 없습니다."
        
        # 포트 3001에서 실행 중인 프로세스 확인
        echo "🔍 포트 3001에서 실행 중인 프로세스 확인 중..."
        if lsof -ti:3001 > /dev/null 2>&1; then
            echo "📋 포트 3001 사용 중인 프로세스:"
            lsof -ti:3001 | xargs ps -p
            echo ""
            echo "❓ 포트 3001의 프로세스를 종료하시겠습니까? (y/N)"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                lsof -ti:3001 | xargs kill -TERM
                echo "✅ 포트 3001 프로세스 종료 완료"
            else
                echo "❌ 취소됨"
            fi
        else
            echo "❌ 포트 3001에서 실행 중인 프로세스가 없습니다."
        fi
    fi
fi

# 로그 파일 정리
if [[ -f "frontend.log" ]]; then
    echo "🧹 로그 파일 정리 중..."
    echo "   frontend.log 파일이 남아있습니다. 로그를 확인하려면:"
    echo "   tail -n 20 frontend.log"
    echo ""
    echo "❓ 로그 파일을 삭제하시겠습니까? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        rm -f frontend.log
        echo "✅ 로그 파일 삭제 완료"
    fi
fi

echo "✅ 프론트엔드 종료 완료"