const data = window.DASHBOARD_DATA;

const state = {
  from: 2012,
  to: 2025,
  cohort: 'B',
  region: 'All',
  dimension: 'Violence type'
};

const cohortLabels = {
  A: 'All SINAN violence notifications',
  B: 'Domestic or family violence',
  C: 'Intimate partner violence'
};

const policyEvents = data.policyEvents || [];

const policyTypes = [
  'Violence against women',
  'Vulnerable-population protection',
  'Alcohol tax and regulation'
];

const policyTypeClass = {
  'Violence against women': 'policy-women',
  'Vulnerable-population protection': 'policy-vulnerable',
  'Alcohol tax and regulation': 'policy-alcohol'
};

const number = new Intl.NumberFormat('en-US');
const compact = new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 });
const percent1 = new Intl.NumberFormat('en-US', { style: 'percent', maximumFractionDigits: 1 });
const monthFormat = new Intl.DateTimeFormat('en-US', { month: 'short', year: 'numeric' });

const regions = ['All', ...new Set(data.monthlyCohort.map(row => row.region_name).filter(Boolean).filter(name => name !== 'Unknown'))];
const dimensions = [
  'Violence type',
  'Aggressor relationship',
  'Victim sex',
  'Victim age group',
  'Victim race/ethnicity',
  'Victim disability status',
  'Place of occurrence',
  'Repeated violence',
  'Region',
  'State'
];

function parseDate(value) {
  return new Date(`${String(value).slice(0, 10)}T00:00:00`);
}

function formatMonth(value) {
  return monthFormat.format(parseDate(value));
}

function sum(list, accessor) {
  return list.reduce((total, item) => total + accessor(item), 0);
}

function aggregate(rows, keyFn, valueFn) {
  const map = new Map();
  rows.forEach(row => {
    const key = keyFn(row);
    map.set(key, (map.get(key) || 0) + valueFn(row));
  });
  return map;
}

function monthlyRowsFor(cohortCode) {
  return data.monthlyCohort.filter(row =>
    row.cohort_code === cohortCode &&
    row.occurrence_year >= state.from &&
    row.occurrence_year <= state.to &&
    (state.region === 'All' || row.region_name === state.region)
  );
}

function alcoholRows() {
  return data.alcoholMonthly.filter(row =>
    row.cohort_code === state.cohort &&
    row.occurrence_year >= state.from &&
    row.occurrence_year <= state.to &&
    (state.region === 'All' || row.region_name === state.region)
  );
}

function breakdownRows() {
  return data.breakdowns.filter(row =>
    row.cohort_code === state.cohort &&
    row.year >= state.from &&
    row.year <= state.to &&
    (state.region === 'All' || row.region_name === state.region) &&
    row.dimension_name === state.dimension
  );
}

function calendarRows() {
  return data.calendarCounts.filter(row =>
    row.cohort_code === state.cohort &&
    row.year >= state.from &&
    row.year <= state.to &&
    (state.region === 'All' || row.region_name === state.region)
  );
}

function weekdayRows() {
  return data.weekdayCounts.filter(row =>
    row.cohort_code === state.cohort &&
    row.year >= state.from &&
    row.year <= state.to &&
    (state.region === 'All' || row.region_name === state.region)
  );
}

function holidayRows() {
  return data.holidaySummary.filter(row =>
    row.cohort_code === state.cohort &&
    row.year >= state.from &&
    row.year <= state.to &&
    (state.region === 'All' || row.region_name === state.region)
  );
}

function protectionRows() {
  return data.protectionYearly.filter(row => row.year >= state.from && row.year <= Math.min(state.to, 2026));
}

function violationRows() {
  return data.protectionViolations.filter(row => row.year >= state.from && row.year <= Math.min(state.to, 2026));
}

function channelRows() {
  return data.protectionChannels.filter(row => row.year >= state.from && row.year <= Math.min(state.to, 2026));
}

function quarterlyRows() {
  return data.quarterlyCohort.filter(row =>
    row.cohort_code === state.cohort &&
    row.year >= state.from &&
    row.year <= state.to
  );
}

function ambevAnnualRows() {
  const annual = new Map();
  data.ambev
    .filter(row => row.year >= state.from && row.year <= state.to)
    .forEach(row => {
      const current = annual.get(row.year) || { year: row.year, beerVolume: 0, taxTotal: 0, taxCount: 0 };
      current.beerVolume += row.beer_volume_sold_000_hl || 0;
      if (row.brazil_beer_sales_tax_pct_gross_sales !== null && row.brazil_beer_sales_tax_pct_gross_sales !== undefined) {
        current.taxTotal += row.brazil_beer_sales_tax_pct_gross_sales;
        current.taxCount += 1;
      }
      annual.set(row.year, current);
    });
  return [...annual.values()]
    .map(row => ({ ...row, beerTaxShare: row.taxCount ? row.taxTotal / row.taxCount : null }))
    .sort((a, b) => a.year - b.year);
}

