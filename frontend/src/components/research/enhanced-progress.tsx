'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Activity,
  Brain,
  Users,
  MessageSquare,
  FileText,
  CheckCircle,
  Search,
  Sparkles,
  Loader2,
  ChevronRight,
  Circle,
  Zap
} from 'lucide-react';
import { cn, formatTime, getStatusColor } from '@/lib/utils';

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

interface EnhancedProgressProps {
  progress: string;
  status: 'idle' | 'connecting' | 'connected' | 'running' | 'completed' | 'error';
  currentStep?: string;
  agentActivity?: AgentActivity;
  sessionId?: string;
  subActivity?: string;
}

const researchSteps = [
  {
    id: 'setup',
    title: '연구 설정',
    description: '연구 매개변수 구성',
    icon: Circle,
    color: 'text-blue-500'
  },
  {
    id: 'analysts',
    title: '전문가 팀 구성',
    description: '분야별 전문가 생성',
    icon: Users,
    color: 'text-green-500'
  },
  {
    id: 'interviews',
    title: '심층 인터뷰',
    description: '전문가 인터뷰 진행',
    icon: MessageSquare,
    color: 'text-purple-500'
  },
  {
    id: 'report',
    title: '보고서 작성',
    description: '종합 분석 보고서 생성',
    icon: FileText,
    color: 'text-orange-500'
  },
  {
    id: 'feedback',
    title: '피드백 검토',
    description: '보고서 검토 및 개선',
    icon: Sparkles,
    color: 'text-yellow-500'
  },
  {
    id: 'completed',
    title: '완료',
    description: '연구 완료',
    icon: CheckCircle,
    color: 'text-green-600'
  }
];

const activityMessages = {
  analyzing_topic: {
    icon: Search,
    title: '주제 분석 중',
    description: '연구 주제 분석 및 전문 분야 식별',
    color: 'text-blue-500'
  },
  creating_profiles: {
    icon: Brain,
    title: '전문가 프로필 생성',
    description: '분야별 전문가 배경 및 프로필 생성',
    color: 'text-blue-500'
  },
  generating_analysts: {
    icon: Brain,
    title: '전문가 생성 중',
    description: '주제에 적합한 전문가 프로필 생성',
    color: 'text-blue-500'
  },
  analysts_created: {
    icon: Users,
    title: '전문가 팀 구성 완료',
    description: '분야별 전문가 배치 완료',
    color: 'text-green-500'
  },
  preparing_questions: {
    icon: MessageSquare,
    title: '질문 준비 중',
    description: '맞춤형 인터뷰 질문 생성',
    color: 'text-purple-500'
  },
  starting_interviews: {
    icon: MessageSquare,
    title: '인터뷰 시작',
    description: '전문가들과 심층 대화 시작',
    color: 'text-purple-500'
  },
  parallel_interviews_started: {
    icon: Zap,
    title: '병렬 인터뷰 시작',
    description: '여러 전문가와 동시 인터뷰 진행',
    color: 'text-blue-500'
  },
  sequential_interviews_started: {
    icon: MessageSquare,
    title: '순차 인터뷰 시작',
    description: '전문가와 차례대로 인터뷰 진행',
    color: 'text-purple-500'
  },
  conducting_interview: {
    icon: MessageSquare,
    title: '인터뷰 진행 중',
    description: '전문가와 심층 대화 진행',
    color: 'text-purple-500'
  },
  interview_completed: {
    icon: CheckCircle,
    title: '인터뷰 완료',
    description: '개별 전문가 인터뷰 완료',
    color: 'text-green-500'
  },
  interviews_completed: {
    icon: CheckCircle,
    title: '모든 인터뷰 완료',
    description: '모든 전문가 인터뷰 완료',
    color: 'text-green-500'
  },
  analyzing_interviews: {
    icon: Search,
    title: '인터뷰 분석 중',
    description: '수집된 데이터 분석 및 인사이트 추출',
    color: 'text-orange-500'
  },
  structuring_report: {
    icon: FileText,
    title: '보고서 구조 설계',
    description: '논리적 구조와 섹션별 내용 구성',
    color: 'text-orange-500'
  },
  writing_report: {
    icon: FileText,
    title: '보고서 작성 중',
    description: '인터뷰 결과를 종합 분석',
    color: 'text-orange-500'
  },
  reviewing_report: {
    icon: Sparkles,
    title: '보고서 검토 중',
    description: '보고서 내용 검토 및 품질 확인',
    color: 'text-yellow-500'
  },
  research_completed: {
    icon: Sparkles,
    title: '연구 완료',
    description: '모든 연구 과정 완료',
    color: 'text-green-600'
  }
};

