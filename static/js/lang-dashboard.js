// Simple client-side filter for built-ins table (supports single or grouped layouts)
(function(){
  const input = document.getElementById('bi-filter');
  const count = document.getElementById('bi-count');
  const body = document.getElementById('bi-body');
  if (!body) return;

  let group = 'all';
  const tabBtns = Array.from(document.querySelectorAll('[data-bi-tab]'));

  const getRows = () => Array.from(body.querySelectorAll('[data-row]'));

  const getQuery = () => ((input && input.value) || '').toLowerCase().trim();

  const update = () => {
    const rows = getRows();
    const q = getQuery();
    let visible = 0;
    rows.forEach(tr => {
      const text = tr.innerText.toLowerCase();
      // Determine group with robust fallback based on Kind column
      let rowGroup = tr.dataset.group;
      if (!rowGroup) {
        const kindCell = tr.children && tr.children[1] ? tr.children[1].innerText.toLowerCase() : '';
        if (/\b(method|member)\b/.test(kindCell)) rowGroup = 'methods';
        else if (/\b(class|type|enum|object|struct|interface)\b/.test(kindCell)) rowGroup = 'classes';
        else if (/\b(module|package|namespace)\b/.test(kindCell)) rowGroup = 'modules';
        else if (/\b(library|stdlib|standard library)\b/.test(kindCell)) rowGroup = 'libraries';
        else if (/\b(function|proc|macro|predicate|cmdlet|statement|task)\b/.test(kindCell)) rowGroup = 'functions';
        else rowGroup = 'functions';
        tr.dataset.group = rowGroup; // cache for subsequent passes
      }
      const matchText = !q || text.includes(q);
      const matchGroup = group === 'all' || rowGroup === group;
      const show = matchText && matchGroup;
      tr.style.display = show ? 'table-row' : 'none';
      if (show) visible++;
    });
    if (count) count.textContent = visible + ' matching';
    // Failsafe: if nothing visible on All with empty search, show everything
    if (!visible && !q && group === 'all') {
      rows.forEach(tr => (tr.style.display = 'table-row'));
      if (count) count.textContent = rows.length + ' matching';
    }
  };

  const setActive = (name) => {
    group = name;
    tabBtns.forEach(b => {
      const active = b.dataset.biTab === name;
      b.classList.toggle('active', active);
      b.setAttribute('aria-pressed', String(active));
    });
    update();
  };

  tabBtns.forEach(b => b.addEventListener('click', () => setActive(b.dataset.biTab)));
  const init = () => {
    // Ensure rows are visible by default, then apply current filter
    getRows().forEach(tr => tr.style.display = 'table-row');
    setActive('all');
  };
  if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  window.addEventListener('load', init);
  if (input) input.addEventListener('input', update);
})();

// Copy buttons for code blocks
(function(){
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-code-copy]');
    if (!btn) return;
    const pre = btn.parentElement.nextElementSibling;
    if (!pre || !pre.querySelector('code')) return;
    const text = pre.querySelector('code').innerText;
    try { await navigator.clipboard.writeText(text); btn.textContent = 'Copied'; setTimeout(() => btn.textContent = 'Copy', 1200); } catch {}
  });
})();
