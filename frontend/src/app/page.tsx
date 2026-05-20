import Link from "next/link";

const NAV_LINKS = [
  { href: "/corpus", label: "Corpus" },
  { href: "/narratives", label: "Narrativas" },
  { href: "/analyst", label: "Analyst" },
  { href: "/briefing", label: "Briefing" },
  { href: "/evals", label: "Evals" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800">
        <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <span className="text-lg font-bold tracking-tight text-gray-100">
            HYDRA
          </span>
          <div className="flex gap-6">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-sm text-gray-400 hover:text-gray-100"
              >
                {link.label}
              </Link>
            ))}
          </div>
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
        <h1 className="mb-6 text-2xl font-semibold text-gray-100">
          Dashboard
        </h1>

        <p className="mb-6 text-sm text-gray-400">
          HYDRA — Inteligencia narrativa trazable. Selecciona una vista del
          men&uacute; para consultar corpus, narrativas, an&aacute;lisis,
          briefing o evaluaciones.
        </p>

        <div className="mb-6 rounded border border-yellow-900/50 bg-yellow-950/30 p-3 text-sm text-yellow-200">
          Limitaci&oacute;n: el an&aacute;lisis depende del corpus
          disponible. Las evidencias y limitaciones se muestran cuando est&aacute;n
          presentes.
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded-lg border border-gray-800 bg-gray-900/60 p-4 transition-colors hover:border-gray-600 hover:bg-gray-900"
            >
              <h2 className="text-lg font-medium text-gray-100">
                {link.label}
              </h2>
              <p className="mt-1 text-xs text-gray-500">
                {link.href === "/corpus" &&
                  "Listado de documentos procesados."}
                {link.href === "/narratives" &&
                  "Marcos narrativos extra&iacute;dos del corpus."}
                {link.href === "/analyst" &&
                  "Consulta controlada con evidencias recuperadas."}
                {link.href === "/briefing" &&
                  "Briefing con revisi&oacute;n del consejo."}
                {link.href === "/evals" &&
                  "Ejecuci&oacute;n y resultados de evaluaciones."}
              </p>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