function vigitelRows() {
  return data.vigitel.filter(row => row.year >= state.from && row.year <= state.to);
}

function calendarDayMap() {
  return aggregate(
    data.calendarDays.filter(row => row.year >= state.from && row.year <= state.to),
    row => row.calendar_bucket,
    row => row.eligible_days
  );
}

function weekdayDayMap() {
  return aggregate(
    data.weekdayDays.filter(row => row.year >= state.from && row.year <= state.to),
    row => row.day_of_week_name,
    row => row.eligible_days
  );
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function addTooltips(container) {
  const tooltip = document.createElement('div');
  tooltip.className = 'chart-tooltip';
  tooltip.setAttribute('role', 'status');
  container.append(tooltip);

  const hide = () => tooltip.classList.remove('is-visible');
  const show = target => {
    tooltip.innerHTML = target.dataset.tooltip;
    tooltip.classList.add('is-visible');
    const containerRect = container.getBoundingClientRect();
    const targetRect = target.getBoundingClientRect();
    tooltip.style.left = `${Math.max(8, Math.min(targetRect.left - containerRect.left, containerRect.width - 190))}px`;
    tooltip.style.top = `${Math.max(8, targetRect.top - containerRect.top - 78)}px`;
  };

  container.querySelectorAll('[data-tooltip]').forEach(target => {
    target.addEventListener('pointerenter', () => show(target));
    target.addEventListener('pointerleave', hide);
    target.addEventListener('focus', () => show(target));
    target.addEventListener('blur', hide);
    target.addEventListener('click', event => event.stopPropagation());
  });
}

function enableChartFullscreen(element, title) {
  if (element.dataset.fullscreenEnabled) return;
  element.dataset.fullscreenEnabled = 'true';
  element.tabIndex = 0;
  element.setAttribute('aria-label', `${title}. Click to expand fullscreen.`);

  const toggleFullscreen = () => {
    if (document.fullscreenElement === element) {
      document.exitFullscreen().catch(() => {});
    } else if (element.requestFullscreen) {
      element.requestFullscreen().catch(() => {});
    }
  };

  element.addEventListener('click', event => {
    if (!event.target.closest('[data-tooltip]')) toggleFullscreen();
  });
  element.addEventListener('keydown', event => {
    if (event.target.closest('[data-tooltip]')) return;
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggleFullscreen();
    }
  });
}

function asDay(value) {
  return new Date(`${String(value).slice(0, 10)}T00:00:00`);
}

function policyMarkerLayer(timelineDates, x, pad, height) {
  if (!timelineDates?.length || !policyEvents.length) return '';
  const dates = timelineDates.map(asDay);
  const firstDate = dates[0];
  const lastDate = dates.at(-1);
  const markerCounts = new Map();

  return policyEvents
    .filter(event => {
      const eventDate = asDay(event.event_date);
      return eventDate >= firstDate && eventDate <= lastDate;
    })
    .map(event => {
      const eventDate = asDay(event.event_date);
      let index = 0;
      dates.forEach((date, candidate) => {
        if (date <= eventDate) index = candidate;
      });
      const offset = markerCounts.get(index) || 0;
      markerCounts.set(index, offset + 1);
      const markerX = x(index) + ((offset % 3) - 1) * 4;
      const typeClass = policyTypeClass[event.event_type] || 'policy-vulnerable';
      const tooltip = `<strong>${escapeHtml(event.title)}</strong><span>${escapeHtml(`${event.event_date} | ${event.event_type}`)}</span><b>${escapeHtml(event.legal_reference || 'Policy context')}</b><span>${escapeHtml(event.description)}</span>`;
      return `<g class="policy-marker ${typeClass}">
        <line x1="${markerX}" y1="${pad.top}" x2="${markerX}" y2="${height - pad.bottom}"></line>
        <circle class="policy-marker-dot" cx="${markerX}" cy="${pad.top + 8 + (offset % 3) * 12}" r="6" aria-hidden="true"></circle>
        <circle class="policy-marker-hit" cx="${markerX}" cy="${pad.top + 8 + (offset % 3) * 12}" r="14" tabindex="0" role="img" aria-label="${escapeHtml(`${event.title}, ${event.event_date}`)}" data-tooltip="${escapeHtml(tooltip)}"></circle>
      </g>`;
    }).join('');
}

