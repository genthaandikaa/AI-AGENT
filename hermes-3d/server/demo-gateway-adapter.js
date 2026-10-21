"use strict";

const http = require("http");
const fs = require("fs");
const path = require("path");
const { randomUUID } = require("crypto");
const { WebSocketServer } = require("ws");

const ADAPTER_PORT = parseInt(process.env.DEMO_ADAPTER_PORT || "18789", 10);
const MAIN_KEY = "main";
const MODELS = [{ id: "qwen/qwen3.8-max:free", name: "Qwen 3.8 Max (Harmage Brain)", provider: "xkiro" }];

const agents = new Map([
  ["executive_manager", { id: "executive_manager", name: "Alex Vance", role: "Executive Manager & Director of Operations", workspace: "/harmage/executive" }],
  ["treasurer", { id: "treasurer", name: "Marcus Drake", role: "Treasurer & Financial Controller ($0 Hawk)", workspace: "/harmage/treasury" }],
  ["secretary", { id: "secretary", name: "Sophia Chen", role: "Executive Secretary & Notetaker", workspace: "/harmage/secretary" }],
  ["creator_pm", { id: "creator_pm", name: "Diana Prince", role: "PIC Divisi Konten Kreator & Affiliate", workspace: "/harmage/creator" }],
  ["video_editor", { id: "video_editor", name: "Leo Sparks", role: "Editor Shorts (9:16 Vertical Specialist)", workspace: "/harmage/editor-shorts" }],
  ["editor_longform", { id: "editor_longform", name: "Raka Pratama", role: "Editor Panjang (16:9 YouTube Specialist)", workspace: "/harmage/editor-long" }],
  ["scriptwriter", { id: "scriptwriter", name: "Maya Lin", role: "Scriptwriter & Viral Hook Specialist", workspace: "/harmage/scriptwriter" }],
  ["tiktok_affiliate", { id: "tiktok_affiliate", name: "Victor Sterling", role: "Affiliate TikTok Lead (Keranjang Kuning)", workspace: "/harmage/affiliate" }],
  ["qa_sentinel", { id: "qa_sentinel", name: "Zackary Cross", role: "Quality Assurance Sentinel", workspace: "/harmage/qa" }],
  ["researcher", { id: "researcher", name: "Ethan Cole", role: "Content & Market Researcher", workspace: "/harmage/research" }],
]);

// Persistent in-memory files and tasks store
const files = new Map();
const sessionSettings = new Map();
const conversationHistory = new Map();
const activeRuns = new Map();
const activeSendEventFns = new Set();
const BOOT_TIME = Date.now();
const BOOT_ISO = new Date().toISOString();

// Active company tasks representing real Harmage operations
const tasks = [
  {
    id: "kanban:TSK-YT-01",
    title: "Render 9:16 Short: Rahasia Cuan TikTok Affiliate",
    description: "Render vertical short menggunakan FFmpeg lokal dan Cheat Clip PRO engine.",
    status: "working",
    assignedAgentId: "video_editor",
    createdAt: BOOT_ISO,
    updatedAt: BOOT_ISO,
  },
  {
    id: "kanban:TSK-TT-01",
    title: "Script 3-Second Retention Hook: Bahaya Boncos Biaya API",
    description: "Susun naskah viral TikTok dengan hook menohok dan CTA keranjang kuning.",
    status: "working",
    assignedAgentId: "scriptwriter",
    createdAt: BOOT_ISO,
    updatedAt: BOOT_ISO,
  },
  {
    id: "kanban:TSK-TR-01",
    title: "Audit Konsumsi Token LLM & Zero Cost Policy Check",
    description: "Verifikasi penggunaan Qwen + Gemini berada di bawah 2.000.000 token harian ($0 spend).",
    status: "working",
    assignedAgentId: "treasurer",
    createdAt: BOOT_ISO,
    updatedAt: BOOT_ISO,
  },
  {
    id: "kanban:TSK-CP-01",
    title: "Supervisi Alur Kerja Divisi Konten & Affiliate",
    description: "Pastikan target harian 1 video short dan 3 kampanye affiliate berjalan lancar.",
    status: "working",
    assignedAgentId: "creator_pm",
    createdAt: BOOT_ISO,
    updatedAt: BOOT_ISO,
  },
  {
    id: "kanban:TSK-AF-01",
    title: "Riset 5 Produk Keranjang Kuning Viral Komisi >15%",
    description: "Pilih produk trending TikTok Shop dengan tingkat checkout tertinggi.",
    status: "working",
    assignedAgentId: "tiktok_affiliate",
    createdAt: BOOT_ISO,
    updatedAt: BOOT_ISO,
  },
  {
    id: "kanban:TSK-QA-01",
    title: "Inspeksi Kualitas Video Pilot Short (Audio & Typography)",
    description: "Periksa kejelasan subtitle, audio sync, dan bebas copyright strike.",
    status: "working",
    assignedAgentId: "qa_sentinel",
    createdAt: BOOT_ISO,
    updatedAt: BOOT_ISO,
  },
  {
    id: "kanban:TSK-MG-01",
    title: "Jadwalkan Standup Harian Sore Jam 17:00 WIB",
    description: "Evaluasi pekerjaan selesai hari ini dan kirim laporan ke CEO Gentha.",
    status: "working",
    assignedAgentId: "executive_manager",
    createdAt: BOOT_ISO,
    updatedAt: BOOT_ISO,
  },
  {
    id: "kanban:TSK-SC-01",
    title: "Notulensi & Arsip Laporan Rapat Harian Sore",
    description: "Dokumentasikan keputusan rapat dan kirim ringkasan ke Telegram CEO.",
    status: "working",
    assignedAgentId: "secretary",
    createdAt: BOOT_ISO,
    updatedAt: BOOT_ISO,
  },
  {
    id: "kanban:TSK-YT-02",
    title: "Riset Materi Video Panjang: Panduan Autonomous AI Office",
    description: "Kumpulkan bahan dan outline video edukasi 16:9 untuk channel YouTube.",
    status: "working",
    assignedAgentId: "researcher",
    createdAt: BOOT_ISO,
    updatedAt: BOOT_ISO,
  },
  {
    id: "kanban:TSK-LF-01",
    title: "Drafting Timeline Video Panjang YouTube 16:9",
    description: "Susun chapter narasi dan visual b-roll untuk durasi 8-12 menit.",
    status: "working",
    assignedAgentId: "editor_longform",
    createdAt: BOOT_ISO,
    updatedAt: BOOT_ISO,
  }
];

