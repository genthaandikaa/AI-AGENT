import React, { useState } from 'react';
import { Building2, ExternalLink, RefreshCw, Eye, Sparkles } from 'lucide-react';

export const VirtualOfficeView: React.FC = () => {
  const [key, setKey] = useState(0);

  return (
    <div className="space-y-5 animate-fadeIn pb-12">
      {/* Header */}
      <div className="bg-slate-900 rounded-3xl p-6 text-white border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center border border-indigo-500/30">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                HERMES 3D VIRTUAL OFFICE
              </span>
              <span className="text-[11px] text-emerald-400 font-bold flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                Live 3D Agent HQ Online
              </span>
            </div>
            <h1 className="text-xl font-bold">Virtual Office 3D & Agent Desk Simulation</h1>
            <p className="text-xs text-slate-400">
              Penggabungan Hermes3D (:3000) langsung ke dalam dashboard utama port 5173
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setKey(k => k + 1)}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all cursor-pointer"
            title="Reload Kantor 3D"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <a
            href="http://localhost:3000/office"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition-all cursor-pointer"
          >
            <span>Buka di Tab Terpisah (:3000)</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>

      {/* Embedded Iframe */}
      <div className="bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden shadow-2xl h-[820px]">
        <iframe 
          key={key}
          src="/virtual-office/office"
          title="Hermes 3D Office"
          className="w-full h-full border-none"
        />
      </div>
    </div>
  );
};
