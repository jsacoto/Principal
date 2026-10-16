'use client';

import { useEffect, useState } from 'react';
import { getDimensions, getKeyResults, getKpis, getObjectives, getTraceability } from '@/lib/api';

export function ModelExplorer() {
  const [dimensions, setDimensions] = useState<any[]>([]);
  const [objectives, setObjectives] = useState<any[]>([]);
  const [krs, setKrs] = useState<any[]>([]);
  const [kpis, setKpis] = useState<any[]>([]);
  const [dimension, setDimension] = useState('D1');
  const [traceability, setTraceability] = useState<any[]>([]);

  useEffect(() => {
    Promise.all([getDimensions(), getObjectives(), getKeyResults(), getKpis(), getTraceability()]).then(([d, o, r, k, t]) => {
      setDimensions(d); setObjectives(o); setKrs(r); setKpis(k); setTraceability(t);
    });
  }, []);

  const selectedDimension = dimensions.find((item) => item.code === dimension);
  const currentKpis = kpis.filter((item) => item.dimension_code === dimension);
  const objective = objectives.find((item) => item.code === `O${dimension.replace('D', '')}`);
  const currentKrs = krs.filter((item) => item.objective_code === objective?.code);
  const currentTrace = traceability.filter((item) => [dimension, objective?.code].includes(item.from_key) || [dimension, objective?.code].includes(item.to_key)).slice(0, 12);

  return (
    <div className="space-y-5">
      <div>
        <div className="eyebrow">Modelo institucional · trazabilidad</div>
        <h1 className="mt-2 text-3xl font-semibold tracking-[-.04em]">Dimensiones, objetivos, KRs y KPIs</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 muted">Explore la cadena conceptual que alimenta los índices. Los KRs y KPIs de esta primera versión son datos mock marcados como <code>demo_seed</code>.</p>
      </div>
      <div className="grid gap-2 sm:grid-cols-5">
        {dimensions.map((item) => (
          <button key={item.code} onClick={() => setDimension(item.code)} className={`focus-ring rounded-2xl border hairline p-4 text-left transition ${dimension === item.code ? 'bg-sky-500/10 ring-1 ring-sky-500/30' : 'glass'}`}>
            <div className="text-xs font-semibold">{item.code}</div><div className="mt-1 text-[11px] leading-4 muted">{item.name}</div>
          </button>
        ))}
      </div>
      {selectedDimension && (
        <div className="grid gap-5 xl:grid-cols-[.72fr_1.28fr]">
          <section className="glass rounded-[28px] p-5 lg:p-6">
            <div className="eyebrow">{selectedDimension.code}</div><h2 className="mt-2 text-xl font-semibold">{selectedDimension.name}</h2>
            <p className="mt-3 text-sm leading-6 muted">{selectedDimension.description}</p>
            <div className="mt-6 grid grid-cols-2 gap-3"><Mini label="Peso IGMD" value={`${Math.round(selectedDimension.weight * 100)}%`} /><Mini label="Meta" value={`${selectedDimension.target.toFixed(1)} / 5`} /></div>
            {objective && <div className="mt-5 rounded-2xl border hairline p-4"><div className="text-[10px] uppercase tracking-[.12em] muted">Objetivo asociado</div><div className="mt-2 text-sm font-semibold">{objective.code}{objective.legacy_code ? ` · ${objective.legacy_code}` : ''}</div><div className="mt-1 text-xs leading-5 muted">{objective.name}</div></div>}
          </section>
          <section className="glass rounded-[28px] p-5 lg:p-6">
            <div className="grid gap-6 md:grid-cols-2">
              <div><div className="eyebrow">Cumplimiento estratégico</div><h3 className="mt-1 text-lg font-semibold">Key Results</h3><div className="mt-4 space-y-2">
                {currentKrs.length ? currentKrs.map((item) => <Measure key={item.code} code={item.code} title={item.title} value={item.compliance} current={`${item.current} ${item.unit}`} target={`${item.target} ${item.unit}`} color="var(--ioc)" source={item.source} />) : <Empty />}
              </div></div>
              <div><div className="eyebrow">Desempeño operativo</div><h3 className="mt-1 text-lg font-semibold">KPIs</h3><div className="mt-4 space-y-2">
                {currentKpis.length ? currentKpis.map((item) => <Measure key={item.code} code={item.code} title={item.title} value={item.normalized} current={`${item.current} ${item.unit}`} target={`${item.target} ${item.unit}`} color="var(--iko)" source={item.source} />) : <Empty />}
              </div></div>
            </div>
          </section>
          <section className="glass rounded-[28px] p-5 lg:p-6 xl:col-span-2">
            <div className="eyebrow">Cadena de trazabilidad</div><h3 className="mt-1 text-lg font-semibold">Relaciones activas de {dimension}{objective ? ` / ${objective.code}` : ''}</h3>
            <div className="mt-4 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
              {currentTrace.length ? currentTrace.map((edge, index) => <div key={`${edge.from_type}-${edge.from_key}-${edge.to_type}-${edge.to_key}-${index}`} className="rounded-2xl border hairline p-3 text-xs"><div className="font-semibold">{edge.from_type}:{edge.from_key}</div><div className="my-1 text-[10px] muted">{edge.relation} →</div><div>{edge.to_type}:{edge.to_key}</div><div className="mt-2 text-[10px] muted">{edge.source}{edge.weight != null ? ` · peso ${edge.weight}` : ''}</div></div>) : <Empty />}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

function Mini({ label, value }: { label: string; value: string }) {
  return <div className="rounded-2xl border hairline p-3"><div className="text-[10px] muted">{label}</div><div className="metric mt-1 text-lg font-semibold">{value}</div></div>;
}

function Measure({ code,title,value,current,target,color,source }: { code:string;title:string;value:number;current:string;target:string;color:string;source:string }) {
  return <div className="rounded-2xl border hairline p-3"><div className="flex items-start justify-between gap-3"><div><div className="text-[10px] font-semibold muted">{code} · {source}</div><div className="mt-1 text-xs font-medium leading-5">{title}</div></div><div className="metric text-sm font-semibold">{(value * 100).toFixed(0)}%</div></div><div className="mt-3 h-1.5 overflow-hidden rounded-full bg-black/5 dark:bg-white/5"><div className="h-full rounded-full" style={{ width: `${value * 100}%`, background: color }} /></div><div className="mt-2 flex justify-between text-[10px] muted"><span>Actual {current}</span><span>Meta {target}</span></div></div>;
}

function Empty() { return <div className="rounded-2xl border hairline p-4 text-xs muted">Sin métricas cargadas.</div>; }
