import type { Metadata } from 'next';
import Link from 'next/link';
import { Activity, ChartNoAxesCombined, FlaskConical, Layers3, Waypoints } from 'lucide-react';
import './globals.css';

export const metadata: Metadata = {
  title: 'Observatorio de Transformación Digital | UPS',
  description: 'Gobernanza, madurez, OKRs, KPIs y trazabilidad de Transformación Digital de la UPS',
};

const nav = [
  { href: '/', label: 'Cockpit', icon: ChartNoAxesCombined },
  { href: '/initiatives', label: 'Portafolio', icon: Layers3 },
  { href: '/model', label: 'Modelo', icon: Waypoints },
  { href: '/simulator', label: 'What-If', icon: FlaskConical },
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>
        <header className="sticky top-0 z-50 border-b hairline bg-[color:var(--panel)] backdrop-blur-2xl">
          <div className="mx-auto flex max-w-[1480px] items-center justify-between px-5 py-3 lg:px-8">
            <Link href="/" className="flex items-center gap-3 focus-ring rounded-xl">
              <div className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-sky-500 to-violet-600 text-white shadow-lg shadow-sky-500/20">
                <Activity size={19} strokeWidth={2.1} />
              </div>
              <div>
                <div className="text-[13px] font-semibold leading-tight">Observatorio TD</div>
                <div className="text-[11px] muted">Universidad Politécnica Salesiana</div>
              </div>
            </Link>
            <nav className="flex items-center gap-1 rounded-2xl border hairline p-1 glass">
              {nav.map(({ href, label, icon: Icon }) => (
                <Link key={href} href={href} className="flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-medium transition hover:bg-black/5 dark:hover:bg-white/5">
                  <Icon size={15} /> <span className="hidden sm:inline">{label}</span>
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-[1480px] px-5 py-6 lg:px-8 lg:py-8">{children}</main>
      </body>
    </html>
  );
}
