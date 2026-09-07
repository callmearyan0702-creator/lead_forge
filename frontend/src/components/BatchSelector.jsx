export default function BatchSelector({ batches, activeBatchId, onChange }) {
  if (batches.length === 0) return null;

  return (
    <div className="flex items-center gap-2">
      <label className="text-xs uppercase tracking-wider" style={{ color: "var(--color-ink-faint)" }}>
        Batch
      </label>
      <select
        value={activeBatchId || ""}
        onChange={(e) => onChange(e.target.value)}
        className="bg-[color:var(--color-surface-raised)] border text-sm px-2 py-1.5 outline-none max-w-[220px] truncate"
        style={{ borderColor: "var(--color-line)", color: "var(--color-ink)" }}
      >
        <option value="">All uploads</option>
        {batches.map((b) => (
          <option key={b.id} value={b.id}>
            {b.filename} ({b.row_count})
          </option>
        ))}
      </select>
    </div>
  );
}
