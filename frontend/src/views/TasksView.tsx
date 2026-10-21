import React, { useState } from 'react';
import { CheckSquare, Plus, AlertCircle, CheckCircle2, Clock } from 'lucide-react';
import { TaskItem } from '../types';

interface TasksViewProps {
  tasks: TaskItem[];
  onSelectTask: (task: TaskItem) => void;
  onOpenNewTask: () => void;
  onRefresh: () => void;
}

export const TasksView: React.FC<TasksViewProps> = ({
  tasks,
  onSelectTask,
  onOpenNewTask,
  onRefresh
}) => {
  const [viewMode, setViewMode] = useState<'kanban' | 'list'>('kanban');
  const [filterPriority, setFilterPriority] = useState<string>('all');

  const filteredTasks = tasks.filter(t => {
    return filterPriority === 'all' || t.priority === filterPriority;
  });

  const columns = [
    { id: 'queued', label: 'Queued', color: 'bg-slate-200' },
    { id: 'in_progress', label: 'In Progress', color: 'bg-indigo-500' },
    { id: 'blocked', label: 'Blocked', color: 'bg-rose-500' },
    { id: 'review', label: 'Review', color: 'bg-amber-500' },
    { id: 'completed', label: 'Completed', color: 'bg-emerald-500' },
  ];

  return (
    <div className="space-y-6">
      {/* Controls Bar */}
      <div className="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <CheckSquare className="w-4 h-4 text-indigo-500" />
            Task & Project Management ({filteredTasks.length})
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Real persistent tasks stored in SQLite with dependency checks and retry counters.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Priority filter */}
          <select 
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 focus:outline-none"
          >
            <option value="all">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          {/* View Switcher */}
          <div className="flex items-center bg-slate-100 p-1 rounded-2xl text-xs font-semibold">
            <button
              onClick={() => setViewMode('kanban')}
              className={`px-3 py-1 rounded-xl transition-all ${viewMode === 'kanban' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500'}`}
            >
              Kanban
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-1 rounded-xl transition-all ${viewMode === 'list' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500'}`}
            >
              List Table
            </button>
          </div>

          <button
            onClick={onOpenNewTask}
            className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl text-xs font-semibold shadow-md transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Create Task</span>
          </button>
        </div>
      </div>

      {/* Kanban Board View */}
      {viewMode === 'kanban' ? (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 overflow-x-auto pb-4">
          {columns.map(col => {
            const colTasks = filteredTasks.filter(t => t.status === col.id);
            return (
              <div key={col.id} className="bg-slate-100/70 rounded-3xl p-4 flex flex-col gap-3 min-w-[220px]">
                <div className="flex items-center justify-between px-1">
                  <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">{col.label}</span>
                  <span className="text-[10px] font-bold bg-white text-slate-600 px-2 py-0.5 rounded-full shadow-sm">
                    {colTasks.length}
                  </span>
                </div>

                <div className="space-y-2.5 flex-1">
                  {colTasks.map(task => (
                    <div
                      key={task.id}
                      onClick={() => onSelectTask(task)}
                      className="bg-white rounded-2xl p-3.5 border border-slate-100 shadow-sm hover:shadow-md hover:border-indigo-100 transition-all cursor-pointer space-y-2 group"
                    >
                      <div className="flex items-center justify-between text-[10px]">
                        <span className="font-mono text-slate-400 font-medium">{task.id}</span>
                        <span className={`px-2 py-0.5 rounded-lg font-bold uppercase tracking-wider ${
                          task.priority === 'high' || task.priority === 'critical' 
                            ? 'bg-rose-50 text-rose-600' 
                            : 'bg-slate-100 text-slate-600'
                        }`}>
                          {task.priority}
                        </span>
                      </div>

                      <h4 className="text-xs font-bold text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-2">
                        {task.title}
                      </h4>

                      <div className="pt-2 border-t border-slate-50 flex items-center justify-between text-[10px] text-slate-500">
                        <span className="truncate max-w-[120px]">👤 {task.assignee}</span>
                        {task.retry_count > 0 && <span>🔄 {task.retry_count}/{task.max_retries}</span>}
                      </div>
                    </div>
                  ))}
                  {colTasks.length === 0 && (
                    <div className="text-center py-6 text-slate-400 text-xs italic">
                      No tasks in {col.label}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* List Table View */
        <div className="bg-white rounded-3xl border border-slate-100 shadow-soft overflow-hidden">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100 text-slate-500 uppercase tracking-wider text-[10px]">
                <th className="p-4">ID</th>
                <th className="p-4">Title</th>
                <th className="p-4">Assignee</th>
                <th className="p-4">Priority</th>
                <th className="p-4">Status</th>
                <th className="p-4">Retries</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredTasks.map(t => (
                <tr 
                  key={t.id}
                  onClick={() => onSelectTask(t)}
                  className="hover:bg-slate-50 cursor-pointer transition-colors"
                >
                  <td className="p-4 font-mono font-medium text-slate-500">{t.id}</td>
                  <td className="p-4 font-bold text-slate-900">{t.title}</td>
                  <td className="p-4 text-slate-600">{t.assignee}</td>
                  <td className="p-4">
                    <span className="px-2 py-0.5 rounded-lg text-[10px] font-bold uppercase bg-slate-100 text-slate-700">
                      {t.priority}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-0.5 rounded-lg text-[10px] font-bold uppercase ${
                      t.status === 'completed' ? 'bg-emerald-50 text-emerald-600' : 
                      (t.status === 'in_progress' ? 'bg-indigo-50 text-indigo-600' : 'bg-slate-100 text-slate-600')
                    }`}>
                      {t.status}
                    </span>
                  </td>
                  <td className="p-4 text-slate-500">{t.retry_count} / {t.max_retries}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
