"""AutoGen STORM Research Assistant Workflow

이 모듈은 AutoGen의 GraphFlow를 사용하여 STORM 연구 워크플로우를 정의합니다.
자동 모드와 인터랙티브 모드를 모두 지원합니다.
"""

import json
import asyncio
import uuid
from typing import List, Dict, Any, Optional
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

from .agents import (
    create_analyst_generator_agent,
    create_interviewer_agent,
    create_expert_agent,
    create_section_writer_agent,
    create_report_writer_agent,
    create_intro_writer_agent,
    create_conclusion_writer_agent,
    create_feedback_aware_interviewer,
    create_feedback_aware_report_writer,
    create_feedback_aware_intro_writer,
    create_feedback_aware_conclusion_writer
)
from .models import Analyst, ResearchTask, ResearchResult, InterviewResult, Perspectives
from .config import StormConfig, ModelConfig
from .tracing import get_tracing_manager


def safe_input(prompt: str, fallback_prompt: str = None) -> str:
    """Safely handle input with encoding issues"""
    try:
        return input(prompt).strip()
    except UnicodeDecodeError:
        print("입력 인코딩 오류. 숫자나 영문만 입력해주세요.")
        fallback = fallback_prompt or prompt.replace("한국어", "Korean").replace("선택", "Choice")
        return input(fallback).strip()


