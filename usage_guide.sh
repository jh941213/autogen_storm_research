#!/bin/bash

echo "🌩️ STORM 연구 시스템 - 최적 사용법 가이드"
echo "==============================================="

echo ""
echo "📋 1단계: 환경 설정 확인"
echo "  python setup_check.py"
echo ""

echo "🚀 2단계: 실행 방법들"
echo ""
echo "✨ 기본 실행 (대화형 모드):"
echo "  python storm_research.py"
echo ""

echo "⚡ 간단 실행:"
echo "  python simple_run.py \"주제명\""
echo "  예시: python simple_run.py \"인공지능의 의료 분야 활용\""
echo ""

echo "🤖 자동 실행 (사용자 개입 없음):"
echo "  python simple_run.py \"주제명\" --auto"
echo "  예시: python simple_run.py \"블록체인 기술\" --auto"
echo ""

echo "📊 배치 실행 (여러 주제 한번에):"
echo "  python batch_run.py"
echo ""

echo "💡 권장 사용법:"
echo "────────────────"
echo "1. 처음 사용: python setup_check.py로 환경 확인"
echo "2. 단일 주제: python simple_run.py \"주제\" --auto"
echo "3. 여러 주제: python batch_run.py"
echo "4. 품질 중시: python storm_research.py (human-in-the-loop)"
echo ""

echo "⚙️ 성능 최적화 팁:"
echo "──────────────────"
echo "• CPU 코어가 많으면 max_workers 늘리기 (2-8 권장)"
echo "• 메모리가 적으면 max_workers 줄이기"
echo "• Tavily API 키 설정으로 검색 품질 향상"
echo "• Rich 라이브러리 설치로 UI 개선"
echo ""

echo "🔧 문제 해결:"
echo "─────────────"
echo "• API 오류: .env 파일의 키 확인"
echo "• 메모리 부족: max_workers=2로 설정"
echo "• 느린 속도: --auto 모드 사용"
echo "• 품질 개선: human-in-the-loop 모드 사용"
