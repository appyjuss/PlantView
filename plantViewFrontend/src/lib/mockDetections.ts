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

const STORAGE_KEY = "mock_detections_v1";

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

function randChoice<T>(arr: T[]) {
  return arr[Math.floor(Math.random() * arr.length)];
}

export async function createDetectionFromFile(file: File, userId?: string): Promise<Detection> {
  const dataUrl = await readFileAsDataURL(file);
  // simple thumbnail: small canvas
  const thumb = await makeThumbnail(dataUrl, 240);

  // mock inference
  const labels = ["Late blight", "Powdery mildew", "Bacterial spot", "Healthy"];
  const label = randChoice(labels);
  const confidence = +(0.6 + Math.random() * 0.4).toFixed(2);

  const detection: Detection = {
    id: String(Date.now()) + Math.random().toString(36).slice(2, 9),
    userId,
    createdAt: new Date().toISOString(),
    status: "done",
    imageDataUrl: dataUrl,
    thumbnailDataUrl: thumb,
    result: [{ label, confidence }],
    modelVersion: "mock-v1",
  };

  const items = readStore();
  items.unshift(detection);
  writeStore(items);
  return detection;
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
    // convert data URL back to File for upload
    const blob = await fetch(items[idx].imageDataUrl).then((r) => r.blob());
    const file = new File([blob], `reprocess_${id}.jpg`, { type: "image/jpeg" });

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Reprocess failed: ${response.status}`);
    }

    const data = await response.json();

    // update detection with new server prediction
    items[idx].result = [
      {
        label: data.prediction.class_name,
        confidence: data.prediction.confidence ?? 0,
      },
    ];
    items[idx].status = "done";
    items[idx].modelVersion = data.prediction.modelVersion ?? "server";
    writeStore(items);

    return items[idx];
  } catch (err) {
    console.error("Reprocess error:", err);
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

function readFileAsDataURL(file: File): Promise<string> {
  return new Promise((res, rej) => {
    const fr = new FileReader();
    fr.onload = () => res(String(fr.result));
    fr.onerror = rej;
    fr.readAsDataURL(file);
  });
}

function makeThumbnail(dataUrl: string, size = 240): Promise<string> {
  return new Promise((res) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      const scale = Math.min(size / img.width, size / img.height, 1);
      canvas.width = Math.round(img.width * scale);
      canvas.height = Math.round(img.height * scale);
      const ctx = canvas.getContext("2d")!;
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      res(canvas.toDataURL("image/jpeg", 0.8));
    };
    img.src = dataUrl;
  });
}
