import React from 'react';
import { X, CheckCircle, Shield, Wrench, FileCode } from 'lucide-react';
import { Agent } from '../types';

interface AgentDetailModalProps {
  agent: Agent | null;
  onClose: () => void;
}

export const AgentDetailModal: React.FC<AgentDetailModalProps> = ({ agent, onClose }) => {
  if (!agent) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-slate-100 p-6 flex flex-col gap-5">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-14 h-14 rounded-2xl bg-indigo-50 flex items-center justify-center p-1 border border-indigo-100 flex-shrink-0">
              {agent.avatar_svg ? (
                <div 
                  className="w-full h-full [&>svg]:w-full [&>svg]:h-full" 
                  dangerouslySetInnerHTML={{ __html: agent.avatar_svg }} 
                />
              ) : (
                <span className="font-bold text-lg text-indigo-600">{agent.name.substring(0, 2)}</span>
              )}
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">{agent.name}</h3>
              <p className="text-xs text-indigo-600 font-medium">{agent.role_title}</p>
              <span className="inline-block mt-1 text-[9px] font-bold uppercase tracking-wider bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
                {agent.division}
              </span>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 rounded-xl hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Personality & Tone */}
        <div className="space-y-1.5">
          <h4 className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5 text-indigo-500" />
            Personality Traits & Voice Tone
          </h4>
          <div className="flex flex-wrap gap-1.5 pt-1">
            {agent.personality_traits.map((t, idx) => (
              <span key={idx} className="bg-purple-50 text-purple-700 text-[11px] font-semibold px-2.5 py-1 rounded-xl border border-purple-100">
                {t}
              </span>
            ))}
          </div>
          <p className="text-xs text-slate-500 mt-1 italic">
            Tone: {agent.tone_of_voice}
          </p>
        </div>

        {/* Competencies */}
        <div className="space-y-1.5">
          <h4 className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
            Core Competencies
          </h4>
          <div className="grid grid-cols-2 gap-2 text-xs text-slate-600">
            {agent.competencies.map((c, idx) => (
              <div key={idx} className="flex items-center gap-1.5 bg-slate-50 p-2 rounded-xl border border-slate-100">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                <span>{c}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Allowed Tools */}
        <div className="space-y-1.5">
          <h4 className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
            <Wrench className="w-3.5 h-3.5 text-amber-500" />
            Allowed Tools & MCPs
          </h4>
          <div className="flex flex-wrap gap-1.5 text-xs">
            {agent.allowed_tools.map((tool, idx) => (
              <code key={idx} className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded-lg text-[10px] font-mono border border-slate-200">
                {tool}
              </code>
            ))}
          </div>
        </div>

        {/* System Prompt */}
        <div className="space-y-1.5">
          <h4 className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
            <FileCode className="w-3.5 h-3.5 text-sky-500" />
            Operational System Prompt & Boundaries
          </h4>
          <pre className="bg-slate-900 text-slate-200 p-3.5 rounded-2xl text-[11px] font-mono whitespace-pre-wrap max-h-36 overflow-y-auto leading-relaxed border border-slate-800">
            {agent.system_prompt}
          </pre>
        </div>

        {/* Footer */}
        <div className="flex justify-end pt-2 border-t border-slate-100">
          <button 
            onClick={onClose}
            className="px-5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-2xl transition-colors"
          >
            Close Profile
          </button>
        </div>
      </div>
    </div>
  );
};