function lineChart(element, config) {
  const width = 940;
  const height = 320;
  const pad = { left: 56, right: 18, top: 18, bottom: 36 };
  const allValues = config.series.flatMap(series => series.values).filter(value => Number.isFinite(value));
  const min = config.percent ? 0 : Math.min(...allValues, 0);
  const max = Math.max(...allValues, 1);
  const span = max - min || 1;
  const x = index => pad.left + index * ((width - pad.left - pad.right) / Math.max(config.labels.length - 1, 1));
  const y = value => height - pad.bottom - ((value - min) / span) * (height - pad.top - pad.bottom);
  const yLabel = value => config.percent ? `${value.toFixed(1)}%` : compact.format(value);
  const grid = Array.from({ length: 5 }, (_, idx) => {
    const value = min + (span * idx / 4);
    return `<line class="grid-line" x1="${pad.left}" y1="${y(value)}" x2="${width - pad.right}" y2="${y(value)}"></line>
      <text class="axis-label" x="0" y="${y(value) + 3}">${yLabel(value)}</text>`;
  }).join('');
  const ticks = config.labels.map((label, idx) => {
    const show = idx % Math.max(1, Math.ceil(config.labels.length / 7)) === 0 || idx === config.labels.length - 1;
    return show ? `<text class="axis-label" text-anchor="middle" x="${x(idx)}" y="${height - 8}">${label}</text>` : '';
  }).join('');
  const lines = config.series.map(series => {
    let hasPreviousValue = false;
    const path = series.values.map((value, idx) => {
      if (!Number.isFinite(value)) {
        hasPreviousValue = false;
        return '';
      }
      const command = hasPreviousValue ? 'L' : 'M';
      hasPreviousValue = true;
      return `${command}${x(idx).toFixed(2)},${y(value).toFixed(2)}`;
    }).join(' ');
    return `<path class="${series.className}" d="${path}"></path>`;
  }).join('');
  const markers = policyMarkerLayer(config.timelineDates, x, pad, height);
  const points = config.series.flatMap((series, seriesIndex) => series.values.map((value, idx) => {
    if (!Number.isFinite(value)) return '';
    const label = (config.tooltipLabels || config.labels)[idx] || `Point ${idx + 1}`;
    const seriesLabel = series.label || `Series ${seriesIndex + 1}`;
    const formattedValue = config.tooltipFormatter ? config.tooltipFormatter(value) : yLabel(value);
    const tooltip = `<strong>${escapeHtml(seriesLabel)}</strong><span>${escapeHtml(label)}</span><b>${escapeHtml(formattedValue)}</b>`;
    return `<circle class="chart-point" cx="${x(idx)}" cy="${y(value)}" r="8" tabindex="0" role="img" aria-label="${escapeHtml(`${seriesLabel}, ${label}: ${formattedValue}`)}" data-tooltip="${escapeHtml(tooltip)}"></circle>`;
  })).join('');
  const policyLegend = config.timelineDates?.length && policyEvents.length ? `
    <p class="policy-marker-legend"><span class="policy-marker-title">Policy markers</span>
      <span class="policy-key policy-women"><i></i>Violence against women</span>
      <span class="policy-key policy-vulnerable"><i></i>Vulnerable-population protection</span>
      <span class="policy-key policy-alcohol"><i></i>Alcohol tax and regulation</span>
    </p>` : '';
  const fullscreenHeader = `<div class="fullscreen-chart-header">
    <div><p>Fullscreen chart</p><h3>${escapeHtml(config.title)}</h3></div>
    <span>Hover a line point or policy marker for details. Press Esc to exit.</span>
  </div>`;
  const fullscreenSeriesLegend = `<p class="fullscreen-series-legend"><span>Line series</span>${config.series.map((series, index) => `
    <span class="series-key"><i class="${series.className}"></i>${escapeHtml(series.label || `Series ${index + 1}`)}</span>`).join('')}
  </p>`;
  element.innerHTML = `${fullscreenHeader}${fullscreenSeriesLegend}${policyLegend}<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${config.title}">
    ${grid}${ticks}${lines}${points}${markers}
  </svg>`;
  addTooltips(element);
  enableChartFullscreen(element, config.title);
}

function renderBars(containerId, rows, formatter, captionFormatter) {
  const container = document.getElementById(containerId);
  if (!rows.length) {
    container.innerHTML = '<p class="empty-state">No data in the selected range.</p>';
    return;
  }
  const max = Math.max(...rows.map(row => row.value), 1);
  container.innerHTML = rows.map(row => {
    const caption = captionFormatter ? captionFormatter(row) : '';
    const tooltip = `<strong>${escapeHtml(row.label)}</strong><b>${escapeHtml(formatter(row.value))}</b>${caption ? `<span>${escapeHtml(caption)}</span>` : ''}`;
    return `
    <div class="bar-row" tabindex="0" data-tooltip="${escapeHtml(tooltip)}">
      <span>${row.label}</span>
      <div class="bar-track"><div class="bar-value" style="width:${(row.value / max) * 100}%"></div></div>
      <strong>${formatter(row.value)}</strong>
      ${caption ? `<small>${caption}</small>` : ''}
    </div>
  `;
  }).join('');
  addTooltips(container);
}

