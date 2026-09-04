/* JANMED - zdarzenia do Google Analytics 4.
 *
 * Odsłony liczy sam gtag. Tutaj dokładamy to, czego GA4 samo nie widzi:
 * kliknięcia w zrzutkę, telefony, maile, wejście w formularz i jego kroki.
 *
 * Zdarzenia, które lecą do GA4:
 *   donate_click      klik w link do zrzutki (skąd - parametr `miejsce`)
 *   phone_click       klik w numer telefonu (`placowka`, `numer`)
 *   email_click       klik w biuro@janmed.pl
 *   form_cta_click    klik w „Zgłoś pacjenta" (`miejsce`)
 *   form_open         otwarcie strony formularza
 *   form_start        wypełniający przeszedł z kroku 1 dalej
 *   form_step         każdy kolejny krok formularza (`krok`)
 *   form_submit       formularz wysłany
 *   (formularze rozróżnia parametr `rodzaj`: zgloszenie / rekrutacja,
 *    a przy rekrutacji dochodzi `oferta` - slug oferty pracy)
 *   article_read      przewinięcie artykułu do ~75%
 *
 * Uwaga: zdarzeń niestandardowych GA4 nie pokaże w raportach od razu -
 * trzeba je raz oznaczyć w panelu (Administracja → Zdarzenia / Kluczowe
 * zdarzenia), a parametry (`miejsce`, `krok`, …) dodać jako wymiary
 * niestandardowe. Szczegóły w README.
 */

(function () {
  "use strict";

  function track(name, params) {
    if (typeof window.gtag === "function") {
      window.gtag("event", name, params || {});
    }
  }
  window.janmedTrack = track;

  /* Skąd padło kliknięcie - nazwa sekcji, nagłówek albo stopka. */
  function where(el) {
    if (el.closest(".header")) return "naglowek";
    if (el.closest(".footer")) return "stopka";
    if (el.closest(".aside")) return "panel-boczny";
    if (el.closest(".hero")) return "hero";
    var sec = el.closest("section[id]");
    return sec ? sec.id : "tresc";
  }

  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[href]");
    if (!a) return;
    var href = a.getAttribute("href") || "";

    if (href.indexOf("zrzutka.pl") > -1) {
      track("donate_click", { miejsce: where(a), link_url: href });
    } else if (href.indexOf("tel:") === 0) {
      var card = a.closest(".card--contact");
      var head = card && card.querySelector("h3");
      track("phone_click", {
        miejsce: where(a),
        numer: href.replace("tel:", ""),
        placowka: head ? head.textContent.trim() : (a.textContent || "").trim()
      });
    } else if (href.indexOf("mailto:") === 0) {
      track("email_click", { miejsce: where(a) });
    } else if (href.indexOf("formularz-zgloszeniowy") > -1) {
      track("form_cta_click", { miejsce: where(a) });
    }
  });

  /* ------------------------------------------------- formularz (Tally) -- */

  var embed = document.querySelector(".form-embed, .apply[data-form]");
  if (embed && embed.querySelector("iframe")) {
    // Ten sam nasłuch obsługuje zgłoszenie pacjenta i aplikację o pracę -
    // różni je tylko `rodzaj` i numer oferty, po której ktoś aplikuje.
    var kind = embed.getAttribute("data-form") || "zgloszenie";
    var offer = embed.getAttribute("data-oferta") || "";
    function formTrack(name, params) {
      params = params || {};
      params.rodzaj = kind;
      if (offer) params.oferta = offer;
      track(name, params);
    }

    formTrack("form_open", {});

    var started = false;
    var frame = embed.querySelector("iframe");

    window.addEventListener("message", function (e) {
      var fromFrame = frame && e.source === frame.contentWindow;
      var fromTally = typeof e.origin === "string" && e.origin.indexOf("tally.so") > -1;
      if (!fromFrame && !fromTally) return;

      var data = e.data;
      if (typeof data === "string") {
        try { data = JSON.parse(data); } catch (err) { return; }
      }
      if (!data || typeof data.event !== "string") return;

      var payload = data.payload || {};

      if (data.event === "Tally.FormPageView") {
        var step = Number(payload.page || payload.pageIndex || 0);
        formTrack("form_step", { krok: step });
        if (!started && step > 1) {
          started = true;
          formTrack("form_start", {});
        }
      } else if (data.event === "Tally.FormSubmitted") {
        formTrack("form_submit", {});
      }
    });
  }

  /* ------------------------------------------- czytelność artykułu 75% -- */

  var article = document.querySelector("article .prose");
  if (article && "IntersectionObserver" in window) {
    var marker = document.createElement("div");
    marker.setAttribute("aria-hidden", "true");
    // Absolutnie, nie w przepływie: wersja z ujemnym `margin-top` skracała
    // kolumnę tekstu o 25% jej szerokości i zjadała dolny odstęp sekcji -
    // tło następnej sekcji ucinało się tuż pod ostatnim akapitem.
    marker.style.cssText =
      "position:absolute;left:0;right:0;bottom:25%;height:1px;pointer-events:none";
    article.appendChild(marker);

    var seen = false;
    var ro = new IntersectionObserver(function (entries) {
      if (seen || !entries.some(function (x) { return x.isIntersecting; })) return;
      seen = true;
      ro.disconnect();
      track("article_read", { artykul: document.title });
    });
    ro.observe(marker);
  }
})();
