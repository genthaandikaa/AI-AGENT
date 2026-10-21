import React, { useState } from 'react';
import { Bot, Search, Shield, Wrench } from 'lucide-react';
import { Agent } from '../types';

interface AgentsViewProps {
  agents: Agent[];
  onSelectAgent: (agent: Agent) => void;
}

export const AgentsView: React.FC<AgentsViewProps> = ({ agents, onSelectAgent }) => {
  const [filterDivision, setFilterDivision] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const divisions = ['all', 'Executive Suite', 'Creator Division', 'Affiliate Division', 'Trading Division', 'Cybersecurity Division'];

  const filteredAgents = agents.filter(agent => {
    const matchesDiv = filterDivision === 'all' || agent.division === filterDivision;
    const matchesQuery = agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         agent.role_title.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesDiv && matchesQuery;
  });

  return (
    <div className="space-y-6">
      {/* Header & Filter Controls */}
      <div className="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Bot className="w-4 h-4 text-indigo-500" />
            2D NPC Personas & Organizational Roles ({filteredAgents.length})
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Every agent operates with a dedicated 2D persona, behavioral traits, and scoped toolset.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search agent or role..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>

          {/* Division Filter */}
          <select 
            value={filterDivision}
            onChange={(e) => setFilterDivision(e.target.value)}
            className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 focus:outline-none cursor-pointer"
          >
            {divisions.map(d => (
              <option key={d} value={d}>
                {d === 'all' ? 'All Divisions' : d}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Agents 2D Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredAgents.map((agent) => (
          <div 
            key={agent.id}
            onClick={() => onSelectAgent(agent)}
            className="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft hover:shadow-xl hover:border-indigo-100 transition-all duration-200 cursor-pointer flex flex-col justify-between group"
          >
            <div>
              <div className="flex items-center gap-3.5 mb-3.5">
                <div className="w-14 h-14 rounded-2xl bg-indigo-50 flex items-center justify-center p-1 border border-indigo-100/60 shadow-sm flex-shrink-0 group-hover:scale-105 transition-transform">
                  {agent.avatar_svg ? (
                    <div 
                      className="w-full h-full [&>svg]:w-full [&>svg]:h-full" 
                      dangerouslySetInnerHTML={{ __html: agent.avatar_svg }} 
                    />
                  ) : (
                    <span className="font-bold text-indigo-600 text-sm">{agent.name.substring(0, 2)}</span>
                  )}
                </div>

                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-bold text-slate-900 truncate group-hover:text-indigo-600 transition-colors">
                      {agent.name}
                    </h3>
                    <span className="w-2 h-2 rounded-full bg-emerald-500 flex-shrink-0"></span>
                  </div>
                  <p className="text-xs text-indigo-600 font-medium truncate mt-0.5">{agent.role_title}</p>
                  <span className="inline-block mt-1 text-[9px] font-bold uppercase tracking-wider bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
                    {agent.division}
                  </span>
                </div>
              </div>

              {/* Personality Chips */}
              <div className="flex flex-wrap gap-1 mb-3">
                {agent.personality_traits.map((t, idx) => (
                  <span key={idx} className="bg-slate-50 text-slate-600 text-[10px] font-medium px-2 py-0.5 rounded-lg border border-slate-100">
                    {t}
                  </span>
                ))}
              </div>

              {/* Tone Preview */}
              <p className="text-[11px] text-slate-400 line-clamp-2 italic mb-3">
                "{agent.tone_of_voice}"
              </p>
            </div>

            {/* Bottom Meta */}
            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
              <span className="flex items-center gap-1 font-medium">
                <Shield className="w-3.5 h-3.5 text-indigo-500" />
                {agent.competencies.length} Competencies
              </span>
              <span className="flex items-center gap-1 font-mono font-medium text-slate-400">
                <Wrench className="w-3.5 h-3.5 text-amber-500" />
                {agent.allowed_tools.length} Tools
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
