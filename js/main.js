/* JANMED - Hospicjum Domowe
   Bez zależności. Trzy rzeczy: menu mobilne, scroll-reveal, notka o cookies. */

(function () {
  "use strict";

  /* ------------------------------------------------------------ menu -- */

  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
    });

    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        toggle.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        toggle.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
        toggle.focus();
      }
    });
  }

  /* --------------------------------------------------- scroll-reveal -- */

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var off = location.search.indexOf("noanim") > -1;
  var targets = document.querySelectorAll(".reveal");

  function showAll() {
    Array.prototype.forEach.call(targets, function (el) { el.classList.add("is-in"); });
  }

  if (reduce || off || !("IntersectionObserver" in window)) {
    Array.prototype.forEach.call(targets, function (el) { el.classList.add("is-in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-in");
        io.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -12% 0px", threshold: 0.06 });

    // Dwie klatki zwłoki na starcie: bez tego elementy widoczne od razu
    // dostają klasę zanim przeglądarka namaluje stan wyjściowy i pojawiają się
    // bez animacji - to dlatego „nie animowała się" góra strony.
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () {
        Array.prototype.forEach.call(targets, function (el) { io.observe(el); });
      });
    });

    // Bezpiecznik: treść nigdy nie może zostać niewidoczna przez animację.
    window.setTimeout(showAll, 3000);
  }

  /* ------------------------------------------------------ wideo hero -- */

  /* Ramka Vimeo wstaje dopiero z JS-a: nic nie leci do trzeciej strony przed
     pierwszym malowaniem, a przy prefers-reduced-motion nie leci wcale.
     Plakat jest pod spodem, więc brak filmu niczego nie psuje. */
  (function () {
    var media = document.querySelector(".hero__media[data-video]");
    if (!media) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    function start() {
      var frame = document.createElement("iframe");
      frame.src = media.getAttribute("data-video");
      frame.title = media.getAttribute("data-video-title") || "";
      frame.setAttribute("allow", "autoplay; fullscreen");
      frame.setAttribute("referrerpolicy", "strict-origin-when-cross-origin");
      frame.setAttribute("tabindex", "-1");
      frame.setAttribute("aria-hidden", "true");
      frame.setAttribute("loading", "lazy");

      /* Ramkę odsłaniamy dopiero wtedy, gdy odtwarzacz sam powie, że gra.
         Samo zdarzenie `load` odpala się także wtedy, gdy Vimeo zwróci 401
         (film ma whitelistę domen) - i wtedy zamiast filmu wjeżdżała plansza
         z błędem, dosunięta do lewej krawędzi kadru. Bez potwierdzenia
         zostaje plakat, który wygląda dokładnie tak, jak ma wyglądać. */
      var shown = false;
      function show() {
        if (shown) return;
        shown = true;
        media.classList.add("is-playing");
      }

      window.addEventListener("message", function (e) {
        if (String(e.origin).indexOf("player.vimeo.com") < 0) return;
        if (!frame.contentWindow || e.source !== frame.contentWindow) return;
        var data = e.data;
        if (typeof data === "string") {
          try { data = JSON.parse(data); } catch (err) { return; }
        }
        if (!data) return;
        if (data.event === "ready") {
          frame.contentWindow.postMessage(
            JSON.stringify({ method: "addEventListener", value: "play" }), "*");
          // Odtwarzacz wstał - pierwsza klatka jest kwestią chwili.
          window.setTimeout(show, 900);
        } else if (data.event === "play" || data.event === "playing") {
          show();
        }
      });

      media.appendChild(frame);
    }

    if ("requestIdleCallback" in window) {
      window.requestIdleCallback(start, { timeout: 2500 });
    } else {
      window.setTimeout(start, 900);
    }
  })();

  /* ------------------------------------------------ filtr ofert pracy -- */

  (function () {
    var bar = document.querySelector("[data-job-filters]");
    if (!bar) return;
    var cards = document.querySelectorAll(".job-card[data-places]");
    var empty = document.querySelector(".job-empty");
    if (!cards.length) return;

    bar.hidden = false;   // pasek istnieje tylko wtedy, gdy działa

    bar.addEventListener("click", function (e) {
      var btn = e.target.closest(".filter");
      if (!btn) return;
      var want = btn.getAttribute("data-filter");
      var shown = 0;

      Array.prototype.forEach.call(bar.querySelectorAll(".filter"), function (b) {
        var on = b === btn;
        b.classList.toggle("is-on", on);
        b.setAttribute("aria-pressed", String(on));
      });

      Array.prototype.forEach.call(cards, function (card) {
        var places = (card.getAttribute("data-places") || "").split("|");
        var ok = !want || places.indexOf(want) > -1;
        card.hidden = !ok;
        if (ok) shown++;
      });

      if (empty) empty.hidden = shown > 0;
      if (window.janmedTrack) window.janmedTrack("job_filter", { miejsce: want || "wszystkie" });
    });
  })();

  /* --------------------------------------------------- kopiuj e-mail -- */

  var CHECK = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true">' +
    '<path d="M3 8.5 6.2 11.7 13 4.9" stroke="currentColor" stroke-width="1.8" ' +
    'stroke-linecap="round" stroke-linejoin="round"/></svg>';

  function flash(note, text, state) {
    if (!note) return;
    note.innerHTML = (state === "error" ? "" : CHECK) + "<span>" + text + "</span>";
    note.setAttribute("data-state", state || "ok");
    note.classList.add("is-on");
    window.clearTimeout(note._t);
    note._t = window.setTimeout(function () { note.classList.remove("is-on"); }, 2600);
  }

  function legacyCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.cssText = "position:fixed;top:-1000px;opacity:0";
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-copy]");
    if (!btn) return;
    var value = btn.getAttribute("data-copy");
    var wrap = btn.closest(".copy-wrap") || btn.parentNode;
    var note = wrap.querySelector(".copy-note");

    function done() {
      flash(note, "Skopiowano adres e-mail", "ok");
      if (window.janmedTrack) window.janmedTrack("email_copy", { adres: value });
    }
    function fail() {
      flash(note, "Nie udało się skopiować - adres to " + value, "error");
    }

    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(value).then(done, function () {
        if (legacyCopy(value)) { done(); } else { fail(); }
      });
    } else if (legacyCopy(value)) {
      done();
    } else {
      fail();
    }
  });

  /* --------------------------------------------------------- cookies -- */

  var KEY = "janmed-cookies-ok";
  var notice = document.getElementById("cookie-notice");

  if (notice) {
    var stored = null;
    try { stored = window.localStorage.getItem(KEY); } catch (e) { stored = "1"; }

    if (!stored) {
      // pokazujemy dopiero po pierwszym malowaniu - bez skoku layoutu
      window.setTimeout(function () { notice.hidden = false; }, 700);
    }

    notice.addEventListener("click", function (e) {
      if (!e.target.closest("[data-cookie-accept]")) return;
      notice.hidden = true;
      try { window.localStorage.setItem(KEY, "1"); } catch (err) { /* prywatne okno */ }
    });
  }
})();
