import { useAuth } from "../context/AuthContext";
import UploadForm from "../components/dashboard/UploadForm";
import HistoryList from "../components/dashboard/HistoryList";
import DetectionDetails from "../components/dashboard/DetectionDetails";
import StatCard from "../components/dashboard/StatCard";
import { useState } from "react";
import type { Detection } from "../lib/detections";
import { listDetections } from "../lib/detections";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [selected, setSelected] = useState<Detection | null>(null);
  const [latest, setLatest] = useState<Detection | null>(null);
  const [uploadComplete, setUploadComplete] = useState<number>(0);

  const handleUploadComplete = (d: Detection) => {
    setLatest(d);
    setUploadComplete(Date.now()); // Trigger history refresh
  };

  // derive small stats from local store as a fast fallback
  const local = listDetections();
  const totalDetections = local.length;
  const avgConfidence = (() => {
    const withConf = local.flatMap((d) => (d.result && d.result[0] && typeof d.result[0].confidence === 'number') ? [d.result[0].confidence] : []);
    if (!withConf.length) return null;
    const avg = withConf.reduce((s, v) => s + v, 0) / withConf.length;
    return Math.round(avg * 100) / 100; // fraction
  })();

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-12">
      {/* hero */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-brand-500">Dashboard</h1>
          <p className="text-sm text-slate-600 mt-1">Welcome back{user ? `, ${user.email}` : ""} — overview of recent detections and quick actions.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={logout} className="text-sm text-red-600">Sign out</button>
          <button onClick={() => { const el = document.getElementById('upload-form'); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' }); }} className="px-4 py-2 bg-accent-500 text-white rounded hover:bg-emerald-700">Upload & Detect</button>
        </div>
      </div>

      {/* stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        <StatCard title="Total detections" value={totalDetections} subtitle="Stored locally or from server" />
        <StatCard title="Average confidence" value={avgConfidence !== null ? `${(avgConfidence * 100).toFixed(1)}%` : '—'} subtitle="Based on local detections" />
        <StatCard title="Uploads" value={totalDetections} subtitle="Uploads received" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <aside className="lg:col-span-1">
          <div id="upload-form" className="bg-white rounded-lg p-6 shadow">
            <UploadForm onComplete={handleUploadComplete} />
          </div>

          <div className="mt-6 bg-white rounded-lg p-6 shadow">
            <h3 className="font-semibold mb-3">Live stream (mock)</h3>
            <p className="text-sm text-slate-500">Start a datastream to send frames for detection. (Not implemented in mock)</p>
          </div>
        </aside>

        <main className="lg:col-span-2">
          <div className="bg-white rounded-lg p-6 shadow mb-6">
            <h2 className="font-semibold">Latest result</h2>
            {latest ? (
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                <img src={latest.thumbnailDataUrl} alt="latest" className="w-full rounded" />
                <div>
                  <div className="font-semibold">{latest.result?.[0]?.label}</div>
                  <div className="text-sm text-slate-500">Confidence: {latest.result?.[0]?.confidence ? `${(latest.result[0].confidence * 100).toFixed(1)}%` : 'N/A'}</div>
                  <div className="mt-4">
                    <button onClick={() => setSelected(latest)} className="px-3 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700">View details</button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="mt-4 text-sm text-slate-500">No recent results. Upload an image to test.</div>
            )}
          </div>

          <div className="bg-white rounded-lg p-6 shadow">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold">Recent detections</h2>
            </div>
            <HistoryList onOpen={(detection) => setSelected(detection)} onUploadComplete={uploadComplete} />
          </div>
        </main>
      </div>

      {selected && <DetectionDetails detection={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
