#!/bin/bash

# AutoGen DeepResearch - 환경 변수 설정 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 변수 설정
setup_env_vars() {
    log_info "Cloud Run 서비스에 환경 변수 설정 중..."
    
    # 환경 변수 입력받기
    echo ""
    echo "필수 환경 변수를 입력하세요:"
    echo ""
    
    read -p "Azure OpenAI Endpoint: " AZURE_OPENAI_ENDPOINT
    read -s -p "Azure OpenAI API Key: " AZURE_OPENAI_API_KEY
    echo ""
    read -p "Azure OpenAI Deployment Name: " AZURE_OPENAI_DEPLOYMENT
    read -s -p "Tavily API Key: " TAVILY_API_KEY
    echo ""
    
    # 선택적 환경 변수
    echo ""
    echo "선택적 환경 변수 (엔터로 스킵 가능):"
    echo ""
    
    read -s -p "OpenAI API Key (선택): " OPENAI_API_KEY
    echo ""
    read -s -p "Anthropic API Key (선택): " ANTHROPIC_API_KEY
    echo ""
    read -s -p "Langfuse Secret Key (선택): " LANGFUSE_SECRET_KEY
    echo ""
    read -s -p "Langfuse Public Key (선택): " LANGFUSE_PUBLIC_KEY
    echo ""
    read -p "Langfuse Host (선택): " LANGFUSE_HOST
    
    # 환경 변수 문자열 구성
    ENV_VARS="AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT},AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY},AZURE_OPENAI_DEPLOYMENT=${AZURE_OPENAI_DEPLOYMENT},TAVILY_API_KEY=${TAVILY_API_KEY},PORT=8002"
    
    if [ -n "$OPENAI_API_KEY" ]; then
        ENV_VARS="${ENV_VARS},OPENAI_API_KEY=${OPENAI_API_KEY}"
    fi
    
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        ENV_VARS="${ENV_VARS},ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}"
    fi
    
    if [ -n "$LANGFUSE_SECRET_KEY" ]; then
        ENV_VARS="${ENV_VARS},LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}"
    fi
    
    if [ -n "$LANGFUSE_PUBLIC_KEY" ]; then
        ENV_VARS="${ENV_VARS},LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}"
    fi
    
    if [ -n "$LANGFUSE_HOST" ]; then
        ENV_VARS="${ENV_VARS},LANGFUSE_HOST=${LANGFUSE_HOST}"
    fi
    
    # Cloud Run 서비스 업데이트
    log_info "Cloud Run 서비스 업데이트 중..."
    
    gcloud run services update autogen-deepresearch \
        --region asia-northeast3 \
        --update-env-vars="$ENV_VARS"
    
    log_success "환경 변수 설정 완료"
}

# Secret Manager 설정 (권장)
setup_secret_manager() {
    log_info "Secret Manager 설정 중..."
    
    # Secret Manager API 활성화
    gcloud services enable secretmanager.googleapis.com --quiet
    
    # 시크릿 생성
    echo "$AZURE_OPENAI_API_KEY" | gcloud secrets create azure-openai-key --data-file=-
    echo "$TAVILY_API_KEY" | gcloud secrets create tavily-api-key --data-file=-
    
    if [ -n "$OPENAI_API_KEY" ]; then
        echo "$OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=-
    fi
    
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        echo "$ANTHROPIC_API_KEY" | gcloud secrets create anthropic-api-key --data-file=-
    fi
    
    if [ -n "$LANGFUSE_SECRET_KEY" ]; then
        echo "$LANGFUSE_SECRET_KEY" | gcloud secrets create langfuse-secret-key --data-file=-
    fi
    
    if [ -n "$LANGFUSE_PUBLIC_KEY" ]; then
        echo "$LANGFUSE_PUBLIC_KEY" | gcloud secrets create langfuse-public-key --data-file=-
    fi
    
    # Cloud Run에서 시크릿 사용
    SECRETS="AZURE_OPENAI_API_KEY=azure-openai-key:latest,TAVILY_API_KEY=tavily-api-key:latest"
    
    if [ -n "$OPENAI_API_KEY" ]; then
        SECRETS="${SECRETS},OPENAI_API_KEY=openai-api-key:latest"
    fi
    
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        SECRETS="${SECRETS},ANTHROPIC_API_KEY=anthropic-api-key:latest"
    fi
    
    if [ -n "$LANGFUSE_SECRET_KEY" ]; then
        SECRETS="${SECRETS},LANGFUSE_SECRET_KEY=langfuse-secret-key:latest"
    fi
    
    if [ -n "$LANGFUSE_PUBLIC_KEY" ]; then
        SECRETS="${SECRETS},LANGFUSE_PUBLIC_KEY=langfuse-public-key:latest"
    fi
    
    # 환경 변수 및 시크릿 업데이트
    NON_SECRET_VARS="AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT},AZURE_OPENAI_DEPLOYMENT=${AZURE_OPENAI_DEPLOYMENT},PORT=8002"
    
    if [ -n "$LANGFUSE_HOST" ]; then
        NON_SECRET_VARS="${NON_SECRET_VARS},LANGFUSE_HOST=${LANGFUSE_HOST}"
    fi
    
    gcloud run services update autogen-deepresearch \
        --region asia-northeast3 \
        --update-env-vars="$NON_SECRET_VARS" \
        --update-secrets="$SECRETS"
    
    log_success "Secret Manager 설정 완료"
}

# 메인 실행
main() {
    echo "======================================"
    echo "🔧 AutoGen DeepResearch 환경 변수 설정"
    echo "======================================"
    echo ""
    echo "1. 환경 변수 직접 설정"
    echo "2. Secret Manager 사용 (권장)"
    echo ""
    read -p "선택하세요 (1 또는 2): " choice
    
    case $choice in
        1)
            setup_env_vars
            ;;
        2)
            setup_env_vars
            setup_secret_manager
            ;;
        *)
            log_error "잘못된 선택입니다."
            exit 1
            ;;
    esac
    
    log_success "환경 변수 설정 완료!"
    echo ""
    echo "서비스 확인:"
    echo "  gcloud run services describe autogen-deepresearch --region asia-northeast3"
    echo ""
    echo "로그 확인:"
    echo "  gcloud logs read --service=autogen-deepresearch --limit=20"
}

# 스크립트 실행
main "$@"