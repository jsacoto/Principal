'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { ArrowLeft, Check, Plus, ShieldCheck, UserCog, UserRoundCheck, UserRoundX } from 'lucide-react';
import { createAdminUser, getAdminUsers, getManagedInitiatives, getMe, updateAdminUser } from '@/lib/api';
import type { AdminUser, ManagedInitiative } from '@/lib/types';

export function UserAdminPanel() {
  const router = useRouter();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [initiatives, setInitiatives] = useState<ManagedInitiative[]>([]);
  const [name,setName]=useState(''); const [email,setEmail]=useState(''); const [password,setPassword]=useState('');
  const [role,setRole]=useState<'admin'|'responsible'>('responsible'); const [codes,setCodes]=useState<string[]>([]);
  const [busy,setBusy]=useState(false); const [notice,setNotice]=useState('');

  async function load(){
    try{
      const me=await getMe(); if(me.user.role!=='admin'){router.replace('/gestion');return;}
      const [u,i]=await Promise.all([getAdminUsers(),getManagedInitiatives()]); setUsers(u);setInitiatives(i);
    }catch{router.replace('/login');}
  }
  useEffect(()=>{load();},[]);

  async function create(e:React.FormEvent){e.preventDefault();setBusy(true);setNotice('');try{await createAdminUser({name,email,password,role,initiative_codes:codes});setName('');setEmail('');setPassword('');setCodes([]);setNotice('Usuario creado y permisos asignados.');await load();}catch(err){setNotice(err instanceof Error?err.message:String(err));}finally{setBusy(false);}}
  async function toggleActive(user:AdminUser){setNotice('');try{await updateAdminUser(user.id,{is_active:!user.is_active});await load();}catch(err){setNotice(err instanceof Error?err.message:String(err));}}
  async function togglePermission(user:AdminUser, code:string){const next=user.initiative_codes.includes(code)?user.initiative_codes.filter(c=>c!==code):[...user.initiative_codes,code];try{await updateAdminUser(user.id,{initiative_codes:next});await load();}catch(err){setNotice(err instanceof Error?err.message:String(err));}}

  return <div className="space-y-5">
    <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end"><div><div className="eyebrow">Administración de acceso</div><h1 className="mt-2 text-3xl font-semibold tracking-[-.045em]">Usuarios responsables y permisos</h1><p className="mt-2 max-w-3xl text-sm leading-6 muted">Cree cuentas para responsables y limite explícitamente qué iniciativas puede modificar cada persona.</p></div><Link href="/gestion" className="focus-ring flex items-center gap-2 rounded-2xl border hairline px-3 py-2.5 text-xs glass"><ArrowLeft size={14}/>Volver</Link></div>
    {notice&&<div className="rounded-2xl border hairline px-4 py-3 text-xs">{notice}</div>}
    <div className="grid gap-5 xl:grid-cols-[.72fr_1.28fr]">
      <form onSubmit={create} className="glass rounded-[28px] p-5 lg:p-6"><div className="flex items-center gap-2"><UserRoundCheck size={18} className="text-emerald-500"/><h2 className="font-semibold">Crear usuario</h2></div><div className="mt-5 space-y-3"><Field label="Nombre completo"><input required value={name} onChange={e=>setName(e.target.value)} className="control"/></Field><Field label="Correo"><input required type="email" value={email} onChange={e=>setEmail(e.target.value)} className="control"/></Field><Field label="Contraseña inicial"><input required type="password" minLength={10} value={password} onChange={e=>setPassword(e.target.value)} className="control"/><div className="mt-1 text-[9px] muted">Mínimo 10 caracteres. En producción envíela por un canal seguro.</div></Field><Field label="Rol"><select value={role} onChange={e=>setRole(e.target.value as any)} className="control"><option value="responsible">Responsable</option><option value="admin">Administrador</option></select></Field></div><div className="mt-5 text-[10px] font-semibold muted">Iniciativas autorizadas</div><div className="mt-2 max-h-[250px] space-y-1 overflow-y-auto rounded-2xl border hairline p-2">{initiatives.map(i=><label key={i.code} className="flex cursor-pointer items-center gap-2 rounded-xl p-2 text-[10px] hover:bg-black/[.025] dark:hover:bg-white/[.025]"><input type="checkbox" checked={codes.includes(i.code)} onChange={()=>setCodes(prev=>prev.includes(i.code)?prev.filter(c=>c!==i.code):[...prev,i.code])}/><b>{i.code}</b><span className="truncate muted">{i.description}</span></label>)}</div><button disabled={busy} className="focus-ring mt-5 flex w-full items-center justify-center gap-2 rounded-2xl bg-[color:var(--text)] px-4 py-3 text-xs font-semibold text-[color:var(--canvas)] disabled:opacity-50"><Plus size={14}/>{busy?'Creando…':'Crear cuenta'}</button></form>
      <section className="glass rounded-[28px] p-5 lg:p-6"><div className="flex items-center gap-2"><UserCog size={18} className="text-violet-500"/><h2 className="font-semibold">Cuentas registradas</h2></div><div className="mt-4 space-y-3">{users.map(user=><article key={user.id} className="rounded-[22px] border hairline p-4"><div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start"><div><div className="flex items-center gap-2"><b className="text-xs">{user.name}</b>{user.role==='admin'&&<span className="rounded-full bg-violet-500/10 px-2 py-0.5 text-[9px] font-semibold text-violet-500">ADMIN</span>}</div><div className="mt-1 text-[10px] muted">{user.email}</div></div><button onClick={()=>toggleActive(user)} className={`focus-ring flex items-center gap-1.5 rounded-xl px-2.5 py-1.5 text-[9px] font-semibold ${user.is_active?'bg-emerald-500/10 text-emerald-500':'bg-rose-500/10 text-rose-500'}`}>{user.is_active?<><Check size={11}/>Activo</>:<><UserRoundX size={11}/>Inactivo</>}</button></div><div className="mt-3 text-[9px] font-semibold muted">Permisos por iniciativa</div><div className="mt-2 flex flex-wrap gap-1.5">{initiatives.map(i=>{const active=user.role==='admin'||user.initiative_codes.includes(i.code);return <button key={i.code} disabled={user.role==='admin'} onClick={()=>togglePermission(user,i.code)} className={`focus-ring rounded-lg border px-2 py-1 text-[9px] ${active?'border-sky-500/25 bg-sky-500/10 text-sky-500':'hairline muted'} disabled:cursor-not-allowed`}>{i.code}</button>})}</div>{user.role==='admin'&&<div className="mt-2 text-[9px] muted">Los administradores tienen acceso a toda la cartera.</div>}</article>)}</div></section>
    </div>
  </div>;
}
function Field({label,children}:{label:string;children:React.ReactNode}){return <label className="block"><span className="mb-1.5 block text-[10px] font-semibold muted">{label}</span>{children}</label>}
