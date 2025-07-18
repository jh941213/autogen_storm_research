'use client';

import { useState } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Switch } from '@/components/ui/switch';
import { Loader2, Search, Sparkles, Users, MessageSquare } from 'lucide-react';
import { ResearchFormData } from '@/types';

const formSchema = z.object({
  topic: z.string().min(5, {
    message: '연구 주제는 최소 5자 이상 입력해주세요.',
  }),
  maxAnalysts: z.number().min(1).max(10),
  maxInterviewTurns: z.number().min(1).max(10),
  parallelInterviews: z.boolean(),
  modelProvider: z.enum(['openai', 'azure_openai', 'anthropic']),
  apiKey: z.string().optional(),
  azureEndpoint: z.string().optional(),
  azureDeployment: z.string().optional(),
});

interface ResearchFormProps {
  onSubmit: (data: ResearchFormData) => void;
  isLoading?: boolean;
}

export function ResearchForm({ onSubmit, isLoading = false }: ResearchFormProps) {
  const [topicSuggestions] = useState([
    'AI의 미래와 윤리적 도전',
    '기후 변화와 재생에너지 정책',
    '메타버스와 디지털 경제',
    '양자컴퓨팅의 현재와 미래',
    '바이오테크놀로지와 헬스케어 혁신',
  ]);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      topic: '',
      maxAnalysts: 3,
      maxInterviewTurns: 3,
      parallelInterviews: true,
      modelProvider: 'azure_openai',
      apiKey: '',
      azureEndpoint: '',
      azureDeployment: '',
    },
  });

  const selectedProvider = form.watch('modelProvider');

  const handleSubmit = (values: z.infer<typeof formSchema>) => {
    onSubmit({
      topic: values.topic,
      maxAnalysts: values.maxAnalysts,
      maxInterviewTurns: values.maxInterviewTurns,
      parallelInterviews: values.parallelInterviews,
      modelProvider: values.modelProvider,
      apiKey: values.apiKey,
      azureEndpoint: values.azureEndpoint,
      azureDeployment: values.azureDeployment,
    });
  };

  const handleSuggestionClick = (suggestion: string) => {
    form.setValue('topic', suggestion);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl flex items-center justify-center gap-2">
          <Search className="h-6 w-6 text-primary" />
          새로운 연구 시작
        </CardTitle>
        <CardDescription>
          AI 전문가들이 협력하여 깊이 있는 연구를 수행합니다
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            {/* 연구 주제 */}
            <FormField
              control={form.control}
              name="topic"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-base font-medium">연구 주제</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="연구하고 싶은 주제를 상세히 입력해주세요..."
                      className="min-h-20 resize-none"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    명확하고 구체적인 주제일수록 더 정확한 연구 결과를 얻을 수 있습니다.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* 주제 제안 */}
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">추천 주제:</p>
              <div className="flex flex-wrap gap-2">
                {topicSuggestions.map((suggestion) => (
                  <Badge
                    key={suggestion}
                    variant="secondary"
                    className="cursor-pointer hover:bg-primary/10 transition-colors"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    {suggestion}
                  </Badge>
                ))}
              </div>
            </div>

            {/* 연구 설정 */}
            <div className="grid grid-cols-1 gap-4">
              <FormField
                control={form.control}
                name="maxInterviewTurns"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <MessageSquare className="h-4 w-4" />
                      인터뷰 라운드
                    </FormLabel>
                    <Select onValueChange={(value) => field.onChange(Number(value))} defaultValue={field.value.toString()}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="라운드 수 선택" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                          <SelectItem key={num} value={num.toString()}>
                            {num}라운드
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      각 분석가와 진행할 인터뷰 라운드 수 (분석가 수는 연구 시작 시 선택)
                    </FormDescription>
                  </FormItem>
                )}
              />
            </div>

            {/* 고급 설정 */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">고급 설정</h3>
              
              <FormField
                control={form.control}
                name="parallelInterviews"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">병렬 인터뷰</FormLabel>
                      <FormDescription>
                        모든 분석가와 동시에 인터뷰를 진행하여 시간을 단축합니다
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="modelProvider"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <Sparkles className="h-4 w-4" />
                      AI 모델 제공자
                    </FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="모델 제공자 선택" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="azure_openai">Azure OpenAI</SelectItem>
                        <SelectItem value="openai">OpenAI</SelectItem>
                        <SelectItem value="anthropic">Anthropic</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      연구에 사용할 AI 모델 제공자를 선택하세요
                    </FormDescription>
                  </FormItem>
                )}
              />

              {/* API 키 설정 */}
              <FormField
                control={form.control}
                name="apiKey"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>API 키 <span className="text-xs text-muted-foreground">(선택사항)</span></FormLabel>
                    <FormControl>
                      <Input
                        type="password"
                        placeholder={
                          selectedProvider === 'openai' ? 'OpenAI API 키 (비어있으면 환경변수 사용)' :
                          selectedProvider === 'anthropic' ? 'Anthropic API 키 (비어있으면 환경변수 사용)' :
                          'Azure OpenAI API 키 (비어있으면 환경변수 사용)'
                        }
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      {selectedProvider === 'openai' && '입력하지 않으면 서버의 기본 OpenAI API 키를 사용합니다'}
                      {selectedProvider === 'anthropic' && '입력하지 않으면 서버의 기본 Anthropic API 키를 사용합니다'}
                      {selectedProvider === 'azure_openai' && '입력하지 않으면 서버의 기본 Azure OpenAI 설정을 사용합니다'}
                    </FormDescription>
                  </FormItem>
                )}
              />

              {/* Azure OpenAI 추가 설정 */}
              {selectedProvider === 'azure_openai' && (
                <>
                  <FormField
                    control={form.control}
                    name="azureEndpoint"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Azure OpenAI 엔드포인트 <span className="text-xs text-muted-foreground">(선택사항)</span></FormLabel>
                        <FormControl>
                          <Input
                            placeholder="https://your-resource.openai.azure.com (비어있으면 환경변수 사용)"
                            {...field}
                          />
                        </FormControl>
                        <FormDescription>
                          입력하지 않으면 서버의 기본 Azure OpenAI 엔드포인트를 사용합니다
                        </FormDescription>
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="azureDeployment"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>배포 이름 <span className="text-xs text-muted-foreground">(선택사항)</span></FormLabel>
                        <FormControl>
                          <Input
                            placeholder="gpt-4o (비어있으면 환경변수 사용)"
                            {...field}
                          />
                        </FormControl>
                        <FormDescription>
                          입력하지 않으면 서버의 기본 Azure OpenAI 배포 이름을 사용합니다
                        </FormDescription>
                      </FormItem>
                    )}
                  />
                </>
              )}
            </div>

            <Button type="submit" disabled={isLoading} className="w-full h-12 text-lg">
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  연구 시작 중...
                </>
              ) : (
                <>
                  <Search className="mr-2 h-4 w-4" />
                  연구 시작하기
                </>
              )}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}