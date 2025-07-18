# Google Cloud Run 배포 가이드

이 가이드는 AutoGen DeepResearch 백엔드를 Google Cloud Run에 배포하는 방법을 설명합니다.

## 🚀 사전 준비

### 1. Google Cloud Platform 설정
```bash
# Google Cloud SDK 설치 (macOS)
brew install google-cloud-sdk

# 또는 다른 방법으로 설치
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### 2. 프로젝트 초기화
```bash
# Google Cloud에 로그인
gcloud auth login

# 프로젝트 설정 (프로젝트 ID는 고유해야 함)
gcloud config set project YOUR_PROJECT_ID

# 필요한 API 활성화
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. 환경 변수 설정
```bash
# 프로젝트 ID 확인
gcloud config get-value project

# 리전 설정 (서울 리전)
gcloud config set run/region asia-northeast3
```

## 📦 배포 방법

### 방법 1: Google Cloud Build 사용 (권장)
```bash
# 프로젝트 루트 디렉토리에서 실행
gcloud builds submit --config cloudbuild.yaml

# 빌드 상태 확인
gcloud builds list --limit=5
```

### 방법 2: 직접 배포
```bash
# 1. 컨테이너 이미지 빌드
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/autogen-deepresearch

# 2. Cloud Run에 배포
gcloud run deploy autogen-deepresearch \
  --image gcr.io/YOUR_PROJECT_ID/autogen-deepresearch \
  --region asia-northeast3 \
  --platform managed \
  --allow-unauthenticated \
  --port 8002 \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --concurrency 10
```

## 🔧 환경 변수 설정

### Cloud Run 서비스에 환경 변수 추가
```bash
# 환경 변수 설정 (배포 시)
gcloud run deploy autogen-deepresearch \
  --image gcr.io/YOUR_PROJECT_ID/autogen-deepresearch \
  --region asia-northeast3 \
  --set-env-vars="AZURE_OPENAI_ENDPOINT=your_endpoint" \
  --set-env-vars="AZURE_OPENAI_API_KEY=your_api_key" \
  --set-env-vars="AZURE_OPENAI_DEPLOYMENT=your_deployment" \
  --set-env-vars="TAVILY_API_KEY=your_tavily_key" \
  --set-env-vars="PORT=8002"

# 또는 환경 변수만 업데이트
gcloud run services update autogen-deepresearch \
  --region asia-northeast3 \
  --update-env-vars="AZURE_OPENAI_ENDPOINT=your_endpoint,AZURE_OPENAI_API_KEY=your_api_key"
```

### Secret Manager 사용 (권장)
```bash
# Secret Manager API 활성화
gcloud services enable secretmanager.googleapis.com

# 시크릿 생성
gcloud secrets create azure-openai-key --data-file=-
# 키 입력 후 Ctrl+D

# Cloud Run에서 시크릿 사용
gcloud run deploy autogen-deepresearch \
  --image gcr.io/YOUR_PROJECT_ID/autogen-deepresearch \
  --region asia-northeast3 \
  --update-secrets="AZURE_OPENAI_API_KEY=azure-openai-key:latest"
```

## 📊 서비스 관리

### 서비스 상태 확인
```bash
# 서비스 리스트
gcloud run services list

# 서비스 상세 정보
gcloud run services describe autogen-deepresearch --region asia-northeast3

# 로그 확인
gcloud logs read --service=autogen-deepresearch --limit=50
```

### 서비스 업데이트
```bash
# 새 이미지로 업데이트
gcloud run deploy autogen-deepresearch \
  --image gcr.io/YOUR_PROJECT_ID/autogen-deepresearch:latest \
  --region asia-northeast3

# 트래픽 분할 (카나리 배포)
gcloud run services update-traffic autogen-deepresearch \
  --to-revisions=autogen-deepresearch-00001-abc=50,autogen-deepresearch-00002-def=50 \
  --region asia-northeast3
```

### 서비스 삭제
```bash
# 서비스 삭제
gcloud run services delete autogen-deepresearch --region asia-northeast3

# 컨테이너 이미지 삭제
gcloud container images delete gcr.io/YOUR_PROJECT_ID/autogen-deepresearch
```

## 🔍 문제 해결

### 로그 확인
```bash
# 실시간 로그 확인
gcloud logs tail --service=autogen-deepresearch

# 에러 로그만 확인
gcloud logs read --service=autogen-deepresearch --severity=ERROR --limit=20
```

### 서비스 디버깅
```bash
# 서비스 URL 확인
gcloud run services describe autogen-deepresearch --region asia-northeast3 --format="value(status.url)"

# 헬스체크 테스트
curl -f https://YOUR_SERVICE_URL/health
```

### 일반적인 문제들

1. **포트 문제**
   - Dockerfile에서 `EXPOSE 8002` 확인
   - Cloud Run 배포 시 `--port 8002` 옵션 확인

2. **환경 변수 문제**
   - 환경 변수가 올바르게 설정되었는지 확인
   - Secret Manager 권한 확인

3. **메모리/CPU 부족**
   - `--memory 2Gi --cpu 1` 옵션으로 리소스 증가

4. **타임아웃 문제**
   - `--timeout 300` 옵션으로 타임아웃 연장

## 🌐 도메인 연결

### 커스텀 도메인 사용
```bash
# 도메인 매핑
gcloud run domain-mappings create \
  --service autogen-deepresearch \
  --domain your-domain.com \
  --region asia-northeast3
```

## 💰 비용 최적화

### 설정 권장사항
```bash
# 비용 효율적인 설정
gcloud run deploy autogen-deepresearch \
  --image gcr.io/YOUR_PROJECT_ID/autogen-deepresearch \
  --region asia-northeast3 \
  --cpu-throttling \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --concurrency 10
```

## 🚀 자동 배포 설정

### GitHub Actions (선택사항)
`.github/workflows/deploy.yml` 파일 생성:
```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - uses: google-github-actions/setup-gcloud@v0
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: ${{ secrets.GCP_PROJECT_ID }}
        
    - name: Build and Deploy
      run: |
        gcloud builds submit --config cloudbuild.yaml
```

---

이 가이드를 따라하면 AutoGen DeepResearch 백엔드를 Google Cloud Run에 성공적으로 배포할 수 있습니다!