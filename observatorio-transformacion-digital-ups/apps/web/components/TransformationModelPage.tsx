'use client';

import { motion } from 'framer-motion';
import { ArrowRight, BarChart3, Binary, Boxes, CheckCircle2, Gauge, Goal, Network } from 'lucide-react';

const objectives = [
  ['O1', 'Flexibilizar la oferta académica', 'Alinea la oferta, modalidades y experiencias de aprendizaje con nuevas necesidades académicas y digitales.'],
  ['O2', 'Mejorar experiencia del estudiante y colaborador', 'Integra procesos, servicios, autoservicios y experiencia omnicanal para la comunidad universitaria.'],
  ['O3', 'Asegurar sostenibilidad económica con datos y modelos predictivos', 'Fortalece decisiones financieras y académicas mediante analítica, predicción y gestión integrada de información.'],
  ['O4', 'Articular docencia, investigación y vinculación', 'Conecta capacidades académicas, investigación aplicada, innovación, empleabilidad y transferencia.'],
  ['O5', 'Universidad Cero Emisiones', 'Orienta la transformación digital hacia sostenibilidad ambiental, eficiencia energética y reducción de huella.'],
];

const layers = [
  {
    number: '01',
    title: 'Madurez Estructural',
    code: 'IGMD',
    icon: Boxes,
    color: 'var(--igmd)',
    text: 'Evalúa el avance verificado de las iniciativas y su contribución ponderada a las cinco dimensiones D1–D5.',
    formula: 'C_d = Σ(E_i · I_i,d) / Σ(I_i,d)  →  M_d = 5 · C_d  →  IGMD = Σ(v_d · M_d)',
  },
  {
    number: '02',
    title: 'Cumplimiento Estratégico',
    code: 'IOC',
    icon: Goal,
    color: 'var(--ioc)',
    text: 'Mide el grado de cumplimiento de los objetivos estratégicos a través de Key Results normalizados y ponderados.',
    formula: 'O_o = Σ(w_kr · c_kr)  →  IOC = Σ(α_o · O_o)  →  IOC(5) = 5 · IOC',
  },
  {
    number: '03',
    title: 'Desempeño Operativo',
    code: 'IKO',
    icon: Gauge,
    color: 'var(--iko)',
    text: 'Integra KPIs operativos normalizados para evidenciar si la transformación produce resultados medibles en la operación.',
    formula: 'n_k ∈ [0,1]  →  IKO = Σ(β_k · n_k)  →  IKO(5) = 5 · IKO',
  },
];