function renderOverview() {
  const allRows = monthlyRowsFor('A');
  const domesticRows = monthlyRowsFor('B');
  const ipvRows = monthlyRowsFor('C');
  const allTotal = sum(allRows, row => row.notification_count);
  const domesticTotal = sum(domesticRows, row => row.notification_count);
  const ipvTotal = sum(ipvRows, row => row.notification_count);
  const ambev = ambevAnnualRows();
  const ambevWithTax = ambev.filter(row => row.beerTaxShare !== null);
  const latestAmbevTax = ambevWithTax.at(-1);
  const domesticShare = allTotal ? domesticTotal / allTotal : 0;
  const ipvShare = domesticTotal ? ipvTotal / domesticTotal : 0;

  setText('metricAllSinan', number.format(allTotal));
  setText('metricAllSinanNote', `${state.from}-${state.to} in ${state.region === 'All' ? 'Brazil' : state.region}`);
  setText('metricDomestic', number.format(domesticTotal));
  setText('metricDomesticNote', `${percent1.format(domesticShare)} of all SINAN notifications`);
  setText('metricIpv', number.format(ipvTotal));
  setText('metricIpvNote', `${percent1.format(ipvShare)} of domestic/family notifications`);
  setText('metricAmbevTax', latestAmbevTax ? percent1.format(latestAmbevTax.beerTaxShare / 100) : 'N/A');
  setText('metricAmbevTaxNote', latestAmbevTax ? `${latestAmbevTax.year} latest reported Ambev Form 20-F measure` : 'No reported tax data in selected years');

  const labels = [...new Set([...domesticRows, ...ipvRows].map(row => row.occurrence_month))].sort();
  const buildSeries = rows => {
    const map = aggregate(rows, row => row.occurrence_month, row => row.notification_count);
    return labels.map(label => map.get(label) || 0);
  };

  lineChart(document.getElementById('overviewChart'), {
    title: 'Monthly domestic/family and intimate partner notifications',
    labels: labels.map(label => parseDate(label).getMonth() === 0 ? String(parseDate(label).getFullYear()) : ''),
    tooltipLabels: labels.map(formatMonth),
    timelineDates: labels,
    series: [
      { label: 'Domestic/family notifications', className: 'line-secondary', values: buildSeries(domesticRows) },
      { label: 'Intimate partner notifications', className: 'line-teal', values: buildSeries(ipvRows) }
    ]
  });

  const domesticSeries = buildSeries(domesticRows);
  const peakMonth = labels.length ? labels[domesticSeries.indexOf(Math.max(...domesticSeries))] : null;
  setText(
    'overviewTakeaway',
    peakMonth
      ? `Domestic/family notifications peaked in ${formatMonth(peakMonth)} within the selected view.`
      : 'No SINAN data is available in the selected view.'
  );

  const baseBeerVolume = ambevWithTax.find(row => row.beerVolume > 0)?.beerVolume || 1;
  const baseBeerTax = ambevWithTax[0]?.beerTaxShare || 1;
  lineChart(document.getElementById('ambevOverviewChart'), {
    title: 'Indexed annual Ambev beer volume sold and sales-tax share',
    labels: ambevWithTax.map(row => String(row.year)),
    timelineDates: ambevWithTax.map(row => `${row.year}-12-31`),
    tooltipFormatter: value => `Index: ${value.toFixed(1)}`,
    series: [
      { label: 'Beer volume sold', className: 'line-gold', values: ambevWithTax.map(row => (row.beerVolume / baseBeerVolume) * 100) },
      { label: 'Beer sales tax share', className: 'line-teal', values: ambevWithTax.map(row => (row.beerTaxShare / baseBeerTax) * 100) }
    ]
  });
}

