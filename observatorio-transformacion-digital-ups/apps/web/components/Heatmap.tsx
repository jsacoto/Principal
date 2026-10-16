'use client';

export function Heatmap({ data }: { data: Record<string, Record<string, number>> }) {
  const objectives = Object.keys(data).sort();
  const dimensions = ['D1','D2','D3','D4','D5'];
  const bg = ['rgba(127,127,127,.06)','rgba(0,163,255,.16)','rgba(0,163,255,.38)','rgba(0,163,255,.72)'];
  return (
    <section className="glass rounded-[28px] p-5 lg:p-6">
      <div className="eyebrow">Alineación estratégica</div>
      <h2 className="mt-1 text-lg font-semibold">Objetivos × Dimensiones</h2>
      <p className="mt-1 text-xs muted">Intensidad institucional editable: 0 nulo · 1 bajo · 2 medio · 3 alto.</p>
      <div className="mt-6 overflow-x-auto">
        <div className="grid min-w-[520px] grid-cols-[70px_repeat(5,minmax(70px,1fr))] gap-2 text-center text-xs">
          <div />{dimensions.map(d => <div key={d} className="py-2 font-semibold">{d}</div>)}
          {objectives.map(o => (
            <div className="contents" key={o}>
              <div className="flex items-center justify-start font-semibold">{o}</div>
              {dimensions.map(d => {
                const value = data[o]?.[d] ?? 0;
                return <div key={`${o}-${d}`} className="grid h-12 place-items-center rounded-xl border hairline metric font-semibold" style={{ background: bg[value] }}>{value}</div>;
              })}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
