import ScoreDial from "./ScoreDial";

function Field({ label, value }) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-ink-faint)" }}>
        {label}
      </div>
      <div className="text-sm font-mono mt-0.5" style={{ color: "var(--color-ink)" }}>
        {value ?? "—"}
      </div>
    </div>
  );
}

export default function LeadDetailDrawer({ lead, onClose }) {
  if (!lead) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end" role="dialog" aria-modal="true">
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />
      <div
        className="relative w-full max-w-md h-full overflow-y-auto scrollbar-thin border-l"
        style={{ backgroundColor: "var(--color-surface)", borderColor: "var(--color-line)" }}
      >
        <div className="flex items-start justify-between p-6 border-b" style={{ borderColor: "var(--color-line)" }}>
          <div>
            <h2 className="font-display text-xl font-semibold" style={{ color: "var(--color-ink)" }}>
              {lead.company_name || "Unnamed lead"}
            </h2>
            <p className="text-sm mt-0.5" style={{ color: "var(--color-ink-dim)" }}>
              {lead.contact_name}
              {lead.contact_name && lead.email ? " · " : ""}
              {lead.email}
            </p>
          </div>
          <button onClick={onClose} className="text-2xl leading-none" style={{ color: "var(--color-ink-faint)" }}>
            ×
          </button>
        </div>

        <div className="flex items-center gap-4 p-6 border-b" style={{ borderColor: "var(--color-line)" }}>
          <ScoreDial score={lead.lead_score} size={110} />
          <div>
            <div className="text-[11px] uppercase tracking-wider" style={{ color: "var(--color-ink-faint)" }}>
              Lead Score
            </div>
            <div className="font-display text-lg font-medium mt-1" style={{ color: "var(--color-ink)" }}>
              {lead.score_label} priority
            </div>
          </div>
        </div>

        <div className="p-6 border-b" style={{ borderColor: "var(--color-line)" }}>
          <h3 className="text-[11px] uppercase tracking-wider mb-3" style={{ color: "var(--color-ink-faint)" }}>
            Why this score
          </h3>
          <ul className="space-y-3">
            {(lead.explanation || []).map((item, i) => (
              <li key={i} className="flex gap-3">
                <span
                  className="mt-0.5 text-xs font-mono w-10 shrink-0"
                  style={{ color: item.direction === "increased" ? "var(--color-hot)" : "var(--color-cold)" }}
                >
                  {item.direction === "increased" ? "▲ up" : "▼ down"}
                </span>
                <span className="text-sm" style={{ color: "var(--color-ink-dim)" }}>
                  {item.detail}
                </span>
              </li>
            ))}
            {(!lead.explanation || lead.explanation.length === 0) && (
              <li className="text-sm" style={{ color: "var(--color-ink-faint)" }}>
                No explanation available for this lead.
              </li>
            )}
          </ul>
        </div>

        <div className="p-6 grid grid-cols-2 gap-x-4 gap-y-4">
          <Field label="Industry" value={lead.industry} />
          <Field label="Company Size" value={lead.company_size} />
          <Field
            label="Annual Revenue"
            value={lead.annual_revenue ? `₹${Number(lead.annual_revenue).toLocaleString("en-IN")}` : null}
          />
          <Field label="Budget" value={lead.budget ? `₹${Number(lead.budget).toLocaleString("en-IN")}` : null} />
          <Field label="Engagement Score" value={lead.engagement_score} />
          <Field label="Email Opens" value={lead.email_opens} />
          <Field label="Website Visits" value={lead.website_visits} />
          <Field label="Days Since Contact" value={lead.days_since_last_contact} />
        </div>

        {lead.extra_fields && Object.keys(lead.extra_fields).length > 0 && (
          <div className="p-6 pt-0">
            <h3 className="text-[11px] uppercase tracking-wider mb-3" style={{ color: "var(--color-ink-faint)" }}>
              Other CSV fields
            </h3>
            <div className="grid grid-cols-2 gap-x-4 gap-y-3">
              {Object.entries(lead.extra_fields).map(([k, v]) => (
                <Field key={k} label={k} value={String(v)} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
