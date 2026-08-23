/* ==========================================================================
   SUCCESSAI — AUTH INTERACTIONS
   Shared by login.html and register.html.
   No framework, no backend calls — purely presentational.
   ========================================================================== */
(function () {
  "use strict";

  var prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  /* ------------------------------------------------------------------
     1. Password visibility toggles
     ------------------------------------------------------------------ */
  document.querySelectorAll("[data-pw-toggle]").forEach(function (btn) {
    var targetId = btn.getAttribute("data-pw-toggle");
    var input = document.getElementById(targetId);
    if (!input) return;

    btn.addEventListener("click", function () {
      var showing = input.type === "text";
      input.type = showing ? "password" : "text";
      btn.setAttribute("data-visible", String(!showing));
      btn.setAttribute("aria-pressed", String(!showing));
      btn.setAttribute("aria-label", showing ? "Show password" : "Hide password");
    });
  });

  /* ------------------------------------------------------------------
     2. Password strength meter (register page only — purely frontend,
        never touches the value that gets submitted to Flask)
     ------------------------------------------------------------------ */
  var strengthInput = document.querySelector("[data-pw-strength-input]");
  var strengthMeter = document.querySelector("[data-pw-strength-meter]");

  if (strengthInput && strengthMeter) {
    var fill = strengthMeter.querySelector("[data-pw-strength-fill]");
    var label = strengthMeter.querySelector("[data-pw-strength-label]");

    var levels = [
      { min: 0, pct: 0, text: "", color: "var(--error)" },
      { min: 1, pct: 30, text: "Weak", color: "var(--error)" },
      { min: 2, pct: 60, text: "Medium", color: "var(--warn)" },
      { min: 3, pct: 85, text: "Strong", color: "var(--cyan)" },
      { min: 4, pct: 100, text: "Very strong", color: "var(--success)" }
    ];

    function scorePassword(value) {
      var score = 0;
      if (value.length >= 8) score++;
      if (/[A-Z]/.test(value) && /[a-z]/.test(value)) score++;
      if (/\d/.test(value)) score++;
      if (/[^A-Za-z0-9]/.test(value)) score++;
      return score;
    }

    strengthInput.addEventListener("input", function () {
      var value = strengthInput.value;

      if (!value) {
        strengthMeter.classList.remove("is-active");
        return;
      }

      strengthMeter.classList.add("is-active");
      var score = scorePassword(value);
      var level = levels[Math.min(score, levels.length - 1)];
      fill.style.width = level.pct + "%";
      fill.style.background = level.color;
      label.textContent = level.text || "Weak";
    });
  }

  /* ------------------------------------------------------------------
     3. Flash message tone detection
        get_flashed_messages() is called without categories, so we infer
        a tone from common wording to pick success / error / info styling
        and give registration/login acknowledgements the right feel.
        (If categorized flashes are added later, prefer those instead.)
     ------------------------------------------------------------------ */
  var SUCCESS_HINTS = ["success", "created", "welcome", "logged in", "registered", "account created"];
  var ERROR_HINTS = ["invalid", "incorrect", "error", "failed", "already exists", "not found", "wrong"];

  document.querySelectorAll("[data-flash-message]").forEach(function (el) {
    var text = el.textContent.toLowerCase();
    var tone = "info";

    if (SUCCESS_HINTS.some(function (w) { return text.indexOf(w) !== -1; })) {
      tone = "success";
    } else if (ERROR_HINTS.some(function (w) { return text.indexOf(w) !== -1; })) {
      tone = "error";
    }

    el.setAttribute("data-tone", tone);

    var successIcon = el.querySelector("[data-icon-success]");
    var errorIcon = el.querySelector("[data-icon-error]");
    var infoIcon = el.querySelector("[data-icon-info]");
    [successIcon, errorIcon, infoIcon].forEach(function (icon) {
      if (icon) icon.style.display = "none";
    });
    var activeIcon = tone === "success" ? successIcon : tone === "error" ? errorIcon : infoIcon;
    if (activeIcon) activeIcon.style.display = "block";
  });

  /* ------------------------------------------------------------------
     4. Login <-> Register page transition
        These are separate Flask routes/templates, so instead of a true
        SPA slide we animate the card out on click, then navigate — and
        the incoming page's own load animation (see login.css
        shellEnter/panelIn) completes the illusion of one continuous move.
     ------------------------------------------------------------------ */
  var shell = document.querySelector("[data-auth-shell]");

  document.querySelectorAll("[data-auth-nav]").forEach(function (link) {
    link.addEventListener("click", function (e) {
      if (!shell || prefersReducedMotion) return; // let it navigate immediately
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return; // respect new-tab clicks

      e.preventDefault();
      var href = link.getAttribute("href");
      shell.classList.add("is-leaving");

      window.setTimeout(function () {
        window.location.href = href;
      }, 380);
    });
  });
})();