function renderAlcohol() {
  const rows = alcoholRows();
  const yes = sum(rows, row => row.yes_count);
  const no = sum(rows, row => row.no_count);
  const known = yes + no;
  const knownShare = known ? yes / known : 0;
  const noShare = known ? no / known : 0;

  setText('alcoholKnownShare', percent1.format(knownShare));
  setText('alcoholKnownShareNote', `${number.format(yes)} yes out of ${number.format(known)} known responses`);
  setText('alcoholNoShare', percent1.format(noShare));
  setText('alcoholNoShareNote', `${number.format(no)} no out of ${number.format(known)} known responses`);
  setText('alcoholYesCount', number.format(yes));
  setText('alcoholYesCountNote', cohortLabels[state.cohort]);
  setText('alcoholNoCount', number.format(no));
  setText('alcoholNoCountNote', cohortLabels[state.cohort]);

  const labels = [...new Set(rows.map(row => row.occurrence_month))].sort();
  const byMonth = aggregate(rows, row => row.occurrence_month, row => 0);
  rows.forEach(row => {
    byMonth.set(row.occurrence_month, {
      yes: (byMonth.get(row.occurrence_month)?.yes || 0) + row.yes_count,
      no: (byMonth.get(row.occurrence_month)?.no || 0) + row.no_count
    });
  });
  const knownSeries = labels.map(label => {
    const row = byMonth.get(label);
    return row && (row.yes + row.no) ? (row.yes / (row.yes + row.no)) * 100 : 0;
  });
  const noSeries = labels.map(label => {
    const row = byMonth.get(label);
    return row && (row.yes + row.no) ? (row.no / (row.yes + row.no)) * 100 : 0;
  });
  lineChart(document.getElementById('alcoholChart'), {
    title: 'Monthly alcohol indication shares',
    labels: labels.map(label => parseDate(label).getMonth() === 0 ? String(parseDate(label).getFullYear()) : ''),
    tooltipLabels: labels.map(formatMonth),
    timelineDates: labels,
    percent: true,
    series: [
      { label: 'Yes: alcohol suspected', className: 'line-main', values: knownSeries },
      { label: 'No: alcohol not suspected', className: 'line-secondary', values: noSeries }
    ]
  });

  setText(
    'alcoholTakeaway',
    `Across ${state.from}-${state.to}, known alcohol responses split between ${percent1.format(knownShare)} Yes (alcohol suspected) and ${percent1.format(noShare)} No (alcohol not suspected). Unknown responses are excluded from this comparison.`
  );
}

function renderBreakdowns() {
  const rows = breakdownRows();
  const totals = aggregate(rows, row => row.dimension_value, row => row.notification_count);
  const ranking = [...totals.entries()]
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 8);
  const selectedTotal = sum(monthlyRowsFor(state.cohort), row => row.notification_count);
  const baseTotal = selectedTotal || 1;
  const topCategory = ranking[0];
  renderBars('breakdownBars', ranking, value => compact.format(value), row => `${percent1.format(row.value / baseTotal)} of selected cohort`);
  setText('breakdownTitle', state.dimension);
  setText(
    'breakdownCalculationNote',
    topCategory && selectedTotal
      ? `Out of ${number.format(selectedTotal)} selected SINAN notifications, ${percent1.format(topCategory.value / selectedTotal)} (${number.format(topCategory.value)}) are recorded as ${topCategory.label} in this ${state.dimension.toLowerCase()} breakdown.`
      : 'No notifications match the selected filters.'
  );
  setText(
    'breakdownCaption',
    state.dimension === 'Violence type' || state.dimension === 'Aggressor relationship'
      ? 'These are mention-based counts. A single notification can contribute to more than one category.'
      : 'These counts represent notifications in the selected cohort and years.'
  );
  setText('breakdownCohortNote', `Cohort: ${cohortLabels[state.cohort]}.`);
  setText('breakdownRegionNote', `Region filter: ${state.region === 'All' ? 'all Brazilian regions combined' : state.region}.`);
  setText(
    'breakdownMentionNote',
    state.dimension === 'Violence type' || state.dimension === 'Aggressor relationship'
      ? 'Totals can exceed the number of notifications because categories are mention-based.'
      : 'Shares are calculated against the selected cohort total, not against the subtotal of the displayed top eight categories.'
  );
}

