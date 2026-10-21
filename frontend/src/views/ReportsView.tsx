import React, { useState, useEffect } from 'react';
import { FileText, Calendar, CheckCircle2, TrendingUp, AlertCircle, RefreshCw } from 'lucide-react';

interface ReportItem {
  id: string;
  report_type: string;
  title: string;
  author_agent: string;
  content: string;
  metrics?: Record<string, any>;
  recommendations?: string[];
  created_at: string;
}

export const ReportsView: React.FC = () => {
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [selectedReport, setSelectedReport] = useState<ReportItem | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchReports = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/reports');
      const data = await res.json();
      if (Array.isArray(data)) {
        setReports(data);
        if (data.length > 0 && !selectedReport) {
          setSelectedReport(data[0]);
        }
      }
    } catch (err) {
      console.error('Failed to load reports:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-purple-700 via-indigo-700 to-purple-900 rounded-3xl p-6 text-white shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider bg-white/20 px-2.5 py-0.5 rounded-full inline-block mb-1.5">
            Operational Intelligence
          </span>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <FileText className="w-5 h-5 text-purple-300" />
            Laporan Operasional & Evaluasi Kinerja
          </h2>
          <p className="text-xs text-purple-100 mt-1 max-w-xl">
            Laporan harian yang diserahkan oleh PIC Divisi (Diana Prince), Bendahara (Marcus Drake), dan Executive Manager (Alex Vance) langsung kepada CEO Gentha.
          </p>
        </div>

        <button
          onClick={fetchReports}
          disabled={isLoading}
          className="flex items-center gap-2 px-4 py-2.5 bg-white text-purple-700 hover:bg-purple-50 rounded-2xl text-xs font-bold shadow-md transition-all active:scale-95 disabled:opacity-50 self-start md:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Reports</span>
        </button>
      </div>

      {/* Grid: Reports List & Content Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Reports Index */}
        <div className="lg:col-span-1 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">Daftar Dokumen ({reports.length})</h3>
            <span className="text-xs text-purple-600 font-semibold">Terkirim ke Telegram</span>
          </div>

          <div className="space-y-2.5 max-h-[600px] overflow-y-auto pr-1">
            {reports.map((r) => {
              const isSelected = selectedReport?.id === r.id;
              return (
                <div
                  key={r.id}
                  onClick={() => setSelectedReport(r)}
                  className={`p-4 rounded-3xl border transition-all cursor-pointer ${
                    isSelected 
                      ? 'bg-purple-600 text-white border-purple-600 shadow-md shadow-purple-500/25' 
                      : 'bg-white text-slate-800 border-purple-50 hover:border-purple-200 shadow-soft'
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px] mb-1.5 opacity-80">
                    <span className="font-mono font-bold">{r.id}</span>
                    <span>{new Date(r.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' })}</span>
                  </div>
                  <h4 className="text-xs font-bold truncate mb-1">{r.title}</h4>
                  <p className={`text-[11px] line-clamp-2 ${isSelected ? 'text-purple-100' : 'text-slate-400'}`}>
                    Penulis: {r.author_agent}
                  </p>
                  <div className="mt-2.5">
                    <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                      isSelected ? 'bg-white/20 text-white' : 'bg-purple-50 text-purple-700'
                    }`}>
                      {r.report_type}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Report Content View */}
        <div className="lg:col-span-2">
          {selectedReport ? (
            <div className="bg-white rounded-3xl p-6 border border-purple-100 shadow-soft space-y-5">
              <div className="flex items-center justify-between border-b border-purple-50 pb-4">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider bg-purple-100 text-purple-700 px-2.5 py-0.5 rounded-full inline-block mb-1">
                    {selectedReport.report_type}
                  </span>
                  <h3 className="text-base font-bold text-slate-900">{selectedReport.title}</h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Penulis: <strong className="text-slate-800">{selectedReport.author_agent}</strong> • Diserahkan: {new Date(selectedReport.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="font-mono text-xs bg-slate-50 px-3 py-1 rounded-xl text-slate-600 border border-slate-100">
                  {selectedReport.id}
                </div>
              </div>

              {/* Metrics cards if available */}
              {selectedReport.metrics && Object.keys(selectedReport.metrics).length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {Object.entries(selectedReport.metrics).map(([key, val]) => (
                    <div key={key} className="bg-purple-50/50 p-3 rounded-2xl border border-purple-100">
                      <span className="text-[10px] uppercase font-bold text-purple-600 tracking-wider block">
                        {key.replace('_', ' ')}
                      </span>
                      <span className="text-base font-bold text-slate-900 mt-0.5 block">
                        {typeof val === 'number' ? val.toLocaleString() : String(val)}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* Report Body */}
              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wide mb-2">
                  Isi Laporan Operasional
                </h4>
                <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100 text-xs text-slate-800 font-sans whitespace-pre-wrap leading-relaxed max-h-72 overflow-y-auto">
                  {selectedReport.content}
                </div>
              </div>

              {/* Recommendations */}
              {selectedReport.recommendations && selectedReport.recommendations.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                    <TrendingUp className="w-4 h-4 text-purple-600" />
                    Rekomendasi Tindakan Strategis
                  </h4>
                  <div className="space-y-1.5">
                    {selectedReport.recommendations.map((rec, idx) => (
                      <div key={idx} className="flex items-center gap-2 p-2.5 rounded-xl bg-purple-50/70 border border-purple-100 text-xs text-purple-950">
                        <CheckCircle2 className="w-4 h-4 text-purple-600 flex-shrink-0" />
                        <span>{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-3xl p-12 border border-purple-50 text-center shadow-soft text-slate-400">
              Pilih laporan dari panel sebelah kiri.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
