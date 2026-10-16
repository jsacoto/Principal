'use client';

import { useEffect, useState } from 'react';
import { AlertTriangle, Database, FileCheck2, ListChecks, ShieldCheck } from 'lucide-react';
import { getQuality, getSummary } from '@/lib/api';
import type { ExecutiveSummary, QualityIssue } from '@/lib/types';
import { HeroGauge } from './HeroGauge';
import { LayerCards } from './LayerCards';
import { RadarPanel } from './RadarPanel';
import { Heatmap } from './Heatmap';

export function DashboardClient() {
  const [scope, setScope] = useState<'all'|'institutional16'>('all');
  const [data, setData] = useState<ExecutiveSummary | null>(null);
  const [quality, setQuality] = useState<{count:number;critical:number;high:number;issues:QualityIssue[]} | null>(null);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    let active = true;
    setError('');
    Promise.all([getSummary(scope), getQuality()])
      .then(([summary, q]) => { if (active) { setData(summary); setQuality(q); } })
      .catch((e) => active && setError(e instanceof Error ? e.message : String(e)));
    return () => { active = false; };
  }, [scope]);

  if (error) return <ErrorState error={error} />;
  if (!data) return <Loading />;

  return (
    <div className="space-y-5 lg:space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <div className="eyebrow">Gobernanza continua · UPS</div>
          <h1 className="mt-2 text-3xl font-semibold tracking-[-.04em] lg:text-4xl">Observatorio de Transformación Digital</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 muted">Madurez estructural → OKRs → KPIs → evidencias → índices sintéticos. Una sola cadena de trazabilidad para dirección, investigación y operación.</p>
        </div>
        <div className="glass flex rounded-2xl p-1 text-xs">
          <button onClick={() => setScope('all')} className={`focus-ring rounded-xl px-3 py-2 transition ${scope==='all'?'bg-[color:var(--text)] text-[color:var(--canvas)]':'muted hover:text-[color:var(--text)]'}`}>Portafolio actual</button>
          <button onClick={() => setScope('institutional16')} className={`focus-ring rounded-xl px-3 py-2 transition ${scope==='institutional16'?'bg-[color:var(--text)] text-[color:var(--canvas)]':'muted hover:text-[color:var(--text)]'}`}>Modelo 16 agregado</button>
        </div>
      </div>

      <HeroGauge value={data.igtd} weights={data.layer_weights} />
      <LayerCards data={data} />

      <div className="grid gap-5 xl:grid-cols-[1.22fr_.78fr]">
        <RadarPanel dimensions={data.dimensions} reference={data.reference_maturity} />
        <Heatmap data={data.heatmap} />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MiniStat icon={Database} label="Iniciativas analizadas" value={data.portfolio_count} />
        <MiniStat icon={ListChecks} label="Actividades registradas" value={data.activity_count} />
        <MiniStat icon={FileCheck2} label="Referencias de evidencia" value={data.evidence_count} />
        <MiniStat icon={quality?.critical ? AlertTriangle : ShieldCheck} label="Alertas críticas de calidad" value={quality?.critical ?? 0} accent={!!quality?.critical} />
      </div>

      <section className="glass rounded-[28px] p-5 lg:p-6">
        <div className="grid gap-6 lg:grid-cols-[.8fr_1.2fr]">
          <div>
            <div className="eyebrow">Cumplimiento estratégico</div>
            <h2 className="mt-1 text-lg font-semibold">Objetivos O1–O5</h2>
            <p className="mt-2 text-xs leading-5 muted">OB1–OB4 de la cartera histórica se normalizan a O1–O4. O5 incorpora Universidad Cero Emisiones como objetivo del modelo ampliado.</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {data.objectives.map(o => (
              <div key={o.code} className="rounded-2xl border hairline bg-black/[.018] p-4 dark:bg-white/[.025]">
                <div className="flex items-center justify-between gap-4">
                  <span className="text-xs font-semibold">{o.code}{o.legacy_code ? ` · ${o.legacy_code}` : ''}</span>
                  <span className="metric text-sm font-semibold">{o.score_5.toFixed(2)} / 5</span>
                </div>
                <div className="mt-2 text-xs muted">{o.name}</div>
                <div className="mt-3 h-1 overflow-hidden rounded-full bg-black/5 dark:bg-white/5"><div className="h-full rounded-full bg-[color:var(--ioc)]" style={{width:`${o.compliance*100}%`}} /></div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {quality && quality.issues.length > 0 && (
        <section className="glass rounded-[28px] p-5 lg:p-6">
          <div className="flex items-center justify-between gap-4">
            <div><div className="eyebrow">Gobernanza del dato</div><h2 className="mt-1 text-lg font-semibold">Alertas de consistencia de Notion</h2></div>
            <span className="rounded-full border hairline px-3 py-1 text-xs muted">{quality.count} hallazgos</span>
          </div>
          <div className="mt-4 grid gap-2">
            {quality.issues.slice(0, 6).map((issue, idx) => (
              <div key={`${issue.initiative}-${issue.activity}-${idx}`} className="flex gap-3 rounded-2xl border hairline p-3 text-xs">
                <div className={`mt-1 h-2 w-2 shrink-0 rounded-full ${issue.severity==='critical'?'bg-red-500':'bg-amber-500'}`} />
                <div><b>Iniciativa {issue.initiative}{issue.activity ? ` · ${issue.activity}` : ''}</b><div className="mt-1 muted">{issue.message}</div></div>
              </div>
            ))}
          </div>
        </section>
      )}

      <div className="rounded-2xl border hairline p-4 text-xs leading-5 muted">
        {data.data_notes.map(note => <div key={note}>• {note}</div>)}
      </div>
    </div>
  );
}

function MiniStat({ icon: Icon, label, value, accent=false }: { icon:any; label:string; value:number; accent?:boolean }) {
  return <div className="glass rounded-[22px] p-4"><div className="flex items-center gap-3"><div className={`grid h-9 w-9 place-items-center rounded-xl ${accent?'bg-red-500/10 text-red-500':'bg-sky-500/10 text-sky-500'}`}><Icon size={17}/></div><div><div className="metric text-2xl font-semibold">{value}</div><div className="text-[11px] muted">{label}</div></div></div></div>;
}

function Loading() { return <div className="grid min-h-[60vh] place-items-center"><div className="text-sm muted">Calculando madurez, OKRs y KPIs…</div></div>; }
function ErrorState({error}:{error:string}) { return <div className="glass rounded-3xl p-8"><div className="font-semibold">No se pudo cargar el observatorio</div><pre className="mt-3 whitespace-pre-wrap text-xs muted">{error}</pre></div>; }
