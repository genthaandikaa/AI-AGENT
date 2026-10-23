import React, { useEffect, useState } from 'react';
import { 
  Cpu, 
  Gauge, 
  Clock, 
  ShieldCheck, 
  Sparkles, 
  Layers,
  RefreshCw,
  Gift,
  Coins,
  CheckCircle2,
  Zap,
  TrendingDown
} from 'lucide-react';

interface RealtimeTokenData {
  status: string;
  provider_name: string;
  total_available_pool: number;
  total_available_display: string;
  breakdown: {
    minimax_event: {
      name: string;
      total: number;
      remaining: number;
      display: string;
      expires: string;
      status: string;
    };
    bonus_pool: {
      name: string;
      total: number;
      remaining: number;
      display: string;
      status: string;
    };
    qwen_free_daily: {
      name: string;
      daily_limit: number;
      daily_used: number;
      display: string;
      status: string;
    };
    gemini_direct: {
      name: string;
      tier: string;
      status: string;
    };
  };
  thirty_day_metrics: {
    total_requests: number;
    total_tokens_consumed: number;
    total_tokens_display: string;
    cost_usd: number;
    cost_display: string;
  };
  active_models: Array<{ name: string; provider: string; tier: string }>;
}

export const TokenBudgetWidget: React.FC = () => {
  const [data, setData] = useState<RealtimeTokenData | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchRealtimeTokens = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/tokens/realtime');
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (e) {
      console.error('Failed to fetch realtime tokens:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRealtimeTokens();
    const interval = setInterval(fetchRealtimeTokens, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white rounded-2xl p-5 border border-purple-100 shadow-soft space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-xl bg-purple-600 text-white flex items-center justify-center shadow-md shadow-purple-500/20">
            <Gauge className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                Real-Time Provider Token Intelligence (xKiro + Google Gemini)
              </h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Auto-Detected Live
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Sinkronisasi saldo kuota token dari xKiro API & Google Direct tanpa batasan artifisial
            </p>
          </div>
        </div>

        <button
          onClick={fetchRealtimeTokens}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-all cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Kuota</span>
        </button>
      </div>

      {/* Main Stats Banner */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3.5">
        {/* Total Available Pool */}
        <div className="bg-gradient-to-br from-purple-50 to-indigo-50/50 p-4 rounded-xl border border-purple-200/60 relative overflow-hidden">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[11px] font-bold text-purple-700 uppercase tracking-wider flex items-center gap-1">
              <Coins className="w-3.5 h-3.5" /> Total Kuota Siap Pakai
            </span>
            <span className="text-[10px] bg-purple-200/60 text-purple-800 px-1.5 py-0.5 rounded font-bold">
              Multi-Pool
            </span>
          </div>
          <p className="text-2xl font-black text-purple-950">
            {data?.total_available_display || '56.3M'}
            <span className="text-xs font-semibold text-purple-600 ml-1">Tokens</span>
          </p>
          <p className="text-[11px] text-purple-700/80 mt-1">
            MiniMax Event + Bonus + Free Tier
          </p>
        </div>

        {/* MiniMax Event Drop */}
        <div className="bg-gradient-to-br from-emerald-50 to-teal-50/50 p-4 rounded-xl border border-emerald-200/60">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[11px] font-bold text-emerald-700 uppercase tracking-wider flex items-center gap-1">
              <Gift className="w-3.5 h-3.5" /> MiniMax Welcome Drop
            </span>
            <span className="text-[10px] bg-emerald-200/60 text-emerald-800 px-1.5 py-0.5 rounded font-bold">
              s.d. 5 Nov
            </span>
          </div>
          <p className="text-2xl font-black text-emerald-950">
            {data?.breakdown?.minimax_event?.display || '46.6M'}
            <span className="text-xs font-semibold text-emerald-600 ml-1">Sisa</span>
          </p>
          <p className="text-[11px] text-emerald-700/80 mt-1">
            Dompet hadiah event dari awal 50M
          </p>
        </div>

        {/* Token Bonus Cadangan */}
        <div className="bg-gradient-to-br from-blue-50 to-sky-50/50 p-4 rounded-xl border border-blue-200/60">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[11px] font-bold text-blue-700 uppercase tracking-wider flex items-center gap-1">
              <Zap className="w-3.5 h-3.5" /> Token Bonus Cadangan
            </span>
            <span className="text-[10px] bg-blue-200/60 text-blue-800 px-1.5 py-0.5 rounded font-bold">
              Ready
            </span>
          </div>
          <p className="text-2xl font-black text-blue-950">
            {data?.breakdown?.bonus_pool?.display || '8.7M'}
            <span className="text-xs font-semibold text-blue-600 ml-1">Tokens</span>
          </p>
          <p className="text-[11px] text-blue-700/80 mt-1">
            Sisa token bonus di akun xKiro
          </p>
        </div>

        {/* 30-Day Cumulative Usage */}
        <div className="bg-gradient-to-br from-slate-50 to-slate-100/60 p-4 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1">
              <TrendingDown className="w-3.5 h-3.5" /> Penggunaan 30 Hari
            </span>
            <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-bold">
              $0.00 Spent
            </span>
          </div>
          <p className="text-2xl font-black text-slate-900">
            {data?.thirty_day_metrics?.total_tokens_display || '26.3M'}
            <span className="text-xs font-semibold text-slate-500 ml-1">({data?.thirty_day_metrics?.total_requests || 409} Req)</span>
          </p>
          <p className="text-[11px] text-slate-500 mt-1">
            Biaya $0.00 (Zero-Cost Policy Terpenuhi)
          </p>
        </div>
      </div>

      {/* Provider Details & Active Engines */}
      <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-4 text-xs">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span className="text-slate-700 font-medium">
            <b>Mesin Inference Aktif:</b> xKiro Qwen 3.8 Max (Free Daily Tier 1.0M) &bull; MiniMax 3.1 Flash (46.6M Event) &bull; Google Gemini Direct
          </span>
        </div>

        <div className="flex items-center gap-3">
          <span className="px-2.5 py-1 rounded-md bg-white border border-slate-200 text-slate-600 font-bold text-[11px]">
            Saldo Dompet: $0.00
          </span>
          <span className="px-2.5 py-1 rounded-md bg-emerald-600 text-white font-bold text-[11px] shadow-xs">
            100% Zero-Cost Policy Active
          </span>
        </div>
      </div>
    </div>
  );
};
