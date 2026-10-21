import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { TopHeader } from './components/TopHeader';

// 11 Core Views matching user specifications
import { DashboardView } from './views/DashboardView';
import { OverviewView } from './views/OverviewView';
import { DivisionsView } from './views/DivisionsView';
import { TasksView } from './views/TasksView';
import { ScheduleView } from './views/ScheduleView';
import { MeetingsView } from './views/MeetingsView';
import { ReportsView } from './views/ReportsView';
import { IntegrationsView } from './views/IntegrationsView';
import { ActivityView } from './views/ActivityView';
import { ApprovalsView } from './views/ApprovalsView';
import { SettingsView } from './views/SettingsView';

import { AgentDetailModal } from './components/AgentDetailModal';
import { NewTaskModal } from './components/NewTaskModal';
import { NavSection, Agent, TaskItem, ActivityItem } from './types';

export const App: React.FC = () => {
  // First item is Dashboard
  const [activeSection, setActiveSection] = useState<NavSection>('dashboard');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);

  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [integrations, setIntegrations] = useState<any>(null);
  const [pendingApprovalsCount, setPendingApprovalsCount] = useState<number>(0);

  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [selectedTask, setSelectedTask] = useState<TaskItem | null>(null);
  const [isNewTaskOpen, setIsNewTaskOpen] = useState<boolean>(false);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const fetchData = async () => {
    setIsRefreshing(true);
    try {
      const [npcsRes, tasksRes, actRes, integRes, overviewRes] = await Promise.all([
        fetch('/api/npcs').then(r => r.json()).catch(() => []),
        fetch('/api/tasks').then(r => r.json()).catch(() => []),
        fetch('/api/activity').then(r => r.json()).catch(() => []),
        fetch('/api/integrations/status').then(r => r.json()).catch(() => null),
        fetch('/api/overview').then(r => r.json()).catch(() => null)
      ]);

      if (Array.isArray(npcsRes) && npcsRes.length > 0) {
        setAgents(npcsRes);
      }
      if (Array.isArray(tasksRes)) {
        setTasks(tasksRes);
      }
      if (Array.isArray(actRes)) {
        setActivities(actRes);
      }
      if (integRes) {
        setIntegrations(integRes);
      }
      if (overviewRes && typeof overviewRes.pending_approvals === 'number') {
        setPendingApprovalsCount(overviewRes.pending_approvals);
      }
    } catch (err) {
      console.error('Error fetching dashboard state:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 8000);
    return () => clearInterval(interval);
  }, []);

  const getSectionTitle = () => {
    switch (activeSection) {
      case 'dashboard':
        return { 
          title: 'Harmage Dashboard', 
          subtitle: 'Ringkasan operasional bisnis, KPI inti, dan live agent chat.' 
        };
      case 'overview':
        return { 
          title: 'Hermes 3D Virtual Office', 
          subtitle: 'Eksplorasi kantor 3D interaktif native Hermes dan status AI workforce.' 
        };
      case 'divisions':
        return { 
          title: 'Divisi Bisnis & Kreator', 
          subtitle: 'Pusat pengelolaan unit operasional video, affiliate, dan evaluasi.' 
        };
      case 'tasks':
        return { 
          title: 'Tasks & Projects', 
          subtitle: 'Manajemen pekerjaan, papan Kanban, dan auto-retry tracking.' 
        };
      case 'schedule':
        return { 
          title: 'Schedule & Automation', 
          subtitle: 'Jadwal otomatis SQLite dan heartbeat executor.' 
        };
      case 'meetings':
        return { 
          title: 'Meetings & Standup', 
          subtitle: 'Arsip agenda, transkrip notulensi Sophia Chen, dan tindak lanjut.' 
        };
      case 'reports':
        return { 
          title: 'Reports & Evaluations', 
          subtitle: 'Laporan harian PIC Divisi Diana Prince & Bendahara Marcus Drake.' 
        };
      case 'integrations':
        return { 
          title: 'Integrations & Tools', 
          subtitle: 'Konektivitas MCP, model provider, Telegram gateway, dan status $0 budget.' 
        };
      case 'activity':
        return { 
          title: 'Activity Logs', 
          subtitle: 'Audit trail kronologis seluruh aksi AI dan event sistem.' 
        };
      case 'approvals':
        return { 
          title: 'CEO Governance Approvals', 
          subtitle: 'Pintu persetujuan keputusan dan anggaran oleh CEO.' 
        };
      case 'settings':
        return { 
          title: 'Settings & Policies', 
          subtitle: 'Konfigurasi tata kelola dan penegakan $0 budget.' 
        };
      default:
        return { 
          title: 'Harmage Agents Platform', 
          subtitle: 'Autonomous AI Enterprise' 
        };
    }
  };

  const headerInfo = getSectionTitle();

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#faf8ff]">
      {/* 1. Categorized & Spaced Sidebar (White & Purple, Non-scrolling, Flush) */}
      <Sidebar 
        activeSection={activeSection} 
        onSelectSection={(sec) => setActiveSection(sec)}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(prev => !prev)}
        pendingApprovalsCount={pendingApprovalsCount}
      />

      {/* 2. Main Canvas Offset by Sidebar Width */}
      <div 
        className={`flex-1 flex flex-col h-screen overflow-hidden transition-all duration-300 ease-in-out ${
          isSidebarCollapsed ? 'ml-[72px]' : 'ml-64'
        }`}
      >
        {/* FIXED TopHeader (Does NOT scroll) */}
        <header className="flex-shrink-0 bg-white/95 backdrop-blur-md border-b border-purple-100/90 px-6 py-3.5 z-20 shadow-xs">
          <TopHeader 
            title={headerInfo.title}
            subtitle={headerInfo.subtitle}
            onOpenNewTask={() => setIsNewTaskOpen(true)}
            onRefresh={fetchData}
            isRefreshing={isRefreshing}
          />
        </header>

        {/* Scrollable View Container (Only content scrolls) */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#faf8ff]">
          {activeSection === 'dashboard' && (
            <DashboardView 
              agents={agents} 
              tasks={tasks}
              activities={activities}
              onSelectTask={(t) => setSelectedTask(t)}
              onNavigate={(sec) => setActiveSection(sec)}
              onOpenNewTask={() => setIsNewTaskOpen(true)}
            />
          )}

          {activeSection === 'overview' && (
            <OverviewView 
              agents={agents} 
              onSelectAgent={(a) => setSelectedAgent(a)} 
            />
          )}

          {activeSection === 'divisions' && (
            <DivisionsView />
          )}

          {activeSection === 'tasks' && (
            <TasksView 
              tasks={tasks}
              onSelectTask={(t) => setSelectedTask(t)}
              onOpenNewTask={() => setIsNewTaskOpen(true)}
              onRefresh={fetchData}
            />
          )}

          {activeSection === 'schedule' && (
            <ScheduleView />
          )}

          {activeSection === 'meetings' && (
            <MeetingsView />
          )}

          {activeSection === 'reports' && (
            <ReportsView />
          )}

          {activeSection === 'integrations' && (
            <IntegrationsView integrations={integrations} />
          )}

          {activeSection === 'activity' && (
            <ActivityView 
              activities={activities}
              onRefresh={fetchData}
              isRefreshing={isRefreshing}
            />
          )}

          {activeSection === 'approvals' && (
            <ApprovalsView />
          )}

          {activeSection === 'settings' && (
            <SettingsView />
          )}
        </main>
      </div>

      {/* Modals */}
      <AgentDetailModal 
        agent={selectedAgent} 
        onClose={() => setSelectedAgent(null)} 
      />

      <NewTaskModal 
        isOpen={isNewTaskOpen} 
        onClose={() => setIsNewTaskOpen(false)}
        agents={agents}
        onTaskCreated={fetchData}
      />
    </div>
  );
};

export default App;
