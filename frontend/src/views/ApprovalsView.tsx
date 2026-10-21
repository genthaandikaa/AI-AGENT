import React, { useState, useEffect } from 'react';
import { ShieldAlert, CheckCircle2, XCircle, Clock, AlertTriangle, ShieldCheck, RefreshCw } from 'lucide-react';

interface ApprovalItem {
  id: string;
  requester_agent: string;
  category: string;
  title: string;
  description: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  impact_summary: string;
  status: 'pending' | 'approved' | 'rejected';
  ceo_notes?: string;
  created_at: string;
}

export const ApprovalsView: React.FC = () => {
  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchApprovals = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/approvals');
      const data = await res.json();
      if (Array.isArray(data)) {
        setApprovals(data);
      }
    } catch (err) {
      console.error('Failed to fetch approvals:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, []);

  const handleAction = async (id: string, action: 'approved' | 'rejected') => {
    setActionLoading(id);
    try {
      const res = await fetch(`/api/approvals/${id}/act`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, ceo_notes: `Processed directly by CEO via Dashboard.` })
      });
      if (res.ok) {
        await fetchApprovals();
      }
    } catch (err) {
      console.error('Action error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const pendingList = approvals.filter(a => a.status === 'pending');
  const resolvedList = approvals.filter(a => a.status !== 'pending');

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'critical':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-700 border border-rose-200">Critical Risk</span>;
      case 'high':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-700 border border-amber-200">High Risk</span>;
      case 'medium':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-700 border border-purple-200">Medium</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">Low</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-purple-700 via-indigo-700 to-purple-900 rounded-3xl p-6 text-white shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider bg-white/20 px-2.5 py-0.5 rounded-full inline-block mb-1.5">
            CEO Governance Gate
          </span>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            Persetujuan & Kebijakan Operasional
          </h2>
          <p className="text-xs text-purple-100 mt-1 max-w-xl">
            Tindakan berisiko tinggi, pengeluaran finansial, atau perubahan arsitektur membutuhkan otorisasi eksplisit CEO sebelum agen AI mengeksekusinya.
          </p>
        </div>

        <button
          onClick={fetchApprovals}
          disabled={isLoading}
          className="flex items-center gap-2 px-4 py-2.5 bg-white text-purple-700 hover:bg-purple-50 rounded-2xl text-xs font-bold shadow-md transition-all active:scale-95 disabled:opacity-50 self-start md:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* Pending Approvals */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-purple-600" />
            Menunggu Keputusan CEO ({pendingList.length})
          </h3>
          <span className="text-xs text-slate-400">Otorisasi langsung via API backend</span>
        </div>

        {pendingList.length === 0 ? (
          <div className="bg-white rounded-3xl p-8 border border-purple-50 text-center shadow-soft">
            <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
            <h4 className="text-sm font-bold text-slate-800">Semua Antrean Persetujuan Bersih</h4>
            <p className="text-xs text-slate-400 mt-1">Tidak ada proposal tertunda dari agen AI saat ini.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {pendingList.map((item) => (
              <div 
                key={item.id}
                className="bg-white rounded-3xl p-6 border border-purple-100 shadow-soft hover:shadow-lg transition-all flex flex-col md:flex-row md:items-center justify-between gap-5"
              >
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <span className="font-mono text-xs font-bold text-purple-700 bg-purple-50 px-2.5 py-0.5 rounded-lg border border-purple-100">
                      {item.id}
                    </span>
                    {getRiskBadge(item.risk_level)}
                    <span className="text-xs font-semibold text-slate-500">
                      Diajukan oleh: <strong className="text-slate-800">{item.requester_agent}</strong>
                    </span>
                    <span className="text-[10px] text-slate-400">
                      {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>

                  <h4 className="text-base font-bold text-slate-900">{item.title}</h4>
                  <p className="text-xs text-slate-600 leading-relaxed">{item.description}</p>
                  
                  {item.impact_summary && (
                    <div className="bg-slate-50 p-3 rounded-2xl border border-slate-100 text-xs text-slate-700 flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                      <span><strong>Dampak Operasional:</strong> {item.impact_summary}</span>
                    </div>
                  )}
                </div>

                <div className="flex md:flex-col items-center gap-2.5 flex-shrink-0">
                  <button
                    onClick={() => handleAction(item.id, 'approved')}
                    disabled={actionLoading === item.id}
                    className="w-full md:w-32 flex items-center justify-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-2xl text-xs font-bold shadow-md shadow-emerald-500/20 transition-all active:scale-95 disabled:opacity-50"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Setujui</span>
                  </button>

                  <button
                    onClick={() => handleAction(item.id, 'rejected')}
                    disabled={actionLoading === item.id}
                    className="w-full md:w-32 flex items-center justify-center gap-2 px-4 py-2.5 bg-rose-50 hover:bg-rose-100 text-rose-700 rounded-2xl text-xs font-bold border border-rose-200 transition-all active:scale-95 disabled:opacity-50"
                  >
                    <XCircle className="w-4 h-4" />
                    <span>Tolak</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Historical Approvals */}
      <div className="space-y-4 pt-4">
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <Clock className="w-4 h-4 text-slate-400" />
          Riwayat Keputusan Sebelumnya ({resolvedList.length})
        </h3>

        <div className="bg-white rounded-3xl border border-purple-50 shadow-soft overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-purple-50/50 text-slate-500 font-bold border-b border-purple-100">
                <tr>
                  <th className="p-4">ID</th>
                  <th className="p-4">Judul Permohonan</th>
                  <th className="p-4">Agen</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Catatan CEO</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-purple-50">
                {resolvedList.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/50">
                    <td className="p-4 font-mono font-bold text-slate-700">{item.id}</td>
                    <td className="p-4 font-semibold text-slate-900">{item.title}</td>
                    <td className="p-4 text-slate-600">{item.requester_agent}</td>
                    <td className="p-4">
                      {item.status === 'approved' ? (
                        <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                          Disetujui
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800">
                          Ditolak
                        </span>
                      )}
                    </td>
                    <td className="p-4 text-slate-500">{item.ceo_notes || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
