"""AutoGen STORM Research Assistant 메인 실행 파일

이 파일은 AutoGen 기반의 STORM Research Assistant를 실행합니다.
"""

import asyncio
import os
import argparse
from dotenv import load_dotenv
from autogen_storm import create_storm_workflow, initialize_tracing, get_tracing_manager
from autogen_storm.config import StormConfig, ModelConfig, ModelProvider
from autogen_storm.models import ResearchTask

# .env 파일 로드
load_dotenv()


async def main():
    """메인 실행 함수"""
    
    # 명령행 인수 파싱
    parser = argparse.ArgumentParser(description="STORM Research Assistant")
    parser.add_argument("--topic", type=str, help="연구 주제")
    parser.add_argument("--interactive", action="store_true", help="인터랙티브 모드 (휴먼 피드백 포함)")
    parser.add_argument("--auto", action="store_true", help="완전 자동 모드 (휴먼 피드백 없음)")
    parser.add_argument("--max-analysts", type=int, default=3, help="최대 분석가 수")
    parser.add_argument("--max-interview-turns", type=int, default=3, help="최대 인터뷰 턴 수")
    parser.add_argument("--parallel", action="store_true", help="병렬 인터뷰 활성화")
    
    args = parser.parse_args()
    
    print("🌟 AutoGen STORM Research Assistant")
    print("=" * 50)
    
    # Langfuse 추적 초기화
    print("\n🔍 Langfuse 추적 초기화 중...")
    tracing_enabled = initialize_tracing()
    if tracing_enabled:
        print("✅ Langfuse 추적이 활성화되었습니다!")
    else:
        print("⚠️  Langfuse 추적이 비활성화되었습니다. (API 키 확인 필요)")
    
    # 모델 제공자 선택
    if args.auto:
        # 자동 모드에서는 Azure OpenAI를 기본으로 사용
        choice = "2"
        print("\n🤖 자동 모드: Azure OpenAI 모델 사용")
    else:
        print("\n🤖 사용할 모델 제공자를 선택하세요:")
        print("1. OpenAI")
        print("2. Azure OpenAI")
        print("3. Anthropic")
        
        try:
            choice = input("선택 (1-3, 기본값: 1): ").strip() or "1"
        except UnicodeDecodeError:
            print("입력 인코딩 오류. 숫자만 입력해주세요.")
            choice = input("Choice (1-3, default: 1): ").strip() or "1"
    
    # 모델 설정 생성
    if choice == "1":
        # OpenAI 설정
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
            print("   export OPENAI_API_KEY='your-api-key'")
            return
        
        model_config = ModelConfig.from_env(ModelProvider.OPENAI)
        print(f"✅ OpenAI 모델 사용: {model_config.model}")
        
    elif choice == "2":
        # Azure OpenAI 설정
        required_vars = ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"⚠️  다음 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
            print("   Azure OpenAI 사용을 위해 다음 환경변수를 설정해주세요:")
            print("   export AZURE_OPENAI_ENDPOINT='https://your-endpoint.openai.azure.com/'")
            print("   export AZURE_OPENAI_DEPLOYMENT='your-deployment-name'")
            print("   export AZURE_OPENAI_API_KEY='your-api-key'  # 또는 Azure AD 사용")
            return
        
        model_config = ModelConfig.from_env(ModelProvider.AZURE_OPENAI)
        print(f"✅ Azure OpenAI 모델 사용: {model_config.model} (배포: {model_config.azure_deployment})")
        
    elif choice == "3":
        # Anthropic 설정
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("⚠️  ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
            print("   export ANTHROPIC_API_KEY='your-api-key'")
            return
        
        model_config = ModelConfig.from_env(ModelProvider.ANTHROPIC)
        print(f"✅ Anthropic 모델 사용: {model_config.model}")
        
    else:
        print("❌ 잘못된 선택입니다. 기본값(OpenAI)을 사용합니다.")
        model_config = ModelConfig.from_env(ModelProvider.OPENAI)
    
    # STORM 설정 생성
    config = StormConfig(
        model_config=model_config,
        max_analysts=args.max_analysts,
        max_interview_turns=args.max_interview_turns,
        parallel_interviews=args.parallel,
        tavily_api_key=os.getenv("TAVILY_API_KEY")
    )
    
    # 연구 주제 입력
    if args.topic:
        topic = args.topic
    else:
        try:
            topic = input("\n🔍 연구하고 싶은 주제를 입력하세요: ").strip()
        except UnicodeDecodeError:
            print("입력 인코딩 오류. 영문으로 입력해주세요.")
            topic = input("Enter research topic: ").strip()
        if not topic:
            topic = "인공지능의 미래와 사회적 영향"
            print(f"기본 주제 사용: {topic}")
    
    # 워크플로우 모드 결정
    if args.interactive:
        workflow = create_storm_workflow(config, interactive_mode=True)
        mode_name = "인터랙티브"
    elif args.auto:
        workflow = create_storm_workflow(config, interactive_mode=False)
        mode_name = "완전 자동"
    else:
        # 기본값: 사용자에게 선택하게 함
        print("\n" + "="*60)
        print("🎯 실행 모드를 선택해주세요:")
        print("="*60)
        print("1. 🤝 인터랙티브 모드 (간단한 2단계 피드백)")
        print("   - 분석가 수 선택")
        print("   - 최종 보고서 승인")
        print("   - 사용자가 직접 제어 가능")
        print("\n2. 🚀 완전 자동 모드 (사용자 개입 없이 자동 실행)")
        print("   - 모든 과정이 자동으로 진행")
        print("   - 빠른 결과 생성")
        
        while True:
            try:
                mode_choice = input("\n선택 (1 또는 2): ").strip()
            except UnicodeDecodeError:
                print("입력 인코딩 오류. 숫자만 입력해주세요.")
                mode_choice = input("Choice (1 or 2): ").strip()
            if mode_choice == "1":
                workflow = create_storm_workflow(config, interactive_mode=True)
                mode_name = "인터랙티브"
                break
            elif mode_choice == "2":
                workflow = create_storm_workflow(config, interactive_mode=False)
                mode_name = "완전 자동"
                break
            else:
                print("올바른 번호를 입력해주세요 (1 또는 2)")
    
    # 연구 작업 생성
    task = ResearchTask(
        topic=topic,
        max_analysts=config.max_analysts,
        max_interview_turns=config.max_interview_turns,
        parallel_interviews=config.parallel_interviews
    )
    
    tracing_manager = get_tracing_manager()
    
    try:
        print(f"\n🚀 연구 시작...")
        print(f"🎯 실행 모드: {mode_name}")
        print(f"📊 설정: 분석가 {task.max_analysts}명, 인터뷰 턴 {task.max_interview_turns}회")
        print(f"⚡ 병렬 처리: {'활성화' if task.parallel_interviews else '비활성화'}")
        print("-" * 60)
        
        result = await workflow.run_research(task)
        
        print("\n" + "=" * 50)
        print("📊 연구 완료!")
        print("=" * 50)
        
        # 결과 출력
        print(f"\n📋 주제: {result.topic}")
        print(f"👥 분석가 수: {len(result.analysts)}")
        print(f"🎤 인터뷰 수: {len(result.interviews)}")
        
        print("\n👥 생성된 분석가들:")
        for i, analyst in enumerate(result.analysts, 1):
            print(f"  {i}. {analyst.name} ({analyst.role}) - {analyst.affiliation}")
        
        # 최종 보고서 저장
        output_file = f"research_report_{topic.replace(' ', '_')[:30]}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.final_report)
        
        print(f"\n📄 최종 보고서가 '{output_file}'에 저장되었습니다.")
        
        # Langfuse 추적 정보 출력
        if tracing_enabled and tracing_manager.enabled:
            print(f"\n🔍 Langfuse에서 연구 과정을 확인할 수 있습니다:")
            print(f"   추적 대시보드: {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')}")
        
        # 보고서 미리보기
        print("\n📖 보고서 미리보기:")
        print("-" * 30)
        preview = result.final_report[:500] + "..." if len(result.final_report) > 500 else result.final_report
        print(preview)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 리소스 정리
        await workflow.close()
        if tracing_manager.enabled:
            tracing_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
