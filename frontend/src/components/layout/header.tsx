'use client';

import { Brain, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { AuroraText } from '@/components/ui/aurora-text';
import Link from 'next/link';

export function Header() {
  return (
    <header className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <div className="flex items-center space-x-2">
              <div className="relative">
                <Brain className="h-6 w-6 text-primary" />
                <Sparkles className="h-3 w-3 text-primary/60 absolute -top-1 -right-1" />
              </div>
              <span className="font-bold text-xl">
                <AuroraText 
                  text="AutoGen DeepResearch"
                  speed={50}
                  showCursor={false}
                />
              </span>
            </div>
          </Link>
        </div>
        <div className="flex flex-1 items-center space-x-2 justify-end">
          <nav className="flex items-center space-x-2">
            <Button variant="ghost" asChild>
              <Link href="/">Home</Link>
            </Button>
            <Button variant="ghost" asChild>
              <Link href="/history">History</Link>
            </Button>
            <Button variant="ghost" asChild>
              <Link href="/architecture">Architecture</Link>
            </Button>
            <Button variant="ghost" asChild>
              <Link href="/versions">Versions</Link>
            </Button>
          </nav>
        </div>
      </div>
    </header>
  );
}