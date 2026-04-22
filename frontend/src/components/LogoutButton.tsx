'use client';

import { useRouter } from 'next/navigation';
import { logout } from '@/lib/session';

export function LogoutButton() {
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  return (
    <button
      onClick={handleLogout}
      className="px-4 py-2 rounded-lg bg-[#753991] text-white text-sm font-semibold hover:bg-opacity-90 transition"
    >
      Logout
    </button>
  );
}
