#!/usr/bin/env python3
"""
STORM 시스템 설정 및 테스트 스크립트
API 키 확인, 의존성 검사, 간단한 테스트 실행
"""

import os
import sys
import asyncio
import json
from typing import Dict, List, Tuple
import importlib

def check_python_version() -> bool:
    """Python 버전 확인"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (3.8+ 필요)")
        return False

def check_dependencies() -> Dict[str, bool]:
    """필수 패키지 설치 확인"""
    required_packages = [
        ("autogen_agentchat", "AutoGen AgentChat"),
        ("autogen_ext", "AutoGen Extensions"),
        ("pydantic", "Pydantic"),
        ("dotenv", "Python-dotenv"),
        ("tavily", "Tavily (선택사항)"),
        ("duckduckgo_search", "DuckDuckGo Search"),
        ("rich", "Rich (선택사항)")
    ]
    
    results = {}
    print("\n📦 패키지 의존성 확인:")
    
    for package, display_name in required_packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {display_name}")
            results[package] = True
        except ImportError:
            print(f"   ❌ {display_name}")
            results[package] = False
    
    return results

def check_environment_variables() -> Dict[str, bool]:
    """환경 변수 확인"""
    required_vars = [
        ("AZURE_OPENAI_API_KEY", "Azure OpenAI API 키", True),
        ("AZURE_OPENAI_ENDPOINT", "Azure OpenAI 엔드포인트", True),
        ("AZURE_OPENAI_API_VERSION", "Azure OpenAI API 버전", False),
        ("AZURE_OPENAI_MODEL", "Azure OpenAI 모델", False),
        ("TAVILY_API_KEY", "Tavily API 키", False)
    ]
    
    results = {}
    print("\n🔑 환경 변수 확인:")
    
    for var_name, display_name, required in required_vars:
        value = os.getenv(var_name)
        if value:
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"   ✅ {display_name}: {masked_value}")
            results[var_name] = True
        else:
            status = "❌" if required else "⚠️ "
            print(f"   {status} {display_name}: 설정되지 않음")
            results[var_name] = False
    
    return results

def load_env_file() -> bool:
    """환경 파일 로드"""
    try:
        from dotenv import load_dotenv
        if os.path.exists('.env'):
            load_dotenv()
            print("✅ .env 파일 로드됨")
            return True
        elif os.path.exists('.env.example'):
            print("⚠️  .env.example 파일이 있습니다. .env로 복사하고 설정하세요:")
            print("   cp .env.example .env")
            return False
        else:
            print("❌ .env 파일이 없습니다. .env.example을 참조하여 생성하세요.")
            return False
    except ImportError:
        print("❌ python-dotenv 패키지가 필요합니다: pip install python-dotenv")
        return False

async def test_basic_functionality() -> bool:
    """기본 기능 테스트"""
    print("\n🧪 기본 기능 테스트:")
    
    try:
        # AutoGen 모델 클라이언트 테스트
        from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
        
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        
        if not api_key or not endpoint:
            print("   ❌ Azure OpenAI 설정이 없어 테스트를 건너뜁니다.")
            return False
        
        client = AzureOpenAIChatCompletionClient(
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-4o"),
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        )
        
        print("   ✅ Azure OpenAI 클라이언트 생성 성공")
        
        # 클라이언트 정리
        await client.close()
        print("   ✅ 클라이언트 연결 테스트 완료")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 기본 기능 테스트 실패: {e}")
        return False

def generate_sample_config():
    """샘플 설정 파일 생성"""
    print("\n⚙️  샘플 설정 파일들을 생성합니다...")
    
    # .env 파일이 없으면 .env.example에서 복사
    if not os.path.exists('.env') and os.path.exists('.env.example'):
        with open('.env.example', 'r') as src, open('.env', 'w') as dst:
            dst.write(src.read())
        print("   ✅ .env 파일 생성됨 (.env.example에서 복사)")
        print("   ⚠️  .env 파일을 편집하여 실제 API 키를 입력하세요!")
    
    # 샘플 주제 파일 생성
    sample_topics = [
        "인공지능의 의료 진단 분야 활용과 한계",
        "블록체인 기술의 탈중앙화 금융(DeFi) 혁신",
        "양자 컴퓨팅이 현재 암호화 기술에 미치는 위협과 대응",
        "메타버스 플랫폼의 기술적 아키텍처와 사회문화적 영향",
        "지속가능한 AI: 환경 영향을 고려한 AI 모델 개발"
    ]
    
    with open('sample_topics.json', 'w', encoding='utf-8') as f:
        json.dump({
            "description": "STORM 연구를 위한 샘플 주제들",
            "topics": sample_topics
        }, f, ensure_ascii=False, indent=2)
    
    print("   ✅ sample_topics.json 파일 생성됨")

def print_quick_start_guide():
    """빠른 시작 가이드 출력"""
    print("\n🚀 빠른 시작 가이드:")
    print("\n1. 환경 설정:")
    print("   • .env 파일을 편집하여 Azure OpenAI API 키를 입력하세요")
    print("   • (선택사항) Tavily API 키를 추가하면 더 나은 검색 결과를 얻을 수 있습니다")
    
    print("\n2. 실행 방법:")
    print("   • 기본 실행: python storm_research.py")
    print("   • 간단 실행: python simple_run.py \"주제명\"")
    print("   • 자동 실행: python simple_run.py \"주제명\" --auto")
    print("   • 배치 실행: python batch_run.py")
    
    print("\n3. 예시 명령어:")
    print("   python simple_run.py \"인공지능의 의료 분야 활용\"")
    print("   python simple_run.py \"블록체인 기술\" --auto")

def install_missing_packages(missing_packages: List[str]):
    """누락된 패키지 설치 안내"""
    if not missing_packages:
        return
    
    print(f"\n📦 누락된 패키지 설치 안내:")
    print(f"   다음 명령어로 설치하세요:")
    print(f"   pip install {' '.join(missing_packages)}")
    
    # requirements.txt가 있으면 그것으로 설치 안내
    if os.path.exists('requirements.txt'):
        print(f"\n   또는 requirements.txt로 일괄 설치:")
        print(f"   pip install -r requirements.txt")

async def main():
    """메인 함수"""
    print("🌩️ STORM 시스템 설정 및 테스트")
    print("=" * 50)
    
    # 1. Python 버전 확인
    if not check_python_version():
        sys.exit(1)
    
    # 2. 환경 파일 로드
    load_env_file()
    
    # 3. 패키지 의존성 확인
    dep_results = check_dependencies()
    missing_packages = [pkg for pkg, installed in dep_results.items() if not installed]
    
    if missing_packages:
        install_missing_packages(missing_packages)
        print("\n⚠️  누락된 패키지를 설치한 후 다시 실행하세요.")
        return
    
    # 4. 환경 변수 확인
    env_results = check_environment_variables()
    
    # 5. 기본 기능 테스트
    if env_results.get("AZURE_OPENAI_API_KEY", False):
        test_success = await test_basic_functionality()
        if test_success:
            print("\n🎉 모든 테스트 통과! STORM 시스템이 준비되었습니다.")
        else:
            print("\n⚠️  기본 기능 테스트에 실패했습니다. API 키와 설정을 확인하세요.")
    else:
        print("\n⚠️  Azure OpenAI API 키가 설정되지 않아 기능 테스트를 건너뜁니다.")
    
    # 6. 설정 파일 생성 제안
    if not os.path.exists('.env'):
        generate_sample_config()
    
    # 7. 빠른 시작 가이드
    print_quick_start_guide()
    
    # 8. 최종 상태 요약
    print(f"\n📊 시스템 상태 요약:")
    print(f"   • Python: {'✅' if check_python_version() else '❌'}")
    print(f"   • 필수 패키지: {'✅' if not missing_packages else '❌'}")
    print(f"   • Azure OpenAI: {'✅' if env_results.get('AZURE_OPENAI_API_KEY') else '❌'}")
    print(f"   • Tavily API: {'✅' if env_results.get('TAVILY_API_KEY') else '⚠️'}")

if __name__ == "__main__":
    asyncio.run(main())
