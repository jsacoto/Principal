'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useMemo, useState } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  FileText,
  FolderUp,
  History,
  LockKeyhole,
  Plus,
  RefreshCw,
  Save,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Users,
} from 'lucide-react';
import {
  getInitiativeAudit,
  getManagedInitiative,
  getManagedInitiatives,
  getMe,
  updateManagedActivity,
  uploadActivityEvidence,
} from '@/lib/api';
import type { Activity, AuthUser, ManagedInitiative } from '@/lib/types';

const states = ['En desarrollo', 'Completo', 'Iniciado', 'Por Iniciar', 'No Iniciado'];
const priorities = ['Alta', 'Media', 'Baja'];

export function ManagementConsole() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [items, setItems] = useState<ManagedInitiative[]>([]);
  const [selected, setSelected] = useState<ManagedInitiative | null>(null);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [audit, setAudit] = useState<any | null>(null);

  async function load() {
    setLoading(true);
    try {
      const me = await getMe();
      setUser(me.user);
      const initiatives = await getManagedInitiatives();
      setItems(initiatives);
      if (selected) {
        const refreshed = await getManagedInitiative(selected.code);
        setSelected(refreshed);
      }
    } catch (err: any) {
      if (err?.status === 401 || String(err?.message).toLowerCase().includes('authentication')) {
        router.push('/login');
      } else {
        setMessage(err instanceof Error ? err.message : String(err));
      }
    } finally { setLoading(false); }
  }

  useEffect(() => { load(); }, []);

  const filtered = useMemo(() => items.filter(i => `${i.code} ${i.title} ${i.description} ${i.scope || ''}`.toLowerCase().includes(query.toLowerCase())), [items, query]);

  async function open(code: string) {
    setMessage('');
    setAudit(null);
    try { setSelected(await getManagedInitiative(code)); }
    catch (err) { setMessage(err instanceof Error ? err.message : String(err)); }
  }

  async function showAudit() {
    if (!selected) return;
    setAudit(await getInitiativeAudit(selected.code));
  }

  async function refreshedSelected() {
    if (!selected) return;
    const detail = await getManagedInitiative(selected.code);
    setSelected(detail);
    const list = await getManagedInitiatives();
    setItems(list);
  }

  if (loading && !user) return <div className="grid min-h-[55vh] place-items-center text-sm muted">Validando acceso autorizado…</div>;

  return (
    <div className="space-y-5">
      <section className="glass rounded-[30px] p-5 lg:p-7">
        <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-center">
          <div>
            <div className="eyebrow">Espacio autorizado · gobernanza operativa</div>
            <h1 className="mt-2 text-3xl font-semibold tracking-[-.045em]">Gestión de iniciativas y evidencias</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 muted">Actualice actividades, registre la justificación del avance y adjunte evidencias. Cada modificación queda asociada al usuario autenticado y a la iniciativa autorizada.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <div className="flex items-center gap-2 rounded-2xl border hairline px-3 py-2.5 text-xs"><ShieldCheck size={15} className="text-emerald-500"/><div><b>{user?.name}</b><div className="text-[10px] muted">{user?.role === 'admin' ? 'Administrador' : 'Responsable de iniciativa'}</div></div></div>
            {user?.role === 'admin' && <>
              <Link href="/gestion/nueva" className="focus-ring flex items-center gap-2 rounded-2xl border hairline px-3 py-2.5 text-xs font-semibold glass"><Plus size={15}/>Nueva iniciativa</Link>
              <Link href="/gestion/usuarios" className="focus-ring flex items-center gap-2 rounded-2xl border hairline px-3 py-2.5 text-xs font-semibold glass"><Users size={15}/>Usuarios</Link>
            </>}
          </div>
        </div>
      </section>

      {message && <div className="rounded-2xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-xs text-rose-500">{message}</div>}

      <div className="grid gap-5 xl:grid-cols-[.72fr_1.28fr]">
        <section className="glass min-h-[640px] rounded-[28px] p-4 lg:p-5">
          <div className="flex items-center justify-between gap-3">
            <div><div className="eyebrow">Cartera autorizada</div><h2 className="mt-1 font-semibold">{items.length} iniciativa(s)</h2></div>
            <button onClick={load} className="focus-ring rounded-xl border hairline p-2" title="Actualizar"><RefreshCw size={15}/></button>
          </div>
          <label className="mt-4 flex items-center gap-2 rounded-2xl border hairline px-3 py-2.5"><Search size={14} className="muted"/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Buscar…" className="w-full bg-transparent text-xs outline-none"/></label>
          <div className="mt-4 space-y-2">
            {filtered.map(i => <button key={i.code} onClick={()=>open(i.code)} className={`focus-ring w-full rounded-2xl border p-4 text-left transition ${selected?.code===i.code?'border-sky-500/35 bg-sky-500/8':'hairline hover:bg-black/[.025] dark:hover:bg-white/[.025]'}`}>
              <div className="flex items-start justify-between gap-3"><div><div className="text-xs font-semibold">Iniciativa {i.code}</div><div className="mt-1 line-clamp-2 text-[11px] leading-4 muted">{i.description}</div></div><ChevronRight size={15} className="mt-0.5 shrink-0 muted"/></div>
              <div className="mt-3 flex items-center gap-3"><Progress value={i.analytical_progress}/><span className="text-[10px] muted">{i.objective_code} · {i.status}</span></div>
            </button>)}
            {!filtered.length && <div className="rounded-2xl border hairline p-5 text-center text-xs muted">No hay iniciativas asignadas que coincidan con la búsqueda.</div>}
          </div>
        </section>

        <section className="glass min-h-[640px] rounded-[28px] p-5 lg:p-6">
          {!selected ? <EmptySelection/> : <InitiativeWorkspace initiative={selected} onRefresh={refreshedSelected} onAudit={showAudit} audit={audit}/>} 
        </section>
      </div>
    </div>
  );
}

