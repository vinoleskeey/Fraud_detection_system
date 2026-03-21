// Professional Fraud Detection Frontend
console.log('Fraud Detection Dashboard Loaded');

let historyChart = null;

// Initialize feature inputs
function initFeatures() {
  const vFeatures = document.getElementById('vFeatures');
  for (let i = 1; i <= 28; i++) {
    const div = document.createElement('div');
    div.className = 'form-group';
    div.innerHTML = `
      <label>V${i}</label>
      <input type="number" id="V${i}" step="0.01" value="0" placeholder="0.00">
    `;
    vFeatures.appendChild(div);
  }
}

initFeatures();

// Toggle advanced features
function toggleFeatures() {
  const section = document.getElementById('featureSection');
  const icon = document.getElementById('toggleIcon');
  section.classList.toggle('active');
  icon.textContent = section.classList.contains('active') ? '▲' : '▼';
}

// Get all form data
function getFormData() {
  const data = {
    Time: parseFloat(document.getElementById('Time').value) || 0,
    Amount: parseFloat(document.getElementById('Amount').value) || 0
  };
  
  for (let i = 1; i <= 28; i++) {
    data[`V${i}`] = parseFloat(document.getElementById(`V${i}`).value) || 0;
  }
  
  return data;
}

// Predict fraud
async function predictFraud() {
  const btn = document.getElementById('predictBtn');
  const originalText = btn.innerHTML;
  
  btn.disabled = true;
  btn.innerHTML = '<span class="loading"></span> Analyzing...';
  
  try {
    const data = getFormData();
    const response = await fetch('/api/predict', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    });
    
    if (!response.ok) throw new Error('Prediction failed');
    
    const result = await response.json();
    displayResult(result);
    loadHistory();
    
  } catch (error) {
    console.error('Prediction error:', error);
    document.getElementById('resultSection').innerHTML = `
      <div class="card">
        <h2 class="section-title">❌ Error</h2>
        <p style="color: #f87171;">${error.message}. Please check your inputs.</p>
      </div>
    `;
  }
  
  btn.disabled = false;
  btn.innerHTML = originalText;
}

// Display prediction result
function displayResult(result) {
  const section = document.getElementById('resultSection');
  section.style.display = 'block';
  
  const isFraud = result.is_fraud;
  const confidence = result.confidence;
  const riskScore = result.risk_score;
  
  const statusText = isFraud ? '🚨 HIGH RISK FRAUD' : '✅ TRANSACTION SAFE';
  const statusClass = isFraud ? 'result-fraud' : 'result-safe';
  
  document.getElementById('riskText').textContent = statusText;
  document.getElementById('riskText').className = statusClass;
  document.getElementById('confidenceText').innerHTML = `
    <p><strong>Confidence:</strong> ${(confidence * 100).toFixed(1)}%</p>
    <p><strong>Risk Score:</strong> ${(riskScore * 100).toFixed(1)}%</p>
  `;
  
  // Create gauge chart
  const ctx = document.getElementById('riskGauge').innerHTML = '';
  const canvas = document.createElement('canvas');
  canvas.width = 200;
  canvas.height = 200;
  document.getElementById('riskGauge').appendChild(canvas);
  
  const riskCtx = canvas.getContext('2d');
  new Chart(riskCtx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [riskScore * 100, 100 - riskScore * 100],
        backgroundColor: isFraud ? ['#ef4444', '#374151'] : ['#10b981', '#374151']
      }]
    },
    options: {
      cutout: '80%',
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      }
    }
  });
}

// Load history
async function loadHistory() {
  try {
    const response = await fetch('/api/history');
    const history = await response.json();
    displayHistory(history);
  } catch (error) {
    console.error('History load error:', error);
  }
}

// Display history table
function displayHistory(history) {
  const tbody = document.getElementById('historyBody');
  tbody.innerHTML = '';
  
  history.slice(0, 10).forEach(tx => {
    const row = tbody.insertRow();
    row.innerHTML = `
      <td>${tx.Time?.toFixed(0) || 'N/A'}</td>
      <td>$${tx.Amount?.toFixed(2) || '0.00'}</td>
      <td>${tx.is_fraud ? '🚨 Fraud' : '✅ Safe'}</td>
      <td>${(tx.confidence * 100).toFixed(1)}%</td>
      <td>${(tx.risk_score * 100).toFixed(1)}%</td>
      <td>${new Date(tx.created_at).toLocaleString()}</td>
    `;
  });
}

// Auto load history on start
loadHistory();

// Enter key support
document.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !document.getElementById('predictBtn').disabled) {
    predictFraud();
  }
});
