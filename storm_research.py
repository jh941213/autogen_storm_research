
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
from datetime import datetime

# AutoGen imports
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination, HandoffTermination
from autogen_agentchat.base import TaskResult
from autogen_agentchat.base import Handoff
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

# 외부 도구들
from tavily import TavilyClient
from duckduckgo_search import DDGS

# 시각화 도구 (Rich 라이브러리)
try:
    from rich.console import Console
    from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Rich 라이브러리가 설치되지 않았습니다. 설치하려면: pip install rich")

# 환경 설정
load_dotenv()

# Rich 콘솔 설정
if RICH_AVAILABLE:
    console = Console()
    
    # Rich 핸들러로 로깅 설정 (WARNING 레벨 이상만 표시)
    logging.basicConfig(
        level=logging.WARNING,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)]
    )
    
    # 특정 라이브러리 로그 레벨 조정
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("autogen").setLevel(logging.WARNING)
    logging.getLogger("azure").setLevel(logging.WARNING)
    
else:
    logging.basicConfig(level=logging.WARNING)
    
logger = logging.getLogger(__name__)

# 데이터 모델들
class Subsection(BaseModel):
    subsection_title: str = Field(..., title="서브섹션 제목")
    description: str = Field(..., title="서브섹션 내용")

class Section(BaseModel):
    section_title: str = Field(..., title="섹션 제목")
    description: str = Field(..., title="섹션 내용")
    subsections: Optional[List[Subsection]] = Field(default=None, title="서브섹션들")

class Outline(BaseModel):
    page_title: str = Field(..., title="위키페이지 제목")
    sections: List[Section] = Field(default_factory=list, title="섹션들")

class Editor(BaseModel):
    affiliation: str = Field(..., title="소속")
    name: str = Field(..., title="이름")
    role: str = Field(..., title="역할")
    description: str = Field(..., title="설명")

class SearchResult(BaseModel):
    content: str
    url: str
    title: str = ""

@dataclass
class StormResearchState:
    """STORM 연구 상태를 추적하는 클래스"""
    topic: str
    outline: Optional[Outline] = None
    editors: List[Editor] = None
    interview_results: Dict[str, List[str]] = None
    references: Dict[str, str] = None
    sections: Dict[str, str] = None
    final_article: str = ""

