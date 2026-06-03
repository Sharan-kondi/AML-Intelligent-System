// ============================================================================
//  AML Intelligence Dashboard — Main Application Module
// ============================================================================

const API_BASE = window.location.origin + '/api';
const chartInstances = {};

// ---------------------------------------------------------------------------
//  Utilities
// ---------------------------------------------------------------------------

function formatCurrency(n) {
  return n == null ? '₹0' : '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 2 });
}

function getRiskColor(s) {
  return s >= 80 ? '#EF4444' : s >= 50 ? '#F59E0B' : '#10B981';
}

function getRiskLabel(s) {
  return s >= 80 ? 'HIGH' : s >= 50 ? 'MEDIUM' : 'LOW';
}

function createChart(id, cfg) {
  if (chartInstances[id]) { chartInstances[id].destroy(); delete chartInstances[id]; }
  const el = document.getElementById(id);
  if (!el) return null;
  const c = new Chart(el, cfg);
  chartInstances[id] = c;
  return c;
}

function initIcons() { if (typeof lucide !== 'undefined') lucide.createIcons(); }

async function api(ep) {
  try {
    const r = await fetch(API_BASE + ep);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } catch (e) { console.error(`API [${ep}]:`, e); return null; }
}

function errorCard(msg = 'Unable to load data. Is the API running?') {
  return `<div class="card" style="text-align:center;padding:3rem;">
    <div style="font-size:2.5rem;margin-bottom:1rem;">⚠️</div>
    <h3 style="color:#F59E0B;margin-bottom:.5rem;">Error</h3>
    <p style="color:#8B95A8;">${msg}</p></div>`;
}

function pageHeader(t, s) {
  return `<div class="page-header animate-in"><h2>${t}</h2>${s ? `<p>${s}</p>` : ''}</div>`;
}

// ---------------------------------------------------------------------------
//  Router
// ---------------------------------------------------------------------------

const routes = {
  overview:          renderOverview,
  network:           renderNetwork,
  'fraud-detection': renderFraudDetection,
  'fraud-rings':     renderFraudRings,
  gnn:               renderGNN,
  investigation:     renderInvestigation,
  xai:               renderXAI,
};

function navigate(page) {
  document.querySelectorAll('.nav-item').forEach(l => l.classList.toggle('active', l.dataset.page === page));
  (routes[page] || renderOverview)();
}

// ---------------------------------------------------------------------------
//  Overview
// ---------------------------------------------------------------------------

