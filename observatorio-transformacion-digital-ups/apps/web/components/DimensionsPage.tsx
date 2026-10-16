'use client';

import { motion } from 'framer-motion';
import { BookOpenCheck, Building2, FlaskConical, Leaf, LineChart, type LucideIcon } from 'lucide-react';

const dimensions: Array<{
  code: string;
  title: string;
  objective: string;
  icon: LucideIcon;
  color: string;
  summary: string;
  areas: string[];
  questions: string[];
}> = [
  {
    code: 'D1', title: 'Oferta Académica y Aprendizaje Digital', objective: 'Principalmente O1', icon: BookOpenCheck, color: '#00A3FF',
    summary: 'Evalúa cómo la UPS transforma su propuesta académica, las modalidades de aprendizaje y las capacidades digitales necesarias para una oferta flexible y pertinente.',
    areas: ['LMS y ecosistemas de aprendizaje', 'Objetos y recursos abiertos/reutilizables (ORA/RLO)', 'Movilidad y flexibilidad académica', 'Competencias digitales', 'Diseño de experiencias híbridas y virtuales'],
    questions: ['¿La tecnología amplía realmente la flexibilidad académica?', '¿Los recursos digitales mejoran acceso, permanencia y egreso?', '¿Docentes y estudiantes desarrollan capacidades digitales medibles?'],
  },
  {
    code: 'D2', title: 'Experiencia Universitaria y Procesos', objective: 'Principalmente O2', icon: Building2, color: '#8A2BE2',
    summary: 'Mide la digitalización de servicios y procesos, la experiencia de estudiantes y colaboradores y la capacidad institucional de operar de forma integrada y omnicanal.',
    areas: ['SLA y tiempos de atención', 'CRM y visión 360° de usuarios', 'Digitalización omnicanal', 'CSAT / NPS', 'Autoservicios', 'Interoperabilidad de procesos'],
    questions: ['¿Los servicios son más simples y rápidos?', '¿La experiencia es consistente entre canales?', '¿Los procesos eliminan fricción y reprocesos?'],
  },
  {
    code: 'D3', title: 'Sostenibilidad Económica y Analítica de Datos', objective: 'Principalmente O3', icon: LineChart, color: '#FF9500',
    summary: 'Valora el uso de datos y modelos analíticos para sostenibilidad económica, retención, planificación, recaudación y toma de decisiones basada en evidencia.',
    areas: ['Modelos predictivos de retención', 'Unificación financiera', 'Analítica institucional', 'Recaudación y sostenibilidad', 'Gobierno y calidad de datos', 'Tableros para decisión'],
    questions: ['¿Los datos reducen incertidumbre en decisiones?', '¿La analítica anticipa riesgos de deserción o sostenibilidad?', '¿Existen fuentes integradas y confiables?'],
  },
  {
    code: 'D4', title: 'Investigación, Vinculación e Innovación', objective: 'Principalmente O4', icon: FlaskConical, color: '#00B8A9',
    summary: 'Examina la articulación entre docencia, investigación, vinculación e innovación para generar impacto, transferencia, publicaciones, patentes y empleabilidad.',
    areas: ['Posgrados vinculados a grupos de investigación', 'Patentes y propiedad intelectual', 'Publicaciones', 'Vinculación e innovación aplicada', 'Empleabilidad', 'Transferencia de conocimiento'],
    questions: ['¿Las capacidades académicas se convierten en innovación?', '¿La investigación se conecta con necesidades reales?', '¿Existe trazabilidad entre proyectos, resultados e impacto?'],
  },
  {
    code: 'D5', title: 'Sostenibilidad Ambiental · Universidad Cero Emisiones', objective: 'Principalmente O5', icon: Leaf, color: '#00E676',
    summary: 'Integra transformación digital y sostenibilidad ambiental para reducir huella de carbono, consumo de papel y energía, y mejorar la eficiencia de infraestructura tecnológica.',
    areas: ['Huella de CO₂', 'Energías renovables', 'Cero papel', 'Data centers verdes', 'Eficiencia energética', 'Monitoreo ambiental basado en datos'],
    questions: ['¿La digitalización reduce impacto ambiental?', '¿La infraestructura tecnológica es energéticamente eficiente?', '¿Las metas ambientales se miden con indicadores verificables?'],
  },
];

export function DimensionsPage() {
  return (
    <div className="space-y-6">
      <section className="glass rounded-[32px] p-6 lg:p-9">
        <div className="eyebrow">Marco de madurez estructural</div>
        <h1 className="mt-3 max-w-5xl text-4xl font-semibold tracking-[-.05em] lg:text-5xl">Las cinco dimensiones de Transformación Digital UPS</h1>
        <p className="mt-4 max-w-4xl text-sm leading-7 muted">Cada iniciativa contribuye con intensidad 0–3 a una o más dimensiones. El avance verificado de las iniciativas y la matriz de contribución determinan la cobertura y el nivel de madurez de cada dimensión en escala 0–5.</p>
        <div className="mt-6 grid gap-2 sm:grid-cols-5">
          {dimensions.map(d => <a key={d.code} href={`#${d.code}`} className="focus-ring rounded-2xl border hairline p-3 text-center transition hover:-translate-y-0.5"><div className="metric text-xl font-semibold" style={{ color: d.color }}>{d.code}</div><div className="mt-1 text-[10px] muted">{d.title}</div></a>)}
        </div>
      </section>

      <div className="space-y-4">
        {dimensions.map((d, index) => {
          const Icon = d.icon;
          return (
            <motion.section id={d.code} key={d.code} initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: .2 }} transition={{ delay: Math.min(index * .04, .15) }} className="glass scroll-mt-28 rounded-[30px] p-6 lg:p-8">
              <div className="grid gap-7 lg:grid-cols-[.9fr_1.1fr]">
                <div>
                  <div className="flex items-center gap-3"><div className="grid h-12 w-12 place-items-center rounded-2xl" style={{ color: d.color, background: `color-mix(in srgb, ${d.color} 13%, transparent)` }}><Icon size={21} /></div><div><div className="metric text-2xl font-semibold" style={{ color: d.color }}>{d.code}</div><div className="text-[10px] uppercase tracking-[.12em] muted">{d.objective}</div></div></div>
                  <h2 className="mt-5 text-2xl font-semibold tracking-[-.035em]">{d.title}</h2>
                  <p className="mt-3 text-sm leading-7 muted">{d.summary}</p>
                  <div className="mt-5 h-1.5 overflow-hidden rounded-full bg-black/5 dark:bg-white/5"><div className="h-full w-full rounded-full opacity-70" style={{ background: d.color }} /></div>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-[22px] border hairline p-4"><div className="eyebrow">Ámbitos observados</div><ul className="mt-3 space-y-2 text-xs leading-5">{d.areas.map(a => <li key={a} className="flex gap-2"><span className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: d.color }} />{a}</li>)}</ul></div>
                  <div className="rounded-[22px] border hairline p-4"><div className="eyebrow">Preguntas de gobernanza</div><ul className="mt-3 space-y-3 text-xs leading-5 muted">{d.questions.map(q => <li key={q}>“{q}”</li>)}</ul></div>
                </div>
              </div>
            </motion.section>
          );
        })}
      </div>
    </div>
  );
}
