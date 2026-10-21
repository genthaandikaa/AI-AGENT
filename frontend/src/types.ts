export type NavSection = 
  | 'overview' 
  | 'dashboard' 
  | 'divisions' 
  | 'tasks' 
  | 'schedule' 
  | 'meetings' 
  | 'reports' 
  | 'integrations' 
  | 'activity' 
  | 'approvals' 
  | 'settings';

export interface Agent {
  id: string;
  name: string;
  role_title: string;
  division: string;
  status: 'online' | 'busy' | 'idle' | 'in_meeting' | 'off_duty';
  personality_traits: string[];
  tone_of_voice: string;
  system_prompt: string;
  competencies: string[];
  allowed_tools: string[];
  avatar_color: string;
  avatar_accent: string;
  avatar_svg?: string;
  tasks_count: number;
  success_rate: number;
}

export interface TaskItem {
  id: string;
  title: string;
  description?: string;
  assignee: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'queued' | 'in_progress' | 'blocked' | 'review' | 'completed' | 'failed';
  deadline?: string;
  retry_count: number;
  max_retries: number;
  evidence?: string;
}

export interface WorkflowItem {
  id: string;
  name: string;
  progress: number;
  status: string;
  color: string;
}

export interface ActivityItem {
  id: number | string;
  level: string;
  actor: string;
  action: string;
  details?: string;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  agent_name?: string;
  text: string;
  timestamp: string;
  summary_card?: {
    title: string;
    date: string;
    completed: number;
    success_rate: string;
  };
}