export function TransformationModelPage() {
  return (
    <div className="space-y-6">
      <section className="glass overflow-hidden rounded-[32px] p-6 lg:p-9">
        <div className="grid gap-8 lg:grid-cols-[1.05fr_.95fr] lg:items-center">
          <div>
            <div className="eyebrow">Modelo institucional de gobernanza digital</div>
            <h1 className="mt-3 max-w-4xl text-4xl font-semibold tracking-[-.055em] lg:text-6xl">Transformación Digital UPS en tres capas conectadas</h1>
            <p className="mt-5 max-w-3xl text-sm leading-7 muted">
              El Observatorio no funciona como un formulario aislado. El modelo conecta el avance de las iniciativas con dimensiones, objetivos, resultados clave, indicadores operativos y evidencias para construir una lectura trazable de la transformación digital.
            </p>
            <div className="mt-6 flex flex-wrap gap-2 text-[11px]">
              {['Iniciativa Eᵢ', 'Dimensión D1–D5', 'Objetivo O1–O5', 'KR', 'KPI', 'Evidencia', 'IGTD'].map((item, index, list) => (
                <div key={item} className="flex items-center gap-2">
                  <span className="rounded-full border hairline px-3 py-1.5 font-medium">{item}</span>
                  {index < list.length - 1 && <ArrowRight size={12} className="muted" />}
                </div>
              ))}
            </div>
          </div>
          <div className="relative mx-auto grid aspect-square w-full max-w-[390px] place-items-center rounded-full border hairline bg-black/[.018] dark:bg-white/[.02]">
            <div className="absolute inset-[13%] rounded-full border border-dashed hairline" />
            <div className="absolute inset-[27%] rounded-full border hairline" />
            <div className="grid h-28 w-28 place-items-center rounded-full bg-emerald-500/10 text-center shadow-[0_0_70px_rgba(0,230,118,.16)]">
              <div><div className="metric text-2xl font-semibold text-emerald-500">IGTD</div><div className="mt-1 text-[10px] muted">Índice Global</div></div>
            </div>
            <Node className="left-[7%] top-[24%]" label="IGMD" color="var(--igmd)" />
            <Node className="right-[6%] top-[24%]" label="IOC" color="var(--ioc)" />
            <Node className="bottom-[7%] left-1/2 -translate-x-1/2" label="IKO" color="var(--iko)" />
          </div>
        </div>
      </section>

      <section>
        <div className="eyebrow">Motor analítico</div>
        <h2 className="mt-2 text-2xl font-semibold tracking-[-.035em]">Tres capas, una sola cadena de trazabilidad</h2>
        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          {layers.map((layer, index) => {
            const Icon = layer.icon;
            return (
              <motion.article key={layer.code} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * .08 }} className="glass rounded-[26px] p-5 lg:p-6">
                <div className="flex items-start justify-between gap-4">
                  <div><div className="eyebrow">Capa {layer.number}</div><h3 className="mt-2 text-lg font-semibold">{layer.title}</h3></div>
                  <div className="grid h-10 w-10 place-items-center rounded-2xl" style={{ background: `color-mix(in srgb, ${layer.color} 12%, transparent)`, color: layer.color }}><Icon size={19} /></div>
                </div>
                <div className="metric mt-5 text-4xl font-semibold" style={{ color: layer.color }}>{layer.code}</div>
                <p className="mt-3 text-sm leading-6 muted">{layer.text}</p>
                <div className="mt-5 rounded-2xl border hairline bg-black/[.018] p-3 font-mono text-[10px] leading-5 dark:bg-white/[.025]">{layer.formula}</div>
              </motion.article>
            );
          })}
        </div>
      </section>

      <section className="glass rounded-[30px] p-6 lg:p-8">
        <div className="grid gap-7 lg:grid-cols-[.6fr_1.4fr]">
          <div>
            <div className="eyebrow">Síntesis institucional</div>
            <h2 className="mt-2 text-2xl font-semibold tracking-[-.035em]">Índice Global Ajustado</h2>
            <p className="mt-3 text-sm leading-6 muted">La configuración estándar prioriza la madurez estructural, sin perder la conexión con estrategia y operación.</p>
            <div className="mt-5 rounded-2xl border hairline p-4 font-mono text-xs">IGTD = 0,50·IGMD + 0,30·IOC(5) + 0,20·IKO(5)</div>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <Weight title="Madurez" value="50%" icon={Boxes} color="var(--igmd)" />
            <Weight title="OKRs" value="30%" icon={Goal} color="var(--ioc)" />
            <Weight title="KPIs" value="20%" icon={BarChart3} color="var(--iko)" />
          </div>
        </div>
      </section>

      <section>
        <div className="eyebrow">Objetivos estratégicos</div>
        <h2 className="mt-2 text-2xl font-semibold tracking-[-.035em]">O1–O5</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
          {objectives.map(([code, title, text]) => (
            <article key={code} className="glass rounded-[24px] p-5">
              <div className="metric text-3xl font-semibold text-violet-500">{code}</div>
              <h3 className="mt-3 text-sm font-semibold leading-5">{title}</h3>
              <p className="mt-2 text-xs leading-5 muted">{text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="glass rounded-[30px] p-6 lg:p-8">
        <div className="flex items-start gap-4">
          <div className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-emerald-500/10 text-emerald-500"><Network size={20} /></div>
          <div>
            <div className="eyebrow">Principio de gobernanza</div>
            <h2 className="mt-1 text-xl font-semibold">La evidencia precede al índice</h2>
            <p className="mt-3 max-w-5xl text-sm leading-6 muted">Los responsables autorizados actualizan actividades, justifican los cambios y adjuntan evidencias. El sistema conserva trazabilidad de quién modificó cada avance, cuándo lo hizo y con qué sustento. Así, el índice no es una cifra aislada sino la salida de una cadena auditable.</p>
            <div className="mt-4 flex flex-wrap gap-2 text-[11px]">
              {['Control de acceso', 'Registro de cambios', 'Evidencia documental', 'Trazabilidad', 'Priorización de brechas'].map(x => <span key={x} className="inline-flex items-center gap-1.5 rounded-full border hairline px-3 py-1.5"><CheckCircle2 size={12} className="text-emerald-500" />{x}</span>)}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function Node({ className, label, color }: { className: string; label: string; color: string }) {
  return <div className={`absolute grid h-16 w-16 place-items-center rounded-2xl border hairline glass ${className}`}><span className="metric text-sm font-semibold" style={{ color }}>{label}</span></div>;
}

function Weight({ title, value, icon: Icon, color }: { title: string; value: string; icon: any; color: string }) {
  return <div className="rounded-[22px] border hairline p-5"><div className="grid h-10 w-10 place-items-center rounded-2xl" style={{ color, background: `color-mix(in srgb, ${color} 12%, transparent)` }}><Icon size={18} /></div><div className="metric mt-6 text-4xl font-semibold">{value}</div><div className="mt-1 text-xs muted">{title}</div></div>;
}
