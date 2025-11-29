import { useEffect, useState } from "react";
import { listDetections, type Detection } from "../../lib/detections";
import DetectionCard from "./DetectionCard";
import { getToken } from "../../lib/api";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export default function HistoryList({ onOpen }: { onOpen?: (id: string) => void }) {
  const [items, setItems] = useState<Detection[]>([]);

  useEffect(() => {
    let isMounted = true;

    const fetchAndSetItems = async () => {
      if (!isMounted) return;
      try {
        const token = getToken();
        
        if (!token) {
          if (isMounted) setItems(listDetections());
          return;
        }

        const resp = await fetch(`${API_URL}/api/uploads`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!resp.ok) {
          if (isMounted) setItems(listDetections());
          return;
        }

        const json = await resp.json();

        if (!Array.isArray(json)) {
          if (isMounted) setItems(listDetections());
          return;
        }

        const serverItems: Detection[] = json.map((r: any) => {
          let result = undefined;
          if (r.detection && typeof r.detection === 'object') {
            // Handle both old and new response formats
            const detection = r.detection;
            const className = detection.class_name || 'Unknown';
            const confidence = detection.confidence || 0;
            result = [{ 
              label: className,
              confidence: confidence
            }];
          }
          return {
            id: String(r.id),
            createdAt: r.created_at || new Date().toISOString(),
            status: 'done',
            imageDataUrl: r.file_url || null,
            thumbnailDataUrl: r.file_url || null,
            result: result,
            modelVersion: r.model_version || 'server',
          };
        });

        if (isMounted) {
          setItems(serverItems);
        }
      } catch (err) {
        // Exception during history fetch - silently fallback to local detections
        if (isMounted) setItems(listDetections());
      }
    };

    // Fetch once on mount
    fetchAndSetItems();

    return () => {
      isMounted = false;
    };
  }, []);

  if (!items.length) return <div className="text-sm text-slate-500">No detections yet.</div>;

  return (
    <div className="grid gap-4">
      {items.map((d) => (
        <DetectionCard key={d.id} detection={d} onView={onOpen} />
      ))}
    </div>
  );
}
