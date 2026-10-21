import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowUpRight, ArrowDownRight, TrendingUp } from 'lucide-react';

const chartData = [
  { day: 'Mon', value: 45 },
  { day: 'Tue', value: 58 },
  { day: 'Wed', value: 52 },
  { day: 'Thu', value: 74 },
  { day: 'Fri', value: 68 },
  { day: 'Sat', value: 85 },
  { day: 'Sun', value: 96 },
];

export const AgentPerformanceChart: React.FC = () => {
  return (
    <div className="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-purple-600" />
          Agent Performance
        </h3>
        <select className="bg-slate-50 border border-slate-200/80 rounded-xl px-2.5 py-1 text-[11px] font-semibold text-slate-600 focus:outline-none cursor-pointer">
          <option>This Week</option>
          <option>This Month</option>
        </select>
      </div>

      {/* Recharts Area Chart */}
      <div className="h-36 w-full -ml-3">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="purpleGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <XAxis 
              dataKey="day" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: '#94a3b8', fontSize: 10 }} 
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: '#94a3b8', fontSize: 10 }}
              ticks={[0, 25, 50, 75, 100]}
              domain={[0, 100]}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#0f172a', 
                borderRadius: '12px', 
                border: 'none', 
                color: '#fff', 
                fontSize: '11px',
                padding: '6px 10px'
              }} 
            />
            <Area 
              type="monotone" 
              dataKey="value" 
              stroke="#8b5cf6" 
              strokeWidth={3} 
              fillOpacity={1} 
              fill="url(#purpleGradient)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Bottom 3 KPI stats */}
      <div className="grid grid-cols-3 gap-2 pt-3 border-t border-slate-100/80 mt-2">
        <div>
          <span className="text-[10px] text-slate-400 font-medium block">Success Rate</span>
          <div className="flex items-center gap-1">
            <span className="text-xs font-bold text-slate-900">96.4%</span>
            <span className="text-[10px] text-emerald-600 font-semibold flex items-center">
              <ArrowUpRight className="w-3 h-3" /> 8.2%
            </span>
          </div>
        </div>

        <div>
          <span className="text-[10px] text-slate-400 font-medium block">Tasks Completed</span>
          <div className="flex items-center gap-1">
            <span className="text-xs font-bold text-slate-900">1,243</span>
            <span className="text-[10px] text-emerald-600 font-semibold flex items-center">
              <ArrowUpRight className="w-3 h-3" /> 12.5%
            </span>
          </div>
        </div>

        <div>
          <span className="text-[10px] text-slate-400 font-medium block">Avg. Response Time</span>
          <div className="flex items-center gap-1">
            <span className="text-xs font-bold text-slate-900">1.3s</span>
            <span className="text-[10px] text-emerald-600 font-semibold flex items-center">
              <ArrowDownRight className="w-3 h-3" /> 0.4s
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
