// Runs a demo: each message through lookup, Jev checks and serve/miss, plus controls and routing.
/* ---- one message through the guard ---- */
function messagesSoFar(side) {
  return turnsOf().slice(0, state.idx + 1).filter(t => t.side === side).length * 2 - 1;
}

async function generate(t, reply, why) {
  const typing = addTyping(t.side, "Sonnet 5.5 is writing…");
  await narrate(typing, `${why} So the main model writes the answer: about ${Math.round(t.llmSec)} seconds and <b>$${PRICE.turn.toFixed(4)}</b>.`);
  typing.remove();
  addBubble(t.side, "bot", `${esc(reply)}<div class="badge"><span>Sonnet 5.5</span><span>${t.llmSec.toFixed(1)} s</span><span>$${PRICE.turn.toFixed(4)}</span></div>`);
  state.llm++;
  renderScores();
  await sleep(350);
  const entry = storeEntry(t, reply, messagesSoFar(t.side));
  addStep(`<div class="sh"><span>Stored in cache</span><span class="k">store(entry, reply)</span></div><div class="q">Saved against <b>“${esc(t.user)}”</b>, with a snapshot of the conversation.</div>`);
  await narrate(entry, state.stored++
    ? `${userLabel(t.side)}'s answer goes into the cache too.`
    : `The answer is stored in the cache, with a snapshot of the conversation, ready for the next person who asks.`);
}

