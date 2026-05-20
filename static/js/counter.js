// Animated counter for stats section
(function () {
  function animateCount(el, target, suffix, duration) {
    const start = 0;
    const startTime = performance.now();
    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(eased * target) + suffix;
      if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
  }

  function initCounters() {
    document.querySelectorAll('.stat-number[data-target]').forEach(el => {
      const raw = el.getAttribute('data-target');
      const suffix = raw.replace(/[0-9]/g, '');
      const target = parseInt(raw.replace(/\D/g, ''), 10);
      animateCount(el, target, suffix, 2000);
    });
  }

  // Trigger on first intersection
  const section = document.querySelector('.stats-section');
  if (!section) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        initCounters();
        observer.disconnect();
      }
    });
  }, { threshold: 0.3 });

  observer.observe(section);
})();
