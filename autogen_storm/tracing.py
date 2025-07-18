"""Langfuse 통합을 위한 추적 모듈

이 모듈은 AutoGen STORM과 Langfuse를 통합하여 
연구 과정을 추적하고 모니터링할 수 있게 합니다.
"""

import os
from typing import Optional, Dict, Any, Union
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Langfuse 클라이언트를 지연 로드하여 의존성 문제 방지
langfuse_client = None
openlit_initialized = False


def _get_langfuse_client():
    """Langfuse 클라이언트를 지연 로드"""
    global langfuse_client
    if langfuse_client is None:
        try:
            # Dynamic import to avoid dependency issues
            from langfuse import Langfuse  # type: ignore
            
            # Import settings here to avoid circular imports
            try:
                from app.config import settings
                public_key = settings.langfuse_public_key
                secret_key = settings.langfuse_secret_key
                host = settings.langfuse_host
            except ImportError:
                # Fallback to environment variables if settings not available
                public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
                secret_key = os.getenv("LANGFUSE_SECRET_KEY")
                host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            
            if not public_key or not secret_key:
                logger.warning("Langfuse API 키가 설정되지 않았습니다.")
                return None
            
            langfuse_client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=host
            )
            
        except ImportError:
            logger.warning("Langfuse가 설치되지 않았습니다.")
            return None
        except Exception as e:
            logger.error(f"Langfuse 클라이언트 생성 오류: {e}")
            return None
    
    return langfuse_client


def _init_openlit():
    """OpenLIT 초기화"""
    global openlit_initialized
    if openlit_initialized:
        return True
        
    try:
        import openlit  # type: ignore
        client = _get_langfuse_client()
        if client and hasattr(client, '_otel_tracer'):
            openlit.init(tracer=client._otel_tracer, disable_batch=True)
            openlit_initialized = True
            logger.info("✅ OpenLIT 계측이 초기화되었습니다.")
            return True
    except ImportError:
        logger.warning("OpenLIT가 설치되지 않았습니다.")
    except Exception as e:
        logger.warning(f"OpenLIT 초기화 실패: {e}")
    
    return False


class TracingManager:
    """Langfuse 추적 관리자 - 간소화된 버전"""
    
    def __init__(self):
        self.enabled = False
        self.current_trace = None
        self._session_id: Optional[str] = None
        
    def initialize(self) -> bool:
        """Langfuse 추적 초기화"""
        try:
            client = _get_langfuse_client()
            if not client:
                logger.info("⚠️  Langfuse 추적이 비활성화되었습니다. (API 키 확인 필요)")
                return False
            
            # 연결 테스트
            if client.auth_check():
                logger.info("✅ Langfuse 클라이언트가 성공적으로 인증되었습니다!")
                self.enabled = True
                
                # OpenLIT 초기화 시도
                _init_openlit()
                
                return True
            else:
                logger.error("❌ Langfuse 인증에 실패했습니다.")
                return False
                
        except Exception as e:
            logger.error(f"❌ Langfuse 초기화 중 오류 발생: {e}")
            return False
    
    @contextmanager
    def trace_research(self, topic: str, task_id: Optional[str] = None):
        """연구 작업 추적 컨텍스트 관리자"""
        if not self.enabled:
            yield None
            return
        
        client = _get_langfuse_client()
        if not client:
            yield None
            return
        
        trace = None
        try:
            # 안전한 입력 데이터 준비
            input_data: Dict[str, str] = {
                "topic": str(topic) if topic else "Unknown",
                "task_id": str(task_id) if task_id else "auto-generated"
            }
            
            # 새로운 Langfuse SDK 방식으로 trace 생성
            trace = client.trace(
                name="storm_research",
                input=input_data,
                metadata={
                    "framework": "autogen_storm",
                    "version": "1.0.0"
                },
                tags=["research", "storm", "autogen"]
            )
            
            self.current_trace = trace
            logger.info(f"🔍 연구 작업 추적 시작: {topic}")
            yield trace
            
        except Exception as e:
            logger.error(f"연구 작업 추적 오류: {e}")
            yield None
        finally:
            if trace:
                try:
                    # 추적 완료 처리는 별도로 하지 않음 (자동 처리)
                    self.current_trace = None
                except Exception as e:
                    logger.error(f"추적 완료 처리 오류: {e}")
    
    def log_event(self, name: str, data: Optional[Dict[str, Any]] = None, level: str = "INFO"):
        """간단한 이벤트 로깅"""
        if not self.enabled or not self.current_trace:
            return
        
        try:
            client = _get_langfuse_client()
            if not client:
                return
            
            # 안전한 데이터 처리
            safe_data: Dict[str, Any] = {}
            if data:
                for key, value in data.items():
                    if value is not None:
                        safe_data[key] = str(value) if not isinstance(value, (str, int, float, bool, list, dict)) else value
            
            client.event(
                trace_id=self.current_trace.id if self.current_trace else None,
                name=name,
                metadata=safe_data,
                level=level
            )
            
        except Exception as e:
            logger.error(f"이벤트 로깅 오류: {e}")
    
    def log_generation(self, name: str, input_data: Optional[Union[str, Dict[str, Any]]] = None, 
                      output_data: Optional[Union[str, Dict[str, Any]]] = None, model: Optional[str] = None):
        """생성 과정 로깅"""
        if not self.enabled or not self.current_trace:
            return
        
        try:
            client = _get_langfuse_client()
            if not client:
                return
            
            # 안전한 데이터 처리
            safe_input = str(input_data) if input_data and not isinstance(input_data, dict) else input_data
            safe_output = str(output_data) if output_data and not isinstance(output_data, dict) else output_data
            
            generation_data: Dict[str, Any] = {
                "name": name,
                "trace_id": self.current_trace.id if self.current_trace else None
            }
            
            if safe_input is not None:
                generation_data["input"] = safe_input
            if safe_output is not None:
                generation_data["output"] = safe_output
            if model:
                generation_data["model"] = model
            
            client.generation(**generation_data)
            
        except Exception as e:
            logger.error(f"생성 로깅 오류: {e}")
    
    def get_trace_url(self) -> Optional[str]:
        """현재 추적 URL 반환"""
        if not self.enabled or not self.current_trace:
            return None
        
        try:
            host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            return f"{host}/trace/{self.current_trace.id}"
        except Exception as e:
            logger.error(f"추적 URL 생성 오류: {e}")
            return None
    
    def close(self) -> None:
        """리소스 정리"""
        if self.enabled:
            try:
                client = _get_langfuse_client()
                if client:
                    client.flush()
                logger.info("✅ Langfuse 클라이언트가 정리되었습니다.")
            except Exception as e:
                logger.error(f"Langfuse 클라이언트 정리 오류: {e}")


# 전역 추적 관리자 인스턴스
tracing_manager = TracingManager()


def get_tracing_manager() -> TracingManager:
    """추적 관리자 인스턴스 반환"""
    return tracing_manager


def initialize_tracing() -> bool:
    """추적 초기화 편의 함수"""
    return tracing_manager.initialize() 