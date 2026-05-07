let allTutorials = [];

const CATEGORIES = [
  { name: "Home & Plumbing",      abbr: "PL", slug: "home-plumbing" },
  { name: "Home & Cleaning",      abbr: "CL", slug: "home-cleaning" },
  { name: "Home & Repair",        abbr: "RP", slug: "home-repair" },
  { name: "Home & Electrical",    abbr: "EL", slug: "home-electrical" },
  { name: "Home & Pets",          abbr: "PT", slug: "home-pets" },
  { name: "Kitchen & Pests",      abbr: "KP", slug: "kitchen-pests" },
  { name: "Kitchen & Appliances", abbr: "KA", slug: "kitchen-appliances" },
  { name: "Kitchen & Cookware",   abbr: "KC", slug: "kitchen-cookware" },
  { name: "Clothing & Shoes",     abbr: "SH", slug: "clothing-shoes" },
  { name: "Clothing & Laundry",   abbr: "LN", slug: "clothing-laundry" },
  { name: "Clothing & Repair",    abbr: "CR", slug: "clothing-repair" },
  { name: "Personal Care",        abbr: "PC", slug: "personal-care" },
];

async function loadTutorials() {
  if (allTutorials.length) return allTutorials;
  const res = await fetch('data/tutorials.json');
  allTutorials = await res.json();
  return allTutorials;
}

function difficultyBadge(d) {
  const cls = d === 'Easy' ? 'badge-easy' : d === 'Medium' ? 'badge-medium' : 'badge-hard';
  return `<span class="badge ${cls}">${d}</span>`;
}

function categoryColor(cat) {
  const colors = {
    'Home & Plumbing': '#0ea5e9',
    'Home & Cleaning': '#8b5cf6',
    'Home & Repair': '#f59e0b',
    'Home & Electrical': '#f97316',
    'Home & Pets': '#ec4899',
    'Kitchen & Pests': '#84cc16',
    'Kitchen & Appliances': '#06b6d4',
    'Kitchen & Cookware': '#ef4444',
    'Clothing & Shoes': '#6366f1',
    'Clothing & Laundry': '#14b8a6',
    'Clothing & Repair': '#a855f7',
    'Personal Care': '#f43f5e',
  };
  return colors[cat] || '#2563eb';
}

function tutorialCard(t) {
  return `
    <div class="tutorial-card" onclick="window.location='tutorial.html?id=${t.id}'">
      ${t.image ? `<div class="card-img"><img src="${t.image}" alt="${t.title}" loading="lazy"></div>` : `<div class="card-cat-bar"></div>`}
      <div class="card-body">
        <div class="card-meta">
          <span class="badge badge-cat">${t.category}</span>
          ${difficultyBadge(t.difficulty)}
          <span class="card-time">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            ${t.time}
          </span>
        </div>
        <div class="card-title">${t.title}</div>
        <div class="card-desc">${t.description}</div>
      </div>
      <div class="card-footer">
        <div class="card-tags">
          ${t.tags.slice(0, 3).map(tag => `<span class="tag">${tag}</span>`).join('')}
        </div>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </div>
    </div>`;
}

