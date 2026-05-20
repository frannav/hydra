/**
 * StatusBadge — wraps a label and optionally shows an active indicator.
 *
 * Used by MainNavigation to highlight the current route.
 */

interface StatusBadgeProps {
  children: React.ReactNode;
  isActive?: boolean;
}

export default function StatusBadge({
  children,
  isActive = false,
}: StatusBadgeProps) {
  return (
    <span className="inline-flex items-center gap-1.5">
      {isActive && (
        <span className="h-1.5 w-1.5 rounded-full bg-blue-400" />
      )}
      {children}
    </span>
  );
}
