/* ==========================================================================
   Harmage Agents — SaaS Administrative Dashboard Client Logic
   ========================================================================== */

const API_BASE = window.location.origin;

// State Cache
let AppState = {
  activeSection: "overview",
  overview: null,
  npcs: [],
  tasks: [],
  schedules: [],
  approvals: [],
  meetings: [],
  reports: [],
  activities: [],
  integrations: null,
  taskViewMode: "kanban", // or 'list'
  scheduleViewMode: "calendar" // or 'list'
};

// DOM Content Loaded
document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  initModals();
  fetchAllData();
  
  // Auto-refresh every 12 seconds
  setInterval(fetchAllData, 12000);
});

// --- Navigation Handling ---
function initNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  navItems.forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const section = item.getAttribute("data-section");
      switchSection(section);
    });
  });

  // Top refresh button
  document.getElementById("btn-refresh")?.addEventListener("click", () => {
    fetchAllData();
  });

  // Task view toggle
  document.getElementById("btn-view-kanban")?.addEventListener("click", () => setTaskView("kanban"));
  document.getElementById("btn-view-list")?.addEventListener("click", () => setTaskView("list"));

  // Schedule heartbeat trigger
  document.getElementById("btn-trigger-heartbeat")?.addEventListener("click", triggerHeartbeat);

  // Trigger Creator Video Production
  document.getElementById("btn-trigger-production")?.addEventListener("click", triggerCreatorPipeline);
}

function switchSection(sectionId) {
  AppState.activeSection = sectionId;

  // Update nav items
  document.querySelectorAll(".nav-item").forEach(item => {
    if (item.getAttribute("data-section") === sectionId) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });

  // Update page title
  const titleMap = {
    overview: "Operational Overview",
    organization: "Company Organization & 2D NPC Roster",
    divisions: "Business Divisions & Workflows",
    tasks: "Task & Project Management",
    schedule: "Operational Schedule & Calendars",
    meetings: "Internal Meeting Records",
    reports: "Executive Briefings & Audits",
    integrations: "Infrastructure & Tool Integrations",
    activity: "Audit Trail & Activity Logs",
    approvals: "CEO Governance Approval Gate",
    settings: "System & LLM Stack Settings"
  };
  const titleEl = document.getElementById("current-page-title");
  if (titleEl) titleEl.innerText = titleMap[sectionId] || "Dashboard";

  // Show section container
  document.querySelectorAll(".content-section").forEach(sec => {
    if (sec.id === `section-${sectionId}`) {
      sec.classList.add("active");
    } else {
      sec.classList.remove("active");
    }
  });
}

// --- Data Fetching ---
async function fetchAllData() {
  try {
    const [ov, npcs, tasks, sched, apprv, mtg, rep, act, integ] = await Promise.all([
      fetch(`${API_BASE}/api/overview`).then(r => r.json()),
      fetch(`${API_BASE}/api/npcs`).then(r => r.json()),
      fetch(`${API_BASE}/api/tasks`).then(r => r.json()),
      fetch(`${API_BASE}/api/schedules`).then(r => r.json()),
      fetch(`${API_BASE}/api/approvals`).then(r => r.json()),
      fetch(`${API_BASE}/api/meetings`).then(r => r.json()),
      fetch(`${API_BASE}/api/reports`).then(r => r.json()),
      fetch(`${API_BASE}/api/activity`).then(r => r.json()),
      fetch(`${API_BASE}/api/integrations/status`).then(r => r.json())
    ]);

    AppState.overview = ov;
    AppState.npcs = npcs;
    AppState.tasks = tasks;
    AppState.schedules = sched;
    AppState.approvals = apprv;
    AppState.meetings = mtg;
    AppState.reports = rep;
    AppState.activities = act;
    AppState.integrations = integ;

    renderOverview();
    renderNPCs();
    renderTasks();
    renderSchedules();
    renderApprovals();
    renderMeetings();
    renderReports();
    renderActivity();
    renderIntegrations();
    updateBadges();
  } catch (err) {
    console.error("Error fetching Harmage dashboard data:", err);
  }
}

// --- Renderers ---

function updateBadges() {
  const pendingCount = AppState.approvals.filter(a => a.status === "pending").length;
  const badgeApprv = document.getElementById("badge-approvals");
  if (badgeApprv) {
    badgeApprv.innerText = pendingCount;
    badgeApprv.style.display = pendingCount > 0 ? "inline-block" : "none";
  }

  const badgeTasks = document.getElementById("badge-tasks");
  if (badgeTasks) {
    const activeTasks = AppState.tasks.filter(t => t.status === "in_progress" || t.status === "queued").length;
    badgeTasks.innerText = activeTasks;
  }
}

