document.addEventListener('DOMContentLoaded', () => {
  const modelChart = document.getElementById('modelComparisonChart');

  if (modelChart) {
    const labels = JSON.parse(modelChart.dataset.labels || '[]');
    const accuracy = JSON.parse(modelChart.dataset.accuracy || '[]');
    const roc = JSON.parse(modelChart.dataset.roc || '[]');
    const f1 = JSON.parse(modelChart.dataset.f1 || '[]');
    const yMax = Number(modelChart.dataset.yMax || 1);
    const width = 560;
    const height = 320;
    const padding = { top: 24, right: 24, bottom: 46, left: 46 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;
    const xStep = labels.length > 1 ? chartWidth / (labels.length - 1) : chartWidth;

    const buildPath = (series) => {
      return series.map((value, index) => {
        const x = padding.left + (index * xStep);
        const y = padding.top + chartHeight - ((value / yMax) * chartHeight);
        return `${index === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
      }).join(' ');
    };

    const pointMarkup = (series, color) => {
      return series.map((value, index) => {
        const x = padding.left + (index * xStep);
        const y = padding.top + chartHeight - ((value / yMax) * chartHeight);
        return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="4.5" fill="${color}"></circle>`;
      }).join('');
    };

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', 'Model comparison line chart');

    const gridLines = Array.from({ length: 5 }, (_, index) => {
      const y = padding.top + (chartHeight / 4) * index;
      return `<line x1="${padding.left}" y1="${y.toFixed(1)}" x2="${width - padding.right}" y2="${y.toFixed(1)}" stroke="#dce5ea" stroke-dasharray="4 4"></line>`;
    }).join('');

    const xLabels = labels.map((label, index) => {
      const x = padding.left + (index * xStep);
      return `<text x="${x.toFixed(1)}" y="${height - 14}" text-anchor="middle" fill="#6b7a87" font-size="12">${label}</text>`;
    }).join('');

    const yLabels = Array.from({ length: 5 }, (_, index) => {
      const value = (yMax / 4) * (4 - index);
      const y = padding.top + (chartHeight / 4) * index;
      return `<text x="${padding.left - 10}" y="${y.toFixed(1) + 4}" text-anchor="end" fill="#6b7a87" font-size="11">${value.toFixed(2)}</text>`;
    }).join('');

    svg.innerHTML = `
      <rect x="${padding.left}" y="${padding.top}" width="${chartWidth}" height="${chartHeight}" rx="12" fill="#f9fbfc"></rect>
      ${gridLines}
      <line x1="${padding.left}" y1="${padding.top + chartHeight}" x2="${padding.left}" y2="${padding.top}" stroke="#6b7a87"></line>
      <line x1="${padding.left}" y1="${padding.top + chartHeight}" x2="${width - padding.right}" y2="${padding.top + chartHeight}" stroke="#6b7a87"></line>
      <path d="${buildPath(accuracy)}" fill="none" stroke="#287a8e" stroke-width="3"></path>
      <path d="${buildPath(roc)}" fill="none" stroke="#d7773f" stroke-width="3"></path>
      <path d="${buildPath(f1)}" fill="none" stroke="#5f8f3d" stroke-width="3"></path>
      ${pointMarkup(accuracy, '#287a8e')}
      ${pointMarkup(roc, '#d7773f')}
      ${pointMarkup(f1, '#5f8f3d')}
      ${xLabels}
      ${yLabels}
    `;
    modelChart.appendChild(svg);
  }

  const accordionItems = Array.from(document.querySelectorAll('.accordion-item'));
  const tabButtons = Array.from(document.querySelectorAll('.tab-switcher button'));
  const tabPanels = Array.from(document.querySelectorAll('.tab-panel'));
  const searchInput = document.getElementById('drugSearch');
  const drugCards = Array.from(document.querySelectorAll('.drug-card'));
  const drugDetail = document.getElementById('drugDetail');
  const geneSearchInput = document.getElementById('geneSearchInput');
  const geneResults = document.getElementById('geneResults');
  const geneDetail = document.getElementById('geneDetail');
  const geneCards = Array.from(document.querySelectorAll('.gene-card'));

  function closeOtherItems(currentItem) {
    accordionItems.forEach((item) => {
      if (item !== currentItem) {
        item.open = false;
      }
    });
  }

  accordionItems.forEach((item) => {
    item.addEventListener('toggle', () => {
      if (item.open) {
        closeOtherItems(item);
        item.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  function selectDrug(card) {
    if (!drugDetail) {
      return;
    }

    drugCards.forEach((item) => item.classList.remove('is-selected'));
    card.classList.add('is-selected');

    const name = card.dataset.name;
    const category = card.dataset.category;
    const evidence = card.dataset.evidence;
    const detail = card.dataset.detail;

    drugDetail.innerHTML = `
      <span class="section-kicker">Drug detail</span>
      <h3>${name}</h3>
      <p><strong>Category:</strong> ${category}</p>
      <p><strong>Evidence:</strong> ${evidence}</p>
      <p>${detail}</p>
    `;
  }

  drugCards.forEach((card) => {
    card.addEventListener('click', () => selectDrug(card));
  });

  tabButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const target = button.dataset.tabTarget;
      tabButtons.forEach((item) => item.classList.remove('active'));
      tabPanels.forEach((panel) => panel.classList.remove('active'));
      button.classList.add('active');
      const activePanel = document.getElementById(target);
      if (activePanel) {
        activePanel.classList.add('active');
      }
    });
  });

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      const query = searchInput.value.trim().toLowerCase();

      drugCards.forEach((card) => {
        const name = card.dataset.drug || '';
        const match = name.includes(query);
        card.style.display = match ? '' : 'none';
      });
    });
  }

  function renderGeneDetail(card) {
    if (!geneDetail || !card) {
      return;
    }

    const name = card.dataset.gene || 'Unknown';
    const description = card.dataset.description || '';
    const interactionCount = card.dataset.interactionCount || '0';
    const drugs = (card.dataset.drugs || '').split(',').filter(Boolean);

    geneCards.forEach((item) => item.classList.remove('is-selected'));
    card.classList.add('is-selected');

    geneDetail.innerHTML = `
      <span class="section-kicker">Selected gene</span>
      <h3>${name}</h3>
      <div class="detail-block">
        <strong>Clinical-style description</strong>
        <p>${description}</p>
      </div>
      <div class="detail-block">
        <strong>Linked drugs</strong>
        <ul>${drugs.map((drug) => `<li>${drug}</li>`).join('')}</ul>
      </div>
      <div class="detail-block">
        <strong>Evidence snapshot</strong>
        <p>${interactionCount} interaction records available in the current dataset.</p>
      </div>
    `;
  }

  geneCards.forEach((card) => {
    card.addEventListener('click', () => renderGeneDetail(card));
  });

  if (geneSearchInput && geneResults) {
    geneSearchInput.addEventListener('input', async () => {
      const query = geneSearchInput.value.trim().toUpperCase();
      const response = await fetch(`/api/genes?q=${encodeURIComponent(query)}`);
      const data = await response.json();

      geneResults.innerHTML = '';

      if (!data.length) {
        geneResults.innerHTML = '<p class="muted-note">No matching genes found in the current dataset.</p>';
        return;
      }

      data.forEach((item) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'gene-card';
        button.dataset.gene = item.gene;
        button.dataset.description = item.description;
        button.dataset.interactionCount = item.interaction_count;
        button.dataset.drugs = (item.related_drugs || []).join(',');
        button.innerHTML = `
          <span class="gene-pill">${item.gene}</span>
          <h3>${item.gene}</h3>
          <p>${item.description}</p>
          <small>${item.interaction_count} interaction records</small>
        `;
        button.addEventListener('click', () => renderGeneDetail(button));
        geneResults.appendChild(button);
      });
    });
  }
});
