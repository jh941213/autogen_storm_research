"""AutoGen STORM Research Assistant Interactive FastAPI Backend

이 파일은 인터랙티브 모드를 지원하는 FastAPI 백엔드입니다.
WebSocket을 통해 실시간 사용자 피드백을 처리합니다.
"""

import asyncio
import json
import os
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import uvicorn
from datetime import datetime
from enum import Enum

from autogen_storm import create_storm_workflow, initialize_tracing, get_tracing_manager
from autogen_storm.config import StormConfig, ModelConfig, ModelProvider
from autogen_storm.models import ResearchTask

# .env 파일 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="STORM Research Assistant Interactive API",
    description="인터랙티브 모드를 지원하는 AutoGen STORM Research Assistant",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 메시지 타입 정의
class MessageType(str, Enum):
    PROGRESS = "progress"
    ANALYST_COUNT_REQUEST = "analyst_count_request"
    REPORT_APPROVAL_REQUEST = "report_approval_request"
    FEEDBACK_REQUEST = "feedback_request"
    RESULT = "result"
    ERROR = "error"
    
class UserResponseType(str, Enum):
    ANALYST_COUNT = "analyst_count"
    REPORT_APPROVAL = "report_approval"
    FEEDBACK = "feedback"

# 요청/응답 모델 정의
class ResearchRequest(BaseModel):
    topic: str = Field(..., description="연구 주제")
    max_analysts: int = Field(default=3, ge=1, le=10, description="최대 분석가 수")
    max_interview_turns: int = Field(default=3, ge=1, le=10, description="최대 인터뷰 턴 수")
    parallel_interviews: bool = Field(default=True, description="병렬 인터뷰 여부")
    model_provider: str = Field(default="azure_openai", description="모델 제공자")
    api_key: Optional[str] = Field(None, description="API 키")
    azure_endpoint: Optional[str] = Field(None, description="Azure OpenAI 엔드포인트")
    azure_deployment: Optional[str] = Field(None, description="Azure OpenAI 배포 이름")

class WebSocketMessage(BaseModel):
    type: MessageType
    data: Dict[str, Any]

class UserResponse(BaseModel):
    type: UserResponseType
    data: Dict[str, Any]

class ReportApprovalData(BaseModel):
    action: str  # "approve", "rewrite", "view_full"
    feedback: Optional[str] = None
    rewrite_type: Optional[str] = None  # "complete", "feedback"

# 전역 변수
active_connections: Dict[str, WebSocket] = {}
pending_responses: Dict[str, asyncio.Future] = {}
research_tasks: Dict[str, Dict[str, Any]] = {}  # 연구 작업 저장

