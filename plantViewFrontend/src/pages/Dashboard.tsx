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

  function prettyLabel(raw?: string | null) {
    if (!raw) return 'No result';
    const cleaned = raw.replace(/[_,]+/g, ' ').replace(/\s+/g, ' ').trim();
    return cleaned
      .split(' ')
      .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
      .join(' ');
  }

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-12">
      {/* hero */}
      <div className="mb-8">
        <div className="bg-gradient-to-r from-brand-50 to-white dark:from-slate-50 rounded-lg p-6 md:p-8 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-brand-500">Dashboard</h1>
            <p className="text-sm text-slate-600 mt-2 max-w-xl">Welcome back{user ? `, ${user.email}` : ""} — overview of recent detections and quick actions.</p>
          </div>

          <div className="flex items-center gap-3">
            {/* grouped pill with curved border containing sign-out and CTA */}
            <div className="inline-flex items-center rounded-full border border-slate-200 bg-white px-1 py-1 shadow-sm">
              <button
                onClick={logout}
                className="text-sm text-red-600 px-3 py-1 rounded-full hover:bg-red-50 transition"
                aria-label="Sign out"
              >
                Sign out
              </button>

              <div className="h-6 w-px bg-slate-100 mx-1" aria-hidden="true" />

              <button
                onClick={() => { const el = document.getElementById('upload-form'); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' }); }}
                className="ml-1 px-4 py-2 bg-white text-accent-500 border border-accent-500/20 rounded-full shadow-sm hover:bg-accent-500/5 focus:outline-none focus:ring-2 focus:ring-accent-500/20 transition"
              >
                Upload & Detect
              </button>
            </div>
          </div>
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
                  <div className="font-semibold">{prettyLabel(latest.result?.[0]?.label)}</div>
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
