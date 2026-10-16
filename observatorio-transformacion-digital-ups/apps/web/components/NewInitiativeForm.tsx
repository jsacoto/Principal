'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { ArrowLeft, CirclePlus, Plus, Save, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { createInitiative, getInitiativeTemplate, getMe } from '@/lib/api';
import type { InitiativeTemplate } from '@/lib/types';

type ActivityDraft = {
  external_id: string;
  title: string;
  progress: number;
  state: string;
  priority: string;
  start_date: string;
  end_date: string;
  observation: string;
  in_field: string;
  responsible_name: string;
  responsible_email: string;
};

const blankActivity = (id: number): ActivityDraft => ({
  external_id: String(id), title: '', progress: 0, state: 'Por Iniciar', priority: 'Media',
  start_date: '', end_date: '', observation: '', in_field: '', responsible_name: '', responsible_email: '',
});

export function NewInitiativeForm() {
  const router = useRouter();
  const [template, setTemplate] = useState<InitiativeTemplate | null>(null);
  const [code, setCode] = useState('');
  const [objective, setObjective] = useState('O1');
  const [scope, setScope] = useState('');
  const [description, setDescription] = useState('');
  const [leaderName, setLeaderName] = useState('');
  const [leaderEmail, setLeaderEmail] = useState('');
  const [status, setStatus] = useState('Por Iniciar');
  const [contributions, setContributions] = useState<Record<string, number>>({D1:0,D2:0,D3:0,D4:0,D5:0});
  const [activities, setActivities] = useState<ActivityDraft[]>([blankActivity(1)]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([getMe(), getInitiativeTemplate()]).then(([me, t]) => {
      if (me.user.role !== 'admin') { router.replace('/gestion'); return; }
      setTemplate(t);
      if (t.objectives[0]) setObjective(t.objectives[0].code);
      if (t.state_options.includes('Por Iniciar')) setStatus('Por Iniciar');
    }).catch(() => router.replace('/login'));
  }, []);

  function updateActivity(index: number, patch: Partial<ActivityDraft>) {
    setActivities(prev => prev.map((a,i)=>i===index?{...a,...patch}:a));
  }

  function addActivity() { setActivities(prev => [...prev, blankActivity(prev.length + 1)]); }
  function removeActivity(index: number) { setActivities(prev => prev.filter((_,i)=>i!==index).map((a,i)=>({...a, external_id: a.external_id || String(i+1)}))); }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    if (!Object.values(contributions).some(v=>v>0)) { setError('Defina al menos una contribución D1–D5 mayor que cero.'); return; }
    if (!activities.length) { setError('La plantilla requiere al menos una actividad.'); return; }
    if (activities.some(a=>!a.title.trim())) { setError('Todas las actividades deben tener un nombre.'); return; }
    setBusy(true);
    try {
      const result = await createInitiative({
        code, objective_code: objective, scope, description, leader_name: leaderName, leader_email: leaderEmail,
        status, contributions,
        activities: activities.map(a=>({
          ...a,
          start_date: a.start_date || null,
          end_date: a.end_date || null,
        })),
      });
      router.push(`/gestion?created=${encodeURIComponent(result.initiative.code)}`);
      router.refresh();
    } catch (err) { setError(err instanceof Error ? err.message : String(err)); }
    finally { setBusy(false); }
  }

  if (!template) return <div className="grid min-h-[55vh] place-items-center text-sm muted">Cargando plantilla institucional…</div>;

  return <form onSubmit={submit} className="space-y-5">
    <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end"><div><div className="eyebrow">Administración · plantilla de cartera</div><h1 className="mt-2 text-3xl font-semibold tracking-[-.045em]">Agregar nueva iniciativa</h1><p className="mt-2 max-w-3xl text-sm leading-6 muted">La estructura reproduce los campos observados en la plantilla Notion de la UPS y añade la contribución D1–D5 requerida por el modelo analítico.</p></div><Link href="/gestion" className="focus-ring flex items-center gap-2 rounded-2xl border hairline px-3 py-2.5 text-xs glass"><ArrowLeft size={14}/>Volver a gestión</Link></div>

    <section className="glass rounded-[28px] p-5 lg:p-7">
      <div className="eyebrow">1. Identificación y alineación</div>
      <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Field label="Código de iniciativa *"><input required value={code} onChange={e=>setCode(e.target.value)} placeholder="27 o 27.a" className="control"/></Field>
        <Field label="Objetivo estratégico *"><select value={objective} onChange={e=>setObjective(e.target.value)} className="control">{template.objectives.map(o=><option key={o.code} value={o.code}>{o.code}{o.legacy_code?` / ${o.legacy_code}`:''} · {o.name}</option>)}</select></Field>
        <Field label="Ámbito *"><input required value={scope} onChange={e=>setScope(e.target.value)} placeholder="Académico, Gestión, Bienestar…" className="control"/></Field>
        <Field label="Estado inicial"><select value={status} onChange={e=>setStatus(e.target.value)} className="control">{template.state_options.map(s=><option key={s}>{s}</option>)}</select></Field>
      </div>
      <div className="mt-4 grid gap-4 md:grid-cols-2"><Field label="Líder de iniciativa *"><input required value={leaderName} onChange={e=>setLeaderName(e.target.value)} className="control"/></Field><Field label="Correo del líder"><input type="email" value={leaderEmail} onChange={e=>setLeaderEmail(e.target.value)} placeholder="nombre@ups.edu.ec" className="control"/></Field></div>
      <Field label="Descripción de la iniciativa *" className="mt-4"><textarea required minLength={10} rows={4} value={description} onChange={e=>setDescription(e.target.value)} placeholder="Defina el propósito, alcance y resultado esperado de la iniciativa." className="control resize-y"/></Field>
    </section>

    <section className="glass rounded-[28px] p-5 lg:p-7">
      <div className="eyebrow">2. Contribución al modelo D1–D5</div><h2 className="mt-1 text-lg font-semibold">Matriz I(i,d)</h2><p className="mt-2 text-xs leading-5 muted">0 = sin contribución · 1 = baja · 2 = media · 3 = alta. Estos valores se incorporan directamente al cálculo de madurez estructural.</p>
      <div className="mt-5 grid gap-3 sm:grid-cols-5">{template.dimensions.map(d=><div key={d.code} className="rounded-2xl border hairline p-4"><div className="metric text-xl font-semibold text-sky-500">{d.code}</div><div className="mt-1 min-h-[34px] text-[10px] leading-4 muted">{d.name}</div><select value={contributions[d.code] ?? 0} onChange={e=>setContributions(prev=>({...prev,[d.code]:Number(e.target.value)}))} className="control mt-3">{template.contribution_levels.map(v=><option key={v} value={v}>{v} · {['Nula','Baja','Media','Alta'][v]}</option>)}</select></div>)}</div>
    </section>

    <section className="glass rounded-[28px] p-5 lg:p-7">
      <div className="flex items-start justify-between gap-4"><div><div className="eyebrow">3. Actividades principales</div><h2 className="mt-1 text-lg font-semibold">Plantilla operativa</h2><p className="mt-2 text-xs leading-5 muted">Campos replicados: Id, Actividades para la Implementación, Fecha Inicio, Fecha Fin, Avance (%), Responsable, Evidencias, Estado, In, Prioridad y Observación general. Las evidencias se cargan desde Gestión una vez creada la iniciativa.</p></div><button type="button" onClick={addActivity} className="focus-ring flex shrink-0 items-center gap-2 rounded-2xl border hairline px-3 py-2 text-xs font-semibold"><Plus size={14}/>Actividad</button></div>
      <div className="mt-5 space-y-4">{activities.map((a,index)=><article key={index} className="rounded-[24px] border hairline p-4 lg:p-5"><div className="flex items-center justify-between"><div className="flex items-center gap-2"><CirclePlus size={15} className="text-violet-500"/><div className="text-xs font-semibold">Actividad {index+1}</div></div>{activities.length>1&&<button type="button" onClick={()=>removeActivity(index)} className="focus-ring rounded-xl p-2 text-rose-500"><Trash2 size={14}/></button>}</div>
        <div className="mt-4 grid gap-3 md:grid-cols-[110px_1fr]"><Field label="Id"><input required value={a.external_id} onChange={e=>updateActivity(index,{external_id:e.target.value})} className="control"/></Field><Field label="Actividades para la Implementación *"><input required value={a.title} onChange={e=>updateActivity(index,{title:e.target.value})} className="control"/></Field></div>
        <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4"><Field label="Fecha Inicio"><input type="date" value={a.start_date} onChange={e=>updateActivity(index,{start_date:e.target.value})} className="control"/></Field><Field label="Fecha Fin"><input type="date" value={a.end_date} onChange={e=>updateActivity(index,{end_date:e.target.value})} className="control"/></Field><Field label="Avance (%)"><input type="number" min="0" max="100" step="1" value={a.progress} onChange={e=>updateActivity(index,{progress:Number(e.target.value)})} className="control"/></Field><Field label="Estado"><select value={a.state} onChange={e=>updateActivity(index,{state:e.target.value})} className="control">{template.state_options.map(s=><option key={s}>{s}</option>)}</select></Field></div>
        <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4"><Field label="Responsable"><input value={a.responsible_name} onChange={e=>updateActivity(index,{responsible_name:e.target.value})} className="control"/></Field><Field label="Correo responsable"><input type="email" value={a.responsible_email} onChange={e=>updateActivity(index,{responsible_email:e.target.value})} className="control"/></Field><Field label="Prioridad"><select value={a.priority} onChange={e=>updateActivity(index,{priority:e.target.value})} className="control">{template.priority_options.map(p=><option key={p}>{p}</option>)}</select></Field><Field label="In"><input value={a.in_field} onChange={e=>updateActivity(index,{in_field:e.target.value})} placeholder="Referencia interna opcional" className="control"/></Field></div>
        <Field label="Observación general" className="mt-3"><textarea rows={2} value={a.observation} onChange={e=>updateActivity(index,{observation:e.target.value})} className="control resize-y"/></Field>
      </article>)}</div>
    </section>

    {error&&<div className="rounded-2xl bg-rose-500/10 px-4 py-3 text-xs text-rose-500">{error}</div>}
    <div className="flex justify-end"><button disabled={busy} className="focus-ring flex items-center gap-2 rounded-2xl bg-[color:var(--text)] px-5 py-3 text-xs font-semibold text-[color:var(--canvas)] disabled:opacity-50"><Save size={15}/>{busy?'Creando iniciativa…':'Crear iniciativa y actividades'}</button></div>
  </form>;
}

function Field({label,children,className=''}:{label:string;children:React.ReactNode;className?:string}) { return <label className={`block ${className}`}><span className="mb-1.5 block text-[10px] font-semibold muted">{label}</span>{children}</label>; }
