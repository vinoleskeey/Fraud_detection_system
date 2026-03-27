'use strict';

let gaugeChart = null;

/* ─── Feature inputs ─────────────────────────────────────────── */
(function buildFeatureInputs() {
  const grid = document.getElementById('vFeatures');
  if (!grid) return;
  for (let i = 1; i <= 28; i++) {
    const div = document.createElement('div');
    div.className = 'form-group';
    div.innerHTML = `<label>V${i}</label><input type="number" id="V${i}" step="0.000001" value="0" placeholder="0.000000">`;
    grid.appendChild(div);
  }
})();

/* ─── Toggle advanced features ───────────────────────────────── */
function toggleFeatures() {
  const section = document.getElementById('featureSection');
  const icon    = document.getElementById('toggleIcon');
  const isOpen  = section.classList.toggle('open');
  icon.textContent = isOpen ? '▲' : '▼';
}

/* ─── Presets ────────────────────────────────────────────────── */
const PRESETS = {
  safe: {
    Amount: 45.50, Time: 3600,
    V1: 1.19, V2: 0.26, V3: 0.17, V4: 0.45, V5: -0.06, V6: -0.08,
    V7: 0.12, V8: -0.08, V9: 0.29, V10: -0.12, V11: 0.17, V12: 0.27,
    V13: -0.04, V14: -0.11, V15: 0.05, V16: -0.07, V17: 0.09, V18: 0.15,
    V19: -0.05, V20: 0.04, V21: 0.01, V22: 0.03, V23: 0.00, V24: 0.02,
    V25: -0.01, V26: 0.05, V27: 0.00, V28: 0.01,
  },
  fraud: {
    // Real fraud transaction from the training dataset (Class=1)
    Amount: 0.0, Time: 406,
    V1: -2.3122, V2: 1.9520, V3: -1.6099, V4: 3.9979, V5: -0.5222, V6: -1.4265,
    V7: -2.5374, V8: 1.3917, V9: -2.7701, V10: -2.7723, V11: 3.2020, V12: -2.8996,
    V13: -0.5952, V14: -4.2895, V15: 0.3898, V16: -1.1407, V17: -2.8304, V18: -0.0168,
    V19: 0.4165, V20: 0.1267, V21: 0.5176, V22: -0.0354, V23: -0.4654, V24: 0.2480,
    V25: 0.6514, V26: 0.0693, V27: -0.2258, V28: -0.1639,
  },
};

function loadPreset(type) {
  if (type === 'random') {
    document.getElementById('Amount').value = (Math.random() * 2000 + 10).toFixed(2);
    document.getElementById('Time').value   = Math.floor(Math.random() * 172800);
    for (let i = 1; i <= 28; i++) {
      document.getElementById(`V${i}`).value = ((Math.random() - 0.5) * 6).toFixed(6);
    }
    showToast('Random transaction loaded', 'info');
    return;
  }
  const p = PRESETS[type];
  document.getElementById('Amount').value = p.Amount;
  document.getElementById('Time').value   = p.Time;
  for (let i = 1; i <= 28; i++) {
    const el = document.getElementById(`V${i}`);
    if (el) el.value = p[`V${i}`] ?? 0;
  }
  showToast(type === 'safe' ? 'Safe transaction preset loaded' : 'Fraud transaction preset loaded',
            type === 'safe' ? 'success' : 'error');
}

/* ─── Collect form data ──────────────────────────────────────── */
function getFormData() {
  const data = {
    Time:   parseFloat(document.getElementById('Time').value)   || 0,
    Amount: parseFloat(document.getElementById('Amount').value) || 0,
  };
  for (let i = 1; i <= 28; i++) {
    data[`V${i}`] = parseFloat(document.getElementById(`V${i}`)?.value) || 0;
  }
  return data;
}

/* ─── Predict ────────────────────────────────────────────────── */
async function predictFraud() {
  const btn = document.getElementById('predictBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Analyzing…';

  try {
    const data     = getFormData();
    const response = await fetch('/api/predict', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(data),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || `Server error ${response.status}`);
    }

    displayResult(result);
    await loadStats();
    await loadHistory();

  } catch (err) {
    showToast(err.message, 'error');
    const section = document.getElementById('resultSection');
    section.style.display = 'block';
    section.innerHTML = `
      <div class="card">
        <div class="section-title"><span class="icon">!</span> Error</div>
        <p style="color:#fca5a5">${err.message}</p>
      </div>`;
  } finally {
    btn.disabled  = false;
    btn.innerHTML = '<span>&#128269;</span> Analyze Transaction';
  }
}

