# AutoGen DeepResearch

AI 전문가들이 협력하여 어떤 주제든 깊이 있게 연구하는 차세대 연구 플랫폼

## 🌟 주요 기능

- **지능형 분석**: AI 전문가들이 다각도로 주제를 분석
- **협업 연구**: 여러 분석가가 협력하여 깊이 있는 인사이트 제공
- **대화형 인터뷰**: 실시간 질의응답으로 정확한 정보 수집
- **인터랙티브 피드백**: 보고서 검토 및 피드백 반영
- **실시간 WebSocket**: 연구 진행 상황을 실시간으로 확인
- **세련된 UI**: 빅테크 스타일의 모던한 사용자 인터페이스

## 🏗️ 시스템 구성

### 백엔드 (FastAPI)
- **포트**: 8002
- **기술**: Python, FastAPI, WebSocket
- **AI 모델**: Azure OpenAI, OpenAI, Anthropic 지원
- **실시간 통신**: WebSocket 기반 양방향 통신

### 프론트엔드 (Next.js)
- **포트**: 3001
- **기술**: Next.js 15, TypeScript, Tailwind CSS
- **UI 라이브러리**: shadcn/ui
- **상태 관리**: Zustand
- **실시간 통신**: WebSocket 클라이언트

## 🚀 빠른 시작

### 1. 전체 시스템 실행
```bash
./run-all.sh
```

### 2. 개별 서버 실행
```bash
# 백엔드만 실행
./start.sh

# 프론트엔드만 실행 (새 터미널에서)
cd frontend && ./start.sh
```

### 3. 시스템 중지
```bash
# 전체 시스템 중지
./stop-all.sh

# 또는 run-all.sh 실행 중 Ctrl+C
```

## 🌐 접속 URL

- **메인 애플리케이션**: http://localhost:3001
- **백엔드 API**: http://localhost:8002
- **API 문서**: http://localhost:8002/docs

## 📋 사용 방법

1. **연구 주제 입력**
   - 메인 페이지에서 연구하고 싶은 주제 입력
   - 분석가 수, 인터뷰 라운드 등 설정 조정

2. **연구 진행**
   - 실시간으로 연구 진행 상황 확인
   - 분석가 수 선택 (인터랙티브)
   - 전문가 팀 구성 및 인터뷰 진행

3. **보고서 검토**
   - 작성된 보고서 미리보기
   - 승인 또는 피드백 제공
   - 피드백 반영 시 자동 재작성

4. **최종 결과**
   - 완성된 연구 보고서 확인
   - 다운로드 및 공유 가능

## 🔧 환경 설정

### 백엔드 환경 변수 (.env)
```bash
# Azure OpenAI 설정
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT=your_deployment
AZURE_OPENAI_API_KEY=your_api_key

# OpenAI 설정 (선택사항)
OPENAI_API_KEY=your_openai_key

# Anthropic 설정 (선택사항)
ANTHROPIC_API_KEY=your_anthropic_key

# Tavily Search API
TAVILY_API_KEY=your_tavily_key

# Langfuse 추적 (선택사항)
LANGFUSE_SECRET_KEY=your_langfuse_secret
LANGFUSE_PUBLIC_KEY=your_langfuse_public
LANGFUSE_HOST=your_langfuse_host
```

### 프론트엔드 환경 변수 (.env.local)
```bash
# 백엔드 API URL
NEXT_PUBLIC_API_URL=http://localhost:8002

# 앱 정보
NEXT_PUBLIC_APP_NAME=AutoGen DeepResearch
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## 🛠️ 개발 도구

### 스크립트 목록
- `run-all.sh`: 전체 시스템 실행
- `stop-all.sh`: 전체 시스템 중지
- `start.sh`: 백엔드 서버 시작
- `stop.sh`: 백엔드 서버 중지
- `frontend/start.sh`: 프론트엔드 서버 시작
- `frontend/stop.sh`: 프론트엔드 서버 중지
- `test_interactive_client.py`: 인터랙티브 기능 테스트

### 로그 확인
```bash
# 백엔드 로그
tail -f server.log

# 프론트엔드 로그
tail -f frontend/frontend.log

# 실시간 로그 (둘 다)
tail -f server.log frontend/frontend.log
```

## 🔍 문제 해결

### 포트 충돌
```bash
# 사용 중인 포트 확인
lsof -i :8002 -i :3001

# 프로세스 종료
kill -9 <PID>
```

### 서버 상태 확인
```bash
# 백엔드 상태
curl http://localhost:8002/health

# 프론트엔드 상태
curl http://localhost:3001
```

### 환경 변수 확인
```bash
# 백엔드 환경 변수
python -c "import os; print([k for k in os.environ.keys() if 'AZURE' in k or 'OPENAI' in k])"

# 프론트엔드 환경 변수
cd frontend && npm run env
```

## 📚 기술 스택

### 백엔드
- **Python 3.9+**
- **FastAPI**: 고성능 웹 프레임워크
- **WebSocket**: 실시간 통신
- **AutoGen**: 멀티 에이전트 프레임워크
- **Azure OpenAI**: AI 모델 서비스
- **Langfuse**: AI 추적 및 모니터링

### 프론트엔드
- **Next.js 15**: React 기반 풀스택 프레임워크
- **TypeScript**: 타입 안전성
- **Tailwind CSS**: 유틸리티 퍼스트 CSS
- **shadcn/ui**: 모던 UI 컴포넌트
- **Zustand**: 상태 관리
- **React Hook Form**: 폼 관리

## 🎯 프로젝트 구조

```
storm-research/
├── 백엔드 (FastAPI)
│   ├── app_interactive.py          # 인터랙티브 서버
│   ├── app.py                      # 기본 API 서버
│   ├── autogen_storm/              # STORM 연구 모듈
│   │   ├── workflow.py             # 워크플로우 로직
│   │   ├── agents.py               # AI 에이전트 정의
│   │   ├── models.py               # 데이터 모델
│   │   └── config.py               # 설정 관리
│   ├── start.sh                    # 백엔드 시작
│   └── stop.sh                     # 백엔드 중지
├── 프론트엔드 (Next.js)
│   ├── src/
│   │   ├── app/                    # 페이지 컴포넌트
│   │   ├── components/             # UI 컴포넌트
│   │   ├── lib/                    # 유틸리티
│   │   ├── store/                  # 상태 관리
│   │   └── types/                  # 타입 정의
│   ├── start.sh                    # 프론트엔드 시작
│   └── stop.sh                     # 프론트엔드 중지
├── run-all.sh                      # 전체 시스템 시작
└── stop-all.sh                     # 전체 시스템 중지
```

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

버그 리포트, 기능 요청, 풀 리퀘스트는 언제든 환영합니다!

---

**AutoGen DeepResearch** - AI 전문가들이 협력하는 차세대 연구 플랫폼 🚀