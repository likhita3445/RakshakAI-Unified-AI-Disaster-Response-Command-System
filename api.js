/* ==========================================================================
   RAKSHAKAI — FRONTEND API SERVICE LAYER
   Connects frontend to Flask REST backend at http://127.0.0.1:5000
   All functions fall back to local JS if backend is unreachable.
   ========================================================================== */

const API_BASE = 'http://127.0.0.1:5000';

/* --- Internal fetch helper with 5s timeout --- */
async function _apiFetch(url, options = {}) {
  const controller = new AbortController();
  const tid = setTimeout(() => controller.abort(), 5000);
  try {
    const res = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }
    });
    clearTimeout(tid);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const json = await res.json();
    if (!json.success) throw new Error(json.message || 'API error');
    return json.data;
  } catch (err) {
    clearTimeout(tid);
    throw err;
  }
}

const RakshakAPI = {
  _connected: false,

  /** GET /api/health */
  async health() {
    try {
      const controller = new AbortController();
      const tid = setTimeout(() => controller.abort(), 2000);
      const res = await fetch(API_BASE + '/api/health', { signal: controller.signal });
      clearTimeout(tid);
      const json = await res.json();
      this._connected = json.status === 'HEALTHY';
    } catch { this._connected = false; }
    return this._connected;
  },

  /** POST /api/analysis/nlp */
  async parseNLP(text, lang = 'hi') {
    return _apiFetch(API_BASE + '/api/analysis/nlp', {
      method: 'POST', body: JSON.stringify({ text, lang })
    });
  },

  /** POST /api/analysis/priority */
  async calcPriority(areaData) {
    return _apiFetch(API_BASE + '/api/analysis/priority', {
      method: 'POST', body: JSON.stringify(areaData)
    });
  },

  /** POST /api/analysis/simulate */
  async simulate(params) {
    return _apiFetch(API_BASE + '/api/analysis/simulate', {
      method: 'POST', body: JSON.stringify(params)
    });
  },

  /** POST /api/analysis/satellite */
  async getSatellite() {
    return _apiFetch(API_BASE + '/api/analysis/satellite', { method: 'POST', body: '{}' });
  },

  /** GET /api/analysis/predict */
  async getForecast() {
    return _apiFetch(API_BASE + '/api/analysis/predict');
  },

  /** POST /api/fix/action-plan */
  async getActionPlan(areaName) {
    return _apiFetch(API_BASE + '/api/fix/action-plan', {
      method: 'POST', body: JSON.stringify({ area_name: areaName || 'Area A — Yamuna Sector 9' })
    });
  },

  /** POST /api/fix/reroute */
  async reroute(origin, destination) {
    return _apiFetch(API_BASE + '/api/fix/reroute', {
      method: 'POST', body: JSON.stringify({ origin: origin || 'Command Base', destination: destination || 'Area A' })
    });
  },

  /** POST /api/fix/allocate */
  async allocate(areas, inventory) {
    return _apiFetch(API_BASE + '/api/fix/allocate', {
      method: 'POST', body: JSON.stringify({ areas: areas || [], inventory: inventory || {} })
    });
  },

  /** GET /api/security/explain/:areaId */
  async explainDecision(areaId) {
    return _apiFetch(API_BASE + '/api/security/explain/' + areaId);
  },

  /** POST /api/security/dispatch */
  async dispatchAgency(agency, targetArea, task) {
    return _apiFetch(API_BASE + '/api/security/dispatch', {
      method: 'POST', body: JSON.stringify({ agency, target_area: targetArea, task })
    });
  },

  /** POST /api/security/sync-offline */
  async syncOffline(reports) {
    return _apiFetch(API_BASE + '/api/security/sync-offline', {
      method: 'POST', body: JSON.stringify({ reports: reports || [] })
    });
  },

  /** GET /api/test/judge-demo/:stepId */
  async getJudgeStep(stepId) {
    return _apiFetch(API_BASE + '/api/test/judge-demo/' + stepId);
  },

  /** GET /api/shelters/nearest */
  async getNearestHospitals(lat = 28.6139, lng = 77.2090, type = 'ALL', radius = 30) {
    return _apiFetch(`${API_BASE}/api/shelters/nearest?lat=${lat}&lng=${lng}&type=${type}&radius=${radius}`);
  },

  /** POST /api/shelters/check-in */
  async checkInFamily(payload) {
    return _apiFetch(API_BASE + '/api/shelters/check-in', {
      method: 'POST', body: JSON.stringify(payload)
    });
  },

  /** POST /api/shelters/sos/broadcast */
  async broadcastSOS(payload) {
    return _apiFetch(API_BASE + '/api/shelters/sos/broadcast', {
      method: 'POST', body: JSON.stringify(payload)
    });
  }
};

/* --- Backend health badge updater --- */
async function checkAndDisplayBackendStatus() {
  const badge = document.getElementById('backend-status-badge');
  const isOnline = await RakshakAPI.health();
  if (badge) {
    if (isOnline) {
      badge.innerHTML = '<span class="live-dot" style="background:#10b981;"></span> BACKEND ONLINE';
      badge.style.cssText += ';background:rgba(16,185,129,0.15);border-color:rgba(16,185,129,0.4);color:var(--accent-low);';
    } else {
      badge.innerHTML = '<span class="live-dot" style="background:#ff8800;"></span> OFFLINE MODE';
      badge.style.cssText += ';background:rgba(255,136,0,0.15);border-color:rgba(255,136,0,0.4);color:var(--accent-high);';
    }
  }
  return isOnline;
}

document.addEventListener('DOMContentLoaded', () => setTimeout(checkAndDisplayBackendStatus, 1000));

window.RakshakAPI = RakshakAPI;
window.checkAndDisplayBackendStatus = checkAndDisplayBackendStatus;