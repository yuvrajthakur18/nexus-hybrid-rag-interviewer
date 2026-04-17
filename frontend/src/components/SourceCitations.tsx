type Citation = {
  source: string;
  chunk_id: string;
  score: number;
};

export function SourceCitations({ citations }: { citations: Citation[] }) {
  if (!citations.length) return null;

  return (
    <div className="mt-2">
      <p className="text-xs text-slate-400">Sources</p>
      <ul className="mt-1 space-y-1">
        {citations.map((c) => (
          <li key={c.chunk_id} className="text-[12px] text-slate-300">
            {c.source} <span className="text-slate-500">({c.score.toFixed(2)})</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
