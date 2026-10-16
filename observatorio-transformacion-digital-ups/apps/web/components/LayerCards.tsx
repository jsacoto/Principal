'use client';
import { motion } from 'framer-motion';
import type { ExecutiveSummary } from '@/lib/types';

export function LayerCards({ data }: { data: ExecutiveSummary }) {
  const cards = [data.igmd, data.ioc, data.iko];
  return (
    <div className="grid gap-4 md:grid-cols-3">
      {cards.map((item, index) => (
        <motion.div key={item.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * .07 }} className="glass rounded-[24px] p-5">
          <div className="flex items-start justify-between gap-4">
            <div><div className="eyebrow">Capa {index + 1}</div><h3 className="mt-2 text-sm font-semibold">{item.label}</h3></div>
            <div className="h-2.5 w-2.5 rounded-full shadow-[0_0_18px_currentColor]" style={{ color: item.color, background: item.color }} />
          </div>
          <div className="mt-7 flex items-end justify-between"><div className="metric text-4xl font-semibold">{item.score_5.toFixed(2)}</div><div className="text-xs muted">/ 5,00</div></div>
          <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-black/5 dark:bg-white/5">
            <motion.div initial={{ width: 0 }} animate={{ width: `${Math.max(0, Math.min(100, item.normalized * 100))}%` }} className="h-full rounded-full" style={{ background: item.color }} />
          </div>
        </motion.div>
      ))}
    </div>
  );
}
