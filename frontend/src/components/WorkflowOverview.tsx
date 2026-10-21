import React from 'react';
import { Layers, Video, Users, Search, FileText } from 'lucide-react';
import { WorkflowItem } from '../types';

interface WorkflowOverviewProps {
  onViewAll?: () => void;
}

export const WorkflowOverview: React.FC<WorkflowOverviewProps> = ({ onViewAll }) => {
  const workflows: (WorkflowItem & { icon: any })[] = [
    { id: '1', name: 'Short-Form Video Engine', progress: 88, status: 'Active', color: 'bg-indigo-600', icon: Video },
    { id: '2', name: 'Market & Viral Research', progress: 94, status: 'Active', color: 'bg-emerald-500', icon: Search },
    { id: '3', name: 'Lead & Affiliate Qualification', progress: 78, status: 'Active', color: 'bg-sky-500', icon: Users },
    { id: '4', name: 'CEO Executive Reporting', progress: 65, status: 'Scheduled', color: 'bg-amber-500', icon: FileText },
  ];

  return (
    <div className="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-500" />
          Workflow Overview
        </h3>
        <button 
          onClick={onViewAll} 
          className="text-[11px] font-semibold text-indigo-600 hover:text-indigo-700 transition-colors"
        >
          View all
        </button>
      </div>

      <div className="space-y-4">
        {workflows.map((wf) => {
          const Icon = wf.icon;
          return (
            <div key={wf.id} className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 font-medium text-slate-800">
                  <div className="p-1 rounded-lg bg-slate-100 text-slate-600">
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                  <span className="truncate max-w-[150px]">{wf.name}</span>
                </div>
                <span className="font-bold text-slate-700 text-[11px]">{wf.progress}%</span>
              </div>

              {/* Progress Bar */}
              <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full ${wf.color} transition-all duration-500`}
                  style={{ width: `${wf.progress}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
