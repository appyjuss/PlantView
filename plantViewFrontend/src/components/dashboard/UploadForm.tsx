import React, { useRef, useState } from "react";
import { getToken } from "../../lib/api";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export default function UploadForm({ onComplete }: { onComplete?: (d: any) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const token = getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/API/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      // Mock response for now (backend will return detection data)
      const mockDetection = {
        id: `detection-${Date.now()}`,
        filename: file.name,
        thumbnailDataUrl: URL.createObjectURL(file),
        result: [
          { label: 'Healthy', confidence: 0.95 }
        ],
        timestamp: new Date().toISOString()
      };

      onComplete?.(mockDetection);
      setFile(null);
      if (fileRef.current) fileRef.current.value = "";
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
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

      {error && (
        <div className="p-2 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
          {error}
        </div>
      )}

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
          className="inline-flex items-center gap-2 px-3 py-2 border rounded bg-white text-slate-700 hover:bg-slate-50 disabled:bg-gray-200"
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
