import React from 'react';
import { CheckCircle2, Clock, AlertCircle } from 'lucide-react';
import { TaskItem } from '../types';

interface TaskQueueProps {
  tasks: TaskItem[];
  onSelectTask: (task: TaskItem) => void;
  onViewAll?: () => void;
}

export const TaskQueue: React.FC<TaskQueueProps> = ({ tasks, onSelectTask, onViewAll }) => {
  // If database tasks are fewer, provide realistic sample tasks
  const defaultTasks: TaskItem[] = [
    {
      id: 'TSK-101',
      title: 'Analyze customer feedback & viral hooks',
      assignee: 'Ethan Cole (Researcher)',
      priority: 'high',
      status: 'in_progress',
      retry_count: 0,
      max_retries: 3
    },
    {
      id: 'TSK-102',
      title: 'Generate 9:16 vertical short script',
      assignee: 'Maya Lin (Scriptwriter)',
      priority: 'medium',
      status: 'queued',
      retry_count: 0,
      max_retries: 3
    },
    {
      id: 'TSK-103',
      title: 'Audit port & secret leak logs',
      assignee: 'Kage Kuro (Security)',
      priority: 'medium',
      status: 'completed',
      retry_count: 0,
      max_retries: 3
    },
    {
      id: 'TSK-104',
      title: 'Compile evening CEO executive summary',
      assignee: 'Alex Vance (Executive Manager)',
      priority: 'low',
      status: 'queued',
      retry_count: 0,
      max_retries: 3
    }
  ];

  const displayTasks = tasks.length > 0 ? tasks.slice(0, 4) : defaultTasks;

  return (
    <div className="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Clock className="w-4 h-4 text-purple-500" />
          Task Queue
        </h3>
        <button 
          onClick={onViewAll} 
          className="text-[11px] font-semibold text-indigo-600 hover:text-indigo-700 transition-colors"
        >
          View all
        </button>
      </div>

      <div className="space-y-3">
        {displayTasks.map((task) => {
          const isHigh = task.priority === 'high' || task.priority === 'critical';
          const isMed = task.priority === 'medium';

          return (
            <div 
              key={task.id}
              onClick={() => onSelectTask(task)}
              className="flex items-center justify-between p-2 rounded-2xl hover:bg-slate-50 transition-colors cursor-pointer group"
            >
              <div className="flex items-center gap-2.5 min-w-0 pr-2">
                <div className={`w-7 h-7 rounded-xl flex items-center justify-center text-white flex-shrink-0 ${
                  isHigh ? 'bg-rose-500' : (isMed ? 'bg-amber-500' : 'bg-emerald-500')
                }`}>
                  {isHigh ? <AlertCircle className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
                </div>

                <div className="min-w-0">
                  <h4 className="text-xs font-semibold text-slate-800 truncate group-hover:text-indigo-600 transition-colors">
                    {task.title}
                  </h4>
                  <p className="text-[10px] text-slate-400 truncate">
                    {task.assignee}
                  </p>
                </div>
              </div>

              {/* Priority Tag */}
              <span className={`px-2.5 py-1 rounded-xl text-[10px] font-bold uppercase tracking-wider flex-shrink-0 ${
                isHigh ? 'bg-rose-50 text-rose-600 border border-rose-200' : 
                (isMed ? 'bg-amber-50 text-amber-600 border border-amber-200' : 'bg-emerald-50 text-emerald-600 border border-emerald-200')
              }`}>
                {task.priority}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
