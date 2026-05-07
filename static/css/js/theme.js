/* ── Theme switcher shared across all pages ──
   Reads saved preference from localStorage on load,
   and updates the <html> data-theme attribute when the user clicks a button. */

function setTheme(t) {
  /* Apply theme to the root element so CSS variables update */
  document.documentElement.setAttribute('data-theme', t === 'light' ? '' : t);
  /* Save choice so it persists when navigating between pages */
  localStorage.setItem('wq-theme', t);
  /* Update which button appears active */
  document.querySelectorAll('.theme-btn').forEach(b => b.classList.toggle('active', b.dataset.t === t));
}

/* Apply saved theme immediately on page load to avoid flash */
(function () { setTheme(localStorage.getItem('wq-theme') || 'light'); })();