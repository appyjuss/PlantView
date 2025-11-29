import type { Detection } from "../../lib/detections";
import { useState } from "react";

export default function DetectionCard({ detection, onView }: { detection: Detection; onView?: () => void }) {
  const [imageError, setImageError] = useState(false);
  const top = detection.result?.[0];
  const confidence = top?.confidence ? `${(top.confidence * 100).toFixed(1)}%` : '';
  
  const hasValidImage = detection.thumbnailDataUrl && !imageError;
  
  return (
    <div className="p-3 bg-white rounded shadow flex gap-3 items-center">
      {hasValidImage ? (
        <img 
          src={detection.thumbnailDataUrl} 
          alt="thumb" 
          className="w-20 h-20 object-cover rounded" 
          onError={() => {
            console.error('Image failed to load:', detection.thumbnailDataUrl);
            setImageError(true);
          }}
          loading="lazy"
        />
      ) : (
        <div className="w-20 h-20 bg-slate-100 rounded flex items-center justify-center text-xs text-slate-400">No image</div>
      )}
      <div className="flex-1">
        <div className="font-semibold">{top?.label ?? "No result"}</div>
        {confidence && <div className="text-xs text-emerald-600">{confidence} confidence</div>}
        <div className="text-xs text-slate-500">{new Date(detection.createdAt).toLocaleString()}</div>
      </div>
      <div>
        <button onClick={onView} className="text-sm text-emerald-600 hover:text-emerald-700 font-medium">View</button>
      </div>
    </div>
  );
}