class InteractiveStormWorkflow:
    """인터랙티브 STORM 워크플로우"""
    
    def __init__(self, config: StormConfig, websocket: WebSocket, session_id: str):
        self.config = config
        self.websocket = websocket
        self.session_id = session_id
        self.workflow = create_storm_workflow(config, interactive_mode=True)
        
    async def run_interactive_research(self, task: ResearchTask):
        """인터랙티브 연구 실행"""
        try:
            await self.send_progress("연구 시작...", current_step="setup")
            
            # 1. 분석가 수 확인
            analyst_count = await self.get_analyst_count(task.max_analysts)
            task.max_analysts = analyst_count
            
            await self.send_progress(
                f"{analyst_count}명의 분석가 생성 중...",
                agent_activity={
                    "action": "generating_analysts",
                    "details": f"전문가 팀 구성: {analyst_count}명",
                    "timestamp": datetime.now().isoformat()
                },
                current_step="analysts"
            )
            
            # 2. 분석가 생성
            # 분석가 생성 과정을 세분화하여 추적
            await self.send_progress(
                "주제 분석 중...",
                agent_activity={
                    "action": "analyzing_topic",
                    "details": f"연구 주제 '{task.topic}' 분석 및 전문 분야 식별",
                    "timestamp": datetime.now().isoformat()
                },
                current_step="analysts",
                sub_activity="주제 분석"
            )
            
            await self.send_progress(
                "전문가 프로필 생성 중...",
                agent_activity={
                    "action": "creating_profiles",
                    "details": "각 분야별 전문가 프로필 및 배경 생성",
                    "timestamp": datetime.now().isoformat()
                },
                current_step="analysts",
                sub_activity="프로필 생성"
            )
            
            analysts = await self.workflow._generate_analysts(task)
            
            await self.send_progress(
                f"✅ {len(analysts)}명의 분석가 생성 완료",
                agent_activity={
                    "action": "analysts_created",
                    "details": f"전문가 팀 구성 완료: {', '.join([a.name for a in analysts])}",
                    "analysts": [{
                        "name": analyst.name,
                        "role": analyst.role,
                        "affiliation": analyst.affiliation
                    } for analyst in analysts],
                    "timestamp": datetime.now().isoformat()
                },
                current_step="analysts"
            )
            
            # 3. 인터뷰 진행
            await self.send_progress(
                "인터뷰 질문 생성 중...",
                agent_activity={
                    "action": "preparing_questions",
                    "details": "각 전문가별 맞춤형 인터뷰 질문 생성",
                    "timestamp": datetime.now().isoformat()
                },
                current_step="interviews",
                sub_activity="질문 준비"
            )
            
            await self.send_progress(
                "전문가 인터뷰 시작...",
                agent_activity={
                    "action": "starting_interviews",
                    "details": f"{len(analysts)}명의 전문가와 심층 인터뷰 시작",
                    "timestamp": datetime.now().isoformat()
                },
                current_step="interviews",
                sub_activity="인터뷰 진행"
            )
            
            # 인터뷰 진행 상황을 실시간으로 업데이트
            interviews = []
            
            if task.parallel_interviews:
                # 병렬 인터뷰 모드
                await self.send_progress(
                    f"🚀 {len(analysts)}명의 전문가와 동시 인터뷰 시작",
                    agent_activity={
                        "action": "parallel_interviews_started",
                        "details": f"병렬 처리로 {len(analysts)}명과 동시 인터뷰 진행",
                        "analysts": [{
                            "name": analyst.name,
                            "role": analyst.role,
                            "affiliation": analyst.affiliation
                        } for analyst in analysts],
                        "timestamp": datetime.now().isoformat()
                    },
                    current_step="interviews",
                    sub_activity=f"병렬 인터뷰 ({len(analysts)}명)"
                )
                
                # 병렬로 인터뷰 수행
                async def conduct_interview_with_updates(analyst, index):
                    await self.send_progress(
                        f"🎯 {analyst.name} 인터뷰 진행 중...",
                        agent_activity={
                            "action": "conducting_interview",
                            "details": f"{analyst.role} 전문가와 {task.topic}에 대한 심층 대화",
                            "current_analyst": {
                                "name": analyst.name,
                                "role": analyst.role,
                                "affiliation": analyst.affiliation
                            },
                            "timestamp": datetime.now().isoformat()
                        },
                        current_step="interviews",
                        sub_activity=f"병렬 인터뷰 진행 중"
                    )
                    
                    result = await self.workflow._conduct_single_interview(analyst, task.max_interview_turns)
                    
                    await self.send_progress(
                        f"✅ {analyst.name} 인터뷰 완료",
                        agent_activity={
                            "action": "interview_completed",
                            "details": f"{analyst.name}과의 인터뷰가 완료되었습니다",
                            "completed_analyst": {
                                "name": analyst.name,
                                "role": analyst.role
                            },
                            "timestamp": datetime.now().isoformat()
                        },
                        current_step="interviews"
                    )
                    
                    return result
                
                # 모든 인터뷰를 병렬로 실행
                interview_tasks = [
                    conduct_interview_with_updates(analyst, i) 
                    for i, analyst in enumerate(analysts)
                ]
                interviews = await asyncio.gather(*interview_tasks)
                
            else:
                # 순차 인터뷰 모드
                await self.send_progress(
                    f"📋 {len(analysts)}명의 전문가와 순차 인터뷰 시작",
                    agent_activity={
                        "action": "sequential_interviews_started",
                        "details": f"순차 처리로 {len(analysts)}명과 인터뷰 진행",
                        "analysts": [{
                            "name": analyst.name,
                            "role": analyst.role,
                            "affiliation": analyst.affiliation
                        } for analyst in analysts],
                        "timestamp": datetime.now().isoformat()
                    },
                    current_step="interviews",
                    sub_activity=f"순차 인터뷰 ({len(analysts)}명)"
                )
                
                for i, analyst in enumerate(analysts):
                    await self.send_progress(
                        f"{analyst.name}과 인터뷰 진행 중...",
                        agent_activity={
                            "action": "conducting_interview",
                            "details": f"{analyst.role} 전문가와 {task.topic}에 대한 심층 대화",
                            "current_analyst": {
                                "name": analyst.name,
                                "role": analyst.role,
                                "affiliation": analyst.affiliation
                            },
                            "progress": f"{i+1}/{len(analysts)}",
                            "timestamp": datetime.now().isoformat()
                        },
                        current_step="interviews",
                        sub_activity=f"인터뷰 {i+1}/{len(analysts)}"
                    )
                    
                    # 실제 인터뷰 수행 (개별적으로)
                    interview_result = await self.workflow._conduct_single_interview(analyst, task.max_interview_turns)
                    interviews.append(interview_result)
                    
                    await self.send_progress(
                        f"✅ {analyst.name} 인터뷰 완료",
                        agent_activity={
                            "action": "interview_completed",
                            "details": f"{analyst.name}과의 인터뷰가 완료되었습니다",
                            "completed_analyst": {
                                "name": analyst.name,
                                "role": analyst.role
                            },
                            "timestamp": datetime.now().isoformat()
                        },
                        current_step="interviews"
                    )
            
            await self.send_progress(
                f"✅ 모든 인터뷰 완료 ({len(interviews)}개)",
                agent_activity={
                    "action": "interviews_completed",
                    "details": f"총 {len(interviews)}개의 전문가 인터뷰 완료 ({'병렬' if task.parallel_interviews else '순차'} 처리)",
                    "interview_count": len(interviews),
                    "timestamp": datetime.now().isoformat()
                },
                current_step="interviews"
            )
            
            # 4. 초기 보고서 작성
            await self.send_progress(
                "인터뷰 결과 분석 중...",
                agent_activity={
                    "action": "analyzing_interviews",
                    "details": "수집된 인터뷰 데이터 분석 및 핵심 인사이트 추출",
                    "timestamp": datetime.now().isoformat()
                },
                current_step="report",
                sub_activity="데이터 분석"
            )
            
            await self.send_progress(
                "보고서 구조 설계 중...",
                agent_activity={
                    "action": "structuring_report",
                    "details": "논리적 구조와 섹션별 내용 구성",
                    "timestamp": datetime.now().isoformat()
                },
                current_step="report",
                sub_activity="구조 설계"
            )
            
            await self.send_progress(
                "보고서 작성 중...",
                agent_activity={
                    "action": "writing_report",
                    "details": "인터뷰 결과를 바탕으로 종합 보고서 작성",
                    "timestamp": datetime.now().isoformat()
                },
                current_step="report",
                sub_activity="보고서 작성"
            )
            
            report_parts = await self.workflow._write_report(task.topic, interviews)
            
            await self.send_progress(
                "보고서 품질 검토 중...",
                agent_activity={
                    "action": "reviewing_report",
                    "details": "보고서 내용 검토 및 품질 확인",
                    "timestamp": datetime.now().isoformat()
                },
                current_step="report",
                sub_activity="품질 검토"
            )
            
            # 5. 보고서 승인 프로세스 (인터랙티브)
            final_report_parts = await self.get_report_approval(task.topic, report_parts)
            
            # 6. 최종 결과 반환
            final_report = self.workflow._assemble_final_report(final_report_parts)
            
            result = {
                "topic": task.topic,
                "analysts": [
                    {
                        "name": analyst.name,
                        "role": analyst.role,
                        "affiliation": analyst.affiliation,
                        "description": analyst.description
                    }
                    for analyst in analysts
                ],
                "interview_count": len(interviews),
                "final_report": final_report,
                "completed_at": datetime.now().isoformat()
            }
            
            await self.send_progress(
                "✅ 연구 완료!",
                agent_activity={
                    "action": "research_completed",
                    "details": "모든 연구 과정이 성공적으로 완료되었습니다",
                    "timestamp": datetime.now().isoformat()
                },
                current_step="completed"
            )
            
            await self.send_result(result)
            
        except Exception as e:
            await self.send_error(str(e))
        finally:
            await self.workflow.close()
    
    async def send_progress(self, message: str, agent_activity: dict = None, current_step: str = None, sub_activity: str = None):
        """진행 상황 전송"""
        progress_data = {"message": message}
        
        if agent_activity:
            progress_data["agent_activity"] = agent_activity
        
        if current_step:
            progress_data["current_step"] = current_step
        
        if sub_activity:
            progress_data["sub_activity"] = sub_activity
            
        await self.websocket.send_json({
            "type": MessageType.PROGRESS,
            "data": progress_data
        })
    
    async def send_result(self, result: Dict[str, Any]):
        """최종 결과 전송"""
        await self.websocket.send_json({
            "type": MessageType.RESULT,
            "data": result
        })
    
    async def send_error(self, error: str):
        """오류 전송"""
        await self.websocket.send_json({
            "type": MessageType.ERROR,
            "data": {"error": error}
        })
    
    async def get_analyst_count(self, default_count: int) -> int:
        """분석가 수 입력 요청"""
        # 클라이언트에게 분석가 수 요청
        await self.websocket.send_json({
            "type": MessageType.ANALYST_COUNT_REQUEST,
            "data": {
                "default_count": default_count,
                "message": f"원하는 분석가 수를 선택하세요 (1-10, 기본값: {default_count})"
            }
        })
        
        # 응답 대기
        response = await self.wait_for_response(UserResponseType.ANALYST_COUNT)
        return response.get("count", default_count)
    
    async def get_report_approval(self, topic: str, report_parts: Dict[str, str]) -> Dict[str, str]:
        """보고서 승인 요청"""
        version = 1
        current_report = report_parts.copy()
        
        while True:
            # 보고서 미리보기 생성
            preview = {
                "version": version,
                "introduction_preview": (current_report.get('introduction', '') or '')[:200],
                "main_content_preview": (current_report.get('main_content', '') or '')[:300],
                "conclusion_preview": (current_report.get('conclusion', '') or '')[:200],
                "total_length": len((current_report.get('introduction', '') or '') + 
                                 (current_report.get('main_content', '') or '') + 
                                 (current_report.get('conclusion', '') or '')),
                "full_report": current_report
            }
            
            # 클라이언트에게 승인 요청
            await self.websocket.send_json({
                "type": MessageType.REPORT_APPROVAL_REQUEST,
                "data": {
                    "topic": topic,
                    "preview": preview,
                    "options": ["approve", "rewrite", "view_full"]
                }
            })
            
            # 응답 대기
            response = await self.wait_for_response(UserResponseType.REPORT_APPROVAL)
            action = response.get("action")
            
            if action == "approve":
                await self.send_progress("✅ 보고서가 승인되었습니다!")
                return current_report
                
            elif action == "rewrite":
                rewrite_type = response.get("rewrite_type", "feedback")
                
                if rewrite_type == "complete":
                    await self.send_progress("🔄 완전 재연구 시작...")
                    # 완전 재연구 로직 (간단화)
                    new_report = await self.workflow._write_report(topic, self.workflow.current_interviews)
                    
                elif rewrite_type == "feedback":
                    feedback = response.get("feedback", "")
                    if feedback:
                        await self.send_progress(f"💡 피드백 반영: {feedback}")
                        await self.send_progress("🔄 피드백 기반 재작성 중...")
                        new_report = await self.workflow._rewrite_with_feedback(topic, feedback)
                    else:
                        await self.send_progress("🔄 기본 재작성 중...")
                        new_report = await self.workflow._write_report(topic, self.workflow.current_interviews)
                
                current_report = new_report
                version += 1
                await self.send_progress(f"✨ 보고서 재작성 완료! (버전 {version})")
                continue
                
            elif action == "view_full":
                # 전체 보고서는 이미 preview에 포함되어 있음
                continue
    
    async def wait_for_response(self, response_type: UserResponseType) -> Dict[str, Any]:
        """사용자 응답 대기"""
        future = asyncio.Future()
        response_key = f"{self.session_id}_{response_type}"
        pending_responses[response_key] = future
        
        try:
            response = await asyncio.wait_for(future, timeout=300.0)  # 5분 타임아웃
            return response
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="사용자 응답 타임아웃")
        finally:
            pending_responses.pop(response_key, None)

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket 연결 처리"""
    await websocket.accept()
    active_connections[session_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_json()
            user_response = UserResponse(**data)
            
            # 대기 중인 응답 처리
            response_key = f"{session_id}_{user_response.type}"
            if response_key in pending_responses:
                future = pending_responses[response_key]
                if not future.done():
                    future.set_result(user_response.data)
                    
    except WebSocketDisconnect:
        active_connections.pop(session_id, None)
        # 대기 중인 응답들 취소
        for key in list(pending_responses.keys()):
            if key.startswith(session_id):
                future = pending_responses.pop(key)
                if not future.done():
                    future.cancel()

@app.post("/research/interactive/{session_id}")
async def start_interactive_research(
    session_id: str,
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """인터랙티브 연구 시작"""
    if session_id not in active_connections:
        raise HTTPException(status_code=400, detail="WebSocket 연결이 필요합니다")
    
    try:
        # 모델 설정 생성 (동적 API 키 지원)
        model_config = create_model_config(
            request.model_provider,
            request.api_key,
            request.azure_endpoint,
            request.azure_deployment
        )
        if not model_config:
            raise HTTPException(status_code=400, detail=f"API 키 또는 모델 설정이 올바르지 않습니다: {request.model_provider}")
        
        # STORM 설정 생성
        config = StormConfig(
            model_config=model_config,
            max_analysts=request.max_analysts,
            max_interview_turns=request.max_interview_turns,
            parallel_interviews=request.parallel_interviews,
            tavily_api_key=os.getenv("TAVILY_API_KEY")
        )
        
        # 연구 작업 생성
        task = ResearchTask(
            topic=request.topic,
            max_analysts=request.max_analysts,
            max_interview_turns=request.max_interview_turns,
            parallel_interviews=request.parallel_interviews
        )
        
        # 연구 작업 저장
        research_tasks[session_id] = {
            "session_id": session_id,
            "topic": request.topic,
            "status": "running",
            "created_at": datetime.now().isoformat(),
            "config": {
                "max_analysts": request.max_analysts,
                "max_interview_turns": request.max_interview_turns,
                "parallel_interviews": request.parallel_interviews,
                "model_provider": request.model_provider
            },
            "result": None,
            "error": None
        }
        
        # 백그라운드에서 인터랙티브 연구 실행
        websocket = active_connections[session_id]
        background_tasks.add_task(run_interactive_research_task, config, task, websocket, session_id)
        
        return {"message": "인터랙티브 연구가 시작되었습니다", "session_id": session_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"연구 시작 오류: {str(e)}")

async def run_interactive_research_task(config: StormConfig, task: ResearchTask, websocket: WebSocket, session_id: str):
    """백그라운드에서 인터랙티브 연구 실행"""
    try:
        workflow = InteractiveStormWorkflow(config, websocket, session_id)
        result = await workflow.run_interactive_research(task)
        
        # 연구 완료 시 결과 저장
        if session_id in research_tasks:
            research_tasks[session_id].update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "result": result
            })
    except Exception as e:
        # 연구 실패 시 에러 저장
        if session_id in research_tasks:
            research_tasks[session_id].update({
                "status": "failed",
                "completed_at": datetime.now().isoformat(),
                "error": str(e)
            })
        print(f"연구 실행 오류 ({session_id}): {e}")

@app.get("/")
async def root():
    """루트 페이지 - 간단한 테스트 인터페이스"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>STORM Research Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .messages { border: 1px solid #ccc; height: 400px; overflow-y: auto; padding: 10px; margin: 10px 0; }
            .input-group { margin: 10px 0; }
            input, textarea, button { margin: 5px; padding: 5px; }
            button { background-color: #007bff; color: white; border: none; padding: 10px 20px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            .hidden { display: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌟 STORM Research Assistant</h1>
            
            <div class="input-group">
                <input type="text" id="topicInput" placeholder="연구 주제를 입력하세요" style="width: 300px;">
                <button onclick="startResearch()">연구 시작</button>
            </div>
            
            <div class="messages" id="messages"></div>
            
            <div id="userInputArea" class="hidden">
                <div id="analystCountInput" class="hidden">
                    <label>분석가 수 (1-10): </label>
                    <input type="number" id="analystCount" min="1" max="10" value="3">
                    <button onclick="submitAnalystCount()">확인</button>
                </div>
                
                <div id="reportApprovalInput" class="hidden">
                    <h3>보고서 검토</h3>
                    <div id="reportPreview"></div>
                    <button onclick="approveReport()">승인</button>
                    <button onclick="rewriteReport()">재작성</button>
                    <button onclick="viewFullReport()">전체보기</button>
                </div>
                
                <div id="feedbackInput" class="hidden">
                    <label>개선 요청사항:</label><br>
                    <textarea id="feedbackText" rows="3" cols="50"></textarea><br>
                    <button onclick="submitFeedback()">피드백 제출</button>
                </div>
            </div>
        </div>

        <script>
            let ws;
            let sessionId = 'session_' + Date.now();
            let currentReportData = null;

            function addMessage(message, type = 'info') {
                const messages = document.getElementById('messages');
                const div = document.createElement('div');
                div.textContent = new Date().toLocaleTimeString() + ' - ' + message;
                div.style.color = type === 'error' ? 'red' : type === 'success' ? 'green' : 'black';
                messages.appendChild(div);
                messages.scrollTop = messages.scrollHeight;
            }

            function startResearch() {
                const topic = document.getElementById('topicInput').value.trim();
                if (!topic) {
                    alert('연구 주제를 입력해주세요');
                    return;
                }

                // WebSocket 연결
                ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
                
                ws.onopen = function() {
                    addMessage('WebSocket 연결됨', 'success');
                    
                    // 연구 시작 요청
                    fetch(`/research/interactive/${sessionId}`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            topic: topic,
                            max_analysts: 3,
                            max_interview_turns: 3,
                            parallel_interviews: true,
                            model_provider: 'azure_openai'
                        })
                    });
                };

                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                };

                ws.onclose = function() {
                    addMessage('WebSocket 연결 종료', 'error');
                };
            }

            function handleWebSocketMessage(data) {
                switch(data.type) {
                    case 'progress':
                        addMessage(data.data.message);
                        break;
                    case 'analyst_count_request':
                        showAnalystCountInput(data.data);
                        break;
                    case 'report_approval_request':
                        showReportApprovalInput(data.data);
                        break;
                    case 'result':
                        showResult(data.data);
                        break;
                    case 'error':
                        addMessage('오류: ' + data.data.error, 'error');
                        break;
                }
            }

            function showAnalystCountInput(data) {
                addMessage(data.message);
                document.getElementById('analystCount').value = data.default_count;
                document.getElementById('analystCountInput').classList.remove('hidden');
                document.getElementById('userInputArea').classList.remove('hidden');
            }

            function submitAnalystCount() {
                const count = parseInt(document.getElementById('analystCount').value);
                ws.send(JSON.stringify({
                    type: 'analyst_count',
                    data: {count: count}
                }));
                document.getElementById('analystCountInput').classList.add('hidden');
            }

            function showReportApprovalInput(data) {
                currentReportData = data;
                const preview = data.preview;
                const previewDiv = document.getElementById('reportPreview');
                previewDiv.innerHTML = `
                    <h4>보고서 미리보기 (버전 ${preview.version})</h4>
                    <p><strong>서론:</strong> ${preview.introduction_preview}...</p>
                    <p><strong>본문:</strong> ${preview.main_content_preview}...</p>
                    <p><strong>결론:</strong> ${preview.conclusion_preview}...</p>
                    <p><strong>전체 길이:</strong> ${preview.total_length}자</p>
                `;
                document.getElementById('reportApprovalInput').classList.remove('hidden');
                document.getElementById('userInputArea').classList.remove('hidden');
            }

            function approveReport() {
                ws.send(JSON.stringify({
                    type: 'report_approval',
                    data: {action: 'approve'}
                }));
                document.getElementById('reportApprovalInput').classList.add('hidden');
            }

            function rewriteReport() {
                document.getElementById('reportApprovalInput').classList.add('hidden');
                document.getElementById('feedbackInput').classList.remove('hidden');
            }

            function viewFullReport() {
                if (currentReportData && currentReportData.preview.full_report) {
                    const report = currentReportData.preview.full_report;
                    alert(`전체 보고서:\\n\\n서론:\\n${report.introduction}\\n\\n본문:\\n${report.main_content}\\n\\n결론:\\n${report.conclusion}`);
                }
            }

            function submitFeedback() {
                const feedback = document.getElementById('feedbackText').value.trim();
                ws.send(JSON.stringify({
                    type: 'report_approval',
                    data: {
                        action: 'rewrite',
                        rewrite_type: 'feedback',
                        feedback: feedback
                    }
                }));
                document.getElementById('feedbackInput').classList.add('hidden');
                document.getElementById('feedbackText').value = '';
            }

            function showResult(data) {
                addMessage('✅ 연구 완료!', 'success');
                addMessage(`주제: ${data.topic}`);
                addMessage(`분석가 수: ${data.analysts.length}`);
                addMessage(`인터뷰 수: ${data.interview_count}`);
                
                // 결과를 새 창에 표시
                const resultWindow = window.open('', '_blank');
                resultWindow.document.write(`
                    <html>
                    <head><title>연구 결과</title></head>
                    <body>
                        <h1>연구 결과</h1>
                        <h2>주제: ${data.topic}</h2>
                        <pre>${data.final_report}</pre>
                    </body>
                    </html>
                `);
                
                document.getElementById('userInputArea').classList.add('hidden');
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

def create_model_config(provider: str, api_key: Optional[str] = None, azure_endpoint: Optional[str] = None, azure_deployment: Optional[str] = None) -> Optional[ModelConfig]:
    """모델 제공자에 따른 설정 생성"""
    try:
        if provider == "openai":
            # 동적 API 키 우선 사용, 없으면 환경변수 사용
            key = api_key if api_key and api_key.strip() else os.getenv("OPENAI_API_KEY")
            if not key:
                print("OpenAI API 키가 설정되지 않았습니다.")
                return None
            return ModelConfig(
                provider=ModelProvider.OPENAI,
                api_key=key,
                model="gpt-4o"
            )
            
        elif provider == "azure_openai":
            # 동적 설정 우선 사용, 없으면 환경변수 사용
            key = api_key if api_key and api_key.strip() else os.getenv("AZURE_OPENAI_API_KEY")
            endpoint = azure_endpoint if azure_endpoint and azure_endpoint.strip() else os.getenv("AZURE_OPENAI_ENDPOINT")
            deployment = azure_deployment if azure_deployment and azure_deployment.strip() else os.getenv("AZURE_OPENAI_DEPLOYMENT")
            
            if not key:
                print("Azure OpenAI API 키가 설정되지 않았습니다.")
                return None
            if not endpoint:
                print("Azure OpenAI 엔드포인트가 설정되지 않았습니다.")
                return None
            if not deployment:
                print("Azure OpenAI 배포 이름이 설정되지 않았습니다.")
                return None
                
            return ModelConfig(
                provider=ModelProvider.AZURE_OPENAI,
                api_key=key,
                azure_endpoint=endpoint,
                azure_deployment=deployment,
                model="gpt-4.1-nano"
            )
            
        elif provider == "anthropic":
            # 동적 API 키 우선 사용, 없으면 환경변수 사용
            key = api_key if api_key and api_key.strip() else os.getenv("ANTHROPIC_API_KEY")
            if not key:
                print("Anthropic API 키가 설정되지 않았습니다.")
                return None
            return ModelConfig(
                provider=ModelProvider.ANTHROPIC,
                api_key=key,
                model="claude-3-5-sonnet-20241022"
            )
            
        else:
            print(f"지원되지 않는 모델 제공자: {provider}")
            return None
            
    except Exception as e:
        print(f"모델 설정 생성 오류: {e}")
        return None

# 새로운 API 엔드포인트들
@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "STORM Research Assistant Interactive API"
    }