function InitiativeWorkspace({ initiative, onRefresh, onAudit, audit }: { initiative: ManagedInitiative; onRefresh: () => Promise<void>; onAudit: () => Promise<void>; audit: any | null }) {
  const [activeId, setActiveId] = useState<number | null>(initiative.activities.find(a=>a.activity_type==='activity')?.id || null);
  const active = initiative.activities.find(a=>a.id===activeId) || null;
  const uploads = initiative.uploads || [];
  const activeUploads = active ? uploads.filter(u=>u.activity_id===active.id) : [];

  useEffect(()=>{ setActiveId(initiative.activities.find(a=>a.activity_type==='activity')?.id || null); },[initiative.code]);

  return <div>
    <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
      <div><div className="eyebrow">{initiative.objective_code} · {initiative.scope || 'Institucional'}</div><h2 className="mt-2 text-2xl font-semibold tracking-[-.035em]">Iniciativa {initiative.code}</h2><p className="mt-2 max-w-3xl text-xs leading-5 muted">{initiative.description}</p></div>
      <div className="text-right"><div className="metric text-3xl font-semibold text-emerald-500">{initiative.analytical_progress.toFixed(1)}%</div><div className="text-[10px] muted">avance analítico</div></div>
    </div>
    <div className="mt-5 grid gap-2 sm:grid-cols-5">{['D1','D2','D3','D4','D5'].map(d=><div key={d} className="rounded-xl border hairline p-2 text-center"><div className="text-[9px] muted">{d}</div><div className="metric mt-1 font-semibold">{initiative.contributions[d] || 0}</div></div>)}</div>

    <div className="mt-6 grid gap-5 lg:grid-cols-[.72fr_1.28fr]">
      <div>
        <div className="flex items-center justify-between"><div className="text-xs font-semibold">Actividades</div><button onClick={onAudit} className="focus-ring flex items-center gap-1.5 rounded-xl border hairline px-2.5 py-1.5 text-[10px]"><History size={12}/>Historial</button></div>
        <div className="mt-3 max-h-[520px] space-y-2 overflow-y-auto pr-1">
          {initiative.activities.filter(a=>a.activity_type==='activity').map(a=><button key={a.id} onClick={()=>setActiveId(a.id)} className={`focus-ring w-full rounded-2xl border p-3 text-left transition ${activeId===a.id?'border-violet-500/35 bg-violet-500/8':'hairline'}`}><div className="flex items-start justify-between gap-3"><div><div className="text-[10px] font-semibold muted">{a.external_id}</div><div className="mt-1 text-xs font-medium leading-5">{a.title}</div></div><span className="metric shrink-0 text-xs font-semibold">{a.progress==null?'—':`${a.progress.toFixed(0)}%`}</span></div><div className="mt-2 flex gap-2 text-[9px] muted"><span>{a.state || 'Sin estado'}</span><span>·</span><span>{a.priority || 'Sin prioridad'}</span></div></button>)}
        </div>
      </div>
      <div>{active ? <ActivityEditor key={`${initiative.code}-${active.id}-${active.progress}-${active.state}`} activity={active} uploads={activeUploads} onSaved={onRefresh}/> : <div className="grid min-h-[320px] place-items-center rounded-2xl border hairline text-xs muted">Seleccione una actividad.</div>}</div>
    </div>

    {audit && <AuditPanel audit={audit}/>} 
  </div>;
}

