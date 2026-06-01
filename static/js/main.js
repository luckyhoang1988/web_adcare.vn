// ADCARE - Main JS
document.addEventListener('DOMContentLoaded', function () {

  // Auto-init Bootstrap tooltips
  const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipEls.forEach(el => new bootstrap.Tooltip(el));

  // Active nav link
  const currentPath = window.location.pathname;
  document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    if (href === '/') {
      if (currentPath === '/') link.closest('.nav-item')?.classList.add('active');
    } else {
      const base = href.endsWith('/') ? href : href + '/';
      if (currentPath === href || currentPath.startsWith(base)) {
        link.closest('.nav-item')?.classList.add('active');
      }
    }
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Back to top button
  const backBtn = document.getElementById('backToTop');
  if (backBtn) {
    let ticking = false;
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          backBtn.classList.toggle('show', window.scrollY > 400);
          ticking = false;
        });
        ticking = true;
      }
    });
    backBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }
});
