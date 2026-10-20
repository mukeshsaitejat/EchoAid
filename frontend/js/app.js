(function() {
'use strict';

/* ────────────────────────────────────────────────────────────────────
   API HELPERS
   ──────────────────────────────────────────────────────────────────── */

/**
 * Thin wrapper around fetch() that always targets the same origin.
 *
 * @param {string} path       - API path, e.g. "/api/health"
 * @param {RequestInit} [options] - Standard fetch options
 * @returns {Promise<any>}    - Parsed JSON response body
 * @throws {Error}            - On network failure or non-2xx status
 */
async function apiRequest(path, options = {}) {
  const url = path.startsWith('/') ? path : `/${path}`;
  const defaultHeaders = { 'Content-Type': 'application/json' };

  const response = await fetch(url, {
    ...options,
    headers: { ...defaultHeaders, ...(options.headers || {}) },
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status} ${response.statusText}`;
    try {
      const body = await response.json();
      if (body && body.detail) {
        message = typeof body.detail === 'string'
          ? body.detail
          : JSON.stringify(body.detail);
      }
    } catch (_) { /* ignore parse errors */ }
    throw new Error(message);
  }

  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return response.json();
  }
  return null;
}

/** API helpers object (created inline to avoid global scope pollution) */

/* ────────────────────────────────────────────────────────────────────
   TOAST NOTIFICATIONS
   ──────────────────────────────────────────────────────────────────── */

let _toastContainer = null;

function _getToastContainer() {
  if (!_toastContainer) {
    _toastContainer = document.createElement('div');
    _toastContainer.className = 'toast-container';
    _toastContainer.setAttribute('aria-live', 'polite');
    _toastContainer.setAttribute('aria-atomic', 'false');
    document.body.appendChild(_toastContainer);
  }
  return _toastContainer;
}

/**
 * Display a toast notification.
 *
 * @param {string} message          - Text to display
 * @param {'info'|'success'|'error'} [type='info'] - Visual variant
 * @param {number} [duration=4000]  - Auto-dismiss delay in ms (0 = persistent)
 */
function showToast(message, type = 'info', duration = 4000) {
  const container = _getToastContainer();

  const icons = { info: '💬', success: '✓', error: '✗' };

  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.setAttribute('role', 'status');

  // Use textContent for the icon to avoid any XSS risk
  const iconSpan = document.createElement('span');
  iconSpan.textContent = icons[type] || icons.info;
  iconSpan.setAttribute('aria-hidden', 'true');

  const msgSpan = document.createElement('span');
  msgSpan.textContent = message;   // always textContent, never innerHTML

  toast.appendChild(iconSpan);
  toast.appendChild(msgSpan);
  container.appendChild(toast);

  if (duration > 0) {
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 300ms ease';
      setTimeout(() => toast.remove(), 320);
    }, duration);
  }
}

/* ────────────────────────────────────────────────────────────────────
   HEALTH CHECK
   ──────────────────────────────────────────────────────────────────── */

/**
 * Checks /api/health and updates a status indicator element if present.
 *
 * @param {string} [indicatorId='health-indicator'] - ID of the element to update
 */
async function checkHealth(indicatorId = 'health-indicator') {
  const indicator = document.getElementById(indicatorId);
  try {
    const data = await api.get('/api/health');
    if (indicator) {
      const dot = indicator.querySelector('.status-dot');
      const label = indicator.querySelector('.status-label');
      if (dot) {
        dot.className = 'status-dot status-dot--ok';
      }
      if (label) {
        label.textContent = `v${data.version} · ${data.environment}`;
      }
    }
    return data;
  } catch (err) {
    if (indicator) {
      const dot = indicator.querySelector('.status-dot');
      const label = indicator.querySelector('.status-label');
      if (dot) dot.className = 'status-dot status-dot--error';
      if (label) label.textContent = 'offline';
    }
    console.warn('[EchoAid] Health check failed:', err.message);
    return null;
  }
}

/* ────────────────────────────────────────────────────────────────────
   PREFERENCES (localStorage)
   ──────────────────────────────────────────────────────────────────── */

const PREFS_KEY = 'echoaid_prefs';

const DEFAULT_PREFS = {
  highContrast: false,
  largeText: false,
  speakOnSelect: false,
  speechRate: 1.0,    // Web Speech API rate (0.1–10)
  speechPitch: 1.0,   // Web Speech API pitch (0–2)
  preferredVoice: '',
};

/**
 * Load persisted user preferences from localStorage.
 * @returns {object} Merged preferences object
 */
function loadPrefs() {
  try {
    const raw = localStorage.getItem(PREFS_KEY);
    return raw ? { ...DEFAULT_PREFS, ...JSON.parse(raw) } : { ...DEFAULT_PREFS };
  } catch (_) {
    return { ...DEFAULT_PREFS };
  }
}

/**
 * Save user preferences to localStorage.
 * @param {object} prefs - Partial or full preferences object to merge and save
 */
function savePrefs(prefs) {
  try {
    const current = loadPrefs();
    localStorage.setItem(PREFS_KEY, JSON.stringify({ ...current, ...prefs }));
  } catch (err) {
    console.warn('[EchoAid] Could not save preferences:', err.message);
  }
}

/**
 * Apply display preferences (high-contrast, large-text) to the document root.
 */
function applyDisplayPrefs() {
  const prefs = loadPrefs();
  const root = document.documentElement;
  root.setAttribute('data-high-contrast', String(prefs.highContrast));
  root.setAttribute('data-large-text',    String(prefs.largeText));
}

/* ────────────────────────────────────────────────────────────────────
   DOM HELPERS
   ──────────────────────────────────────────────────────────────────── */

/**
 * Safe text setter — always uses textContent to avoid XSS.
 * @param {Element} el
 * @param {string} text
 */
function setText(el, text) {
  if (el) el.textContent = text;
}

/**
 * Toggle a CSS class based on a boolean condition.
 */
function toggleClass(el, className, force) {
  if (el) el.classList.toggle(className, force);
}

/**
 * Create a DOM element with optional properties.
 * @param {string} tag
 * @param {object} [props] - className, textContent, attributes, etc.
 * @returns {Element}
 */
function createElement(tag, props = {}) {
  const el = document.createElement(tag);
  const { className, textContent, attributes = {}, ...rest } = props;
  if (className) el.className = className;
  if (textContent !== undefined) el.textContent = textContent;
  for (const [attr, val] of Object.entries(attributes)) {
    el.setAttribute(attr, val);
  }
  return el;
}

/* ────────────────────────────────────────────────────────────────────
   EXPORTS (module-compatible and global)
   ──────────────────────────────────────────────────────────────────── */

// Attach to window so non-module scripts can use these utilities.
window.EchoAid = window.EchoAid || {};
Object.assign(window.EchoAid, {
  // Create API object inline to avoid global scope pollution
  api: {
    get:    (path)         => apiRequest(path, { method: 'GET' }),
    post:   (path, body)   => apiRequest(path, { method: 'POST',   body: JSON.stringify(body) }),
    put:    (path, body)   => apiRequest(path, { method: 'PUT',    body: JSON.stringify(body) }),
    patch:  (path, body)   => apiRequest(path, { method: 'PATCH',  body: JSON.stringify(body) }),
    delete: (path)         => apiRequest(path, { method: 'DELETE' }),
  },
  showToast,
  checkHealth,
  loadPrefs,
  savePrefs,
  applyDisplayPrefs,
  setText,
  toggleClass,
  createElement,
});

// Apply display preferences immediately to avoid a flash of unstyled content.
applyDisplayPrefs();

})(); // End of IIFE
