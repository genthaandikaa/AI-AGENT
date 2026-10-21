import React, { useEffect, useState } from 'react';
import { Video, TrendingUp, Play, CheckCircle2, Send, Sparkles, Film, FileText, CheckCircle, Clock, ExternalLink, RefreshCw, Layers } from 'lucide-react';

interface LongFormProduction {
  id: string;
  topic_id: string;
  title: string;
  slug: string;
  stage: string;
  assignee: string;
  manifest_path: string;
  script_path: string;
  storyboard_path: string;
  ledger_path: string;
  output_video_path: string;
  preview_video_path: string;
  duration_seconds: number;
  resolution: string;
  file_size_bytes: number;
  qa_status: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

interface TopicItem {
  id: string;
  category: string;
  title: string;
  hook_question: string;
  total_score: number;
  scores: Record<string, number>;
  editorial_rationale: string;
  source_links: string[];
  status: string;
}

const STAGES = [
  { key: 'topic_research', label: '1. Riset Topik' },
  { key: 'fact_check', label: '2. Fact Check' },
  { key: 'script', label: '3. Naskah' },
  { key: 'storyboard', label: '4. Storyboard' },
  { key: 'visual_assets', label: '5. Visual 16:9' },
  { key: 'editing', label: '6. Audio Mix' },
  { key: 'render', label: '7. Render' },
  { key: 'qa', label: '8. QA Lab' },
  { key: 'ceo_review', label: '9. CEO Review' },
];

export const DivisionsView: React.FC = () => {
  const [isProducing, setIsProducing] = useState(false);
  const [isStandupRunning, setIsStandupRunning] = useState(false);
  const [standupResult, setStandupResult] = useState<any>(null);

  // YouTube Long-Form States
  const [longform, setLongform] = useState<LongFormProduction | null>(null);
  const [topics, setTopics] = useState<TopicItem[]>([]);
  const [selectedTopicId, setSelectedTopicId] = useState<string>('');
  const [isProducingLongform, setIsProducingLongform] = useState(false);

  const fetchLongformData = async () => {
    try {
      const [resStatus, resTopics] = await Promise.all([
        fetch('/api/longform/status'),
        fetch('/api/longform/topics')
      ]);
      const dataStatus = await resStatus.json();
      const dataTopics = await resTopics.json();

      if (dataStatus.latest) {
        setLongform(dataStatus.latest);
      }
      if (Array.isArray(dataTopics)) {
        setTopics(dataTopics);
        if (dataTopics.length > 0 && !selectedTopicId) {
          setSelectedTopicId(dataTopics[0].id);
        }
      }
    } catch (e) {
      console.error('Failed to load longform data:', e);
    }
  };

  useEffect(() => {
    fetchLongformData();
  }, []);

  const handleTriggerProduction = async () => {
    setIsProducing(true);
    try {
      const res = await fetch('/api/creator/produce', { method: 'POST' });
      const data = await res.json();
      alert(`Render Sukses!\nTask: ${data.task_id}\nVideo: ${data.output_path || data.rendered_video}`);
    } catch (err) {
      alert('Error: ' + err);
    } finally {
      setIsProducing(false);
    }
  };

  const handleTriggerStandup = async () => {
    setIsStandupRunning(true);
    try {
      const res = await fetch('/api/standup', { method: 'POST' });
      const data = await res.json();
      setStandupResult(data);
      alert('Standup selesai & notulensi tersimpan.');
    } catch (err) {
      alert('Error: ' + err);
    } finally {
      setIsStandupRunning(false);
    }
  };

  const handleTriggerLongform = async () => {
    setIsProducingLongform(true);
    try {
      const url = selectedTopicId ? `/api/longform/produce?topic_id=${selectedTopicId}` : '/api/longform/produce';
      const res = await fetch(url, { method: 'POST' });
      const data = await res.json();
      alert(`Produksi YouTube Long-Form Selesai!\nJudul: ${data.topic?.title}\nDurasi: ${data.duration_seconds}s (16:9 1080p)\nStatus: Ready for CEO Review`);
      await fetchLongformData();
    } catch (err) {
      alert('Error produksi longform: ' + err);
    } finally {
      setIsProducingLongform(false);
    }
  };

  const subDivisions = [
    {
      id: 'yt-long',
      title: 'YouTube Panjang (16:9)',
      lead: 'Raka Pratama (Editor Long-Form)',
      format: '1920x1080 Horizontal Explainer',
      status: longform ? `Stage: ${longform.stage}` : 'Pipeline Aktif',
      activeTask: longform ? `Produksi '${longform.title.slice(0, 32)}...'` : 'Riset naskah & kurasi topik sains'
    },
    {
      id: 'yt-shorts',
      title: 'YouTube Shorts (9:16)',
      lead: 'Leo Sparks (Editor FFmpeg)',
      format: '1080x1920 Vertikal',
      status: 'Pipeline Siap',
      activeTask: 'Render otomatis 60 FPS lokal'
    },
    {
      id: 'tiktok-viral',
      title: 'Konten TikTok Viral',
      lead: 'Maya Lin (Kreator 3s Hook)',
      format: 'Storytelling Ringkas',
      status: 'Review QA',
      activeTask: 'Validasi hook 3 detik pertama'
    },
    {
      id: 'tiktok-affiliate',
      title: 'TikTok Affiliate',
      lead: 'Victor Sterling (Cuan Hunter)',
      format: 'Showcase Produk & Keranjang Kuning',
      status: 'Tracking Komisi',
      activeTask: 'Analisis produk winning rate tinggi'
    }
  ];

  const currentStageIndex = longform ? STAGES.findIndex(s => s.key === longform.stage) : -1;

  return (
    <div className="space-y-6">
      {/* Action Header */}
      <div className="bg-white rounded-3xl p-6 border border-purple-100 shadow-soft flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider bg-purple-50 text-purple-700 px-2.5 py-0.5 rounded-full inline-block mb-1">
            Lead: Diana Prince (PIC Divisi) & Raka Pratama (Lead Long-Form)
          </span>
          <h2 className="text-lg font-bold text-slate-900">Divisi Konten Kreator & YouTube Long-Form</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Eksplorasi edukasi sains, sejarah, dan kurasi konten 16:9 mandiri dengan evaluasi standup harian.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleTriggerStandup}
            disabled={isStandupRunning}
            className="flex items-center gap-1.5 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all active:scale-95 disabled:opacity-50"
          >
            <Send className={`w-3.5 h-3.5 ${isStandupRunning ? 'animate-spin' : ''}`} />
            <span>{isStandupRunning ? 'Rapat...' : 'Standup Sore'}</span>
          </button>

          <button
            onClick={handleTriggerProduction}
            disabled={isProducing}
            className="flex items-center gap-1.5 px-4 py-2 bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 rounded-xl text-xs font-bold transition-all active:scale-95 disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${isProducing ? 'animate-spin' : ''}`} />
            <span>{isProducing ? 'Rendering...' : 'Render Shorts'}</span>
          </button>
        </div>
      </div>

      {/* Standup Result Snippet */}
      {standupResult && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-950 space-y-1.5">
          <div className="flex items-center justify-between font-bold text-emerald-800">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              Notulensi Standup Sore Berhasil Disimpan & Dikirim ke Telegram CEO
            </span>
            <span className="font-mono text-[10px] bg-emerald-100 px-2 py-0.5 rounded-full">
              {standupResult.standup_id}
            </span>
          </div>
          <p className="text-[11px] text-emerald-900">{standupResult.summary}</p>
        </div>
      )}

