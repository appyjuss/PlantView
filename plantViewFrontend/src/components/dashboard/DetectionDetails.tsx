import { useState } from "react";
import { reprocessDetection, type Detection } from "../../lib/detections";

export default function DetectionDetails({ detection: initialDetection, onClose }: { detection: Detection; onClose: () => void }) {
  const [detection, setDetection] = useState<Detection>(initialDetection);
  const [loading, setLoading] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function reprocess() {
    setLoading(true);
    setError(null);
    try {
      const updated = await reprocessDetection(detection);
      if (updated) {
        setDetection(updated);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Reprocess failed';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center p-6">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="relative bg-white rounded-lg shadow max-w-3xl w-full p-6 z-10">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-xl font-semibold">Detection details</h3>
            <div className="text-sm text-slate-500">{new Date(detection.createdAt).toLocaleString()}</div>
          </div>
          <div>
            <button onClick={onClose} className="text-sm text-slate-500">Close</button>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            {detection.imageDataUrl && !imageError ? (
              <div className="relative">
                <img 
                  src={detection.imageDataUrl} 
                  alt="full" 
                  className="w-full rounded" 
                  onError={() => {
                    setImageError(true);
                  }}
                />
              </div>
            ) : (
              <div className="w-full h-48 bg-slate-100 rounded flex items-center justify-center text-sm text-slate-400">
                {imageError ? 'Image failed to load' : 'No image available'}
              </div>
            )}
          </div>
          <div>
            <div className="font-semibold">Result</div>
            <div className="mt-2 divide-y divide-slate-100">
              {Array.isArray(detection.result) && detection.result.length ? (
                detection.result.map((r, i) => {
                  // compute percent 0-100
                  const pctNum = typeof r.confidence === 'number' ? Math.max(0, Math.min(100, r.confidence * 100)) : 0;
                  const pctLabel = `${pctNum.toFixed(1)}%`;
                  const raw = r.label || 'Unknown';
                  const pretty = raw.replace(/[_,]+/g, ' ').replace(/\s+/g, ' ').trim()
                    .split(' ')
                    .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
                    .join(' ');

                  // emphasize the top (first) result visually
                  if (i === 0) {
                    return (
                      <div key={i} className="p-4 bg-slate-50 rounded border border-slate-100 shadow-sm">
                        <div className="flex items-center justify-between gap-4">
                          <div>
                            <div className="text-lg font-semibold text-slate-900">{pretty}</div>
                            <div className="text-sm text-slate-500">Top prediction</div>
                          </div>
                          <div className="text-right">
                            <div className="text-3xl font-extrabold text-brand-500">{pctLabel}</div>
                            <div className="text-xs text-slate-500">confidence</div>
                          </div>
                        </div>
                      </div>
                    );
                  }

                  return (
                    <div key={i} className="py-3 flex items-center justify-between">
                      <div className="text-sm text-slate-800">{pretty}</div>
                      <div className="text-sm text-slate-600 font-semibold">{pctLabel}</div>
                    </div>
                  );
                })
              ) : (
                <div className="text-sm text-slate-500">No result available.</div>
              )}
            </div>

            {error && (
              <div className="mt-3 p-2 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
                {error}
              </div>
            )}

            <div className="mt-4 flex gap-3">
              <button 
                onClick={reprocess} 
                disabled={loading || !detection.imageDataUrl} 
                className="px-3 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {loading ? "Reprocessing…" : "Reprocess"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
