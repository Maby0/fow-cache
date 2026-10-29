// Page state and rendering: narrator bubbles, chat panels, guard trace, cache list, scores.
const $ = id => document.getElementById(id);
const ABORT = Symbol("abort");
const state = { key: "demo-1", stage: false, idx: 0, run: 0, playing: false, mode: "click", speed: 1, scale: 1, advance: null, abortWait: null,
  saved: 0, guard: 0, hits: 0, llm: 0, blocked: 0, stored: 0, plain: { served: 0, wrong: 0, seen: 0, missedSaves: 0 }, cache: {} };

const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
const turnsOf = () => SCENARIOS[state.key].turns;

function sleep(ms) {
  const id = state.run;
  const factor = state.mode === "auto" ? state.speed : 1;
  return new Promise((res, rej) => setTimeout(() => id === state.run ? res() : rej(ABORT), ms / factor));
}
const esc = s => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const money = v => {
  const x = Math.abs(v * state.scale), sign = v < -1e-9 ? "−" : "";
  return sign + "$" + (state.scale === 1 ? x.toFixed(4) : Math.round(x).toLocaleString("en-US"));
};
const userLabel = side => side === "L" ? "User 1" : "User 2";
const scrollEnd = el => { el.scrollTop = el.scrollHeight; };
const clearEmpty = el => { const e = el.querySelector(":scope > .empty"); if (e) e.remove(); };

/* ---- narrator: a speech bubble pinned to whatever just happened ---- */
const say = { el: null, target: null, raf: 0 };

function hideCallout() {
  cancelAnimationFrame(say.raf);
  if (say.el) say.el.remove();
  if (say.target) say.target.classList.remove("focus-ring");
  say.el = say.target = null;
}
function placeCallout() {
  const c = say.el, t = say.target;
  if (!c || !t) return;
  const r = t.getBoundingClientRect(), cw = c.offsetWidth, ch = c.offsetHeight, vw = innerWidth, vh = innerHeight, gap = 12;
  const below = r.bottom + gap + ch <= vh - 8 || r.top - gap - ch < 8;
  const top = Math.max(8, Math.min(vh - ch - 8, below ? r.bottom + gap : r.top - gap - ch));
  const left = Math.max(8, Math.min(vw - cw - 8, r.left + r.width / 2 - cw / 2));
  c.style.transform = `translate(${left}px, ${top}px)`;
  c.dataset.side = below ? "below" : "above";
  c.style.setProperty("--tail-x", Math.max(16, Math.min(cw - 16, r.left + r.width / 2 - left)) + "px");
  say.raf = requestAnimationFrame(placeCallout);
}
function waitAdvance() {
  return new Promise((res, rej) => { state.advance = res; state.abortWait = rej; });
}
async function narrate(target, html) {
  hideCallout();
  const c = document.createElement("div");
  c.className = "callout";
  c.setAttribute("role", "status");
  c.innerHTML = `<div class="ct">${html}</div><div class="hint">${state.mode === "click" ? "click to continue ▸" : ""}</div><span class="tail"></span>`;
  document.body.appendChild(c);
  say.el = c; say.target = target;
  target.classList.add("focus-ring");
  placeCallout();
  const run = state.run;
  try {
    if (state.mode === "click") await waitAdvance();
    else await Promise.race([waitAdvance(), sleep(1600 + html.replace(/<[^>]+>/g, "").length * 32)]);
  } finally {
    state.advance = null;
    if (run === state.run) hideCallout();
  }
}
function advance() {
  if (!state.advance) return false;
  const a = state.advance; state.advance = null; a();
  return true;
}

/* ---- chat panels ---- */
function addBubble(side, cls, html) {
  const box = $("msgs-" + side);
  clearEmpty(box);
  const b = document.createElement("div");
  b.className = "b " + cls;
  b.innerHTML = html;
  box.appendChild(b);
  scrollEnd(box);
  return b;
}
function addTyping(side, label) {
  const box = $("msgs-" + side);
  const t = document.createElement("div");
  t.className = "typing";
  t.innerHTML = `<span class="dots"><i></i><i></i><i></i></span>${esc(label)}`;
  box.appendChild(t);
  scrollEnd(box);
  return t;
}

