import { Mail, ShieldCheck, Workflow } from 'lucide-react';

export default function ContactPage() {
  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <section className="glass rounded-[32px] p-7 lg:p-10">
        <div className="eyebrow">Contacto institucional</div>
        <h1 className="mt-3 text-4xl font-semibold tracking-[-.05em] lg:text-5xl">Coordinación de Transformación Digital</h1>
        <p className="mt-4 max-w-3xl text-sm leading-7 muted">Para consultas sobre el modelo, actualización de iniciativas, validación de evidencias, acceso de responsables o incorporación de nuevas iniciativas, comuníquese con la coordinación.</p>
        <a href="mailto:transformaciondigital@ups.edu.ec" className="focus-ring mt-7 flex items-center gap-4 rounded-[24px] border hairline p-5 transition hover:-translate-y-0.5 hover:shadow-lg">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-sky-500/10 text-sky-500"><Mail size={21} /></div>
          <div><div className="text-xs muted">Correo de la Coordinación</div><div className="mt-1 text-lg font-semibold">transformaciondigital@ups.edu.ec</div></div>
        </a>
      </section>
      <div className="grid gap-4 md:grid-cols-2">
        <article className="glass rounded-[26px] p-6"><ShieldCheck className="text-emerald-500" size={22}/><h2 className="mt-4 text-lg font-semibold">Acceso autorizado</h2><p className="mt-2 text-sm leading-6 muted">Los responsables de iniciativas acceden con credenciales asignadas por la Coordinación. Cada cuenta puede limitarse a las iniciativas que le corresponde gestionar.</p></article>
        <article className="glass rounded-[26px] p-6"><Workflow className="text-violet-500" size={22}/><h2 className="mt-4 text-lg font-semibold">Nuevas iniciativas</h2><p className="mt-2 text-sm leading-6 muted">La Coordinación puede crear nuevas iniciativas con la plantilla institucional: objetivo, dimensión, responsable, actividades, fechas, prioridad, avance, observaciones y evidencias.</p></article>
      </div>
    </div>
  );
}
