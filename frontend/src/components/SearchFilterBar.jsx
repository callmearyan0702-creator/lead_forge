const SORT_OPTIONS = [
  { value: "lead_score", label: "Score" },
  { value: "company_name", label: "Company" },
  { value: "annual_revenue", label: "Revenue" },
  { value: "engagement_score", label: "Engagement" },
  { value: "created_at", label: "Uploaded" },
];

const LABEL_FILTERS = ["Hot", "Warm", "Cold"];

export default function SearchFilterBar({
  search,
  onSearchChange,
  label,
  onLabelChange,
  sortBy,
  onSortByChange,
  sortDir,
  onSortDirToggle,
  onExport,
  resultCount,
}) {
  return (
    <div className="blueprint-panel px-4 py-3 flex flex-wrap items-center gap-3">
      <div className="flex items-center gap-2 flex-1 min-w-[220px]">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-ink-faint)" strokeWidth="2">
          <circle cx="11" cy="11" r="7" />
          <path d="M21 21l-4.3-4.3" strokeLinecap="round" />
        </svg>
        <input
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search company, contact, or email…"
          className="bg-transparent outline-none text-sm w-full placeholder:text-[color:var(--color-ink-faint)]"
          style={{ color: "var(--color-ink)" }}
        />
      </div>

      <div className="flex items-center gap-1">
        {LABEL_FILTERS.map((opt) => {
          const active = label === opt;
          return (
            <button
              key={opt}
              onClick={() => onLabelChange(active ? "" : opt)}
              className="text-xs uppercase tracking-wider px-2.5 py-1 border transition-colors"
              style={{
                color: active ? "var(--color-canvas)" : "var(--color-ink-dim)",
                backgroundColor: active ? "var(--color-accent)" : "transparent",
                borderColor: active ? "var(--color-accent)" : "var(--color-line)",
              }}
            >
              {opt}
            </button>
          );
        })}
      </div>

      <div className="flex items-center gap-1.5 text-sm">
        <label className="text-[color:var(--color-ink-faint)] text-xs uppercase tracking-wider">Sort</label>
        <select
          value={sortBy}
          onChange={(e) => onSortByChange(e.target.value)}
          className="bg-[color:var(--color-surface-raised)] border text-sm px-2 py-1 outline-none"
          style={{ borderColor: "var(--color-line)", color: "var(--color-ink)" }}
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <button
          onClick={onSortDirToggle}
          title="Toggle sort direction"
          className="border px-2 py-1 text-[color:var(--color-ink-dim)]"
          style={{ borderColor: "var(--color-line)" }}
        >
          {sortDir === "desc" ? "↓" : "↑"}
        </button>
      </div>

      <span className="text-xs font-mono tabular-nums" style={{ color: "var(--color-ink-faint)" }}>
        {resultCount} result{resultCount === 1 ? "" : "s"}
      </span>

      <button
        onClick={onExport}
        className="flex items-center gap-1.5 text-sm px-3 py-1.5 font-medium transition-colors"
        style={{ backgroundColor: "var(--color-accent)", color: "var(--color-canvas)" }}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 3v12" strokeLinecap="round" />
          <path d="M7 10l5 5 5-5" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M5 21h14" strokeLinecap="round" />
        </svg>
        Export CSV
      </button>
    </div>
  );
}
