// Simple client-side loader to display the citation and publication counts.
// Place <span id="citation-count">308</span> and <span id="publication-count">52</span> in your HTML where you want the numbers.
//
// This script fetches /data/citations.json (written by the GitHub Action) and updates the DOM.
(async function () {
  try {
    const resp = await fetch('/data/citations.json', { cache: 'no-cache' });
    if (!resp.ok) return;
    const j = await resp.json();
    const el = document.getElementById('citation-count');
    if (el && j && typeof j.citations === 'number') {
      el.textContent = j.citations.toLocaleString();
      el.title = 'Last updated: ' + (j.fetched_at || '');
    }
    const pubEl = document.getElementById('publication-count');
    if (pubEl && j && typeof j.publications === 'number') {
      pubEl.textContent = j.publications.toLocaleString();
      pubEl.title = 'Last updated: ' + (j.fetched_at || '');
    }
  } catch (err) {
    // silently fail — keep existing numbers
    console.warn('Could not load citation/publication counts', err);
  }
})();
