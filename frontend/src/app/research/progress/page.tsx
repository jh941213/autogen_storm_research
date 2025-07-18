'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Header } from '@/components/layout/header';
import { EnhancedProgress } from '@/components/research/enhanced-progress';
import { 
  AnalystCountDialog, 
  ReportApprovalDialog, 
  FeedbackDialog, 
  FullReportDialog 
} from '@/components/research/feedback-dialogs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, Home, RotateCcw, Settings, Brain, Users, MessageSquare, Zap } from 'lucide-react';
import { useResearchStore } from '@/store/research-store';

export default function ResearchProgressPage() {
  const router = useRouter();
  const {
    currentSession,
    status,
    progress,
    currentStep,
    result,
    error,
    agentActivity,
    subActivity,
    researchConfig,
    pendingAnalystCount,
    pendingReportApproval,
    showFeedbackDialog,
    showFullReportDialog,
    sendAnalystCount,
    sendReportApproval,
    setShowFeedbackDialog,
    setShowFullReportDialog,
    resetState
  } = useResearchStore();

  // 세션이 없으면 홈으로 리다이렉트
  useEffect(() => {
    if (!currentSession && status === 'idle') {
      router.push('/');
    }
  }, [currentSession, status, router]);

  // 연구 완료 시 결과 페이지로 이동
  useEffect(() => {
    if (status === 'completed' && result) {
      setTimeout(() => {
        router.push(`/research/result/${currentSession}`);
      }, 2000);
    }
  }, [status, result, currentSession, router]);

  // 컴포넌트 언마운트 시 WebSocket 연결 해제
  useEffect(() => {
    return () => {
      // 페이지를 떠날 때 WebSocket 연결 유지 (결과 페이지로 이동할 수 있도록)
    };
  }, []);

  const handleAnalystCountSubmit = (count: number) => {
    sendAnalystCount(count);
  };

  const handleReportApproval = (action: 'approve' | 'rewrite' | 'view_full', feedback?: string) => {
    if (action === 'view_full' && pendingReportApproval) {
      setShowFullReportDialog(true);
    } else if (action === 'rewrite' && !feedback) {
      setShowFeedbackDialog(true);
    } else {
      sendReportApproval(action, feedback);
    }
  };

  const handleFeedbackSubmit = (feedback: string) => {
    sendReportApproval('rewrite', feedback);
    setShowFeedbackDialog(false);
  };

  const handleRestart = () => {
    resetState();
    router.push('/');
  };

  const handleGoHome = () => {
    router.push('/');
  };

  const getModelDisplayName = (provider: string, azureDeployment?: string) => {
    switch (provider) {
      case 'openai':
        return 'OpenAI GPT-4';
      case 'azure_openai':
        return azureDeployment ? `Azure OpenAI (${azureDeployment})` : 'Azure OpenAI';
      case 'anthropic':
        return 'Anthropic Claude';
      default:
        return provider;
    }
  };

  if (!currentSession && status === 'idle') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-background/95">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center min-h-[60vh]">
            <Card className="max-w-md">
              <CardHeader>
                <CardTitle className="text-center">연구 세션이 없습니다</CardTitle>
              </CardHeader>
              <CardContent className="text-center space-y-4">
                <p className="text-muted-foreground">
                  진행 중인 연구가 없습니다. 새로운 연구를 시작해주세요.
                </p>
                <Button onClick={handleGoHome} className="w-full">
                  <Home className="mr-2 h-4 w-4" />
                  홈으로 돌아가기
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-background/95">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* 헤더 */}
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold">연구 진행 상황</h1>
            <p className="text-muted-foreground">
              AI 전문가들이 실시간으로 연구를 수행하고 있습니다
            </p>
            {currentSession && (
              <Badge variant="outline" className="text-xs">
                세션 ID: {currentSession}
              </Badge>
            )}
          </div>

          {/* 연구 설정 정보 */}
          {researchConfig && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  연구 설정
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm font-medium">
                      <Brain className="h-4 w-4" />
                      AI 모델
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {getModelDisplayName(researchConfig.modelProvider, researchConfig.azureDeployment)}
                    </div>
                    {researchConfig.modelProvider === 'azure_openai' && researchConfig.azureEndpoint && (
                      <div className="text-xs text-muted-foreground/80">
                        {researchConfig.azureEndpoint}
                      </div>
                    )}
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm font-medium">
                      <Users className="h-4 w-4" />
                      최대 분석가 수
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {researchConfig.maxAnalysts}명
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm font-medium">
                      <MessageSquare className="h-4 w-4" />
                      인터뷰 턴 수
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {researchConfig.maxInterviewTurns}턴
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm font-medium">
                      <Zap className="h-4 w-4" />
                      병렬 처리
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {researchConfig.parallelInterviews ? '활성화' : '비활성화'}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 에러 상태 */}
          {status === 'error' && (
            <Card className="border-red-200 bg-red-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-red-700">
                  <AlertCircle className="h-5 w-5" />
                  연구 중 오류 발생
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-red-600 mb-4">{error}</p>
                <div className="flex gap-2">
                  <Button onClick={handleRestart} variant="outline">
                    <RotateCcw className="mr-2 h-4 w-4" />
                    다시 시도
                  </Button>
                  <Button onClick={handleGoHome} variant="outline">
                    <Home className="mr-2 h-4 w-4" />
                    홈으로
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 진행 상황 표시 */}
          <EnhancedProgress
            progress={progress}
            status={status}
            currentStep={currentStep}
            agentActivity={agentActivity || undefined}
            sessionId={currentSession || undefined}
            subActivity={subActivity || undefined}
          />

          {/* 완료 상태 */}
          {status === 'completed' && (
            <Card className="border-green-200 bg-green-50">
              <CardContent className="pt-6">
                <div className="text-center space-y-4">
                  <div className="text-2xl">🎉</div>
                  <h3 className="text-lg font-semibold text-green-800">
                    연구가 완료되었습니다!
                  </h3>
                  <p className="text-green-600">
                    곧 결과 페이지로 이동합니다...
                  </p>
                  <Button 
                    onClick={() => router.push(`/research/result/${currentSession}`)}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    결과 확인하기
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </main>

      {/* 인터랙티브 다이얼로그들 */}
      {pendingAnalystCount && (
        <AnalystCountDialog
          isOpen={true}
          data={pendingAnalystCount}
          onSubmit={handleAnalystCountSubmit}
          onClose={() => {
            // 취소 시 WebSocket 연결 해제하고 홈페이지로 이동
            resetState();
            router.push('/');
          }}
        />
      )}

      {pendingReportApproval && (
        <ReportApprovalDialog
          isOpen={true}
          data={pendingReportApproval}
          onApprove={() => handleReportApproval('approve')}
          onRewrite={(feedback) => handleReportApproval('rewrite', feedback)}
          onViewFull={() => handleReportApproval('view_full')}
          onClose={() => {}}
        />
      )}

      {showFeedbackDialog && (
        <FeedbackDialog
          isOpen={true}
          onSubmit={handleFeedbackSubmit}
          onClose={() => setShowFeedbackDialog(false)}
        />
      )}

      {showFullReportDialog && pendingReportApproval && (
        <FullReportDialog
          isOpen={true}
          report={pendingReportApproval.preview.full_report}
          onClose={() => setShowFullReportDialog(false)}
        />
      )}
    </div>
  );
}