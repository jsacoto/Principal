'use client';

import { motion } from 'framer-motion';

export function HeroGauge({ value, weights }: { value: number; weights: { igmd: number; ioc: number; iko: number } }) {
  const max = 5;
  const pct = Math.max(0, Math.min(1, value / max));
  const radius = 108;
  const cx = 130;
  const cy = 126;
  const start = -210;
  const sweep = 240;
  const point = (angle: number) => {
    const r = (Math.PI / 180) * angle;
    return { x: cx + radius * Math.cos(r), y: cy + radius * Math.sin(r) };
  };
  const arc = (fraction: number) => {
    const a0 = point(start);
    const a1 = point(start + sweep * fraction);
    const large = sweep * fraction > 180 ? 1 : 0;
    return `M ${a0.x} ${a0.y} A ${radius} ${radius} 0 ${large} 1 ${a1.x} ${a1.y}`;
  };

  return (
    <section className="glass relative overflow-hidden rounded-[30px] p-6 lg:p-8">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_28%,rgba(0,230,118,.12),transparent_42%)]" />
      <div className="relative grid items-center gap-6 lg:grid-cols-[1fr_310px]">
        <div>
          <div className="eyebrow">Índice Global Ajustado de Transformación Digital</div>
          <div className="mt-2 flex items-end gap-3">
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="metric text-6xl font-semibold tracking-[-0.06em] lg:text-8xl">{value.toFixed(2)}</motion.div>
            <div className="mb-2 text-sm muted">/ 5,00</div>
          </div>
          <p className="mt-4 max-w-2xl text-sm leading-6 muted">
            Síntesis ponderada de madurez estructural, cumplimiento estratégico y desempeño operativo. La lectura no reemplaza la trazabilidad: cada punto puede rastrearse hasta iniciativa, KR, KPI y evidencia.
          </p>
          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            <Weight label="Madurez Estructural" value={weights.igmd} color="var(--igmd)" />
            <Weight label="Cumplimiento OKR" value={weights.ioc} color="var(--ioc)" />
            <Weight label="Desempeño KPI" value={weights.iko} color="var(--iko)" />
          </div>
        </div>
        <div className="relative mx-auto h-[250px] w-[260px]">
          <svg viewBox="0 0 260 250" className="h-full w-full overflow-visible" aria-label={`IGTD ${value.toFixed(2)} de 5`}>
            <path d={arc(1)} fill="none" stroke="rgba(127,127,127,.16)" strokeWidth="16" strokeLinecap="round" />
            <motion.path d={arc(pct)} fill="none" stroke="var(--igtd)" strokeWidth="16" strokeLinecap="round"
              initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 1.1, ease: [0.2, 0.8, 0.2, 1] }} />
          </svg>
          <div className="absolute inset-0 grid place-items-center pt-7 text-center">
            <div>
              <div className="metric text-4xl font-semibold">{(pct * 100).toFixed(0)}%</div>
              <div className="mt-1 text-[11px] font-medium uppercase tracking-[.14em] muted">de escala máxima</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Weight({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="rounded-2xl border hairline bg-black/[.018] p-3 dark:bg-white/[.025]">
      <div className="mb-2 h-1 w-10 rounded-full" style={{ background: color }} />
      <div className="metric text-xl font-semibold">{Math.round(value * 100)}%</div>
      <div className="mt-0.5 text-[11px] muted">{label}</div>
    </div>
  );
}
