#!/bin/bash

# AutoGen DeepResearch - Vercel 프론트엔드 배포 스크립트
# 사용법: ./deploy-frontend.sh [BACKEND_URL]

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

# 백엔드 URL 설정
BACKEND_URL=${1:-"https://autogen-deepresearch-296922371397.asia-northeast3.run.app"}

# Vercel CLI 설치 확인
check_vercel_cli() {
    log_info "Vercel CLI 설치 확인 중..."
    
    if ! command -v vercel &> /dev/null; then
        log_warning "Vercel CLI가 설치되지 않았습니다. 설치 중..."
        npm install -g vercel
        log_success "Vercel CLI 설치 완료"
    else
        log_success "Vercel CLI 이미 설치됨"
    fi
}

# 프론트엔드 디렉토리로 이동
cd_frontend() {
    log_info "프론트엔드 디렉토리로 이동 중..."
    
    # 스크립트 디렉토리 기준으로 frontend 디렉토리 찾기
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    FRONTEND_DIR="$SCRIPT_DIR/../frontend"
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        log_error "프론트엔드 디렉토리를 찾을 수 없습니다: $FRONTEND_DIR"
        exit 1
    fi
    
    cd "$FRONTEND_DIR"
    log_success "프론트엔드 디렉토리로 이동 완료: $(pwd)"
}

# 환경 변수 설정
setup_env() {
    log_info "환경 변수 설정 중..."
    
    # .env.local 파일 생성/업데이트
    echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" > .env.local
    
    log_success "환경 변수 설정 완료"
    log_info "백엔드 URL: $BACKEND_URL"
}

# 의존성 설치
install_dependencies() {
    log_info "의존성 설치 중..."
    
    npm install
    
    log_success "의존성 설치 완료"
}

# 빌드 테스트
test_build() {
    log_info "빌드 테스트 중..."
    
    npm run build
    
    log_success "빌드 테스트 완료"
}

# Vercel 로그인 확인
check_vercel_auth() {
    log_info "Vercel 인증 확인 중..."
    
    if ! vercel whoami &> /dev/null; then
        log_warning "Vercel 로그인이 필요합니다."
        log_info "브라우저에서 로그인을 완료해주세요."
        vercel login
    else
        log_success "Vercel 인증 완료"
    fi
}

# Vercel 배포
deploy_to_vercel() {
    log_info "Vercel에 배포 중..."
    
    # 기존 .vercel 디렉토리 제거 (필요시)
    if [ -d ".vercel" ]; then
        log_warning "기존 .vercel 디렉토리 제거 중..."
        rm -rf .vercel
    fi
    
    # 프로덕션 배포
    vercel --prod --yes
    
    log_success "Vercel 배포 완료"
}

# 배포 정보 출력
show_deployment_info() {
    echo ""
    echo "======================================"
    echo "🚀 프론트엔드 배포 완료!"
    echo "======================================"
    echo "백엔드 URL: $BACKEND_URL"
    echo "프론트엔드: Vercel에서 배포 완료"
    echo ""
    echo "다음 단계:"
    echo "1. 배포된 URL로 접속하여 테스트"
    echo "2. 백엔드 API 연결 확인"
    echo "3. 기능 동작 테스트"
    echo ""
    echo "관리 명령어:"
    echo "  배포 상태: vercel ls"
    echo "  로그 확인: vercel logs"
    echo "  도메인 설정: vercel domains"
    echo "======================================"
}

# 메인 실행
main() {
    log_info "AutoGen DeepResearch 프론트엔드 배포 시작"
    
    # 단계별 실행
    check_vercel_cli
    cd_frontend
    setup_env
    install_dependencies
    test_build
    check_vercel_auth
    deploy_to_vercel
    show_deployment_info
    
    log_success "프론트엔드 배포 프로세스 완료!"
}

# 스크립트 실행
main "$@"