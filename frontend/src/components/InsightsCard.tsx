import React from 'react';
import { Bot, Layers, Sparkles } from 'lucide-react';

export const InsightsCard: React.FC = () => {
  return (
    <div className="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-bold text-slate-900 tracking-tight">Insights</h3>
        <select className="bg-slate-50 border border-slate-200/80 rounded-xl px-2.5 py-1 text-[11px] font-semibold text-slate-600 focus:outline-none cursor-pointer">
          <option>This Week</option>
          <option>Last 30 Days</option>
        </select>
      </div>

      {/* Two Mini Cards Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {/* Most Active Agent */}
        <div className="bg-slate-50 rounded-2xl p-3 border border-slate-100">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-7 h-7 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[9px] uppercase font-bold text-slate-400 block">Most Active Agent</span>
              <h4 className="text-xs font-bold text-slate-800">Alex Vance</h4>
            </div>
          </div>
          <p className="text-[10px] text-slate-500 font-medium">32% of total tasks</p>
          {/* Mini Sparkline SVG */}
          <div className="h-6 w-full mt-2">
            <svg viewBox="0 0 100 20" className="w-full h-full stroke-purple-500 fill-none">
              <path d="M0 15 Q 25 5, 50 12 T 100 4" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
        </div>

        {/* Top Workflow */}
        <div className="bg-slate-50 rounded-2xl p-3 border border-slate-100">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-7 h-7 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[9px] uppercase font-bold text-slate-400 block">Top Workflow</span>
              <h4 className="text-xs font-bold text-slate-800">Video Engine</h4>
            </div>
          </div>
          <p className="text-[10px] text-slate-500 font-medium">94% success rate</p>
          {/* Mini Sparkline SVG */}
          <div className="h-6 w-full mt-2">
            <svg viewBox="0 0 100 20" className="w-full h-full stroke-emerald-500 fill-none">
              <path d="M0 16 Q 30 18, 60 8 T 100 2" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
        </div>
      </div>

      {/* Tip Banner */}
      <div className="flex items-center gap-2 bg-indigo-50/70 border border-indigo-100/80 rounded-2xl px-3.5 py-2 text-indigo-900 text-xs font-medium">
        <Sparkles className="w-4 h-4 text-indigo-600 flex-shrink-0" />
        <span className="truncate">Tip: Short-form video local rendering latency improved by 40%.</span>
      </div>
    </div>
  );
};
