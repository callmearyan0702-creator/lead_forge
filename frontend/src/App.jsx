import { useCallback, useEffect, useRef, useState } from "react";
import UploadZone from "./components/UploadZone";
import StatsBar from "./components/StatsBar";
import SearchFilterBar from "./components/SearchFilterBar";
import LeadTable from "./components/LeadTable";
import LeadDetailDrawer from "./components/LeadDetailDrawer";
import BatchSelector from "./components/BatchSelector";
import { uploadCsv, fetchLeads, fetchBatches, exportCsvUrl } from "./api/client";

const HOME_PATH = "/";
const DASHBOARD_PATH = "/dashboard";

export default function App() {
  const [leads, setLeads] = useState([]);
  const [batches, setBatches] = useState([]);
  const [activeBatchId, setActiveBatchId] = useState("");
  const [search, setSearch] = useState("");
  const [label, setLabel] = useState("");
  const [sortBy, setSortBy] = useState("lead_score");
  const [sortDir, setSortDir] = useState("desc");
  const [selectedLead, setSelectedLead] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoadingLeads, setIsLoadingLeads] = useState(false);
  const [error, setError] = useState("");
  const [warnings, setWarnings] = useState([]);
  const [hasData, setHasData] = useState(false);
  const [view, setView] = useState("home");

  // Keep a ref in sync with hasData so the popstate handler (registered once)
  // always reads the latest value instead of a stale closure.
  const hasDataRef = useRef(hasData);
  useEffect(() => {
    hasDataRef.current = hasData;
  }, [hasData]);

  // Navigate between the upload ("home") screen and the dashboard, pushing a
  // real history entry so the browser's back/forward buttons work.
  const navigate = useCallback((nextView, { replace = false } = {}) => {
    const path = nextView === "dashboard" ? DASHBOARD_PATH : HOME_PATH;
    const method = replace ? "replaceState" : "pushState";
    window.history[method]({ view: nextView }, "", path);
    setView(nextView);
  }, []);

  // Every fresh load of the app starts on the upload screen, regardless of
  // what was open before the page was reloaded or what URL was requested.
  useEffect(() => {
    window.history.replaceState({ view: "home" }, "", HOME_PATH);
    setView("home");
  }, []);

  // Wire up browser back/forward navigation.
  useEffect(() => {
    function onPopState(event) {
      const requestedView = event.state?.view || "home";
      if (requestedView === "dashboard" && !hasDataRef.current) {
        // No data loaded in this session (e.g. after a refresh) — there's
        // nothing to show on the dashboard, so send the user home instead.
        navigate("home", { replace: true });
        return;
      }
      setView(requestedView);
    }
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, [navigate]);

  const loadLeads = useCallback(async () => {
    setIsLoadingLeads(true);
    try {
      const data = await fetchLeads({
        batch_id: activeBatchId || undefined,
        search: search || undefined,
        label: label || undefined,
        sort_by: sortBy,
        sort_dir: sortDir,
      });
      setLeads(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoadingLeads(false);
    }
  }, [activeBatchId, search, label, sortBy, sortDir]);

  const loadBatches = useCallback(async () => {
    try {
      const data = await fetchBatches();
      setBatches(data);
      // Note: we deliberately do NOT flip hasData/view to the dashboard here
      // just because the backend already has batches from a prior session.
      // Every fresh page load should start clean at the upload screen; the
      // dashboard only becomes reachable once the user uploads a file in
      // the current session (see handleFileSelected).
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    loadBatches();
  }, [loadBatches]);

  useEffect(() => {
    if (hasData) loadLeads();
  }, [hasData, loadLeads]);

  async function handleFileSelected(file) {
    setError("");
    setWarnings([]);
    setIsUploading(true);
    try {
      const result = await uploadCsv(file);
      setWarnings(result.warnings || []);
      setHasData(true);
      setActiveBatchId(result.batch.id);
      navigate("dashboard");
      await loadBatches();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  }

  function handleExport() {
    const url = exportCsvUrl({
      batch_id: activeBatchId || undefined,
      label: label || undefined,
      search: search || undefined,
    });
    window.open(url, "_blank");
  }

  return (
    <div className="min-h-screen blueprint-grid">
      <header className="border-b" style={{ borderColor: "var(--color-line)" }}>
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between gap-4">
          <button
            onClick={() => navigate("home")}
            className="flex items-center gap-3 text-left"
            title="Back to upload screen"
          >
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" strokeWidth="1.5">
              <rect x="3" y="3" width="18" height="18" rx="1" />
              <path d="M8 16l3-5 2.5 3L18 8" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <div>
              <h1 className="font-display text-lg font-semibold tracking-tight" style={{ color: "var(--color-ink)" }}>
                Industrial AI Lead Intelligence
              </h1>
              <p className="text-xs" style={{ color: "var(--color-ink-faint)" }}>
                ML-scored lead prioritization with per-lead explainability
              </p>
            </div>
          </button>

          <div className="flex items-center gap-4 shrink-0">
            <nav className="flex items-center gap-1">
              <button
                onClick={() => navigate("home")}
                className="flex items-center gap-1.5 text-sm px-3 py-1.5 border transition-colors"
                style={{
                  borderColor: "var(--color-line)",
                  color: view === "home" ? "var(--color-canvas)" : "var(--color-ink-dim)",
                  backgroundColor: view === "home" ? "var(--color-accent)" : "transparent",
                }}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 11l9-7 9 7" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M5 10v9a1 1 0 001 1h4v-6h4v6h4a1 1 0 001-1v-9" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                Home
              </button>
              <button
                onClick={() => hasData && navigate("dashboard")}
                disabled={!hasData}
                title={hasData ? undefined : "Upload a CSV to view the dashboard"}
                className="flex items-center gap-1.5 text-sm px-3 py-1.5 border transition-colors"
                style={{
                  borderColor: "var(--color-line)",
                  color: !hasData
                    ? "var(--color-ink-faint)"
                    : view === "dashboard"
                    ? "var(--color-canvas)"
                    : "var(--color-ink-dim)",
                  backgroundColor: hasData && view === "dashboard" ? "var(--color-accent)" : "transparent",
                  opacity: hasData ? 1 : 0.5,
                  cursor: hasData ? "pointer" : "not-allowed",
                }}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="7" height="9" rx="1" />
                  <rect x="14" y="3" width="7" height="5" rx="1" />
                  <rect x="14" y="12" width="7" height="9" rx="1" />
                  <rect x="3" y="16" width="7" height="5" rx="1" />
                </svg>
                Dashboard
              </button>
            </nav>
            {view === "dashboard" && hasData && (
              <BatchSelector batches={batches} activeBatchId={activeBatchId} onChange={setActiveBatchId} />
            )}
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 flex flex-col gap-6">
        {view !== "dashboard" || !hasData ? (
          <div className="max-w-xl mx-auto w-full mt-12">
            <UploadZone onFileSelected={handleFileSelected} isUploading={isUploading} />
            {error && (
              <p className="text-sm mt-4 text-center" style={{ color: "var(--color-hot)" }}>
                {error}
              </p>
            )}
          </div>
        ) : (
          <>
            <div className="flex flex-wrap items-start justify-between gap-4">
              <StatsBar leads={leads} />
              <div className="shrink-0">
                <label
                  className="flex items-center gap-2 text-sm px-3 py-2 border cursor-pointer transition-colors"
                  style={{ borderColor: "var(--color-line)", color: "var(--color-ink-dim)" }}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M7 9l5-5 5 5" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M12 4v12" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  {isUploading ? "Uploading…" : "Upload another CSV"}
                  <input
                    type="file"
                    accept=".csv"
                    className="hidden"
                    disabled={isUploading}
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleFileSelected(file);
                      e.target.value = "";
                    }}
                  />
                </label>
              </div>
            </div>

            {error && (
              <p className="text-sm" style={{ color: "var(--color-hot)" }}>
                {error}
              </p>
            )}
            {warnings.length > 0 && (
              <div
                className="text-sm border px-4 py-2.5"
                style={{ borderColor: "var(--color-warm)", color: "var(--color-warm)" }}
              >
                {warnings.join(" ")}
              </div>
            )}

            <SearchFilterBar
              search={search}
              onSearchChange={setSearch}
              label={label}
              onLabelChange={setLabel}
              sortBy={sortBy}
              onSortByChange={setSortBy}
              sortDir={sortDir}
              onSortDirToggle={() => setSortDir((d) => (d === "desc" ? "asc" : "desc"))}
              onExport={handleExport}
              resultCount={leads.length}
            />

            <LeadTable leads={leads} onSelectLead={setSelectedLead} isLoading={isLoadingLeads} />
          </>
        )}
      </main>

      <LeadDetailDrawer lead={selectedLead} onClose={() => setSelectedLead(null)} />

      <footer className="max-w-6xl mx-auto px-6 py-8 text-xs" style={{ color: "var(--color-ink-faint)" }}>
        Scores are generated by an XGBoost model trained on synthetic data for
        demonstration purposes. See the README for details.
      </footer>
    </div>
  );
}