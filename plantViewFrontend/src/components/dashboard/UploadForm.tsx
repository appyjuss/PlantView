import React, { useRef, useState } from "react";
import { createDetectionFromFile } from "../../lib/mockDetections";

export default function UploadForm({ onComplete }: { onComplete?: (d: any) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const fileRef = useRef<HTMLInputElement | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    try {
      const res = await createDetectionFromFile(file);
      onComplete?.(res);
      setFile(null);
      // reset native input value so same file can be selected again
      if (fileRef.current) fileRef.current.value = "";
    } finally {
      setLoading(false);
    }
  }

  function handleChoose() {
    if (loading) return;
    fileRef.current?.click();
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      <label className="block text-sm font-medium text-slate-700">Upload single image</label>

      {/* hidden native input, triggered from custom button for clearer UI */}
      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        disabled={loading}
        aria-hidden={loading}
      />

      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={handleChoose}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3 py-2 border rounded bg-white text-slate-700 hover:bg-slate-50"
        >
          Choose file
        </button>

        <div className="text-sm text-slate-600">{file ? file.name : "No file selected"}</div>
      </div>

      {file && (
        <div className="mt-2">
          <img src={URL.createObjectURL(file)} alt="preview" className="w-40 rounded" />
        </div>
      )}

      <div className="mt-3">
        <button
          disabled={!file || loading}
          className={`inline-flex items-center gap-2 px-4 py-2 rounded font-medium ${
            loading ? "bg-slate-300 text-slate-700 cursor-not-allowed" : "bg-emerald-600 text-white hover:bg-emerald-700"
          }`}
        >
          {loading ? (
              <span>Uploading & detecting…</span>
            ) : (
              <span>Upload & Detect</span>
            )}
        </button>
      </div>
    </form>
  );
}
