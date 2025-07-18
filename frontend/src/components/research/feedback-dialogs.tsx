'use client';

import { useState } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle, 
  DialogFooter 
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Users, 
  FileText, 
  MessageSquare, 
  CheckCircle, 
  RefreshCw, 
  Eye,
  Loader2 
} from 'lucide-react';
import { 
  AnalystCountRequest, 
  ReportApprovalRequest 
} from '@/types';

interface AnalystCountDialogProps {
  isOpen: boolean;
  data: AnalystCountRequest;
  onSubmit: (count: number) => void;
  onClose: () => void;
}

export function AnalystCountDialog({ isOpen, data, onSubmit, onClose }: AnalystCountDialogProps) {
  const [selectedCount, setSelectedCount] = useState(data.default_count);

  const handleSubmit = () => {
    onSubmit(selectedCount);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Users className="h-5 w-5 text-primary" />
            분석가 수 선택
          </DialogTitle>
          <DialogDescription>
            {data.message}
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">분석가 수</label>
            <Input
              type="number"
              min="1"
              max="10"
              value={selectedCount}
              onChange={(e) => setSelectedCount(Number(e.target.value))}
              className="text-center text-lg"
            />
          </div>
          
          <div className="grid grid-cols-5 gap-2">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((count) => (
              <Button
                key={count}
                variant={selectedCount === count ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCount(count)}
              >
                {count}
              </Button>
            ))}
          </div>
          
          <div className="text-sm text-muted-foreground">
            <p>• 더 많은 분석가 = 더 다양한 관점의 분석</p>
            <p>• 권장: 3-5명 (균형잡힌 속도와 품질)</p>
            <p>• 최대 10명까지 선택 가능</p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            취소
          </Button>
          <Button onClick={handleSubmit}>
            <Users className="mr-2 h-4 w-4" />
            {selectedCount}명으로 시작
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

interface ReportApprovalDialogProps {
  isOpen: boolean;
  data: ReportApprovalRequest;
  onApprove: () => void;
  onRewrite: (feedback?: string) => void;
  onViewFull: () => void;
  onClose: () => void;
}

export function ReportApprovalDialog({ 
  isOpen, 
  data, 
  onApprove, 
  onRewrite, 
  onViewFull, 
  onClose 
}: ReportApprovalDialogProps) {
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleRewriteWithFeedback = async () => {
    if (!feedback.trim()) return;
    
    setIsSubmitting(true);
    try {
      await onRewrite(feedback);
      setFeedback('');
      setShowFeedback(false);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleApprove = () => {
    onApprove();
    onClose();
  };

  const handleViewFull = () => {
    onViewFull();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            보고서 검토 (버전 {data.preview?.version || 1})
          </DialogTitle>
          <DialogDescription>
            작성된 보고서를 검토하고 승인하거나 피드백을 제공하세요.
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="max-h-96">
          <div className="space-y-4">
            {/* 보고서 미리보기 */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="font-medium">주제: {data.topic}</h3>
                <Badge variant="outline">
                  {data.preview?.total_length || 0}자
                </Badge>
              </div>
              
              <div className="space-y-3">
                <div className="p-3 bg-muted/50 rounded-lg">
                  <h4 className="font-medium text-sm mb-2">📝 서론</h4>
                  <p className="text-sm text-muted-foreground">
                    {data.preview?.introduction_preview || ''}...
                  </p>
                </div>
                
                <div className="p-3 bg-muted/50 rounded-lg">
                  <h4 className="font-medium text-sm mb-2">📊 본문</h4>
                  <p className="text-sm text-muted-foreground">
                    {data.preview?.main_content_preview || ''}...
                  </p>
                </div>
                
                <div className="p-3 bg-muted/50 rounded-lg">
                  <h4 className="font-medium text-sm mb-2">🎯 결론</h4>
                  <p className="text-sm text-muted-foreground">
                    {data.preview?.conclusion_preview || ''}...
                  </p>
                </div>
              </div>
            </div>

            {/* 피드백 입력 */}
            {showFeedback && (
              <div className="space-y-3 p-4 border rounded-lg">
                <h4 className="font-medium flex items-center gap-2">
                  <MessageSquare className="h-4 w-4" />
                  개선 요청사항
                </h4>
                <Textarea
                  placeholder="보고서 개선을 위한 구체적인 피드백을 입력하세요..."
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  className="min-h-20"
                />
                <div className="flex gap-2">
                  <Button
                    onClick={handleRewriteWithFeedback}
                    disabled={!feedback.trim() || isSubmitting}
                    className="flex-1"
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        재작성 중...
                      </>
                    ) : (
                      <>
                        <RefreshCw className="mr-2 h-4 w-4" />
                        피드백 반영하여 재작성
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowFeedback(false)}
                    disabled={isSubmitting}
                  >
                    취소
                  </Button>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        <DialogFooter className="flex-col sm:flex-row gap-2">
          <div className="flex gap-2 flex-1">
            <Button
              variant="outline"
              onClick={handleViewFull}
              className="flex-1"
            >
              <Eye className="mr-2 h-4 w-4" />
              전체 보기
            </Button>
            
            {!showFeedback && (
              <Button
                variant="outline"
                onClick={() => setShowFeedback(true)}
                className="flex-1"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                재작성 요청
              </Button>
            )}
          </div>
          
          <Button onClick={handleApprove} className="flex-1">
            <CheckCircle className="mr-2 h-4 w-4" />
            승인하기
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

interface FeedbackDialogProps {
  isOpen: boolean;
  onSubmit: (feedback: string) => void;
  onClose: () => void;
}

export function FeedbackDialog({ isOpen, onSubmit, onClose }: FeedbackDialogProps) {
  const [feedback, setFeedback] = useState('');

  const handleSubmit = () => {
    if (feedback.trim()) {
      onSubmit(feedback);
      setFeedback('');
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-primary" />
            피드백 제공
          </DialogTitle>
          <DialogDescription>
            보고서 개선을 위한 구체적인 피드백을 제공해주세요.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          <Textarea
            placeholder="예: 더 많은 데이터와 통계를 포함해주세요, 특정 측면을 더 자세히 다뤄주세요..."
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            className="min-h-24"
          />
          
          <div className="text-sm text-muted-foreground">
            <p>💡 효과적인 피드백 팁:</p>
            <ul className="list-disc ml-4 mt-1 space-y-1">
              <li>구체적이고 실행 가능한 요청</li>
              <li>추가하고 싶은 내용이나 관점</li>
              <li>개선이 필요한 부분의 명확한 지적</li>
            </ul>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            취소
          </Button>
          <Button onClick={handleSubmit} disabled={!feedback.trim()}>
            <MessageSquare className="mr-2 h-4 w-4" />
            피드백 제출
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

interface FullReportDialogProps {
  isOpen: boolean;
  report: ReportApprovalRequest['preview']['full_report'];
  onClose: () => void;
}

export function FullReportDialog({ isOpen, report, onClose }: FullReportDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-4xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            전체 보고서
          </DialogTitle>
        </DialogHeader>
        
        <ScrollArea className="max-h-[60vh]">
          <div className="space-y-6 text-sm">
            {report?.introduction && (
              <div>
                <h3 className="font-semibold text-lg mb-3">서론</h3>
                <div className="prose prose-sm max-w-none">
                  {report.introduction.split('\n').map((paragraph, index) => (
                    <p key={index} className="mb-2">{paragraph}</p>
                  ))}
                </div>
              </div>
            )}
            
            {report?.main_content && (
              <div>
                <h3 className="font-semibold text-lg mb-3">본문</h3>
                <div className="prose prose-sm max-w-none">
                  {report.main_content.split('\n').map((paragraph, index) => (
                    <p key={index} className="mb-2">{paragraph}</p>
                  ))}
                </div>
              </div>
            )}
            
            {report?.conclusion && (
              <div>
                <h3 className="font-semibold text-lg mb-3">결론</h3>
                <div className="prose prose-sm max-w-none">
                  {report.conclusion.split('\n').map((paragraph, index) => (
                    <p key={index} className="mb-2">{paragraph}</p>
                  ))}
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
        
        <DialogFooter>
          <Button onClick={onClose}>
            닫기
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}