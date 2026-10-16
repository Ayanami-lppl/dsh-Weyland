/* ══════════════════════════════════════════════════════════════
   splash.js — timeline host for the WEYLAND-YUTANI boot sequence

   ?dur=8000   master duration in ms
   ?t=4200     freeze the whole timeline at that instant (visual QA)
   ?loop=1     replay after finishing, when not hosted by pywebview
   ══════════════════════════════════════════════════════════════ */

(() => {
  "use strict";

  const q = new URLSearchParams(location.search);
  const DUR = Math.max(1000, Number(q.get("dur")) || 8000);

  if (DUR !== 8000) {
    document.documentElement.style.setProperty("--crt", DUR + "ms");
  }

  const all = () => document.getAnimations();

  /* Freeze every animation at an absolute time — used by the visual
     QA harness and by nothing else. */
  function seek(t) {
    for (const a of all()) {
      try {
        a.pause();
        a.currentTime = t;
      } catch (_) { /* an animation that already finished and was GC'd */ }
    }
  }

  let finished = false;

  function finish() {
    if (finished) return;
    finished = true;
    /* The host polls this flag rather than relying on the js_api bridge. */
    window.__splashFinished = true;
    document.documentElement.dataset.splashDone = "1";
    if (q.get("loop") && !(window.pywebview && window.pywebview.api)) {
      setTimeout(() => location.reload(), 500);
    }
  }

  const frozen = q.get("t");
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

  window.addEventListener("load", () => {
    if (frozen !== null) {
      requestAnimationFrame(() => requestAnimationFrame(() => seek(Number(frozen) || 0)));
      return;
    }
    setTimeout(finish, reduced ? 1200 : DUR + 60);
  });

  /* exposed for the QA harness */
  window.__seek = seek;
  window.__finish = finish;
  window.__duration = DUR;
})();
