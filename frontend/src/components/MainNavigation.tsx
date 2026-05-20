"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import StatusBadge from "./StatusBadge";

const NAV_LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/corpus", label: "Corpus" },
  { href: "/narratives", label: "Narrativas" },
  { href: "/analyst", label: "Analyst" },
  { href: "/briefing", label: "Briefing" },
  { href: "/evals", label: "Evals" },
];

export default function MainNavigation() {
  const pathname = usePathname();

  return (
    <nav className="border-b border-gray-800 bg-gray-950">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link
          href="/"
          className="text-lg font-bold tracking-tight text-gray-100"
        >
          HYDRA
        </Link>

        {/* Desktop nav */}
        <div className="hidden items-center gap-1 md:flex">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`rounded px-3 py-1.5 text-sm transition-colors ${
                pathname === link.href
                  ? "bg-gray-800 text-gray-100"
                  : "text-gray-400 hover:text-gray-100"
              }`}
            >
              <StatusBadge isActive={pathname === link.href}>
                {link.label}
              </StatusBadge>
            </Link>
          ))}
        </div>

        {/* Mobile menu button */}
        <MobileMenu links={NAV_LINKS} pathname={pathname} />
      </div>
    </nav>
  );
}

function MobileMenu({
  links,
  pathname,
}: {
  links: { href: string; label: string }[];
  pathname: string;
}) {
  return (
    <details className="md:hidden">
      <summary className="cursor-pointer text-sm text-gray-400 hover:text-gray-100">
        Menu
      </summary>
      <div className="mt-2 space-y-1">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`block rounded px-3 py-1.5 text-sm transition-colors ${
              pathname === link.href
                ? "bg-gray-800 text-gray-100"
                : "text-gray-400 hover:text-gray-100"
            }`}
          >
            <StatusBadge isActive={pathname === link.href}>
              {link.label}
            </StatusBadge>
          </Link>
        ))}
      </div>
    </details>
  );
}
