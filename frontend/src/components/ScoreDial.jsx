/**
 * ScoreDial: renders a lead's 0-100 score as an analog meter/gauge --
 * the page's signature visual motif (an "instrument reading" rather
 * than a generic progress bar or badge).
 */
const SWEEP_START = 140; // degrees
const SWEEP_END = 400; // 260-degree sweep

function polarToCartesian(cx, cy, r, angleDeg) {
  const angleRad = (angleDeg * Math.PI) / 180;
  return { x: cx + r * Math.cos(angleRad), y: cy + r * Math.sin(angleRad) };
}

function arcPath(cx, cy, r, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, r, startAngle);
  const end = polarToCartesian(cx, cy, r, endAngle);
  const largeArc = endAngle - startAngle > 180 ? 1 : 0;
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y}`;
}

function colorForScore(score) {
  if (score >= 70) return "var(--color-hot)";
  if (score >= 40) return "var(--color-warm)";
  return "var(--color-cold)";
}

export default function ScoreDial({ score, size = 96 }) {
  const cx = 60;
  const cy = 60;
  const r = 46;
  const valueAngle = SWEEP_START + (Math.min(Math.max(score, 0), 100) / 100) * (SWEEP_END - SWEEP_START);
  const color = colorForScore(score);

  const ticks = Array.from({ length: 11 }, (_, i) => {
    const angle = SWEEP_START + (i / 10) * (SWEEP_END - SWEEP_START);
    const outer = polarToCartesian(cx, cy, r + 5, angle);
    const inner = polarToCartesian(cx, cy, r - (i % 5 === 0 ? 3 : 0), angle);
    return { x1: inner.x, y1: inner.y, x2: outer.x, y2: outer.y };
  });

  return (
    <svg width={size} height={size} viewBox="0 0 120 120" role="img" aria-label={`Score ${score} out of 100`}>
      <path
        d={arcPath(cx, cy, r, SWEEP_START, SWEEP_END)}
        fill="none"
        stroke="var(--color-line)"
        strokeWidth="6"
        strokeLinecap="round"
      />
      <path
        d={arcPath(cx, cy, r, SWEEP_START, valueAngle)}
        fill="none"
        stroke={color}
        strokeWidth="6"
        strokeLinecap="round"
      />
      {ticks.map((t, i) => (
        <line key={i} x1={t.x1} y1={t.y1} x2={t.x2} y2={t.y2} stroke="var(--color-ink-faint)" strokeWidth="1" />
      ))}
      <text
        x={cx}
        y={cy - 2}
        textAnchor="middle"
        fontFamily="var(--font-mono)"
        fontSize="22"
        fontWeight="600"
        fill="var(--color-ink)"
      >
        {Math.round(score)}
      </text>
      <text
        x={cx}
        y={cy + 16}
        textAnchor="middle"
        fontFamily="var(--font-mono)"
        fontSize="9"
        letterSpacing="1"
        fill="var(--color-ink-faint)"
      >
        / 100
      </text>
    </svg>
  );
}