function renderCalendar() {
  const counts = aggregate(calendarRows(), row => row.calendar_bucket, row => row.notification_count);
  const days = calendarDayMap();
  const rate = bucket => {
    const eligibleDays = days.get(bucket) || 0;
    return eligibleDays ? (counts.get(bucket) || 0) / eligibleDays : null;
  };
  const holidayRate = rate('Holiday');
  const weekendRate = rate('Non-holiday weekend');
  const weekdayRate = rate('Non-holiday weekday');
  const diff = weekdayRate ? (holidayRate / weekdayRate) - 1 : 0;

  setText('holidayRate', holidayRate === null ? 'N/A' : holidayRate.toFixed(1));
  setText('holidayRateNote', `${number.format(days.get('Holiday') || 0)} eligible holiday days`);
  setText('weekendRate', weekendRate === null ? 'N/A' : weekendRate.toFixed(1));
  setText('weekendRateNote', `${number.format(days.get('Non-holiday weekend') || 0)} eligible weekend days`);
  setText('weekdayRate', weekdayRate === null ? 'N/A' : weekdayRate.toFixed(1));
  setText('weekdayRateNote', `${number.format(days.get('Non-holiday weekday') || 0)} eligible weekdays`);
  setText('holidayVsWeekday', percent1.format(diff));
  setText('holidayVsWeekdayNote', 'difference versus non-holiday weekdays');

  renderBars('calendarBars', [
    { label: 'Holiday', value: holidayRate || 0 },
    { label: 'Non-holiday weekend', value: weekendRate || 0 },
    { label: 'Non-holiday weekday', value: weekdayRate || 0 }
  ], value => value.toFixed(1));

  const weekdayCounts = aggregate(weekdayRows(), row => row.day_of_week_name, row => row.notification_count);
  const weekdayDays = weekdayDayMap();
  const weekdayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const weekdayRanking = weekdayOrder.map(label => ({
    label,
    value: (weekdayDays.get(label) || 0) ? (weekdayCounts.get(label) || 0) / weekdayDays.get(label) : 0
  }));
  renderBars('weekdayBars', weekdayRanking, value => value.toFixed(1));

  const holidayAgg = new Map();
  holidayRows().forEach(row => {
    const current = holidayAgg.get(row.holiday_name) || { count: 0, occurrences: 0 };
    current.count += row.notification_count;
    current.occurrences += row.holiday_occurrences || 0;
    holidayAgg.set(row.holiday_name, current);
  });
  const holidayRanking = [...holidayAgg.entries()]
    .map(([label, value]) => ({
      label,
      value: value.occurrences ? value.count / value.occurrences : 0,
      total: value.count,
      occurrences: value.occurrences
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 8);
  renderBars('holidayBars', holidayRanking, value => value.toFixed(1), row => `${number.format(row.total)} notifications across ${number.format(row.occurrences)} occurrences`);
}

function renderProtection() {
  const violations = aggregate(violationRows(), row => row.violation_category, row => row.report_count);
  const violationRanking = [...violations.entries()]
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 8);
  renderBars('protectionViolationBars', violationRanking, value => compact.format(value));

  const channels = aggregate(channelRows(), row => row.report_channel, row => row.report_count);
  const channelRanking = [...channels.entries()]
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 8);
  renderBars('protectionChannelBars', channelRanking, value => compact.format(value));
}

function renderContext() {
  const quarterly = quarterlyRows();
  const quarterlyMap = aggregate(quarterly, row => row.year_quarter, row => row.notification_count);
  const ambev = data.ambev.filter(row => row.year >= state.from && row.year <= state.to);
  const labels = ambev.map(row => row.year_quarter);
  const sinanQuarterly = labels.map(label => quarterlyMap.get(label) || 0);
  const baseSinan = sinanQuarterly.find(value => value > 0) || 1;
  const baseAmbev = ambev[0]?.beer_volume_sold_000_hl || 1;
  lineChart(document.getElementById('contextChart'), {
    title: 'Indexed SINAN cohort and Ambev beer volume',
    labels: labels.map(label => label.endsWith('Q1') ? label.slice(0, 4) : ''),
    tooltipLabels: labels,
    timelineDates: ambev.map(row => row.quarter_start_date),
    tooltipFormatter: value => `Index: ${value.toFixed(1)}`,
    series: [
      { label: 'Selected SINAN cohort', className: 'line-main', values: sinanQuarterly.map(value => (value / baseSinan) * 100) },
      { label: 'Ambev Brazil beer volume', className: 'line-gold', values: ambev.map(row => (row.beer_volume_sold_000_hl / baseAmbev) * 100) }
    ]
  });
  setText(
    'contextCaption',
    state.region === 'All'
      ? `The SINAN line uses ${cohortLabels[state.cohort]}. The Ambev line is national beer volume, indexed to the first visible quarter.`
      : `The SINAN line is filtered to ${state.region}. The Ambev line remains a national beer-volume series, so the comparison is contextual only.`
  );

  const vigitel = vigitelRows();
  lineChart(document.getElementById('vigitelChart'), {
    title: 'Vigitel alcohol indicators',
    labels: vigitel.map(row => String(row.year)),
    timelineDates: vigitel.map(row => `${row.year}-12-31`),
    percent: true,
    series: [
      { label: 'Drank in last 30 days', className: 'line-teal', values: vigitel.map(row => row.weighted_current_alcohol_share === null ? null : row.weighted_current_alcohol_share * 100) },
      { label: 'Abusive consumption', className: 'line-gold', values: vigitel.map(row => row.weighted_abusive_alcohol_share === null ? null : row.weighted_abusive_alcohol_share * 100) }
    ]
  });

  const latestCurrent = [...vigitel].reverse().find(row => Number.isFinite(row.weighted_current_alcohol_share));
  const latestAbusive = [...vigitel].reverse().find(row => Number.isFinite(row.weighted_abusive_alcohol_share));
  const comparabilityNote = vigitel.find(row => row.year === 2024)?.current_alcohol_method_note;
  setText('latestVigitelCurrent', latestCurrent ? percent1.format(latestCurrent.weighted_current_alcohol_share) : 'N/A');
  setText('latestVigitelCurrentNote', latestCurrent ? `${latestCurrent.year} latest comparable survey year` : 'No comparable survey data');
  setText('latestVigitelAbusive', latestAbusive ? percent1.format(latestAbusive.weighted_abusive_alcohol_share) : 'N/A');
  setText('latestVigitelAbusiveNote', latestAbusive ? `${latestAbusive.year} survey year` : 'No survey data');
  setText('vigitelCaption', `Weighted Vigitel survey estimates for Brazilian capitals and the Federal District. 2022 is shown as no collection; the 2024 last-30-days value is intentionally unavailable because the legacy source field is not populated. ${comparabilityNote || ''}`);
}