async function renderOverview() {
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    ${pageHeader('Dashboard Overview', 'Real-time AML Intelligence Monitoring')}
    <div class="kpi-grid" id="kpiGrid">
      <div class="card metric-card skeleton" style="min-height:140px;"></div>
      <div class="card metric-card skeleton" style="min-height:140px;"></div>
      <div class="card metric-card skeleton" style="min-height:140px;"></div>
      <div class="card metric-card skeleton" style="min-height:140px;"></div>
    </div>
    <div class="charts-row">
      <div class="card chart-container animate-in animate-delay-3">
        <h3 style="margin-bottom:1rem;color:var(--text-primary);">Hourly Transaction Activity</h3>
        <canvas id="activityChart"></canvas>
      </div>
      <div class="card chart-container animate-in animate-delay-4">
        <h3 style="margin-bottom:1rem;color:var(--text-primary);">Risk Score Distribution</h3>
        <canvas id="riskDistChart"></canvas>
      </div>
    </div>`;

  const [metrics, heatmap, riskDist] = await Promise.all([
    api('/metrics'), api('/activity-heatmap'), api('/risk-distribution'),
  ]);

  if (metrics) {
    const kpis = [
      { icon: '📋', label: 'Total Cases',   value: metrics.total_cases ?? 0,          accent: 'cyan' },
      { icon: '🔍', label: 'Suspicious',     value: metrics.suspicious_accounts ?? 0,  accent: 'red' },
      { icon: '⚠️', label: 'High Risk',      value: metrics.high_risk_accounts ?? 0,   accent: 'amber' },
      { icon: '🕸️', label: 'Fraud Rings',     value: metrics.fraud_rings_detected ?? 0, accent: 'purple' },
    ];
    document.getElementById('kpiGrid').innerHTML = kpis.map((k, i) => `
      <div class="card metric-card accent-${k.accent} animate-in animate-delay-${i + 1}">
        <span class="metric-icon">${k.icon}</span>
        <div class="metric-value">${k.value.toLocaleString()}</div>
        <div class="metric-label">${k.label}</div>
      </div>`).join('');
  }

  if (heatmap && heatmap.hours) {
    const ctx = document.getElementById('activityChart').getContext('2d');
    const grad = ctx.createLinearGradient(0, 0, 0, 350);
    grad.addColorStop(0, 'rgba(0,245,212,0.3)');
    grad.addColorStop(1, 'rgba(59,130,246,0.02)');
    createChart('activityChart', {
      type: 'line',
      data: {
        labels: heatmap.hours.map(h => h.hour),
        datasets: [{ label: 'Transactions', data: heatmap.hours.map(h => h.transactions),
          borderColor: '#00F5D4', backgroundColor: grad, fill: true, tension: 0.4,
          pointRadius: 3, pointBackgroundColor: '#00F5D4', borderWidth: 2 }],
      },
      options: { responsive: true, plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#8B95A8' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#8B95A8' } },
        },
      },
    });
  }

  if (riskDist && riskDist.distribution) {
    const d = riskDist.distribution;
    createChart('riskDistChart', {
      type: 'bar',
      data: {
        labels: d.map(x => x.range),
        datasets: [{ label: 'Accounts', data: d.map(x => x.count),
          backgroundColor: d.map((_, i) => i < 4 ? '#10B981' : i < 7 ? '#F59E0B' : '#EF4444'),
          borderRadius: 6, maxBarThickness: 40 }],
      },
      options: { responsive: true, plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#8B95A8', font: { size: 11 } } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#8B95A8' } },
        },
      },
    });
  }
  initIcons();
}

// ---------------------------------------------------------------------------
//  Network Graph — optimized physics & real-time differential streaming
// ---------------------------------------------------------------------------

async function renderNetwork() {
  const main = document.getElementById('mainContent');
  if (window.liveNetworkInterval) {
    clearInterval(window.liveNetworkInterval);
    window.liveNetworkInterval = null;
  }

  main.innerHTML = `
    ${pageHeader('Live AML Network', 'Interactive Transaction Graph — Click nodes to investigate')}
    <div style="margin-bottom: 12px; display: flex; align-items: center; gap: 8px;" class="animate-in animate-delay-1">
      <span class="status-dot active"></span>
      <span style="font-size: 0.85rem; color: var(--accent-cyan); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Live streaming via Kafka & Spark</span>
    </div>
    <div class="card animate-in animate-delay-1" style="padding:8px;">
      <div id="graphContainer" class="graph-container" style="position:relative;"></div>
    </div>
    <div id="nodeDetail" class="card animate-in" style="display:none;margin-top:1.5rem;padding:1.5rem;"></div>`;

  const container = document.getElementById('graphContainer');

  try {
    const data = await api('/graph-data');
    if (!data || !data.nodes || data.nodes.length === 0) {
      container.innerHTML = errorCard('Unable to load graph data or no alert cases active.');
      initIcons(); return;
    }

    const visObj = window.vis || (typeof vis !== 'undefined' ? vis : null);
    let visSuccess = false;

    if (visObj) {
      try {
        console.log("[Graph Engine] Vis-Network detected, attempting standard UMD render...");
        await renderVisGraph(container, data, visObj);
        visSuccess = true;
      } catch (visErr) {
        console.error("[Graph Engine] Vis-Network initialization failed:", visErr);
      }
    }

    if (!visSuccess) {
      console.log("[Graph Engine] Vis-Network not active. Booting custom high-fidelity Canvas graph engine.");
      renderCustomCanvasNetwork(container, data);
    }

  } catch (globalErr) {
    console.error("[Graph Engine] Global network graph load error:", globalErr);
    container.innerHTML = errorCard(`Failed to initialize network graph: ${globalErr.message}`);
  }
  
  initIcons();
}

async function renderVisGraph(container, data, visObj) {
  let nodesDataset = null;
  let edgesDataset = null;
  let networkInstance = null;

  async function updateGraphData(isFirstLoad = false) {
    const currentData = isFirstLoad ? data : await api('/graph-data');
    if (!currentData || !currentData.nodes) return;

    const formattedNodes = currentData.nodes.map(n => ({
      id: n.id,
      label: n.label || n.id,
      color: { background: n.color, border: n.color, highlight: { background: '#fff', border: '#00F5D4' } },
      font: { color: '#E2E8F0', size: 11, face: 'Inter' },
      shape: 'dot',
      size: n.size || 18,
      riskScore: n.risk_score,
      suspicious: n.suspicious,
    }));

    const formattedEdges = currentData.edges.map(e => ({
      id: `${e.from}-${e.to}`,
      from: e.from,
      to: e.to,
      value: e.value || 1,
      title: e.title || '',
      arrows: 'to',
      color: { color: 'rgba(0,245,212,0.2)', highlight: '#00F5D4' },
      width: Math.max(0.3, Math.min(3, (e.value || 1) / 30000)),
      smooth: { type: 'continuous' },
    }));

    if (isFirstLoad) {
      nodesDataset = new visObj.DataSet(formattedNodes);
      edgesDataset = new visObj.DataSet(formattedEdges);

      networkInstance = new visObj.Network(container, { nodes: nodesDataset, edges: edgesDataset }, {
        physics: {
          enabled: true,
          barnesHut: { gravitationalConstant: -3000, centralGravity: 0.4, springLength: 100, damping: 0.12 },
          stabilization: { iterations: 60, fit: true },
        },
        interaction: { hover: true, tooltipDelay: 150 },
      });

      networkInstance.once('stabilizationIterationsDone', () => {
        networkInstance.setOptions({ physics: { enabled: false } });
      });

      networkInstance.on('click', params => {
        const panel = document.getElementById('nodeDetail');
        if (!params.nodes.length) { panel.style.display = 'none'; return; }
        const node = nodesDataset.get(params.nodes[0]);
        if (!node) return;
        const risk = node.riskScore ?? 0;
        const rc = getRiskColor(risk);
        const cn = networkInstance.getConnectedNodes(params.nodes[0]);
        const ce = networkInstance.getConnectedEdges(params.nodes[0]);
        panel.style.display = 'block';
        panel.innerHTML = `
          <div style="display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap;">
            <div>
              <h3 style="color:var(--text-primary);margin-bottom:6px;font-family:var(--font-mono);">${node.label}</h3>
              <span class="badge" style="background:${rc}20;color:${rc};border:1px solid ${rc}40;">${getRiskLabel(risk)} RISK — ${risk.toFixed(1)}</span>
            </div>
            <div style="margin-left:auto;display:flex;gap:2rem;">
              <div style="text-align:center;"><div style="font-size:1.5rem;font-weight:700;color:#00F5D4;">${cn.length}</div><div style="color:#8B95A8;font-size:.75rem;">Connections</div></div>
              <div style="text-align:center;"><div style="font-size:1.5rem;font-weight:700;color:#3B82F6;">${ce.length}</div><div style="color:#8B95A8;font-size:.75rem;">Transactions</div></div>
              <div style="text-align:center;"><div style="font-size:1.5rem;font-weight:700;color:${node.suspicious ? '#EF4444' : '#10B981'};">${node.suspicious ? 'YES' : 'NO'}</div><div style="color:#8B95A8;font-size:.75rem;">Suspicious</div></div>
            </div>
          </div>`;
      });
    } else {
      const existingNodeIds = nodesDataset.getIds();
      const newNodeIds = new Set(formattedNodes.map(n => n.id));
      const nodesToRemove = existingNodeIds.filter(id => !newNodeIds.has(id));
      if (nodesToRemove.length > 0) nodesDataset.remove(nodesToRemove);
      nodesDataset.update(formattedNodes);

      const existingEdgeIds = edgesDataset.getIds();
      const newEdgeIds = new Set(formattedEdges.map(e => e.id));
      const edgesToRemove = existingEdgeIds.filter(id => !newEdgeIds.has(id));
      if (edgesToRemove.length > 0) edgesDataset.remove(edgesToRemove);
      edgesDataset.update(formattedEdges);
    }
  }

  await updateGraphData(true);

  window.liveNetworkInterval = setInterval(async () => {
    if (document.getElementById('graphContainer') && !document.getElementById('networkCanvas')) {
      await updateGraphData(false);
    } else if (!document.getElementById('graphContainer')) {
      clearInterval(window.liveNetworkInterval);
      window.liveNetworkInterval = null;
    }
  }, 4000);
}

// ---------------------------------------------------------------------------
//  High-Fidelity Custom Canvas Interactive Floating Network Fallback
// ---------------------------------------------------------------------------

function renderCustomCanvasNetwork(container, data) {
  container.innerHTML = `<canvas id="networkCanvas" style="width: 100%; height: 100%; display: block; background: #0C1426; cursor: grab;"></canvas>`;
  const canvas = document.getElementById('networkCanvas');
  const ctx = canvas.getContext('2d');

  function resize() {
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  }
  resize();
  window.addEventListener('resize', resize);

  const width = canvas.width / window.devicePixelRatio;
  const height = canvas.height / window.devicePixelRatio;

  let nodes = data.nodes.map(n => ({
    id: n.id,
    label: n.label || n.id,
    x: Math.random() * (width - 160) + 80,
    y: Math.random() * (height - 160) + 80,
    vx: (Math.random() - 0.5) * 0.5,
    vy: (Math.random() - 0.5) * 0.5,
    radius: Math.max(12, Math.min(22, (n.risk_score || 50) / 4.5)),
    riskScore: n.risk_score || 0,
    color: n.color || '#10B981',
    suspicious: n.suspicious || false
  }));

  const nodeMap = new Map(nodes.map(n => [n.id, n]));
  let edges = data.edges.map(e => ({
    from: nodeMap.get(e.from),
    to: nodeMap.get(e.to),
    value: e.value || 1000,
    title: e.title || `₹${(e.value || 1000).toLocaleString()}`,
    particles: []
  })).filter(e => e.from && e.to);

  // Distribute streaming neon money particles
  edges.forEach(e => {
    const count = Math.min(3, Math.max(1, Math.floor((e.value || 10000) / 30000)));
    for (let i = 0; i < count; i++) {
      e.particles.push({
        progress: Math.random(),
        speed: 0.003 + Math.random() * 0.005
      });
    }
  });

  let selectedNode = null;
  let hoveredNode = null;
  let draggedNode = null;
  let mouse = { x: 0, y: 0 };

  function getMousePos(evt) {
    const rect = canvas.getBoundingClientRect();
    return {
      x: evt.clientX - rect.left,
      y: evt.clientY - rect.top
    };
  }

  canvas.addEventListener('mousemove', evt => {
    mouse = getMousePos(evt);
    if (draggedNode) {
      draggedNode.x = mouse.x;
      draggedNode.y = mouse.y;
      draggedNode.vx = 0;
      draggedNode.vy = 0;
      return;
    }

    let found = null;
    for (let n of nodes) {
      if (Math.hypot(n.x - mouse.x, n.y - mouse.y) < n.radius + 8) {
        found = n;
        break;
      }
    }
    hoveredNode = found;
    canvas.style.cursor = found ? 'pointer' : draggedNode ? 'grabbing' : 'grab';
  });

  canvas.addEventListener('mousedown', evt => {
    const pos = getMousePos(evt);
    for (let n of nodes) {
      if (Math.hypot(n.x - pos.x, n.y - pos.y) < n.radius + 8) {
        draggedNode = n;
        selectedNode = n;
        canvas.style.cursor = 'grabbing';

        const panel = document.getElementById('nodeDetail');
        const rc = getRiskColor(n.riskScore);
        const cn = edges.filter(e => e.from.id === n.id || e.to.id === n.id).map(e => e.from.id === n.id ? e.to : e.from);
        const ce = edges.filter(e => e.from.id === n.id || e.to.id === n.id);

        panel.style.display = 'block';
        panel.innerHTML = `
          <div style="display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap;" class="animate-in">
            <div>
              <h3 style="color:var(--text-primary);margin-bottom:6px;font-family:var(--font-mono);">${n.label}</h3>
              <span class="badge" style="background:${rc}20;color:${rc};border:1px solid ${rc}40;">${getRiskLabel(n.riskScore)} RISK — ${n.riskScore.toFixed(1)}</span>
            </div>
            <div style="margin-left:auto;display:flex;gap:2rem;">
              <div style="text-align:center;"><div style="font-size:1.5rem;font-weight:700;color:#00F5D4;">${cn.length}</div><div style="color:#8B95A8;font-size:.75rem;">Connections</div></div>
              <div style="text-align:center;"><div style="font-size:1.5rem;font-weight:700;color:#3B82F6;">${ce.length}</div><div style="color:#8B95A8;font-size:.75rem;">Transactions</div></div>
              <div style="text-align:center;"><div style="font-size:1.5rem;font-weight:700;color:${n.suspicious ? '#EF4444' : '#10B981'};">${n.suspicious ? 'YES' : 'NO'}</div><div style="color:#8B95A8;font-size:.75rem;">Suspicious</div></div>
            </div>
          </div>`;
        return;
      }
    }
  });

  canvas.addEventListener('mouseup', () => {
    draggedNode = null;
    canvas.style.cursor = hoveredNode ? 'pointer' : 'grab';
  });

  // Dynamic float and force calculations loop
  function frame() {
    if (!document.getElementById('networkCanvas')) {
      window.removeEventListener('resize', resize);
      return;
    }
    
    ctx.clearRect(0, 0, width, height);

    // Bouncing float boundaries
    nodes.forEach(n => {
      if (n !== draggedNode) {
        n.x += n.vx;
        n.y += n.vy;

        if (n.x < n.radius + 15 || n.x > width - n.radius - 15) n.vx *= -1;
        if (n.y < n.radius + 15 || n.y > height - n.radius - 15) n.vy *= -1;

        n.x = Math.max(n.radius + 15, Math.min(width - n.radius - 15, n.x));
        n.y = Math.max(n.radius + 15, Math.min(height - n.radius - 15, n.y));

        // Center gravity pulls nodes towards middle gently
        n.vx += (width / 2 - n.x) * 0.000015;
        n.vy += (height / 2 - n.y) * 0.000015;
      }
    });

    // Spring tension on edges
    edges.forEach(e => {
      const dx = e.to.x - e.from.x;
      const dy = e.to.y - e.from.y;
      const dist = Math.hypot(dx, dy);
      const target = 130;
      if (dist > 0) {
        const factor = (dist - target) * 0.00025;
        const fx = (dx / dist) * factor;
        const fy = (dy / dist) * factor;

        if (e.from !== draggedNode) { e.from.vx += fx; e.from.vy += fy; }
        if (e.to !== draggedNode) { e.to.vx -= fx; e.to.vy -= fy; }
      }
    });

    // Draw links
    edges.forEach(e => {
      const isRelated = hoveredNode === e.from || hoveredNode === e.to || selectedNode === e.from || selectedNode === e.to;
      ctx.beginPath();
      ctx.moveTo(e.from.x, e.from.y);
      ctx.lineTo(e.to.x, e.to.y);
      ctx.strokeStyle = isRelated ? 'rgba(0, 245, 212, 0.4)' : 'rgba(255, 255, 255, 0.05)';
      ctx.lineWidth = isRelated ? 1.5 : 0.6;
      ctx.stroke();

      // Render flowing money dots
      e.particles.forEach(p => {
        p.progress += p.speed;
        if (p.progress > 1) p.progress = 0;

        const px = e.from.x + (e.to.x - e.from.x) * p.progress;
        const py = e.from.y + (e.to.y - e.from.y) * p.progress;

        ctx.beginPath();
        ctx.arc(px, py, 2.0, 0, 2 * Math.PI);
        ctx.fillStyle = '#00F5D4';
        ctx.shadowColor = '#00F5D4';
        ctx.shadowBlur = 6;
        ctx.fill();
        ctx.shadowBlur = 0;
      });
    });

    // Draw active nodes
    nodes.forEach(n => {
      const isSelected = selectedNode === n;
      const isHovered = hoveredNode === n;

      if (n.suspicious || isHovered || isSelected) {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius + (isHovered || isSelected ? 8 : 4), 0, 2 * Math.PI);
        ctx.fillStyle = n.suspicious ? 'rgba(239, 68, 68, 0.12)' : 'rgba(0, 245, 212, 0.08)';
        ctx.shadowColor = n.color;
        ctx.shadowBlur = isHovered || isSelected ? 12 : 6;
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      ctx.beginPath();
      ctx.arc(n.x, n.y, n.radius, 0, 2 * Math.PI);
      ctx.fillStyle = n.color;
      ctx.lineWidth = isSelected ? 2.0 : 1.0;
      ctx.strokeStyle = isSelected ? '#FFFFFF' : 'rgba(255, 255, 255, 0.15)';
      ctx.fill();
      ctx.stroke();

      ctx.font = '500 10px Inter, sans-serif';
      ctx.fillStyle = isHovered || isSelected ? '#FFFFFF' : '#8B95A8';
      ctx.textAlign = 'center';
      ctx.fillText(n.label, n.x, n.y + n.radius + 12);
    });

    requestAnimationFrame(frame);
  }

  frame();

  // Periodically query new data in fallback mode to maintain live-updates
  window.liveNetworkInterval = setInterval(async () => {
    if (document.getElementById('networkCanvas')) {
      const currentData = await api('/graph-data');
      if (!currentData || !currentData.nodes) return;
      
      const newIds = new Set(currentData.nodes.map(n => n.id));
      
      // Filter out dead nodes
      nodes = nodes.filter(n => newIds.has(n.id));
      const existingIds = new Set(nodes.map(n => n.id));
      
      // Add new nodes
      currentData.nodes.forEach(n => {
        if (!existingIds.has(n.id)) {
          nodes.push({
            id: n.id,
            label: n.label || n.id,
            x: Math.random() * (width - 160) + 80,
            y: Math.random() * (height - 160) + 80,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            radius: Math.max(12, Math.min(22, (n.risk_score || 50) / 4.5)),
            riskScore: n.risk_score || 0,
            color: n.color || '#10B981',
            suspicious: n.suspicious || false
          });
        } else {
          // Update details on existing
          const nodeRef = nodes.find(nodeObj => nodeObj.id === n.id);
          if (nodeRef) {
            nodeRef.color = n.color;
            nodeRef.riskScore = n.risk_score;
            nodeRef.suspicious = n.suspicious;
          }
        }
      });
      
      // Update edges
      const freshMap = new Map(nodes.map(n => [n.id, n]));
      edges = currentData.edges.map(e => {
        const fromNode = freshMap.get(e.from);
        const toNode = freshMap.get(e.to);
        if (!fromNode || !toNode) return null;
        
        // Retain existing particles if edge exists, otherwise init new
        const existingEdge = edges.find(edge => edge.from.id === e.from && edge.to.id === e.to);
        if (existingEdge) return existingEdge;
        
        const newEdge = {
          from: fromNode,
          to: toNode,
          value: e.value || 1000,
          title: e.title || `₹${(e.value || 1000).toLocaleString()}`,
          particles: []
        };
        const count = Math.min(3, Math.max(1, Math.floor((e.value || 10000) / 30000)));
        for (let i = 0; i < count; i++) {
          newEdge.particles.push({
            progress: Math.random(),
            speed: 0.003 + Math.random() * 0.005
          });
        }
        return newEdge;
      }).filter(e => e !== null);
    } else {
      clearInterval(window.liveNetworkInterval);
      window.liveNetworkInterval = null;
    }
  }, 4000);
}

// ---------------------------------------------------------------------------
//  Fraud Detection
// ---------------------------------------------------------------------------

async function renderFraudDetection() {
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    ${pageHeader('Fraud Detection', 'Real-Time Suspicious Transaction Monitor')}
    <div class="card animate-in animate-delay-1" style="padding:0;overflow:auto;" id="txWrap">
      <p style="padding:2rem;color:#8B95A8;">Loading…</p></div>`;

  const data = await api('/transactions');
  const wrap = document.getElementById('txWrap');
  if (!data || !data.transactions) { wrap.innerHTML = errorCard(); initIcons(); return; }

  wrap.innerHTML = `<div class="table-container"><table class="data-table">
    <thead><tr><th>ID</th><th>Sender</th><th>Receiver</th><th>Amount</th><th>Risk</th><th>Status</th><th>Time</th></tr></thead>
    <tbody>${data.transactions.map(tx => {
      const rc = getRiskColor(tx.risk_score ?? 0);
      const sc = tx.status === 'FLAGGED' ? '#EF4444' : '#F59E0B';
      return `<tr>
        <td class="text-mono text-muted">${tx.id}</td><td class="text-mono">${tx.sender}</td><td class="text-mono">${tx.receiver}</td>
        <td style="font-weight:600;">${formatCurrency(tx.amount)}</td>
        <td><span class="badge" style="background:${rc}18;color:${rc};">${tx.risk_score}</span></td>
        <td><span class="badge" style="background:${sc}18;color:${sc};">${tx.status}</span></td>
        <td class="text-muted" style="font-size:.82rem;">${new Date(tx.timestamp).toLocaleString()}</td></tr>`;
    }).join('')}</tbody></table></div>`;
  initIcons();
}