function renderOverview() {
  const ov = AppState.overview;
  if (!ov) return;

  document.getElementById("kpi-active-tasks").innerText = ov.total_tasks || 0;
  document.getElementById("kpi-pending-approvals").innerText = ov.pending_approvals || 0;
  document.getElementById("kpi-active-npcs").innerText = `${ov.active_npcs || 12} / 12`;
  document.getElementById("kpi-budget-spent").innerText = `$${ov.budget_spent_usd.toFixed(2)}`;

  // Recent ticker
  const ticker = document.getElementById("overview-recent-activity");
  if (ticker && ov.recent_activities) {
    ticker.innerHTML = ov.recent_activities.map(log => `
      <div class="log-entry ${log.level}">
        <span style="color: #64748b; font-size: 10px;">${formatTime(log.created_at)}</span>
        <strong style="color: #0f172a;">[${log.actor}]</strong>
        <span>${escapeHtml(log.action)}</span>
        ${log.details ? `<span style="color: #64748b; font-size: 10px;">— ${escapeHtml(log.details)}</span>` : ''}
      </div>
    `).join("");
  }
}

function renderNPCs() {
  const container = document.getElementById("npc-roster-grid");
  if (!container) return;

  container.innerHTML = AppState.npcs.map(npc => `
    <div class="npc-card" onclick="openNPCModal('${npc.id}')">
      <div class="npc-header">
        <div class="npc-avatar-box">
          ${npc.avatar_svg}
        </div>
        <div class="npc-meta">
          <div class="npc-name">${escapeHtml(npc.name)}</div>
          <div class="npc-role">${escapeHtml(npc.role_title)}</div>
          <span class="npc-division-pill">${escapeHtml(npc.division)}</span>
        </div>
      </div>
      <div class="npc-traits">
        ${npc.personality_traits.map(t => `<span class="trait-tag">${escapeHtml(t)}</span>`).join("")}
      </div>
      <div class="npc-footer">
        <span>Status: <strong style="color: ${npc.status === 'in_progress' ? '#0284c7' : '#059669'};">${npc.status.toUpperCase()}</strong></span>
        <span>Tools: ${npc.allowed_tools.length}</span>
      </div>
    </div>
  `).join("");
}

function renderTasks() {
  if (AppState.taskViewMode === "kanban") {
    renderKanban();
  } else {
    renderTaskList();
  }
}

function setTaskView(mode) {
  AppState.taskViewMode = mode;
  document.getElementById("kanban-container").style.display = mode === "kanban" ? "grid" : "none";
  document.getElementById("task-list-container").style.display = mode === "list" ? "block" : "none";
  document.getElementById("btn-view-kanban").className = mode === "kanban" ? "btn btn-primary" : "btn btn-secondary";
  document.getElementById("btn-view-list").className = mode === "list" ? "btn btn-primary" : "btn btn-secondary";
  renderTasks();
}

