'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import {
  Activity,
  BarChart3,
  BookOpenText,
  CircleUserRound,
  ContactRound,
  Layers3,
  LogIn,
  LogOut,
  Settings2,
} from 'lucide-react';
import { getMe, logout } from '@/lib/api';
import type { AuthUser } from '@/lib/types';

const publicNav = [
  { href: '/', label: 'Inicio', icon: BarChart3 },
  { href: '/model', label: 'Modelo TD', icon: BookOpenText },
  { href: '/dimensions', label: 'Dimensiones', icon: Layers3 },
  { href: '/contact', label: 'Contacto', icon: ContactRound },
];

export function PublicHeaderNav() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    let active = true;
    getMe().then((data) => active && setUser(data.user)).catch(() => active && setUser(null));
    return () => { active = false; };
  }, [pathname]);

  async function signOut() {
    try { await logout(); } finally {
      setUser(null);
      router.push('/');
      router.refresh();
    }
  }

  return (
    <header className="sticky top-0 z-50 border-b hairline bg-[color:var(--panel)] backdrop-blur-2xl">
      <div className="mx-auto flex max-w-[1480px] items-center justify-between gap-4 px-5 py-3 lg:px-8">
        <Link href="/" className="focus-ring flex min-w-0 items-center gap-3 rounded-xl">
          <div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-sky-500 to-violet-600 text-white shadow-lg shadow-sky-500/20">
            <Activity size={19} strokeWidth={2.1} />
          </div>
          <div className="min-w-0">
            <div className="truncate text-[13px] font-semibold leading-tight">Observatorio de Transformación Digital</div>
            <div className="truncate text-[11px] muted">Universidad Politécnica Salesiana</div>
          </div>
        </Link>

        <div className="flex items-center gap-2">
          <nav className="hidden items-center gap-1 rounded-2xl border hairline p-1 glass lg:flex">
            {publicNav.map(({ href, label, icon: Icon }) => {
              const active = pathname === href;
              return (
                <Link key={href} href={href} className={`flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-medium transition ${active ? 'bg-black/5 dark:bg-white/7' : 'hover:bg-black/5 dark:hover:bg-white/5'}`}>
                  <Icon size={15} /> {label}
                </Link>
              );
            })}
          </nav>

          {user ? (
            <div className="flex items-center gap-1 rounded-2xl border hairline p-1 glass">
              <Link href="/gestion" className="flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-medium transition hover:bg-black/5 dark:hover:bg-white/5">
                <Settings2 size={15} /> <span className="hidden sm:inline">Gestión</span>
              </Link>
              <button onClick={signOut} title="Cerrar sesión" className="focus-ring rounded-xl p-2 transition hover:bg-black/5 dark:hover:bg-white/5">
                <LogOut size={15} />
              </button>
            </div>
          ) : (
            <Link href="/login" className="flex items-center gap-2 rounded-2xl border hairline px-3 py-2.5 text-xs font-semibold glass transition hover:scale-[1.01]">
              <LogIn size={15} /> Acceso autorizado
            </Link>
          )}
        </div>
      </div>

      <div className="border-t hairline lg:hidden">
        <nav className="mx-auto flex max-w-[1480px] items-center gap-1 overflow-x-auto px-4 py-2">
          {publicNav.map(({ href, label, icon: Icon }) => (
            <Link key={href} href={href} className={`flex shrink-0 items-center gap-2 rounded-xl px-3 py-2 text-[11px] font-medium ${pathname === href ? 'bg-black/5 dark:bg-white/7' : ''}`}>
              <Icon size={14} /> {label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
