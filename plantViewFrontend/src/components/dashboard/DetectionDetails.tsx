import { useState } from "react";
import { reprocessDetection, type Detection } from "../../lib/detections";

export default function DetectionDetails({ detection: initialDetection, onClose }: { detection: Detection; onClose: () => void }) {
  const [detection, setDetection] = useState<Detection>(initialDetection);
  const [loading, setLoading] = useState(false);
  const [imageError, setImageError] = useState(false);

  async function reprocess() {
    setLoading(true);
    try {
      const updated = await reprocessDetection(detection.id);
      if (updated) {
        setDetection(updated);
      }
    } catch (err) {
      console.error('Reprocess failed:', err);
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
                    console.error('Full image failed to load:', detection.imageDataUrl);
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
            <pre className="text-sm bg-slate-50 p-3 mt-2 rounded">
              {JSON.stringify(detection.result, null, 2)}
            </pre>

            <div className="mt-4 flex gap-3">
              <button onClick={reprocess} disabled={loading} className="px-3 py-2 bg-emerald-600 text-white rounded">
                {loading ? "Reprocessing…" : "Reprocess"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