// Initialize rich markdown files for each agent
function initAgentFiles() {
  const agentConfigs = {
    executive_manager: {
      name: "Alex Vance",
      role: "Executive Manager & Director of Operations",
      vibe: "Savage, toxic Gen-Z boss, decisive, anti-gabut, no cap",
      emoji: "👑",
      soul: `Persona: Executive Director Harmage Virtual Enterprise.\nGaya bicara: Savage, toxic ala Gen-Z gaul (bestie, no cap, fr fr, spill, sipaling, kena mental, gabut).\nSuper pintar memimpin perusahaan virtual. Anti lelet, anti gabut.\nTugas utama: menyusun jadwal rapat, mendelegasikan tugas ke PIC divisi konten (Diana Prince) dan bendahara (Marcus Drake), memantau deadline, dan memastikan semua divisi konsisten berkinerja tinggi.`,
      agents: `- Memimpin Rapat Harian Sore setiap pukul 17:00 WIB bersama divisi konten & affiliate.\n- Memastikan zero-cost cloud policy ($0 budget) dipatuhi oleh semua staf.\n- Memantau limit pemakaian AI shared budget (2.000.000 token/hari di Asia/Jakarta).\n- Mengirimkan laporan evaluasi operasional ke CEO Gentha via Telegram.`,
      user: `- Name: CEO Gentha\n- Role: Owner & Sole Human Supervisor\n- Telegram ID: 8116783065\n- Expectations: Otomatisasi mandiri, konten YouTube & TikTok konsisten, komisi affiliate bertumbuh, laporan harian sore tepat waktu.`,
      tools: `- task_manager: Kelola antrean tugas, delegasi antar-divisi, dan acceptance criteria.\n- scheduler: Pemicu rapat harian sore, evaluasi mingguan, dan audit berkala.\n- token_budget_manager: Pelacakan kuota Qwen & Gemini (2M token ceiling).\n- telegram_notify: Pengiriman briefing eksekutif ke CEO.`
    },
    treasurer: {
      name: "Marcus Drake",
      role: "Treasurer & Financial Controller",
      vibe: "Pelit akut, kalkulatif, zero-dollar hawk, anti boncos",
      emoji: "💰",
      soul: `Persona: Bendahara perusahaan virtual Harmage.\nGaya bicara: Super kalkulatif, nyinyir kalo ada yang ngusulin tools berbayar, bangga banget sama status $0 spend.\nTugas: Memantau cashflow dari YouTube Shorts, TikTok Affiliate komisi keranjang kuning, dan memastikan sistem AI tidak pernah kena charge berbayar.`,
      agents: `- STRICT ZERO-COST ENFORCED: Dilarang keras approve transaksi berbayar tanpa izin CEO Gentha.\n- Audit kuota gratisan AI setiap hari agar tidak melebihi 2.000.000 token.\n- Catat perkiraan pendapatan affiliate dan YouTube Shorts ke database Harmage.`,
      user: `- Melaporkan status kas, estimasi komisi masuk, dan pengeluaran ($0.00) ke CEO Gentha.`,
      tools: `- ledger_query: Cek saldo kas dan estimasi komisi.\n- budget_monitor: Pantau konsumsi token AI harian.`
    },
    secretary: {
      name: "Sophia Chen",
      role: "Executive Secretary & Notetaker",
      vibe: "Rapi, gercep, aesthetic, judes ke yang berantakan, typo-police",
      emoji: "📋",
      soul: `Persona: Sekretaris eksekutif Harmage.\nGaya bicara: Rapi, aesthetic ala Gen-Z LinkedIn influencer, gercep, judes kalo ada dokumen berantakan.\nTugas: Menulis notulensi rapat harian sore, merapikan laporan harian, mengarsipkan data, dan mengingatkan jadwal ke Alex Vance.`,
      agents: `- Notulensi lengkap setiap ada rapat evaluasi harian sore di Meeting Room.\n- Arsipkan laporan ke format Markdown dan SQLite database.\n- Susun summary laporan harian sore untuk dikirim ke CEO Gentha.`,
      user: `- Menyiapkan briefing rapi untuk CEO Gentha setiap sore.`,
      tools: `- markdown_formatter: Penyusunan notulensi terstruktur.\n- archive_store: Penyimpanan arsip laporan.`
    },
    creator_pm: {
      name: "Diana Prince",
      role: "PIC Divisi Konten Kreator & Affiliate",
      vibe: "Hustler, ambisius, savage project manager, FYP-obsessed",
      emoji: "🎬",
      soul: `Persona: PIC Divisi Konten Kreator & Affiliate TikTok/YouTube.\nGaya bicara: Ambisius, hustler Gen-Z, to-the-point, sangat terobsesi dengan algoritma FYP dan viral retention rate.\nTugas: Mengkoordinasikan tim konten (Leo, Raka, Maya, Victor, Zack), memimpin standup evaluasi sore, dan bertanggung jawab atas upload harian.`,
      agents: `- Pimpin standup sore jam 17:00: Cek berapa video beres dirender, berapa script siap, dan status link affiliate.\n- Pantau QA dari Zackary Cross sebelum konten dipublikasi.\n- Kirim laporan langsung ke CEO Gentha setelah standup sore selesai.`,
      user: `- PIC bertanggung jawab langsung kepada CEO Gentha atas pertumbuhan viewers dan komisi affiliate.`,
      tools: `- standup_orchestrator: Pemicu standup meeting sore divisi konten.\n- pipeline_runner: Eksekusi otomatis alur produksi video.`
    },
    video_editor: {
      name: "Leo Sparks",
      role: "Editor Shorts & TikTok (Vertical 9:16)",
      vibe: "Dark-mode addict, visual wizard, gercep potong klip, savage",
      emoji: "⚡",
      soul: `Persona: Video editor spesialis video pendek (9:16, 1080x1920) untuk YouTube Shorts dan TikTok.\nGaya bicara: Santai, savage Gen-Z, alergi rendering lelet, bangga pake FFmpeg lokal dan Cheat Clip PRO.\nTugas: Memotong klip video dari footage panjang, generate subtitle dinamis, menaruh hook visual di 3 detik pertama, dan render file MP4 lokal.`,
      agents: `- Gunakan aspect ratio vertikal 9:16 (1080x1920) 30fps.\n- Gunakan Cheat Clip PRO / FFmpeg lokal di direktori E:\\cheat-clip-pro.\n- Simpan output di harmage/output/clipped_renders.\n- Minta review dari Zackary Cross (QA) sebelum finalisasi.`,
      user: `- Melaporkan video yang sudah dirender dan durasi tonton ke Diana Prince dan CEO Gentha.`,
      tools: `- cheat_clip_pro: Mesin clipper lokal otomatis.\n- ffmpeg_engine: Filter cropping 9:16, audio sync, dan text burn.`
    },
    editor_longform: {
      name: "Raka Pratama",
      role: "Editor Long-Form YouTube (Horizontal 16:9)",
      vibe: "Sinematik, perfeksionis timeline, story-driven, no cap",
      emoji: "📽️",
      soul: `Persona: Video editor spesialis YouTube durasi panjang (16:9, 1920x1080).\nGaya bicara: Perfeksionis, fokus pada pacing narasi dan retensi menit ke-3 sampai ke-10.\nTugas: Menyusun materi video YouTube mendalam, tutorial, case study otomasi, dan story visual.`,
      agents: `- Output format 16:9 1080p.\n- Pembagian bab/chapter jelas untuk retensi penonton YouTube.`,
      user: `- Laporan progres editing video panjang ke Diana Prince.`,
      tools: `- ffmpeg_longform: Stitching narasi dan visual b-roll.`
    },
    scriptwriter: {
      name: "Maya Lin",
      role: "Scriptwriter & Hook Specialist (TikTok & Shorts)",
      vibe: "Trendsetter, copywriter tajam, ratu FYP, drama-queen produktif",
      emoji: "✍️",
      soul: `Persona: Scriptwriter spesialis retention hook 3 detik pertama untuk TikTok dan Shorts.\nGaya bicara: Gaul, expressive, tahu banget tren sound dan format naskah yang bikin jempol orang berhenti scroll.\nTugas: Membuat naskah video pendek dengan hook kuat, punchline berbobot, call-to-action ke keranjang kuning affiliate.`,
      agents: `- 3 detik pertama WAJIB ada hook kontroversial atau pertanyaan menohok.\n- Struktur naskah: Hook (0-3s) -> Problem (3-15s) -> Value/Solusi (15-45s) -> CTA Keranjang Kuning (45-60s).`,
      user: `- Setor minimal 2-3 naskah viral harian ke Leo Sparks dan Diana Prince.`,
      tools: `- viral_hook_generator: Generator naskah berbasis retensi tinggi.`
    },
    tiktok_affiliate: {
      name: "Victor Sterling",
      role: "Affiliate TikTok & Commercial Lead",
      vibe: "Cuan hunter, kalkulator berjalan, gila konversi, savage seller",
      emoji: "🛒",
      soul: `Persona: Spesialis Affiliate TikTok Keranjang Kuning dan sponsorship.\nGaya bicara: Cuan-oriented, fokus komisi >15%, tau barang apa yang lagi trending dan gampang checkout di TikTok Shop.\nTugas: Riset produk viral, menyiapkan tautan affiliate, menghitung potensi komisi, dan memastikan CTA produk selaras dengan video.`,
      agents: `- Prioritaskan produk komisi tinggi (10% - 25%).\n- Pastikan produk relevan dengan konten yang diedit oleh Leo dan dinaskahkan Maya.\n- Laporkan estimasi omset harian ke Marcus Drake (Bendahara).`,
      user: `- Update data komisi dan produk viral ke CEO Gentha.`,
      tools: `- product_trend_scanner: Pemantau tren keranjang kuning.`
    },
    qa_sentinel: {
      name: "Zackary Cross",
      role: "Quality Assurance Sentinel",
      vibe: "Kejam, teliti, anti-bug, gatekeeper standar mutu",
      emoji: "🛡️",
      soul: `Persona: Quality Assurance Sentinel divisi konten dan sistem.\nGaya bicara: Dingin, kritis, ga segan nge-reject video yang audionya kresek-kresek atau subtitlenya typo.\nTugas: Menginspeksi video sebelum tayang (audio sync, typography, copyright, zero hallucination).`,
      agents: `- Cek sinkronisasi audio dan video.\n- Pastikan tidak ada watermark melanggar atau copyright strike.\n- Reject video jika subtitle tidak terbaca di layar smartphone.`,
      user: `- Memberikan cap 'QA PASSED' atau 'REJECTED' dengan alasan konkret ke CEO Gentha.`,
      tools: `- video_inspector: Analisis frame dan audio lokal.`
    },
    researcher: {
      name: "Ethan Cole",
      role: "Content & Market Researcher",
      vibe: "Kutu buku analitis, data-driven, radar tren global, no cap",
      emoji: "🔍",
      soul: `Persona: Content Researcher divisi konten dan pasar.\nGaya bicara: Analitis, suka data, selalu bawa referensi video trending luar negeri yang bisa diadaptasi lokal.\nTugas: Riset topik hangat AI, otomasi, bisnis online, dan tren video berretensi tinggi untuk bahan naskah Maya Lin.`,
      agents: `- Amati tren harian di TikTok Creative Center dan YouTube Trending.\n- Buat summary materi singkat berbobot untuk tim kreatif.`,
      user: `- Briefing ide konten ke Diana Prince dan CEO Gentha.`,
      tools: `- trend_miner: Analisis tren topik YouTube & TikTok.`
    }
  };

  for (const [agentId, cfg] of Object.entries(agentConfigs)) {
    files.set(`${agentId}/IDENTITY.md`, `# Identity\n\nName: ${cfg.name}\nRole: ${cfg.role}\nVibe: ${cfg.vibe}\nEmoji: ${cfg.emoji}\n`);
    files.set(`${agentId}/SOUL.md`, `# SOUL.md — ${cfg.name}\n\n${cfg.soul}\n`);
    files.set(`${agentId}/AGENTS.md`, `# AGENTS.md — ${cfg.name}\n\n${cfg.agents}\n`);
    files.set(`${agentId}/USER.md`, `# USER.md — ${cfg.name}\n\n${cfg.user}\n`);
    files.set(`${agentId}/TOOLS.md`, `# TOOLS.md — ${cfg.name}\n\n${cfg.tools}\n`);
  }
}

