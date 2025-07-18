// API 타입 정의
export interface ResearchRequest {
  topic: string;
  max_analysts: number;
  max_interview_turns: number;
  parallel_interviews: boolean;
  model_provider: string;
}

export interface ResearchResponse {
  success: boolean;
  message: string;
  task_id?: string;
  result?: ResearchResult;
}

export interface ResearchStatus {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: string;
  result?: ResearchResult;
  error?: string;
}

export interface Analyst {
  name: string;
  role: string;
  affiliation: string;
  description: string;
}

export interface ResearchResult {
  topic: string;
  analysts: Analyst[];
  interview_count: number;
  final_report: string;
  completed_at: string;
}

// WebSocket 메시지 타입들
export type MessageType = 
  | 'progress'
  | 'analyst_count_request'
  | 'report_approval_request'
  | 'feedback_request'
  | 'result'
  | 'error';

export type UserResponseType = 
  | 'analyst_count'
  | 'report_approval'
  | 'feedback';

export interface WebSocketMessage {
  type: MessageType;
  data: AnalystCountRequest | ReportApprovalRequest | ResearchResult | { message: string } | { error: string };
}

export interface UserResponse {
  type: UserResponseType;
  data: { count: number } | ReportApprovalResponse | { feedback: string };
}

export interface AnalystCountRequest {
  default_count: number;
  message: string;
}

export interface ReportPreview {
  version: number;
  introduction_preview: string;
  main_content_preview: string;
  conclusion_preview: string;
  total_length: number;
  full_report?: {
    introduction: string;
    main_content: string;
    conclusion: string;
  };
}

export interface ReportApprovalRequest {
  topic: string;
  preview: ReportPreview;
  options: string[];
}

export interface ReportApprovalResponse {
  action: 'approve' | 'rewrite' | 'view_full';
  rewrite_type?: 'complete' | 'feedback';
  feedback?: string;
}

// 폼 타입들
export interface ResearchFormData {
  topic: string;
  maxAnalysts: number;
  maxInterviewTurns: number;
  parallelInterviews: boolean;
  modelProvider: 'openai' | 'azure_openai' | 'anthropic';
  apiKey?: string;
  azureEndpoint?: string;
  azureDeployment?: string;
}

// 상태 관리 타입들
export interface ResearchState {
  currentSession: string | null;
  status: 'idle' | 'connecting' | 'connected' | 'running' | 'completed' | 'error';
  progress: string;
  currentStep: 'setup' | 'analysts' | 'interviews' | 'report' | 'feedback' | 'completed';
  websocket: unknown | null;
  result: ResearchResult | null;
  error: string | null;
  
  // 연구 설정 정보
  researchConfig: ResearchFormData | null;
  
  // 인터랙티브 상태들
  pendingAnalystCount: AnalystCountRequest | null;
  pendingReportApproval: ReportApprovalRequest | null;
  showFeedbackDialog: boolean;
  showFullReportDialog: boolean;
}

// UI 컴포넌트 props 타입들
export interface ResearchFormProps {
  onSubmit: (data: ResearchFormData) => void;
  isLoading?: boolean;
}


export interface AnalystCountDialogProps {
  isOpen: boolean;
  data: AnalystCountRequest;
  onSubmit: (count: number) => void;
  onClose: () => void;
}

export interface ReportApprovalDialogProps {
  isOpen: boolean;
  data: ReportApprovalRequest;
  onApprove: () => void;
  onRewrite: (feedback?: string) => void;
  onViewFull: () => void;
  onClose: () => void;
}

export interface FeedbackDialogProps {
  isOpen: boolean;
  onSubmit: (feedback: string) => void;
  onClose: () => void;
}

export interface FullReportDialogProps {
  isOpen: boolean;
  report: ReportPreview['full_report'];
  onClose: () => void;
}