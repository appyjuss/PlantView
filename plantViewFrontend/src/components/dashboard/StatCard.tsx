import React from 'react';

export default function StatCard({ title, value, subtitle }: { title: string; value: React.ReactNode; subtitle?: string }) {
  return (
    <div className="bg-white rounded-lg p-4 shadow">
      <div className="text-sm text-slate-500">{title}</div>
      <div className="mt-2 text-2xl font-bold text-slate-800">{value}</div>
      {subtitle && <div className="mt-1 text-xs text-slate-500">{subtitle}</div>}
    </div>
  );
}
