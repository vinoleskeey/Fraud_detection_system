// Simple Fraud Detector JS
console.log('Simple Fraud Detector Loaded');

let chartInstance = null;

// Presets for V1-V28 (defaults)
const defaultPreset = {
  safe: { Amount: 50, Time: 10, V1: 0, V2: 0.1, V3: -0.1, V4:0, V5:0, V6:0, V7:0, V8:0, V9:0, V10:0, V11:0, V12:0, V13:0, V14:0, V15:0, V16:0, V17:0, V18:0, V19:0, V20:0, V21:0, V22:0, V23:0, V24:0, V25:0, V26:0, V27:0, V28:0 },
  fraud: { Amount: 1000, Time: 100, V1: -5, V2: 4.5, V3: -2.8, V4:-1.2, V5:3.1, V6:-0.8, V7:2.4, V8:-1.9, V9:1.5, V10:-2.7, V11:0.9, V12:-1.1, V13:2.0, V14:-0.5, V15:1.8, V16:-1.3, V17:0.6, V18: -0.2, V19:1.2, V20: -0.9, V21:0.3, V22:1.0, V23: -0.4, V24:0.7, V25:-0.6, V26:0.8, V27: -0.1, V28:0.2 },
  random: { Amount: (Math.random()*1000 + 10), Time: Math.random()*10000, V1: (Math.random()-0.5)*10, V2: (Math.random()-0.5)*10 /* ... all random */ }
};

// Load preset
function loadPreset(type) {
  const p = defaultPreset[type];
  document.getElementById('Amount').value = p.Amount;
  document.getElementById('Time').value = p.Time;
}

// Get complete form data (V1-V28 = 0 if not present)
function getFormData() {
  const data = {
    Time: parseFloat(document.getElementById('Time').value) || 0,
    Amount: parseFloat(document.getElementById('Amount').value) || 0
  };
  // Add V1-V28 (defaults 0, override presets)
  for (let i = 1; i <= 28; i++) {
    data[`V${i}`] = 0; // Default
  }
  return data;
}

// Predict
async function predictFraud() {
  const btn = document.getElementById('predictBtn');
  btn.disabled = true;
  btn.textContent = 'Analyzing...';

  try {
    const data = getFormData();
    const response = await fetch('/api/predict', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }
    
    const result = await response.json();
    showResult(result);
    loadHistory();
  } catch (error) {
    console.error('Error:', error);
    alert('Prediction failed: ' + error.message + '\nConsole for details');
  }
  
  btn.disabled = false;
  btn.textContent = '🔍 Check for Fraud';
}

// Show result
function showResult(result) {
  const section = document.getElementById('resultSection');
  section.style.display = 'block';
  
  const isFraud = result.is_fraud;
  const conf = result.confidence * 100;
  const risk = result.risk_score * 100;
  
  document.getElementById('riskText').innerHTML = isFraud ? '🚨 FRAUD DETECTED' : '✅ SAFE TRANSACTION';
  document.getElementById('riskText').style.color = isFraud ? '#ef4444' : '#10b981';
  
  document.getElementById('confidenceText').innerHTML = `
    Confidence: ${conf.toFixed(1)}%
    <br>Risk Score: ${risk.toFixed(1)}%
  `;
  
  // Gauge
  const canvas = document.getElementById('riskGauge');
  const ctx = canvas.getContext('2d');
  canvas.width = 250;
  canvas.height = 250;
  
  if (chartInstance) chartInstance.destroy();
  chartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [risk, 100-risk],
        backgroundColor: isFraud ? ['#ef4444', '#475569'] : ['#10b981', '#475569']
      }]
    },
    options: {
      cutout: '70%',
      plugins: { legend: { display: false } }
    }
  });
}

// Load history
async function loadHistory() {
  try {
    const res = await fetch('/api/history');
    const history = await res.json();
    const tbody = document.getElementById('historyBody');
    tbody.innerHTML = '';
    
    history.slice(0,10).forEach(tx => {
      const row = tbody.insertRow();
      row.innerHTML = `
        <td>$${tx.Amount?.toFixed(2) || 0}</td>
        <td>${tx.is_fraud ? '🚨 Fraud' : '✅ Safe'}</td>
        <td>${(tx.risk_score * 100).toFixed(1)}%</td>
        <td>${new Date(tx.created_at).toLocaleString()}</td>
      `;
    });
  } catch (e) {
    console.error('History error:', e);
  }
}

// Init
loadHistory();