async function runTurn(t, n) {
  const who = userLabel(t.side);
  const ub = addBubble(t.side, "user", esc(t.user));
  if (state.idx > 0) await sleep(300);
  await narrate(ub, n === 1 && t.side === "L"
    ? `${who} asks MyGym's support bot a question. Before calling the model, the bot checks the cache.`
    : `${who} sends a message. Every message is checked against the cache first.`);

  startTrace(t, n);
  state.guard += PRICE.facts;
  renderScores();

  const cached = t.cand && state.cache[t.cand];
  const lookup = addStep(`<div class="sh"><span>Embedding lookup</span><span class="k">candidates(final message, k=3)</span></div><div class="q">Searching the cache for messages within 0.70 similarity of <b>“${esc(t.user)}”</b>…</div>`);
  await sleep(600);

  if (!cached) {
    const empty = !Object.keys(state.cache).length;
    lookup.querySelector(".q").innerHTML = empty ? `The cache is empty. Nothing for Jev to check.` : `No cached message is close enough. Nothing for Jev to check.`;
    setTurnPill("miss", "MISS");
    await narrate(lookup, empty ? `The cache is empty, so there's nothing to reuse yet.` : `Nothing in the cache is close to this message, so there's nothing to reuse.`);
    await generate(t, t.reply, "Cache miss.");
    return;
  }

  const cwho = userLabel(cached.t.side);
  lookup.querySelector(".q").innerHTML = `1 candidate from ${cwho}: <b>“${esc(cached.t.user)}”</b> at <b>${t.sim.toFixed(2)}</b> similarity.`;
  flagEntry(t.cand, "cand");
  state.guard += PRICE.candidate;
  renderScores();
  await narrate(lookup, t.sim >= 0.995
    ? `The embedding search finds ${cwho}'s message: <b>the exact same words</b>, 1.00 similarity. A plain cache would serve it on the spot.`
    : `The embedding search finds a similar message from ${cwho}, at <b>${t.sim.toFixed(2)}</b> similarity. Similar isn't the same as safe to reuse, so Jev checks.`);

  // what a plain last-message cache would do with this candidate
  const plainServes = t.sim >= PLAIN_T;
  const fits = t.whole >= WHOLE_T && t.rw >= RW_T;
  state.plain.seen++;
  if (plainServes) { state.plain.served++; if (!fits) state.plain.wrong++; }
  else if (fits) state.plain.missedSaves++;
  renderScores();

  const whole = await jevStep("whole conversation",
    `Would the reply cached for ${cwho}'s chat be correct for this chat, given everything said earlier in both?`, t.whole, WHOLE_T);
  await narrate(whole.el, whole.ok
    ? `Jev reads both whole conversations and answers one yes/no question: would the cached reply be right here? <b>${t.whole.toFixed(2)}</b>, above the 0.70 bar.`
    : `Jev reads both whole conversations: <b>${t.whole.toFixed(2)}</b>, well below the 0.70 bar. Something said earlier changes the answer.`);

  let serve = false;
  if (whole.ok) {
    const rw = addStep(`<div class="sh"><span>Haiku 4.5 rewrites both sides</span><span class="k">standalone requests</span></div><div class="q">Turning each final message into a request that makes sense on its own…</div>`);
    await sleep(700);
    const [a, b] = t.rewrites;
    const failing = t.rw < RW_T;
    rw.querySelector(".q").outerHTML = `<div class="rw"><div><small>${cwho} (cached)</small>${failing ? markDiff(b, a) : esc(a)}</div><div><small>${who} (new)</small>${failing ? markDiff(a, b) : esc(b)}</div></div>`;
    scrollEnd($("trace"));
    await narrate(rw, failing
      ? `A second check: Haiku rewrites each final message as a standalone request, spelling out what earlier messages meant. Now the difference is visible.`
      : `A second check: Haiku rewrites each final message as a standalone request, spelling out what earlier messages meant.`);
    const r = await jevStep("standalone rewrites",
      `Would the answer to the cached request be a correct and complete answer to the new one?`, t.rw, RW_T);
    serve = r.ok;
    await narrate(r.el, serve
      ? `Jev on the rewrites: <b>${t.rw.toFixed(2)}</b>, above the 0.15 bar. Both checks pass.`
      : `Jev on the rewrites: <b>${t.rw.toFixed(2)}</b>. No: these are different requests.`);
  }

  if (serve) {
    flagEntry(t.cand, "served");
    const pill = setTurnPill("hit", "HIT · SERVED");
    if (t.note) await narrate(pill, esc(t.note));
    const b = addBubble(t.side, "bot cached", `${esc(cached.reply)}<div class="badge"><span>⚡ served from cache</span><span>${t.guardSec.toFixed(1)} s</span><span>saved $${PRICE.turn.toFixed(4)}</span></div>`);
    state.saved += PRICE.turn;
    state.hits++;
    flyCoin(b, "+$" + PRICE.turn.toFixed(4));
    await sleep(reduced ? 0 : 850);
    renderScores();
    bumpMoney();
    await narrate(b, `${who} gets ${cwho}'s answer in ${t.guardSec.toFixed(1)} seconds, with no model call. <b>$${PRICE.turn.toFixed(4)} saved.</b>`);
  } else {
    flagEntry(t.cand, "rejected");
    const pill = setTurnPill("block", "BLOCKED · MISS");
    state.blocked++;
    renderScores();
    if (t.note) await narrate(pill, esc(t.note));
    if (t.ghost && plainServes) {
      const g = addBubble(t.side, "ghost", `<div class="gl">A plain semantic cache would have sent</div><div class="gt">${esc(cached.reply)}</div><div class="gw">${esc(t.ghost)}</div>`);
      await narrate(g, `A plain semantic cache matches on the last message alone, so it would have sent this to ${who}.`);
    }
    await generate(t, t.reply, "The cached answer is blocked.");
  }
}

async function play() {
  if (state.playing) return;
  if (state.idx >= turnsOf().length) reset();
  state.playing = true; syncButtons();
  const run = state.run;
  try {
    while (state.idx < turnsOf().length) {
      const t = turnsOf()[state.idx];
      const n = turnsOf().slice(0, state.idx + 1).filter(x => x.side === t.side).length;
      await runTurn(t, n);
      state.idx++;
    }
    flagEntry(null);
    await narrate(moneyEl(), `Done. <b>${state.hits}</b> answer${state.hits === 1 ? "" : "s"} served from cache, <b>${state.blocked}</b> wrong answer${state.blocked === 1 ? "" : "s"} blocked, <b>${money(state.saved - state.guard)}</b> saved after paying for the guard.`);
  } catch (e) {
    if (e !== ABORT) throw e;
  } finally {
    if (run === state.run) { state.playing = false; syncButtons(); }
  }
}

