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
  imageDataUrl: string; // base64 data URL
  thumbnailDataUrl: string;
  result?: DetectionResult[];
  modelVersion?: string;
};

const STORAGE_KEY = "detections_v1";

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

export function listDetections(): Detection[] {
  return readStore();
}

export function getDetection(id: string): Detection | undefined {
  return readStore().find((d) => d.id === id);
}

export async function reprocessDetection(id: string): Promise<Detection | undefined> {
  const items = readStore();
  const idx = items.findIndex((d) => d.id === id);
  if (idx === -1) return undefined;

  // mark as pending while reprocessing
  items[idx].status = "pending";
  writeStore(items);

  try {
    const token = localStorage.getItem('authToken');
    if (!token) {
      throw new Error('Not authenticated');
    }

    // Send image_url to /api/detect for reprocessing
    const imageUrl = items[idx].imageDataUrl;

    const response = await fetch("/api/detect", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ image_url: imageUrl }),
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

    // update detection with new server prediction
    items[idx].result = [
      {
        label: data.detection.class_name,
        confidence: data.detection.confidence,
      },
    ];
    items[idx].status = "done";
    items[idx].modelVersion = meta?.model_version;
    writeStore(items);

    return items[idx];
  } catch (err) {
    // Reprocess error - mark as failed and persist state
    items[idx].status = "error";
    writeStore(items);
    return undefined;
  }
}

export function saveDetection(d: Detection) {
  const items = readStore();
  items.unshift(d);
  writeStore(items);
}
