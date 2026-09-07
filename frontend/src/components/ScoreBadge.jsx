const LABEL_STYLES = {
  Hot: { color: "var(--color-hot)", bg: "rgba(242,102,74,0.12)" },
  Warm: { color: "var(--color-warm)", bg: "rgba(242,169,60,0.12)" },
  Cold: { color: "var(--color-cold)", bg: "rgba(91,112,137,0.15)" },
};

export default function ScoreBadge({ score, label }) {
  const style = LABEL_STYLES[label] || LABEL_STYLES.Cold;
  return (
    <div className="flex items-center gap-2">
      <span
        className="font-mono text-sm font-semibold tabular-nums px-1.5 py-0.5 rounded-sm"
        style={{ color: style.color, backgroundColor: style.bg }}
      >
        {score?.toFixed(1)}
      </span>
      <span
        className="text-[10px] uppercase tracking-wider font-medium px-1.5 py-0.5 rounded-sm border"
        style={{ color: style.color, borderColor: style.color + "55" }}
      >
        {label}
      </span>
    </div>
  );
}
