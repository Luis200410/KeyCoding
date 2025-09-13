// Simple client-side filter for built-ins table (supports single or grouped layouts)
(function(){
  const input = document.getElementById('bi-filter');
  const count = document.getElementById('bi-count');
  if (!input) return;
  let rows = [];
  const bodySingle = document.getElementById('bi-body');
  if (bodySingle) {
    rows = Array.from(bodySingle.querySelectorAll('[data-row]'));
  } else {
    const bodies = Array.from(document.querySelectorAll('tbody.bi-body'));
    rows = bodies.flatMap(b => Array.from(b.querySelectorAll('[data-bi-row]')));
  }
  if (!rows.length) return;
  const update = () => {
    const q = (input.value || '').toLowerCase().trim();
    let visible = 0;
    rows.forEach(tr => {
      const text = tr.innerText.toLowerCase();
      const show = !q || text.includes(q);
      tr.style.display = show ? '' : 'none';
      if (show) visible++;
    });
    if (count) count.textContent = visible + ' matching';
    if (q) document.querySelectorAll('details.bi-group').forEach(d => d.open = true);
  };
  input.addEventListener('input', update);
  update();
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
