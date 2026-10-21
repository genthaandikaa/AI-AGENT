import React from 'react';
import { 
  Bot, 
  Activity, 
  Zap, 
  Workflow, 
  Search, 
  Bell, 
  Plus, 
  RefreshCw 
} from 'lucide-react';

interface TopHeaderProps {
  title: string;
  subtitle: string;
  onOpenNewTask: () => void;
  onRefresh: () => void;
  isRefreshing?: boolean;
}

export const TopHeader: React.FC<TopHeaderProps> = ({
  title,
  subtitle,
  onOpenNewTask,
  onRefresh,
  isRefreshing = false
}) => {
  return (
    <div className="space-y-3">
      {/* Top Feature Status Pills */}
      <div className="flex items-center gap-2.5 overflow-x-auto pb-0.5 scrollbar-none text-xs">
        <div className="flex items-center gap-1.5 px-3 py-1 bg-purple-600 text-white rounded-xl font-semibold shadow-sm shadow-purple-500/20 whitespace-nowrap">
          <Bot className="w-3.5 h-3.5" />
          <span>Intelligent NPCs</span>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1 bg-purple-50 text-purple-700 border border-purple-100 rounded-xl font-semibold whitespace-nowrap">
          <Activity className="w-3.5 h-3.5 text-purple-500" />
          <span>Real-time Operations</span>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1 bg-purple-50 text-purple-700 border border-purple-100 rounded-xl font-semibold whitespace-nowrap">
          <Zap className="w-3.5 h-3.5 text-amber-500" />
          <span>Smart Standup & Automation</span>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1 bg-purple-50 text-purple-700 border border-purple-100 rounded-xl font-semibold whitespace-nowrap">
          <Workflow className="w-3.5 h-3.5 text-emerald-500" />
          <span>Local Video Pipeline</span>
        </div>

        <div className="ml-auto flex items-center gap-2">
          <div className="flex items-center gap-1.5 text-[11px] text-purple-700 font-bold bg-purple-50 border border-purple-200 px-3 py-1 rounded-xl whitespace-nowrap">
            <Zap className="w-3 h-3 text-purple-600" />
            <span>2.0M TOKEN/DAY (WIB)</span>
          </div>

          <div className="flex items-center gap-2 text-[11px] text-emerald-700 font-bold bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-xl whitespace-nowrap">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>$0.00 ZERO-COST ENFORCED</span>
          </div>
        </div>
      </div>

      {/* Main Bar: Title + Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-0.5">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">{title}</h1>
          <p className="text-xs text-purple-700/70 font-medium">{subtitle}</p>
        </div>

        {/* Right Search and Actions */}
        <div className="flex items-center gap-2.5">
          {/* Search Bar */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input 
              type="text" 
              placeholder="Cari tugas, agen, notulen..." 
              className="pl-8 pr-3 py-1.5 bg-slate-50 border border-purple-100 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 shadow-sm w-44 sm:w-56 transition-all"
            />
          </div>

          {/* Refresh Button */}
          <button 
            onClick={onRefresh}
            title="Refresh Data"
            className="p-2 bg-white border border-purple-100 rounded-xl text-slate-600 hover:text-purple-600 hover:bg-purple-50 transition-all shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-purple-600' : ''}`} />
          </button>

          {/* Notification Bell */}
          <button className="relative p-2 bg-white border border-purple-100 rounded-xl text-slate-600 hover:text-purple-600 transition-all shadow-sm">
            <Bell className="w-3.5 h-3.5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full ring-2 ring-white"></span>
          </button>

          {/* New Task Button */}
          <button 
            onClick={onOpenNewTask}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-bold shadow-md shadow-purple-600/20 transition-all active:scale-95"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Tugas Baru</span>
          </button>
        </div>
      </div>
    </div>
  );
};