function renderPolicyTimeline() {
  const timeline = document.getElementById('policyTimeline');
  timeline.innerHTML = policyTypes.map(type => {
    const events = policyEvents.filter(event => event.event_type === type);
    return `<article class="policy-type-panel ${policyTypeClass[type]}">
      <p class="eyebrow">${escapeHtml(type)}</p>
      <p class="policy-count">${events.length} events</p>
      <ol class="policy-event-list">
        ${events.map(event => `<li>
          <time datetime="${escapeHtml(event.event_date)}">${escapeHtml(event.date_precision === 'month' ? event.event_date.slice(0, 7) : event.event_date)}</time>
          <div>
            <strong>${escapeHtml(event.title)}</strong>
            <span>${escapeHtml(event.legal_reference || 'Policy context')}</span>
            <p>${escapeHtml(event.description)}</p>
            <small>${escapeHtml(event.verification_note || '')}</small>
            <a href="${escapeHtml(event.source_url)}" target="_blank" rel="noreferrer">Source</a>
          </div>
        </li>`).join('')}
      </ol>
    </article>`;
  }).join('');
}

function renderMethods() {
  const coverage = data.meta.coverage;
  setText(
    'coverageNote',
    `SINAN coverage in this extract runs from January 1, 2012 to December 31, 2025.`
  );
  setText(
    'refreshNote',
    `Dashboard snapshot exported on ${data.meta.refreshTimestamp}. DuckDB file: ${data.meta.database}`
  );
  document.getElementById('cohortDefinitions').innerHTML = data.meta.cohortDefinitions.map(def => `
    <article class="definition-card">
      <strong>${def.code}. ${def.name}</strong>
      <p>${def.rule}</p>
    </article>
  `).join('');
  document.getElementById('limitationsList').innerHTML = data.meta.notes
    .concat([
      'Calendar normalization uses the holiday table already loaded into the DuckDB project.',
      'The 2020 period should be interpreted cautiously because reporting systems and help-seeking behavior changed materially around the COVID-19 disruption.',
      `Protection-report coverage in this extract runs from ${String(coverage.protection_first_date).slice(0, 10)} to ${String(coverage.protection_last_date).slice(0, 10)}.`
    ])
    .map(note => `<li>${note}</li>`)
    .join('');
}

function render() {
  renderOverview();
  renderAlcohol();
  renderBreakdowns();
  renderCalendar();
  renderProtection();
  renderContext();
  renderPolicyTimeline();
  renderMethods();
}