export function EnhancedProgress({ 
  progress, 
  status, 
  currentStep = 'setup',
  agentActivity,
  sessionId,
  subActivity 
}: EnhancedProgressProps) {
  const [activityHistory, setActivityHistory] = useState<AgentActivity[]>([]);
  const [progressValue, setProgressValue] = useState(0);

  useEffect(() => {
    if (agentActivity && agentActivity.action && agentActivity.details) {
      setActivityHistory(prev => [...prev, agentActivity]);
    }
  }, [agentActivity]);

  useEffect(() => {
    const currentStepIndex = researchSteps.findIndex(step => step.id === currentStep);
    const newProgress = currentStepIndex >= 0 ? ((currentStepIndex + 1) / researchSteps.length) * 100 : 0;
    setProgressValue(newProgress);
  }, [currentStep]);


  const getStepStatus = (stepId: string) => {
    const stepIndex = researchSteps.findIndex(s => s.id === stepId);
    const currentIndex = researchSteps.findIndex(s => s.id === currentStep);
    
    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'current';
    return 'pending';
  };


  return (
    <div className="space-y-6">
      {/* 전체 진행률 카드 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              연구 진행률
            </div>
            <Badge className={cn("text-white", getStatusColor(status))}>
              {status === 'running' ? '진행 중' : 
               status === 'completed' ? '완료' : 
               status === 'error' ? '오류' : '대기'}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>전체 진행률</span>
            <span>{Math.round(progressValue)}%</span>
          </div>
          <Progress value={progressValue} className="h-3" />
          
          {/* 현재 활동 */}
          <div className="flex items-center gap-3 p-4 bg-muted/30 rounded-lg">
            {status === 'running' && (
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
            )}
            <div className="flex-1">
              <p className="text-sm font-medium">{progress}</p>
              {subActivity && (
                <p className="text-xs text-blue-600 mt-1 font-medium">
                  🔍 {subActivity}
                </p>
              )}
              {sessionId && (
                <p className="text-xs text-muted-foreground mt-1">
                  세션: {sessionId}
                </p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 실시간 활동 추적 - Perplexity 스타일 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5 text-primary" />
            실시간 연구 활동
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-64">
            <div className="space-y-3">
              {activityHistory.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  <Circle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>활동 기록이 없습니다</p>
                </div>
              ) : (
                activityHistory.map((activity, index) => {
                  const activityConfig = activityMessages[activity.action as keyof typeof activityMessages];
                  if (!activityConfig) {
                    console.warn(`Unknown activity action: ${activity.action}`);
                    return null;
                  }
                  
                  const Icon = activityConfig.icon;
                  
                  return (
                    <div key={index} className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors">
                      <div className={cn("flex-shrink-0 mt-1", activityConfig.color)}>
                        <Icon className="h-4 w-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="text-sm font-medium">{activityConfig.title}</p>
                          <Badge variant="outline" className="text-xs">
                            {formatTime(activity.timestamp)}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">
                          {activity.details}
                        </p>
                        
                        {/* 현재 진행 중인 전문가 표시 */}
                        {activity.current_analyst && (
                          <div className="flex items-center gap-2 text-xs bg-blue-50 border border-blue-200 rounded px-2 py-1 mt-2">
                            <Users className="h-3 w-3 text-blue-500" />
                            <span className="font-medium text-blue-700">{activity.current_analyst.name}</span>
                            <span className="text-blue-400">•</span>
                            <span className="text-blue-600">{activity.current_analyst.role}</span>
                            {activity.progress && (
                              <>
                                <span className="text-blue-400">•</span>
                                <span className="text-blue-600 font-medium">{activity.progress}</span>
                              </>
                            )}
                          </div>
                        )}
                        
                        {/* 완료된 전문가 표시 */}
                        {activity.completed_analyst && (
                          <div className="flex items-center gap-2 text-xs bg-green-50 border border-green-200 rounded px-2 py-1 mt-2">
                            <CheckCircle className="h-3 w-3 text-green-500" />
                            <span className="font-medium text-green-700">{activity.completed_analyst.name}</span>
                            <span className="text-green-400">•</span>
                            <span className="text-green-600">{activity.completed_analyst.role}</span>
                          </div>
                        )}
                        
                        {/* 전문가 목록 표시 */}
                        {activity.analysts && activity.analysts.length > 0 && (
                          <div className="space-y-1 mt-2">
                            <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                              <Users className="h-3 w-3" />
                              <span>전문가 {activity.analysts.length}명</span>
                              {activity.action === 'parallel_interviews_started' && (
                                <div className="flex items-center gap-1 text-blue-500">
                                  <Zap className="h-3 w-3" />
                                  <span>병렬 처리</span>
                                </div>
                              )}
                              {activity.action === 'sequential_interviews_started' && (
                                <div className="flex items-center gap-1 text-purple-500">
                                  <ChevronRight className="h-3 w-3" />
                                  <span>순차 처리</span>
                                </div>
                              )}
                            </div>
                            {activity.analysts.map((analyst, i) => (
                              <div key={i} className="flex items-center gap-2 text-xs bg-muted/30 rounded px-2 py-1">
                                <Users className="h-3 w-3 text-muted-foreground" />
                                <span className="font-medium">{analyst.name}</span>
                                <span className="text-muted-foreground">•</span>
                                <span className="text-muted-foreground">{analyst.role}</span>
                              </div>
                            ))}
                          </div>
                        )}
                        
                        {/* 인터뷰 수 표시 */}
                        {activity.interview_count && (
                          <div className="flex items-center gap-2 text-xs text-muted-foreground mt-2">
                            <MessageSquare className="h-3 w-3" />
                            <span>{activity.interview_count}개 인터뷰 완료</span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* 단계별 진행 상황 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-primary" />
            연구 단계
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {researchSteps.map((step, index) => {
              const stepStatus = getStepStatus(step.id);
              const Icon = step.icon;
              
              return (
                <div key={step.id} className="flex items-center gap-4 relative">
                  <div className={cn(
                    "flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all",
                    stepStatus === 'completed' ? 'bg-green-100 border-green-500' :
                    stepStatus === 'current' ? 'bg-primary/10 border-primary' :
                    'bg-muted border-muted'
                  )}>
                    {stepStatus === 'completed' ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : stepStatus === 'current' ? (
                      <Icon className={cn("h-5 w-5", step.color)} />
                    ) : (
                      <Icon className="h-5 w-5 text-muted-foreground" />
                    )}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className={cn(
                        "font-medium",
                        stepStatus === 'current' ? 'text-primary' :
                        stepStatus === 'completed' ? 'text-green-600' :
                        'text-muted-foreground'
                      )}>
                        {step.title}
                      </h4>
                      {stepStatus === 'current' && (
                        <Badge variant="outline" className="text-xs animate-pulse">
                          진행 중
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {step.description}
                    </p>
                  </div>
                  
                  {stepStatus === 'current' && (
                    <ChevronRight className="h-4 w-4 text-primary animate-pulse" />
                  )}
                  
                  {/* 연결선 */}
                  {index < researchSteps.length - 1 && (
                    <div className={cn(
                      "absolute left-5 top-10 w-0.5 h-6 transition-colors",
                      stepStatus === 'completed' ? 'bg-green-500' : 'bg-muted'
                    )} />
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}