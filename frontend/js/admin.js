// Zedchatbot Admin Telemetry Console
// Reads the /stats and /interactions endpoints and renders a live log view.

const THEME_KEY = "zedchatbot-theme";
const API_BASE = "";
const AUTO_REFRESH_MS = 10000;

const state = {
  limit: 50,
  offset: 0,
  filters: { country: "", channel: "", language: "", rating: "", search: "" },
  total: 0,
  lastItems: [],
  autoRefresh: false,
  timer: null,
};

const el = {
  kpiTotal: document.getElementById("kpi-total"),
  kpiLatency: document.getElementById("kpi-latency"),
  kpiRating: document.getElementById("kpi-rating"),
  kpiRated: document.getElementById("kpi-rated"),
  kpiChannels: document.getElementById("kpi-channels"),
  kpiLanguages: document.getElementById("kpi-languages"),
  tableBody: document.getElementById("table-body"),
  pagerStatus: document.getElementById("pager-status"),
  prevBtn: document.getElementById("prev-btn"),
  nextBtn: document.getElementById("next-btn"),
  applyBtn: document.getElementById("apply-btn"),
  clearBtn: document.getElementById("clear-btn"),
  exportBtn: document.getElementById("export-btn"),
  refreshBtn: document.getElementById("refresh-btn"),
  autoRefresh: document.getElementById("auto-refresh"),
  themeToggle: document.getElementById("theme-toggle-btn"),
  limitSelect: document.getElementById("f-limit"),
  modal: document.getElementById("detail-modal"),
  modalBody: document.getElementById("detail-body"),
  modalTitle: document.getElementById("detail-title"),
  fCountry: document.getElementById("f-country"),
  fChannel: document.getElementById("f-channel"),
  fLanguage: document.getElementById("f-language"),
  fRating: document.getElementById("f-rating"),
  fSearch: document.getElementById("f-search"),
};

function escapeHtml(value) {
  return String(value == null ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatLatency(ms) {
  const n = Number(ms);
  if (!Number.isFinite(n) || n <= 0) return "—";
  return n < 1000 ? `${Math.round(n)} ms` : `${(n / 1000).toFixed(1)} s`;
}

// SQLite stores CURRENT_TIMESTAMP in UTC ("YYYY-MM-DD HH:MM:SS", no offset).
// Interpret it as UTC and render in the viewer's local timezone.
function formatTimestamp(ts) {
  if (!ts) return "—";
  let value = String(ts).trim();
  if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(value)) {
    value = value.replace(" ", "T") + "Z";
  }
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(ts);
  const pad = (n) => String(n).padStart(2, "0");
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ` +
    `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
  );
}

function readFilters() {
  state.filters = {
    country: el.fCountry.value,
    channel: el.fChannel.value,
    language: el.fLanguage.value,
    rating: el.fRating.value,
    search: el.fSearch.value.trim(),
  };
}

function buildQuery(includePaging = true) {
  const params = new URLSearchParams();
  const f = state.filters;
  if (f.country) params.set("country", f.country);
  if (f.channel) params.set("channel", f.channel);
  if (f.language) params.set("language", f.language);
  if (f.rating) params.set("rating", f.rating);
  if (f.search) params.set("search", f.search);
  if (includePaging) {
    params.set("limit", state.limit);
    params.set("offset", state.offset);
  }
  return params.toString();
}

function ratingPill(rating) {
  if (rating == null) return `<span class="rating-pill">—</span>`;
  const n = Number(rating);
  const cls = n >= 4 ? "rating-good" : n <= 2 ? "rating-bad" : "";
  return `<span class="rating-pill ${cls}">${n}</span>`;
}