// ── HOME PAGE ──
async function initHome() {
  const tutorials = await loadTutorials();

  // Categories
  const catGrid = document.getElementById('categories-grid');
  if (catGrid) {
    catGrid.innerHTML = CATEGORIES.map(c => {
      const count = tutorials.filter(t => t.category === c.name).length;
      return `
        <div class="category-card" onclick="window.location='search.html?cat=${encodeURIComponent(c.name)}'">
          <div class="cat-abbr">${c.abbr}</div>
          <div class="name">${c.name}</div>
          <div class="count">${count} guides</div>
        </div>`;
    }).join('');
  }

  // Featured tutorials
  const featuredGrid = document.getElementById('featured-grid');
  if (featuredGrid) {
    featuredGrid.innerHTML = tutorials.slice(0, 6).map(tutorialCard).join('');
  }

  // Recent tutorials
  const recentGrid = document.getElementById('recent-grid');
  if (recentGrid) {
    recentGrid.innerHTML = tutorials.slice(6, 12).map(tutorialCard).join('');
  }

  // Stats
  document.querySelectorAll('[data-stat="total"]').forEach(el => el.textContent = tutorials.length + '+');

  // Hero search
  const heroSearchInput = document.getElementById('hero-search-input');
  const heroSearchBtn = document.getElementById('hero-search-btn');
  if (heroSearchBtn) {
    heroSearchBtn.addEventListener('click', () => {
      const q = heroSearchInput.value.trim();
      if (q) window.location = `search.html?q=${encodeURIComponent(q)}`;
    });
    heroSearchInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') heroSearchBtn.click();
    });
  }

  // Nav search
  const navSearchInput = document.getElementById('nav-search-input');
  if (navSearchInput) {
    navSearchInput.addEventListener('keydown', e => {
      if (e.key === 'Enter' && navSearchInput.value.trim()) {
        window.location = `search.html?q=${encodeURIComponent(navSearchInput.value.trim())}`;
      }
    });
  }
}

// ── TUTORIAL PAGE ──
async function initTutorial() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get('id');
  if (!id) { window.location = 'index.html'; return; }

  const tutorials = await loadTutorials();
  const t = tutorials.find(x => x.id === id);
  if (!t) { window.location = 'index.html'; return; }

  document.title = t.title + ' — FixAnything';

  const container = document.getElementById('tutorial-container');
  if (!container) return;

  const related = tutorials.filter(x => t.relatedIds?.includes(x.id)).slice(0, 4);

  container.innerHTML = `
    <div class="tutorial-layout">
      <main class="tutorial-main">
        <div class="tutorial-header">
          <div class="breadcrumb">
            <a href="index.html">Home</a> ›
            <a href="search.html?cat=${encodeURIComponent(t.category)}">${t.category}</a> ›
            <span>${t.title}</span>
          </div>
          <h1>${t.title}</h1>
          <div class="tutorial-meta-bar">
            <span class="badge badge-cat">${t.category}</span>
            ${difficultyBadge(t.difficulty)}
            <span class="card-time" style="margin-left:0">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              ${t.time}
            </span>
          </div>
        </div>

        ${t.image ? `<div class="tutorial-hero-img"><img src="${t.image}" alt="${t.title}"></div>` : ''}
        <div class="tutorial-intro">${t.intro}</div>

        <div class="ad-slot ad-slot-banner">Advertisement</div>

        <div class="needs-box">
          <h3>What You'll Need</h3>
          <ul class="needs-list">
            ${t.whatYouNeed.map(item => {
              const q = encodeURIComponent(item);
              return `<li><a href="https://www.amazon.com/s?k=${q}&tag=fixanything03-20" target="_blank" rel="noopener" class="amazon-link">${item} <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="opacity:0.6"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg></a></li>`;
            }).join('')}
          </ul>
          <p class="amazon-note">As an Amazon Associate, FixAnything earns from qualifying purchases.</p>
        </div>

        <div class="steps-section">
          <h2>Step-by-Step Instructions</h2>
          ${t.steps.map((step, i) => `
            <div class="step" id="step-${i+1}">
              <div class="step-num">${i+1}</div>
              <div class="step-content">
                <h3>${step.title}</h3>
                <p>${step.content}</p>
              </div>
            </div>`).join('')}
        </div>

        ${t.warnings?.length ? `
          <div class="warnings-box">
            <h3>⚠ Watch Out</h3>
            <ul>
              ${t.warnings.map(w => `<li>${w}</li>`).join('')}
            </ul>
          </div>` : ''}

        <div class="ad-slot ad-slot-banner" style="margin-top:32px">Advertisement</div>
      </main>

      <aside class="sidebar">
        <div class="sidebar-box">
          <div class="sidebar-box-header">Steps</div>
          <ul class="toc-list">
            ${t.steps.map((step, i) => `
              <li>
                <a href="#step-${i+1}">
                  <span class="toc-num">${i+1}</span>
                  ${step.title}
                </a>
              </li>`).join('')}
          </ul>
        </div>

        <div class="ad-slot ad-slot-sidebar">Advertisement</div>

        ${related.length ? `
          <div class="sidebar-box" style="margin-top:20px">
            <div class="sidebar-box-header">Related Guides</div>
            <ul class="related-list">
              ${related.map(r => `
                <li><a href="tutorial.html?id=${r.id}">${r.title}</a></li>`).join('')}
            </ul>
          </div>` : ''}
      </aside>
    </div>`;
}