function renderKanban() {
  const cols = {
    queued: document.getElementById("col-queued"),
    in_progress: document.getElementById("col-in_progress"),
    blocked: document.getElementById("col-blocked"),
    review: document.getElementById("col-review"),
    completed: document.getElementById("col-completed")
  };

  // Reset columns
  Object.keys(cols).forEach(k => {
    if (cols[k]) cols[k].innerHTML = "";
  });

  AppState.tasks.forEach(task => {
    const col = cols[task.status] || cols["queued"];
    if (!col) return;

    const card = document.createElement("div");
    card.className = "kanban-card";
    card.onclick = () => openTaskModal(task.id);
    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span class="badge badge-prio-${task.priority}">${task.priority}</span>
        <span style="font-size: 10px; color: #64748b;">${task.id}</span>
      </div>
      <div class="kanban-card-title">${escapeHtml(task.title)}</div>
      <div class="kanban-card-meta">
        <span>👤 ${escapeHtml(task.assignee)}</span>
        ${task.retry_count > 0 ? `<span>🔄 ${task.retry_count}/${task.max_retries}</span>` : ''}
      </div>
    `;
    col.appendChild(card);
  });

  // Update column counters
  Object.keys(cols).forEach(k => {
    const cntEl = document.getElementById(`cnt-${k}`);
    if (cntEl && cols[k]) {
      cntEl.innerText = cols[k].children.length;
    }
  });
}

function renderTaskList() {
  const tbody = document.getElementById("task-table-body");
  if (!tbody) return;

  tbody.innerHTML = AppState.tasks.map(t => `
    <tr onclick="openTaskModal('${t.id}')" style="cursor: pointer;">
      <td><code>${t.id}</code></td>
      <td><strong>${escapeHtml(t.title)}</strong></td>
      <td>${escapeHtml(t.assignee)}</td>
      <td><span class="badge badge-prio-${t.priority}">${t.priority}</span></td>
      <td><span class="badge badge-${t.status}">${t.status}</span></td>
      <td>${t.deadline ? formatTime(t.deadline) : '—'}</td>
      <td>${t.retry_count} / ${t.max_retries}</td>
    </tr>
  `).join("");
}

function renderSchedules() {
  const container = document.getElementById("schedule-grid-body");
  if (!container) return;

  container.innerHTML = AppState.schedules.map(s => `
    <tr>
      <td><strong>${escapeHtml(s.title)}</strong></td>
      <td><code>${escapeHtml(s.cron_expr || s.interval_type)}</code></td>
      <td>👤 ${escapeHtml(s.target_role)}</td>
      <td><code>${escapeHtml(s.action)}</code></td>
      <td>${formatTime(s.next_run)}</td>
      <td>${s.last_run ? formatTime(s.last_run) : 'Never'}</td>
      <td>
        <span class="badge ${s.enabled ? 'badge-completed' : 'badge-queued'}">${s.enabled ? 'ACTIVE' : 'PAUSED'}</span>
      </td>
      <td>
        <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="toggleSchedule('${s.id}', ${s.enabled ? 0 : 1})">
          ${s.enabled ? 'Pause' : 'Resume'}
        </button>
      </td>
    </tr>
  `).join("");
}

function renderApprovals() {
  const tbody = document.getElementById("approvals-table-body");
  if (!tbody) return;

  if (AppState.approvals.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: #94a3b8; padding: 24px;">No governance requests pending.</td></tr>`;
    return;
  }

  tbody.innerHTML = AppState.approvals.map(a => `
    <tr>
      <td><code>${a.id}</code></td>
      <td><strong style="color: #0284c7;">${escapeHtml(a.action_type)}</strong></td>
      <td>${escapeHtml(a.description)}</td>
      <td>👤 ${escapeHtml(a.requested_by)}</td>
      <td>
        <span class="badge ${a.status === 'pending' ? 'badge-review' : (a.status === 'approved' ? 'badge-completed' : 'badge-failed')}">
          ${a.status.toUpperCase()}
        </span>
      </td>
      <td>
        ${a.status === 'pending' ? `
          <div style="display: flex; gap: 6px;">
            <button class="btn btn-success" style="padding: 4px 8px; font-size: 10px;" onclick="resolveApproval('${a.id}', 'approved')">✓ Approve</button>
            <button class="btn btn-danger" style="padding: 4px 8px; font-size: 10px;" onclick="resolveApproval('${a.id}', 'rejected')">✕ Reject</button>
          </div>
        ` : `<span style="font-size: 11px; color: #64748b;">${escapeHtml(a.ceo_notes || 'Resolved')}</span>`}
      </td>
    </tr>
  `).join("");
}

function renderMeetings() {
  const container = document.getElementById("meetings-list");
  if (!container) return;

  container.innerHTML = AppState.meetings.map(m => `
    <div class="surface-panel" style="margin-bottom: 14px;">
      <div class="panel-header">
        <div class="panel-title">
          <span>📅 ${escapeHtml(m.title)}</span>
          <span class="badge badge-queued">${m.meeting_type}</span>
        </div>
        <span style="font-size: 11px; color: #64748b;">${formatTime(m.created_at)}</span>
      </div>
      <div class="panel-body" style="display: flex; flex-direction: column; gap: 10px; font-size: 12px;">
        <div><strong>Agenda:</strong> ${escapeHtml(m.agenda)}</div>
        <div><strong>Participants:</strong> ${m.participants.map(p => `<span class="trait-tag">👤 ${p}</span>`).join(" ")}</div>
        ${m.discussion ? `<div style="background: #f8fafc; padding: 10px; border-radius: 6px; border-left: 3px solid #0284c7;">${escapeHtml(m.discussion)}</div>` : ''}
        ${m.action_items && m.action_items.length > 0 ? `
          <div>
            <strong>Action Items:</strong>
            <ul style="padding-left: 20px; margin-top: 4px;">
              ${m.action_items.map(ai => `<li>${escapeHtml(ai)}</li>`).join("")}
            </ul>
          </div>
        ` : ''}
      </div>
    </div>
  `).join("");
}

function renderReports() {
  const container = document.getElementById("reports-container");
  if (!container) return;

  container.innerHTML = AppState.reports.map(r => `
    <div class="surface-panel" style="margin-bottom: 16px;">
      <div class="panel-header">
        <div class="panel-title">
          <span>📊 ${escapeHtml(r.title)}</span>
          <span class="badge badge-completed">${r.report_type}</span>
        </div>
        <span style="font-size: 11px; color: #64748b;">${formatTime(r.created_at)}</span>
      </div>
      <div class="panel-body" style="font-size: 13px; line-height: 1.6;">
        <p style="font-weight: 600; margin-bottom: 12px; color: #0284c7;">${escapeHtml(r.summary)}</p>
        <pre style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px; font-family: var(--font-mono); font-size: 11px; overflow-x: auto; white-space: pre-wrap;">${escapeHtml(r.content_markdown)}</pre>
      </div>
    </div>
  `).join("");
}

function renderActivity() {
  const container = document.getElementById("full-activity-stream");
  if (!container) return;

  container.innerHTML = AppState.activities.map(log => `
    <div class="log-entry ${log.level}">
      <span style="color: #64748b; font-size: 10px; width: 80px; flex-shrink: 0;">${formatTime(log.created_at)}</span>
      <span class="badge ${log.level === 'GOVERNANCE' ? 'badge-completed' : (log.level === 'ERROR' ? 'badge-failed' : 'badge-queued')}" style="font-size: 9px;">${log.level}</span>
      <strong style="color: #0f172a; min-width: 120px;">👤 ${escapeHtml(log.actor)}</strong>
      <span style="flex-grow: 1;">${escapeHtml(log.action)}</span>
      ${log.details ? `<span style="color: #64748b; font-size: 10px;">${escapeHtml(log.details)}</span>` : ''}
    </div>
  `).join("");
}

function renderIntegrations() {
  const integ = AppState.integrations;
  if (!integ) return;

  // Ports
  const pList = document.getElementById("integ-ports-list");
  if (pList) {
    pList.innerHTML = Object.entries(integ.ports).map(([name, data]) => `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f1f5f9;">
        <div>
          <strong>${escapeHtml(name)}</strong>
          <div style="font-size: 11px; color: #64748b;">${data.url || data.bot || ''}</div>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-family: var(--font-mono); font-size: 11px; background: #f1f5f9; padding: 2px 6px; border-radius: 4px;">Port: ${data.port}</span>
          <span class="badge badge-completed">${data.status}</span>
        </div>
      </div>
    `).join("");
  }

  // Tools
  const tList = document.getElementById("integ-tools-list");
  if (tList) {
    tList.innerHTML = Object.entries(integ.tools).map(([tool, info]) => `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f1f5f9;">
        <div>
          <strong style="text-transform: uppercase;">${escapeHtml(tool)}</strong>
          <div style="font-size: 10px; color: #64748b; font-family: var(--font-mono);">${info.path || (info.graph_json_nodes ? `${info.graph_json_nodes} nodes indexed` : '')}</div>
        </div>
        <span class="badge ${info.installed ? 'badge-completed' : 'badge-failed'}">${info.installed ? 'VERIFIED ACTIVE' : 'MISSING'}</span>
      </div>
    `).join("");
  }

  // LLM Stack
  const llmStack = document.getElementById("integ-llm-stack");
  if (llmStack) {
    llmStack.innerHTML = `
      <div style="padding: 8px 12px; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 6px; margin-bottom: 12px; font-size: 12px; color: #065f46;">
        🛡️ <strong>Zero-Cost Enforcement:</strong> ${integ.llm_stack.zero_cost_policy} ($0.00 Budget Cap Active)
      </div>
      <div style="display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
        <div><strong>Primary:</strong> <code>${escapeHtml(integ.llm_stack.primary)}</code></div>
        <div><strong>Fallback 1:</strong> <code>${escapeHtml(integ.llm_stack.fallback_1)}</code></div>
        <div><strong>Fallback 2:</strong> <code>${escapeHtml(integ.llm_stack.fallback_2)}</code></div>
      </div>
    `;
  }
}

// --- Action Handlers ---

async function resolveApproval(approvalId, action) {
  const note = prompt(`Enter CEO decision note for ${action.toUpperCase()}:`, `CEO approved via Harmage Dashboard`);
  if (note === null) return;

  try {
    const res = await fetch(`${API_BASE}/api/approvals/${approvalId}/act`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: action, ceo_notes: note })
    }).then(r => r.json());

    if (res.success) {
      alert(`Approval ${approvalId} successfully ${action.toUpperCase()}`);
      fetchAllData();
    }
  } catch (err) {
    alert("Error updating approval: " + err);
  }
}