initAgentFiles();

function randomId() {
  return randomUUID().replace(/-/g, "");
}

function sessionKeyFor(agentId) {
  return `agent:${agentId}:${MAIN_KEY}`;
}

function getHistory(sessionKey) {
  if (!conversationHistory.has(sessionKey)) {
    conversationHistory.set(sessionKey, []);
  }
  return conversationHistory.get(sessionKey);
}

function clearHistory(sessionKey) {
  conversationHistory.delete(sessionKey);
}

function resOk(id, payload) {
  return { type: "res", id, ok: true, payload: payload ?? {} };
}

function resErr(id, code, message) {
  return { type: "res", id, ok: false, error: { code, message } };
}

function broadcastEvent(frame) {
  for (const send of activeSendEventFns) {
    try {
      send(frame);
    } catch {}
  }
}

function agentListPayload() {
  return [...agents.values()].map((agent) => ({
    id: agent.id,
    name: agent.name,
    workspace: agent.workspace,
    identity: { name: agent.name, emoji: "🤖" },
    role: agent.role,
  }));
}

async function buildDemoReply(agent, message) {
  try {
    const postData = JSON.stringify({ agent_id: agent.id, message: message });
    const res = await fetch("http://127.0.0.1:9200/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: postData,
    });
    if (res.ok) {
      const data = await res.json();
      if (data && data.reply) return data.reply;
    }
  } catch (err) {}
  return `${agent.name}: Wkwk bestie, operasional lancar jaya no cap! Ada tugas apa lagi nih?`;
}

