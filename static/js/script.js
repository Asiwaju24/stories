// Small progressive enhancements. The site works without any of this.
document.addEventListener("DOMContentLoaded", () => {
  // Mobile menu
  const toggle = document.querySelector("[data-menu-toggle]");
  const nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  // Reading progress bar + text size (story pages only)
  const text = document.querySelector(".story-text");
  if (!text) return;

  const bar = document.getElementById("progress");
  if (bar) {
    const update = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (max > 0 ? Math.min(100, (window.scrollY / max) * 100) : 0) + "%";
    };
    window.addEventListener("scroll", update, { passive: true });
    update();
  }

  const KEY = "storytell-text-size";
  let size = 1.15;
  try { size = parseFloat(localStorage.getItem(KEY)) || size; } catch (e) {}
  const apply = () => {
    size = Math.max(0.95, Math.min(1.7, size));
    document.documentElement.style.setProperty("--read-size", size + "rem");
    try { localStorage.setItem(KEY, String(size)); } catch (e) {}
  };
  apply();
  document.querySelectorAll("[data-text-size]").forEach((btn) => {
    btn.addEventListener("click", () => {
      size += btn.dataset.textSize === "up" ? 0.1 : -0.1;
      apply();
    });
  });
});