async function toggleSchedule(scheduleId, enable) {
  try {
    const res = await fetch(`${API_BASE}/api/schedules/${scheduleId}/toggle`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: Boolean(enable) })
    }).then(r => r.json());

    if (res.success) {
      fetchAllData();
    }
  } catch (err) {
    alert("Error toggling schedule: " + err);
  }
}

async function triggerHeartbeat() {
  const btn = document.getElementById("btn-trigger-heartbeat");
  if (btn) btn.innerText = "Checking...";
  try {
    const res = await fetch(`${API_BASE}/api/schedules/heartbeat`, { method: "POST" }).then(r => r.json());
    alert(`Operational Heartbeat Executed! Due items: ${res.due_count}`);
    fetchAllData();
  } catch (err) {
    alert("Heartbeat failed: " + err);
  } finally {
    if (btn) btn.innerText = "⚡ Trigger Heartbeat";
  }
}

async function triggerCreatorPipeline() {
  const btn = document.getElementById("btn-trigger-production");
  if (btn) btn.innerText = "Producing Video...";
  try {
    const res = await fetch(`${API_BASE}/api/creator/produce`, { method: "POST" }).then(r => r.json());
    alert(`Video Production Pipeline Finished!\nTask: ${res.task_id}\nVideo: ${res.rendered_video}\nQA: ${res.qa_status}\nDraft Staged: ${res.tiktok_draft?.status || 'Held for CEO Approval'}`);
    fetchAllData();
  } catch (err) {
    alert("Production failed: " + err);
  } finally {
    if (btn) btn.innerText = "🎬 Produce Video Now";
  }
}