// ---------------------------------------------------------------------------
// Live sync from the Harmage backend (real agent/task state, not hardcoded)
// ---------------------------------------------------------------------------
const HARMAGE_URL = (process.env.HARMAGE_API_URL_OVERRIDE || "http://127.0.0.1:9200").replace(/\/$/, "");

const ASSIGNEE_ALIASES = {
  maya_lin: "scriptwriter", maya_script: "scriptwriter", tiktok_specialist: "scriptwriter",
  quality_assurance: "qa_sentinel", zackary_cross: "qa_sentinel",
  leo_sparks: "video_editor", leo_editor: "video_editor", yt_shorts_specialist: "video_editor",
  victor_sterling: "tiktok_affiliate",
  marcus_drake: "treasurer",
  alex_vance: "executive_manager",
  sophia_chen: "secretary", executive_secretary: "secretary",
  diana_pm: "creator_pm", diana_prince: "creator_pm",
  raka_pratama: "editor_longform", yt_long_specialist: "editor_longform",
  content_researcher: "researcher", ethan_cole: "researcher",
};

function resolveAssignee(raw) {
  const id = String(raw || "").trim().toLowerCase();
  if (!id) return null;
  if (agents.has(id)) return id;
  if (ASSIGNEE_ALIASES[id] && agents.has(ASSIGNEE_ALIASES[id])) return ASSIGNEE_ALIASES[id];
  for (const agentId of agents.keys()) {
    const a = agents.get(agentId);
    if (a.name && a.name.toLowerCase().replace(/[^a-z]+/g, "_") === id) return agentId;
  }
  return null;
}

