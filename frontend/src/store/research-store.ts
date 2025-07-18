import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { 
  ResearchState, 
  ResearchFormData, 
  ResearchResult, 
  AnalystCountRequest, 
  ReportApprovalRequest 
} from '@/types';

interface AgentActivity {
  action: string;
  details: string;
  timestamp: string;
  analysts?: Array<{
    name: string;
    role: string;
    affiliation: string;
  }>;
  interview_count?: number;
  current_analyst?: {
    name: string;
    role: string;
    affiliation: string;
  };
  completed_analyst?: {
    name: string;
    role: string;
  };
  progress?: string;
}
import { WebSocketClient } from '@/lib/websocket';
import { apiClient } from '@/lib/api';

interface ResearchStore extends ResearchState {
  // Enhanced progress data
  agentActivity: AgentActivity | null;
  subActivity: string | null;
  
  // Actions
  startResearch: (data: ResearchFormData) => Promise<void>;
  connectWebSocket: (sessionId: string) => Promise<void>;
  disconnectWebSocket: () => void;
  sendAnalystCount: (count: number) => void;
  sendReportApproval: (action: 'approve' | 'rewrite' | 'view_full', feedback?: string) => void;
  
  // UI Actions
  setShowFeedbackDialog: (show: boolean) => void;
  setShowFullReportDialog: (show: boolean) => void;
  resetState: () => void;
  
  // Internal actions
  setStatus: (status: ResearchState['status']) => void;
  setProgress: (progress: string) => void;
  setCurrentStep: (step: ResearchState['currentStep']) => void;
  setResult: (result: ResearchResult) => void;
  setError: (error: string) => void;
  setPendingAnalystCount: (data: AnalystCountRequest | null) => void;
  setPendingReportApproval: (data: ReportApprovalRequest | null) => void;
  setAgentActivity: (activity: AgentActivity | null) => void;
  setSubActivity: (subActivity: string | null) => void;
}

const initialState: ResearchState & { agentActivity: AgentActivity | null; subActivity: string | null } = {
  currentSession: null,
  status: 'idle',
  progress: '',
  currentStep: 'setup',
  websocket: null,
  result: null,
  error: null,
  researchConfig: null,
  pendingAnalystCount: null,
  pendingReportApproval: null,
  showFeedbackDialog: false,
  showFullReportDialog: false,
  agentActivity: null,
  subActivity: null,
};

