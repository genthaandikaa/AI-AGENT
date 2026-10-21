import React from 'react';
import { Mail, Bot, FileText, Bell, Plus, ArrowRight, Sparkles } from 'lucide-react';

interface AutomationHubProps {
  onAddAutomation?: () => void;
}

export const AutomationHub: React.FC<AutomationHubProps> = ({ onAddAutomation }) => {
  return (
    <div className="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-indigo-500" />
          Automation Hub
        </h3>
        <button className="text-[11px] font-semibold text-indigo-600 hover:text-indigo-700 transition-colors">
          View all
        </button>
      </div>

      {/* Pipeline Sequence Cards */}
      <div className="flex items-center gap-2 overflow-x-auto py-2 scrollbar-none">
        {/* Step 1: Trigger */}
        <div className="flex items-center gap-3 bg-slate-50 border border-slate-200/80 rounded-2xl p-3 min-w-[160px] flex-shrink-0">
          <div className="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center flex-shrink-0">
            <Mail className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[9px] uppercase font-bold text-slate-400 block tracking-wider">Trigger</span>
            <span className="text-xs font-bold text-slate-800">CEO Goal / Prompt</span>
          </div>
        </div>

        <ArrowRight className="w-4 h-4 text-slate-300 flex-shrink-0" />

        {/* Step 2: AI Agent */}
        <div className="flex items-center gap-3 bg-slate-50 border border-slate-200/80 rounded-2xl p-3 min-w-[160px] flex-shrink-0">
          <div className="w-8 h-8 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center flex-shrink-0">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[9px] uppercase font-bold text-slate-400 block tracking-wider">AI Agent</span>
            <span className="text-xs font-bold text-slate-800">Orchestrate & Plan</span>
          </div>
        </div>

        <ArrowRight className="w-4 h-4 text-slate-300 flex-shrink-0" />

        {/* Step 3: Action */}
        <div className="flex items-center gap-3 bg-slate-50 border border-slate-200/80 rounded-2xl p-3 min-w-[160px] flex-shrink-0">
          <div className="w-8 h-8 rounded-xl bg-sky-100 text-sky-600 flex items-center justify-center flex-shrink-0">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[9px] uppercase font-bold text-slate-400 block tracking-wider">Action</span>
            <span className="text-xs font-bold text-slate-800">Render Local Short</span>
          </div>
        </div>

        <ArrowRight className="w-4 h-4 text-slate-300 flex-shrink-0" />

        {/* Step 4: Notify */}
        <div className="flex items-center gap-3 bg-slate-50 border border-slate-200/80 rounded-2xl p-3 min-w-[160px] flex-shrink-0">
          <div className="w-8 h-8 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center flex-shrink-0">
            <Bell className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[9px] uppercase font-bold text-slate-400 block tracking-wider">Notify</span>
            <span className="text-xs font-bold text-slate-800">Telegram Gateway</span>
          </div>
        </div>
      </div>

      {/* Add Automation Action Button */}
      <div className="pt-3 mt-3 border-t border-slate-100 flex justify-center">
        <button 
          onClick={onAddAutomation}
          className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1.5 transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add New Automation</span>
        </button>
      </div>
    </div>
  );
};
