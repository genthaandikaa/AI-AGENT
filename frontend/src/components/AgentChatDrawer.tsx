import React, { useState } from 'react';
import { Send, Bot, Sparkles } from 'lucide-react';
import { ChatMessage } from '../types';

export const AgentChatDrawer: React.FC = () => {
  const [selectedAgentId, setSelectedAgentId] = useState<string>('executive_manager');
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init-1',
      sender: 'agent',
      agent_name: 'Alex Vance',
      text: 'Halo CEO! Gue Alex Vance, Sipaling Manager Harmage. Mau delegasiin apaan lagi hari ini? Jangan bilang lo mau nyuruh gue ngerjain hal receh ya wkwk.',
      timestamp: 'Baru saja'
    }
  ]);

  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);

  const availableNpcs = [
    { id: 'executive_manager', name: 'Alex Vance', role: 'Executive Manager' },
    { id: 'treasurer', name: 'Marcus Drake', role: 'Bendahara ($0 Hawk)' },
    { id: 'secretary', name: 'Sophia Chen', role: 'Sekretaris & Notulen' },
    { id: 'creator_pm', name: 'Diana Prince', role: 'PIC Divisi Konten' },
    { id: 'video_editor', name: 'Leo Sparks', role: 'Editor Shorts' },
    { id: 'scriptwriter', name: 'Maya Lin', role: 'Scriptwriter TikTok' },
    { id: 'tiktok_affiliate', name: 'Victor Sterling', role: 'Affiliate TikTok' },
    { id: 'qa_sentinel', name: 'Zackary Cross', role: 'QA Sentinel' }
  ];

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isSending) return;

    const userText = input.trim();
    const newMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: userText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, newMsg]);
    setInput('');
    setIsSending(true);

    try {
      const history = messages.slice(-4).map(m => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text
      }));

      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: selectedAgentId,
          message: userText,
          history
        })
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      const reply: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        agent_name: data.name || 'NPC Brain',
        text: data.reply || 'Waduh connection timeout bestie, coba lagi bentar!',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, reply]);
    } catch (err) {
      const errMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        agent_name: 'System',
        text: 'Gagal menghubungi otak AI NPC. Pastikan backend server online.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setIsSending(false);
    }
  };

  const currentAgent = availableNpcs.find(n => n.id === selectedAgentId) || availableNpcs[0];

  return (
    <div className="bg-white rounded-3xl p-5 border border-purple-100 shadow-soft flex flex-col justify-between h-[520px]">
      {/* Header with NPC Switcher */}
      <div className="flex items-center justify-between pb-3 border-b border-purple-50 mb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center flex-shrink-0">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-slate-900 tracking-tight flex items-center gap-1.5">
              Live NPC Brain
              <span className="flex items-center gap-1 text-[9px] text-emerald-600 font-semibold bg-emerald-50 px-1.5 py-0.2 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                Real LLM
              </span>
            </h3>
            <p className="text-[10px] text-purple-600 font-medium">
              Toxic Gen-Z Slang Active
            </p>
          </div>
        </div>

        {/* NPC Selector */}
        <select
          value={selectedAgentId}
          onChange={(e) => {
            setSelectedAgentId(e.target.value);
            const npc = availableNpcs.find(n => n.id === e.target.value);
            if (npc) {
              setMessages(prev => [
                ...prev,
                {
                  id: Date.now().toString(),
                  sender: 'agent',
                  agent_name: npc.name,
                  text: `Lo switch ngobrol sama ${npc.name} (${npc.role}). Spill ada urusan apa?`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }
              ]);
            }
          }}
          className="bg-purple-50 border border-purple-200 text-purple-800 text-[11px] font-bold rounded-xl px-2 py-1 focus:outline-none focus:border-purple-500 cursor-pointer"
        >
          {availableNpcs.map(npc => (
            <option key={npc.id} value={npc.id}>
              {npc.name} ({npc.role})
            </option>
          ))}
        </select>
      </div>

      {/* Message Feed */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1 text-xs">
        {messages.map((m) => {
          const isUser = m.sender === 'user';
          return (
            <div key={m.id} className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
              {!isUser && (
                <span className="text-[10px] font-bold text-purple-700 mb-0.5 ml-1">
                  {m.agent_name}
                </span>
              )}
              <div className={`p-3 rounded-2xl max-w-[88%] ${
                isUser 
                  ? 'bg-purple-600 text-white rounded-br-none shadow-sm' 
                  : 'bg-purple-50/70 border border-purple-100 text-slate-800 rounded-bl-none'
              }`}>
                <p className="whitespace-pre-wrap leading-relaxed">{m.text}</p>
                <div className={`text-[9px] mt-1 text-right ${isUser ? 'text-purple-200' : 'text-slate-400'}`}>
                  {m.timestamp}
                </div>
              </div>
            </div>
          );
        })}
        {isSending && (
          <div className="flex items-center gap-2 text-xs text-purple-600 italic p-2 bg-purple-50/50 rounded-xl">
            <Sparkles className="w-3.5 h-3.5 animate-spin" />
            <span>{currentAgent.name} lagi mikir roasting...</span>
          </div>
        )}
      </div>

      {/* Input Field */}
      <form onSubmit={handleSend} className="pt-3 border-t border-purple-50 flex items-center gap-2">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={`Chat dengan ${currentAgent.name}...`}
          disabled={isSending}
          className="flex-1 bg-slate-50 border border-purple-100 rounded-2xl px-3.5 py-2 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-purple-500"
        />
        <button 
          type="submit" 
          disabled={!input.trim() || isSending}
          className="w-8 h-8 rounded-xl bg-purple-600 hover:bg-purple-700 text-white flex items-center justify-center transition-colors shadow-sm disabled:opacity-40"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
};
