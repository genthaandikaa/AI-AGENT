import React from 'react';
import { Agent } from '../types';

interface ActiveAgentsProps {
  agents: Agent[];
  onSelectAgent: (agent: Agent) => void;
  onViewAll: () => void;
}

export const ActiveAgents: React.FC<ActiveAgentsProps> = ({ agents, onSelectAgent, onViewAll }) => {
  // Pastel avatar color configurations
  const colorThemes = [
    { bg: 'bg-purple-100', text: 'text-purple-600', ring: 'ring-purple-200' },
    { bg: 'bg-emerald-100', text: 'text-emerald-600', ring: 'ring-emerald-200' },
    { bg: 'bg-sky-100', text: 'text-sky-600', ring: 'ring-sky-200' },
    { bg: 'bg-amber-100', text: 'text-amber-600', ring: 'ring-amber-200' },
    { bg: 'bg-rose-100', text: 'text-rose-600', ring: 'ring-rose-200' },
    { bg: 'bg-indigo-100', text: 'text-indigo-600', ring: 'ring-indigo-200' },
  ];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-bold text-slate-900 tracking-tight">Active Agents</h2>
        <button 
          onClick={onViewAll} 
          className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 transition-colors"
        >
          View all
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        {agents.slice(0, 4).map((agent, index) => {
          const theme = colorThemes[index % colorThemes.length];
          const isOnline = agent.status === 'online' || agent.status === 'idle';
          const isBusy = agent.status === 'busy' || agent.status === 'in_meeting';

          return (
            <div
              key={agent.id}
              onClick={() => onSelectAgent(agent)}
              className="bg-white rounded-3xl p-4 border border-slate-100/90 shadow-soft hover:shadow-lg hover:border-indigo-100 transition-all duration-200 cursor-pointer flex flex-col justify-between group"
            >
              <div className="flex items-center gap-3 mb-3">
                {/* 2D / Styled Avatar Box */}
                <div className={`w-12 h-12 rounded-2xl ${theme.bg} ${theme.text} flex items-center justify-center p-1.5 shadow-sm group-hover:scale-105 transition-transform flex-shrink-0`}>
                  {agent.avatar_svg ? (
                    <div 
                      className="w-full h-full [&>svg]:w-full [&>svg]:h-full" 
                      dangerouslySetInnerHTML={{ __html: agent.avatar_svg }} 
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white font-bold flex items-center justify-center text-xs">
                      {agent.name.substring(0, 2).toUpperCase()}
                    </div>
                  )}
                </div>

                {/* Name & Status */}
                <div className="min-w-0">
                  <h3 className="text-xs font-bold text-slate-900 truncate group-hover:text-indigo-600 transition-colors">
                    {agent.name}
                  </h3>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      isOnline ? 'bg-emerald-500' : (isBusy ? 'bg-amber-500' : 'bg-slate-400')
                    }`}></span>
                    <span className="text-[10px] font-medium text-slate-500 capitalize">
                      {isOnline ? 'Online' : (isBusy ? 'Busy' : 'Idle')}
                    </span>
                  </div>
                </div>
              </div>

              {/* Metrics Row */}
              <div className="grid grid-cols-2 gap-2 pt-3 border-t border-slate-100/80">
                <div>
                  <span className="text-[10px] text-slate-400 font-medium block">Tasks</span>
                  <span className="text-xs font-bold text-slate-800">{agent.tasks_count || 18}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-medium block">Success Rate</span>
                  <span className="text-xs font-bold text-slate-800">{agent.success_rate || 97}%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