// ---------------------------------------------------------------------------
//  Fraud Rings
// ---------------------------------------------------------------------------

async function renderFraudRings() {
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    ${pageHeader('Fraud Ring Detection', 'Organized Criminal Network Analysis')}
    <div id="ringsBox" class="animate-in"><p style="color:#8B95A8;">Loading…</p></div>`;

  const data = await api('/fraud-rings');
  const box = document.getElementById('ringsBox');
  if (!data || !data.rings) { box.innerHTML = errorCard(); initIcons(); return; }

  box.innerHTML = data.rings.map((r, i) => {
    const bc = r.risk_level === 'CRITICAL' ? '#EF4444' : '#F59E0B';
    return `<div class="card ring-card animate-in animate-delay-${(i%4)+1}" style="border-left:4px solid ${bc};margin-bottom:1rem;">
      <div class="ring-header">
        <div>
          <h4 style="color:var(--text-primary);margin-bottom:6px;">Ring #${r.ring_id}</h4>
          <span class="badge" style="background:${bc}20;color:${bc};">${r.risk_level}</span>
          <span style="margin-left:8px;color:var(--text-secondary);font-size:.82rem;">Pattern: <strong style="color:var(--text-primary);">${r.pattern}</strong></span>
        </div>
        <div style="text-align:right;">
          <div style="color:var(--text-muted);font-size:.75rem;">Total Amount</div>
          <div style="color:var(--text-primary);font-weight:700;font-size:1.1rem;">${formatCurrency(r.total_amount)}</div>
        </div>
      </div>
      <div class="ring-members" style="margin-top:12px;display:flex;flex-wrap:wrap;gap:8px;">
        ${r.members.map(m => `<span style="background:rgba(255,255,255,0.05);padding:4px 10px;border-radius:6px;font-family:var(--font-mono);font-size:.78rem;color:var(--text-secondary);">${m}</span>`).join('')}
      </div>
    </div>`;
  }).join('');
  initIcons();
}

// ---------------------------------------------------------------------------
//  GNN Intelligence
// ---------------------------------------------------------------------------

async function renderGNN() {
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    ${pageHeader('GNN Intelligence', 'Graph Neural Network Analysis')}
    <div class="card animate-in" style="padding:0;overflow:auto;" id="gnnWrap">
      <p style="padding:2rem;color:#8B95A8;">Loading…</p></div>`;

  const data = await api('/gnn-intelligence');
  const wrap = document.getElementById('gnnWrap');
  if (!data || !data.nodes) { wrap.innerHTML = errorCard(); initIcons(); return; }

  const bar = (v) => {
    const p = (v * 100).toFixed(1);
    const c = v > 0.8 ? '#EF4444' : v > 0.5 ? '#F59E0B' : '#10B981';
    return `<div style="display:flex;align-items:center;gap:8px;">
      <div class="progress-bar-container" style="flex:1;"><div class="progress-bar-fill ${v > 0.8 ? 'high' : v > 0.5 ? 'medium' : 'low'}" style="width:${p}%;"></div></div>
      <span style="font-size:.78rem;color:${c};min-width:2.5rem;text-align:right;">${v.toFixed(2)}</span></div>`;
  };

  wrap.innerHTML = `<div class="table-container"><table class="data-table">
    <thead><tr><th>Account</th><th>Embedding Risk</th><th>Cluster</th><th>Fraud Probability</th><th>Status</th></tr></thead>
    <tbody>${data.nodes.map(r => {
      const sc = r.suspicious ? '#EF4444' : '#10B981';
      return `<tr>
        <td class="text-mono">${r.account}</td>
        <td style="min-width:160px;">${bar(r.embedding_risk ?? 0)}</td>
        <td style="text-align:center;"><span style="background:rgba(139,92,246,0.15);color:#8B5CF6;padding:3px 10px;border-radius:12px;font-size:.8rem;">${r.cluster}</span></td>
        <td style="min-width:160px;">${bar(r.fraud_probability ?? 0)}</td>
        <td><span class="badge" style="background:${sc}18;color:${sc};">${r.suspicious ? 'SUSPICIOUS' : 'NORMAL'}</span></td></tr>`;
    }).join('')}</tbody></table></div>`;
  initIcons();
}

