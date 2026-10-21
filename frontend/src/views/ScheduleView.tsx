import React, { useState } from 'react';
import { Calendar, Clock, Zap, CheckCircle2 } from 'lucide-react';

interface ScheduleViewProps {
  schedules?: any[];
  onRefresh?: () => void;
}

export const ScheduleView: React.FC<ScheduleViewProps> = ({ schedules: initialSchedules, onRefresh: externalRefresh }) => {
  const [internalSchedules, setInternalSchedules] = useState<any[]>([]);
  const [isHeartbeatRunning, setIsHeartbeatRunning] = useState(false);

  const fetchInternalSchedules = async () => {
    try {
      const res = await fetch('/api/schedules');
      const data = await res.json();
      if (Array.isArray(data)) setInternalSchedules(data);
    } catch (e) {
      console.error(e);
    }
  };

  React.useEffect(() => {
    if (!initialSchedules) {
      fetchInternalSchedules();
    }
  }, [initialSchedules]);

  const schedules = initialSchedules || internalSchedules;

  const refreshAll = () => {
    if (externalRefresh) externalRefresh();
    fetchInternalSchedules();
  };

  const handleTriggerHeartbeat = async () => {
    setIsHeartbeatRunning(true);
    try {
      const res = await fetch('/api/schedules/heartbeat', { method: 'POST' });
      const data = await res.json();
      alert(`Operational Heartbeat Selesai! Due items dieksekusi: ${data.due_count}`);
      refreshAll();
    } catch (err) {
      alert('Heartbeat error: ' + err);
    } finally {
      setIsHeartbeatRunning(false);
    }
  };

  const handleToggleSchedule = async (id: string, currentEnabled: boolean) => {
    try {
      await fetch(`/api/schedules/${id}/toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !currentEnabled })
      });
      refreshAll();
    } catch (err) {
      alert('Toggle error: ' + err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-3xl p-5 border border-purple-100 shadow-soft flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Calendar className="w-4 h-4 text-purple-600" />
            Jadwal Operasional & Eksekusi Terjadwal (Crons)
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Sistem penjadwalan persisten SQLite dengan eksekusi otomatis standup sore dan watchdog.
          </p>
        </div>

        <button
          onClick={handleTriggerHeartbeat}
          disabled={isHeartbeatRunning}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-2xl text-xs font-semibold shadow-md transition-all active:scale-95 disabled:opacity-50"
        >
          <Zap className={`w-3.5 h-3.5 ${isHeartbeatRunning ? 'animate-spin' : ''}`} />
          <span>{isHeartbeatRunning ? 'Memeriksa...' : 'Trigger Heartbeat Manual'}</span>
        </button>
      </div>

      <div className="bg-white rounded-3xl border border-purple-100 shadow-soft overflow-hidden">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-purple-50/50 border-b border-purple-100 text-purple-900 uppercase tracking-wider text-[10px]">
              <th className="p-4">Nama Jadwal</th>
              <th className="p-4">Interval / Cron</th>
              <th className="p-4">Penanggung Jawab</th>
              <th className="p-4">Aksi Operasional</th>
              <th className="p-4">Next Run</th>
              <th className="p-4">Status</th>
              <th className="p-4">Kontrol</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-purple-50">
            {schedules.map((s) => (
              <tr key={s.id} className="hover:bg-purple-50/30 transition-colors">
                <td className="p-4 font-bold text-slate-900">{s.title}</td>
                <td className="p-4 font-mono text-[11px] text-purple-700 font-semibold">{s.cron_expr || s.interval_type}</td>
                <td className="p-4 font-medium text-slate-700">👤 {s.target_role}</td>
                <td className="p-4 font-mono text-[11px] text-slate-500">{s.action}</td>
                <td className="p-4 text-slate-600">{new Date(s.next_run).toLocaleString('id-ID', { hour: '2-digit', minute: '2-digit', day: 'numeric', month: 'short' })}</td>
                <td className="p-4">
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                    s.enabled ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-100 text-slate-500'
                  }`}>
                    {s.enabled ? 'AKTIF' : 'PAUSED'}
                  </span>
                </td>
                <td className="p-4">
                  <button
                    onClick={() => handleToggleSchedule(s.id, Boolean(s.enabled))}
                    className="px-3 py-1 bg-slate-100 hover:bg-purple-100 text-slate-700 hover:text-purple-700 font-semibold text-[11px] rounded-xl transition-colors"
                  >
                    {s.enabled ? 'Pause' : 'Resume'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
