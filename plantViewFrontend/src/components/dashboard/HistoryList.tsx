import { useEffect, useState } from "react";
import { listDetections, type Detection, getServerCache, setServerCache } from "../../lib/detections";
import DetectionCard from "./DetectionCard";
import { getToken } from "../../lib/api";
import { RefreshCw } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export default function HistoryList({ onOpen, onUploadComplete }: { onOpen?: (detection: Detection) => void; onUploadComplete?: number }) {
  const [items, setItems] = useState<Detection[]>([]);
  const [loading, setLoading] = useState(false);
  const [lastFetch, setLastFetch] = useState<number | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchAndSetItems = async (forceRefresh = false) => {
      if (!isMounted) return;
      
      const token = getToken();
      
      if (!token) {
        if (isMounted) setItems(listDetections());
        return;
      }

      // Try cache first unless forced refresh
      if (!forceRefresh) {
        const cached = getServerCache();
        if (cached) {
          if (isMounted) {
            setItems(cached.items);
            setLastFetch(cached.timestamp);
          }
          return;
        }
      }

      setLoading(true);
      
      try {
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
            status: 'done' as const,
            imageDataUrl: r.file_url || null,
            thumbnailDataUrl: r.file_url || null,
            result: result,
            modelVersion: r.model_version || 'server',
          };
        });

        // Cache the results
        setServerCache(serverItems);
        
        if (isMounted) {
          setItems(serverItems);
          setLastFetch(Date.now());
        }
      } catch (err) {
        // Exception during history fetch - silently fallback to local detections
        if (isMounted) setItems(listDetections());
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    // Fetch once on mount
    fetchAndSetItems();

    return () => {
      isMounted = false;
    };
  }, []);

  // Refresh when new upload completes
  useEffect(() => {
    if (onUploadComplete) {
      fetchAndSetItems(true);
    }
  }, [onUploadComplete]);

  const handleRefresh = () => {
    fetchAndSetItems(true);
  };

  const fetchAndSetItems = async (forceRefresh = false) => {
    const token = getToken();
    
    if (!token) {
      setItems(listDetections());
      return;
    }

    // Try cache first unless forced refresh
    if (!forceRefresh) {
      const cached = getServerCache();
      if (cached) {
        setItems(cached.items);
        setLastFetch(cached.timestamp);
        return;
      }
    }

    setLoading(true);
    
    try {
      const resp = await fetch(`${API_URL}/api/uploads`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!resp.ok) {
        setItems(listDetections());
        return;
      }

      const json = await resp.json();

      if (!Array.isArray(json)) {
        setItems(listDetections());
        return;
      }

      const serverItems: Detection[] = json.map((r: any) => {
        let result = undefined;
        if (r.detection && typeof r.detection === 'object') {
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
          status: 'done' as const,
          imageDataUrl: r.file_url || null,
          thumbnailDataUrl: r.file_url || null,
          result: result,
          modelVersion: r.model_version || 'server',
          fileKey: r.file_key, // Store file_key for reprocessing
        };
      });

      setServerCache(serverItems);
      setItems(serverItems);
      setLastFetch(Date.now());
    } catch (err) {
      setItems(listDetections());
    } finally {
      setLoading(false);
    }
  };

  const cacheAge = lastFetch ? Math.floor((Date.now() - lastFetch) / 1000) : null;
  const cacheAgeText = cacheAge ? (cacheAge < 60 ? `${cacheAge}s ago` : `${Math.floor(cacheAge / 60)}m ago`) : null;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="text-xs text-slate-500">
          {cacheAgeText && `Updated ${cacheAgeText}`}
        </div>
        <button
          onClick={handleRefresh}
          disabled={loading}
          className="text-xs text-emerald-600 hover:text-emerald-700 disabled:text-slate-400 flex items-center gap-1"
          title="Refresh history"
        >
          <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>
      
      {!items.length ? (
        <div className="text-sm text-slate-500">No detections yet.</div>
      ) : (
        <div className="grid gap-4">
          {items.map((d) => (
            <DetectionCard key={d.id} detection={d} onView={() => onOpen?.(d)} />
          ))}
        </div>
      )}
    </div>
  );
}
