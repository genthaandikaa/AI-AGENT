import React from 'react';
import { Bot, Sparkles, Building2, Shield, Wrench } from 'lucide-react';
import { Hermes3DViewer } from '../components/Hermes3DViewer';
import { Agent } from '../types';

interface OverviewViewProps {
  agents: Agent[];
  onSelectAgent: (agent: Agent) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({ agents, onSelectAgent }) => {
  return (
    <div className="space-y-6">
      {/* 1. Hermes 3D Virtual Office Integration */}
      <Hermes3DViewer onSelectAgent={onSelectAgent} />

      {/* 2. Roster of 12 AI Workforce Members (Loaded dynamically from API) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <Bot className="w-4 h-4 text-purple-600" />
              Anggota AI Workforce & Otak LLM ({agents.length})
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Setiap agen dibekali persona Gen-Z unik dan terhubung ke LLM via backend Harmage.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <div
              key={agent.id}
              onClick={() => onSelectAgent(agent)}
              className="bg-white rounded-2xl p-4 border border-purple-50 shadow-soft hover:shadow-md hover:border-purple-200 transition-all duration-150 cursor-pointer flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center gap-3 mb-2.5">
                  <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center p-1 border border-purple-100 flex-shrink-0 group-hover:scale-105 transition-transform">
                    {agent.avatar_svg ? (
                      <div 
                        className="w-full h-full [&>svg]:w-full [&>svg]:h-full" 
                        dangerouslySetInnerHTML={{ __html: agent.avatar_svg }} 
                      />
                    ) : (
                      <span className="font-bold text-purple-600 text-xs">{agent.name.substring(0, 2)}</span>
                    )}
                  </div>

                  <div className="min-w-0">
                    <div className="flex items-center gap-1.5">
                      <h4 className="text-xs font-bold text-slate-900 truncate group-hover:text-purple-600 transition-colors">
                        {agent.name}
                      </h4>
                      <span className="w-2 h-2 rounded-full bg-emerald-500 flex-shrink-0"></span>
                    </div>
                    <p className="text-[11px] text-purple-600 font-medium truncate">{agent.role_title}</p>
                    <span className="inline-block mt-0.5 text-[9px] font-bold uppercase tracking-wider bg-purple-50 text-purple-700 px-2 py-0.2 rounded-full">
                      {agent.division}
                    </span>
                  </div>
                </div>

                <div className="flex flex-wrap gap-1 mb-2">
                  {agent.personality_traits.slice(0, 3).map((t, idx) => (
                    <span key={idx} className="bg-slate-50 text-slate-600 text-[10px] font-medium px-2 py-0.5 rounded-md border border-slate-100">
                      {t}
                    </span>
                  ))}
                </div>

                <p className="text-[11px] text-slate-400 line-clamp-2 italic mb-2">
                  "{agent.tone_of_voice}"
                </p>
              </div>

              <div className="pt-2 border-t border-purple-50 flex items-center justify-between text-[11px] text-slate-400 font-medium">
                <span>{agent.competencies.length} Kompetensi</span>
                <span className="text-purple-600 font-bold group-hover:translate-x-0.5 transition-transform">
                  Inspect Brain →
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
