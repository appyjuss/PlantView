import { useEffect, useState } from "react";
import { getDetection, reprocessDetection, type Detection } from "../../lib/detections";

export default function DetectionDetails({ id, onClose }: { id: string; onClose: () => void }) {
  const [detection, setDetection] = useState<Detection | undefined>(undefined);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setDetection(getDetection(id));
  }, [id]);

  async function reprocess() {
    setLoading(true);
    const updated = await reprocessDetection(id);
    const refreshed = getDetection(id);
    setDetection(refreshed || updated);
    setLoading(false);
  }

  if (!detection) return <div className="p-4">Not found</div>;

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
            {detection.imageDataUrl ? (
              <img src={detection.imageDataUrl} alt="full" className="w-full rounded" />
            ) : (
              <div className="w-full h-48 bg-slate-100 rounded flex items-center justify-center text-sm text-slate-400">No image available</div>
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
