import React, { useState } from 'react';
import { Video, Layers, TrendingUp, ShieldCheck, Play, CheckCircle2, Download } from 'lucide-react';

export const WorkflowsView: React.FC = () => {
  const [isProducing, setIsProducing] = useState(false);
  const [productionResult, setProductionResult] = useState<any>(null);

  const handleTriggerProduction = async () => {
    setIsProducing(true);
    setProductionResult(null);
    try {
      const res = await fetch('/api/creator/produce', { method: 'POST' });
      const data = await res.json();
      setProductionResult(data);
    } catch (err) {
      alert('Video production error: ' + err);
    } finally {
      setIsProducing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Creator Division Card */}
      <div className="bg-white rounded-3xl p-6 border border-slate-100 shadow-soft space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-purple-100 text-purple-600 flex items-center justify-center">
              <Video className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">Creator Division — 9:16 Video Engine</h3>
              <p className="text-xs text-slate-500">
                Native offline Windows TTS + FFmpeg 1080x1920 local rendering + QA Gate + TikTok & YouTube uploader spec.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleTriggerProduction}
              disabled={isProducing}
              className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-2xl text-xs font-semibold shadow-md disabled:opacity-50 transition-all"
            >
              <Play className={`w-3.5 h-3.5 ${isProducing ? 'animate-spin' : ''}`} />
              <span>{isProducing ? 'Rendering Local Video...' : 'Produce Video Now'}</span>
            </button>
          </div>
        </div>

        {/* Video Pipeline Output & Specs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100">
            <span className="text-slate-400 font-semibold block text-[10px] uppercase">Format & Resolution</span>
            <span className="font-bold text-slate-800 text-sm mt-0.5 block">1080x1920 (9:16 Vertical)</span>
            <span className="text-slate-500 text-[11px] mt-1 block">Optimized for TikTok & Shorts</span>
          </div>
          <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100">
            <span className="text-slate-400 font-semibold block text-[10px] uppercase">Audio & Subtitles</span>
            <span className="font-bold text-slate-800 text-sm mt-0.5 block">Windows System.Speech + SRT</span>
            <span className="text-slate-500 text-[11px] mt-1 block">Zero cloud cost TTS burned in</span>
          </div>
          <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100">
            <span className="text-slate-400 font-semibold block text-[10px] uppercase">Governance Gate</span>
            <span className="font-bold text-amber-600 text-sm mt-0.5 block">Draft Stage (CEO Approval Required)</span>
            <span className="text-slate-500 text-[11px] mt-1 block">Held before public release</span>
          </div>
        </div>

        {/* Result Callout if run */}
        {productionResult && (
          <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">Production Cycle Completed Successfully!</p>
              <p className="text-[11px] text-emerald-800 mt-1">
                Task ID: <code>{productionResult.task_id}</code> | Output: <code>{productionResult.rendered_video}</code> | QA: {productionResult.qa_status}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* 2. Affiliate, Trading & Cybersecurity Divisions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Affiliate */}
        <div className="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft flex flex-col justify-between">
          <div>
            <div className="w-10 h-10 rounded-2xl bg-sky-100 text-sky-600 flex items-center justify-center mb-3">
              <Layers className="w-5 h-5" />
            </div>
            <h4 className="text-xs font-bold text-slate-900">Affiliate Division</h4>
            <p className="text-[11px] text-slate-500 mt-1">
              Monitors partner referral campaigns, shortens tracking URLs, and syncs promotional angles.
            </p>
            <div className="mt-3 text-[11px] text-slate-600 space-y-1">
              <div>• Active Deals: <strong>Shopee & Tokopedia</strong></div>
              <div>• Funnel Status: <strong>Tracking Ready</strong></div>
            </div>
          </div>
        </div>

        {/* Trading */}
        <div className="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft flex flex-col justify-between">
          <div>
            <div className="w-10 h-10 rounded-2xl bg-amber-100 text-amber-600 flex items-center justify-center mb-3">
              <TrendingUp className="w-5 h-5" />
            </div>
            <h4 className="text-xs font-bold text-slate-900">Trading Division</h4>
            <p className="text-[11px] text-slate-500 mt-1">
              Quantitative strategy backtesting in simulated paper mode only. Zero real capital risk.
            </p>
            <div className="mt-3 bg-emerald-50 border border-emerald-200 p-2 rounded-xl text-[10px] text-emerald-800 font-semibold">
              🔒 Live Execution Guard: STRICTLY LOCKED
            </div>
          </div>
        </div>

        {/* Cybersecurity */}
        <div className="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft flex flex-col justify-between">
          <div>
            <div className="w-10 h-10 rounded-2xl bg-rose-100 text-rose-600 flex items-center justify-center mb-3">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h4 className="text-xs font-bold text-slate-900">Cybersecurity Division</h4>
            <p className="text-[11px] text-slate-500 mt-1">
              Continuous monitoring of local ports, secret leak detection in git commits, and token safety.
            </p>
            <div className="mt-3 text-[11px] text-emerald-600 font-semibold">
              ✓ No plain-text API secrets exposed.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
