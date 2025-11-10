import type { Detection } from "../../lib/mockDetections";

export default function DetectionCard({ detection, onView }: { detection: Detection; onView?: (id: string) => void }) {
  const top = detection.result?.[0];
  return (
    <div className="p-3 bg-white rounded shadow flex gap-3 items-center">
      <img src={detection.thumbnailDataUrl} alt="thumb" className="w-20 h-20 object-cover rounded" />
      <div className="flex-1">
        <div className="font-semibold">{top?.label ?? "No result"}</div>
        <div className="text-xs text-slate-500">{new Date(detection.createdAt).toLocaleString()}</div>
      </div>
      <div>
        <button onClick={() => onView?.(detection.id)} className="text-sm text-emerald-600">View</button>
      </div>
    </div>
  );
}