// ── SEARCH PAGE ──
async function initSearch() {
  const tutorials = await loadTutorials();
  const params = new URLSearchParams(window.location.search);
  let query = params.get('q') || '';
  let activeCat = params.get('cat') || '';

  const searchInput = document.getElementById('search-input');
  const resultsInfo = document.getElementById('results-info');
  const resultsGrid = document.getElementById('results-grid');
  const filterBtns = document.querySelectorAll('.filter-btn[data-cat]');

  if (searchInput) searchInput.value = query;

  // Activate category filter
  if (activeCat) {
    filterBtns.forEach(btn => {
      if (btn.dataset.cat === activeCat) btn.classList.add('active');
    });
  }

  // Build cat filter buttons
  const filterBar = document.getElementById('filter-bar');
  if (filterBar) {
    const cats = [...new Set(tutorials.map(t => t.category))].sort();
    filterBar.innerHTML = `
      <button class="filter-btn ${!activeCat ? 'active' : ''}" data-cat="">All</button>
      ${cats.map(c => `<button class="filter-btn ${activeCat === c ? 'active' : ''}" data-cat="${c}">${c}</button>`).join('')}`;
    filterBar.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        activeCat = btn.dataset.cat;
        filterBar.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderResults();
      });
    });
  }

  function renderResults() {
    let results = tutorials;
    if (activeCat) results = results.filter(t => t.category === activeCat);
    if (query) {
      const q = query.toLowerCase();
      results = results.filter(t =>
        t.title.toLowerCase().includes(q) ||
        t.description.toLowerCase().includes(q) ||
        t.tags.some(tag => tag.toLowerCase().includes(q)) ||
        t.category.toLowerCase().includes(q)
      );
    }

    if (resultsInfo) {
      resultsInfo.innerHTML = query || activeCat
        ? `Showing <strong>${results.length}</strong> result${results.length !== 1 ? 's' : ''}`
        + (query ? ` for "<strong>${query}</strong>"` : '')
        + (activeCat ? ` in <strong>${activeCat}</strong>` : '')
        : `Showing all <strong>${results.length}</strong> guides`;
    }

    if (resultsGrid) {
      if (results.length === 0) {
        resultsGrid.innerHTML = `
          <div class="no-results" style="grid-column:1/-1">
            <h3>No results found</h3>
            <p>Try a different search term or browse categories below.</p>
          </div>`;
      } else {
        resultsGrid.innerHTML = results.map(tutorialCard).join('');
      }
    }
  }

  renderResults();

  // Search input + button
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      query = searchInput.value.trim();
      renderResults();
    });
  }

  const searchBtn = document.querySelector('.search-bar-lg button');
  if (searchBtn) {
    searchBtn.addEventListener('click', () => {
      if (searchInput) query = searchInput.value.trim();
      renderResults();
    });
  }

  const navSearch = document.getElementById('nav-search-input');
  if (navSearch) {
    navSearch.addEventListener('keydown', e => {
      if (e.key === 'Enter' && navSearch.value.trim()) {
        query = navSearch.value.trim();
        if (searchInput) searchInput.value = query;
        renderResults();
      }
    });
  }
}
