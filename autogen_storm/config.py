"""AutoGen STORM Research Assistant Configuration

이 모듈은 연구 어시스턴트 시스템의 런타임 설정을 관리합니다.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Union
from enum import Enum
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


class ModelProvider(Enum):
    """지원되는 모델 제공자"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"


@dataclass
class ModelConfig:
    """모델 설정을 위한 클래스"""
    
    provider: ModelProvider = field(
        default=ModelProvider.OPENAI,
        metadata={"description": "모델 제공자"}
    )
    
    model: str = field(
        default="gpt-4o-mini",
        metadata={"description": "사용할 모델 이름"}
    )
    
    # OpenAI 설정
    api_key: Optional[str] = field(
        default=None,
        metadata={"description": "OpenAI API 키"}
    )
    
    base_url: Optional[str] = field(
        default=None,
        metadata={"description": "OpenAI 호환 API의 베이스 URL"}
    )
    
    # Azure OpenAI 설정
    azure_endpoint: Optional[str] = field(
        default=None,
        metadata={"description": "Azure OpenAI 엔드포인트"}
    )
    
    azure_deployment: Optional[str] = field(
        default=None,
        metadata={"description": "Azure OpenAI 배포 이름"}
    )
    
    api_version: Optional[str] = field(
        default="2024-06-01",
        metadata={"description": "Azure OpenAI API 버전"}
    )
    
    # Azure AD 인증 설정
    use_azure_ad: bool = field(
        default=False,
        metadata={"description": "Azure AD 토큰 인증 사용 여부"}
    )
    
    # 추가 설정
    temperature: float = field(
        default=0.0,
        metadata={"description": "모델 온도 설정"}
    )
    
    max_tokens: Optional[int] = field(
        default=None,
        metadata={"description": "최대 토큰 수"}
    )

    def to_autogen_config(self) -> Dict[str, Any]:
        """AutoGen 모델 클라이언트 설정으로 변환"""
        if self.provider == ModelProvider.OPENAI:
            config = {
                "provider": "autogen_ext.models.openai.OpenAIChatCompletionClient",
                "config": {
                    "model": self.model,
                    "temperature": self.temperature,
                }
            }
            
            if self.api_key:
                config["config"]["api_key"] = self.api_key
            if self.base_url:
                config["config"]["base_url"] = self.base_url
            if self.max_tokens:
                config["config"]["max_tokens"] = self.max_tokens
                
        elif self.provider == ModelProvider.AZURE_OPENAI:
            config = {
                "provider": "autogen_ext.models.openai.AzureOpenAIChatCompletionClient",
                "config": {
                    "model": self.model,
                    "temperature": self.temperature,
                    "api_version": self.api_version,
                }
            }
            
            if self.azure_endpoint:
                config["config"]["azure_endpoint"] = self.azure_endpoint
            if self.azure_deployment:
                config["config"]["azure_deployment"] = self.azure_deployment
            if self.api_key and not self.use_azure_ad:
                config["config"]["api_key"] = self.api_key
            if self.max_tokens:
                config["config"]["max_tokens"] = self.max_tokens
                
        elif self.provider == ModelProvider.ANTHROPIC:
            config = {
                "provider": "autogen_ext.models.anthropic.AnthropicChatCompletionClient",
                "config": {
                    "model": self.model,
                    "temperature": self.temperature,
                }
            }
            
            if self.api_key:
                config["config"]["api_key"] = self.api_key
            if self.max_tokens:
                config["config"]["max_tokens"] = self.max_tokens
        else:
            # 기본 fallback - Azure OpenAI로 설정
            config = {
                "provider": "autogen_ext.models.openai.AzureOpenAIChatCompletionClient",
                "config": {
                    "model": self.model,
                    "temperature": self.temperature,
                    "api_version": self.api_version or "2024-06-01",
                }
            }
            if self.azure_endpoint:
                config["config"]["azure_endpoint"] = self.azure_endpoint
            if self.azure_deployment:
                config["config"]["azure_deployment"] = self.azure_deployment
            if self.api_key and not self.use_azure_ad:
                config["config"]["api_key"] = self.api_key
            if self.max_tokens:
                config["config"]["max_tokens"] = self.max_tokens
        
        return config

    @classmethod
    def from_env(cls, provider: ModelProvider = ModelProvider.OPENAI) -> "ModelConfig":
        """환경 변수에서 모델 설정 생성"""
        if provider == ModelProvider.OPENAI:
            return cls(
                provider=provider,
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )
        elif provider == ModelProvider.AZURE_OPENAI:
            return cls(
                provider=provider,
                model=os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1-nano"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1-nano")),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
                use_azure_ad=os.getenv("AZURE_USE_AD", "false").lower() == "true",
            )
        elif provider == ModelProvider.ANTHROPIC:
            return cls(
                provider=provider,
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
        
        return cls()


@dataclass
class StormConfig:
    """STORM Research Assistant 설정 클래스
    
    연구 과정에서 사용할 수 있는 설정 옵션들을 정의합니다.
    """

    # 기본 모델 설정
    model_config: ModelConfig = field(
        default_factory=lambda: ModelConfig.from_env(ModelProvider.AZURE_OPENAI),
        metadata={"description": "기본 모델 클라이언트 설정"}
    )
    
    # 에이전트별 모델 설정 (선택사항)
    expert_model_config: Optional[ModelConfig] = field(
        default=None,
        metadata={"description": "전문가 에이전트용 고성능 모델 설정 (검색 도구 사용)"}
    )
    
    writer_model_config: Optional[ModelConfig] = field(
        default=None,
        metadata={"description": "작성 에이전트용 고성능 모델 설정 (보고서, 섹션 작성)"}
    )
    
    analyst_model_config: Optional[ModelConfig] = field(
        default=None,
        metadata={"description": "분석가 생성 에이전트용 모델 설정"}
    )
    
    interviewer_model_config: Optional[ModelConfig] = field(
        default=None,
        metadata={"description": "인터뷰어 에이전트용 모델 설정"}
    )

    # 연구 설정
    max_analysts: int = field(
        default=5,
        metadata={
            "description": "생성할 분석가의 최대 수",
            "range": [1, 10],
        },
    )

    max_interview_turns: int = field(
        default=5,
        metadata={
            "description": "인터뷰당 최대 대화 턴 수",
            "range": [1, 10],
        },
    )

    # 검색 설정
    tavily_max_results: int = field(
        default=3,
        metadata={
            "description": "Tavily 검색 결과의 최대 수",
            "range": [1, 10],
        },
    )

    arxiv_max_docs: int = field(
        default=3,
        metadata={
            "description": "ArXiv 검색 문서의 최대 수",
            "range": [1, 10],
        },
    )

    # 병렬 처리 설정
    parallel_interviews: bool = field(
        default=True, 
        metadata={"description": "인터뷰를 병렬로 실행할지 여부"}
    )

    # API 키 설정 (하위 호환성을 위해 유지)
    openai_api_key: Optional[str] = field(
        default=None,
        metadata={"description": "OpenAI API 키 (deprecated: model_config 사용 권장)"}
    )
    
    tavily_api_key: Optional[str] = field(
        default=None,
        metadata={"description": "Tavily API 키"}
    )
    
    naver_client_id: Optional[str] = field(
        default=None,
        metadata={"description": "네이버 API 클라이언트 ID"}
    )
    
    naver_client_secret: Optional[str] = field(
        default=None,
        metadata={"description": "네이버 API 클라이언트 시크릿"}
    )

    @classmethod
    def from_dict(cls, config_dict: dict) -> "StormConfig":
        """딕셔너리에서 설정 인스턴스 생성
        
        Args:
            config_dict: 설정 딕셔너리
            
        Returns:
            StormConfig 인스턴스
        """
        return cls(**{k: v for k, v in config_dict.items() if hasattr(cls, k)})