class StormWorkflow:
    """STORM 연구 워크플로우 클래스 - 자동 모드와 인터랙티브 모드 통합"""
    
    def __init__(self, config: StormConfig, interactive_mode: bool = False):
        """워크플로우 초기화
        
        Args:
            config: STORM 설정
            interactive_mode: 인터랙티브 모드 활성화 여부
        """
        self.config = config
        self.interactive_mode = interactive_mode
        self.tracing_manager = get_tracing_manager()
        
        # 기본 모델 클라이언트 생성
        model_config = config.model_config.to_autogen_config()
        self.model_client = ChatCompletionClient.load_component(model_config)
        
        # 에이전트별 모델 클라이언트 생성
        self.expert_model_client = self._create_model_client(config.expert_model_config)
        self.writer_model_client = self._create_model_client(config.writer_model_config)
        self.analyst_model_client = self._create_model_client(config.analyst_model_config)
        self.interviewer_model_client = self._create_model_client(config.interviewer_model_config)
        
        # 인터랙티브 모드를 위한 상태
        if self.interactive_mode:
            self.current_analysts: List[Analyst] = []
            self.current_interviews: List[InterviewResult] = []
            self.current_report_parts: Dict[str, str] = {}
            self.current_task: Optional[ResearchTask] = None
            self.report_versions: List[Dict[str, str]] = []
    
    def _create_model_client(self, model_config: Optional[ModelConfig]):
        """모델 설정에서 클라이언트 생성 (없으면 기본 클라이언트 사용)"""
        if model_config is None:
            return self.model_client
        
        config_dict = model_config.to_autogen_config()
        return ChatCompletionClient.load_component(config_dict)
        
    async def run_research(self, task: ResearchTask) -> ResearchResult:
        """연구 작업을 실행합니다
        
        Args:
            task: 연구 작업
            
        Returns:
            연구 결과
        """
        if self.interactive_mode:
            return await self._run_interactive_research(task)
        else:
            return await self._run_automatic_research(task)
    
    async def _run_automatic_research(self, task: ResearchTask) -> ResearchResult:
        """자동 모드로 연구를 실행합니다"""
        # Langfuse 추적 시작
        task_id = str(uuid.uuid4())
        
        with self.tracing_manager.trace_research(topic=task.topic, task_id=task_id) as trace:
            try:
                print(f"🔬 연구 시작: {task.topic}")
                if trace:
                    trace_url = self.tracing_manager.get_trace_url()
                    if trace_url:
                        print(f"🔍 Langfuse 추적 시작 - Trace URL: {trace_url}")
                
                # 1단계: 분석가 생성
                print("👥 분석가 생성 중...")
                analysts = await self._generate_analysts_with_diverse_tools(task)
                print(f"✅ {len(analysts)}명의 분석가 생성 완료")
                
                # 분석가 생성 이벤트 로깅
                self.tracing_manager.log_event(
                    "analysts_created",
                    {
                        "count": len(analysts),
                        "analysts": [{"name": a.name, "role": a.role} for a in analysts]
                    }
                )
                
                # 2단계: 병렬 인터뷰 진행
                print("🎤 인터뷰 진행 중...")
                interviews = await self._conduct_interviews(analysts, task)
                print(f"✅ {len(interviews)}개의 인터뷰 완료")
                
                # 인터뷰 완료 이벤트 로깅
                self.tracing_manager.log_event(
                    "interviews_completed",
                    {"count": len(interviews)}
                )
                
                # 3단계: 보고서 작성
                print("📝 보고서 작성 중...")
                report_parts = await self._write_report(task.topic, interviews)
                print("✅ 보고서 작성 완료")
                
                # 최종 결과 조합
                final_report = self._assemble_final_report(report_parts)
                
                # 보고서 생성 로깅
                self.tracing_manager.log_generation(
                    "final_report",
                    input_data={"topic": task.topic, "analyst_count": len(analysts)},
                    output_data={"length": len(final_report), "word_count": len(final_report.split())}
                )
                
                result = ResearchResult(
                    topic=task.topic,
                    analysts=analysts,
                    interviews=interviews,
                    introduction=report_parts["introduction"],
                    main_content=report_parts["main_content"],
                    conclusion=report_parts["conclusion"],
                    final_report=final_report
                )
                
                # 성공 이벤트 로깅
                self.tracing_manager.log_event(
                    "research_completed",
                    {
                        "analyst_count": len(analysts),
                        "interview_count": len(interviews),
                        "report_length": len(final_report),
                        "word_count": len(final_report.split())
                    }
                )
                
                return result
            
            except Exception as e:
                print(f"❌ 연구 중 오류 발생: {e}")
                
                # 에러 이벤트 로깅
                self.tracing_manager.log_event(
                    "research_error",
                    {"error": str(e), "error_type": type(e).__name__},
                    level="ERROR"
                )
                
                raise
    
    async def _run_interactive_research(self, task: ResearchTask) -> ResearchResult:
        """인터랙티브 모드로 연구를 실행합니다"""
        print(f"\n🚀 인터랙티브 STORM 연구 시작: {task.topic}")
        print("="*60)
        
        # 1단계: 분석가 수 선택 (휴먼 피드백)
        final_analyst_count = self._get_analyst_count_from_user(task.max_analysts)
        task.max_analysts = final_analyst_count
        
        print(f"\n👥 {final_analyst_count}명의 분석가로 연구를 진행합니다...")
        
        # 2단계: 자동 연구 진행 (다양한 툴 활용 분석가 생성 → 인터뷰 → 보고서 작성)
        print("\n🔍 다양한 데이터 소스와 툴을 활용하는 분석가 생성 중...")
        analysts = await self._generate_analysts_with_diverse_tools(task)
        self.current_analysts = analysts  # 상태 저장
        
        print(f"\n🎤 {len(analysts)}명의 분석가와 인터뷰 진행 중...")
        interviews = await self._conduct_interviews(analysts, task)
        self.current_interviews = interviews  # 상태 저장
        
        print(f"\n📝 {len(interviews)}개의 인터뷰를 바탕으로 보고서 작성 중...")
        report_parts = await self._write_report(task.topic, interviews)
        
        # 3단계: 최종 보고서 승인 (휴먼 피드백)
        final_report_parts = await self._get_final_report_approval(task.topic, report_parts)
        
        # 최종 결과 조합
        final_report = self._assemble_final_report(final_report_parts)
        
        return ResearchResult(
            topic=task.topic,
            analysts=analysts,
            interviews=interviews,
            introduction=final_report_parts["introduction"],
            main_content=final_report_parts["main_content"],
            conclusion=final_report_parts["conclusion"],
            final_report=final_report
        )
    
    def _get_analyst_count_from_user(self, default_count: int) -> int:
        """사용자로부터 분석가 수를 입력받습니다"""
        
        print(f"\n👥 분석가 수 선택")
        print("="*40)
        print(f"기본 설정: {default_count}명의 분석가")
        print("더 많은 분석가는 더 다양한 관점을 제공하지만 시간이 더 걸립니다.")
        
        while True:
            try:
                user_input = safe_input(
                    f"\n원하는 분석가 수를 입력하세요 (1-10, 기본값: {default_count}): ",
                    f"Enter number of analysts (1-10, default: {default_count}): "
                )
                
                if not user_input:  # 엔터만 누른 경우
                    return default_count
                
                count = int(user_input)
                if 1 <= count <= 10:
                    return count
                else:
                    print("❌ 1-10 사이의 숫자를 입력해주세요.")
                    
            except ValueError:
                print("❌ 올바른 숫자를 입력해주세요.")
    
    async def _get_final_report_approval(self, topic: str, report_parts: Dict[str, str]) -> Dict[str, str]:
        """최종 보고서 승인을 받습니다"""
        
        # 첫 번째 보고서 버전 저장
        self.report_versions.append(report_parts.copy())
        self.current_report_parts = report_parts.copy()  # 현재 보고서 저장
        
        print(f"\n📋 최종 보고서 검토 (버전 {len(self.report_versions)})")
        print("="*60)
        
        # 전체 보고서 길이 계산 (빈 문자열 고려)
        total_length = len((report_parts.get('introduction', '') or '') + 
                          (report_parts.get('main_content', '') or '') + 
                          (report_parts.get('conclusion', '') or ''))
        
        # 보고서 미리보기 생성
        preview = f"""
📖 **보고서 미리보기 (버전 {len(self.report_versions)})**

**서론 (처음 200자):**
{(report_parts.get('introduction', '') or '서론 내용이 빈 값입니다.')[:200]}...

**본문 (처음 300자):**
{(report_parts.get('main_content', '') or '본문 내용이 빈 값입니다.')[:300]}...

**결론 (처음 200자):**
{(report_parts.get('conclusion', '') or '결론 내용이 빈 값입니다.')[:200]}...

전체 보고서 길이: 약 {total_length}자
"""
        
        print(preview)
        
        while True:
            menu_options = [
                "1. ✅ 승인 - 이 보고서로 완료",
                "2. 🔄 재작성 - 보고서를 다시 작성",
                "3. 📄 전체보기 - 전체 보고서 내용 확인"
            ]
            
            # 이전 버전이 있는 경우 비교 옵션 추가
            if len(self.report_versions) > 1:
                menu_options.append("4. 🔍 이전 버전과 비교")
            
            print(f"\n다음 중 선택해주세요:")
            for option in menu_options:
                print(option)
            
            choice = safe_input(
                f"\n선택 (1-{len(menu_options)}): ",
                f"Choice (1-{len(menu_options)}): "
            )
            
            if choice == "1":
                print("\n✅ 보고서가 승인되었습니다!")
                print(f"💾 총 {len(self.report_versions)}개의 버전이 생성되었습니다.")
                return report_parts
                
            elif choice == "2":
                print("\n🔄 보고서 재작성 옵션을 선택하세요:")
                print("1. 🔄 완전 재연구 (새로운 인터뷰부터 다시)")
                print("2. ✏️ 사용자 피드백 반영 재작성")
                
                rewrite_choice = safe_input(
                    "\n재작성 방식 선택 (1-2): ",
                    "Choice (1-2): "
                )
                
                if rewrite_choice == "1":
                    print("\n🔄 완전히 새로운 연구를 시작합니다...")
                    print("💡 다양한 툴을 활용하는 새로운 분석가들로 전체 워크플로우를 재실행합니다.")
                    # 새로운 전체 연구 진행
                    task_copy = ResearchTask(
                        topic=topic,
                        max_analysts=len(self.current_analysts),
                        max_interview_turns=3,
                        parallel_interviews=True
                    )
                    # 전체 워크플로우 재실행
                    research_result = await self._run_automatic_research(task_copy)
                    new_report_parts = {
                        "main_content": research_result.main_content,
                        "introduction": research_result.introduction,
                        "conclusion": research_result.conclusion
                    }
                    # 새로운 데이터로 상태 업데이트
                    self.current_analysts = research_result.analysts
                    self.current_interviews = research_result.interviews
                    
                elif rewrite_choice == "2":
                    print("\n✏️ 어떤 부분을 개선하고 싶으신가요?")
                    feedback = safe_input(
                        "개선 요청사항을 입력하세요: ",
                        "Enter improvement request: "
                    )
                    if feedback:
                        print(f"\n💡 피드백 반영: {feedback}")
                        print("🔄 피드백을 반영하여 새로운 인터뷰부터 다시 시작합니다...")
                        print("⚠️ 완전히 새로운 관점과 내용으로 보고서를 생성합니다.")
                        new_report_parts = await self._rewrite_with_feedback(topic, feedback)
                    else:
                        print("피드백이 없어 기본 재작성을 진행합니다.")
                        new_report_parts = await self._write_report(topic, self.current_interviews)
                else:
                    print("잘못된 선택입니다. 기본 재작성을 진행합니다.")
                    new_report_parts = await self._write_report(topic, self.current_interviews)
                
                # 새 버전을 히스토리에 추가
                self.report_versions.append(new_report_parts.copy())
                self.current_report_parts = new_report_parts.copy()  # 현재 보고서 업데이트
                
                # 재작성된 보고서로 다시 검토 (루프 계속)
                print(f"\n✨ 보고서가 재작성되었습니다! (버전 {len(self.report_versions)})")
                report_parts = new_report_parts
                continue  # while 루프 계속해서 다시 검토
                
            elif choice == "3":
                self._show_full_report(report_parts)
                
            elif choice == "4" and len(self.report_versions) > 1:
                self._compare_report_versions()
                
            else:
                print(f"❌ 1-{len(menu_options)}을 입력해주세요.")
    
    def _show_full_report(self, report_parts: Dict[str, str]):
        """전체 보고서를 보여줍니다"""
        
        print("\n" + "="*80)
        print("📄 전체 보고서")
        print("="*80)
        
        print("\n🔸 서론")
        print("-" * 40)
        print(report_parts['introduction'])
        
        print("\n🔸 본문")
        print("-" * 40)
        print(report_parts['main_content'])
        
        print("\n🔸 결론")
        print("-" * 40)
        print(report_parts['conclusion'])
        
        print("\n" + "="*80)
        
        safe_input("\n계속하려면 엔터를 누르세요...", "Press Enter to continue...")  # 사용자가 읽을 시간 제공
    
    def _compare_report_versions(self):
        """보고서 버전들을 비교합니다"""
        
        print("\n" + "="*80)
        print("🔍 보고서 버전 비교")
        print("="*80)
        
        print(f"\n총 {len(self.report_versions)}개의 버전이 있습니다:")
        
        # 각 버전의 요약 정보 표시
        for i, version in enumerate(self.report_versions, 1):
            intro_preview = version['introduction'][:100] + "..." if len(version['introduction']) > 100 else version['introduction']
            total_length = len(version['introduction'] + version['main_content'] + version['conclusion'])
            
            print(f"\n📄 버전 {i}:")
            print(f"   서론 미리보기: {intro_preview}")
            print(f"   전체 길이: {total_length}자")
        
        # 비교할 버전 선택
        while True:
            try:
                version_num = safe_input(
                    f"\n어떤 버전을 자세히 보시겠습니까? (1-{len(self.report_versions)}, 0=취소): ",
                    f"Which version would you like to see? (1-{len(self.report_versions)}, 0=cancel): "
                )
                
                if version_num == "0":
                    print("비교를 취소합니다.")
                    break
                
                version_idx = int(version_num) - 1
                if 0 <= version_idx < len(self.report_versions):
                    selected_version = self.report_versions[version_idx]
                    
                    print(f"\n📖 버전 {version_num} 전체 내용:")
                    print("-" * 60)
                    
                    print(f"\n🔸 서론")
                    print("-" * 30)
                    print(selected_version['introduction'])
                    
                    print(f"\n🔸 본문")
                    print("-" * 30)
                    print(selected_version['main_content'])
                    
                    print(f"\n🔸 결론")
                    print("-" * 30)
                    print(selected_version['conclusion'])
                    
                    print("-" * 60)
                    
                    # 계속 다른 버전을 볼지 물어보기
                    continue_choice = safe_input(
                        "\n다른 버전을 보시겠습니까? (y/n): ",
                        "View another version? (y/n): "
                    ).lower()
                    if continue_choice != 'y':
                        break
                else:
                    print(f"❌ 1-{len(self.report_versions)} 사이의 숫자를 입력해주세요.")
                    
            except ValueError:
                print("❌ 올바른 숫자를 입력해주세요.")
        
        print("\n" + "="*80)
        safe_input("\n계속하려면 엔터를 누르세요...", "Press Enter to continue...")
    
    async def _rewrite_with_feedback(self, topic: str, feedback: str) -> Dict[str, str]:
        """사용자 피드백을 반영하여 기존 분석가 + 추가 분석가로 전체 워크플로우를 재실행합니다"""
        
        print("🔄 피드백을 반영한 추가 분석가 생성 중...")
        
        # 피드백을 반영한 추가 분석가 1명 생성
        task_with_feedback = ResearchTask(
            topic=topic,
            max_analysts=1,  # 추가 분석가 1명만
            max_interview_turns=3,
            parallel_interviews=True,
            user_feedback=feedback
        )
        
        # 추가 분석가 생성
        additional_analyst = await self._generate_additional_analyst_with_feedback(
            task_with_feedback, 
            feedback,
            self.current_analysts
        )
        
        print(f"🎤 추가 분석가 '{additional_analyst.name}'와 함께 피드백 중심 워크플로우 재실행 중...")
        print(f"👥 총 {len(self.current_analysts) + 1}명의 분석가로 피드백 중심 연구 진행")
        
        # 기존 분석가들 + 추가 분석가로 전체 워크플로우 재실행
        all_analysts = self.current_analysts + [additional_analyst]
        updated_task = ResearchTask(
            topic=topic,
            max_analysts=len(all_analysts),
            max_interview_turns=3,
            parallel_interviews=True,
            user_feedback=feedback  # 피드백 컨텍스트 추가
        )
        
        # 피드백 컨텍스트가 강화된 인터뷰 진행
        print(f"\n🎤 {len(all_analysts)}명의 분석가와 피드백 중심 인터뷰 진행 중...")
        interviews = await self._conduct_feedback_aware_interviews(all_analysts, updated_task, feedback)
        print(f"✅ {len(interviews)}개의 피드백 중심 인터뷰 완료")
        
        # 피드백이 반영된 보고서 작성
        print("\n📝 피드백을 중심으로 보고서 작성 중...")
        report_parts = await self._write_feedback_aware_report(topic, interviews, feedback)
        print("✅ 피드백 중심 보고서 작성 완료")
        
        # 새로운 데이터로 상태 업데이트
        self.current_analysts = all_analysts
        self.current_interviews = interviews
        
        return report_parts
    
    async def _generate_analysts(self, task: ResearchTask) -> List[Analyst]:
        """분석가들을 생성합니다"""
        
        generator_agent = create_analyst_generator_agent(self.analyst_model_client)
        
        # 분석가 생성 요청
        prompt = f"""다음 연구 주제에 대해 {task.max_analysts}명의 전문 분석가를 생성해주세요:

        주제: {task.topic}

        각 분석가는 서로 다른 관점과 전문성을 가져야 하며, 다음 JSON 형식으로 반환해주세요:

        {{
            "analysts": [
                {{
                    "name": "분석가 이름",
                    "role": "역할",
                    "affiliation": "소속 기관",
                    "description": "관심사와 전문성에 대한 상세한 설명"
                }}
            ]
        }}"""
        
        # 단일 에이전트 실행
        team = RoundRobinGroupChat(
            [generator_agent],
            termination_condition=MaxMessageTermination(max_messages=2)
        )
        
        result = await team.run(task=prompt)
        response_text = result.messages[-1].content
        
        # JSON 파싱
        try:
            # JSON 부분 추출
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            
            data = json.loads(json_str)
            perspectives = Perspectives(**data)
            return perspectives.analysts
        except Exception as e:
            print(f"분석가 파싱 오류: {e}")
            # 기본 분석가 반환
            return [
                Analyst(
                    name="일반 연구자",
                    role="연구 분석가",
                    affiliation="연구 기관",
                    description=f"{task.topic}에 대한 일반적인 연구와 분석을 담당"
                )
            ]
    
    async def _generate_analysts_with_diverse_tools(self, task: ResearchTask) -> List[Analyst]:
        """다양한 툴과 데이터 소스를 활용할 수 있는 분석가들을 생성합니다"""
        
        generator_agent = create_analyst_generator_agent(self.analyst_model_client)
        
        # 다양한 툴과 데이터 소스를 고려한 분석가 생성 프롬프트
        prompt = f"""다음 연구 주제에 대해 {task.max_analysts}명의 다양한 전문 분석가를 생성해주세요:

        주제: {task.topic}

        중요: 각 분석가는 다음과 같은 검색 도구들을 활용할 수 있습니다:
        
        사용 가능한 검색 도구:
        - web_search: 웹에서 최신 정보와 일반적인 주제 검색 (Tavily API)
        - duckduckgo_search: 프라이버시 중시 검색과 즉석 답변
        - naver_news_search: 한국 관련 뉴스와 최신 이슈 검색
        - wikipedia_search: 백과사전 정보, 기본 개념, 정의, 역사적 배경
        - arxiv_search: 과학적, 기술적 주제의 학술 논문 검색
        
        데이터 소스 활용 예시:
        - 학술 연구: ArXiv 논문 + Wikipedia 배경지식 + 웹 검색으로 최신 동향
        - 시장 분석: 웹 검색으로 산업 동향 + 뉴스 검색으로 최신 이슈
        - 기술 동향: ArXiv 최신 논문 + 웹 검색으로 실제 적용 사례
        - 사회 이슈: 뉴스 검색 + Wikipedia 배경 + DuckDuckGo로 다양한 관점
        - 역사/문화: Wikipedia 기본 정보 + 웹 검색으로 상세 자료
        
        각 분석가는 서로 다른 관점과 전문성을 가져야 하며, 다음 JSON 형식으로 반환해주세요:

        {{
            "analysts": [
                {{
                    "name": "분석가 이름",
                    "role": "역할",
                    "affiliation": "소속 기관",
                    "description": "관심사, 전문성, 그리고 어떤 검색 도구들을 주로 활용할지에 대한 구체적인 설명 (예: 'ArXiv와 웹 검색을 활용한 최신 AI 기술 동향 분석')"
                }}
            ]
        }}"""
        
        # 단일 에이전트 실행
        team = RoundRobinGroupChat(
            [generator_agent],
            termination_condition=MaxMessageTermination(max_messages=2)
        )
        
        result = await team.run(task=prompt)
        response_text = result.messages[-1].content
        
        # JSON 파싱
        try:
            # JSON 부분 추출
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            
            data = json.loads(json_str)
            perspectives = Perspectives(**data)
            return perspectives.analysts
        except Exception as e:
            print(f"다양한 툴 분석가 파싱 오류: {e}")
            # 기본 분석가 반환
            return [
                Analyst(
                    name="다양한 데이터 전문가",
                    role="데이터 마이닝 전문가",
                    affiliation="연구 기관",
                    description=f"{task.topic}에 대한 다양한 데이터 소스와 분석 툴을 활용한 연구를 담당"
                )
            ]
    
    async def _generate_additional_analyst_with_feedback(self, task: ResearchTask, feedback: str, existing_analysts: List[Analyst]) -> Analyst:
        """피드백을 반영한 추가 분석가 1명을 생성합니다"""
        
        analyst_generator = create_analyst_generator_agent(self.analyst_model_client)
        
        # 기존 분석가 정보 구성
        existing_context = "**기존 분석가들:**\n"
        for analyst in existing_analysts:
            existing_context += f"- {analyst.name} ({analyst.role}): {analyst.description}\n"
        
        # 피드백을 반영한 추가 분석가 생성 프롬프트
        analyst_prompt = f"""
        주제: {task.topic}
        사용자 피드백: {feedback}
        
        {existing_context}
        
        사용 가능한 검색 도구:
        - web_search: 웹에서 최신 정보와 일반적인 주제 검색
        - duckduckgo_search: 프라이버시 중시 검색과 즉석 답변
        - naver_news_search: 한국 관련 뉴스와 최신 이슈 검색
        - wikipedia_search: 백과사전 정보, 기본 개념, 정의, 역사적 배경
        - arxiv_search: 과학적, 기술적 주제의 학술 논문 검색
        
        위 피드백을 분석하여, 기존 분석가들이 다루지 못한 관점을 보완할 수 있는 
        추가 분석가 1명을 생성해주세요.
        
        요구사항:
        1. 피드백에서 언급된 구체적 요구사항에 직접 대응
        2. 기존 분석가들과 다른 새로운 전문 분야/관점
        3. 위에 나열된 검색 도구들을 적절히 활용할 수 있는 전문성
        4. 실무적이고 실용적인 인사이트 제공 가능
        
        다음 JSON 형식으로 반환해주세요:
        {{
            "name": "분석가 이름",
            "role": "역할",
            "affiliation": "소속 기관",
            "description": "피드백을 반영한 전문성과 어떤 검색 도구들을 주로 활용할지에 대한 구체적인 설명 (예: '뉴스와 웹 검색을 활용한 시장 동향 분석')"
        }}
        """
        
        team = RoundRobinGroupChat([analyst_generator], termination_condition=MaxMessageTermination(max_messages=2))
        result = await team.run(task=analyst_prompt)
        
        # 결과 파싱
        try:
            # JSON 부분 추출
            response_text = result.messages[-1].content
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            
            data = json.loads(json_str)
            return Analyst(**data)
        except Exception as e:
            print(f"추가 분석가 파싱 오류: {e}")
            # 기본값 반환
            return Analyst(
                name="피드백 전문가",
                role="피드백 분석 전문가",
                affiliation="연구 기관",
                description=f"피드백 '{feedback}'을 반영한 전문적 분석을 담당"
            )
    
    async def _run_research_with_additional_analyst(self, task: ResearchTask, additional_analyst: Analyst) -> ResearchResult:
        """추가 분석가를 포함하여 기존 워크플로우를 재실행합니다"""
        
        # Langfuse 추적 시작
        task_id = str(uuid.uuid4())
        
        with self.tracing_manager.trace_research(topic=task.topic, task_id=task_id) as trace:
            try:
                print(f"🔄 추가 분석가와 함께 연구 재실행: {task.topic}")
                if trace:
                    trace_url = self.tracing_manager.get_trace_url()
                    if trace_url:
                        print(f"🔍 Langfuse 추적 시작 - Trace URL: {trace_url}")
                
                # 기존 분석가들과 추가 분석가 함께 사용
                # interactive 모드에서 current_analysts가 존재할 경우
                if hasattr(self, 'current_analysts') and self.current_analysts:
                    analysts = self.current_analysts + [additional_analyst]
                else:
                    # 기본 모드이거나 current_analysts가 없을 경우
                    analysts = [additional_analyst]
                
                # 추가 분석가 생성 이벤트 로깅
                self.tracing_manager.log_event(
                    "additional_analyst_created",
                    {
                        "analyst_name": additional_analyst.name,
                        "analyst_role": additional_analyst.role
                    }
                )
                
                # 인터뷰 진행
                print("🎤 추가 분석가와 인터뷰 진행 중...")
                interviews = await self._conduct_interviews(analysts, task)
                print(f"✅ {len(interviews)}개의 인터뷰 완료")
                
                # 인터뷰 완료 이벤트 로깅
                self.tracing_manager.log_event(
                    "additional_interviews_completed",
                    {"count": len(interviews)}
                )
                
                # 보고서 작성
                print("📝 추가 인터뷰를 반영한 보고서 작성 중...")
                report_parts = await self._write_report(task.topic, interviews)
                print("✅ 보고서 작성 완료")
                
                # 최종 결과 조합
                final_report = self._assemble_final_report(report_parts)
                
                # 보고서 생성 로깅
                self.tracing_manager.log_generation(
                    "additional_final_report",
                    input_data={"topic": task.topic, "additional_analyst": additional_analyst.name},
                    output_data={"length": len(final_report), "word_count": len(final_report.split())}
                )
                
                result = ResearchResult(
                    topic=task.topic,
                    analysts=analysts,
                    interviews=interviews,
                    introduction=report_parts["introduction"],
                    main_content=report_parts["main_content"],
                    conclusion=report_parts["conclusion"],
                    final_report=final_report
                )
                
                # 성공 이벤트 로깅
                self.tracing_manager.log_event(
                    "additional_research_completed",
                    {
                        "additional_analyst": additional_analyst.name,
                        "interview_count": len(interviews),
                        "report_length": len(final_report),
                        "word_count": len(final_report.split())
                    }
                )
                
                return result
            
            except Exception as e:
                print(f"❌ 추가 연구 중 오류 발생: {e}")
                
                # 에러 이벤트 로깅
                self.tracing_manager.log_event(
                    "additional_research_error",
                    {"error": str(e), "error_type": type(e).__name__},
                    level="ERROR"
                )
                
                raise
    
    async def _conduct_interviews(self, analysts: List[Analyst], task: ResearchTask) -> List[InterviewResult]:
        """분석가들과 전문가 간의 인터뷰를 진행합니다"""
        
        interviews = []
        
        if task.parallel_interviews:
            # 병렬 인터뷰
            interview_tasks = [
                self._conduct_single_interview(analyst, task.max_interview_turns)
                for analyst in analysts
            ]
            interview_results = await asyncio.gather(*interview_tasks)
            interviews.extend(interview_results)
        else:
            # 순차 인터뷰
            for analyst in analysts:
                interview_result = await self._conduct_single_interview(analyst, task.max_interview_turns)
                interviews.append(interview_result)
        
        return interviews
    
    async def _conduct_feedback_aware_interviews(self, analysts: List[Analyst], task: ResearchTask, feedback: str) -> List[InterviewResult]:
        """피드백 컨텍스트가 강화된 인터뷰를 진행합니다"""
        
        interviews = []
        
        if task.parallel_interviews:
            # 병렬 인터뷰 (피드백 컨텍스트 포함)
            interview_tasks = [
                self._conduct_single_feedback_aware_interview(analyst, task.max_interview_turns, feedback)
                for analyst in analysts
            ]
            interview_results = await asyncio.gather(*interview_tasks)
            interviews.extend(interview_results)
        else:
            # 순차 인터뷰 (피드백 컨텍스트 포함)
            for analyst in analysts:
                interview_result = await self._conduct_single_feedback_aware_interview(analyst, task.max_interview_turns, feedback)
                interviews.append(interview_result)
        
        return interviews
    
    async def _conduct_single_feedback_aware_interview(self, analyst: Analyst, max_turns: int, feedback: str) -> InterviewResult:
        """피드백 컨텍스트가 포함된 단일 인터뷰를 진행합니다"""
        
        # 피드백 컨텍스트가 강화된 인터뷰어 생성
        interviewer = create_feedback_aware_interviewer(analyst, feedback, self.interviewer_model_client)
        expert = create_expert_agent(self.expert_model_client)
        section_writer = create_section_writer_agent(analyst, self.writer_model_client)
        
        # 피드백 중심 인터뷰 진행
        termination = TextMentionTermination("정말 도움이 되었습니다. 감사합니다!") | MaxMessageTermination(max_messages=max_turns * 2 + 2)
        
        interview_team = RoundRobinGroupChat(
            [interviewer, expert],
            termination_condition=termination
        )
        
        # 피드백이 강조된 인터뷰 프롬프트
        interview_prompt = f"""
        {analyst.persona}의 관점에서 전문가와 인터뷰를 진행해주세요.
        
        **중요 - 사용자 피드백 반영**: 다음 사용자 피드백을 반드시 고려하여 질문하세요:
        "{feedback}"
        
        이 피드백이 요구하는 관점, 정보, 그리고 분석 방향을 중심으로 인터뷰를 진행해주세요.
        피드백에서 언급된 특정 영역이나 관점에 대해 깊이 있게 탐구하세요.
        """
        
        interview_result = await interview_team.run(task=interview_prompt)
        
        # 인터뷰 내용 추출 (content가 리스트일 수 있으므로 안전하게 처리)
        interview_content = "\n".join([
            msg.content if isinstance(msg.content, str) else str(msg.content) 
            for msg in interview_result.messages
        ])
        
        # 피드백 중심 인터뷰 이벤트 로깅
        self.tracing_manager.log_event(
            "feedback_aware_interview_completed",
            {
                "interviewer": analyst.name,
                "analyst_role": analyst.role,
                "feedback": feedback[:100] + "..." if len(feedback) > 100 else feedback,
                "message_count": len(interview_result.messages),
                "content_length": len(interview_content)
            }
        )
        
        # 피드백이 반영된 섹션 작성
        section_team = RoundRobinGroupChat(
            [section_writer],
            termination_condition=MaxMessageTermination(max_messages=2)
        )
        
        section_prompt = f"""
        다음 인터뷰 내용을 바탕으로 보고서 섹션을 작성해주세요:
        
        **사용자 피드백**: {feedback}
        **중요**: 위 피드백을 섹션 작성에 적극 반영하여, 사용자가 원하는 관점과 정보를 중심으로 구성해주세요.
        
        **인터뷰 내용**:
        {interview_content}
        """
        
        section_result = await section_team.run(task=section_prompt)
        section_content = section_result.messages[-1].content
        
        return InterviewResult(
            analyst=analyst,
            interview_content=interview_content,
            section_content=section_content
        )
    
    async def _conduct_single_interview(self, analyst: Analyst, max_turns: int) -> InterviewResult:
        """단일 인터뷰를 진행합니다"""
        
        interviewer = create_interviewer_agent(analyst, self.interviewer_model_client)
        expert = create_expert_agent(self.expert_model_client)
        section_writer = create_section_writer_agent(analyst, self.writer_model_client)
        
        # 인터뷰 진행
        termination = TextMentionTermination("정말 도움이 되었습니다. 감사합니다!") | MaxMessageTermination(max_messages=max_turns * 2 + 2)
        
        interview_team = RoundRobinGroupChat(
            [interviewer, expert],
            termination_condition=termination
        )
        
        interview_result = await interview_team.run(
            task=f"{analyst.persona}의 관점에서 전문가와 인터뷰를 진행해주세요."
        )
        
        # 인터뷰 내용 추출 (content가 리스트일 수 있으므로 안전하게 처리)
        interview_content = "\n".join([
            msg.content if isinstance(msg.content, str) else str(msg.content) 
            for msg in interview_result.messages
        ])
        
        # 인터뷰 이벤트 로깅
        self.tracing_manager.log_event(
            "interview_completed",
            {
                "interviewer": analyst.name,
                "analyst_role": analyst.role,
                "message_count": len(interview_result.messages),
                "content_length": len(interview_content)
            }
        )
        
        # 섹션 작성
        section_team = RoundRobinGroupChat(
            [section_writer],
            termination_condition=MaxMessageTermination(max_messages=2)
        )
        
        section_result = await section_team.run(
            task=f"다음 인터뷰 내용을 바탕으로 보고서 섹션을 작성해주세요:\n\n{interview_content}"
        )
        
        section_content = section_result.messages[-1].content
        
        return InterviewResult(
            analyst=analyst,
            interview_content=interview_content,
            section_content=section_content
        )
    
    async def _write_report(self, topic: str, interviews: List[InterviewResult]) -> Dict[str, str]:
        """최종 보고서를 작성합니다"""
        
        # 모든 섹션 내용 수집
        all_sections = "\n\n---\n\n".join([
            interview.section_content for interview in interviews
        ])
        
        # 보고서 작성자들 생성 (고성능 모델 사용)
        report_writer = create_report_writer_agent(self.writer_model_client)
        intro_writer = create_intro_writer_agent(self.writer_model_client)
        conclusion_writer = create_conclusion_writer_agent(self.writer_model_client)
        
        # 병렬로 각 부분 작성
        tasks = [
            self._write_main_content(report_writer, topic, all_sections),
            self._write_introduction(intro_writer, all_sections),
            self._write_conclusion(conclusion_writer, all_sections)
        ]
        
        main_content, introduction, conclusion = await asyncio.gather(*tasks)
        
        return {
            "main_content": main_content,
            "introduction": introduction,
            "conclusion": conclusion
        }
    
    async def _write_feedback_aware_report(self, topic: str, interviews: List[InterviewResult], feedback: str) -> Dict[str, str]:
        """피드백 컨텍스트가 강화된 보고서를 작성합니다"""
        
        # 모든 섹션 내용 수집
        all_sections = "\n\n---\n\n".join([
            interview.section_content for interview in interviews
        ])
        
        # 피드백 컨텍스트가 강화된 보고서 작성자들 생성
        report_writer = create_feedback_aware_report_writer(feedback, self.writer_model_client)
        intro_writer = create_feedback_aware_intro_writer(feedback, self.writer_model_client)
        conclusion_writer = create_feedback_aware_conclusion_writer(feedback, self.writer_model_client)
        
        # 병렬로 각 부분 작성 (피드백 컨텍스트 포함)
        tasks = [
            self._write_main_content(report_writer, topic, all_sections),
            self._write_introduction(intro_writer, all_sections),
            self._write_conclusion(conclusion_writer, all_sections)
        ]
        
        main_content, introduction, conclusion = await asyncio.gather(*tasks)
        
        return {
            "main_content": main_content,
            "introduction": introduction,
            "conclusion": conclusion
        }
    
    async def _write_main_content(self, writer_agent, topic: str, sections: str) -> str:
        """메인 콘텐츠를 작성합니다"""
        
        team = RoundRobinGroupChat(
            [writer_agent],
            termination_condition=MaxMessageTermination(max_messages=2)
        )
        
        result = await team.run(
            task=f"주제 '{topic}'에 대한 다음 인터뷰 섹션들을 종합하여 독창적이고 포괄적인 연구 보고서를 작성해주세요. 각 섹션의 내용을 단순 나열하지 말고 새로운 관점으로 종합하여 완전히 새로운 보고서를 작성하세요:\n\n{sections}"
        )
        
        return result.messages[-1].content
    
    async def _write_introduction(self, intro_agent, sections: str) -> str:
        """서론을 작성합니다"""
        
        team = RoundRobinGroupChat(
            [intro_agent],
            termination_condition=MaxMessageTermination(max_messages=2)
        )
        
        result = await team.run(
            task=f"다음 인터뷰 섹션들을 바탕으로 독창적이고 매력적인 서론을 작성해주세요. 섹션 내용을 단순 요약하지 말고 독자의 관심을 끌 수 있는 새로운 관점의 서론을 작성하세요:\n\n{sections}"
        )
        
        return result.messages[-1].content
    
    async def _write_conclusion(self, conclusion_agent, sections: str) -> str:
        """결론을 작성합니다"""
        
        team = RoundRobinGroupChat(
            [conclusion_agent],
            termination_condition=MaxMessageTermination(max_messages=2)
        )
        
        result = await team.run(
            task=f"다음 인터뷰 섹션들을 바탕으로 독창적이고 강력한 결론을 작성해주세요. 섹션 내용을 단순 요약하지 말고 새로운 인사이트와 미래 전망을 제시하는 독창적인 결론을 작성하세요:\n\n{sections}"
        )
        
        return result.messages[-1].content
    
    def _assemble_final_report(self, parts: Dict[str, str]) -> str:
        """최종 보고서를 조합합니다"""
        
        main_content = parts["main_content"]
        
        # 메인 콘텐츠가 이미 완전한 보고서인지 확인
        if (("# " in main_content or "## 서론" in main_content) and 
            ("결론" in main_content.lower() or "## 결론" in main_content)):
            # 이미 완전한 보고서이므로 그대로 반환
            return main_content.strip()
        
        # 메인 콘텐츠에서 "## Insights" 제목 제거
        if main_content.startswith("## Insights"):
            main_content = main_content.replace("## Insights", "", 1).strip()
        
        # 참고문헌/소스 섹션 분리
        references = None
        sources = None
        
        # "## 참고문헌" 또는 "## References" 찾기
        if "## 참고문헌" in main_content:
            try:
                main_content, references = main_content.split("\n## 참고문헌\n", 1)
            except:
                references = None
        elif "## References" in main_content:
            try:
                main_content, references = main_content.split("\n## References\n", 1)
            except:
                references = None
        
        # "## Sources" 찾기
        if "## Sources" in main_content:
            try:
                main_content, sources = main_content.split("\n## Sources\n", 1)
            except:
                sources = None
        
        # 개별 섹션들을 조합하여 완전한 보고서 생성
        final_report = (
            parts["introduction"] + 
            "\n\n---\n\n## 주요 내용\n\n" + 
            main_content + 
            "\n\n---\n\n" + 
            parts["conclusion"]
        )
        
        # 참고문헌 섹션 추가
        if references:
            final_report += "\n\n## 참고문헌\n" + references
        elif sources:
            final_report += "\n\n## Sources\n" + sources
        
        return final_report
    
    async def close(self):
        """리소스 정리"""
        await self.model_client.close()
        
        # Langfuse 리소스 정리
        if self.tracing_manager.enabled:
            self.tracing_manager.close()


def create_storm_workflow(config: StormConfig, interactive_mode: bool = False) -> StormWorkflow:
    """STORM 워크플로우를 생성합니다
    
    Args:
        config: STORM 설정
        interactive_mode: 인터랙티브 모드 활성화 여부
        
    Returns:
        StormWorkflow 인스턴스
    """
    return StormWorkflow(config, interactive_mode)
