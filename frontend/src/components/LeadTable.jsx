import ScoreBadge from "./ScoreBadge";

/*function formatCurrency(value) {
  if (value === null || value === undefined) return "—";
  return `$${Number(value).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
}*/
function formatCurrency(value) {
  if (value === null || value === undefined) return "—";
  return `₹${Number(value).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

function formatNumber(value) {
  if (value === null || value === undefined) return "—";
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: 0 });
}

export default function LeadTable({ leads, onSelectLead, isLoading }) {
  if (isLoading) {
    return (
      <div className="blueprint-panel px-6 py-16 text-center text-sm" style={{ color: "var(--color-ink-faint)" }}>
        Scoring leads…
      </div>
    );
  }

  if (leads.length === 0) {
    return (
      <div className="blueprint-panel px-6 py-16 text-center">
        <p className="font-display text-base" style={{ color: "var(--color-ink)" }}>
          No leads match the current filters
        </p>
        <p className="text-sm mt-1" style={{ color: "var(--color-ink-faint)" }}>
          Try clearing the search or label filter.
        </p>
      </div>
    );
  }
  
  return (
    <div className="blueprint-panel overflow-x-auto scrollbar-thin">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b text-left" style={{ borderColor: "var(--color-line)" }}>
            {["Company", "Contact", "Industry", "Revenue(In Crores)", "Engagement", "Score"].map((h) => (
              <th
                key={h}
                className="px-4 py-2.5 text-[11px] uppercase tracking-wider font-medium"
                style={{ color: "var(--color-ink-faint)" }}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr
              key={lead.id}
              onClick={() => onSelectLead(lead)}
              className="border-b cursor-pointer transition-colors hover:bg-[color:var(--color-surface-raised)]"
              style={{ borderColor: "var(--color-line-soft)" }}
            >
              <td className="px-4 py-3 font-medium" style={{ color: "var(--color-ink)" }}>
                {lead.company_name || "—"}
              </td>
              <td className="px-4 py-3" style={{ color: "var(--color-ink-dim)" }}>
                <div>{lead.contact_name || "—"}</div>
                {lead.email && (
                  <div className="text-xs" style={{ color: "var(--color-ink-faint)" }}>
                    {lead.email}
                  </div>
                )}
              </td>
              <td className="px-4 py-3" style={{ color: "var(--color-ink-dim)" }}>
                {lead.industry || "—"}
              </td>
              <td className="px-4 py-3 font-mono tabular-nums" style={{ color: "var(--color-ink-dim)" }}>
                {formatCurrency(lead.annual_revenue)}
              </td>
              <td className="px-4 py-3 font-mono tabular-nums" style={{ color: "var(--color-ink-dim)" }}>
                {formatNumber(lead.engagement_score)}
              </td>
              <td className="px-4 py-3">
                <ScoreBadge score={lead.lead_score} label={lead.score_label} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
