import { useCallback, useRef, useState } from "react";

export default function UploadZone({ onFileSelected, isUploading }) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef(null);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files?.[0];
      if (file) onFileSelected(file);
    },
    [onFileSelected]
  );

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className="blueprint-panel blueprint-grid rounded-none cursor-pointer transition-colors"
      style={{
        borderColor: isDragging ? "var(--color-accent)" : undefined,
        borderStyle: "dashed",
      }}
    >
      <div className="flex flex-col items-center justify-center gap-3 px-8 py-16 text-center">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" strokeWidth="1.5">
          <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M7 9l5-5 5 5" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M12 4v12" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <div>
          <p className="font-display text-lg font-medium" style={{ color: "var(--color-ink)" }}>
            {isUploading ? "Processing upload…" : "Drop a lead CSV here"}
          </p>
          <p className="text-sm mt-1" style={{ color: "var(--color-ink-dim)" }}>
            or click to browse. Common columns (company, revenue, engagement,
            budget, etc.) are detected automatically.
          </p>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) onFileSelected(file);
            e.target.value = "";
          }}
        />
      </div>
    </div>
  );
}
