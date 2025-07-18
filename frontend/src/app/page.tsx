'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Header } from '@/components/layout/header';
import { ResearchForm } from '@/components/research/research-form';
import { AuroraText } from '@/components/ui/aurora-text';
import { ResearchFormData } from '@/types';
import { useResearchStore } from '@/store/research-store';

export default function Home() {
  const router = useRouter();
  const { startResearch, status } = useResearchStore();

  const handleStartResearch = async (data: ResearchFormData) => {
    try {
      await startResearch(data);
      // 연구 시작 후 진행 상황 페이지로 이동
      router.push('/research/progress');
    } catch (error) {
      console.error('연구 시작 중 오류:', error);
    }
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      <Header />
      
      {/* 배경 그라데이션 오버레이 */}
      <div className="fixed inset-0 bg-gradient-to-br from-blue-50/30 via-transparent to-purple-50/30 pointer-events-none"></div>
      
      <main className="relative container mx-auto px-4 py-8 lg:py-16">
        {/* 히어로 섹션 - 테크 기업 스타일 */}
        <section className="text-center space-y-8 lg:space-y-12 mb-16 lg:mb-24 min-h-[60vh] flex flex-col justify-center">
          <div className="space-y-6">
            <div className="relative">
              <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold tracking-tight text-gray-900 mb-4">
                <AuroraText 
                  text="DeepResearch"
                  speed={120}
                />
              </h1>
              <div className="h-2 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 mx-auto w-24 rounded-full opacity-80"></div>
            </div>
            
            <div className="max-w-4xl mx-auto mt-8">
              <p className="text-xl sm:text-2xl md:text-3xl text-gray-600 font-light px-4 leading-relaxed">
                <AuroraText 
                  text="AI 전문가들이 협력하여 깊이 있는 연구를 수행합니다"
                  speed={60}
                  startDelay={1500}
                  className="text-gray-700"
                  variant="typing"
                />
              </p>
            </div>
          </div>
          
          {/* 장식적 요소들 */}
          <div className="flex justify-center items-center space-x-8 mt-12">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse delay-150"></div>
            <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse delay-300"></div>
          </div>
        </section>

        {/* 연구 시작 폼 - 반응형 개선 */}
        <section className="mb-12 lg:mb-16" id="research-form">
          <ResearchForm 
            onSubmit={handleStartResearch}
            isLoading={status === 'connecting' || status === 'running'}
          />
        </section>

        {/* 푸터 - kdb 정보 추가 */}
        <footer className="text-center pt-12 lg:pt-16 pb-8 border-t border-gray-200 space-y-2">
          <p className="text-sm text-gray-500">
            Made by <span className="font-medium text-gray-700">kdb</span>
          </p>
          <p className="text-xs text-gray-400">
            Contact: <a href="mailto:hyun030508@gmail.com" className="hover:text-gray-600 transition-colors">hyun030508@gmail.com</a>
          </p>
        </footer>
      </main>
    </div>
  );
}