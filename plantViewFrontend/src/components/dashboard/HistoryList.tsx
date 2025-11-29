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
            result = [{ 
              label: r.detection.class_name || 'Unknown',
              confidence: r.detection.confidence || 0
            }];
          }
          return {
            id: String(r.id),
            createdAt: r.created_at || new Date().toISOString(),
            status: 'done',
            imageDataUrl: r.file_url || null,
            thumbnailDataUrl: r.file_url || null,
            result: result,
            modelVersion: 'server',
          };
        });

        if (isMounted) {
          setItems(serverItems);
        }
      } catch (err) {
        console.error('[HistoryList] Exception:', err);
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