/* ---- guard trace ---- */
let turnEl = null;
function startTrace(t, n) {
  const tr = $("trace");
  clearEmpty(tr);
  tr.querySelectorAll(".turn").forEach(el => el.classList.add("collapsed"));
  turnEl = document.createElement("div");
  turnEl.className = "turn";
  turnEl.innerHTML = `<div class="th"><span>${userLabel(t.side)} <span class="who">· message ${n}</span></span><span class="pill run">checking</span></div><div class="steps"></div>`;
  const el = turnEl;
  el.querySelector(".th").addEventListener("click", e => { if (!state.advance) { e.stopPropagation(); el.classList.toggle("collapsed"); } });
  tr.appendChild(turnEl);
  scrollEnd(tr);
}
function setTurnPill(kind, text) {
  const p = turnEl.querySelector(".pill");
  p.className = "pill " + kind;
  p.textContent = text;
  return p;
}
function addStep(html, cls = "") {
  const s = document.createElement("div");
  s.className = "step " + cls;
  s.innerHTML = html;
  turnEl.querySelector(".steps").appendChild(s);
  scrollEnd($("trace"));
  return s;
}
async function jevStep(title, question, p, threshold) {
  const s = addStep(`
    <div class="sh"><span class="name">Jev · ${title}</span><span class="k">yes/no, calibrated</span></div>
    <div class="q">${question}</div>
    <div class="gauge"><div class="gfill"></div><div class="gtick" style="left:${threshold * 100}%"></div></div>
    <div class="gmeta"><span>p(yes) <span class="p">0.00</span></span><span>needs ≥ ${threshold.toFixed(2)}</span></div>`, "jev");
  await sleep(120);
  s.querySelector(".gfill").style.width = (p * 100) + "%";
  const pEl = s.querySelector(".p");
  for (let i = 1; i <= 14; i++) { pEl.textContent = (p * i / 14).toFixed(2); await sleep(45); }
  const ok = p >= threshold;
  const v = document.createElement("div");
  v.className = "verdict " + (ok ? "ok" : "no");
  v.textContent = ok ? "Yes: the cached answer fits" : "No: the cached answer would be wrong";
  s.appendChild(v);
  scrollEnd($("trace"));
  await sleep(200);
  return { ok, el: s };
}
function markDiff(a, b) {
  const norm = w => w.toLowerCase().replace(/[^a-z0-9£]/g, "");
  const set = new Set(a.split(/\s+/).map(norm));
  return b.split(/\s+/).map(w => set.has(norm(w)) ? esc(w) : `<mark>${esc(w)}</mark>`).join(" ");
}

/* ---- cache list ---- */
function renderCacheCount() {
  const n = Object.keys(state.cache).length;
  $("cache-count").textContent = n + (n === 1 ? " entry" : " entries");
  if (!n) $("cache-list").innerHTML = `<div class="empty" style="margin:4px 0">Empty</div>`;
}
function storeEntry(t, reply, msgCount) {
  const list = $("cache-list");
  clearEmpty(list);
  const e = document.createElement("div");
  e.className = "entry";
  e.id = "entry-" + t.id;
  e.innerHTML = `<span class="ek">“${esc(t.user)}”</span><span class="ea">→ ${esc(reply)}</span><span class="em">from ${userLabel(t.side)} · answer + snapshot of ${msgCount} message${msgCount === 1 ? "" : "s"}</span>`;
  list.prepend(e);
  list.parentElement.scrollTop = 0;
  state.cache[t.id] = { t, reply };
  renderCacheCount();
  return e;
}
function flagEntry(id, cls) {
  document.querySelectorAll(".entry").forEach(e => e.classList.remove("cand", "served", "rejected"));
  const e = $("entry-" + id);
  if (e && cls) { e.classList.add(cls); e.scrollIntoView({ block: "nearest" }); }
  return e;
}

/* ---- scores ---- */
function renderScores() {
  const net = money(state.saved - state.guard);
  $("net").textContent = net;
  $("stage-net").textContent = net;
  $("stage-hits").textContent = `${state.hits} from cache · ${state.blocked} blocked`;
  $("net-sub").textContent = `LLM calls avoided ${money(state.saved)} − guard ${money(state.guard)}`;
  $("hits").textContent = state.hits;
  $("hits-sub").textContent = `${state.llm} full LLM call${state.llm === 1 ? "" : "s"}`;
  $("blocked").textContent = state.blocked;
  const p = state.plain;
  if (!p.seen) { $("plain").textContent = "Not run yet"; return; }
  let html = `${p.served} served`;
  html += p.wrong ? `, <span class="bad">${p.wrong} wrong</span>` : ", 0 wrong";
  if (p.missedSaves) html += `, ${p.missedSaves} saving missed`;
  $("plain").innerHTML = html;
}
const moneyEl = () => state.stage ? $("stage-saved") : $("money-tile");
function bumpMoney() {
  const el = moneyEl();
  el.classList.remove("bump"); void el.offsetWidth; el.classList.add("bump");
}
function flyCoin(fromEl, text) {
  if (reduced) return;
  const r = fromEl.getBoundingClientRect(), to = moneyEl().getBoundingClientRect();
  const c = document.createElement("div");
  c.className = "coin";
  c.textContent = text;
  c.style.left = (r.left + 12) + "px";
  c.style.top = (r.top + 8) + "px";
  document.body.appendChild(c);
  requestAnimationFrame(() => requestAnimationFrame(() => {
    c.style.transform = `translate(${to.left + 20 - r.left}px, ${to.top + 10 - r.top}px) scale(.8)`;
    c.style.opacity = "0.15";
  }));
  setTimeout(() => c.remove(), 1000);
}
