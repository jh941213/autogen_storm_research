'use client';

import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface AuroraTextProps {
  text: string;
  className?: string;
  speed?: number;
  showCursor?: boolean;
  startDelay?: number;
  variant?: 'aurora' | 'typing';
}

export function AuroraText({ 
  text, 
  className, 
  speed = 100, 
  showCursor = true, 
  startDelay = 0,
  variant = 'aurora'
}: AuroraTextProps) {
  const [displayText, setDisplayText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showCursorBlink, setShowCursorBlink] = useState(true);

  useEffect(() => {
    if (startDelay > 0) {
      const delayTimer = setTimeout(() => {
        setCurrentIndex(0);
      }, startDelay);
      return () => clearTimeout(delayTimer);
    }
  }, [startDelay]);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timer = setTimeout(() => {
        setDisplayText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, speed);
      return () => clearTimeout(timer);
    }
  }, [currentIndex, text, speed]);

  useEffect(() => {
    if (showCursor) {
      const cursorTimer = setInterval(() => {
        setShowCursorBlink(prev => !prev);
      }, 530);
      return () => clearInterval(cursorTimer);
    }
  }, [showCursor]);

  if (variant === 'typing') {
    return (
      <span className={cn("inline-block", className)}>
        {displayText}
        {showCursor && (
          <span 
            className={cn(
              "inline-block w-0.5 h-[1em] bg-current ml-1 transition-opacity duration-100",
              showCursorBlink ? "opacity-100" : "opacity-0"
            )}
          />
        )}
      </span>
    );
  }

  return (
    <>
      <style jsx>{`
        @keyframes aurora {
          0% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
          100% {
            background-position: 0% 50%;
          }
        }
        
        .aurora-text {
          background: linear-gradient(45deg, #3b82f6, #8b5cf6, #6366f1, #ec4899, #3b82f6);
          background-size: 400% 400%;
          animation: aurora 4s ease-in-out infinite;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        
        .aurora-glow {
          background: linear-gradient(45deg, #3b82f6, #8b5cf6, #6366f1, #ec4899, #3b82f6);
          background-size: 400% 400%;
          animation: aurora 3s ease-in-out infinite;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
      `}</style>
      
      <span className={cn("inline-block relative", className)}>
        {/* 글로우 효과 */}
        <span 
          className="absolute inset-0 blur-sm opacity-40 aurora-glow"
        >
          {displayText}
        </span>
        
        {/* 메인 텍스트 */}
        <span 
          className="relative z-10 aurora-text"
        >
          {displayText}
        </span>
        
        {showCursor && (
          <span 
            className={cn(
              "inline-block w-0.5 h-[1em] bg-gradient-to-b from-blue-600 to-purple-600 ml-1 transition-opacity duration-100",
              showCursorBlink ? "opacity-100" : "opacity-0"
            )}
            style={{
              background: 'linear-gradient(to bottom, #3b82f6, #8b5cf6)',
              animation: 'aurora 2s ease-in-out infinite'
            }}
          />
        )}
      </span>
    </>
  );
}