      {/* 4 Clean Sub-division Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {subDivisions.map((sub) => (
          <div key={sub.id} className="bg-white rounded-2xl p-4 border border-purple-100 shadow-soft space-y-2">
            <div className="flex items-start justify-between gap-2">
              <div>
                <h3 className="text-xs font-bold text-slate-900">{sub.title}</h3>
                <p className="text-[11px] text-purple-600 font-medium">{sub.lead}</p>
              </div>
              <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-purple-50 text-purple-700 border border-purple-100 shrink-0">
                {sub.status}
              </span>
            </div>

            <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100 space-y-1 text-[11px]">
              <div className="text-slate-500 text-[10px]">Format: <strong className="text-slate-800">{sub.format}</strong></div>
              <div className="text-slate-500 text-[10px]">Aktivitas: <strong className="text-slate-800">{sub.activeTask}</strong></div>
            </div>
          </div>
        ))}
      </div>

      {/* --- YOUTUBE LONG-FORM PRODUCTION STUDIO (16:9) --- */}
      <div className="bg-white rounded-3xl p-6 border border-purple-100 shadow-soft space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-5">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Film className="w-5 h-5 text-purple-600" />
              <h3 className="text-base font-bold text-slate-900">YouTube Long-Form Production Studio (16:9)</h3>
              <span className="bg-purple-100 text-purple-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                Horizontal 1080p
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Pipeline otonom: Riset topik → Fact Check → Naskah 8-Tahap → Visual 16:9 → Audio Mix → Render MP4 → CEO Approval.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={selectedTopicId}
              onChange={(e) => setSelectedTopicId(e.target.value)}
              className="text-xs border border-purple-200 bg-purple-50/50 rounded-xl px-3 py-2 text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-purple-400 max-w-[280px]"
            >
              {topics.map(t => (
                <option key={t.id} value={t.id}>
                  [{t.total_score} pts] {t.title}
                </option>
              ))}
            </select>

