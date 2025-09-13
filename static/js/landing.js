// Simple, lightweight interactions for the landing page
(function() {
  // Fade-in on view with safe fallbacks
  const candidates = Array.from(document.querySelectorAll('[data-reveal]'));

  // Initialize hidden state (only if not already revealed)
  candidates.forEach(el => {
    if (!el.__revealed) {
      el.style.transform = 'translateY(12px)';
      el.style.opacity = '0';
      el.style.transition = 'opacity .6s ease, transform .6s ease';
    }
  });

  const revealNow = (el) => {
    el.style.transform = 'translateY(0)';
    el.style.opacity = '1';
    el.__revealed = true;
  };

  const revealAll = () => candidates.forEach(revealNow);

  const setupIO = () => {
    try {
      if (!('IntersectionObserver' in window)) return false;
      const io = new IntersectionObserver((entries) => {
        entries.forEach(e => {
          if (e.isIntersecting) {
            revealNow(e.target);
            io.unobserve(e.target);
          }
        });
      }, { threshold: 0.15 });
      candidates.forEach(el => io.observe(el));
      return true;
    } catch {
      return false;
    }
  };

  const ok = candidates.length ? setupIO() : true;
  // Fallbacks: if IO unsupported or didn’t trigger, reveal after load and with a timer
  if (!ok) {
    // No IO support: reveal immediately
    revealAll();
  } else {
    // Safety net: ensure visible after load in case IO misses
    const safety = () => {
      candidates.forEach(el => {
        if (!el.__revealed) revealNow(el);
      });
    };
    window.addEventListener('load', () => setTimeout(safety, 800));
    // Also apply a late safety in case load already fired
    setTimeout(safety, 1500);
  }

  // Subtle parallax for hero card
  const card = document.querySelector('.hero .card');
  const tiltTargets = Array.from(document.querySelectorAll('[data-tilt]'));
  const applyTilt = (el, e, strength=8) => {
    const r = el.getBoundingClientRect();
    const cx = r.left + r.width / 2;
    const cy = r.top + r.height / 2;
    const dx = (e.clientX - cx) / (r.width / 2);
    const dy = (e.clientY - cy) / (r.height / 2);
    el.style.transform = `translateY(0) rotateX(${-dy * strength}deg) rotateY(${dx * strength}deg)`;
  };
  const resetTilt = (el) => { el.style.transform = 'translateY(0) rotateX(0) rotateY(0)'; };
  if (card) {
    const onMove = (e) => applyTilt(card, e, 10);
    const onLeave = () => resetTilt(card);
    card.style.transition = 'transform .3s ease';
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseleave', onLeave);
  }
  tiltTargets.forEach(el => {
    el.style.transition = 'transform .25s ease';
    el.addEventListener('mousemove', (e) => applyTilt(el, e, 6));
    el.addEventListener('mouseleave', () => resetTilt(el));
  });

  // Code demo: tabs, copy, rotate
  const demo = document.querySelector('[data-code-demo]');
  if (demo) {
    const tabs = Array.from(demo.querySelectorAll('[data-tab]'));
    const panes = Array.from(demo.querySelectorAll('[data-lang]'));
    const copyBtn = demo.querySelector('[data-copy]');
    let idx = 0;
    let userInteracted = false;

    const activate = (name) => {
      tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === name));
      panes.forEach(p => p.classList.toggle('active', p.dataset.lang === name));
    };

    tabs.forEach((t, i) => {
      t.addEventListener('click', () => { userInteracted = true; idx = i; activate(t.dataset.tab); });
    });

    if (copyBtn) {
      copyBtn.addEventListener('click', async () => {
        const active = demo.querySelector('.code-pane.active pre');
        if (!active) return;
        const text = active.innerText;
        try { await navigator.clipboard.writeText(text); copyBtn.textContent = 'Copied'; setTimeout(() => copyBtn.textContent = 'Copy', 1200); } catch {}
      });
    }

    // Auto-rotate until user interacts
    const names = tabs.map(t => t.dataset.tab);
    if (names.length) {
      activate(names[0]);
      const timer = setInterval(() => {
        if (userInteracted) { clearInterval(timer); return; }
        idx = (idx + 1) % names.length;
        activate(names[idx]);
      }, 3500);
    }
  }
})();
