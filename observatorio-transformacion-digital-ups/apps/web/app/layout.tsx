import type { Metadata } from 'next';
import './globals.css';
import { PublicHeaderNav } from '@/components/PublicHeaderNav';

export const metadata: Metadata = {
  title: 'Observatorio de Transformación Digital | UPS',
  description: 'Índice de Transformación Digital, dimensiones, modelo institucional y gestión de iniciativas de la Universidad Politécnica Salesiana.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>
        <PublicHeaderNav />
        <main className="mx-auto max-w-[1480px] px-5 py-6 lg:px-8 lg:py-8">{children}</main>
        <footer className="mt-10 border-t hairline">
          <div className="mx-auto flex max-w-[1480px] flex-col justify-between gap-2 px-5 py-6 text-[11px] muted sm:flex-row lg:px-8">
            <span>Observatorio de Transformación Digital · Universidad Politécnica Salesiana</span>
            <a className="hover:text-[color:var(--text)]" href="mailto:transformaciondigital@ups.edu.ec">transformaciondigital@ups.edu.ec</a>
          </div>
        </footer>
      </body>
    </html>
  );
}