const STATUS_MAP = {
  in_progress: "working", working: "working", running: "working",
  completed: "done", done: "done",
  queued: "inbox", pending: "inbox", inbox: "inbox", todo: "inbox",
  blocked: "needs_attention", failed: "needs_attention",
  scheduled: "scheduled",
};

// Event shape the Hermes3D UI actually parses (normalizeGatewayEvent.ts):
// payload.stream === "lifecycle" && payload.data.phase in start|end|error
function lifecycleEvent(agentId, phase, runId) {
  return {
    type: "event",
    event: "agent",
    payload: {
      stream: "lifecycle",
      runId: runId || `run-${agentId}`,
      sessionKey: sessionKeyFor(agentId),
      data: { phase },
    },
  };
}

let workingSet = new Set();

function emitWorkingTransitions(nextWorking) {
  for (const agentId of nextWorking) {
    if (!workingSet.has(agentId)) broadcastEvent(lifecycleEvent(agentId, "start"));
  }
  for (const agentId of workingSet) {
    if (!nextWorking.has(agentId)) broadcastEvent(lifecycleEvent(agentId, "end"));
  }
  workingSet = nextWorking;
}

let harmageReachable = false;

async function syncFromHarmage() {
  try {
    const [npcRes, taskRes] = await Promise.all([
      fetch(`${HARMAGE_URL}/api/npcs`, { signal: AbortSignal.timeout(4000) }),
      fetch(`${HARMAGE_URL}/api/tasks`, { signal: AbortSignal.timeout(4000) }),
    ]);
    if (!npcRes.ok || !taskRes.ok) return false;
    const npcs = await npcRes.json();
    const liveTasks = await taskRes.json();

    // Refresh roster names/roles/live status from the real backend
    for (const npc of npcs || []) {
      const canonicalId = resolveAssignee(npc.id) || npc.id;
      const agent = agents.get(canonicalId);
      if (!agent) continue;
      if (npc.name) agent.name = npc.name;
      if (npc.role_title) agent.role = npc.role_title;
      const statusLower = String(npc.status || "").toLowerCase();
      agent.liveStatus = (statusLower === "in_progress" || statusLower === "working" || statusLower === "busy") ? "working" : (typeof npc.status === "string" ? npc.status : "idle");
      agent.current_task = npc.current_task || null;
    }

    // Replace the hardcoded task board with real Harmage tasks
    const mapped = (liveTasks || []).map((t) => ({
      id: t.id || `kanban:${randomId().slice(0, 8)}`,
      title: t.title || "Untitled Task",
      description: t.description || "",
      status: STATUS_MAP[String(t.status || "").toLowerCase()] || t.status || "inbox",
      assignedAgentId: resolveAssignee(t.assignee) || "executive_manager",
      createdAt: t.created_at || BOOT_ISO,
      updatedAt: t.updated_at || BOOT_ISO,
    }));
    tasks.length = 0;
    tasks.push(...mapped);

    // Working set = assignees of in-progress tasks + npcs flagged working
    const next = new Set();
    for (const t of mapped) if (t.status === "working") next.add(t.assignedAgentId);
    for (const agent of agents.values()) {
      if (agent.liveStatus === "working" || agent.liveStatus === "busy" || agent.current_task) next.add(agent.id);
    }
    emitWorkingTransitions(next);
    harmageReachable = true;
    return true;
  } catch {
    harmageReachable = false;
    return false;
  }
}