function syncButtons() {
  const done = state.idx >= turnsOf().length;
  $("play").textContent = state.playing ? "Running" : done ? "Replay" : "Start";
  $("play").disabled = state.playing;
  $("speed").hidden = state.mode !== "auto";
}

function reset() {
  state.run++;
  if (state.abortWait) state.abortWait(ABORT);
  state.advance = state.abortWait = null;
  hideCallout();
  Object.assign(state, { idx: 0, playing: false, saved: 0, guard: 0, hits: 0, llm: 0, blocked: 0, stored: 0,
    plain: { served: 0, wrong: 0, seen: 0, missedSaves: 0 }, cache: {} });
  const sc = SCENARIOS[state.key];
  $("intro").innerHTML = sc.intro;
  $("bot-l").textContent = sc.bot;
  $("bot-r").textContent = sc.bot;
  $("msgs-L").innerHTML = `<div class="empty">Click anywhere or press space to start.</div>`;
  $("msgs-R").innerHTML = `<div class="empty">User 2 starts after User 1.</div>`;
  $("trace").innerHTML = `<div class="empty">Each lookup appears here: the candidate the embedding search found, then Jev's two yes/no checks.</div>`;
  $("cache-list").innerHTML = "";
  document.querySelectorAll(".coin").forEach(c => c.remove());
  turnEl = null;
  renderCacheCount();
  renderScores();
  syncButtons();
}

function writeHash() {
  const h = state.key + (state.stage ? "-stage" : "");
  if (location.hash.slice(1) !== h) history.replaceState(null, "", "#" + h);
}
function choose(key) {
  if (!SCENARIOS[key]) key = "demo-1";
  state.key = key;
  document.querySelectorAll(".tab").forEach(t => t.setAttribute("aria-selected", String(t.dataset.s === key)));
  document.querySelectorAll(".corner [data-s]").forEach(t => t.setAttribute("aria-pressed", String(t.dataset.s === key)));
  writeHash();
  restart();
}
// every start opens on the first speech bubble, with no click needed
function restart() {
  reset();
  play();
}
function setView(stage) {
  state.stage = stage;
  document.body.classList.toggle("stage-only", stage);
  writeHash();
}
function fromHash(initial) {
  const h = location.hash.slice(1);
  const stage = initial === true || h.endsWith("-stage");
  const key = h.endsWith("-stage") ? h.slice(0, -6) : h;
  setView(stage);
  if (initial === true || key !== state.key) choose(key || "demo-1");
}

document.querySelectorAll(".tab, .corner [data-s]").forEach(t => t.addEventListener("click", () => choose(t.dataset.s)));
$("play").addEventListener("click", play);
$("reset").addEventListener("click", restart);
$("c-reset").addEventListener("click", restart);
$("view").addEventListener("click", () => setView(true));
$("c-view").addEventListener("click", () => setView(false));
$("mode").addEventListener("change", e => { state.mode = e.target.value; syncButtons(); });
$("speed").addEventListener("change", e => { state.speed = parseFloat(e.target.value); });
$("scale-1").addEventListener("click", () => { state.scale = 1; $("scale-1").setAttribute("aria-pressed", "true"); $("scale-m").setAttribute("aria-pressed", "false"); renderScores(); });
$("scale-m").addEventListener("click", () => { state.scale = 1e6; $("scale-m").setAttribute("aria-pressed", "true"); $("scale-1").setAttribute("aria-pressed", "false"); renderScores(); });

// click anywhere (outside the controls) to move the story on
document.addEventListener("click", e => {
  if (e.target.closest(".top, .scores, .corner, select, button, a")) return;
  if (advance()) return;
  if (!state.playing) play();
});
document.addEventListener("keydown", e => {
  if (e.target.closest("select, input, textarea")) return;
  if (e.key === " " || e.key === "ArrowRight" || e.key === "Enter") {
    e.preventDefault();
    if (!advance() && !state.playing) play();
  } else if (e.key === "r" || e.key === "R") restart();
  else if (e.key === "v" || e.key === "V") setView(!state.stage);
  else if (e.key === "1" || e.key === "2") choose("demo-" + e.key);
});
addEventListener("hashchange", () => fromHash(false));

fromHash(true);
