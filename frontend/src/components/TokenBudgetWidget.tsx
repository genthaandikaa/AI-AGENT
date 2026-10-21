import React, { useEffect, useState } from 'react';
import { 
  Cpu, 
  Gauge, 
  Clock, 
  ShieldCheck, 
  AlertTriangle, 
  Sparkles, 
  Layers,
  RefreshCw
} from 'lucide-react';

export interface BudgetStatus {
  window_id: string;
  date_str: string;
  timezone: string;
  daily_limit: number;
  soft_limit: number;
  conservation_limit: number;
  safety_reserve: number;
  confirmed_tokens: number;
  estimated_tokens: number;
  reserved_tokens: number;
  total_consumed: number;
  remaining_tokens: number;
  percent_used: number;
  mode: 'NORMAL' | 'EFFICIENT' | 'CONSERVATION' | 'CEILING_REACHED';
  provider_breakdown: {
    qwen: number;
    gemini: number;
    other: number;
  };
  agent_breakdown: Array<{ agent_id: string; tokens: number }>;
  deferred_queue_count: number;
  next_reset_iso: string;
  seconds_until_reset: number;
  countdown_display: string;
  alerts: string[];
}

export const TokenBudgetWidget: React.FC = () => {
  const [budget, setBudget] = useState<BudgetStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchBudget = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/budget/status');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: BudgetStatus = await res.json();
      setBudget(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load token budget:', err);
      setError('Gagal memuat status kuota AI.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBudget();
    const interval = setInterval(fetchBudget, 15000);
    return () => clearInterval(interval);
  }, []);

  if (!budget && loading) {
    return (
      <div className="bg-white rounded-2xl p-5 border border-purple-100 shadow-soft animate-pulse flex items-center justify-center h-48">
        <div className="text-xs font-semibold text-purple-600 flex items-center gap-2">
          <RefreshCw className="w-4 h-4 animate-spin" />
          Memuat Shared AI Token Budget Manager (Qwen + Gemini)...
        </div>
      </div>
    );
  }

  const modeBadge = (mode: BudgetStatus['mode']) => {
    switch (mode) {
      case 'NORMAL':
        return {
          bg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
          dot: 'bg-emerald-500',
          label: 'Mode 1: Normal (Inference Penuh)',
          desc: 'Semua agen menggunakan model reasoning terbaik tanpa kompresi konteks.'
        };
      case 'EFFICIENT':
        return {
          bg: 'bg-amber-50 text-amber-700 border-amber-200',
          dot: 'bg-amber-500',
          label: 'Mode 2: Efficient (>80% Kuota)',
          desc: 'Ringkasan otomatis riwayat sesi, batas output 400 token, background batching.'
        };
      case 'CONSERVATION':
        return {
          bg: 'bg-orange-50 text-orange-700 border-orange-200',
          dot: 'bg-orange-500',
          label: 'Mode 3: Conservation (>90% Kuota)',
          desc: 'Tugas non-kritis ditunda, fallback ke model hemat Gemini Flash, strict token gating.'
        };
      case 'CEILING_REACHED':
        return {
          bg: 'bg-rose-50 text-rose-700 border-rose-200',
          dot: 'bg-rose-500',
          label: 'Mode 4: Ceiling Reached (100% Batas Harian)',
          desc: 'Inference mandek otomatis hingga reset pukul 00:00 WIB. Nol boncos terjamin!'
        };
      default:
        return {
          bg: 'bg-slate-50 text-slate-700 border-slate-200',
          dot: 'bg-slate-500',
          label: mode,
          desc: ''
        };
    }
  };

  const badge = modeBadge(budget?.mode || 'NORMAL');
  const percent = Math.min(100, Math.max(0, budget?.percent_used || 0));
  const limitFormatted = ((budget?.daily_limit || 2000000) / 1000000).toFixed(1) + 'M';
  const consumedFormatted = (budget?.total_consumed || 0).toLocaleString();
  const remainingFormatted = (budget?.remaining_tokens || 2000000).toLocaleString();
  const qwenTokens = budget?.provider_breakdown?.qwen || 0;
  const geminiTokens = budget?.provider_breakdown?.gemini || 0;

  return (
    <div className="bg-white rounded-2xl p-5 border border-purple-100 shadow-soft space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-purple-600 text-white flex items-center justify-center shadow-md shadow-purple-500/20">
            <Gauge className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                Shared AI Token Budget Manager (Qwen + Gemini)
              </h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-purple-50 text-purple-700 border border-purple-200">
                WIB Boundary
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Batas gabungan 2.000.000 token/hari • Reset setiap tengah malam 00:00 Asia/Jakarta
            </p>
          </div>
        </div>

        {/* Action / Refresh & Mode */}
        <div className="flex items-center gap-2.5">
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-semibold border ${badge.bg}`}>
            <span className={`w-2 h-2 rounded-full ${badge.dot} animate-pulse`}></span>
            <span>{badge.label}</span>
          </div>

          <button
            onClick={fetchBudget}
            disabled={loading}
            className="p-1.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600 transition-colors"
            title="Refresh Token Budget"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Main Progress Gauge Bar */}
      <div className="space-y-2">
        <div className="flex justify-between items-end text-xs">
          <div>
            <span className="text-lg font-bold text-slate-900">{consumedFormatted}</span>
            <span className="text-slate-500 font-medium"> / {limitFormatted} Tokens Terpakai</span>
          </div>
          <div className="text-right">
            <span className="text-xs font-bold text-purple-700">{percent.toFixed(1)}%</span>
            <span className="text-slate-400 text-[11px] block">Sisa: {remainingFormatted}</span>
          </div>
        </div>

        {/* Multi-segmented Progress Bar */}
        <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden flex relative">
          <div 
            className={`h-full transition-all duration-500 ${
              percent >= 90 ? 'bg-rose-500' : percent >= 80 ? 'bg-amber-500' : 'bg-purple-600'
            }`}
            style={{ width: `${percent}%` }}
          />
          {/* Soft limit marker 80% */}
          <div 
            className="absolute top-0 bottom-0 w-0.5 bg-amber-400/80" 
            style={{ left: '80%' }}
            title="Soft Limit 80% (Mode Efficient)"
          />
          {/* Conservation marker 90% */}
          <div 
            className="absolute top-0 bottom-0 w-0.5 bg-rose-400/80" 
            style={{ left: '90%' }}
            title="Conservation Limit 90% (Mode Conservation)"
          />
        </div>
      </div>

      {/* Grid Details: Providers, Reset Countdown, & Controls */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
        {/* Provider Breakdown */}
        <div className="bg-slate-50 rounded-xl p-3 border border-slate-100 space-y-1.5">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-600">
            <div className="flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-purple-600" />
              <span>Breakdown Provider AI</span>
            </div>
            <span className="text-[10px] text-slate-400">$0.00 Spend</span>
          </div>
          <div className="text-xs space-y-1">
            <div className="flex justify-between items-center">
              <span className="text-slate-600">Qwen 3.8 Max (Brain Utama):</span>
              <span className="font-bold text-slate-900">{qwenTokens.toLocaleString()} tkn</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-600">Gemini 2.5 Flash (Support):</span>
              <span className="font-bold text-slate-900">{geminiTokens.toLocaleString()} tkn</span>
            </div>
          </div>
        </div>

        {/* Midnight Reset Countdown */}
        <div className="bg-slate-50 rounded-xl p-3 border border-slate-100 space-y-1.5">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-600">
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-amber-600" />
              <span>Reset Harian Asia/Jakarta</span>
            </div>
            <span className="text-[10px] text-emerald-600 font-bold">WIB</span>
          </div>
          <div className="flex items-baseline justify-between pt-0.5">
            <div>
              <span className="text-lg font-bold text-slate-900">{budget?.countdown_display || '24h 00m'}</span>
              <span className="text-[11px] text-slate-400 ml-1">menuju reset</span>
            </div>
            <span className="text-[11px] text-slate-500 font-medium">00:00 WIB</span>
          </div>
        </div>

        {/* Policy & Safety Status */}
        <div className="bg-slate-50 rounded-xl p-3 border border-slate-100 space-y-1.5">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-600">
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              <span>Pencegahan Over-Limit</span>
            </div>
            <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100/60 px-1.5 py-0.5 rounded">
              AKTIF
            </span>
          </div>
          <p className="text-[11px] text-slate-500 leading-tight">
            Safety reserve: 50.000 token untuk panggilan darurat CEO. Antrean tertunda: {budget?.deferred_queue_count || 0} tugas.
          </p>
        </div>
      </div>
    </div>
  );
};