export const useResearchStore = create<ResearchStore>()(
  devtools(
    (set, get) => ({
      ...initialState,

      startResearch: async (data: ResearchFormData) => {
        try {
          set({ status: 'connecting', progress: '연구 시작 중...', error: null });
          
          // 세션 ID 생성
          const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          
          // WebSocket 연결
          await get().connectWebSocket(sessionId);
          
          // 인터랙티브 연구 시작
          const request = {
            topic: data.topic,
            max_analysts: data.maxAnalysts,
            max_interview_turns: data.maxInterviewTurns,
            parallel_interviews: data.parallelInterviews,
            model_provider: data.modelProvider,
            api_key: data.apiKey,
            azure_endpoint: data.azureEndpoint,
            azure_deployment: data.azureDeployment,
          };
          
          await apiClient.startInteractiveResearch(sessionId, request);
          
          set({ 
            currentSession: sessionId,
            status: 'running',
            currentStep: 'analysts',
            progress: '연구가 시작되었습니다...',
            researchConfig: data
          });
          
        } catch (error) {
          console.error('Error starting research:', error);
          console.error('Error details:', {
            name: error instanceof Error ? error.name : 'Unknown',
            message: error instanceof Error ? error.message : String(error),
            stack: error instanceof Error ? error.stack : undefined
          });
          set({ 
            status: 'error', 
            error: error instanceof Error ? error.message : '연구 시작 중 오류가 발생했습니다.' 
          });
        }
      },

      connectWebSocket: async (sessionId: string) => {
        const wsUrl = apiClient.getWebSocketURL(sessionId);
        const ws = new WebSocketClient(wsUrl);
        
        // 메시지 핸들러 등록
        ws.on('progress', (data) => {
          if ('message' in data) {
            const updates: Partial<ResearchStore> = { progress: data.message };
            
            // 에이전트 활동 정보 처리
            if ('agent_activity' in data) {
              updates.agentActivity = data.agent_activity as AgentActivity;
            }
            
            // 현재 단계 업데이트
            if ('current_step' in data) {
              updates.currentStep = data.current_step as ResearchState['currentStep'];
            }
            
            // 서브 활동 처리
            if ('sub_activity' in data) {
              updates.subActivity = data.sub_activity as string;
            }
            
            set(updates);
          }
        });
        
        ws.on('analyst_count_request', (data) => {
          if ('default_count' in data && 'message' in data) {
            set({ 
              pendingAnalystCount: data as AnalystCountRequest,
              currentStep: 'analysts'
            });
          }
        });
        
        ws.on('report_approval_request', (data) => {
          if ('topic' in data && 'preview' in data) {
            set({ 
              pendingReportApproval: data as ReportApprovalRequest,
              currentStep: 'feedback'
            });
          }
        });
        
        ws.on('result', (data) => {
          if ('topic' in data && 'analysts' in data) {
            set({ 
              result: data as ResearchResult,
              status: 'completed',
              currentStep: 'completed',
              progress: '연구가 완료되었습니다!'
            });
          }
        });
        
        ws.on('error', (data) => {
          if ('error' in data) {
            set({ 
              status: 'error',
              error: data.error || '알 수 없는 오류가 발생했습니다.'
            });
          }
        });
        
        // 연결 상태 핸들러
        ws.onConnection({
          onOpen: () => {
            console.log('WebSocket connected successfully');
            set({ status: 'connected' });
          },
          onClose: () => {
            console.log('WebSocket connection closed');
            set({ status: 'idle' });
          },
          onError: (error) => {
            console.error('WebSocket connection error:', error);
            set({ 
              status: 'error',
              error: `WebSocket 연결 오류: ${error.type || 'Unknown error'}`
            });
          }
        });
        
        await ws.connect();
        set({ websocket: ws });
      },

      disconnectWebSocket: () => {
        const { websocket } = get();
        if (websocket) {
          (websocket as WebSocketClient).disconnect();
          set({ websocket: null });
        }
      },

      sendAnalystCount: (count: number) => {
        const { websocket } = get();
        if (websocket) {
          (websocket as WebSocketClient).sendMessage('analyst_count', { count });
          set({ 
            pendingAnalystCount: null,
            currentStep: 'interviews',
            progress: `${count}명의 분석가로 연구를 진행합니다...`
          });
        }
      },

      sendReportApproval: (action: 'approve' | 'rewrite' | 'view_full', feedback?: string) => {
        const { websocket } = get();
        if (websocket) {
          const data: { action: 'approve' | 'rewrite' | 'view_full'; rewrite_type?: 'complete' | 'feedback'; feedback?: string } = { action };
          
          if (action === 'rewrite') {
            data.rewrite_type = 'feedback';
            data.feedback = feedback;
          }
          
          (websocket as WebSocketClient).sendMessage('report_approval', data);
          
          if (action === 'approve') {
            set({ 
              pendingReportApproval: null,
              currentStep: 'completed',
              progress: '보고서가 승인되었습니다!'
            });
          } else if (action === 'rewrite') {
            set({ 
              pendingReportApproval: null,
              currentStep: 'report',
              progress: '피드백을 바탕으로 보고서를 다시 작성하고 있습니다...'
            });
          }
        }
      },

      setShowFeedbackDialog: (show: boolean) => {
        set({ showFeedbackDialog: show });
      },

      setShowFullReportDialog: (show: boolean) => {
        set({ showFullReportDialog: show });
      },

      resetState: () => {
        const { websocket } = get();
        if (websocket) {
          (websocket as WebSocketClient).disconnect();
        }
        set({ ...initialState });
      },

      setStatus: (status: ResearchState['status']) => {
        set({ status });
      },

      setProgress: (progress: string) => {
        set({ progress });
      },

      setCurrentStep: (step: ResearchState['currentStep']) => {
        set({ currentStep: step });
      },

      setResult: (result: ResearchResult) => {
        set({ result });
      },

      setError: (error: string) => {
        set({ error });
      },

      setPendingAnalystCount: (data: AnalystCountRequest | null) => {
        set({ pendingAnalystCount: data });
      },

      setPendingReportApproval: (data: ReportApprovalRequest | null) => {
        set({ pendingReportApproval: data });
      },

      setAgentActivity: (activity: AgentActivity | null) => {
        set({ agentActivity: activity });
      },

      setSubActivity: (subActivity: string | null) => {
        set({ subActivity });
      },
    }),
    {
      name: 'research-store',
    }
  )
);