// ---------------------------------------------------------------------------
//  AI Investigation — runs all 4 agents
// ---------------------------------------------------------------------------

async function renderInvestigation() {
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    ${pageHeader('AI Investigation Center', 'Multi-Agent AML Intelligence Analysis')}
    <div class="card animate-in animate-delay-1" style="padding:1.5rem;">
      <label style="color:var(--text-secondary);font-size:.85rem;display:block;margin-bottom:8px;">Select Account to Investigate</label>
      <select id="caseSelect" style="width:100%;max-width:400px;padding:10px 14px;background:var(--bg-secondary);border:1px solid var(--border-glass);border-radius:8px;color:var(--text-primary);font-family:var(--font-sans);font-size:.9rem;outline:none;">
        <option value="">— Loading cases —</option>
      </select>
    </div>
    <div id="caseDetail" style="margin-top:1.5rem;"></div>`;

  const data = await api('/cases?limit=50');
  const sel = document.getElementById('caseSelect');
  if (!data || !data.cases) { sel.innerHTML = '<option>Unable to load</option>'; initIcons(); return; }

  sel.innerHTML = '<option value="">— Select an account —</option>' +
    data.cases.map(c => `<option value="${c.account}">${c.account} (Risk: ${(c.risk_score ?? 0).toFixed(1)})</option>`).join('');

  sel.addEventListener('change', async () => {
    const id = sel.value;
    const det = document.getElementById('caseDetail');
    if (!id) { det.innerHTML = ''; return; }

    det.innerHTML = '<div class="card" style="padding:2rem;text-align:center;"><div class="skeleton" style="height:24px;width:200px;margin:0 auto 1rem;"></div><p style="color:#8B95A8;">Running AI agents on ' + id + '…</p></div>';

    const result = await api(`/investigate/${id}`);
    if (!result || result.error) { det.innerHTML = errorCard(result?.error || 'Investigation failed'); initIcons(); return; }

    const risk = result.risk_score ?? 0;
    const rc = getRiskColor(risk);
    const circ = 2 * Math.PI * 54;
    const off = circ - (risk / 100) * circ;
    const sus = result.suspicious;
    const agents = result.agents || {};

    const agentCard = (title, icon, content, color) => `
      <div class="card animate-in" style="padding:1.25rem;border-left:3px solid ${color};">
        <h4 style="color:${color};font-size:.9rem;margin-bottom:10px;">${icon} ${title}</h4>
        <pre style="color:var(--text-secondary);font-size:.84rem;line-height:1.6;white-space:pre-wrap;font-family:var(--font-sans);margin:0;">${content}</pre>
      </div>`;

    det.innerHTML = `
      <div class="animate-in" style="display:grid;grid-template-columns:240px 1fr;gap:1.5rem;">
        <!-- Risk Gauge -->
        <div class="card" style="padding:1.5rem;display:flex;flex-direction:column;align-items:center;justify-content:center;">
          <svg width="140" height="140" viewBox="0 0 140 140" style="margin-bottom:1rem;">
            <circle cx="70" cy="70" r="54" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="12"/>
            <circle cx="70" cy="70" r="54" fill="none" stroke="${rc}" stroke-width="12"
              stroke-dasharray="${circ}" stroke-dashoffset="${off}"
              stroke-linecap="round" transform="rotate(-90 70 70)" style="transition:stroke-dashoffset .8s ease;"/>
            <text x="70" y="70" text-anchor="middle" dominant-baseline="central"
              fill="${rc}" font-size="28" font-weight="800" font-family="var(--font-mono)">${risk.toFixed(1)}</text>
          </svg>
          <div style="color:var(--text-secondary);font-size:.85rem;">Risk Score</div>
          <span class="badge ${sus ? 'badge-flagged' : 'badge-safe'}" style="margin-top:8px;">${sus ? '🚨 SUSPICIOUS' : '✅ NORMAL'}</span>
          <div style="margin-top:16px;text-align:center;">
            <div style="color:var(--text-muted);font-size:.72rem;">Fraud Rings</div>
            <div style="color:#8B5CF6;font-size:1.3rem;font-weight:700;">${result.fraud_ring_count ?? 0}</div>
          </div>
        </div>

        <!-- AI Agent Results -->
        <div style="display:grid;gap:1rem;">
          ${agentCard('Risk Analysis Agent', '🔴', agents.risk_analysis || 'No data', '#EF4444')}
          ${agentCard('Explanation Agent', '🧠', agents.explanation || 'No data', '#3B82F6')}
          ${agentCard('Investigation Agent', '🕵️', agents.investigation || 'No data', '#F59E0B')}
          ${agentCard('Compliance Agent', '📋', agents.compliance || 'No data', '#8B5CF6')}
        </div>
      </div>

      <!-- Explanations -->
      <div class="card animate-in" style="padding:1.5rem;margin-top:1.5rem;">
        <h4 style="color:var(--text-primary);margin-bottom:10px;">Raw AI Explanations</h4>
        <ul class="explanation-list">
          ${(result.explanations || []).map(e => `<li>${e}</li>`).join('')}
        </ul>
      </div>`;

    initIcons();
  });
  initIcons();
}

// ---------------------------------------------------------------------------
//  Explainable AI
// ---------------------------------------------------------------------------

async function renderXAI() {
  const main = document.getElementById('mainContent');
  const features = [
    { name: 'Transaction Amount',      importance: 0.91, desc: 'Measures monetary value. Unusually large transactions are strong fraud indicators.' },
    { name: 'Degree Centrality',       importance: 0.84, desc: 'Counts direct connections. Highly connected nodes may indicate shell networks.' },
    { name: 'PageRank',                importance: 0.72, desc: 'Evaluates account importance within the transaction graph.' },
    { name: 'Transaction Frequency',   importance: 0.69, desc: 'Tracks how often an account transacts. Rapid bursts signal structuring.' },
    { name: 'Connected Risk Accounts', importance: 0.63, desc: 'Counts linked high-risk accounts — guilt by association metric.' },
  ];

  main.innerHTML = `
    ${pageHeader('Explainable AI', 'SHAP Feature Importance Analysis')}
    <div class="card animate-in animate-delay-1 chart-container"><canvas id="xaiChart" height="200"></canvas></div>
    <div class="feature-cards">
      ${features.map((f, i) => `
        <div class="card feature-card-item animate-in animate-delay-${(i%4)+2}">
          <h4>${f.name}</h4><p>${f.desc}</p>
          <div style="margin-top:10px;display:flex;align-items:center;gap:8px;">
            <div style="flex:1;height:6px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden;">
              <div style="width:${f.importance*100}%;height:100%;background:linear-gradient(90deg,#00F5D4,#3B82F6);border-radius:3px;"></div>
            </div>
            <span style="color:var(--text-primary);font-size:.8rem;font-weight:600;">${f.importance}</span>
          </div>
        </div>`).join('')}
    </div>`;

  const ctx = document.getElementById('xaiChart').getContext('2d');
  const g = ctx.createLinearGradient(0, 0, ctx.canvas.width, 0);
  g.addColorStop(0, '#00F5D4');  g.addColorStop(1, '#3B82F6');
  createChart('xaiChart', {
    type: 'bar',
    data: { labels: features.map(f => f.name), datasets: [{ label: 'Importance', data: features.map(f => f.importance), backgroundColor: g, borderRadius: 6, maxBarThickness: 36 }] },
    options: { indexAxis: 'y', responsive: true, plugins: { legend: { display: false } },
      scales: { x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#8B95A8' }, max: 1 }, y: { grid: { display: false }, ticks: { color: '#E2E8F0', font: { size: 13 } } } },
    },
  });
  initIcons();
}

// ---------------------------------------------------------------------------
//  Init
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
  initIcons();
  document.querySelectorAll('.nav-item').forEach(l => {
    l.addEventListener('click', e => { e.preventDefault(); if (l.dataset.page) navigate(l.dataset.page); });
  });
  navigate('overview');
});
