/* ═══════════════════════════════════════════════════════════════
   DocSummarizer — main.js
   Handles: form loading state, summary expand/collapse,
            auto-dismiss flash messages, progress feedback
═══════════════════════════════════════════════════════════════ */

// ── Loading overlay ───────────────────────────────────────────
(function () {
  const form = document.getElementById("processForm");
  if (!form) return;

  // Build loading overlay once
  const overlay = document.createElement("div");
  overlay.className = "loading-overlay";
  overlay.innerHTML = `
    <div class="loading-spinner"></div>
    <p class="loading-text" id="loadingMsg">Connecting to Google Drive…</p>
  `;
  document.body.appendChild(overlay);

  const messages = [
    "Connecting to Google Drive…",
    "Listing documents in folder…",
    "Downloading files…",
    "Extracting text content…",
    "Generating AI summaries…",
    "Almost done…",
  ];
  let msgIdx = 0;
  let msgTimer = null;

  function cycleMessages() {
    const el = document.getElementById("loadingMsg");
    if (!el) return;
    msgIdx = (msgIdx + 1) % messages.length;
    el.style.opacity = "0";
    setTimeout(() => {
      el.textContent = messages[msgIdx];
      el.style.transition = "opacity 0.4s";
      el.style.opacity = "1";
    }, 200);
  }

  form.addEventListener("submit", function (e) {
    const btn = document.getElementById("submitBtn");
    if (btn) {
      btn.disabled = true;
      const txt = btn.querySelector(".btn__text");
      if (txt) txt.textContent = "Processing…";
    }
    overlay.classList.add("active");
    msgTimer = setInterval(cycleMessages, 2800);
  });

  // Safety: if user navigates back, clear overlay
  window.addEventListener("pageshow", function () {
    overlay.classList.remove("active");
    if (msgTimer) clearInterval(msgTimer);
    const btn = document.getElementById("submitBtn");
    if (btn) btn.disabled = false;
  });
})();


// ── Expand / collapse summary text ───────────────────────────
function toggleExpand(id, btn) {
  const el = document.getElementById(id);
  if (!el) return;
  const expanded = el.classList.toggle("expanded");
  btn.textContent = expanded ? "Show less ▲" : "Show more ▼";
}

// Auto-expand all summaries that are short enough not to need a button
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".summary-text").forEach(function (el) {
    // If content doesn't overflow, remove the max-height constraint silently
    if (el.scrollHeight <= el.clientHeight + 4) {
      el.classList.add("expanded");
      const btn = el.nextElementSibling;
      if (btn && btn.classList.contains("expand-btn")) {
        btn.style.display = "none";
      }
    }
  });
});


// ── Auto-dismiss flash messages ───────────────────────────────
document.addEventListener("DOMContentLoaded", function () {
  const flashes = document.querySelectorAll(".flash");
  flashes.forEach(function (flash, i) {
    setTimeout(function () {
      flash.style.transition = "opacity 0.5s, transform 0.5s";
      flash.style.opacity = "0";
      flash.style.transform = "translateY(-4px)";
      setTimeout(function () { flash.remove(); }, 500);
    }, 4000 + i * 400);
  });
});


// ── Copy folder ID hint ───────────────────────────────────────
document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("folder_id");
  if (!input) return;
  input.addEventListener("paste", function (e) {
    // If pasted text looks like a full Drive URL, extract the folder ID
    setTimeout(function () {
      const val = input.value.trim();
      const match = val.match(/\/folders\/([a-zA-Z0-9_-]{10,})/);
      if (match) {
        input.value = match[1];
        input.style.borderColor = "var(--green)";
        setTimeout(() => { input.style.borderColor = ""; }, 1500);
      }
    }, 0);
  });
});