            <button
              onClick={handleTriggerLongform}
              disabled={isProducingLongform}
              className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-xl text-xs font-bold shadow-md transition-all active:scale-95 disabled:opacity-50 shrink-0"
            >
              <Play className={`w-3.5 h-3.5 ${isProducingLongform ? 'animate-spin' : ''}`} />
              <span>{isProducingLongform ? 'Memproduksi...' : 'Mulai Produksi (16:9)'}</span>
            </button>
          </div>
        </div>

        {/* 9-Stage Progress Stepper */}
        <div className="space-y-2">
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
            <span>Alur Produksi 9-Tahap Terverifikasi</span>
            <span className="text-purple-600 font-mono">
              {longform ? `Status Aktif: ${longform.stage.toUpperCase()}` : 'Siap Dijalankan'}
            </span>
          </div>

          <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-9 gap-1.5">
            {STAGES.map((st, idx) => {
              const isPast = currentStageIndex >= idx;
              const isCurrent = currentStageIndex === idx;
              return (
                <div
                  key={st.key}
                  className={`p-2 rounded-xl text-center border transition-all ${
                    isCurrent
                      ? 'bg-purple-600 text-white border-purple-600 font-bold shadow-sm'
                      : isPast
                        ? 'bg-purple-50 text-purple-700 border-purple-200 font-semibold'
                        : 'bg-slate-50 text-slate-400 border-slate-100'
                  }`}
                >
                  <div className="text-[10px] leading-tight">{st.label}</div>
                  <div className="text-[9px] mt-0.5 opacity-80">
                    {isCurrent ? 'Aktif' : isPast ? 'Selesai' : 'Antrean'}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Latest Render Inspection & Video Player */}
        {longform && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 pt-2">
            {/* Video Player */}
            <div className="lg:col-span-7 bg-slate-950 rounded-2xl p-2 flex flex-col justify-center items-center overflow-hidden border border-slate-800 shadow-inner">
              <div className="w-full aspect-video rounded-xl overflow-hidden bg-slate-900 relative flex items-center justify-center">
                <video
                  controls
                  className="w-full h-full object-contain"
                  src={`/api/longform/video/${longform.slug}`}
                  poster="/static/harmage-preview-banner.png"
                >
                  Browser Anda tidak mendukung tag video HTML5.
                </video>
              </div>
              <div className="w-full px-3 py-2 flex items-center justify-between text-[11px] text-slate-400">
                <span className="font-mono text-slate-300">Format: {longform.resolution} (16:9)</span>
                <span className="font-mono text-purple-400 font-bold">Durasi: {longform.duration_seconds}s</span>
              </div>
            </div>

            {/* Artifact & Metadata Inspector */}
            <div className="lg:col-span-5 bg-purple-50/40 rounded-2xl p-4 border border-purple-100 flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-bold uppercase bg-purple-100 text-purple-800 px-2 py-0.5 rounded-full">
                    Kandidat Siap Review CEO
                  </span>
                  <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                    QA: {longform.qa_status}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-slate-900 mt-2">{longform.title}</h4>
                <p className="text-[11px] text-slate-500 mt-1">
                  Diproduksi oleh Editor Long-Form (Raka Pratama). Audio ducking dan subtitle telah dibakar otomatis.
                </p>
              </div>

              {/* Technical Spec Box */}
              <div className="bg-white p-3 rounded-xl border border-purple-100 space-y-1.5 text-xs">
                <div className="flex justify-between text-slate-600">
                  <span>Ukuran File:</span>
                  <strong className="text-slate-900 font-mono">{(longform.file_size_bytes / (1024 * 1024)).toFixed(2)} MB</strong>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Resolusi:</span>
                  <strong className="text-slate-900 font-mono">{longform.resolution} @ 30 FPS</strong>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Aspect Ratio:</span>
                  <strong className="text-purple-700 font-mono">16:9 Landscape</strong>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Status Governance:</span>
                  <strong className="text-amber-600">Pending CEO Review</strong>
                </div>
              </div>

              {/* Artifacts links */}
              <div className="pt-1 flex flex-wrap gap-2 text-[11px]">
                <span className="inline-flex items-center gap-1 bg-white border border-slate-200 text-slate-700 px-2 py-1 rounded-lg">
                  <FileText className="w-3 h-3 text-purple-600" /> manifest.json
                </span>
                <span className="inline-flex items-center gap-1 bg-white border border-slate-200 text-slate-700 px-2 py-1 rounded-lg">
                  <CheckCircle className="w-3 h-3 text-emerald-600" /> source_ledger.json
                </span>
                <span className="inline-flex items-center gap-1 bg-white border border-slate-200 text-slate-700 px-2 py-1 rounded-lg">
                  <Clock className="w-3 h-3 text-blue-600" /> storyboard.json
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Topic Backlog & Transparent Rubric Table */}
        <div className="space-y-3 pt-3 border-t border-slate-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-purple-600" />
              <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Topic Discovery Backlog & Rubrik Skor Transparan (Maks. 70.0 Poin)
              </h4>
            </div>
            <button
              onClick={fetchLongformData}
              className="text-[11px] font-bold text-purple-600 hover:text-purple-700 flex items-center gap-1"
            >
              <RefreshCw className="w-3 h-3" /> Refresh
            </button>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-200">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-3.5 py-2.5">Kategori</th>
                  <th className="px-3.5 py-2.5">Judul Topik & Hook Question</th>
                  <th className="px-3.5 py-2.5 text-center">Skor Total</th>
                  <th className="px-3.5 py-2.5">Status</th>
                  <th className="px-3.5 py-2.5 text-right">Aksi</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {topics.slice(0, 5).map((t) => (
                  <tr key={t.id} className="hover:bg-purple-50/30 transition-colors">
                    <td className="px-3.5 py-2.5">
                      <span className="font-mono text-[10px] font-bold uppercase bg-slate-100 px-2 py-0.5 rounded text-slate-700">
                        {t.category}
                      </span>
                    </td>
                    <td className="px-3.5 py-2.5">
                      <div className="font-bold text-slate-800">{t.title}</div>
                      <div className="text-[11px] text-slate-400 line-clamp-1">{t.hook_question}</div>
                    </td>
                    <td className="px-3.5 py-2.5 text-center">
                      <span className="font-mono font-bold text-purple-700 bg-purple-50 px-2 py-1 rounded-lg border border-purple-100">
                        {t.total_score.toFixed(1)}
                      </span>
                    </td>
                    <td className="px-3.5 py-2.5">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        t.status === 'produced' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-600'
                      }`}>
                        {t.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-3.5 py-2.5 text-right">
                      <button
                        onClick={() => {
                          setSelectedTopicId(t.id);
                          handleTriggerLongform();
                        }}
                        disabled={isProducingLongform}
                        className="px-2.5 py-1 bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 rounded-lg text-[11px] font-bold transition-all disabled:opacity-50"
                      >
                        Pilih & Render
                      </button>
                    </td>
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
