'use client';

import { useEffect, useMemo, useState } from 'react';
import { ExternalLink, Search, X } from 'lucide-react';
import { getInitiative, getInitiatives, verifyInitiative } from '@/lib/api';
import type { Activity, Initiative } from '@/lib/types';

export function InitiativesExplorer() {
  const [items, setItems] = useState<Initiative[]>([]);
  const [selected, setSelected] = useState<Initiative | null>(null);
  const [query, setQuery] = useState('');
  const [objective, setObjective] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => { getInitiatives(false).then(setItems).finally(() => setLoading(false)); },[]);

  const filtered = useMemo(() => items.filter(i => {
    const text = `${i.code} ${i.title} ${i.description} ${i.leaders.map(x=>x.name).join(' ')}`.toLowerCase();
    return text.includes(query.toLowerCase()) && (objective === 'all' || i.objective_code === objective);
  }), [items, query, objective]);

  async function open(code: string) { setSelected(await getInitiative(code)); }

  return (
    <div className="space-y-5">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div>
          <div className="eyebrow">Data Explorer · trazabilidad operativa</div>
          <h1 className="mt-2 text-3xl font-semibold tracking-[-.04em]">Portafolio de iniciativas UPS</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 muted">29 páginas de iniciativa de la cartera Notion, incluyendo actividades, avances, responsables de iniciativa, cronograma, prioridad, observaciones y referencias de evidencia.</p>
        </div>
        <div className="flex gap-2">
          <label className="glass flex min-w-[250px] items-center gap-2 rounded-2xl px-3 py-2.5 text-xs"><Search size={15} className="muted" /><input value={query} onChange={(e:any)=>setQuery(e.target.value)} placeholder="Buscar iniciativa, líder…" className="w-full bg-transparent outline-none" /></label>
          <select value={objective} onChange={(e:any)=>setObjective(e.target.value)} className="glass rounded-2xl px-3 py-2.5 text-xs outline-none"><option value="all">O1–O5</option><option>O1</option><option>O2</option><option>O3</option><option>O4</option><option>O5</option></select>
        </div>
      </div>
      <div className="glass overflow-hidden rounded-[28px]">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1040px] border-collapse text-left text-xs">
            <thead className="border-b hairline muted"><tr><th className="px-5 py-4">Iniciativa</th><th className="px-3 py-4">Objetivo</th><th className="px-3 py-4">Responsable</th><th className="px-3 py-4">Reportado</th><th className="px-3 py-4">Verificado*</th><th className="px-3 py-4">Estado</th><th className="px-5 py-4 text-right">Contribución D1–D5</th></tr></thead>
            <tbody>
              {loading ? <tr><td colSpan={7} className="px-5 py-12 text-center muted">Cargando cartera…</td></tr> : filtered.map(i => (
                <tr key={i.code} onClick={()=>open(i.code)} className="cursor-pointer border-b hairline transition hover:bg-black/[.025] dark:hover:bg-white/[.025]">
                  <td className="px-5 py-4"><div className="font-semibold">{i.code} · {i.scope || 'Institucional'}</div><div className="mt-1 max-w-[390px] truncate muted">{i.description}</div></td>
                  <td className="px-3 py-4"><span className="rounded-full border hairline px-2 py-1 font-semibold">{i.objective_code}</span></td>
                  <td className="px-3 py-4"><div className="max-w-[220px] truncate">{i.leaders.map(x=>x.name).join(' · ')}</div></td>
                  <td className="px-3 py-4"><Progress value={i.reported_progress} /></td>
                  <td className="px-3 py-4">{i.verified_progress == null ? <span className="muted">—</span> : <Progress value={i.verified_progress} secondary />}</td>
                  <td className="px-3 py-4"><State value={i.status} /></td>
                  <td className="px-5 py-4"><div className="flex justify-end gap-1">{['D1','D2','D3','D4','D5'].map(d=><Impact key={d} label={d} value={i.contributions[d]||0}/>)}</div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="border-t hairline px-5 py-3 text-[10px] muted">* Verificado = promedio de actividades que tienen porcentaje numérico explícito en la instantánea. No se infieren porcentajes cuando Notion solo registra estado.</div>
      </div>
      {selected && <Detail initiative={selected} onClose={()=>setSelected(null)} onVerified={(updated)=>{setSelected(updated);setItems(prev=>prev.map(x=>x.code===updated.code?{...x,...updated,activities:[]}:x));}} />}
    </div>
  );
}

function Progress({value, secondary=false}:{value:number; secondary?:boolean}) {
  return <div className="flex items-center gap-2"><div className="h-1.5 w-16 overflow-hidden rounded-full bg-black/5 dark:bg-white/5"><div className="h-full rounded-full" style={{width:`${Math.max(0,Math.min(100,value))}%`,background:secondary?'var(--igmd)':'var(--igtd)'}}/></div><b className="metric">{value.toFixed(1)}%</b></div>;
}
function State({value}:{value:string}) { const c = value.toLowerCase().includes('completo')?'text-emerald-500 bg-emerald-500/10':value.toLowerCase().includes('no')?'text-rose-500 bg-rose-500/10':'text-amber-500 bg-amber-500/10'; return <span className={`rounded-full px-2 py-1 text-[10px] font-semibold ${c}`}>{value}</span>; }
function Impact({label,value}:{label:string;value:number}) { const opacity=[.06,.18,.40,.78][value] ?? .06; return <span title={`${label}: ${value}`} className="grid h-7 w-7 place-items-center rounded-lg border hairline text-[9px] font-semibold" style={{background:`rgba(0,163,255,${opacity})`}}>{label.replace('D','')}</span>; }

function Detail({initiative,onClose,onVerified}:{initiative:Initiative;onClose:()=>void;onVerified:(initiative:Initiative)=>void}) {
  const [verifyProgress,setVerifyProgress]=useState(initiative.verified_progress ?? initiative.analytical_progress);
  const [verifiedBy,setVerifiedBy]=useState(initiative.progress_verified_by ?? '');
  const [verificationNote,setVerificationNote]=useState(initiative.progress_verification_note ?? '');
  const [saving,setSaving]=useState(false);
  const [verificationError,setVerificationError]=useState('');

  async function saveVerification(){
    if(verifiedBy.trim().length<2 || verificationNote.trim().length<2){setVerificationError('Ingrese responsable y nota/evidencia de verificación.');return;}
    setSaving(true);setVerificationError('');
    try { const updated=await verifyInitiative(initiative.code,verifyProgress,verifiedBy,verificationNote); onVerified(updated); }
    catch(e){ setVerificationError(e instanceof Error?e.message:String(e)); }
    finally { setSaving(false); }
  }

  return <div className="fixed inset-0 z-[80] flex justify-end bg-black/35 backdrop-blur-sm" onClick={onClose}>
    <aside onClick={(e:any)=>e.stopPropagation()} className="h-full w-full max-w-[760px] overflow-y-auto border-l hairline bg-[color:var(--canvas)] p-5 shadow-2xl lg:p-7">
      <div className="flex items-start justify-between gap-4"><div><div className="eyebrow">{initiative.objective_code} · {initiative.objective_name}</div><h2 className="mt-2 text-2xl font-semibold tracking-[-.035em]">Iniciativa {initiative.code}</h2></div><button onClick={onClose} className="focus-ring rounded-xl border hairline p-2"><X size={17}/></button></div>
      <p className="mt-4 text-sm leading-6 muted">{initiative.description}</p>
      <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4"><Kpi l="Reportado" v={`${initiative.reported_progress.toFixed(2)}%`}/><Kpi l="Verificado" v={initiative.verified_progress==null?'—':`${initiative.verified_progress.toFixed(2)}%`}/><Kpi l="Actividades" v={`${initiative.activities.length}`}/><Kpi l="Evidencias" v={`${initiative.activities.reduce((sum,a)=>sum+a.evidence_count,0)}`}/></div>
      <div className="mt-5 rounded-2xl border hairline p-4"><div className="text-[10px] uppercase tracking-[.12em] muted">Liderazgo</div><div className="mt-2 flex flex-wrap gap-2">{initiative.leaders.map(l=><span key={l.name} className="rounded-full bg-black/5 px-3 py-1.5 text-xs dark:bg-white/5">{l.name}</span>)}</div>{initiative.notion_url&&<a href={initiative.notion_url} target="_blank" className="mt-3 inline-flex items-center gap-1 text-[11px] text-sky-500">Abrir fuente Notion <ExternalLink size={11}/></a>}</div>
      <div className="mt-5 rounded-2xl border hairline p-4">
        <div className="eyebrow">Avance verificado Eᵢ</div>
        <div className="mt-3 flex items-end justify-between"><div className="text-xs muted">El motor usa este valor sobre el reportado cuando existe.</div><div className="metric text-2xl font-semibold">{verifyProgress.toFixed(1)}%</div></div>
        <input type="range" min="0" max="100" step="0.5" value={verifyProgress} onChange={(e:any)=>setVerifyProgress(Number(e.target.value))} className="range mt-3 w-full" />
        <div className="mt-3 grid gap-2 sm:grid-cols-2"><input value={verifiedBy} onChange={(e:any)=>setVerifiedBy(e.target.value)} placeholder="Responsable de verificación" className="rounded-xl border hairline bg-transparent px-3 py-2 text-xs outline-none" /><input value={verificationNote} onChange={(e:any)=>setVerificationNote(e.target.value)} placeholder="Nota / referencia de evidencia" className="rounded-xl border hairline bg-transparent px-3 py-2 text-xs outline-none" /></div>
        <div className="mt-3 flex items-center justify-between gap-3"><div className="text-[10px] muted">{initiative.progress_verified_at ? `Última verificación: ${initiative.progress_verified_at}${initiative.progress_verified_by?` · ${initiative.progress_verified_by}`:''}` : 'Aún no existe una validación manual persistida.'}</div><button onClick={saveVerification} disabled={saving} className="focus-ring rounded-xl bg-[color:var(--text)] px-3 py-2 text-[10px] font-semibold text-[color:var(--canvas)] disabled:opacity-50">{saving?'Guardando…':'Guardar verificación'}</button></div>
        {verificationError&&<div className="mt-2 text-[10px] text-rose-500">{verificationError}</div>}
      </div>
      <div className="mt-7 flex items-end justify-between"><div><div className="eyebrow">Cadena operativa</div><h3 className="mt-1 text-lg font-semibold">Actividades y trazabilidad</h3></div><span className="text-[10px] muted">Responsables de fila cuando Notion los expone; fallback de liderazgo claramente marcado</span></div>
      <div className="mt-3 space-y-2">{initiative.activities.map(a=><ActivityCard key={a.id} a={a}/>)}</div>
    </aside>
  </div>;
}
function Kpi({l,v}:{l:string;v:string}){return <div className="rounded-2xl border hairline p-3"><div className="text-[10px] muted">{l}</div><div className="metric mt-1 text-lg font-semibold">{v}</div></div>}
function ActivityCard({a}:{a:Activity}) { const isPhase=a.activity_type==='phase'; return <div className={`rounded-2xl border hairline ${isPhase?'bg-black/[.025] p-3 dark:bg-white/[.025]':'p-4'}`}>
  <div className="flex items-start justify-between gap-4"><div><div className="text-[10px] font-semibold muted">{a.external_id} · {isPhase?'FASE':'ACTIVIDAD'}</div><div className={`mt-1 ${isPhase?'font-semibold':'text-xs font-medium leading-5'}`}>{a.title}</div></div>{a.progress!=null&&<div className="metric shrink-0 text-sm font-semibold">{a.progress.toFixed(0)}%</div>}</div>
  {!isPhase&&<><div className="mt-3 flex flex-wrap gap-2 text-[10px] muted">{a.state&&<span className="rounded-full border hairline px-2 py-1">{a.state}</span>}{a.priority&&<span className="rounded-full border hairline px-2 py-1">Prioridad {a.priority}</span>}{(a.start_date||a.end_date)&&<span className="rounded-full border hairline px-2 py-1">{a.start_date||'…'} → {a.end_date||'…'}</span>}{a.evidence_count>0&&<span className="rounded-full border hairline px-2 py-1">{a.evidence_count} evidencia(s)</span>}</div>{a.observation&&<p className="mt-3 text-[11px] leading-5 muted">{a.observation}</p>}<div className="mt-3 text-[10px] muted">Encargados: {a.assignees.slice(0,3).map(x=>x.name).join(', ') || 'No resuelto'}{a.assignees[0]?.source==='initiative_leader_fallback'?' · fallback de liderazgo':''}</div></>}
</div>}
