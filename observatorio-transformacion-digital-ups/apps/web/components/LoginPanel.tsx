'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { KeyRound, LockKeyhole, Mail, ShieldCheck } from 'lucide-react';
import { login } from '@/lib/api';

export function LoginPanel() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true); setError('');
    try {
      await login(email, password);
      router.push('/gestion');
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No fue posible iniciar sesión');
    } finally { setBusy(false); }
  }

  return (
    <div className="mx-auto grid min-h-[65vh] max-w-5xl items-center gap-6 lg:grid-cols-[.9fr_1.1fr]">
      <section className="p-2 lg:p-6">
        <div className="grid h-12 w-12 place-items-center rounded-2xl bg-violet-500/10 text-violet-500"><ShieldCheck size={22} /></div>
        <div className="eyebrow mt-6">Acceso de responsables</div>
        <h1 className="mt-3 text-4xl font-semibold tracking-[-.05em]">Gestión autorizada de iniciativas</h1>
        <p className="mt-4 text-sm leading-7 muted">Ingrese con la cuenta asignada por la Coordinación de Transformación Digital. Los permisos se limitan a las iniciativas autorizadas para cada responsable.</p>
        <div className="mt-6 rounded-2xl border hairline p-4 text-xs leading-5 muted"><b className="text-[color:var(--text)]">Seguridad:</b> la sesión utiliza una cookie HTTP-only; los cambios de avance se registran con usuario, fecha y justificación, y los archivos de evidencia se almacenan en el volumen persistente del servidor.</div>
      </section>
      <form onSubmit={submit} className="glass rounded-[30px] p-6 lg:p-8">
        <div className="flex items-center gap-3"><div className="grid h-10 w-10 place-items-center rounded-2xl bg-sky-500/10 text-sky-500"><KeyRound size={19}/></div><div><h2 className="font-semibold">Iniciar sesión</h2><div className="text-[11px] muted">Observatorio TD · UPS</div></div></div>
        <label className="mt-6 block text-xs font-semibold">Correo institucional</label>
        <div className="mt-2 flex items-center gap-2 rounded-2xl border hairline px-3 py-3"><Mail size={15} className="muted"/><input type="email" required value={email} onChange={e=>setEmail(e.target.value)} placeholder="nombre@ups.edu.ec" className="w-full bg-transparent text-sm outline-none"/></div>
        <label className="mt-4 block text-xs font-semibold">Contraseña</label>
        <div className="mt-2 flex items-center gap-2 rounded-2xl border hairline px-3 py-3"><LockKeyhole size={15} className="muted"/><input type="password" required minLength={10} value={password} onChange={e=>setPassword(e.target.value)} placeholder="••••••••••" className="w-full bg-transparent text-sm outline-none"/></div>
        {error && <div className="mt-4 rounded-2xl bg-rose-500/10 px-3 py-2.5 text-xs text-rose-500">{error}</div>}
        <button disabled={busy} className="focus-ring mt-6 w-full rounded-2xl bg-[color:var(--text)] px-4 py-3.5 text-xs font-semibold text-[color:var(--canvas)] disabled:opacity-50">{busy ? 'Validando…' : 'Ingresar al espacio de gestión'}</button>
        <div className="mt-4 text-center text-[10px] muted">¿Requiere acceso? Escriba a transformaciondigital@ups.edu.ec</div>
      </form>
    </div>
  );
}
