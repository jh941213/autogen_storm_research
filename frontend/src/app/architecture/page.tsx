'use client';

import { Header } from '@/components/layout/header';
import { AuroraText } from '@/components/ui/aurora-text';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  Users, 
  MessageSquare, 
  FileText, 
  Database,
  Network,
  Zap,
  Search,
  Globe,
  Server,
  ArrowRight,
  Sparkles,
  Bot,
  Target,
  CheckCircle
} from 'lucide-react';

export default function ArchitecturePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-background/95">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* 헤더 */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold">
              <AuroraText 
                text="AutoGen DeepResearch Architecture"
                speed={80}
                showCursor={false}
              />
            </h1>
            <p className="text-xl text-muted-foreground">
              AI-Powered Multi-Agent Research System
            </p>
          </div>

          {/* 시스템 개요 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Network className="h-5 w-5" />
                System Overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center space-y-2">
                  <div className="bg-blue-100 p-4 rounded-full w-16 h-16 mx-auto flex items-center justify-center">
                    <Globe className="h-8 w-8 text-blue-600" />
                  </div>
                  <h3 className="font-semibold">Frontend</h3>
                  <p className="text-sm text-muted-foreground">Next.js + TypeScript</p>
                </div>
                <div className="text-center space-y-2">
                  <div className="bg-green-100 p-4 rounded-full w-16 h-16 mx-auto flex items-center justify-center">
                    <Server className="h-8 w-8 text-green-600" />
                  </div>
                  <h3 className="font-semibold">Backend</h3>
                  <p className="text-sm text-muted-foreground">FastAPI + Python</p>
                </div>
                <div className="text-center space-y-2">
                  <div className="bg-purple-100 p-4 rounded-full w-16 h-16 mx-auto flex items-center justify-center">
                    <Brain className="h-8 w-8 text-purple-600" />
                  </div>
                  <h3 className="font-semibold">AI Agents</h3>
                  <p className="text-sm text-muted-foreground">AutoGen + STORM</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 시스템 아키텍처 다이어그램 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Server className="h-5 w-5" />
                System Architecture Diagram
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-8">
                {/* Frontend Layer */}
                <div className="border-2 border-blue-200 bg-blue-50 p-6 rounded-lg">
                  <h3 className="font-semibold text-blue-800 mb-4 flex items-center gap-2">
                    <Globe className="h-5 w-5" />
                    Frontend Layer (Next.js)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white p-4 rounded border">
                      <h4 className="font-medium text-sm">User Interface</h4>
                      <ul className="text-xs text-muted-foreground mt-2 space-y-1">
                        <li>• Research Configuration</li>
                        <li>• Progress Monitoring</li>
                        <li>• Result Visualization</li>
                      </ul>
                    </div>
                    <div className="bg-white p-4 rounded border">
                      <h4 className="font-medium text-sm">State Management</h4>
                      <ul className="text-xs text-muted-foreground mt-2 space-y-1">
                        <li>• Zustand Store</li>
                        <li>• WebSocket Client</li>
                        <li>• Real-time Updates</li>
                      </ul>
                    </div>
                    <div className="bg-white p-4 rounded border">
                      <h4 className="font-medium text-sm">Interactive Dialogs</h4>
                      <ul className="text-xs text-muted-foreground mt-2 space-y-1">
                        <li>• Analyst Count Selection</li>
                        <li>• Report Approval</li>
                        <li>• Feedback Collection</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Connection Arrow */}
                <div className="flex justify-center items-center space-x-4">
                  <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
                  <div className="bg-gray-100 p-2 rounded-full">
                    <ArrowRight className="h-4 w-4 text-gray-600" />
                  </div>
                  <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
                </div>

                {/* API Layer */}
                <div className="border-2 border-green-200 bg-green-50 p-6 rounded-lg">
                  <h3 className="font-semibold text-green-800 mb-4 flex items-center gap-2">
                    <Network className="h-5 w-5" />
                    API Layer (FastAPI)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-white p-4 rounded border">
                      <h4 className="font-medium text-sm">REST Endpoints</h4>
                      <ul className="text-xs text-muted-foreground mt-2 space-y-1">
                        <li>• POST /api/research/start</li>
                        <li>• GET /api/research/status</li>
                        <li>• GET /api/research/result</li>
                      </ul>
                    </div>
                    <div className="bg-white p-4 rounded border">
                      <h4 className="font-medium text-sm">WebSocket</h4>
                      <ul className="text-xs text-muted-foreground mt-2 space-y-1">
                        <li>• Real-time progress updates</li>
                        <li>• Interactive user prompts</li>
                        <li>• Agent activity streaming</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Connection Arrow */}
                <div className="flex justify-center items-center space-x-4">
                  <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
                  <div className="bg-gray-100 p-2 rounded-full">
                    <ArrowRight className="h-4 w-4 text-gray-600" />
                  </div>
                  <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
                </div>

                {/* Orchestration Layer */}
                <div className="border-2 border-purple-200 bg-purple-50 p-6 rounded-lg">
                  <h3 className="font-semibold text-purple-800 mb-4 flex items-center gap-2">
                    <Zap className="h-5 w-5" />
                    Orchestration Layer
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white p-4 rounded border">
                      <h4 className="font-medium text-sm">Session Manager</h4>
                      <ul className="text-xs text-muted-foreground mt-2 space-y-1">
                        <li>• Session lifecycle</li>
                        <li>• State management</li>
                        <li>• WebSocket connections</li>
                      </ul>
                    </div>
                    <div className="bg-white p-4 rounded border">
                      <h4 className="font-medium text-sm">Research Coordinator</h4>
                      <ul className="text-xs text-muted-foreground mt-2 space-y-1">
                        <li>• Agent coordination</li>
                        <li>• Workflow management</li>
                        <li>• Progress tracking</li>
                      </ul>
                    </div>
                    <div className="bg-white p-4 rounded border">
                      <h4 className="font-medium text-sm">Feedback Handler</h4>
                      <ul className="text-xs text-muted-foreground mt-2 space-y-1">
                        <li>• User interaction</li>
                        <li>• Response processing</li>
                        <li>• Loop management</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* AutoGen Multi-Agent Framework */}
                <div className="border-2 border-orange-200 bg-orange-50 p-6 rounded-lg">
                  <h3 className="font-semibold text-orange-800 mb-4 flex items-center gap-2">
                    <Bot className="h-5 w-5" />
                    AutoGen Multi-Agent Framework
                  </h3>
                  <div className="space-y-6">
                    {/* AutoGen Core Components */}
                    <div className="bg-white p-4 rounded border">
                      <h4 className="font-medium text-sm mb-3">AutoGen Core Components</h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div className="bg-blue-50 p-3 rounded text-center">
                          <div className="text-xs font-medium text-blue-700">RoundRobinGroupChat</div>
                          <div className="text-xs text-blue-600 mt-1">순차적 대화 관리</div>
                        </div>
                        <div className="bg-green-50 p-3 rounded text-center">
                          <div className="text-xs font-medium text-green-700">AssistantAgent</div>
                          <div className="text-xs text-green-600 mt-1">전문가 에이전트</div>
                        </div>
                        <div className="bg-purple-50 p-3 rounded text-center">
                          <div className="text-xs font-medium text-purple-700">FunctionTool</div>
                          <div className="text-xs text-purple-600 mt-1">검색 도구 통합</div>
                        </div>
                      </div>
                    </div>

                    {/* Agent Interaction Flow */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="bg-white p-4 rounded border text-center">
                        <div className="bg-blue-100 p-3 rounded-full w-12 h-12 mx-auto mb-2 flex items-center justify-center">
                          <Search className="h-6 w-6 text-blue-600" />
                        </div>
                        <h4 className="font-medium text-sm">Analyst Generator</h4>
                        <p className="text-xs text-muted-foreground mt-1">다양한 전문가 생성</p>
                        <div className="text-xs text-blue-600 mt-1">AssistantAgent</div>
                      </div>
                      <div className="bg-white p-4 rounded border text-center">
                        <div className="bg-green-100 p-3 rounded-full w-12 h-12 mx-auto mb-2 flex items-center justify-center">
                          <Users className="h-6 w-6 text-green-600" />
                        </div>
                        <h4 className="font-medium text-sm">Expert Agent</h4>
                        <p className="text-xs text-muted-foreground mt-1">검색 도구 활용</p>
                        <div className="text-xs text-green-600 mt-1">+ FunctionTool</div>
                      </div>
                      <div className="bg-white p-4 rounded border text-center">
                        <div className="bg-purple-100 p-3 rounded-full w-12 h-12 mx-auto mb-2 flex items-center justify-center">
                          <MessageSquare className="h-6 w-6 text-purple-600" />
                        </div>
                        <h4 className="font-medium text-sm">Interviewer Agent</h4>
                        <p className="text-xs text-muted-foreground mt-1">인터뷰 진행</p>
                        <div className="text-xs text-purple-600 mt-1">RoundRobinGroupChat</div>
                      </div>
                      <div className="bg-white p-4 rounded border text-center">
                        <div className="bg-orange-100 p-3 rounded-full w-12 h-12 mx-auto mb-2 flex items-center justify-center">
                          <FileText className="h-6 w-6 text-orange-600" />
                        </div>
                        <h4 className="font-medium text-sm">Report Writer</h4>
                        <p className="text-xs text-muted-foreground mt-1">보고서 작성</p>
                        <div className="text-xs text-orange-600 mt-1">AssistantAgent</div>
                      </div>
                    </div>

                    {/* Termination Conditions */}
                    <div className="bg-white p-4 rounded border">
                      <h4 className="font-medium text-sm mb-3">Termination Conditions</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div className="bg-yellow-50 p-3 rounded">
                          <div className="text-xs font-medium text-yellow-700">TextMentionTermination</div>
                          <div className="text-xs text-yellow-600 mt-1">&quot;감사합니다!&quot; 키워드로 자연스러운 종료</div>
                        </div>
                        <div className="bg-red-50 p-3 rounded">
                          <div className="text-xs font-medium text-red-700">MaxMessageTermination</div>
                          <div className="text-xs text-red-600 mt-1">최대 메시지 수로 무한 대화 방지</div>
                        </div>
                      </div>
                    </div>

                    {/* Feedback Loop with Expert +1 */}
                    <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 p-4 rounded-lg">
                      <h4 className="font-medium text-sm text-yellow-800 mb-2 flex items-center gap-2">
                        <Sparkles className="h-4 w-4" />
                        Interactive Feedback Loop
                      </h4>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="text-xs text-yellow-700">
                            사용자 피드백 → 보고서 개선 → 재검토 → 최종 승인
                          </div>
                          <div className="flex space-x-2">
                            <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                            <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                            <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                          </div>
                        </div>
                        <div className="bg-white p-3 rounded border border-yellow-300">
                          <div className="text-xs font-medium text-yellow-800 mb-1">Expert +1 Feature</div>
                          <div className="text-xs text-yellow-700">
                            사용자 피드백 시 전문가 에이전트 추가 생성으로 더 풍부한 관점 제공
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Model Layer */}
                <div className="border-2 border-red-200 bg-red-50 p-6 rounded-lg">
                  <h3 className="font-semibold text-red-800 mb-4 flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    Model Integration Layer
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white p-4 rounded border text-center">
                      <div className="flex items-center justify-center mb-3">
                        <img 
                          src="https://upload.wikimedia.org/wikipedia/commons/4/4d/OpenAI_Logo.svg" 
                          alt="OpenAI Logo" 
                          className="w-12 h-12 object-contain"
                        />
                      </div>
                      <h4 className="font-medium text-sm">OpenAI</h4>
                    </div>
                    <div className="bg-white p-4 rounded border text-center">
                      <div className="flex items-center justify-center mb-3">
                        <img 
                          src="https://upload.wikimedia.org/wikipedia/commons/f/fa/Microsoft_Azure.svg" 
                          alt="Azure Logo" 
                          className="w-12 h-12 object-contain"
                        />
                      </div>
                      <h4 className="font-medium text-sm">Azure OpenAI</h4>
                    </div>
                    <div className="bg-white p-4 rounded border text-center">
                      <div className="flex items-center justify-center mb-3">
                        <img 
                          src="https://upload.wikimedia.org/wikipedia/commons/7/78/Anthropic_logo.svg" 
                          alt="Anthropic Logo" 
                          className="w-12 h-12 object-contain"
                        />
                      </div>
                      <h4 className="font-medium text-sm">Anthropic</h4>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 에이전트 설명 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Analyst Generator */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="h-5 w-5 text-blue-500" />
                  Analyst Generator (AutoGen)
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Badge variant="outline" className="bg-blue-50">AssistantAgent</Badge>
                <div className="space-y-2">
                  <h4 className="font-medium">주요 역할</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• 다양한 관점의 전문가 페르소나 생성</li>
                    <li>• 분야별 특성을 고려한 전문가 배치</li>
                    <li>• 주제에 맞는 전문가 수 결정</li>
                    <li>• 전문가 배경 및 전문성 정의</li>
                  </ul>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium">AutoGen 구현</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• 단일 AssistantAgent로 구현</li>
                    <li>• 특화된 시스템 메시지 활용</li>
                    <li>• 동적 전문가 생성 로직</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Expert Agent */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-green-500" />
                  Expert Agent (AutoGen)
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Badge variant="outline" className="bg-green-50">AssistantAgent + FunctionTool</Badge>
                <div className="space-y-2">
                  <h4 className="font-medium">주요 역할</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• 검색 도구를 활용한 정보 수집</li>
                    <li>• 웹검색, 위키피디아, ArXiv 통합</li>
                    <li>• 전문가 질문에 근거 기반 답변</li>
                    <li>• 실시간 정보 업데이트</li>
                  </ul>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium">AutoGen 구현</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• FunctionTool로 검색 기능 통합</li>
                    <li>• RoundRobinGroupChat 참여</li>
                    <li>• 동적 도구 선택 및 실행</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Interviewer Agent */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-purple-500" />
                  Interviewer Agent (AutoGen)
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Badge variant="outline" className="bg-purple-50">AssistantAgent + RoundRobinGroupChat</Badge>
                <div className="space-y-2">
                  <h4 className="font-medium">주요 역할</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• 전문가 관점에서 질문 생성</li>
                    <li>• Expert Agent와 대화 진행</li>
                    <li>• 심층 탐구 및 추가 질문</li>
                    <li>• 인터뷰 완료 시점 판단</li>
                  </ul>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium">AutoGen 구현</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• 전문가별 동적 AssistantAgent 생성</li>
                    <li>• RoundRobinGroupChat으로 대화 관리</li>
                    <li>• TextMentionTermination 조건 활용</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Report Writer */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-orange-500" />
                  Report Writer (AutoGen)
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Badge variant="outline" className="bg-orange-50">AssistantAgent + Feedback Loop</Badge>
                <div className="space-y-2">
                  <h4 className="font-medium">주요 역할</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• 인터뷰 결과 종합 분석</li>
                    <li>• 구조화된 보고서 생성</li>
                    <li>• 사용자 피드백 반영</li>
                    <li>• 보고서 버전 관리</li>
                  </ul>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium">AutoGen 구현</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• AssistantAgent로 보고서 생성</li>
                    <li>• 피드백 기반 재작성 기능</li>
                    <li>• 전문가 +1 추가 시 보강</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 워크플로우 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Research Workflow with Feedback Loop
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex items-center gap-4">
                  <div className="bg-blue-100 p-3 rounded-full">
                    <Search className="h-5 w-5 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium">1. Topic Analysis</h4>
                    <p className="text-sm text-muted-foreground">Topic Curator가 연구 주제를 분석하고 전문가 프로필을 생성합니다.</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>

                <div className="flex items-center gap-4">
                  <div className="bg-green-100 p-3 rounded-full">
                    <Users className="h-5 w-5 text-green-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium">2. Expert Generation</h4>
                    <p className="text-sm text-muted-foreground">사용자가 선택한 수만큼 Perspective Agents가 생성됩니다.</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>

                <div className="flex items-center gap-4">
                  <div className="bg-purple-100 p-3 rounded-full">
                    <MessageSquare className="h-5 w-5 text-purple-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium">3. Interview Process</h4>
                    <p className="text-sm text-muted-foreground">Question Asker가 각 전문가와 심층 인터뷰를 수행합니다 (병렬/순차).</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>

                <div className="flex items-center gap-4">
                  <div className="bg-orange-100 p-3 rounded-full">
                    <FileText className="h-5 w-5 text-orange-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium">4. Report Generation</h4>
                    <p className="text-sm text-muted-foreground">Report Writer가 수집된 정보를 종합하여 초기 보고서를 작성합니다.</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>

                <div className="flex items-center gap-4">
                  <div className="bg-indigo-100 p-3 rounded-full">
                    <Database className="h-5 w-5 text-indigo-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium">5. Langfuse Tracing & Monitoring</h4>
                    <p className="text-sm text-muted-foreground">모든 AI 상호작용을 실시간으로 추적하고 성능 메트릭을 모니터링합니다.</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>

                <div className="flex items-center gap-4">
                  <div className="bg-yellow-100 p-3 rounded-full">
                    <Sparkles className="h-5 w-5 text-yellow-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium">6. User Review & Feedback</h4>
                    <p className="text-sm text-muted-foreground">사용자가 보고서를 검토하고 피드백을 제공합니다.</p>
                  </div>
                </div>

                {/* Feedback Loop Visualization */}
                <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 p-6 rounded-lg">
                  <h4 className="font-medium text-yellow-800 mb-4 flex items-center gap-2">
                    <Sparkles className="h-5 w-5" />
                    Interactive Feedback Loop
                  </h4>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="bg-white p-3 rounded-lg border border-yellow-300 text-center flex-1 mx-2">
                        <div className="text-sm font-medium text-yellow-800">보고서 미리보기</div>
                        <div className="text-xs text-yellow-600 mt-1">초기 보고서 생성</div>
                      </div>
                      <ArrowRight className="h-4 w-4 text-yellow-600" />
                      <div className="bg-white p-3 rounded-lg border border-yellow-300 text-center flex-1 mx-2">
                        <div className="text-sm font-medium text-yellow-800">사용자 선택</div>
                        <div className="text-xs text-yellow-600 mt-1">승인 / 수정 / 전체보기</div>
                      </div>
                    </div>
                    <div className="flex items-center justify-center">
                      <div className="w-full h-px bg-yellow-300"></div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="bg-white p-3 rounded-lg border border-yellow-300 text-center flex-1 mx-2">
                        <div className="text-sm font-medium text-yellow-800">피드백 수집</div>
                        <div className="text-xs text-yellow-600 mt-1">구체적 개선 요청</div>
                      </div>
                      <ArrowRight className="h-4 w-4 text-yellow-600" />
                      <div className="bg-white p-3 rounded-lg border border-yellow-300 text-center flex-1 mx-2">
                        <div className="text-sm font-medium text-yellow-800">보고서 개선</div>
                        <div className="text-xs text-yellow-600 mt-1">AI 에이전트 재작업</div>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 text-center">
                    <div className="inline-flex items-center gap-2 text-sm text-yellow-700">
                      <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                      <span>사용자 만족까지 반복</span>
                      <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="bg-green-100 p-3 rounded-full">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium">7. Final Approval</h4>
                    <p className="text-sm text-muted-foreground">최종 승인 후 완성된 보고서를 제공합니다.</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}