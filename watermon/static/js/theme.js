function setTheme(t) {
  document.documentElement.setAttribute('data-theme', t === 'light' ? '' : t);
  localStorage.setItem('wq-theme', t);
  document.querySelectorAll('.theme-btn').forEach(b => b.classList.toggle('active', b.dataset.t === t));
}

(function () { setTheme(localStorage.getItem('wq-theme') || 'light'); })();