async function loadStats() {
  try {
    const res = await fetch(`${API_BASE}/stats`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const s = await res.json();

    el.kpiTotal.textContent = s.total_interactions ?? 0;
    el.kpiLatency.textContent = formatLatency(s.average_latency_ms);
    el.kpiRating.textContent = s.average_rating ? s.average_rating.toFixed(2) : "—";
    el.kpiRated.textContent = s.rated_count ?? 0;

    const fmt = (obj) =>
      obj && Object.keys(obj).length
        ? Object.entries(obj)
            .sort((a, b) => b[1] - a[1])
            .map(([k, v]) => `${escapeHtml(k)}: ${v}`)
            .join(" · ")
        : "—";

    el.kpiChannels.innerHTML = fmt(s.by_channel);
    el.kpiLanguages.innerHTML = fmt(s.by_language);
  } catch (err) {
    console.error("Stats load failed:", err);
  }
}

async function loadInteractions() {
  el.tableBody.innerHTML = `<tr><td colspan="8" class="admin-empty">Loading…</td></tr>`;
  try {
    const res = await fetch(`${API_BASE}/interactions?${buildQuery(true)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    state.total = data.total || 0;
    const items = data.items || [];
    state.lastItems = items;

    if (!items.length) {
      el.tableBody.innerHTML = `<tr><td colspan="8" class="admin-empty">No interactions match these filters.</td></tr>`;
    } else {
      el.tableBody.innerHTML = items
        .map(
          (it) => `
        <tr data-id="${it.id}">
          <td class="cell-mono">${it.id}</td>
          <td class="cell-time">${escapeHtml(formatTimestamp(it.timestamp))}</td>
          <td><span class="channel-tag ${it.channel === "whatsapp" ? "channel-whatsapp" : ""}">${escapeHtml(it.channel)}</span></td>
          <td class="cell-mono">${escapeHtml((it.country || "").toUpperCase())}</td>
          <td><span class="lang-tag">${escapeHtml(it.detected_language)}</span></td>
          <td class="cell-mono">${formatLatency(it.response_time_ms)}</td>
          <td>${ratingPill(it.rating)}</td>
          <td class="cell-query">${escapeHtml(it.user_query)}</td>
        </tr>`
        )
        .join("");
    }

    updatePager();
  } catch (err) {
    console.error("Interactions load failed:", err);
    el.tableBody.innerHTML = `<tr><td colspan="8" class="admin-empty">Failed to load interactions. Is the server running?</td></tr>`;
  }
}

function updatePager() {
  const start = state.total === 0 ? 0 : state.offset + 1;
  const end = Math.min(state.offset + state.limit, state.total);
  el.pagerStatus.textContent = `Showing ${start}–${end} of ${state.total}`;
  el.prevBtn.disabled = state.offset <= 0;
  el.nextBtn.disabled = end >= state.total;
}

async function refreshAll() {
  await Promise.all([loadStats(), loadInteractions()]);
}

function openDetail(id) {
  const row = state.lastItems && state.lastItems.find((it) => String(it.id) === String(id));
  if (!row) return;

  el.modalTitle.textContent = `Interaction #${row.id}`;
  const sources = Array.isArray(row.retrieved_sources) ? row.retrieved_sources : [];
  const sourceHtml = sources.length
    ? sources.map((s) => `<span class="source-chip">${escapeHtml(s)}</span>`).join("")
    : `<span class="detail-val">No sources recorded.</span>`;

  el.modalBody.innerHTML = `
    <div class="detail-grid">
      <div class="detail-row"><div class="detail-key">Timestamp</div><div class="detail-val">${escapeHtml(formatTimestamp(row.timestamp))}</div></div>
      <div class="detail-row"><div class="detail-key">Channel</div><div class="detail-val">${escapeHtml(row.channel)}</div></div>
      <div class="detail-row"><div class="detail-key">Country</div><div class="detail-val">${escapeHtml((row.country || "").toUpperCase())}</div></div>
      <div class="detail-row"><div class="detail-key">Language</div><div class="detail-val">${escapeHtml(row.detected_language)}</div></div>
      <div class="detail-row"><div class="detail-key">Latency</div><div class="detail-val">${formatLatency(row.response_time_ms)}</div></div>
      <div class="detail-row"><div class="detail-key">Rating</div><div class="detail-val">${row.rating == null ? "Not rated" : row.rating + " / 5"}</div></div>
    </div>
    <div class="detail-row">
      <div class="detail-key">User query</div>
      <div class="detail-val">${escapeHtml(row.user_query)}</div>
    </div>
    <div class="detail-row">
      <div class="detail-key">Response</div>
      <div class="detail-val">${escapeHtml(row.response)}</div>
    </div>
    ${
      row.feedback_comment
        ? `<div class="detail-row"><div class="detail-key">Feedback comment</div><div class="detail-val">${escapeHtml(row.feedback_comment)}</div></div>`
        : ""
    }
    <div class="detail-row">
      <div class="detail-key">Retrieved sources</div>
      <div class="detail-val">${sourceHtml}</div>
    </div>
  `;
  el.modal.hidden = false;
}

function closeDetail() {
  el.modal.hidden = true;
}

function exportCsv() {
  readFilters();
  window.location.href = `${API_BASE}/interactions/export?${buildQuery(false)}`;
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch (_) {}
}

function setAutoRefresh(on) {
  state.autoRefresh = on;
  if (state.timer) {
    clearInterval(state.timer);
    state.timer = null;
  }
  if (on) {
    state.timer = setInterval(refreshAll, AUTO_REFRESH_MS);
  }
}

function init() {
  el.applyBtn.addEventListener("click", () => {
    readFilters();
    state.offset = 0;
    loadInteractions();
  });

  el.clearBtn.addEventListener("click", () => {
    el.fCountry.value = "";
    el.fChannel.value = "";
    el.fLanguage.value = "";
    el.fRating.value = "";
    el.fSearch.value = "";
    readFilters();
    state.offset = 0;
    loadInteractions();
  });

  el.fSearch.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      el.applyBtn.click();
    }
  });

  el.exportBtn.addEventListener("click", exportCsv);
  el.refreshBtn.addEventListener("click", refreshAll);

  el.limitSelect.addEventListener("change", () => {
    state.limit = parseInt(el.limitSelect.value, 10) || 50;
    state.offset = 0;
    loadInteractions();
  });

  el.prevBtn.addEventListener("click", () => {
    state.offset = Math.max(0, state.offset - state.limit);
    loadInteractions();
  });

  el.nextBtn.addEventListener("click", () => {
    if (state.offset + state.limit < state.total) {
      state.offset += state.limit;
      loadInteractions();
    }
  });

  el.autoRefresh.addEventListener("change", () => setAutoRefresh(el.autoRefresh.checked));

  el.themeToggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    applyTheme(current === "dark" ? "light" : "dark");
  });

  el.tableBody.addEventListener("click", (event) => {
    const row = event.target.closest("tr[data-id]");
    if (row) openDetail(row.dataset.id);
  });

  el.modal.addEventListener("click", (event) => {
    if (event.target.hasAttribute("data-close")) closeDetail();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !el.modal.hidden) closeDetail();
  });
}

init();
refreshAll();