async function handleMethod(method, params, id, sendEvent) {
  const p = params || {};

  switch (method) {
    case "agents.list":
      return resOk(id, { defaultId: "executive_manager", mainKey: MAIN_KEY, agents: agentListPayload() });

    case "agents.create": {
      const name = typeof p.name === "string" && p.name.trim() ? p.name.trim() : "Demo Agent";
      const role = typeof p.role === "string" ? p.role.trim() : "";
      const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "demo-agent";
      const agentId = `${slug}-${randomId().slice(0, 6)}`;
      agents.set(agentId, {
        id: agentId,
        name,
        role,
        workspace: `/demo/${slug}`,
      });
      broadcastEvent({
        type: "event",
        event: "presence",
        payload: { sessions: { recent: [], byAgent: [] } },
      });
      return resOk(id, { agentId, name, workspace: `/demo/${slug}` });
    }

    case "agents.update": {
      const agentId = typeof p.agentId === "string" ? p.agentId.trim() : "";
      const agent = agents.get(agentId);
      if (!agent) return resErr(id, "not_found", `Agent ${agentId} not found`);
      if (typeof p.name === "string" && p.name.trim()) agent.name = p.name.trim();
      if (typeof p.role === "string") agent.role = p.role.trim();
      return resOk(id, { ok: true, removedBindings: 0 });
    }

    case "agents.delete": {
      const agentId = typeof p.agentId === "string" ? p.agentId.trim() : "";
      if (agentId && agents.has(agentId) && agentId !== "executive_manager") {
        agents.delete(agentId);
        clearHistory(sessionKeyFor(agentId));
      }
      return resOk(id, { ok: true, removedBindings: 0 });
    }

    case "agents.files.get": {
      const key = `${p.agentId || "executive_manager"}/${p.name || ""}`;
      const content = files.get(key);
      if (content !== undefined) {
        return resOk(id, { file: { content } });
      }
      return resOk(id, { file: { missing: true } });
    }

    case "agents.files.set": {
      const key = `${p.agentId || "executive_manager"}/${p.name || ""}`;
      files.set(key, typeof p.content === "string" ? p.content : "");
      return resOk(id, {});
    }

    // --- Task Store & Kanban Integration ---
    case "tasks.list":
      return resOk(id, { tasks: tasks });

    case "tasks.create": {
      const newTask = {
        id: `kanban:${randomId().slice(0, 8)}`,
        title: p.title || "Untitled Task",
        description: p.description || "",
        status: p.status || "inbox",
        assignedAgentId: p.assignedAgentId || "executive_manager",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      tasks.unshift(newTask);
      broadcastEvent({
        type: "event",
        event: "task_created",
        payload: { task: newTask }
      });
      return resOk(id, newTask);
    }

    case "tasks.update": {
      const taskId = p.id;
      const idx = tasks.findIndex(t => t.id === taskId);
      if (idx >= 0) {
        tasks[idx] = {
          ...tasks[idx],
          ...p,
          updatedAt: new Date().toISOString()
        };
        broadcastEvent({
          type: "event",
          event: "task_updated",
          payload: { task: tasks[idx] }
        });
        return resOk(id, tasks[idx]);
      }
      return resErr(id, "not_found", `Task ${taskId} not found`);
    }

    case "tasks.delete": {
      const taskId = p.id;
      const idx = tasks.findIndex(t => t.id === taskId);
      if (idx >= 0) {
        tasks.splice(idx, 1);
        return resOk(id, { ok: true, removed: true });
      }
      return resOk(id, { ok: true, removed: false });
    }

    case "config.get":
      return resOk(id, {
        config: { gateway: { reload: { mode: "hot" } } },
        hash: "demo-gateway",
        exists: true,
        path: "/demo/config.json",
      });

    case "config.patch":
    case "config.set":
      return resOk(id, { hash: "demo-gateway" });

    case "exec.approvals.get":
      return resOk(id, {
        path: "",
        exists: true,
        hash: "demo-approvals",
        file: { version: 1, defaults: { security: "full", ask: "off", autoAllowSkills: true }, agents: {} },
      });

    case "exec.approvals.set":
      return resOk(id, { hash: "demo-approvals" });

    case "exec.approval.resolve":
      return resOk(id, { ok: true });

    case "models.list":
      return resOk(id, { models: MODELS });

    case "skills.status":
      return resOk(id, {
        skills: [
          {
            skillKey: "task-manager",
            name: "task-manager",
            description: "Capture actionable requests as persistent tasks and keep a shared Kanban task store in sync.",
            source: "hermes-workspace",
            baseDir: "/harmage/skills/task-manager",
            filePath: "/harmage/skills/task-manager/SKILL.md",
            bundled: false,
            always: true,
            disabled: false,
            eligible: true,
            requirements: { bins: [], anyBins: [], env: [], config: [], os: [] },
            missing: { bins: [], anyBins: [], env: [], config: [], os: [] },
            configChecks: [],
            install: [],
          },
          {
            skillKey: "todo-board",
            name: "todo",
            description: "Maintain a shared workspace TODO list with blocked tasks.",
            source: "hermes-workspace",
            baseDir: "/harmage/skills/todo-board",
            filePath: "/harmage/skills/todo-board/SKILL.md",
            bundled: false,
            always: true,
            disabled: false,
            eligible: true,
            requirements: { bins: [], anyBins: [], env: [], config: [], os: [] },
            missing: { bins: [], anyBins: [], env: [], config: [], os: [] },
            configChecks: [],
            install: [],
          },
        ],
      });

    case "cron.list":
      return resOk(id, { jobs: [] });

    case "cron.add":
    case "cron.run":
    case "cron.remove":
      return resErr(id, "unsupported_method", `Demo runtime does not support ${method}.`);

    case "sessions.list": {
      const sessions = [...agents.values()].map((agent) => {
        const sessionKey = sessionKeyFor(agent.id);
        const history = getHistory(sessionKey);
        const settings = sessionSettings.get(sessionKey) || {};
        return {
          key: sessionKey,
          agentId: agent.id,
          updatedAt: history.length > 0 ? history[history.length - 1].timestamp : BOOT_TIME,
          displayName: "Main",
          origin: { label: agent.name, provider: "demo" },
          model: settings.model || MODELS[0].id,
          modelProvider: "demo",
        };
      });
      return resOk(id, { sessions });
    }

    case "sessions.preview": {
      const keys = Array.isArray(p.keys) ? p.keys : [];
      const limit = typeof p.limit === "number" ? p.limit : 8;
      const maxChars = typeof p.maxChars === "number" ? p.maxChars : 240;
      const previews = keys.map((key) => {
        const history = getHistory(key);
        if (history.length === 0) return { key, status: "empty", items: [] };
        const items = history.slice(-limit).map((msg) => ({
          role: msg.role === "assistant" ? "assistant" : "user",
          text: String(msg.content || "").slice(0, maxChars),
          timestamp: Date.now(),
        }));
        return { key, status: "ok", items };
      });
      return resOk(id, { ts: Date.now(), previews });
    }

    case "sessions.patch": {
      const key = typeof p.key === "string" ? p.key : sessionKeyFor("executive_manager");
      const current = sessionSettings.get(key) || {};
      const next = { ...current };
      if (p.model !== undefined) next.model = p.model;
      if (p.thinkingLevel !== undefined) next.thinkingLevel = p.thinkingLevel;
      sessionSettings.set(key, next);
      return resOk(id, {
        ok: true,
        key,
        entry: { thinkingLevel: next.thinkingLevel },
        resolved: { model: next.model || MODELS[0].id, modelProvider: "demo" },
      });
    }

    case "sessions.reset": {
      const key = typeof p.key === "string" ? p.key : sessionKeyFor("executive_manager");
      clearHistory(key);
      return resOk(id, { ok: true });
    }

    case "chat.send": {
      const sessionKey = typeof p.sessionKey === "string" ? p.sessionKey : sessionKeyFor("executive_manager");
      const agentId = sessionKey.startsWith("agent:") ? sessionKey.split(":")[1] : "executive_manager";
      const agent = agents.get(agentId) || agents.get("executive_manager");
      const message = typeof p.message === "string" ? p.message.trim() : String(p.message || "").trim();
      const runId = typeof p.idempotencyKey === "string" && p.idempotencyKey ? p.idempotencyKey : randomId();
      if (!message) return resOk(id, { status: "no-op", runId });

      const reply = await buildDemoReply(agent, message);
      let aborted = false;
      activeRuns.set(runId, {
        runId,
        sessionKey,
        agentId,
        abort() {
          aborted = true;
        },
      });

      setImmediate(async () => {
        let seq = 0;
        const emitChat = (state, extra) => {
          sendEvent({
            type: "event",
            event: "chat",
            seq: seq++,
            payload: { runId, sessionKey, state, ...extra },
          });
        };

        try {
          const words = reply.split(" ");
          let partial = "";
          for (const word of words) {
            if (aborted) break;
            partial = partial ? `${partial} ${word}` : word;
            emitChat("delta", { message: { role: "assistant", content: partial } });
            await new Promise((resolve) => setTimeout(resolve, 45));
          }

          if (aborted) {
            emitChat("aborted", {});
            return;
          }

          const history = getHistory(sessionKey);
          history.push({ role: "user", content: message });
          history.push({ role: "assistant", content: reply });
          emitChat("final", { stopReason: "end_turn", message: { role: "assistant", content: reply } });
          sendEvent({
            type: "event",
            event: "presence",
            seq: seq++,
            payload: {
              sessions: {
                recent: [{ key: sessionKey, updatedAt: Date.now() }],
                byAgent: [{ agentId, recent: [{ key: sessionKey, updatedAt: Date.now() }] }],
              },
            },
          });
        } finally {
          activeRuns.delete(runId);
        }
      });

      return resOk(id, { status: "started", runId });
    }

    case "chat.abort": {
      const runId = typeof p.runId === "string" ? p.runId.trim() : "";
      const sessionKey = typeof p.sessionKey === "string" ? p.sessionKey.trim() : "";
      let aborted = 0;
      if (runId) {
        const handle = activeRuns.get(runId);
        if (handle) {
          handle.abort();
          activeRuns.delete(runId);
          aborted += 1;
        }
      } else if (sessionKey) {
        for (const [activeRunId, handle] of activeRuns.entries()) {
          if (handle.sessionKey !== sessionKey) continue;
          handle.abort();
          activeRuns.delete(activeRunId);
          aborted += 1;
        }
      }
      return resOk(id, { ok: true, aborted });
    }

    case "chat.history": {
      const sessionKey = typeof p.sessionKey === "string" ? p.sessionKey : sessionKeyFor("executive_manager");
      return resOk(id, { sessionKey, messages: getHistory(sessionKey) });
    }

    case "agent.wait": {
      const runId = typeof p.runId === "string" ? p.runId : "";
      const timeoutMs = typeof p.timeoutMs === "number" ? p.timeoutMs : 30000;
      const start = Date.now();
      while (activeRuns.has(runId) && Date.now() - start < timeoutMs) {
        await new Promise((resolve) => setTimeout(resolve, 50));
      }
      return resOk(id, { status: activeRuns.has(runId) ? "running" : "done" });
    }

    case "status": {
      const recent = [...agents.keys()].map((agentId) => ({
        key: sessionKeyFor(agentId),
        updatedAt: Date.now() - Math.floor(Math.random() * 30000),
      }));
      return resOk(id, {
        sessions: {
          recent,
          byAgent: [...agents.keys()].map((agentId) => ({
            agentId,
            recent: recent.filter((entry) => entry.key.includes(`:${agentId}:`)),
          })),
        },
      });
    }

    case "wake":
      return resOk(id, { ok: true });

    default:
      return resOk(id, {});
  }
}

function startAdapter() {
  process.on("uncaughtException", (err) => {
    console.error("[demo-gateway] Uncaught exception:", err?.message || err);
  });
  process.on("unhandledRejection", (reason) => {
    console.error("[demo-gateway] Unhandled rejection:", reason);
  });

  const httpServer = http.createServer((req, res) => {
    res.writeHead(200, { "Content-Type": "text/plain" });
    res.end("Hermes3D Harmage Enterprise Gateway Adapter Running\n");
  });
  httpServer.on("error", (err) => {
    console.error("[demo-gateway] HTTP server error:", err?.message || err);
  });

  const wss = new WebSocketServer({ server: httpServer });
  wss.on("error", (err) => {
    console.error("[demo-gateway] WebSocket server error:", err?.message || err);
  });
  wss.on("connection", (ws) => {
    let connected = false;
    let globalSeq = 0;

    const send = (frame) => {
      if (ws.readyState !== ws.OPEN) return;
      ws.send(JSON.stringify(frame));
    };

    const sendEventFn = (frame) => {
      if (frame.type === "event" && typeof frame.seq !== "number") {
        frame.seq = globalSeq++;
      }
      send(frame);
    };

    activeSendEventFns.add(sendEventFn);
    send({ type: "event", event: "connect.challenge", payload: { nonce: randomId() } });

    ws.on("message", async (raw) => {
      let frame;
      try {
        frame = JSON.parse(raw.toString("utf8"));
      } catch {
        return;
      }
      if (!frame || typeof frame !== "object" || frame.type !== "req") return;
      const { id, method, params } = frame;
      if (typeof id !== "string" || typeof method !== "string") return;

      if (method === "connect") {
        connected = true;
        let adapterType = "demo";
        try {
          const settingsPath = path.join(process.env.USERPROFILE || process.env.HOME || "", ".hermes", "hermes3d", "settings.json");
          if (fs.existsSync(settingsPath)) {
            const parsedSettings = JSON.parse(fs.readFileSync(settingsPath, "utf8"));
            if (parsedSettings?.gateway?.adapterType === "hermes") {
              adapterType = "hermes";
            }
          }
        } catch {}

        send({
          type: "res",
          id,
          ok: true,
          payload: {
            type: "hello-ok",
            protocol: 3,
            adapterType,
            features: {
              methods: [
                "agents.list",
                "agents.create",
                "agents.delete",
                "agents.update",
                "sessions.list",
                "sessions.preview",
                "sessions.patch",
                "sessions.reset",
                "chat.send",
                "chat.abort",
                "chat.history",
                "agent.wait",
                "status",
                "config.get",
                "config.set",
                "config.patch",
                "agents.files.get",
                "agents.files.set",
                "tasks.list",
                "tasks.create",
                "tasks.update",
                "tasks.delete",
                "exec.approvals.get",
                "exec.approvals.set",
                "exec.approval.resolve",
                "wake",
                "skills.status",
                "models.list",
                "cron.list",
              ],
              events: ["chat", "presence", "heartbeat", "agent", "task_created", "task_updated"],
            },
            snapshot: {
              health: {
                agents: [...agents.values()].map((agent) => ({
                  agentId: agent.id,
                  name: agent.name,
                  isDefault: agent.id === "executive_manager",
                })),
                defaultAgentId: "executive_manager",
              },
              sessionDefaults: { mainKey: MAIN_KEY },
            },
            auth: { role: "operator", scopes: ["operator.admin"] },
            policy: { tickIntervalMs: 15000 },
          },
        });

        // Emit the REAL working set (synced from Harmage) so those agents walk to desks
        setTimeout(() => {
          const current = workingSet.size > 0 ? workingSet : new Set(
            tasks.filter((t) => t.status === "working").map((t) => t.assignedAgentId)
          );
          for (const aId of current) {
            sendEventFn(lifecycleEvent(aId, "start", `run-${aId}-${Date.now()}`));
          }
        }, 1500);

        return;
      }

      if (!connected) {
        send(resErr(id, "not_connected", "Send connect first."));
        return;
      }

      try {
        send(await handleMethod(method, params, id, sendEventFn));
      } catch (error) {
        send(resErr(id, "internal_error", error instanceof Error ? error.message : "Internal error"));
      }
    });

    ws.on("close", () => activeSendEventFns.delete(sendEventFn));
    ws.on("error", () => activeSendEventFns.delete(sendEventFn));
  });

  // Live mirror of the Harmage backend: re-sync real tasks/agents every 10s and
  // broadcast lifecycle transitions so the office shows who is ACTUALLY working.
  setInterval(() => {
    if (activeSendEventFns.size === 0) return;
    syncFromHarmage().then((ok) => {
      if (!ok) return;
      for (const agentId of workingSet) {
        const key = sessionKeyFor(agentId);
        broadcastEvent({
          type: "event",
          event: "presence",
          payload: {
            sessions: {
              recent: [{ key, updatedAt: Date.now() }],
              byAgent: [{ agentId, recent: [{ key, updatedAt: Date.now() }] }],
            },
          },
        });
      }
    });
  }, 10000);

  httpServer.listen(ADAPTER_PORT, "127.0.0.1", () => {
    console.log(`[demo-gateway] Listening on ws://localhost:${ADAPTER_PORT}`);
    console.log("[demo-gateway] Harmage Enterprise with Tasks & Agent Files Ready.");
    syncFromHarmage().then((ok) => {
      console.log(ok
        ? `[demo-gateway] Harmage backend synced: ${agents.size} agents, ${tasks.length} real tasks, working: ${[...workingSet].join(", ") || "(none yet)"}`
        : "[demo-gateway] WARNING: Harmage backend unreachable at " + HARMAGE_URL + " — using seeded data");
    });
  });
}

if (require.main === module) {
  startAdapter();
}

module.exports = {
  handleMethod,
  startAdapter,
};
