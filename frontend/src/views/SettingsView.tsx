import React from 'react';
import { Settings, Shield, User, Database, Bot } from 'lucide-react';

export const SettingsView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-3xl p-6 border border-slate-100 shadow-soft space-y-6">
        <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Settings className="w-4 h-4 text-indigo-500" />
          Enterprise Configuration & Governance Policies
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
          {/* Company & Host */}
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 space-y-3">
            <h4 className="font-bold text-slate-800 flex items-center gap-2">
              <Bot className="w-4 h-4 text-indigo-600" />
              Company Workspace
            </h4>
            <div className="space-y-1.5 text-slate-600">
              <div>• Company: <strong>Harmage Agents Virtual Enterprise</strong></div>
              <div>• Host Environment: <strong>Windows (Native Laptop VPS)</strong></div>
              <div>• Local Workspace: <code>E:\AI Agent</code></div>
              <div>• Operational Database: <code>harmage/data/harmage_operations.db</code></div>
            </div>
          </div>

          {/* CEO & Telegram */}
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 space-y-3">
            <h4 className="font-bold text-slate-800 flex items-center gap-2">
              <User className="w-4 h-4 text-purple-600" />
              CEO / Owner Supervisor
            </h4>
            <div className="space-y-1.5 text-slate-600">
              <div>• CEO: <strong>Gentha</strong></div>
              <div>• Telegram User ID: <code>8116783065</code></div>
              <div>• Gateway Bot: <code>@weelsz_bot</code> (Running PID 4020)</div>
              <div>• Authority Level: <strong>Full Governance Veto & Sign-Off</strong></div>
            </div>
          </div>

          {/* Governance Enforcer */}
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 space-y-3 md:col-span-2">
            <h4 className="font-bold text-slate-800 flex items-center gap-2">
              <Shield className="w-4 h-4 text-emerald-600" />
              Governance & Operational Safety Policies
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
              <div className="bg-white p-3 rounded-xl border border-slate-200">
                <span className="font-bold text-slate-800 block">Zero-Dollar Policy</span>
                <span className="text-[11px] text-emerald-600 font-semibold">Strictly Active</span>
                <p className="text-[10px] text-slate-400 mt-1">Blocks any paid cloud API without prior human sign-off.</p>
              </div>

              <div className="bg-white p-3 rounded-xl border border-slate-200">
                <span className="font-bold text-slate-800 block">Public Publishing Gate</span>
                <span className="text-[11px] text-emerald-600 font-semibold">Draft Mode Only</span>
                <p className="text-[10px] text-slate-400 mt-1">All TikTok and YouTube uploads staged as draft until CEO approved.</p>
              </div>

              <div className="bg-white p-3 rounded-xl border border-slate-200">
                <span className="font-bold text-slate-800 block">Paper Trading Policy</span>
                <span className="text-[11px] text-emerald-600 font-semibold">Simulation Locked</span>
                <p className="text-[10px] text-slate-400 mt-1">Zero real money or external order routing permitted.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
