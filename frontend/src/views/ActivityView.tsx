import React, { useState } from 'react';
import { Activity, ShieldCheck, AlertTriangle, AlertCircle, Info, Search, RefreshCw } from 'lucide-react';
import { ActivityItem } from '../types';

interface ActivityViewProps {
  activities: ActivityItem[];
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const ActivityView: React.FC<ActivityViewProps> = ({ activities, onRefresh, isRefreshing }) => {
  const [filterLevel, setFilterLevel] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filtered = activities.filter((act) => {
    const matchesLevel = filterLevel === 'all' || act.level.toUpperCase() === filterLevel.toUpperCase();
    const query = searchQuery.toLowerCase();
    const matchesQuery = 
      act.actor.toLowerCase().includes(query) ||
      act.action.toLowerCase().includes(query) ||
      (act.details && act.details.toLowerCase().includes(query));
    return matchesLevel && matchesQuery;
  });

  const getLevelBadge = (level: string) => {
    switch (level.toUpperCase()) {
      case 'ERROR':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-700 flex items-center gap-1"><AlertCircle className="w-3 h-3" /> Error</span>;
      case 'WARN':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-700 flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> Warning</span>;
      case 'GOVERNANCE':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-100 text-indigo-700 flex items-center gap-1"><ShieldCheck className="w-3 h-3" /> Governance</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-700 flex items-center gap-1"><Info className="w-3 h-3" /> Info</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-purple-700 via-indigo-700 to-purple-900 rounded-3xl p-6 text-white shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider bg-white/20 px-2.5 py-0.5 rounded-full inline-block mb-1.5">
            Audit Trail & Event Stream
          </span>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Activity className="w-5 h-5 text-purple-300" />
            Riwayat Aktivitas & Perubahan Status
          </h2>
          <p className="text-xs text-purple-100 mt-1 max-w-xl">
            Catatan kronologis tidak terhapus (immutable log) dari seluruh tindakan agen AI, eksekusi tools, keputusan CEO, dan status pipeline.
          </p>
        </div>

        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-4 py-2.5 bg-white text-purple-700 hover:bg-purple-50 rounded-2xl text-xs font-bold shadow-md transition-all active:scale-95 disabled:opacity-50 self-start md:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>Refresh Logs</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white rounded-3xl p-4 border border-purple-100 shadow-soft flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto">
          {['all', 'info', 'warn', 'error', 'governance'].map((lvl) => (
            <button
              key={lvl}
              onClick={() => setFilterLevel(lvl)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold capitalize transition-all ${
                filterLevel === lvl
                  ? 'bg-purple-600 text-white shadow-sm'
                  : 'bg-slate-50 text-slate-600 hover:bg-purple-50 hover:text-purple-700'
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Cari aktor atau aktivitas..."
            className="w-full bg-slate-50 border border-slate-200 rounded-2xl pl-9 pr-4 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-purple-500"
          />
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-3xl border border-purple-50 shadow-soft overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-purple-50/50 text-slate-500 font-bold border-b border-purple-100">
              <tr>
                <th className="p-4">Waktu</th>
                <th className="p-4">Level</th>
                <th className="p-4">Aktor / NPC</th>
                <th className="p-4">Tindakan</th>
                <th className="p-4">Detail</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-purple-50">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-slate-400">
                    Tidak ada log aktivitas yang cocok dengan filter.
                  </td>
                </tr>
              ) : (
                filtered.map((item, idx) => (
                  <tr key={idx} className="hover:bg-purple-50/30 transition-colors">
                    <td className="p-4 text-slate-400 font-mono whitespace-nowrap">
                      {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </td>
                    <td className="p-4 whitespace-nowrap">
                      {getLevelBadge(item.level)}
                    </td>
                    <td className="p-4 font-bold text-slate-900 whitespace-nowrap">
                      {item.actor}
                    </td>
                    <td className="p-4 font-semibold text-slate-700">
                      {item.action}
                    </td>
                    <td className="p-4 text-slate-500 font-mono text-[11px] max-w-md truncate" title={item.details}>
                      {item.details || '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