/* ─── Display result ─────────────────────────────────────────── */
function displayResult(result) {
  const isFraud   = result.is_fraud;
  const riskPct   = Math.min(100, Math.max(0, result.risk_score * 100));
  const confPct   = Math.min(100, Math.max(0, result.confidence * 100));
  const riskClass = riskPct >= 60 ? 'high' : riskPct >= 35 ? 'medium' : 'low';

  const section = document.getElementById('resultSection');
  section.style.display = 'block';

  section.innerHTML = `
    <div class="card">
      <div class="section-title">
        <span class="icon">&#127919;</span> Analysis Result
      </div>
      <div class="result-wrap ${isFraud ? 'fraud-result' : 'safe-result'}">
        <p class="result-status">${isFraud ? '&#x1F6A8; FRAUD DETECTED' : '&#x2705; TRANSACTION SAFE'}</p>
        <p class="result-subtitle">
          ${isFraud
            ? 'This transaction shows strong indicators of fraudulent activity.'
            : 'No fraud indicators found. Transaction appears legitimate.'}
          ${result.transaction_id ? `&nbsp;&bull;&nbsp; ID #${result.transaction_id}` : ''}
        </p>

        <div class="gauge-wrap">
          <canvas id="riskGauge" width="200" height="200"></canvas>
          <div class="gauge-center">
            <div class="gauge-percent" style="color:${isFraud ? '#fca5a5' : '#6ee7b7'}">${riskPct.toFixed(1)}%</div>
            <div class="gauge-label">Risk</div>
          </div>
        </div>

        <div class="result-metrics">
          <div class="metric-item">
            <div class="metric-value" style="color:${isFraud ? '#fca5a5' : '#6ee7b7'}">${riskPct.toFixed(2)}%</div>
            <div class="metric-label">Risk Score</div>
          </div>
          <div class="metric-item">
            <div class="metric-value" style="color:#93c5fd">${confPct.toFixed(2)}%</div>
            <div class="metric-label">Confidence</div>
          </div>
          <div class="metric-item">
            <span class="risk-pill ${riskClass}">${riskClass.toUpperCase()}</span>
            <div class="metric-label" style="margin-top:6px">Risk Level</div>
          </div>
        </div>
      </div>
    </div>`;

  const canvas = document.getElementById('riskGauge');
  if (gaugeChart) { gaugeChart.destroy(); gaugeChart = null; }
  gaugeChart = new Chart(canvas.getContext('2d'), {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [riskPct, 100 - riskPct],
        backgroundColor: isFraud
          ? ['#ef4444', 'rgba(255,255,255,.06)']
          : ['#10b981', 'rgba(255,255,255,.06)'],
        borderWidth: 0,
      }],
    },
    options: {
      cutout:   '78%',
      rotation: -90,
      plugins:  { legend: { display: false }, tooltip: { enabled: false } },
      animation: { duration: 900, easing: 'easeInOutQuart' },
    },
  });

  showToast(
    isFraud ? 'Fraud alert! High-risk transaction detected.' : 'Transaction cleared — no fraud detected.',
    isFraud ? 'error' : 'success',
  );
}

/* ─── Stats bar ──────────────────────────────────────────────── */
async function loadStats() {
  try {
    const res   = await fetch('/api/stats');
    const stats = await res.json();
    if (!res.ok) return;

    setValue('statTotal',     stats.total);
    setValue('statFraud',     stats.fraud);
    setValue('statSafe',      stats.safe);
    setValue('statFraudRate', `${stats.fraud_rate}%`);
  } catch (_) { /* silent — stats are informational */ }
}

function setValue(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

/* ─── History ────────────────────────────────────────────────── */
async function loadHistory() {
  try {
    const res     = await fetch('/api/history?limit=20');
    const history = await res.json();
    if (!res.ok) throw new Error(history.error || 'Failed to load history');
    renderHistory(history);
  } catch (err) {
    console.error('History error:', err);
  }
}

function renderHistory(history) {
  const tbody = document.getElementById('historyBody');
  if (!tbody) return;

  if (!history.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="history-empty">No transactions yet.</td></tr>';
    return;
  }

  tbody.innerHTML = history.slice(0, 20).map(tx => {
    const riskPct  = (tx.risk_score * 100).toFixed(1);
    const riskCls  = tx.risk_score >= 0.6 ? 'high' : tx.risk_score >= 0.35 ? 'medium' : 'low';
    const badge    = tx.is_fraud
      ? '<span class="badge fraud">Fraud</span>'
      : '<span class="badge safe">Safe</span>';
    const date     = new Date(tx.created_at).toLocaleString(undefined, {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    });
    return `<tr>
      <td>${tx.id || '–'}</td>
      <td class="amount">$${(tx.Amount ?? 0).toFixed(2)}</td>
      <td>${tx.Time != null ? tx.Time.toFixed(0) : '–'}</td>
      <td>${badge}</td>
      <td><span class="risk-pill ${riskCls}">${riskPct}%</span></td>
      <td class="muted">${date}</td>
    </tr>`;
  }).join('');
}

/* ─── Toast ──────────────────────────────────────────────────── */
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast     = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('fade-out');
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
  }, 3500);
}

/* ─── Init ───────────────────────────────────────────────────── */
(async function init() {
  await Promise.all([loadStats(), loadHistory()]);
})();

document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !document.getElementById('predictBtn').disabled) {
    predictFraud();
  }
});
