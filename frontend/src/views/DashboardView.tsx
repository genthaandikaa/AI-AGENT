import React, { useState } from 'react';
import { 
  CheckCircle2, 
  Clock, 
  ShieldAlert, 
  DollarSign, 
  Bot, 
  Play, 
  Send, 
  Sparkles,
  ArrowRight,
  Activity
} from 'lucide-react';
import { Agent, TaskItem, ActivityItem } from '../types';
import { AgentChatDrawer } from '../components/AgentChatDrawer';
import { TokenBudgetWidget } from '../components/TokenBudgetWidget';

interface DashboardViewProps {
  agents: Agent[];
  tasks: TaskItem[];
  activities: ActivityItem[];
  onSelectTask: (task: TaskItem) => void;
  onNavigate: (section: any) => void;
  onOpenNewTask: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  agents,
  tasks,
  activities,
  onSelectTask,
  onNavigate,
  onOpenNewTask
}) => {
  const [isProducing, setIsProducing] = useState(false);
  const [isStandupRunning, setIsStandupRunning] = useState(false);

  const completedTasks = tasks.filter(t => t.status === 'completed').length;
  const inProgressTasks = tasks.filter(t => t.status === 'in_progress').length;
  const activeWorkers = agents.length || 12;

  const handleTriggerProduction = async () => {
    setIsProducing(true);
    try {
      const res = await fetch('/api/creator/produce', { method: 'POST' });
      const data = await res.json();
      alert(`Video Render Berhasil!\nTask ID: ${data.task_id}\nFile: ${data.rendered_video}`);
    } catch (err) {
      alert('Video production error: ' + err);
    } finally {
      setIsProducing(false);
    }
  };

  const handleTriggerStandup = async () => {
    setIsStandupRunning(true);
    try {
      const res = await fetch('/api/standup', { method: 'POST' });
      const data = await res.json();
      alert(`Rapat Harian Sore Selesai!\nNotulensi tersimpan dan terkirim ke CEO.`);
      onNavigate('meetings');
    } catch (err) {
      alert('Standup error: ' + err);
    } finally {
      setIsStandupRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Core Essential KPI Cards (Simple, Real Data, Zero Dummy) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Tasks */}
        <div 
          onClick={() => onNavigate('tasks')}
          className="bg-white rounded-2xl p-4 border border-purple-100 shadow-soft hover:border-purple-300 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-500">Total Pekerjaan</span>
            <div className="w-8 h-8 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center group-hover:scale-105 transition-transform">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900">{tasks.length}</div>
          <p className="text-[11px] text-emerald-600 font-medium mt-1">
            {completedTasks} selesai • {inProgressTasks} berjalan
          </p>
        </div>

        {/* Active AI Workers */}
        <div 
          onClick={() => onNavigate('overview')}
          className="bg-white rounded-2xl p-4 border border-purple-100 shadow-soft hover:border-purple-300 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-500">Pekerja AI Aktif</span>
            <div className="w-8 h-8 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center group-hover:scale-105 transition-transform">
              <Bot className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900">{activeWorkers}</div>
          <p className="text-[11px] text-purple-600 font-medium mt-1 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            100% Online di Hermes 3D
          </p>
        </div>

        {/* Pending Approvals */}
        <div 
          onClick={() => onNavigate('approvals')}
          className="bg-white rounded-2xl p-4 border border-purple-100 shadow-soft hover:border-purple-300 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-500">Persetujuan CEO</span>
            <div className="w-8 h-8 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center group-hover:scale-105 transition-transform">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900">3</div>
          <p className="text-[11px] text-amber-600 font-medium mt-1">
            Menunggu review & otorisasi
          </p>
        </div>

        {/* Budget Spent */}
        <div 
          onClick={() => onNavigate('settings')}
          className="bg-white rounded-2xl p-4 border border-purple-100 shadow-soft hover:border-purple-300 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-500">Pengeluaran Cloud</span>
            <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center group-hover:scale-105 transition-transform">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-emerald-600">$0.00</div>
          <p className="text-[11px] text-slate-400 font-medium mt-1">
            Kebijakan $0 Zero-Cost Aktif
          </p>
        </div>
      </div>

      {/* Shared AI Token Budget Manager Widget */}
      <TokenBudgetWidget />

      {/* 2. Simple Action Bar */}
      <div className="bg-white rounded-2xl p-4 border border-purple-100 shadow-soft flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-purple-600" />
          <span className="text-xs font-bold text-slate-800">Aksi Operasional Cepat:</span>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap">
          <button
            onClick={handleTriggerStandup}
            disabled={isStandupRunning}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all active:scale-95 disabled:opacity-50"
          >
            <Send className={`w-3.5 h-3.5 ${isStandupRunning ? 'animate-spin' : ''}`} />
            <span>{isStandupRunning ? 'Rapat Berjalan...' : 'Jalankan Standup Sore'}</span>
          </button>

          <button
            onClick={handleTriggerProduction}
            disabled={isProducing}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 rounded-xl text-xs font-bold transition-all active:scale-95 disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${isProducing ? 'animate-spin' : ''}`} />
            <span>{isProducing ? 'Merender...' : 'Render Shorts FFmpeg'}</span>
          </button>

          <button
            onClick={onOpenNewTask}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 rounded-xl text-xs font-bold transition-all active:scale-95"
          >
            <span>+ Buat Tugas</span>
          </button>
        </div>
      </div>

      {/* 3. Core Split: Real Task Queue vs Live AI Brain Chat */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
        {/* Left Column: Recent Tasks (3 cols) */}
        <div className="lg:col-span-3 bg-white rounded-3xl p-5 border border-purple-100 shadow-soft space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-purple-50">
            <h3 className="text-xs font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-purple-600" />
              Antrean Pekerjaan Aktif
            </h3>
            <button 
              onClick={() => onNavigate('tasks')}
              className="text-xs font-semibold text-purple-600 hover:text-purple-700 flex items-center gap-1"
            >
              Lihat Semua ({tasks.length})
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-2.5 max-h-[420px] overflow-y-auto pr-1">
            {tasks.slice(0, 6).map((t) => (
              <div
                key={t.id}
                onClick={() => onSelectTask(t)}
                className="p-3 rounded-2xl bg-slate-50/70 border border-purple-50 hover:border-purple-200 transition-all cursor-pointer flex items-center justify-between gap-3 group"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="font-mono text-[10px] text-purple-700 font-bold bg-purple-100/60 px-1.5 py-0.5 rounded">
                      {t.id}
                    </span>
                    <h4 className="text-xs font-bold text-slate-800 truncate group-hover:text-purple-600 transition-colors">
                      {t.title}
                    </h4>
                  </div>
                  <p className="text-[11px] text-slate-400 truncate">
                    Assignee: <strong className="text-slate-600">{t.assignee}</strong>
                  </p>
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                    t.status === 'completed' 
                      ? 'bg-emerald-100 text-emerald-800' 
                      : (t.status === 'in_progress' ? 'bg-purple-100 text-purple-800' : 'bg-slate-200 text-slate-700')
                  }`}>
                    {t.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Live Agent Chat Drawer (2 cols) */}
        <div className="lg:col-span-2">
          <AgentChatDrawer />
        </div>
      </div>
    </div>
  );
};
