import React, { useEffect, useState } from 'react';
import { 
  Bot, 
  Terminal, 
  Cpu, 
  Layers, 
  MessageSquare, 
  RefreshCw, 
  ExternalLink, 
  ShieldCheck, 
  Zap, 
  Send, 
  Clock, 
  Settings,
  ChevronRight,
  Maximize2
} from 'lucide-react';

interface HermesSession {
  id: string;
  title: string;
  model: string;
  source: string;
  message_count: number;
  last_activity_formatted: string;
  total_tokens: number;
}

interface HermesMessage {
  id: number;
  role: string;
  content: string;
  time: string;
  has_tools: boolean;
}

export const HermesCoreView: React.FC = () => {
  const [sessions, setSessions] = useState<HermesSession[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<HermesMessage[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [viewMode, setViewMode] = useState<'custom' | 'native'>('custom');
  const [promptInput, setPromptInput] = useState('');

  const fetchSessions = async () => {
    try {
      setLoadingSessions(true);
      const res = await fetch('/api/hermes/sessions');
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
        if (data.length > 0 && !selectedSessionId) {
          setSelectedSessionId(data[0].id);
        }
      }
    } catch (e) {
      console.error('Failed to fetch Hermes sessions:', e);
    } finally {
      setLoadingSessions(false);
    }
  };

  const fetchMessages = async (id: string) => {
    try {
      setLoadingMessages(true);
      const res = await fetch(`/api/hermes/sessions/${id}/messages`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data);
      }
    } catch (e) {
      console.error('Failed to fetch messages for session:', id, e);
    } finally {
      setLoadingMessages(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    if (selectedSessionId) {
      fetchMessages(selectedSessionId);
    }
  }, [selectedSessionId]);

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Top Header */}
      <div className="bg-slate-900 rounded-3xl p-6 text-white border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-teal-500/20 text-teal-400 flex items-center justify-center border border-teal-500/30">
            <Terminal className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-teal-500/20 text-teal-300 border border-teal-500/30">
                HERMES AGENT CORE
              </span>
              <span className="flex items-center gap-1 text-[11px] text-emerald-400 font-bold">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                Gateway Running
              </span>
            </div>
            <h1 className="text-xl font-bold">Hermes Agent Control & Session Terminal</h1>
            <p className="text-xs text-slate-400">
              Integrasi langsung dashboard native Hermes (:9119) ke dalam Harmage UI port 5173
            </p>
          </div>
        </div>

        {/* View Switcher: Custom UI vs Native Web Frame */}
        <div className="flex items-center gap-2">
          <div className="bg-slate-800 p-1 rounded-xl flex items-center gap-1 border border-slate-700">
            <button
              onClick={() => setViewMode('custom')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                viewMode === 'custom' ? 'bg-teal-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              Custom Console
            </button>
            <button
              onClick={() => setViewMode('native')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                viewMode === 'native' ? 'bg-teal-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              Native Hermes :9119
            </button>
          </div>

          <a
            href="http://127.0.0.1:9119"
            target="_blank"
            rel="noreferrer"
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all cursor-pointer"
            title="Buka Port 9119 di Tab Baru"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>

      {viewMode === 'native' ? (
        /* Native Hermes Frame */
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-lg h-[800px]">
          <iframe 
            src="/hermes-native/"
            title="Hermes Native Dashboard"
            className="w-full h-full border-none"
          />
        </div>
      ) : (
        /* Custom Synchronized Console */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 h-[750px]">
          {/* Sessions List (Left Column, matching Foto 1 Right Panel) */}
          <div className="lg:col-span-4 bg-white rounded-2xl border border-slate-200 shadow-soft flex flex-col overflow-hidden">
            <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-purple-600" />
                <h3 className="font-bold text-slate-800 text-sm">Riwayat Sesi Chat ({sessions.length})</h3>
              </div>
              <button 
                onClick={fetchSessions}
                className="p-1 text-slate-400 hover:text-purple-600 transition-colors"
                title="Refresh Sesi"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingSessions ? 'animate-spin' : ''}`} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-2 space-y-1.5 scrollbar-thin">
              {sessions.map(s => {
                const isSelected = s.id === selectedSessionId;
                return (
                  <button
                    key={s.id}
                    onClick={() => setSelectedSessionId(s.id)}
                    className={`w-full text-left p-3 rounded-xl transition-all cursor-pointer border ${
                      isSelected 
                        ? 'bg-purple-50/80 border-purple-200 shadow-xs' 
                        : 'bg-white hover:bg-slate-50 border-transparent'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <p className={`text-xs font-bold line-clamp-1 ${isSelected ? 'text-purple-950' : 'text-slate-800'}`}>
                        {s.title}
                      </p>
                      <span className="text-[10px] text-slate-400 whitespace-nowrap">
                        {s.last_activity_formatted}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 mt-1.5 text-[10px] text-slate-500">
                      <span className="px-1.5 py-0.5 rounded bg-slate-100 font-medium">
                        {s.source}
                      </span>
                      <span className="truncate text-slate-400">
                        {s.model}
                      </span>
                      <span className="ml-auto font-semibold text-purple-700">
                        {s.message_count} msgs
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Active Chat Viewer (Middle/Right Area, matching Foto 1 Main Console) */}
          <div className="lg:col-span-8 bg-slate-950 rounded-2xl border border-slate-800 shadow-xl flex flex-col overflow-hidden text-slate-200">
            {/* Console Header */}
            <div className="p-4 border-b border-slate-800/80 bg-slate-900/80 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                <div>
                  <p className="text-xs font-bold text-white">
                    {sessions.find(s => s.id === selectedSessionId)?.title || 'Pilih Sesi'}
                  </p>
                  <p className="text-[10px] text-slate-400">
                    ID: {selectedSessionId || '-'} &bull; Model: {sessions.find(s => s.id === selectedSessionId)?.model || 'qwen3.8-max'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono bg-slate-800 text-teal-400 px-2 py-0.5 rounded border border-slate-700">
                  xKiro Connected
                </span>
              </div>
            </div>

            {/* Messages Feed */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-xs">
              {loadingMessages ? (
                <div className="flex items-center justify-center h-full text-slate-500 gap-2">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Memuat pesan sesi...</span>
                </div>
              ) : messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-slate-600 space-y-2">
                  <Terminal className="w-8 h-8 opacity-40" />
                  <p className="text-xs">Tidak ada riwayat pesan di sesi ini.</p>
                </div>
              ) : (
                messages.map(m => {
                  const isUser = m.role === 'user';
                  const isTool = m.role === 'tool';
                  return (
                    <div 
                      key={m.id}
                      className={`p-3 rounded-xl border ${
                        isUser 
                          ? 'bg-purple-950/40 border-purple-800/50 text-purple-100 ml-6' 
                          : isTool 
                            ? 'bg-slate-900/90 border-slate-700/60 text-slate-300 text-[11px]' 
                            : 'bg-slate-900/50 border-slate-800 text-slate-200 mr-6'
                      }`}
                    >
                      <div className="flex items-center justify-between text-[10px] font-bold text-slate-500 mb-1">
                        <span className={isUser ? 'text-purple-400' : isTool ? 'text-amber-400' : 'text-teal-400'}>
                          [{m.role.toUpperCase()}]
                        </span>
                        <span>{m.time}</span>
                      </div>
                      <div className="whitespace-pre-wrap leading-relaxed">
                        {m.content}
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Bottom Command Input */}
            <div className="p-3 border-t border-slate-800 bg-slate-900/60 flex items-center gap-2">
              <input
                type="text"
                value={promptInput}
                onChange={e => setPromptInput(e.target.value)}
                placeholder="Ketik instruksi atau chat ke Hermes Agent..."
                className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
              />
              <button
                onClick={() => {
                  if (promptInput.trim()) {
                    alert('Instruksi dikirim ke sesi Hermes: ' + promptInput);
                    setPromptInput('');
                  }
                }}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Kirim</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
