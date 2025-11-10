import { useEffect, useState } from "react";
import { listDetections, type Detection } from "../../lib/mockDetections";
import DetectionCard from "./DetectionCard";

export default function HistoryList({ onOpen }: { onOpen?: (id: string) => void }) {
  const [items, setItems] = useState<Detection[]>([]);

  useEffect(() => {
    setItems(listDetections());
    // simple subscription: poll every 2s to pick up changes from uploads
    const t = setInterval(() => setItems(listDetections()), 2000);
    return () => clearInterval(t);
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
