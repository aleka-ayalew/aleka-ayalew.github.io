// Simple client-side loader to display the citation and publication counts in multiple places.
// Place <span id="citation-count">...</span> and <span id="publication-count">...</span> in your HTML where you want the numbers.
// This script fetches /data/citations.json (written by the GitHub Action) and updates any matching elements.
(function () {
  async function load() {
    try {
      const resp = await fetch('/data/citations.json', { cache: 'no-cache' });
      if (!resp.ok) return;
      const j = await resp.json();

      const setText = (id, val) => {
        const el = document.getElementById(id);
        if (!el) return;
        if (typeof val === 'number') {
          el.textContent = val.toLocaleString();
        } else {
          el.textContent = String(val);
        }
      };

      if (j) {
        if (typeof j.citations === 'number') {
          setText('citation-count', j.citations);
        }
        if (typeof j.publications === 'number') {
          const pubs = j.publications;
          // Update all known publication placeholders
          setText('publication-count', pubs);
          setText('publication-count-inline', pubs);
          setText('publication-count-card', pubs + (pubs >= 30 ? '+' : ''));
          setText('publication-count-cta', pubs + (pubs >= 30 ? '+' : ''));

          // Also update any metric-number elements that reference publications (fallback)
          try {
            const labels = document.querySelectorAll('.metric-item');
            labels.forEach(node => {
              const label = node.querySelector('.metric-label');
              const num = node.querySelector('.metric-number');
              if (label && num && /publications?/i.test(label.textContent)) {
                num.textContent = pubs.toLocaleString();
                num.setAttribute('data-count', String(pubs));
              }
            });
          } catch (e) {
            // ignore
          }
        }
      }
    } catch (err) {
      console.warn('Could not load citation/publication counts', err);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }
})();
