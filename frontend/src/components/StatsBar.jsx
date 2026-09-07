function StatCell({ label, value, color }) {
  return (
    <div className="flex flex-col gap-1 px-5 py-4 border-r last:border-r-0" style={{ borderColor: "var(--color-line)" }}>
      <span className="text-[11px] uppercase tracking-wider" style={{ color: "var(--color-ink-faint)" }}>
        {label}
      </span>
      <span className="font-mono text-2xl font-semibold tabular-nums" style={{ color: color || "var(--color-ink)" }}>
        {value}
      </span>
    </div>
  );
}

export default function StatsBar({ leads }) {
  const total = leads.length;
  const avg = total ? (leads.reduce((s, l) => s + (l.lead_score || 0), 0) / total).toFixed(1) : "—";
  const hot = leads.filter((l) => l.score_label === "Hot").length;
  const warm = leads.filter((l) => l.score_label === "Warm").length;
  const cold = leads.filter((l) => l.score_label === "Cold").length;

  return (
    <div className="blueprint-panel flex flex-wrap">
      <StatCell label="Total Leads" value={total} />
      <StatCell label="Avg Score" value={avg} />
      <StatCell label="Hot" value={hot} color="var(--color-hot)" />
      <StatCell label="Warm" value={warm} color="var(--color-warm)" />
      <StatCell label="Cold" value={cold} color="var(--color-cold)" />
    </div>
  );
}
