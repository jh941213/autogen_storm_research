'use client';

import { Header } from '@/components/layout/header';
import { AuroraText } from '@/components/ui/aurora-text';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  GitBranch, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Sparkles,
  Search,
  Database,
  Users,
  MessageSquare,
  Zap,
  Target,
  Layers,
  Globe,
  Brain,
  ArrowRight,
  Calendar,
  Star,
  Rocket
} from 'lucide-react';

export default function VersionsPage() {
  const currentVersion = "1.0.0";
  const releaseDate = "2025-07-18";

  const upcomingFeatures = [
    {
      title: "사용자 토픽 심층 분해",
      description: "입력된 토픽을 다양한 하위 토픽으로 자동 분해하여 더 포괄적인 연구 수행",
      icon: <Target className="h-5 w-5" />,
      status: "planned",
      priority: "high"
    },
    {
      title: "다양한 관점 심층 서치",
      description: "분해된 토픽별로 다양한 관점에서 심층적인 정보 검색 및 분석",
      icon: <Search className="h-5 w-5" />,
      status: "planned",
      priority: "high"
    },
    {
      title: "구글 서치 툴 통합",
      description: "Google Search API 통합으로 실시간 웹 검색 기능 강화",
      icon: <Globe className="h-5 w-5" />,
      status: "in-development",
      priority: "medium"
    },
    {
      title: "다양한 검색엔진 추가",
      description: "Bing, DuckDuckGo, Scholar 등 다양한 검색엔진 지원으로 정보 다양성 확보",
      icon: <Layers className="h-5 w-5" />,
      status: "planned",
      priority: "medium"
    },
    {
      title: "사용자 데이터 기반 RAG 분석",
      description: "개인화된 데이터베이스 구축 및 RAG 시스템으로 맞춤형 분석 제공",
      icon: <Database className="h-5 w-5" />,
      status: "planned",
      priority: "high"
    },
    {
      title: "실시간 협업 시스템",
      description: "여러 사용자가 동시에 연구에 참여할 수 있는 협업 플랫폼",
      icon: <Users className="h-5 w-5" />,
      status: "research",
      priority: "low"
    }
  ];

  const currentFeatures = [
    {
      title: "AutoGen 멀티 에이전트 시스템",
      description: "전문가 에이전트들이 협력하여 심층 연구 수행",
      icon: <Brain className="h-5 w-5" />
    },
    {
      title: "대화형 인터뷰 시스템",
      description: "AI 전문가들 간의 자연스러운 대화를 통한 지식 탐구",
      icon: <MessageSquare className="h-5 w-5" />
    },
    {
      title: "실시간 진행 상황 모니터링",
      description: "WebSocket을 통한 실시간 연구 진행 상황 추적",
      icon: <Zap className="h-5 w-5" />
    },
    {
      title: "사용자 피드백 루프",
      description: "보고서 검토 및 개선 요청을 통한 품질 향상",
      icon: <CheckCircle className="h-5 w-5" />
    },
    {
      title: "다양한 검색 도구 통합",
      description: "Wikipedia, ArXiv, 웹검색 등 다양한 정보원 활용",
      icon: <Search className="h-5 w-5" />
    },
    {
      title: "Langfuse 추적 시스템",
      description: "모든 AI 상호작용 모니터링 및 성능 분석",
      icon: <Target className="h-5 w-5" />
    }
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'planned':
        return <Badge className="bg-blue-100 text-blue-800">계획됨</Badge>;
      case 'in-development':
        return <Badge className="bg-yellow-100 text-yellow-800">개발 중</Badge>;
      case 'research':
        return <Badge className="bg-purple-100 text-purple-800">연구 중</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <Star className="h-4 w-4 text-red-500" />;
      case 'medium':
        return <Star className="h-4 w-4 text-yellow-500" />;
      case 'low':
        return <Star className="h-4 w-4 text-gray-400" />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-background/95">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* 헤더 */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold">
              <AuroraText 
                text="버전 및 업데이트 계획"
                speed={80}
                showCursor={false}
              />
            </h1>
            <p className="text-xl text-muted-foreground">
              현재 버전 정보와 향후 업데이트 예정 사항
            </p>
          </div>

          {/* 현재 버전 정보 */}
          <Card className="border-2 border-green-200 bg-green-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                현재 버전 {currentVersion}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <Calendar className="h-5 w-5 text-green-600" />
                    <span className="font-medium">릴리스 날짜: {releaseDate}</span>
                  </div>
                  <h3 className="font-semibold mb-3">주요 기능</h3>
                  <div className="space-y-3">
                    {currentFeatures.map((feature, index) => (
                      <div key={index} className="flex items-start gap-3">
                        <div className="bg-green-100 p-2 rounded-full">
                          {feature.icon}
                        </div>
                        <div>
                          <h4 className="font-medium text-sm">{feature.title}</h4>
                          <p className="text-xs text-muted-foreground">{feature.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="bg-white p-6 rounded-lg border">
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-green-600" />
                    현재 버전 특징
                  </h3>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      완전 자동화된 연구 워크플로우
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      실시간 사용자 상호작용
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      고품질 보고서 생성
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      다중 AI 모델 지원
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      성능 모니터링 시스템
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 업데이트 예정 사항 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Rocket className="h-5 w-5 text-blue-600" />
                업데이트 예정 사항
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {upcomingFeatures.map((feature, index) => (
                  <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        <div className="bg-blue-100 p-2 rounded-full">
                          {feature.icon}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="font-semibold">{feature.title}</h3>
                            {getPriorityIcon(feature.priority)}
                          </div>
                          <p className="text-sm text-muted-foreground mb-3">
                            {feature.description}
                          </p>
                          <div className="flex items-center gap-2">
                            {getStatusBadge(feature.status)}
                            <span className="text-xs text-muted-foreground">
                              우선순위: {feature.priority === 'high' ? '높음' : feature.priority === 'medium' ? '보통' : '낮음'}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 로드맵 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GitBranch className="h-5 w-5 text-purple-600" />
                개발 로드맵
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex items-center gap-4">
                  <div className="bg-green-100 p-3 rounded-full">
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium">v1.0.0 - 기본 시스템 완성</h4>
                    <p className="text-sm text-muted-foreground">AutoGen 기반 멀티 에이전트 연구 시스템</p>
                    <div className="text-xs text-green-600 mt-1">✓ 완료됨</div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="bg-blue-100 p-3 rounded-full">
                    <Clock className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium">v1.1.0 - 향상된 검색 시스템</h4>
                    <p className="text-sm text-muted-foreground">토픽 분해 및 다양한 검색엔진 통합</p>
                    <div className="text-xs text-blue-600 mt-1">2025 Q3 예정</div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="bg-purple-100 p-3 rounded-full">
                    <AlertCircle className="h-6 w-6 text-purple-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium">v1.2.0 - 개인화 시스템</h4>
                    <p className="text-sm text-muted-foreground">사용자 데이터 기반 RAG 분석 시스템</p>
                    <div className="text-xs text-purple-600 mt-1">2025 Q4 예정</div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="bg-gray-100 p-3 rounded-full">
                    <Users className="h-6 w-6 text-gray-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium">v2.0.0 - 협업 플랫폼</h4>
                    <p className="text-sm text-muted-foreground">실시간 협업 및 팀 연구 기능</p>
                    <div className="text-xs text-gray-600 mt-1">2026 Q1 예정</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 기술 스택 업데이트 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Layers className="h-5 w-5 text-orange-600" />
                기술 스택 업데이트 계획
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-3">백엔드 강화</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <ArrowRight className="h-4 w-4 text-blue-500" />
                      Elasticsearch 통합 (고급 검색)
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="h-4 w-4 text-blue-500" />
                      Redis 캐싱 시스템 도입
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="h-4 w-4 text-blue-500" />
                      PostgreSQL 벡터 데이터베이스
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="h-4 w-4 text-blue-500" />
                      API 버전 관리 시스템
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium mb-3">프론트엔드 개선</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <ArrowRight className="h-4 w-4 text-green-500" />
                      PWA 지원 (오프라인 모드)
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="h-4 w-4 text-green-500" />
                      고급 시각화 라이브러리
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="h-4 w-4 text-green-500" />
                      다크 모드 지원
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="h-4 w-4 text-green-500" />
                      모바일 최적화 강화
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}