class ParallelStormResearchSystem:
    """AutoGen 기반 병렬 STORM 연구 시스템"""
    
    def __init__(self, max_workers: int = 4):
        
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.max_workers = max_workers
        
        # Azure OpenAI 설정 확인
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        azure_model = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")
        
        if not azure_api_key or not azure_endpoint:
            raise ValueError(
                "Azure OpenAI 설정이 필요합니다. .env 파일에 다음을 설정하세요:\n"
                "AZURE_OPENAI_API_KEY=your_api_key\n"
                "AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/"
            )
        
        # OpenAI 클라이언트 설정
        self.model_client = AzureOpenAIChatCompletionClient(
            model=azure_model,
            api_key=azure_api_key,
            azure_endpoint=azure_endpoint,
            api_version=azure_api_version
        )
        
        self.long_context_model = AzureOpenAIChatCompletionClient(
            model=azure_model,
            api_key=azure_api_key,
            azure_endpoint=azure_endpoint,
            api_version=azure_api_version
        )
        
        # 검색 엔진 설정
        if self.tavily_api_key:
            self.search_engine = TavilyClient(api_key=self.tavily_api_key)
        else:
            self.search_engine = DDGS()
            
        self.state = None
        
        # 진행 상태 추적
        self.step_times = {}
        self.current_step = 0
        self.total_steps = 6
        self.step_names = {
            1: "1단계: 초기 아웃라인 생성",
            2: "2단계: 편집자 관점 생성",
            3: "3단계: 병렬 인터뷰 진행",
            4: "4단계: 아웃라인 개선",
            5: "5단계: 병렬 섹션 작성",
            6: "6단계: 최종 아티클 작성"
        }
        
        # Rich 콘솔 설정
        if RICH_AVAILABLE:
            self.console = console
            self.progress = None
            self.main_task = None
        else:
            self.console = None
    
    def start_step(self, step_num: int):
        """단계 시작"""
        self.current_step = step_num
        self.step_times[step_num] = {'start': time.time()}
        
        if RICH_AVAILABLE:
            step_name = self.step_names.get(step_num, f"단계 {step_num}")
            self.console.print(Panel(
                f"[bold blue]{step_name}[/bold blue]",
                title=f"진행률: {step_num}/{self.total_steps}",
                border_style="blue"
            ))
        else:
            step_name = self.step_names.get(step_num, f"단계 {step_num}")
            logger.info(f"[{step_num}/{self.total_steps}] {step_name}")
    
    def complete_step(self, step_num: int, result_summary: str = ""):
        """단계 완료"""
        if step_num in self.step_times:
            self.step_times[step_num]['end'] = time.time()
            duration = self.step_times[step_num]['end'] - self.step_times[step_num]['start']
            
            if RICH_AVAILABLE:
                self.console.print(Panel(
                    f"[bold green]✓ 완료[/bold green] (소요시간: {duration:.2f}초)\n{result_summary}",
                    title=f"단계 {step_num}",
                    border_style="green"
                ))
            else:
                logger.info(f"[{step_num}/{self.total_steps}] 완료 (소요시간: {duration:.2f}초) - {result_summary}")
    
    def show_progress_summary(self):
        """진행 상황 요약 표시"""
        if not RICH_AVAILABLE:
            return
            
        table = Table(title="🏁 STORM 연구 최종 결과")
        table.add_column("단계", style="cyan", no_wrap=True)
        table.add_column("상태", style="magenta")
        table.add_column("소요시간", style="green")
        
        total_duration = 0
        for step_num in range(1, self.total_steps + 1):
            step_name = self.step_names[step_num]
            
            if step_num in self.step_times and 'end' in self.step_times[step_num]:
                duration = self.step_times[step_num]['end'] - self.step_times[step_num]['start']
                total_duration += duration
                
                if duration < 60:
                    time_str = f"{duration:.1f}초"
                else:
                    minutes = int(duration // 60)
                    seconds = duration % 60
                    time_str = f"{minutes}분 {seconds:.1f}초"
                
                status = "✅ 완료"
            else:
                status = "❌ 실행안됨"
                time_str = "-"
            
            table.add_row(step_name, status, time_str)
        
        # 총 소요 시간 추가
        if total_duration < 60:
            total_time_str = f"{total_duration:.1f}초"
        else:
            minutes = int(total_duration // 60)
            seconds = total_duration % 60
            total_time_str = f"{minutes}분 {seconds:.1f}초"
            
        table.add_row("[bold]총 소요시간[/bold]", "[bold green]완료[/bold green]", f"[bold]{total_time_str}[/bold]")
        
        self.console.print(table)
    
    def log_parallel_progress(self, task_name: str, completed: int, total: int):
        """병렬 작업 진행 상황 로그"""
        if RICH_AVAILABLE:
            progress_bar = "█" * int(20 * completed / total) + "░" * (20 - int(20 * completed / total))
            percentage = int(100 * completed / total)
            self.console.print(f"\r[cyan]{task_name}[/cyan]: [{progress_bar}] {completed}/{total} ({percentage}%)", end="")
            if completed == total:
                self.console.print()  # 완료 시 줄바꿈
        else:
            import sys
            print(f"\r{task_name}: {completed}/{total} 완료 ({int(100 * completed / total)}%)", end="", flush=True)
            if completed == total:
                print()  # 완료 시 줄바꿈
        
    async def search_web(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """웹 검색 수행"""
        try:
            if hasattr(self.search_engine, 'search'):  # Tavily
                results = self.search_engine.search(query, max_results=max_results)
                search_results = [SearchResult(
                    content=r.get('content', ''),
                    url=r.get('url', ''),
                    title=r.get('title', '')
                ) for r in results]
            else:  # DuckDuckGo
                results = list(self.search_engine.text(query, max_results=max_results))
                search_results = [SearchResult(
                    content=r.get('body', ''),
                    url=r.get('href', ''),
                    title=r.get('title', '')
                ) for r in results]
            
            # 검색 결과 로깅 (조용히)
            # if RICH_AVAILABLE:
            #     console.print(f"[dim]🔍 검색 완료: '{query}' → {len(search_results)} 결과[/dim]")
            
            return search_results
            
        except Exception as e:
            # 검색 오류 조용히 처리
            return []
    
    async def create_outline_agent(self) -> AssistantAgent:
        """초기 아웃라인 생성 에이전트"""
        system_message = """
        당신은 위키피디아 작성자입니다. 사용자가 제공한 주제에 대한 위키피디아 페이지 아웃라인을 작성하세요.
        포괄적이고 구체적으로 작성하세요.
        
        응답은 반드시 다음 JSON 형식으로 제공하세요:
        {
            "page_title": "페이지 제목",
            "sections": [
                {
                    "section_title": "섹션 제목",
                    "description": "섹션 설명",
                    "subsections": [
                        {
                            "subsection_title": "서브섹션 제목",
                            "description": "서브섹션 설명"
                        }
                    ]
                }
            ]
        }
        """
        
        return AssistantAgent(
            name="outline_generator",
            model_client=self.model_client,
            system_message=system_message
        )
    
    async def create_perspective_agent(self) -> AssistantAgent:
        """다양한 관점의 편집자 생성 에이전트"""
        system_message = """
        당신은 위키피디아 편집자 팀을 구성하는 전문가입니다.
        주제에 대해 다양하고 구별되는 관점을 가진 편집자 그룹을 선택하세요.
        각 편집자는 서로 다른 관점, 역할, 소속을 나타냅니다.
        
        중요: 편집자 이름은 반드시 영문으로 작성하세요 (예: John_Smith, Sarah_Lee 등)
        
        응답은 반드시 다음 JSON 형식으로 제공하세요:
        {
            "editors": [
                {
                    "affiliation": "소속",
                    "name": "영문_이름",
                    "role": "역할",
                    "description": "편집자의 초점, 관심사, 동기에 대한 설명"
                }
            ]
        }
        """
        
        return AssistantAgent(
            name="perspective_generator",
            model_client=self.model_client,
            system_message=system_message
        )
    
    async def create_interview_agent(self, editor: Editor) -> AssistantAgent:
        """특정 편집자 관점의 인터뷰 에이전트"""
        system_message = f"""
        당신은 경험 많은 위키피디아 작성자이며 특정 페이지를 편집하고 싶어합니다.
        위키피디아 작성자로서의 정체성 외에도, 주제를 연구할 때 특정한 초점을 가지고 있습니다.
        
        당신의 페르소나:
        이름: {editor.name}
        역할: {editor.role}
        소속: {editor.affiliation}
        설명: {editor.description}
        
        지금 전문가와 채팅하여 정보를 얻고 있습니다. 다음과 같은 방식으로 인터뷰를 진행하세요:
        1. 기본 개념이나 정의부터 시작하여 점진적으로 심화된 질문을 하세요
        2. 당신의 관점({editor.role})에서 중요한 측면들을 집중적으로 탐구하세요
        3. 실용적인 응용이나 사례에 대해서도 질문하세요
        4. 한 번에 하나의 질문만 하고 이미 물어본 것은 다시 묻지 마세요
        
        전문가가 "지금까지 논의한 내용을 정리하면..."으로 시작하여 내용을 정리해주면, 
        "매우 유용한 정보를 제공해 주셔서 감사합니다!"라고 답하여 인터뷰를 마무리하세요.
        """
        
        # 한글 이름을 영문으로 변환하는 함수
        def sanitize_name(name: str) -> str:
            import re
            import hashlib
            
            # 먼저 영문, 숫자, 언더스코어, 하이픈만 추출
            sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', name)
            
            # 빈 문자열이면 원본 이름의 해시값 사용
            if not sanitized:
                # 원본 이름의 해시값으로 고유한 영문 이름 생성
                hash_value = hashlib.md5(name.encode('utf-8')).hexdigest()[:8]
                sanitized = f"editor_{hash_value}"
            
            return sanitized
        
        safe_name = sanitize_name(editor.name)
        
        return AssistantAgent(
            name=f"interviewer_{safe_name}",
            model_client=self.model_client,
            system_message=system_message
        )
    
    async def create_expert_agent(self) -> AssistantAgent:
        """도메인 전문가 에이전트 (검색 기능 포함)"""
        system_message = """
        당신은 정보를 효과적으로 사용할 수 있는 전문가입니다.
        위키피디아 페이지를 작성하고자 하는 위키피디아 작성자와 채팅하고 있습니다.
        관련 정보를 수집했으며 이제 이 정보를 사용하여 응답을 구성할 것입니다.
        
        응답을 최대한 유익하게 만들고 모든 문장이 수집된 정보에 의해 뒷받침되도록 하세요.
        각 응답은 신뢰할 수 있는 출처의 인용으로 뒷받침되어야 하며, 각주 형식으로 포맷하고 응답 후에 URL을 재현하세요.
        
        검색이 필요한 경우, SEARCH: [검색어] 형식으로 요청하세요.
        
        중요: 대화가 15-16번째 응답 이후부터는 정리를 준비하세요. 
        질문이 반복되거나 새로운 질문이 없을 때, 다음과 같이 마무리하세요:
        "지금까지 논의한 내용을 정리하면..." 으로 시작하여 핵심 포인트들을 체계적으로 정리해주세요.
        이때 다음 구조를 사용하세요:
        1. 주요 개념/정의
        2. 핵심 특징이나 장단점  
        3. 실용적 응용 사례
        4. 향후 전망이나 트렌드
        5. 위키피디아 작성에 유용한 핵심 키워드들
        """
        
        return AssistantAgent(
            name="domain_expert",
            model_client=self.model_client,
            system_message=system_message
        )
    
    async def create_section_writer_agent(self) -> AssistantAgent:
        """섹션 작성 에이전트"""
        system_message = """
        당신은 전문 위키피디아 작성자입니다.
        주어진 아웃라인과 참고 자료를 사용하여 위키피디아 섹션을 완성하세요.
        출처를 인용하고, 다음 참고 자료를 사용하세요.
        
        응답은 마크다운 형식으로 작성하고 [1], [2] 등의 각주를 사용하여 인용하세요.
        """
        
        return AssistantAgent(
            name="section_writer",
            model_client=self.long_context_model,
            system_message=system_message
        )
    
    async def create_final_writer_agent(self) -> AssistantAgent:
        """최종 아티클 작성 에이전트"""
        system_message = """
        당신은 전문 위키피디아 작성자입니다.
        주어진 섹션 초안들을 사용하여 완전한 위키 아티클을 작성하세요.
        위키피디아 형식 가이드라인을 엄격히 따르세요.
        
        마크다운 형식을 사용하여 완전한 위키 아티클을 작성하세요.
        "[1]"과 같은 각주를 사용하여 인용을 정리하고, 바닥글에서 중복을 피하세요.
        바닥글에 URL을 포함하세요.
        """
        
        return AssistantAgent(
            name="final_writer",
            model_client=self.long_context_model,
            system_message=system_message
        )
    
    async def create_human_proxy_agent(self) -> UserProxyAgent:
        """Human-in-the-loop을 위한 사용자 프록시 에이전트"""
        return UserProxyAgent(
            name="human_reviewer",
            input_func=lambda prompt: input(f"\n[Human Input Required] {prompt}\n> ")
        )
    
    async def generate_initial_outline(self, topic: str) -> Outline:
        """1단계: 초기 아웃라인 생성"""
        self.start_step(1)
        
        outline_agent = await self.create_outline_agent()
        termination = MaxMessageTermination(max_messages=2)
        
        team = RoundRobinGroupChat([outline_agent], termination_condition=termination)
        
        result = await team.run(task=f"주제 '{topic}'에 대한 위키피디아 아웃라인을 생성하세요.")
        
        # JSON 응답 파싱
        try:
            last_message = result.messages[-1].content
            # JSON 부분 추출
            if "```json" in last_message:
                json_start = last_message.find("```json") + 7
                json_end = last_message.find("```", json_start)
                json_str = last_message[json_start:json_end].strip()
            else:
                json_str = last_message
            
            outline_data = json.loads(json_str)
            outline = Outline(**outline_data)
            self.complete_step(1, f"아웃라인 생성 완료: {outline.page_title} ({len(outline.sections)}개 섹션)")
            return outline
        except Exception as e:
            # 아웃라인 파싱 오류 시 기본 아웃라인 반환
            outline = Outline(
                page_title=topic,
                sections=[
                    Section(section_title="개요", description="주제에 대한 개요"),
                    Section(section_title="배경", description="주제의 배경 정보"),
                    Section(section_title="주요 내용", description="주제의 핵심 내용")
                ]
            )
            self.complete_step(1, f"기본 아웃라인 생성: {outline.page_title} ({len(outline.sections)}개 섹션)")
            return outline
    
    async def generate_perspectives(self, topic: str) -> List[Editor]:
        """2단계: 다양한 관점의 편집자 생성"""
        self.start_step(2)
        
        perspective_agent = await self.create_perspective_agent()
        termination = MaxMessageTermination(max_messages=2)
        
        team = RoundRobinGroupChat([perspective_agent], termination_condition=termination)
        
        result = await team.run(task=f"주제 '{topic}'에 대해 3-5명의 다양한 관점을 가진 편집자를 생성하세요.")
        
        try:
            last_message = result.messages[-1].content
            if "```json" in last_message:
                json_start = last_message.find("```json") + 7
                json_end = last_message.find("```", json_start)
                json_str = last_message[json_start:json_end].strip()
            else:
                json_str = last_message
            
            editors_data = json.loads(json_str)
            editors = [Editor(**editor) for editor in editors_data["editors"]]
            
            # 편집자 정보 요약
            if RICH_AVAILABLE:
                editor_table = Table(title="생성된 편집자들")
                editor_table.add_column("이름", style="cyan")
                editor_table.add_column("역할", style="magenta")
                editor_table.add_column("소속", style="green")
                
                for editor in editors:
                    editor_table.add_row(editor.name, editor.role, editor.affiliation)
                
                self.console.print(editor_table)
            
            self.complete_step(2, f"{len(editors)}명의 편집자 생성 완료")
            return editors
        except Exception as e:
            # 편집자 파싱 오류 시 기본 편집자들 반환
            editors = [
                Editor(
                    affiliation="학술기관",
                    name="Academic_Researcher",
                    role="연구자",
                    description="학술적 관점에서 주제를 분석"
                ),
                Editor(
                    affiliation="산업계",
                    name="Industry_Expert",
                    role="산업 전문가",
                    description="실무적 관점에서 주제를 분석"
                )
            ]
            self.complete_step(2, f"기본 편집자 {len(editors)}명 생성")
            return editors
    
    async def conduct_single_interview(self, editor: Editor, topic: str, max_turns: int = 20) -> List[str]:
        """단일 편집자와의 인터뷰 진행 (병렬 처리용) - 실시간 출력"""
        
        try:
            interviewer = await self.create_interview_agent(editor)
            expert = await self.create_expert_agent()
            
            # 종료 조건: 19턴에서 강제 종료 (마지막 2턴에 정리할 시간 확보)
            termination = MaxMessageTermination(max_messages=19)
            
            team = RoundRobinGroupChat(
                [interviewer, expert], 
                termination_condition=termination
            )
            
            initial_task = f"주제 '{topic}'에 대한 위키피디아 기사를 작성 중입니다. 전문가님께 체계적으로 질문하겠습니다. 기본 개념부터 시작해서 점진적으로 심화된 내용까지 다루겠습니다."
            
            # 인터뷰 시작 알림
            if RICH_AVAILABLE:
                self.console.print(Panel(
                    f"[bold cyan]📋 {editor.name} 인터뷰 시작[/bold cyan]\n"
                    f"역할: {editor.role}\n"
                    f"소속: {editor.affiliation}\n"
                    f"관점: {editor.description}",
                    title=f"🎤 인터뷰 #{hash(editor.name) % 100:02d}",
                    border_style="cyan"
                ))
            else:
                print(f"\n🎤 {editor.name} 인터뷰 시작")
                print(f"역할: {editor.role}")
                print(f"소속: {editor.affiliation}")
                print("-" * 50)
            
            result = await team.run(task=initial_task)
            
            # 대화 내용 수집 및 실시간 출력
            conversation = []
            summary_found = False
            turn_count = 0
            
            for message in result.messages:
                turn_count += 1
                
                if "SEARCH:" in message.content:
                    # 검색 요청 처리
                    search_query = message.content.split("SEARCH:")[1].strip()
                    search_results = await self.search_web(search_query)
                    search_content = "\n".join([f"[{r.url}] {r.content}" for r in search_results[:3]])
                    conversation.append(f"검색 결과: {search_content}")
                    
                    # 검색 결과 실시간 출력
                    if RICH_AVAILABLE:
                        self.console.print(f"[dim yellow]🔍 검색: {search_query}[/dim yellow]")
                    else:
                        print(f"🔍 검색: {search_query}")
                        
                else:
                    conversation.append(f"{message.source}: {message.content}")
                    
                    # 실시간 대화 출력
                    if RICH_AVAILABLE:
                        # 메시지 출력 (짧게 자르기)
                        content_preview = message.content
                        if len(content_preview) > 150:
                            content_preview = content_preview[:150] + "..."
                        
                        # 발화자에 따라 색상 구분
                        if "interviewer" in message.source:
                            speaker_color = "blue"
                            speaker_icon = "❓"
                        else:
                            speaker_color = "green"
                            speaker_icon = "💡"
                        
                        self.console.print(f"[{speaker_color}]{speaker_icon} {message.source}[/{speaker_color}]: {content_preview}")
                    else:
                        content_preview = message.content
                        if len(content_preview) > 100:
                            content_preview = content_preview[:100] + "..."
                        print(f"{'❓' if 'interviewer' in message.source else '💡'} {message.source}: {content_preview}")
                    
                    # 전문가가 정리를 시작했는지 확인
                    if "지금까지 논의한 내용을 정리하면" in message.content:
                        summary_found = True
                        if RICH_AVAILABLE:
                            self.console.print(f"[bold yellow]📝 {editor.name} 정리 시작![/bold yellow]")
                        else:
                            print(f"📝 {editor.name} 정리 시작!")
            
            # 인터뷰 완료 정보
            if RICH_AVAILABLE:
                turn_info = f"({turn_count}/20턴)"
                if turn_count >= 19:
                    turn_info += " [MAX]"
                if summary_found:
                    turn_info += " [SUMMARY]"
                
                self.console.print(Panel(
                    f"[bold green]✅ 인터뷰 완료 {turn_info}[/bold green]\n"
                    f"총 대화 수: {len(conversation)}개",
                    title=f"🏁 {editor.name} 인터뷰 완료",
                    border_style="green"
                ))
            else:
                print(f"\n✅ {editor.name} 인터뷰 완료 ({turn_count}/20턴)")
                print(f"총 대화 수: {len(conversation)}개")
                print("-" * 50)
            
            return conversation
            
        except Exception as e:
            # 에러 로그
            if RICH_AVAILABLE:
                self.console.print(Panel(
                    f"[red]❌ 인터뷰 중 오류 발생: {str(e)}[/red]",
                    title=f"🚨 {editor.name} 인터뷰 실패",
                    border_style="red"
                ))
            else:
                print(f"❌ {editor.name} 인터뷰 실패: {str(e)}")
            
            return [f"편집자 {editor.name}: 인터뷰 중 오류가 발생했습니다."]
    
    async def conduct_all_interviews_parallel(self, editors: List[Editor], topic: str) -> Dict[str, List[str]]:
        """모든 편집자와의 인터뷰를 병렬로 진행"""
        self.start_step(3)
        
        # 병렬 인터뷰 실행
        tasks = []
        for editor in editors:
            task = asyncio.create_task(
                self.conduct_single_interview(editor, topic),
                name=f"interview_{editor.name}"
            )
            tasks.append((editor.name, task))
        
        # 모든 인터뷰 완료 대기
        interview_results = {}
        completed_count = 0
        
        if RICH_AVAILABLE:
            self.console.print(f"[dim]📋 {len(editors)}명의 편집자와 병렬 인터뷰 진행 중... (각 인터뷰당 최대 20턴)[/dim]")
            self.console.print(f"[dim]   • 기본 개념 → 심화 내용 → 실용적 응용 → 세부사항 탐구 → 전문가 정리 순서로 진행[/dim]")
            self.console.print(f"[dim]   • 실시간 인터뷰 내용을 아래에서 확인할 수 있습니다![/dim]")
            self.console.print("")
        
        for editor_name, task in tasks:
            try:
                result = await task
                interview_results[editor_name] = result
                completed_count += 1
                
                # 진행 상황 표시
                self.log_parallel_progress("인터뷰 진행", completed_count, len(editors))
                    
            except Exception as e:
                if RICH_AVAILABLE:
                    self.console.print(f"[red]❌[/red] 편집자 {editor_name} 인터뷰 실패")
                else:
                    print(f"❌ 편집자 {editor_name} 인터뷰 실패")
                interview_results[editor_name] = [f"인터뷰 실패: {str(e)}"]
                completed_count += 1
                self.log_parallel_progress("인터뷰 진행", completed_count, len(editors))
        
        # 인터뷰 결과 요약
        successful_interviews = sum(1 for v in interview_results.values() if not v[0].startswith("인터뷰 실패"))
        self.complete_step(3, f"병렬 인터뷰 완료: {successful_interviews}/{len(editors)} 성공")
        
        return interview_results
    
    async def write_single_section(self, section: Section, outline: Outline, interview_results: Dict[str, List[str]], topic: str) -> str:
        """단일 섹션 작성 (병렬 처리용)"""
        
        try:
            section_writer = await self.create_section_writer_agent()
            termination = MaxMessageTermination(max_messages=2)
            team = RoundRobinGroupChat([section_writer], termination_condition=termination)
            
            # 참고 자료 준비
            all_references = "\n\n".join([
                f"편집자 {name}의 연구 자료:\n" + "\n".join(conversations)
                for name, conversations in interview_results.items()
            ])
            
            task = f"""
            주제: {topic}
            
            전체 아웃라인:
            {outline.model_dump()}
            
            작성할 섹션: {section.section_title}
            섹션 설명: {section.description}
            
            참고 자료:
            {all_references}
            
            이 섹션의 완전한 위키피디아 콘텐츠를 작성하세요.
            """
            
            result = await team.run(task=task)
            return result.messages[-1].content
            
        except Exception as e:
            # 에러 로그 없이 조용히 처리
            return f"# {section.section_title}\n\n섹션 작성 중 오류가 발생했습니다: {str(e)}"
    
    async def write_sections_parallel(self, outline: Outline, interview_results: Dict[str, List[str]], topic: str) -> Dict[str, str]:
        """모든 섹션을 병렬로 작성"""
        self.start_step(5)
        
        # 병렬 섹션 작성 실행
        tasks = []
        for section in outline.sections:
            task = asyncio.create_task(
                self.write_single_section(section, outline, interview_results, topic),
                name=f"section_{section.section_title}"
            )
            tasks.append((section.section_title, task))
        
        # 모든 섹션 작성 완료 대기
        sections_content = {}
        completed_count = 0
        
        if RICH_AVAILABLE:
            self.console.print(f"[dim]📝 {len(outline.sections)}개 섹션을 병렬로 작성 중...[/dim]")
        
        for section_title, task in tasks:
            try:
                result = await task
                sections_content[section_title] = result
                completed_count += 1
                
                # 진행 상황 표시
                self.log_parallel_progress("섹션 작성", completed_count, len(outline.sections))
                    
            except Exception as e:
                if RICH_AVAILABLE:
                    self.console.print(f"[red]❌[/red] 섹션 '{section_title}' 작성 실패")
                else:
                    print(f"❌ 섹션 '{section_title}' 작성 실패")
                sections_content[section_title] = f"# {section_title}\n\n섹션 작성 실패: {str(e)}"
                completed_count += 1
                self.log_parallel_progress("섹션 작성", completed_count, len(outline.sections))
        
        # 섹션 작성 결과 요약
        successful_sections = sum(1 for v in sections_content.values() if not "섹션 작성 실패" in v)
        self.complete_step(5, f"병렬 섹션 작성 완료: {successful_sections}/{len(outline.sections)} 성공")
        
        return sections_content
    
    async def refine_outline(self, initial_outline: Outline, interview_results: Dict[str, List[str]], topic: str) -> Outline:
        """4단계: 인터뷰 결과를 바탕으로 아웃라인 개선"""
        self.start_step(4)
        
        outline_agent = await self.create_outline_agent()
        termination = MaxMessageTermination(max_messages=2)
        
        team = RoundRobinGroupChat([outline_agent], termination_condition=termination)
        
        # 인터뷰 결과 요약
        interview_summary = "\n\n".join([
            f"편집자 {name}의 인터뷰:\n" + "\n".join(conversations)
            for name, conversations in interview_results.items()
        ])
        
        task = f"""
        주제: {topic}
        
        기존 아웃라인:
        {initial_outline.model_dump()}
        
        전문가 인터뷰 결과:
        {interview_summary}
        
        인터뷰 결과를 바탕으로 위키피디아 아웃라인을 개선하세요.
        아웃라인이 포괄적이고 구체적인지 확인하세요.
        """
        
        result = await team.run(task=task)
        
        try:
            last_message = result.messages[-1].content
            if "```json" in last_message:
                json_start = last_message.find("```json") + 7
                json_end = last_message.find("```", json_start)
                json_str = last_message[json_start:json_end].strip()
            else:
                json_str = last_message
            
            refined_data = json.loads(json_str)
            refined_outline = Outline(**refined_data)
            
            # 개선된 아웃라인 표시
            if RICH_AVAILABLE:
                outline_table = Table(title="개선된 아웃라인")
                outline_table.add_column("섹션", style="cyan")
                outline_table.add_column("설명", style="white")
                
                for section in refined_outline.sections:
                    outline_table.add_row(section.section_title, section.description)
                
                self.console.print(outline_table)
            
            self.complete_step(4, f"아웃라인 개선 완료: {len(refined_outline.sections)}개 섹션")
            return refined_outline
        except Exception as e:
            # 개선된 아웃라인 파싱 오류 시 기존 아웃라인 사용
            self.complete_step(4, "아웃라인 개선 실패 - 기존 아웃라인 사용")
            return initial_outline
    
    async def write_final_article(self, outline: Outline, sections: Dict[str, str], topic: str) -> str:
        """6단계: 최종 위키 아티클 작성"""
        self.start_step(6)
        
        final_writer = await self.create_final_writer_agent()
        termination = MaxMessageTermination(max_messages=2)
        
        team = RoundRobinGroupChat([final_writer], termination_condition=termination)
        
        # 섹션 초안 결합
        sections_draft = "\n\n".join([
            f"## {title}\n{content}" for title, content in sections.items()
        ])
        
        task = f"""
        주제: {topic}
        
        섹션 초안들:
        {sections_draft}
        
        이 섹션 초안들을 사용하여 완전한 위키 아티클을 작성하세요.
        위키피디아 형식 가이드라인을 엄격히 따르세요.
        """
        
        result = await team.run(task=task)
        
        final_article = result.messages[-1].content
        word_count = len(final_article.split())
        
        self.complete_step(6, f"최종 아티클 작성 완료 (약 {word_count}단어)")
        
        return final_article
    
    async def run_parallel_storm_research(self, topic: str, enable_human_loop: bool = False) -> str:
        """병렬 STORM 연구 프로세스 실행"""
        start_time = time.time()
        
        # 시작 배너 표시
        if RICH_AVAILABLE:
            self.console.print(Panel(
                f"[bold yellow]병렬 STORM 연구 시작[/bold yellow]\n주제: {topic}",
                title="🚀 연구 시작",
                border_style="yellow"
            ))
        else:
            logger.info(f"병렬 STORM 연구 시작: {topic}")
        
        # 상태 초기화
        self.state = StormResearchState(topic=topic)
        
        try:
            # 1단계: 초기 아웃라인 생성
            self.state.outline = await self.generate_initial_outline(topic)
            
            # 2단계: 편집자 관점 생성
            self.state.editors = await self.generate_perspectives(topic)
            
            # Human-in-the-loop: 편집자 검토
            if enable_human_loop:
                if RICH_AVAILABLE:
                    self.console.print("\n[bold cyan]=== 생성된 편집자들 ===[/bold cyan]")
                    for editor in self.state.editors:
                        self.console.print(f"- {editor.name} ({editor.role}): {editor.description}")
                    
                    user_input = input("\n편집자들을 승인하시겠습니까? (y/n): ")
                    if user_input.lower() != 'y':
                        self.console.print("편집자 생성을 다시 진행합니다...")
                        self.state.editors = await self.generate_perspectives(topic)
                else:
                    print("\n=== 생성된 편집자들 ===")
                    for editor in self.state.editors:
                        print(f"- {editor.name} ({editor.role}): {editor.description}")
                    
                    user_input = input("\n편집자들을 승인하시겠습니까? (y/n): ")
                    if user_input.lower() != 'y':
                        print("편집자 생성을 다시 진행합니다...")
                        self.state.editors = await self.generate_perspectives(topic)
            
            # 3단계: 병렬 인터뷰 진행
            self.state.interview_results = await self.conduct_all_interviews_parallel(self.state.editors, topic)
            
            # 4단계: 아웃라인 개선
            self.state.outline = await self.refine_outline(
                self.state.outline, 
                self.state.interview_results, 
                topic
            )
            
            # Human-in-the-loop: 아웃라인 검토
            if enable_human_loop:
                if RICH_AVAILABLE:
                    self.console.print(f"\n[bold cyan]=== 개선된 아웃라인 ===[/bold cyan]")
                    self.console.print(f"제목: {self.state.outline.page_title}")
                    for section in self.state.outline.sections:
                        self.console.print(f"- {section.section_title}: {section.description}")
                    
                    user_input = input("\n아웃라인을 승인하시겠습니까? (y/n): ")
                    if user_input.lower() != 'y':
                        self.console.print("아웃라인 개선을 다시 진행합니다...")
                        self.state.outline = await self.refine_outline(
                            self.state.outline, 
                            self.state.interview_results, 
                            topic
                        )
                else:
                    print(f"\n=== 개선된 아웃라인 ===")
                    print(f"제목: {self.state.outline.page_title}")
                    for section in self.state.outline.sections:
                        print(f"- {section.section_title}: {section.description}")
                    
                    user_input = input("\n아웃라인을 승인하시겠습니까? (y/n): ")
                    if user_input.lower() != 'y':
                        print("아웃라인 개선을 다시 진행합니다...")
                        self.state.outline = await self.refine_outline(
                            self.state.outline, 
                            self.state.interview_results, 
                            topic
                        )
            
            # 5단계: 병렬 섹션 작성
            self.state.sections = await self.write_sections_parallel(
                self.state.outline, 
                self.state.interview_results, 
                topic
            )
            
            # 6단계: 최종 아티클 작성
            self.state.final_article = await self.write_final_article(
                self.state.outline, 
                self.state.sections, 
                topic
            )
            
            # 완료 정보 표시
            total_time = time.time() - start_time
            if RICH_AVAILABLE:
                self.console.print(Panel(
                    f"[bold green]병렬 STORM 연구 완료![/bold green]\n전체 소요시간: {total_time:.2f}초",
                    title="✅ 연구 완료",
                    border_style="green"
                ))
                
                # 최종 진행 상황 표시
                self.show_progress_summary()
            else:
                logger.info(f"병렬 STORM 연구 완료! 전체 소요시간: {total_time:.2f}초")
            
            return self.state.final_article
            
        except Exception as e:
            if RICH_AVAILABLE:
                self.console.print(Panel(
                    f"[red]병렬 STORM 연구 중 오류 발생: {e}[/red]",
                    title="❌ 연구 실패",
                    border_style="red"
                ))
            else:
                print(f"❌ 병렬 STORM 연구 중 오류 발생: {e}")
            raise e

# 사용 예제
async def main():
    """메인 실행 함수"""
    # Rich 설치 안내
    if not RICH_AVAILABLE:
        print("💡 더 나은 시각화를 위해 Rich 라이브러리를 설치하세요:")
        print("   pip install rich")
        print("-" * 50)
    
    # 병렬 STORM 시스템 초기화 (워커 수 설정)
    storm_system = ParallelStormResearchSystem(max_workers=4)
    
    # 연구 주제 설정
    topic = "LLM 추론 최적화를 위한 Groq LPU와 NVIDIA GPU 비교 분석"
    
    # 디버그 모드 활성화 (선택사항)
    # export DEBUG_STORM=1 로 설정하면 더 자세한 로그를 볼 수 있습니다.
    # 디버그 모드에서는 각 인터뷰의 턴 수와 완료 상태를 확인할 수 있습니다.
    
    # 시스템 설정 정보 표시
    if RICH_AVAILABLE:
        console.print(Panel(
            f"[cyan]🔧 시스템 설정[/cyan]\n"
            f"• 병렬 워커 수: {storm_system.max_workers}\n"
            f"• 인터뷰당 최대 턴 수: 20\n"
            f"• 총 단계: {storm_system.total_steps}단계\n"
            f"• Human-in-the-Loop: 활성화\n"
            f"• 15-16턴에서 전문가가 내용 정리 시작",
            title="⚙️ 설정 정보",
            border_style="cyan"
        ))
    else:
        print("⚙️ 시스템 설정:")
        print(f"• 병렬 워커 수: {storm_system.max_workers}")
        print(f"• 인터뷰당 최대 턴 수: 20")
        print(f"• 총 단계: {storm_system.total_steps}단계")
        print(f"• Human-in-the-Loop: 활성화")
        print(f"• 15-16턴에서 전문가가 내용 정리 시작")
        print("-" * 50)
    
    # 병렬 STORM 연구 실행
    try:
        final_article = await storm_system.run_parallel_storm_research(
            topic=topic, 
            enable_human_loop=True
        )
        
        # 결과 표시
        if RICH_AVAILABLE:
            console.print(Panel(
                final_article,
                title="📄 최종 연구 결과",
                border_style="cyan"
            ))
        else:
            print("\n" + "="*80)
            print("병렬 STORM 연구 완료!")
            print("="*80)
            print(final_article)
        
        # 결과를 파일로 저장
        filename = f"parallel_storm_research_{topic.replace(' ', '_')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_article)
        
        if RICH_AVAILABLE:
            console.print(f"\n[green]✅ 결과가 파일로 저장되었습니다: {filename}[/green]")
        else:
            print(f"\n결과가 파일로 저장되었습니다: {filename}")
        
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(Panel(
                f"[red]오류 발생: {e}[/red]",
                title="❌ 연구 실패",
                border_style="red"
            ))
        else:
            print(f"❌ 오류 발생: {e}")
    
    finally:
        # 리소스 정리
        await storm_system.model_client.close()
        await storm_system.long_context_model.close()

if __name__ == "__main__":
    # asyncio 이벤트 루프 실행
    asyncio.run(main())