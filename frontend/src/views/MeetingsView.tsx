import React, { useState, useEffect } from 'react';
import { Users, Calendar, CheckSquare, Plus, FileText, Send, Sparkles } from 'lucide-react';

interface MeetingItem {
  id: string;
  title: string;
  meeting_type: string;
  agenda: string;
  participants: string[];
  discussion?: string;
  action_items?: string[];
  created_at: string;
}

export const MeetingsView: React.FC = () => {
  const [meetings, setMeetings] = useState<MeetingItem[]>([]);
  const [selectedMeeting, setSelectedMeeting] = useState<MeetingItem | null>(null);
  const [isStandupLoading, setIsStandupLoading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const fetchMeetings = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/meetings');
      const data = await res.json();
      if (Array.isArray(data)) {
        setMeetings(data);
        if (data.length > 0 && !selectedMeeting) {
          setSelectedMeeting(data[0]);
        }
      }
    } catch (err) {
      console.error('Failed to load meetings:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMeetings();
  }, []);

  const handleTriggerStandup = async () => {
    setIsStandupLoading(true);
    try {
      const res = await fetch('/api/standup', { method: 'POST' });
      const data = await res.json();
      await fetchMeetings();
      alert('Rapat Harian Sore Berhasil Diselenggarakan!\nNotulensi tersimpan dan terkirim ke CEO.');
    } catch (err) {
      alert('Gagal menyelenggarakan rapat: ' + err);
    } finally {
      setIsStandupLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-purple-700 via-indigo-700 to-purple-900 rounded-3xl p-6 text-white shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider bg-white/20 px-2.5 py-0.5 rounded-full inline-block mb-1.5">
            Internal Governance & Sync
          </span>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Users className="w-5 h-5 text-purple-300" />
            Rapat & Evaluasi Operasional
          </h2>
          <p className="text-xs text-purple-100 mt-1 max-w-xl">
            Pusat dokumentasi standup harian, rapat strategi divisi, notulensi otomatis, dan daftar tindak lanjut (action items).
          </p>
        </div>

        <button
          onClick={handleTriggerStandup}
          disabled={isStandupLoading}
          className="flex items-center gap-2 px-4 py-2.5 bg-white text-purple-700 hover:bg-purple-50 rounded-2xl text-xs font-bold shadow-md transition-all active:scale-95 disabled:opacity-50 self-start md:self-auto"
        >
          <Sparkles className={`w-4 h-4 ${isStandupLoading ? 'animate-spin' : ''}`} />
          <span>{isStandupLoading ? 'Rapat Berlangsung...' : 'Jalankan Rapat Sore Sekarang'}</span>
        </button>
      </div>

      {/* Main Grid: Meeting List & Detail Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Meeting List */}
        <div className="lg:col-span-1 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">Arsip Rapat ({meetings.length})</h3>
            <span className="text-xs text-purple-600 font-semibold">Tersimpan di SQLite</span>
          </div>

          <div className="space-y-2.5 max-h-[600px] overflow-y-auto pr-1">
            {meetings.map((m) => {
              const isSelected = selectedMeeting?.id === m.id;
              return (
                <div
                  key={m.id}
                  onClick={() => setSelectedMeeting(m)}
                  className={`p-4 rounded-3xl border transition-all cursor-pointer ${
                    isSelected 
                      ? 'bg-purple-600 text-white border-purple-600 shadow-md shadow-purple-500/25' 
                      : 'bg-white text-slate-800 border-purple-50 hover:border-purple-200 shadow-soft'
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px] mb-1.5 opacity-80">
                    <span className="font-mono font-bold">{m.id}</span>
                    <span>{new Date(m.created_at).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                  <h4 className="text-xs font-bold truncate mb-1">{m.title}</h4>
                  <p className={`text-[11px] line-clamp-2 ${isSelected ? 'text-purple-100' : 'text-slate-400'}`}>
                    {m.agenda}
                  </p>
                  <div className="mt-2.5 flex items-center gap-1.5 flex-wrap">
                    <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold ${
                      isSelected ? 'bg-white/20 text-white' : 'bg-purple-50 text-purple-700'
                    }`}>
                      {m.participants.length} Peserta
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Detail View */}
        <div className="lg:col-span-2">
          {selectedMeeting ? (
            <div className="bg-white rounded-3xl p-6 border border-purple-100 shadow-soft space-y-5">
              <div className="flex items-center justify-between border-b border-purple-50 pb-4">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider bg-purple-100 text-purple-700 px-2.5 py-0.5 rounded-full inline-block mb-1">
                    {selectedMeeting.meeting_type}
                  </span>
                  <h3 className="text-base font-bold text-slate-900">{selectedMeeting.title}</h3>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">ID: {selectedMeeting.id}</p>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-500 font-medium block">Waktu Pertemuan</span>
                  <span className="text-xs font-bold text-purple-700">
                    {new Date(selectedMeeting.created_at).toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Agenda */}
              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wide mb-1.5 flex items-center gap-1.5">
                  <FileText className="w-4 h-4 text-purple-600" />
                  Agenda Pembahasan
                </h4>
                <div className="p-3 bg-purple-50/50 rounded-2xl border border-purple-100 text-xs text-slate-800">
                  {selectedMeeting.agenda}
                </div>
              </div>

              {/* Participants */}
              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wide mb-1.5 flex items-center gap-1.5">
                  <Users className="w-4 h-4 text-purple-600" />
                  Daftar Hadir & Peserta
                </h4>
                <div className="flex flex-wrap gap-2">
                  {selectedMeeting.participants.map((p, idx) => (
                    <span key={idx} className="px-3 py-1 bg-slate-100 text-slate-700 text-xs font-semibold rounded-xl border border-slate-200">
                      {p}
                    </span>
                  ))}
                </div>
              </div>

              {/* Discussion & Transcripts */}
              {selectedMeeting.discussion && (
                <div>
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wide mb-1.5">
                    Notulensi & Transkrip Rapat (Sophia Chen)
                  </h4>
                  <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100 text-xs text-slate-700 font-mono whitespace-pre-wrap max-h-56 overflow-y-auto leading-relaxed">
                    {selectedMeeting.discussion}
                  </div>
                </div>
              )}

              {/* Action Items */}
              {selectedMeeting.action_items && selectedMeeting.action_items.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                    <CheckSquare className="w-4 h-4 text-emerald-600" />
                    Tindak Lanjut (Action Items)
                  </h4>
                  <div className="space-y-1.5">
                    {selectedMeeting.action_items.map((item, idx) => (
                      <div key={idx} className="flex items-center gap-2 p-2.5 rounded-xl bg-emerald-50 border border-emerald-100 text-xs text-emerald-900">
                        <span className="w-5 h-5 rounded-lg bg-emerald-200 text-emerald-800 font-bold flex items-center justify-center text-[10px]">
                          {idx + 1}
                        </span>
                        <span className="font-medium">{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-3xl p-12 border border-purple-50 text-center shadow-soft text-slate-400">
              Pilih rapat dari daftar di sebelah kiri untuk melihat notulensi dan action items.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
