import React from 'react';
import { ActivityItem } from '../types';

interface RealtimeActivityProps {
  activities: ActivityItem[];
}

export const RealtimeActivity: React.FC<RealtimeActivityProps> = ({ activities }) => {
  const defaultItems = [
    { id: 1, actor: 'Alex Vance', action: 'Chaired morning operations sync', time: '2m ago' },
    { id: 2, actor: 'Leo Sparks', action: 'Completed vertical video FFmpeg render', time: '5m ago' },
    { id: 3, actor: 'Zackary Cross', action: 'Approved QA checklist for pilot short', time: '8m ago' },
    { id: 4, actor: 'Aria Thorne', action: 'Staged TikTok draft for CEO review', time: '15m ago' },
  ];

  const items = activities.length > 0 
    ? activities.slice(0, 4).map((a, i) => ({
        id: a.id || i,
        actor: a.actor,
        action: a.action,
        time: 'Just now'
      }))
    : defaultItems;

  return (
    <div className="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-bold text-slate-900 tracking-tight">Realtime Activity</h3>
        <span className="flex items-center gap-1.5 text-[10px] text-emerald-600 font-bold bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span>
          Live
        </span>
      </div>

      <div className="space-y-3">
        {items.map((item) => (
          <div key={item.id} className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2.5 min-w-0 pr-2">
              <div className="w-7 h-7 rounded-xl bg-indigo-50 text-indigo-600 font-bold flex items-center justify-center text-[10px] flex-shrink-0">
                {item.actor.substring(0, 2).toUpperCase()}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-medium text-slate-800 truncate">
                  <span className="font-semibold text-slate-900">{item.actor}</span> {item.action}
                </p>
              </div>
            </div>
            <span className="text-[10px] text-slate-400 whitespace-nowrap flex-shrink-0">{item.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
