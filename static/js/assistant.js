/* ============================================================
   SuccessAI — Frontend Interactions
   ------------------------------------------------------------
   Contents:
     1. Mobile nav toggle
     2. Scroll-reveal for cards / timeline steps
     3. Stat counter animation
     4. SHAP-style bar fill on scroll
     5. SuccessAI Assistant (chatbot)
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {

  /* ------------------------------------------------------------
     1. MOBILE NAV TOGGLE
     ------------------------------------------------------------ */
  const navToggle = document.getElementById("navToggle");
  const navLinks = document.getElementById("navLinks");

  if (navToggle && navLinks) {
    navToggle.addEventListener("click", function () {
      const isOpen = navLinks.classList.toggle("mobile-open");
      navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    // Close mobile nav after tapping a link
    navLinks.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        navLinks.classList.remove("mobile-open");
        navToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ------------------------------------------------------------
     2. SCROLL REVEAL (cards + timeline steps)
     ------------------------------------------------------------ */
  const revealTargets = document.querySelectorAll(".info-card, .timeline-step");

  if ("IntersectionObserver" in window && revealTargets.length) {
    const revealObserver = new IntersectionObserver(
      function (entries, observer) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("reveal");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 }
    );

    revealTargets.forEach(function (el) {
      revealObserver.observe(el);
    });
  } else {
    // Fallback: reveal everything immediately
    revealTargets.forEach(function (el) {
      el.classList.add("reveal");
    });
  }

  /* ------------------------------------------------------------
     3. STAT COUNTER ANIMATION
     ------------------------------------------------------------ */
  const statNums = document.querySelectorAll(".stat-num[data-target]");

  function animateCount(el) {
    const target = parseInt(el.getAttribute("data-target"), 10);
    const duration = 900;
    const start = performance.now();

    function tick(now) {
      const progress = Math.min((now - start) / duration, 1);
      const value = Math.floor(progress * target);
      el.textContent = value;
      if (progress < 1) {
        requestAnimationFrame(tick);
      } else {
        el.textContent = target;
      }
    }
    requestAnimationFrame(tick);
  }

  if ("IntersectionObserver" in window && statNums.length) {
    const statObserver = new IntersectionObserver(
      function (entries, observer) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            animateCount(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );
    statNums.forEach(function (el) {
      statObserver.observe(el);
    });
  }

  /* ------------------------------------------------------------
     4. SHAP-STYLE BAR FILL ON SCROLL
     ------------------------------------------------------------ */
  const shapFills = document.querySelectorAll(".shap-fill[data-width]");

  if ("IntersectionObserver" in window && shapFills.length) {
    const shapObserver = new IntersectionObserver(
      function (entries, observer) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            const width = entry.target.getAttribute("data-width");
            entry.target.style.width = width + "%";
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.4 }
    );
    shapFills.forEach(function (el) {
      shapObserver.observe(el);
    });
  } else {
    shapFills.forEach(function (el) {
      el.style.width = el.getAttribute("data-width") + "%";
    });
  }

  /* ==============================================================
     5. SUCCESSAI ASSISTANT (CHATBOT)
     ==============================================================
     This is a lightweight, frontend-only assistant using predefined
     responses. Routes are injected from Jinja via
     window.SUCCESSAI_ROUTES (see index.html) so this static file
     never has to guess a URL.

     TO UPGRADE TO A REAL AI API LATER:
     Replace the body of `getAssistantReply()` with a fetch() call to
     your backend (e.g. POST /assistant/ask), await the response, and
     return the reply text. Everything else (UI, quick actions,
     navigation matching) can stay exactly as-is.
     ============================================================== */

  const ROUTES = window.SUCCESSAI_ROUTES || {};

  const assistantBtn = document.getElementById("assistantBtn");
  const assistantPanel = document.getElementById("assistantPanel");
  const assistantClose = document.getElementById("assistantClose");
  const assistantBody = document.getElementById("assistantBody");
  const assistantInput = document.getElementById("assistantInput");
  const assistantSend = document.getElementById("assistantSend");
  const quickActionButtons = document.querySelectorAll(".quick-actions button");

  function openAssistant() {
    assistantPanel.classList.add("open");
    assistantBtn.setAttribute("aria-expanded", "true");
    assistantInput.focus();
  }

  function closeAssistant() {
    assistantPanel.classList.remove("open");
    assistantBtn.setAttribute("aria-expanded", "false");
  }

  if (assistantBtn) {
    assistantBtn.addEventListener("click", function () {
      const isOpen = assistantPanel.classList.contains("open");
      isOpen ? closeAssistant() : openAssistant();
    });
  }
  if (assistantClose) {
    assistantClose.addEventListener("click", closeAssistant);
  }

  function appendMessage(text, sender) {
    const msg = document.createElement("div");
    msg.className = "msg " + (sender === "user" ? "msg-user" : "msg-bot");
    msg.textContent = text;
    assistantBody.appendChild(msg);
    assistantBody.scrollTop = assistantBody.scrollHeight;
    return msg;
  }

  function navigateTo(url) {
    if (!url) return;
    window.setTimeout(function () {
      window.location.href = url;
    }, 500);
  }

  /**
   * Predefined knowledge base. Each entry has a list of trigger
   * phrases (matched with simple "includes" checks on the lowercased
   * input) and either a static reply, or an action that navigates
   * the user somewhere.
   */
  const KNOWLEDGE_BASE = [
    {
      triggers: ["how does successai work", "how does it work", "how it works"],
      reply:
        "SuccessAI analyzes academic and behavioral indicators, processes the data and uses machine learning to predict student performance."
    },
    {
      triggers: ["what features are used", "features used", "what features"],
      reply:
        "SuccessAI looks at 8 indicators: attendance, internal marks, assignment marks, study hours, previous SGPA, backlogs, lab performance and participation."
    },
    {
      triggers: ["random forest"],
      reply:
        "Random Forest is one of SuccessAI's five models. It combines multiple decision trees and averages their results for a more robust prediction."
    },
    {
      triggers: ["what is shap", "shap"],
      reply:
        "SHAP is an explainable AI technique that helps identify how individual features influenced a model's prediction."
    },
    {
      triggers: ["decision tree"],
      reply: "Decision Tree uses a tree-like structure of decision rules to classify student performance."
    },
    {
      triggers: ["knn", "k-nearest"],
      reply: "KNN predicts performance by finding similar students in the training dataset."
    },
    {
      triggers: ["logistic regression"],
      reply: "Logistic Regression uses relationships between input features to classify student performance."
    },
    {
      triggers: ["svm", "support vector"],
      reply: "SVM finds a decision boundary that separates different student performance classes."
    },
    {
      triggers: ["recommend", "recommendation"],
      reply:
        "After a prediction, SuccessAI generates personalized recommendations based on that student's specific indicators."
    },
    {
      triggers: ["explainable", "explain ai", "xai"],
      reply:
        "Explainable AI means SuccessAI doesn't just give a prediction — it shows which features influenced that prediction, so the result is transparent."
    },
    {
      triggers: ["login", "log in", "sign in"],
      reply: "Taking you to the login page now.",
      action: function () { navigateTo(ROUTES.login); }
    },
    {
      triggers: [
        "start prediction",
        "take me to prediction",
        "open prediction",
        "predict",
        "prediction page",
        "make a prediction"
      ],
      reply: "Opening the prediction page for you.",
      action: function () { navigateTo(ROUTES.prediction); }
    },
    {
      triggers: [
        "model analysis",
        "take me to model",
        "open model",
        "models",
        "model comparison",
        "compare models"
      ],
      reply: "Opening model analysis for you.",
      action: function () { navigateTo(ROUTES.models); }
    },
    {
      triggers: ["home", "take me home", "go home", "landing page"],
      reply: "Taking you to the home page.",
      action: function () { navigateTo(ROUTES.home); }
    },
  ];

  const FALLBACK_REPLY =
    "I'm not sure about that one yet. Try asking about how SuccessAI works, the ML models, SHAP/explainable AI, or say \"start prediction\" to jump right in.";

  function getAssistantReply(rawInput) {
    const input = rawInput.trim().toLowerCase();

    for (let i = 0; i < KNOWLEDGE_BASE.length; i++) {
      const entry = KNOWLEDGE_BASE[i];
      const matched = entry.triggers.some(function (phrase) {
        return input.includes(phrase);
      });
      if (matched) {
        return entry;
      }
    }
    return { reply: FALLBACK_REPLY };
  }

  function handleUserMessage(text) {
    if (!text || !text.trim()) return;

    appendMessage(text, "user");
    assistantInput.value = "";

    const entry = getAssistantReply(text);

    // Small delay so the reply feels conversational rather than instant
    window.setTimeout(function () {
      appendMessage(entry.reply, "bot");
      if (typeof entry.action === "function") {
        entry.action();
      }
    }, 350);
  }

  if (assistantSend) {
    assistantSend.addEventListener("click", function () {
      handleUserMessage(assistantInput.value);
    });
  }

  if (assistantInput) {
    assistantInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        handleUserMessage(assistantInput.value);
      }
    });
  }

  quickActionButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      handleUserMessage(btn.getAttribute("data-q"));
    });
  });

});