function ActivityEditor({ activity, uploads, onSaved }: { activity: Activity; uploads: any[]; onSaved: () => Promise<void> }) {
  const [progress, setProgress] = useState(activity.progress ?? 0);
  const [state, setState] = useState(activity.state || 'En desarrollo');
  const [priority, setPriority] = useState(activity.priority || 'Media');
  const [startDate, setStartDate] = useState(activity.start_date || '');
  const [endDate, setEndDate] = useState(activity.end_date || '');
  const [observation, setObservation] = useState(activity.observation || '');
  const [justification, setJustification] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [fileDescription, setFileDescription] = useState('');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');

  async function save() {
    if (justification.trim().length < 3) { setNotice('Debe registrar una justificación del avance o cambio.'); return; }
    setBusy(true); setNotice('');
    try {
      await updateManagedActivity(activity.id, {
        progress, state, priority,
        start_date: startDate || null,
        end_date: endDate || null,
        observation,
        justification,
      });
      setNotice('Cambios guardados y trazabilidad registrada.');
      setJustification('');
      await onSaved();
    } catch (err) { setNotice(err instanceof Error ? err.message : String(err)); }
    finally { setBusy(false); }
  }

  async function upload() {
    if (!file) { setNotice('Seleccione un archivo de evidencia.'); return; }
    setBusy(true); setNotice('');
    try {
      await uploadActivityEvidence(activity.id, file, fileDescription);
      setFile(null); setFileDescription('');
      const input = document.getElementById(`evidence-${activity.id}`) as HTMLInputElement | null;
      if (input) input.value='';
      setNotice('Evidencia cargada correctamente.');
      await onSaved();
    } catch (err) { setNotice(err instanceof Error ? err.message : String(err)); }
    finally { setBusy(false); }
  }

  return <div className="rounded-[24px] border hairline p-4 lg:p-5">
    <div className="flex items-start justify-between gap-3"><div><div className="eyebrow">Editar actividad {activity.external_id}</div><h3 className="mt-1 text-sm font-semibold leading-5">{activity.title}</h3></div><SlidersHorizontal size={18} className="muted"/></div>
    <div className="mt-5 flex items-end justify-between"><label className="text-xs font-semibold">Avance (%)</label><div className="metric text-2xl font-semibold">{progress.toFixed(0)}%</div></div>
    <input type="range" min="0" max="100" step="1" value={progress} onChange={e=>setProgress(Number(e.target.value))} className="range mt-3 w-full"/>
    <div className="mt-4 grid gap-3 sm:grid-cols-2"><Field label="Estado"><select value={state} onChange={e=>setState(e.target.value)} className="control">{states.map(s=><option key={s}>{s}</option>)}</select></Field><Field label="Prioridad"><select value={priority} onChange={e=>setPriority(e.target.value)} className="control">{priorities.map(p=><option key={p}>{p}</option>)}</select></Field><Field label="Fecha inicio"><input type="date" value={startDate} onChange={e=>setStartDate(e.target.value)} className="control"/></Field><Field label="Fecha fin"><input type="date" value={endDate} onChange={e=>setEndDate(e.target.value)} className="control"/></Field></div>
    <Field label="Observación general" className="mt-4"><textarea value={observation} onChange={e=>setObservation(e.target.value)} rows={3} className="control resize-y"/></Field>
    <Field label="Justificación del avance / cambio *" className="mt-4"><textarea value={justification} onChange={e=>setJustification(e.target.value)} rows={3} placeholder="Explique qué cambió, por qué y qué evidencia lo respalda." className="control resize-y"/></Field>
    <button onClick={save} disabled={busy} className="focus-ring mt-4 flex w-full items-center justify-center gap-2 rounded-2xl bg-[color:var(--text)] px-4 py-3 text-xs font-semibold text-[color:var(--canvas)] disabled:opacity-50"><Save size={14}/>{busy?'Guardando…':'Guardar avance y justificación'}</button>

    <div className="my-6 h-px bg-[color:var(--line)]"/>
    <div className="flex items-center gap-2"><FolderUp size={17} className="text-sky-500"/><div className="text-xs font-semibold">Evidencias de la actividad</div></div>
    <div className="mt-3 grid gap-2"><input id={`evidence-${activity.id}`} type="file" onChange={e=>setFile(e.target.files?.[0] || null)} className="block w-full rounded-xl border hairline p-2 text-[10px]"/><input value={fileDescription} onChange={e=>setFileDescription(e.target.value)} placeholder="Descripción breve de la evidencia" className="control"/><button onClick={upload} disabled={busy||!file} className="focus-ring rounded-xl border hairline px-3 py-2 text-[10px] font-semibold disabled:opacity-50">Subir evidencia</button></div>
    <div className="mt-3 space-y-2">{uploads.map(u=><a key={u.id} href={u.download_url} className="flex items-center justify-between gap-3 rounded-xl border hairline p-2.5 text-[10px] hover:bg-black/[.025] dark:hover:bg-white/[.025]"><div className="flex min-w-0 items-center gap-2"><FileText size={13} className="shrink-0 text-sky-500"/><div className="min-w-0"><div className="truncate font-semibold">{u.original_name}</div><div className="truncate muted">{u.description || 'Sin descripción'} · {formatBytes(u.size_bytes)}</div></div></div><span className="shrink-0 muted">Descargar</span></a>)}{!uploads.length&&<div className="rounded-xl border hairline p-3 text-[10px] muted">Aún no hay archivos cargados desde la plataforma.</div>}</div>
    {notice && <div className={`mt-4 rounded-xl px-3 py-2 text-[10px] ${notice.toLowerCase().includes('correct')||notice.toLowerCase().includes('guard')?'bg-emerald-500/10 text-emerald-500':'bg-amber-500/10 text-amber-500'}`}>{notice}</div>}
  </div>;
}

