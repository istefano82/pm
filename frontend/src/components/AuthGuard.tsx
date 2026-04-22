'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/session';

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const [isChecking, setIsChecking] = useState(true);
  const [authed, setAuthed] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      // Check if token exists
      if (!isAuthenticated()) {
        router.push('/login');
        return;
      }

      // Verify token with backend
      try {
        const response = await fetch('/api/verify', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
          },
        });

        if (!response.ok) {
          router.push('/login');
          return;
        }

        setAuthed(true);
      } catch (err) {
        console.error('Auth check failed:', err);
        router.push('/login');
      } finally {
        setIsChecking(false);
      }
    };

    checkAuth();
  }, [router]);

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#209dd7]"></div>
          <p className="mt-4 text-[#032147] font-semibold">Loading...</p>
        </div>
      </div>
    );
  }

  if (!authed) {
    return null;
  }

  return <>{children}</>;
}
