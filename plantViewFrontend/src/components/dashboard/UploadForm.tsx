import React, { useRef, useState } from "react";
import { getToken } from "../../lib/api";
import { saveDetection } from "../../lib/detections";

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

      const response = await fetch(`${API_URL}/api/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();

      // data contains `file_key` and `detection` (backend).
      // Retrieve a signed URL for the uploaded file from the backend.
      let fileUrl: string | null = null;
      try {
        const fileKey = data.file_key;
        if (fileKey) {
          const signedResp = await fetch(`${API_URL}/api/uploads/${fileKey}`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
          });
          if (signedResp.ok) {
            const signedJson = await signedResp.json();
            fileUrl = signedJson.url || null;
          }
        }
      } catch (err) {
        // non-fatal; continue without file URL
        console.warn('Failed to fetch signed file URL', err);
      }

      const prediction = data.detection;
      const label = prediction?.class_name ?? 'Unknown';
      const confidence = prediction?.confidence ?? 0;

      // Create detection object with prediction results (use persistent server URL)
      const detection = {
        id: String(Date.now()) + Math.random().toString(36).slice(2, 9),
        createdAt: new Date().toISOString(),
        status: 'done' as const,
        imageDataUrl: fileUrl || URL.createObjectURL(file),
        thumbnailDataUrl: fileUrl || URL.createObjectURL(file),
        file_url: fileUrl,
        result: [ { label, confidence } ],
        modelVersion: prediction?.model_version ?? 'server',
        fileName: file.name,
      };
      //Save detection to history storage
      saveDetection(detection);

      onComplete?.(detection);
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

      {error && (
        <div className="text-sm text-red-600">{error}</div>
      )}

      <div className="mt-3">
        <button
          type="submit"
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
