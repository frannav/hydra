/**
 * EvidenceList — displays a list of evidence fragments.
 *
 * Shows "Sin evidencias" when the array is empty or missing.
 * Fragments are rendered as plain text (escaped by React's JSX).
 */

interface EvidenceListProps {
  fragments: string[];
}

export default function EvidenceList({ fragments }: EvidenceListProps) {
  if (!fragments || fragments.length === 0) {
    return <span className="text-xs text-gray-500">Sin evidencias</span>;
  }

  return (
    <ul className="list-inside list-disc space-y-1 text-xs text-gray-300">
      {fragments.map((fragment, index) => (
        <li key={index} className="leading-relaxed">
          {fragment}
        </li>
      ))}
    </ul>
  );
}
