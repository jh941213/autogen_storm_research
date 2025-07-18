#!/bin/bash

# AutoGen DeepResearch - Google Cloud Run 배포 스크립트

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

# 프로젝트 설정 확인
check_gcloud_setup() {
    log_info "Google Cloud 설정 확인 중..."
    
    if ! command -v gcloud &> /dev/null; then
        log_error "Google Cloud CLI가 설치되지 않았습니다."
        log_info "다음 명령으로 설치하세요: brew install google-cloud-sdk"
        exit 1
    fi
    
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$PROJECT_ID" ]; then
        log_error "Google Cloud 프로젝트가 설정되지 않았습니다."
        log_info "다음 명령으로 설정하세요: gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
    
    log_success "프로젝트 ID: $PROJECT_ID"
}

# 필요한 API 활성화
enable_apis() {
    log_info "필요한 API 활성화 중..."
    
    gcloud services enable cloudbuild.googleapis.com --quiet
    gcloud services enable run.googleapis.com --quiet
    gcloud services enable containerregistry.googleapis.com --quiet
    
    log_success "API 활성화 완료"
}

# 환경 변수 입력
setup_env_vars() {
    log_info "환경 변수 설정..."
    
    # 환경 변수 파일이 있는지 확인
    if [ -f ".env" ]; then
        log_warning ".env 파일이 발견되었습니다. 보안을 위해 Cloud Run에서는 환경 변수를 별도로 설정합니다."
    fi
    
    # 필수 환경 변수 확인
    ENV_VARS=""
    
    if [ -n "$AZURE_OPENAI_ENDPOINT" ]; then
        ENV_VARS="${ENV_VARS}AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT},"
    fi
    
    if [ -n "$AZURE_OPENAI_API_KEY" ]; then
        ENV_VARS="${ENV_VARS}AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY},"
    fi
    
    if [ -n "$AZURE_OPENAI_DEPLOYMENT" ]; then
        ENV_VARS="${ENV_VARS}AZURE_OPENAI_DEPLOYMENT=${AZURE_OPENAI_DEPLOYMENT},"
    fi
    
    if [ -n "$TAVILY_API_KEY" ]; then
        ENV_VARS="${ENV_VARS}TAVILY_API_KEY=${TAVILY_API_KEY},"
    fi
    
    # PORT 환경 변수 추가
    ENV_VARS="${ENV_VARS}PORT=8002"
    
    if [ -n "$ENV_VARS" ]; then
        log_success "환경 변수 설정 완료"
        ENV_VARS_FLAG="--set-env-vars=${ENV_VARS}"
    else
        log_warning "환경 변수가 설정되지 않았습니다. 배포 후 수동으로 설정해야 합니다."
        ENV_VARS_FLAG=""
    fi
}

# 이미지 빌드
build_image() {
    log_info "컨테이너 이미지 빌드 중..."
    
    # 현재 Git 커밋 해시 가져오기
    if git rev-parse --git-dir > /dev/null 2>&1; then
        COMMIT_SHA=$(git rev-parse --short HEAD)
    else
        COMMIT_SHA="latest"
    fi
    
    IMAGE_NAME="gcr.io/${PROJECT_ID}/autogen-deepresearch:${COMMIT_SHA}"
    
    log_info "이미지 이름: $IMAGE_NAME"
    
    # Docker 이미지 빌드 및 푸시
    gcloud builds submit --tag "$IMAGE_NAME" .
    
    log_success "이미지 빌드 완료: $IMAGE_NAME"
}

# Cloud Run 배포
deploy_to_cloud_run() {
    log_info "Cloud Run에 배포 중..."
    
    DEPLOY_CMD="gcloud run deploy autogen-deepresearch \
        --image $IMAGE_NAME \
        --region asia-northeast3 \
        --platform managed \
        --allow-unauthenticated \
        --port 8002 \
        --memory 2Gi \
        --cpu 1 \
        --timeout 300 \
        --max-instances 10 \
        --min-instances 0 \
        --concurrency 10"
    
    if [ -n "$ENV_VARS_FLAG" ]; then
        DEPLOY_CMD="$DEPLOY_CMD $ENV_VARS_FLAG"
    fi
    
    eval $DEPLOY_CMD
    
    log_success "Cloud Run 배포 완료"
}

# 서비스 URL 확인
get_service_url() {
    log_info "서비스 URL 확인 중..."
    
    SERVICE_URL=$(gcloud run services describe autogen-deepresearch \
        --region asia-northeast3 \
        --format="value(status.url)")
    
    if [ -n "$SERVICE_URL" ]; then
        log_success "서비스 URL: $SERVICE_URL"
        log_info "헬스체크 URL: $SERVICE_URL/health"
        log_info "API 문서 URL: $SERVICE_URL/docs"
    else
        log_error "서비스 URL을 가져올 수 없습니다."
    fi
}

# 헬스체크 테스트
test_deployment() {
    log_info "배포 테스트 중..."
    
    if [ -n "$SERVICE_URL" ]; then
        # 헬스체크 테스트
        if curl -f "$SERVICE_URL/health" > /dev/null 2>&1; then
            log_success "헬스체크 통과"
        else
            log_warning "헬스체크 실패. 서비스가 완전히 시작되지 않았을 수 있습니다."
        fi
    fi
}

# 배포 정보 출력
show_deployment_info() {
    echo ""
    echo "======================================"
    echo "🚀 배포 완료!"
    echo "======================================"
    echo "프로젝트 ID: $PROJECT_ID"
    echo "서비스 이름: autogen-deepresearch"
    echo "리전: asia-northeast3"
    echo "이미지: $IMAGE_NAME"
    if [ -n "$SERVICE_URL" ]; then
        echo "서비스 URL: $SERVICE_URL"
        echo "헬스체크: $SERVICE_URL/health"
        echo "API 문서: $SERVICE_URL/docs"
    fi
    echo ""
    echo "관리 명령어:"
    echo "  로그 확인: gcloud logs read --service=autogen-deepresearch --limit=50"
    echo "  서비스 상태: gcloud run services describe autogen-deepresearch --region asia-northeast3"
    echo "  서비스 삭제: gcloud run services delete autogen-deepresearch --region asia-northeast3"
    echo "======================================"
}

# 메인 실행
main() {
    log_info "AutoGen DeepResearch Google Cloud Run 배포 시작"
    
    # 단계별 실행
    check_gcloud_setup
    enable_apis
    setup_env_vars
    build_image
    deploy_to_cloud_run
    get_service_url
    test_deployment
    show_deployment_info
    
    log_success "배포 프로세스 완료!"
}

# 스크립트 실행
main "$@"