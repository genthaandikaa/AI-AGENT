import React from 'react';
import { Film, Video, ExternalLink, Play, Sparkles } from 'lucide-react';

export const VideoStudioView: React.FC = () => {
  return (
    <div className="space-y-5 animate-fadeIn pb-12">
      {/* Header */}
      <div className="bg-slate-900 rounded-3xl p-6 text-white border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-pink-500/20 text-pink-400 flex items-center justify-center border border-pink-500/30">
            <Film className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-pink-500/20 text-pink-300 border border-pink-500/30">
                CHEAT CLIP PRO UNIFIED
              </span>
              <span className="text-[11px] text-emerald-400 font-bold flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                Local Engine Online
              </span>
            </div>
            <h1 className="text-xl font-bold">Video Clipper Studio (Shorts 9:16 & Explainer 16:9)</h1>
            <p className="text-xs text-slate-400">
              Penggabungan project Cheat Clip PRO (:8000) langsung ke dalam dashboard utama port 5173
            </p>
          </div>
        </div>

        <a
          href="http://127.0.0.1:8000"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition-all cursor-pointer"
        >
          <span>Buka di Tab Terpisah (:8000)</span>
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>

      {/* Embedded Iframe */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-lg h-[820px]">
        <iframe 
          src="/clip-pro/"
          title="Cheat Clip PRO"
          className="w-full h-full border-none"
        />
      </div>
    </div>
  );
};