// --- Modals ---
function initModals() {
  // Close buttons
  document.querySelectorAll(".modal-close, .modal-cancel").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".modal-overlay").forEach(m => m.classList.remove("open"));
    });
  });

  // Open Task Create Modal
  document.getElementById("btn-new-task")?.addEventListener("click", () => {
    document.getElementById("modal-create-task").classList.add("open");
  });

  // Task form submit
  document.getElementById("form-create-task")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      title: document.getElementById("task-input-title").value,
      description: document.getElementById("task-input-desc").value,
      assignee: document.getElementById("task-input-assignee").value,
      priority: document.getElementById("task-input-priority").value,
      deadline: document.getElementById("task-input-deadline").value || null
    };

    try {
      const res = await fetch(`${API_BASE}/api/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }).then(r => r.json());

      if (res.success) {
        document.getElementById("modal-create-task").classList.remove("open");
        document.getElementById("form-create-task").reset();
        fetchAllData();
      }
    } catch (err) {
      alert("Failed creating task: " + err);
    }
  });
}

function openNPCModal(npcId) {
  const npc = AppState.npcs.find(n => n.id === npcId);
  if (!npc) return;

  document.getElementById("npc-modal-title").innerText = `${npc.name} (${npc.role_title})`;
  document.getElementById("npc-modal-avatar").innerHTML = npc.avatar_svg;
  document.getElementById("npc-modal-division").innerText = npc.division;
  document.getElementById("npc-modal-traits").innerHTML = npc.personality_traits.map(t => `<span class="trait-tag">${t}</span>`).join(" ");
  document.getElementById("npc-modal-tone").innerText = npc.tone_of_voice;
  document.getElementById("npc-modal-competencies").innerHTML = npc.competencies.map(c => `<li>${c}</li>`).join("");
  document.getElementById("npc-modal-tools").innerHTML = npc.allowed_tools.map(t => `<code>${t}</code>`).join(" ");
  document.getElementById("npc-modal-prompt").innerText = npc.system_prompt;

  document.getElementById("modal-npc-detail").classList.add("open");
}

function openTaskModal(taskId) {
  const task = AppState.tasks.find(t => t.id === taskId);
  if (!task) return;

  document.getElementById("task-detail-id").innerText = task.id;
  document.getElementById("task-detail-title").innerText = task.title;
  document.getElementById("task-detail-desc").innerText = task.description || "No description provided.";
  document.getElementById("task-detail-assignee").innerText = task.assignee;
  document.getElementById("task-detail-priority").innerText = task.priority;
  document.getElementById("task-detail-status").innerText = task.status;
  document.getElementById("task-detail-retries").innerText = `${task.retry_count} / ${task.max_retries}`;
  document.getElementById("task-detail-evidence").innerText = task.evidence || "No evidence recorded yet.";

  document.getElementById("modal-task-detail").classList.add("open");
}

// --- Helpers ---
function formatTime(isoStr) {
  if (!isoStr) return "";
  try {
    const d = new Date(isoStr);
    return d.toLocaleString("id-ID", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  } catch (e) {
    return isoStr;
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
