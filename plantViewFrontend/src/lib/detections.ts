export type DetectionResult = {
  label: string;
  confidence: number;
  boxes?: Array<{ x: number; y: number; w: number; h: number }>;
};

export type Detection = {
  id: string;
  userId?: string;
  createdAt: string;
  status: "pending" | "done" | "error";
  imageDataUrl: string; // base64 data URL or signed URL
  thumbnailDataUrl: string;
  result?: DetectionResult[];
  modelVersion?: string;
  fileKey?: string; // Supabase storage key for regenerating URLs
};

const STORAGE_KEY = "detections_v1";
const SERVER_CACHE_KEY = "server_detections_cache";
const CACHE_TIMESTAMP_KEY = "server_detections_timestamp";
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

function readStore(): Detection[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as Detection[];
  } catch (e) {
    return [];
  }
}

function writeStore(items: Detection[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}

// Server cache management
export function getServerCache(): { items: Detection[], timestamp: number } | null {
  try {
    const items = localStorage.getItem(SERVER_CACHE_KEY);
    const timestamp = localStorage.getItem(CACHE_TIMESTAMP_KEY);
    
    if (!items || !timestamp) return null;
    
    const ts = parseInt(timestamp, 10);
    const age = Date.now() - ts;
    
    // Return null if cache is expired
    if (age > CACHE_TTL) {
      localStorage.removeItem(SERVER_CACHE_KEY);
      localStorage.removeItem(CACHE_TIMESTAMP_KEY);
      return null;
    }
    
    return {
      items: JSON.parse(items) as Detection[],
      timestamp: ts
    };
  } catch (e) {
    return null;
  }
}

export function setServerCache(items: Detection[]) {
  try {
    localStorage.setItem(SERVER_CACHE_KEY, JSON.stringify(items));
    localStorage.setItem(CACHE_TIMESTAMP_KEY, Date.now().toString());
  } catch (e) {
    // Cache write failed, continue without caching
  }
}

export function clearServerCache() {
  localStorage.removeItem(SERVER_CACHE_KEY);
  localStorage.removeItem(CACHE_TIMESTAMP_KEY);
}

export function listDetections(): Detection[] {
  return readStore();
}

export function getDetection(id: string): Detection | undefined {
  return readStore().find((d) => d.id === id);
}

export async function reprocessDetection(detection: Detection): Promise<Detection | undefined> {
  if (!detection.imageDataUrl && !detection.fileKey) {
    return undefined;
  }

  try {
    const token = localStorage.getItem('authToken');
    if (!token) {
      throw new Error('Not authenticated');
    }

    // Prefer file_key over signed URL (which may be expired)
    // If we have a file_key, backend will regenerate a fresh signed URL
    const payload: any = {};
    if (detection.fileKey) {
      payload.file_key = detection.fileKey;
    } else {
      payload.image_url = detection.imageDataUrl;
    }

    // Send to /api/detect for reprocessing
    const response = await fetch(`${API_URL}/api/detect`, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      let errorMessage = `Reprocess failed: ${response.status} ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData && errorData.error?.message) {
          errorMessage = errorData.error.message;
        }
      } catch (jsonErr) {
        // response body is not JSON, keep default errorMessage
      }
      throw new Error(errorMessage);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error?.message || 'Detection failed');
    }

    // Extract data from standardized response
    const { data, meta } = result;

    // Validate detection data exists
    if (!data?.detection?.class_name || data?.detection?.confidence === undefined) {
      throw new Error('Invalid response: missing detection data');
    }

    // Create updated detection object
    const updatedDetection: Detection = {
      ...detection,
      result: [
        {
          label: data.detection.class_name,
          confidence: data.detection.confidence,
        },
      ],
      status: "done",
      modelVersion: meta?.model_version,
    };

    // If this detection is in localStorage, update it there too
    const items = readStore();
    const idx = items.findIndex((d) => d.id === detection.id);
    if (idx !== -1) {
      items[idx] = updatedDetection;
      writeStore(items);
    }

    // Clear server cache to force refresh on next load
    clearServerCache();

    return updatedDetection;
  } catch (err) {
    throw err;
  }
}

export function saveDetection(d: Detection) {
  const items = readStore();
  items.unshift(d);
  writeStore(items);
}
