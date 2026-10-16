'use client';

import { useEffect, useMemo, useState } from 'react';
import { ArrowRight, Gauge, TrendingUp } from 'lucide-react';
import { getGaps, getInitiatives, runWhatIf } from '@/lib/api';
import type { Initiative, WhatIf } from '@/lib/types';

export function WhatIfSimulator() {
  const [items, setItems] = useState<Initiative[]>([]);
  const [code, setCode] = useState('1.a');
  const [value, setValue] = useState(100);
  const [result, setResult] = useState<WhatIf | null>(null);
  const scope = 'all' as const;
  const [busy, setBusy] = useState(false);
  const [gaps, setGaps] = useState<any>({initiatives:[], key_results:[]});

  useEffect(()=>{ getInitiatives(false).then(data => { setItems(data); if(data[0]) { setCode(data[0].code); setValue(data[0].analytical_progress); } }); },[]);
  useEffect(()=>{ getGaps(scope).then(setGaps); },[]);
  const selected = useMemo(()=>items.find(i=>i.code===code),[items,code]);

  useEffect(()=>{
    if (!selected) return;
    setValue(selected.analytical_progress);
    setResult(null);
  },[code,selected]);

  async function simulate() {
    setBusy(true);
    try { setResult(await runWhatIf(code,value,scope)); } finally { setBusy(false); }
  }

  return <div className="space-y-5">
    <div><div className="eyebrow">Prioridad de inversión · análisis de sensibilidad</div><h1 className="mt-2 text-3xl font-semibold tracking-[-.04em]">Simulador What-If</h1><p className="mt-2 max-w-3xl text-sm leading-6 muted">Modifique Eᵢ y mida el efecto proyectado sobre M_d, IGMD e IGTD. La simulación aplica ΔM_d/ΔE_i = 5·I_i,d / ΣI_i,d sobre la matriz activa.</p></div>
    <div className="grid gap-5 xl:grid-cols-[.72fr_1.28fr]">
      <section className="glass rounded-[28px] p-5 lg:p-6">
        <div className="eyebrow">Escenario</div>
        <label className="mt-5 block text-xs font-semibold">Iniciativa</label>
        <select value={code} onChange={(e:any)=>setCode(e.target.value)} className="mt-2 w-full rounded-2xl border hairline bg-transparent px-3 py-3 text-sm outline-none">
          {items.map(i=><option key={i.code} value={i.code}>{i.code} · {i.scope || i.objective_code}</option>)}
        </select>
        <div className="mt-5 rounded-2xl border hairline p-4">
          <div className="text-xs font-semibold">{selected?.description || 'Seleccione una iniciativa'}</div>
          <div className="mt-3 flex flex-wrap gap-1.5">{selected && ['D1','D2','D3','D4','D5'].map(d=><span key={d} className="rounded-lg border hairline px-2 py-1 text-[10px]">{d}: {selected.contributions[d]||0}</span>)}</div>
        </div>
        <div className="mt-6 flex items-end justify-between"><label className="text-xs font-semibold">Avance simulado Eᵢ</label><div className="metric text-3xl font-semibold">{value.toFixed(0)}%</div></div>
        <input type="range" min="0" max="100" step="1" value={value} onChange={(e:any)=>setValue(Number(e.target.value))} className="range mt-4 w-full" />
        <div className="mt-2 flex justify-between text-[10px] muted"><span>0%</span><span>Estado actual: {selected?.analytical_progress.toFixed(1) || 0}%</span><span>100%</span></div>
        <div className="mt-5 flex items-center gap-2">
          <button onClick={simulate} disabled={busy||!selected} className="focus-ring flex-1 rounded-2xl bg-[color:var(--text)] px-4 py-3 text-xs font-semibold text-[color:var(--canvas)] disabled:opacity-50">{busy?'Calculando…':'Simular impacto'}</button>
          <span className="rounded-2xl border hairline px-3 py-3 text-[10px] muted">Portafolio operativo · 29 páginas</span>
        </div>
      </section>
      <section className="glass rounded-[28px] p-5 lg:p-6">
        <div className="flex items-start justify-between"><div><div className="eyebrow">Resultado</div><h2 className="mt-1 text-lg font-semibold">Impacto proyectado</h2></div><Gauge className="text-emerald-500" size={22}/></div>
        {!result ? <div className="grid min-h-[390px] place-items-center text-center"><div><div className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-emerald-500/10 text-emerald-500"><TrendingUp size={20}/></div><div className="mt-3 text-sm font-medium">Construya un escenario</div><div className="mt-1 text-xs muted">El motor recalculará las cinco dimensiones y el IGTD.</div></div></div> : <Results r={result}/>}
      </section>
    </div>
    <section className="glass rounded-[28px] p-5 lg:p-6">
      <div className="eyebrow">Priorización automática</div><h2 className="mt-1 text-lg font-semibold">Brechas que requieren atención</h2>
      <div className="mt-4 grid gap-5 lg:grid-cols-2">
        <div><div className="text-xs font-semibold">Iniciativas sobre dimensiones con M_d &lt; 3,0</div><div className="mt-3 space-y-2">{gaps.initiatives.slice(0,8).map((x:any)=><div key={`${x.initiative}-${x.dimension}`} className="flex items-center justify-between rounded-2xl border hairline p-3 text-xs"><div><b>Iniciativa {x.initiative}</b><div className="mt-1 muted">{x.dimension} · contribución {x.contribution}</div></div><div className="text-right"><div className="metric font-semibold">S {x.sensitivity.toFixed(3)}</div><div className="mt-1 text-[10px] muted">M {x.maturity.toFixed(2)}</div></div></div>)}</div></div>
        <div><div className="text-xs font-semibold">KRs por debajo de 60%</div><div className="mt-3 space-y-2">{gaps.key_results.length?gaps.key_results.map((x:any)=><div key={x.kr} className="flex items-center justify-between rounded-2xl border hairline p-3 text-xs"><b>{x.kr}</b><span className="metric font-semibold text-rose-500">{(x.compliance*100).toFixed(1)}%</span></div>):<div className="rounded-2xl border hairline p-4 text-xs muted">No hay KRs bajo el umbral.</div>}</div></div>
      </div>
    </section>
  </div>
}

function Results({r}:{r:WhatIf}) {
  return <div className="mt-6">
    <div className="grid gap-3 sm:grid-cols-2"><Metric label="IGMD" before={r.original_igmd} after={r.simulated_igmd}/><Metric label="IGTD" before={r.original_igtd} after={r.simulated_igtd} accent/></div>
    <div className="mt-6"><div className="text-xs font-semibold">Δ por dimensión</div><div className="mt-3 grid gap-2 sm:grid-cols-5">{Object.entries(r.dimension_deltas).map(([d,delta])=><div key={d} className="rounded-2xl border hairline p-3 text-center"><div className="text-[10px] muted">{d}</div><div className={`metric mt-1 text-lg font-semibold ${delta>0?'text-emerald-500':delta<0?'text-rose-500':''}`}>{delta>=0?'+':''}{delta.toFixed(3)}</div></div>)}</div></div>
    <div className="mt-6 rounded-2xl border hairline p-4 text-xs leading-5 muted">IGTD cambia <b className="metric text-[color:var(--text)]">{r.delta_igtd>=0?'+':''}{r.delta_igtd.toFixed(4)}</b>. El simulador no modifica la base de datos; solo calcula el escenario.</div>
  </div>
}

function Metric({label,before,after,accent=false}:{label:string;before:number;after:number;accent?:boolean}) {
  const delta=after-before;
  return <div className="rounded-2xl border hairline p-4"><div className="text-[10px] uppercase tracking-[.12em] muted">{label}</div><div className="mt-3 flex items-center gap-3"><span className="metric text-2xl font-semibold">{before.toFixed(2)}</span><ArrowRight size={15} className="muted"/><span className={`metric text-3xl font-semibold ${accent?'text-emerald-500':'text-sky-500'}`}>{after.toFixed(2)}</span></div><div className={`metric mt-2 text-xs ${delta>=0?'text-emerald-500':'text-rose-500'}`}>{delta>=0?'+':''}{delta.toFixed(4)}</div></div>;
}
