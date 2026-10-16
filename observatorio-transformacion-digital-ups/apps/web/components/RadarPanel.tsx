'use client';

import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';
import type { DimensionMetric } from '@/lib/types';

export function RadarPanel({ dimensions, reference }: { dimensions: DimensionMetric[]; reference: Record<string, number> }) {
  const chart = dimensions.map(d => ({
    code: d.code,
    label: `${d.code}`,
    actual: Number(d.maturity.toFixed(2)),
    reference: reference[d.code] ?? 0,
    target: 5,
    name: d.name,
    coverage: d.coverage,
    initiatives: d.initiatives,
  }));
  return (
    <section className="glass rounded-[28px] p-5 lg:p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="eyebrow">Madurez estructural</div>
          <h2 className="mt-1 text-lg font-semibold">Radar pentagonal D1–D5</h2>
          <p className="mt-1 text-xs muted">Estado calculado, referencia inicial del modelo y meta transformadora 5,0.</p>
        </div>
        <div className="hidden text-right text-[10px] muted sm:block">Hover para trazabilidad<br/>por dimensión</div>
      </div>
      <div className="mt-3 h-[390px]">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={chart} outerRadius="72%">
            <PolarGrid stroke="rgba(127,127,127,.18)" />
            <PolarAngleAxis dataKey="label" tick={{ fill: 'currentColor', fontSize: 12, fontWeight: 700 }} />
            <PolarRadiusAxis domain={[0, 5]} tickCount={6} tick={{ fill: '#8b93a0', fontSize: 9 }} axisLine={false} />
            <Radar name="Meta Transformadora" dataKey="target" stroke="rgba(127,127,127,.45)" fill="rgba(127,127,127,.03)" strokeDasharray="4 4" />
            <Radar name="Referencia" dataKey="reference" stroke="#8A2BE2" fill="#8A2BE2" fillOpacity={0.05} />
            <Radar name="Estado actual" dataKey="actual" stroke="#00A3FF" fill="#00A3FF" fillOpacity={0.19} strokeWidth={2.4} />
            <Tooltip content={<RadarTooltip />} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <div className="flex flex-wrap gap-4 text-[11px] muted">
        <Legend color="#00A3FF" label="Calculado" /><Legend color="#8A2BE2" label="Referencia" /><Legend color="rgba(127,127,127,.55)" label="Meta 5,0" />
      </div>
    </section>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  return <span className="inline-flex items-center gap-2"><i className="h-2 w-2 rounded-full" style={{ background: color }} />{label}</span>;
}

function RadarTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const p = payload[0]?.payload;
  return (
    <div className="glass max-w-[270px] rounded-2xl p-3 text-xs shadow-2xl">
      <div className="font-semibold">{p.code} · {p.name}</div>
      <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 muted">
        <span>Madurez</span><b className="metric text-right text-[color:var(--text)]">{p.actual.toFixed(2)}</b>
        <span>Cobertura</span><b className="metric text-right text-[color:var(--text)]">{(p.coverage * 100).toFixed(1)}%</b>
        <span>Iniciativas</span><b className="metric text-right text-[color:var(--text)]">{p.initiatives.length}</b>
      </div>
    </div>
  );
}
