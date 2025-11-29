import { useAuth } from "../context/AuthContext";
import UploadForm from "../components/dashboard/UploadForm";
import HistoryList from "../components/dashboard/HistoryList";
import DetectionDetails from "../components/dashboard/DetectionDetails";
import { useState } from "react";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [selected, setSelected] = useState<string | null>(null);
  const [latest, setLatest] = useState<any | null>(null);

  return (
    <div className="container mx-auto py-12">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-sm text-slate-600 mt-1">Welcome back{user ? `, ${user.email}` : ""}.</p>
        </div>
        <div>
          <button onClick={logout} className="text-sm text-red-600">Sign out</button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <aside className="lg:col-span-1">
          <div className="bg-white rounded-lg p-6 shadow">
            <UploadForm onComplete={(d) => setLatest(d)} />
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
                  <div className="text-sm text-slate-500">Confidence: {latest.result?.[0]?.confidence}</div>
                  <div className="mt-4">
                    <button onClick={() => setSelected(latest.id)} className="px-3 py-2 bg-emerald-600 text-white rounded">View details</button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="mt-4 text-sm text-slate-500">No recent results. Upload an image to test.</div>
            )}
          </div>

          <div className="bg-white rounded-lg p-6 shadow">
            <h2 className="font-semibold mb-4">History</h2>
            <HistoryList onOpen={(id) => setSelected(id)} />
          </div>
        </main>
      </div>

      {selected && <DetectionDetails id={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
