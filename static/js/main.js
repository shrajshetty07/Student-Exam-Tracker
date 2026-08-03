/* ============================================================
   EduTrack AI — main.js
   Theme toggle, mobile sidebar, toast notifications, small UX helpers
   ============================================================ */

(function () {
  "use strict";

  /* ---------------- Theme (Dark / Light) ---------------- */
  const THEME_KEY = "edutrack-theme";

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    const icon = document.getElementById("themeToggleIcon");
    if (icon) {
      icon.className = theme === "dark" ? "fa-solid fa-sun" : "fa-solid fa-moon";
    }
  }

  function initTheme() {
    const saved = window.__EDUTRACK_THEME__ || "light";
    applyTheme(saved);
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);
    document.cookie = `${THEME_KEY}=${next}; path=/; max-age=31536000`;
  }

  /* ---------------- Sidebar (mobile) ---------------- */
  function initSidebar() {
    const sidebar = document.getElementById("appSidebar");
    const toggleBtn = document.getElementById("sidebarToggleBtn");
    const overlay = document.getElementById("sidebarOverlay");
    if (!sidebar || !toggleBtn) return;

    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
      overlay?.classList.toggle("show");
    });
    overlay?.addEventListener("click", () => {
      sidebar.classList.remove("open");
      overlay.classList.remove("show");
    });
  }

  /* ---------------- Toasts ---------------- */
  function showToast(message, category) {
    const stack = document.getElementById("toastStack");
    if (!stack) return;

    const icons = {
      success: "fa-circle-check", danger: "fa-circle-exclamation",
      warning: "fa-triangle-exclamation", info: "fa-circle-info",
    };
    const cat = ["success", "danger", "warning", "info"].includes(category) ? category : "info";

    const el = document.createElement("div");
    el.className = `toast-item toast-${cat}`;
    el.innerHTML = `<i class="fa-solid ${icons[cat]}" style="margin-top:2px;"></i><div>${message}</div>`;
    stack.appendChild(el);

    setTimeout(() => {
      el.style.opacity = "0";
      el.style.transition = "opacity 0.3s ease";
      setTimeout(() => el.remove(), 300);
    }, 4200);
  }

  function initFlashToasts() {
    document.querySelectorAll("[data-flash]").forEach((node) => {
      showToast(node.dataset.flash, node.dataset.category);
    });
  }

  /* ---------------- Confirm delete ---------------- */
  function initConfirmForms() {
    document.querySelectorAll("form[data-confirm]").forEach((form) => {
      form.addEventListener("submit", (e) => {
        if (!window.confirm(form.dataset.confirm)) {
          e.preventDefault();
        }
      });
    });
  }

  /* ---------------- Debounced live search ---------------- */
  function initLiveSearch() {
    const input = document.querySelector("[data-live-search]");
    if (!input) return;
    let timer;
    input.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        input.closest("form")?.submit();
      }, 500);
    });
  }

  /* ---------------- Loading button state on submit ---------------- */
  function initSubmitLoading() {
    document.querySelectorAll("form").forEach((form) => {
      form.addEventListener("submit", () => {
        const btn = form.querySelector('button[type="submit"]');
        if (btn && !form.dataset.confirm) {
          btn.dataset.originalText = btn.innerHTML;
          btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Please wait...';
          btn.disabled = true;
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initSidebar();
    initFlashToasts();
    initConfirmForms();
    initLiveSearch();
    initSubmitLoading();

    document.getElementById("themeToggleBtn")?.addEventListener("click", toggleTheme);
  });

  window.EduTrack = { showToast };
})();
