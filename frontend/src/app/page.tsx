import Link from "next/link";
import AppShell from "@/components/AppShell";

const VIEW_LINKS = [
  {
    href: "/corpus",
    label: "Corpus",
    description: "Listado de documentos procesados.",
  },
  {
    href: "/narratives",
    label: "Narrativas",
    description: "Marcos narrativos extraídos del corpus.",
  },
  {
    href: "/analyst",
    label: "Analyst",
    description: "Consulta controlada con evidencias recuperadas.",
  },
  {
    href: "/briefing",
    label: "Briefing",
    description: "Briefing con revisión del consejo.",
  },
  {
    href: "/evals",
    label: "Evals",
    description: "Ejecución y resultados de evaluaciones.",
  },
];

export default function HomePage() {
  return (
    <AppShell>
      <h1 className="mb-6 text-2xl font-semibold text-gray-100">Dashboard</h1>

      <div className="mb-6 rounded border border-yellow-900/50 bg-yellow-950/30 p-3 text-sm text-yellow-200">
        Limitación: el análisis depende del corpus disponible. Las evidencias y
        limitaciones se muestran cuando están presentes.
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {VIEW_LINKS.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="rounded-lg border border-gray-800 bg-gray-900/60 p-4 transition-colors hover:border-gray-600 hover:bg-gray-900"
          >
            <h2 className="text-lg font-medium text-gray-100">
              {link.label}
            </h2>
            <p className="mt-1 text-xs text-gray-500">{link.description}</p>
          </Link>
        ))}
      </div>
    </AppShell>
  );
}