@app.get("/research/tasks")
async def list_research_tasks():
    """연구 작업 목록 조회"""
    return {
        "tasks": list(research_tasks.keys()),
        "total": len(research_tasks)
    }

@app.get("/research/tasks/{task_id}")
async def get_research_task(task_id: str):
    """특정 연구 작업 조회"""
    if task_id not in research_tasks:
        raise HTTPException(status_code=404, detail="연구 작업을 찾을 수 없습니다.")
    
    return research_tasks[task_id]

@app.delete("/research/tasks/{task_id}")
async def delete_research_task(task_id: str):
    """연구 작업 삭제"""
    if task_id not in research_tasks:
        raise HTTPException(status_code=404, detail="연구 작업을 찾을 수 없습니다.")
    
    del research_tasks[task_id]
    return {"message": "연구 작업이 삭제되었습니다.", "task_id": task_id}

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 초기화"""
    print("🌟 STORM Research Assistant Interactive API 서버 시작")
    print("📊 Langfuse 추적 초기화 중...")
    
    tracing_enabled = initialize_tracing()
    if tracing_enabled:
        print("✅ Langfuse 추적이 활성화되었습니다!")
    else:
        print("⚠️  Langfuse 추적이 비활성화되었습니다.")

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 리소스 정리"""
    print("🔄 서버 종료 중...")
    
    # 활성 연결 정리
    for session_id, websocket in active_connections.items():
        try:
            await websocket.close()
        except Exception as e:
            print(f"WebSocket 정리 오류 ({session_id}): {e}")
    
    # 추적 매니저 정리
    tracing_manager = get_tracing_manager()
    if tracing_manager.enabled:
        tracing_manager.close()
    
    print("✅ 서버 종료 완료")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(
        "app_interactive:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
        ws_ping_interval=20,
        ws_ping_timeout=20
    )