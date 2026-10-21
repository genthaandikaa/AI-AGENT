import React, { useState } from 'react';
import { 
  LayoutDashboard, 
  Layers, 
  GitMerge, 
  CheckSquare, 
  Calendar,
  Users,
  FileText,
  ShieldCheck,
  Activity,
  Cpu, 
  Settings,
  ChevronLeft,
  ChevronRight,
  Bot
} from 'lucide-react';
import { NavSection } from '../types';

interface SidebarProps {
  activeSection: NavSection;
  onSelectSection: (section: NavSection) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  pendingApprovalsCount?: number;
}

interface NavGroup {
  title: string;
  items: {
    id: NavSection;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    badge?: number;
  }[];
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  activeSection, 
  onSelectSection,
  isCollapsed,
  onToggleCollapse,
  pendingApprovalsCount = 0
}) => {
  const [isHovered, setIsHovered] = useState(false);

  // Grouped Navigation structure by Function & Title
  const navGroups: NavGroup[] = [
    {
      title: 'UTAMA',
      items: [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'overview', label: 'Overview', icon: Layers },
        { id: 'divisions', label: 'Divisions', icon: GitMerge },
      ]
    },
    {
      title: 'OPERASIONAL',
      items: [
        { id: 'tasks', label: 'Tasks & Projects', icon: CheckSquare },
        { id: 'schedule', label: 'Schedule', icon: Calendar },
        { id: 'meetings', label: 'Meetings', icon: Users },
        { id: 'reports', label: 'Reports', icon: FileText },
      ]
    },
    {
      title: 'TATA KELOLA',
      items: [
        { id: 'approvals', label: 'Approvals', icon: ShieldCheck, badge: pendingApprovalsCount },
        { id: 'activity', label: 'Activity Logs', icon: Activity },
      ]
    },
    {
      title: 'SISTEM',
      items: [
        { id: 'integrations', label: 'Integrations', icon: Cpu },
        { id: 'settings', label: 'Settings', icon: Settings },
      ]
    }
  ];

  const isExpanded = !isCollapsed || isHovered;

  return (
    <aside 
      onMouseEnter={() => isCollapsed && setIsHovered(true)}
      onMouseLeave={() => isCollapsed && setIsHovered(false)}
      className={`fixed top-0 left-0 bottom-0 z-40 bg-white border-r border-purple-100 flex flex-col justify-between py-5 select-none transition-all duration-300 ease-in-out shadow-xs ${
        isExpanded ? 'w-64 px-4 shadow-xl' : 'w-[72px] px-2.5'
      }`}
    >
      {/* Top Section: Brand & Toggle */}
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-10 h-10 rounded-2xl bg-purple-600 flex items-center justify-center text-white shadow-md shadow-purple-500/25 flex-shrink-0">
              <Bot className="w-5 h-5" />
            </div>
            {isExpanded && (
              <div className="truncate animate-fadeIn">
                <h1 className="text-slate-900 font-bold text-sm tracking-wide flex items-center gap-1.5">
                  HARMAGE <span className="text-[9px] bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded-full font-bold">AI</span>
                </h1>
                <p className="text-[10px] text-purple-600/70 font-semibold">Autonomous Company</p>
              </div>
            )}
          </div>

          {/* Minimize / Expand Toggle */}
          {isExpanded && (
            <button 
              onClick={onToggleCollapse}
              title={isCollapsed ? "Kunci Sidebar Terbuka" : "Kecilkan Sidebar"}
              className="p-1.5 rounded-xl hover:bg-purple-50 text-slate-400 hover:text-purple-600 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
          )}
        </div>

        {!isExpanded && (
          <div className="flex justify-center -mt-2">
            <button 
              onClick={onToggleCollapse}
              title="Perlebar Sidebar"
              className="p-1.5 rounded-xl hover:bg-purple-50 text-slate-400 hover:text-purple-600 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Categorized Navigation Menu */}
        <nav className="space-y-4 overflow-y-auto max-h-[calc(100vh-230px)] scrollbar-none pr-0.5">
          {navGroups.map((group, gIdx) => (
            <div key={gIdx} className="space-y-1">
              {/* Category Group Header */}
              {isExpanded && (
                <div className="px-3 pt-1 pb-1">
                  <span className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">
                    {group.title}
                  </span>
                </div>
              )}

              {/* Items in this group */}
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeSection === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => onSelectSection(item.id)}
                    title={!isExpanded ? item.label : undefined}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold transition-all duration-150 ${
                      isActive 
                        ? 'bg-purple-600 text-white shadow-md shadow-purple-500/20' 
                        : 'text-slate-600 hover:text-purple-700 hover:bg-purple-50/80'
                    } ${!isExpanded ? 'justify-center py-2.5' : ''}`}
                  >
                    <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-purple-600'}`} />
                    
                    {isExpanded && (
                      <span className="truncate flex-1 text-left">{item.label}</span>
                    )}

                    {isExpanded && item.badge !== undefined && item.badge > 0 && (
                      <span className="ml-auto text-[10px] font-bold bg-rose-500 text-white px-2 py-0.5 rounded-full">
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          ))}
        </nav>
      </div>

      {/* Bottom Profile / Owner info */}
      <div className="pt-3 border-t border-purple-100/70">
        {isExpanded ? (
          <div className="flex items-center gap-2.5 p-2 rounded-2xl bg-purple-50/50 border border-purple-100">
            <div className="w-8 h-8 rounded-xl bg-purple-600 text-white font-bold flex items-center justify-center text-xs flex-shrink-0 shadow-sm">
              G
            </div>
            <div className="truncate flex-1">
              <p className="text-xs font-bold text-slate-800 truncate">Gentha</p>
              <p className="text-[10px] text-purple-600 font-semibold">CEO / Owner</p>
            </div>
            <span className="w-2 h-2 rounded-full bg-emerald-500" title="Online"></span>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-purple-600 text-white font-bold flex items-center justify-center text-xs shadow-sm" title="Gentha (CEO / Owner)">
              G
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};