function AuditPanel({ audit }: { audit: any }) {
  return <div className="mt-6 rounded-[24px] border hairline p-4"><div className="flex items-center gap-2"><History size={16} className="text-violet-500"/><div className="text-xs font-semibold">Historial de cambios</div></div><div className="mt-3 space-y-2">{audit.changes?.slice(0,12).map((x:any,idx:number)=><div key={idx} className="rounded-xl border hairline p-3 text-[10px]"><div className="flex justify-between gap-3"><b>Actividad {x.external_id || x.activity_id}</b><span className="muted">{String(x.changed_at).replace('T',' ').slice(0,16)}</span></div><div className="mt-1 muted">{x.old_progress ?? '—'}% → {x.new_progress ?? '—'}% · {x.old_state || '—'} → {x.new_state || '—'}</div><div className="mt-1">{x.justification}</div><div className="mt-1 text-[9px] muted">Por: {x.changed_by || 'Usuario'}</div></div>)}{!audit.changes?.length&&<div className="text-[10px] muted">No hay modificaciones registradas todavía.</div>}</div></div>;
}

function EmptySelection() { return <div className="grid min-h-[560px] place-items-center text-center"><div><div className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-violet-500/10 text-violet-500"><LockKeyhole size={22}/></div><div className="mt-4 text-sm font-semibold">Seleccione una iniciativa autorizada</div><div className="mt-1 text-xs muted">Desde aquí podrá actualizar actividades, justificar avances y adjuntar evidencias.</div></div></div>; }
function Progress({value}:{value:number}) { return <div className="flex items-center gap-2"><div className="h-1.5 w-16 overflow-hidden rounded-full bg-black/5 dark:bg-white/5"><div className="h-full rounded-full bg-emerald-500" style={{width:`${Math.max(0,Math.min(100,value))}%`}}/></div><b className="metric text-[10px]">{value.toFixed(1)}%</b></div>; }
function Field({label,children,className=''}:{label:string;children:React.ReactNode;className?:string}) { return <label className={`block ${className}`}><span className="mb-1.5 block text-[10px] font-semibold muted">{label}</span>{children}</label>; }
function formatBytes(bytes:number){ if(bytes<1024)return `${bytes} B`; if(bytes<1024*1024)return `${(bytes/1024).toFixed(1)} KB`; return `${(bytes/1024/1024).toFixed(1)} MB`; }
