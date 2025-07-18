#!/usr/bin/env python3
"""
간단한 import 테스트 스크립트
"""

try:
    print("Testing basic imports...")
    
    # 기본 autogen 모듈 테스트
    from autogen_agentchat.teams import RoundRobinGroupChat
    print("✅ autogen_agentchat.teams imported successfully")
    
    from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
    print("✅ autogen_agentchat.conditions imported successfully")
    
    from autogen_agentchat.agents import AssistantAgent
    print("✅ autogen_agentchat.agents imported successfully")
    
    from autogen_core.models import ChatCompletionClient
    print("✅ autogen_core.models imported successfully")
    
    # 우리 모듈 테스트
    from autogen_storm.config import StormConfig, ModelConfig, ModelProvider
    print("✅ autogen_storm.config imported successfully")
    
    from autogen_storm.models import Analyst, ResearchTask, ResearchResult, InterviewResult
    print("✅ autogen_storm.models imported successfully")
    
    from autogen_storm.tracing import get_tracing_manager, initialize_tracing
    print("✅ autogen_storm.tracing imported successfully")
    
    print("\n🎉 All imports successful!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()