function setupControls() {
  const years = [...new Set(data.monthlyCohort.map(row => row.occurrence_year))].sort((a, b) => a - b);
  const from = document.getElementById('fromYear');
  const to = document.getElementById('toYear');
  const cohort = document.getElementById('cohortSelect');
  const region = document.getElementById('regionSelect');
  const dimension = document.getElementById('dimensionSelect');
  const filterPanel = document.getElementById('filterPanel');
  const filterToggle = document.getElementById('mobileFilterToggle');
  const filterClose = document.getElementById('closeFilters');
  const filterBackdrop = document.getElementById('filterBackdrop');
  const applyFilters = document.getElementById('applyFilters');
  const filterSummary = document.getElementById('mobileFilterSummary');
  const filterCount = document.getElementById('activeFilterCount');
  const mobileQuery = window.matchMedia('(max-width: 680px)');
  const defaults = {
    from: years[0],
    to: years[years.length - 1],
    cohort: 'B',
    region: 'All'
  };
  let resetDimensionOnApply = false;
  let lastFocusedElement = null;

  from.innerHTML = years.map(year => `<option value="${year}">${year}</option>`).join('');
  to.innerHTML = years.map(year => `<option value="${year}">${year}</option>`).join('');
  cohort.innerHTML = Object.entries(cohortLabels).map(([code, label]) => `<option value="${code}">${label}</option>`).join('');
  region.innerHTML = regions.map(name => `<option value="${name}">${name}</option>`).join('');
  dimension.innerHTML = dimensions.map(name => `<option value="${name}">${name}</option>`).join('');

  const syncControlsFromState = () => {
    from.value = state.from;
    to.value = state.to;
    cohort.value = state.cohort;
    region.value = state.region;
  };

  const updateMobileSummary = () => {
    const activeCount = Number(state.from !== defaults.from || state.to !== defaults.to)
      + Number(state.cohort !== defaults.cohort)
      + Number(state.region !== defaults.region);
    filterCount.textContent = activeCount;
    filterCount.hidden = activeCount === 0;
    filterSummary.textContent = `${state.from}-${state.to} | ${state.region === 'All' ? 'All regions' : state.region}`;
  };

  const commitGlobalFilters = () => {
    state.from = Number(from.value);
    state.to = Number(to.value);
    state.cohort = cohort.value;
    state.region = region.value;
    if (resetDimensionOnApply) {
      state.dimension = 'Violence type';
      dimension.value = state.dimension;
      resetDimensionOnApply = false;
    }
    updateMobileSummary();
    render();
  };

  const closeMobileFilters = ({ restoreControls = true, restoreFocus = true } = {}) => {
    if (restoreControls) syncControlsFromState();
    resetDimensionOnApply = false;
    document.body.classList.remove('filters-open');
    filterPanel.classList.remove('is-open');
    filterPanel.setAttribute('aria-hidden', 'true');
    filterToggle.setAttribute('aria-expanded', 'false');
    filterBackdrop.hidden = true;
    if (restoreFocus && lastFocusedElement) lastFocusedElement.focus();
  };

  const openMobileFilters = () => {
    if (!mobileQuery.matches) return;
    syncControlsFromState();
    lastFocusedElement = document.activeElement;
    document.body.classList.add('filters-open');
    filterPanel.classList.add('is-open');
    filterPanel.setAttribute('role', 'dialog');
    filterPanel.setAttribute('aria-modal', 'true');
    filterPanel.setAttribute('aria-hidden', 'false');
    filterToggle.setAttribute('aria-expanded', 'true');
    filterBackdrop.hidden = false;
    window.setTimeout(() => filterClose.focus(), 200);
  };

  syncControlsFromState();
  dimension.value = state.dimension;
  updateMobileSummary();
  if (mobileQuery.matches) filterPanel.setAttribute('aria-hidden', 'true');

  from.addEventListener('change', () => {
    if (Number(from.value) > Number(to.value)) {
      to.value = from.value;
    }
    if (!mobileQuery.matches) commitGlobalFilters();
  });

  to.addEventListener('change', () => {
    if (Number(to.value) < Number(from.value)) {
      from.value = to.value;
    }
    if (!mobileQuery.matches) commitGlobalFilters();
  });

  cohort.addEventListener('change', () => {
    if (!mobileQuery.matches) commitGlobalFilters();
  });

  region.addEventListener('change', () => {
    if (!mobileQuery.matches) commitGlobalFilters();
  });

  dimension.addEventListener('change', () => {
    state.dimension = dimension.value;
    render();
  });

  document.getElementById('resetFilters').addEventListener('click', () => {
    from.value = defaults.from;
    to.value = defaults.to;
    cohort.value = defaults.cohort;
    region.value = defaults.region;
    resetDimensionOnApply = true;
    if (!mobileQuery.matches) commitGlobalFilters();
  });

  filterToggle.addEventListener('click', openMobileFilters);
  filterClose.addEventListener('click', () => closeMobileFilters());
  filterBackdrop.addEventListener('click', () => closeMobileFilters());
  applyFilters.addEventListener('click', () => {
    commitGlobalFilters();
    closeMobileFilters({ restoreControls: false });
  });

  filterPanel.addEventListener('keydown', event => {
    if (!filterPanel.classList.contains('is-open')) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      closeMobileFilters();
      return;
    }
    if (event.key !== 'Tab') return;
    const focusable = [...filterPanel.querySelectorAll('button:not([disabled]), select:not([disabled])')];
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  mobileQuery.addEventListener('change', event => {
    if (event.matches) {
      filterPanel.setAttribute('role', 'dialog');
      filterPanel.setAttribute('aria-modal', 'true');
      filterPanel.setAttribute('aria-hidden', 'true');
    } else {
      closeMobileFilters({ restoreFocus: false });
      filterPanel.removeAttribute('role');
      filterPanel.removeAttribute('aria-modal');
      filterPanel.removeAttribute('aria-hidden');
    }
  });
}

if (data) {
  setupControls();
  render();
} else {
  document.querySelector('main').innerHTML = '<section class="section"><h1>Dashboard data is missing.</h1></section>';
}
