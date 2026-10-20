'use strict';

const { api, showToast, loadPrefs, savePrefs, applyDisplayPrefs } = window.EchoAid;

// ── State ────────────────────────────────────────────────────────────

let _categories   = [];
let _keywords     = [];
let _urgent       = [];
let _selectedMsg  = '';
let _lastMsg      = '';
let _currentCat   = 'all';
let _prefs        = loadPrefs();
let _aiAvailable  = false;
let _utterance    = null;

// ── Init ─────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
  applyDisplayPrefs();
  window.EchoAid.checkHealth();
  initPreferences();
  await loadData();
  initSpeechButtons();
  initPreferencesPanel();
  checkAiStatus();
});

// ── Data loading ──────────────────────────────────────────────────────

async function loadData() {
  try {
    announce('Loading keywords…');
    [_categories, _keywords, _urgent] = await Promise.all([
      api.get('/api/categories/'),
      api.get('/api/keywords/'),
      api.get('/api/keywords/urgent'),
    ]);
    renderCategoryTabs();
    renderKeywords();
    announce('Keywords loaded.');
  } catch (err) {
    document.getElementById('keyword-area').innerHTML =
      `<div class="empty-state">
        <div class="empty-state__icon" aria-hidden="true">⚠️</div>
        <h3 class="empty-state__title">Could not load keywords</h3>
        <p class="empty-state__body">${escHtml(err.message)}</p>
        <button class="btn btn-primary mt-4" onclick="location.reload()">Retry</button>
      </div>`;
  }
}

// ── Category tabs ─────────────────────────────────────────────────────

function renderCategoryTabs() {
  const tabsEl = document.getElementById('category-tabs');
  if (!tabsEl) return;

  const cats = [
    { id: 'all',    name: 'All',    icon: '' },
    { id: 'urgent', name: 'Urgent', icon: '🚨' },
    ..._categories,
  ];

  tabsEl.innerHTML = cats.map(c => `
    <button class="pill-tab${c.id === _currentCat ? ' active' : ''}"
            role="tab"
            aria-selected="${c.id === _currentCat}"
            data-cat="${c.id}">
      ${c.icon ? `<span aria-hidden="true">${escHtml(c.icon)}</span>` : ''}
      ${escHtml(c.name)}
    </button>`).join('');

  tabsEl.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-cat]');
    if (!btn) return;
    _currentCat = btn.dataset.cat;
    tabsEl.querySelectorAll('.pill-tab').forEach(b => {
      const active = b.dataset.cat === _currentCat;
      b.classList.toggle('active', active);
      b.setAttribute('aria-selected', String(active));
    });
    renderKeywords();
  });
}

// ── Keyword grid ──────────────────────────────────────────────────────

function renderKeywords() {
  const area = document.getElementById('keyword-area');
  if (!area) return;

  let visible = [];

  if (_currentCat === 'all') {
    visible = _keywords;
  } else if (_currentCat === 'urgent') {
    visible = _urgent;
  } else {
    const catId = +_currentCat;
    visible = _keywords.filter(kw => kw.category_id === catId);
  }

  if (visible.length === 0) {
    area.innerHTML = `<div class="empty-state">
      <div class="empty-state__icon" aria-hidden="true">🗂️</div>
      <h3 class="empty-state__title">No keywords here</h3>
      <p class="empty-state__body">Ask your guardian to add keywords for this category.</p>
    </div>`;
    return;
  }

  area.innerHTML = `<div class="keyword-grid" id="kw-grid" role="list"></div>`;
  const grid = document.getElementById('kw-grid');

  visible.forEach(kw => {
    const card = document.createElement('button');
    card.className = `keyword-card${kw.is_urgent ? ' keyword-card--urgent' : ''}`;
    card.setAttribute('role', 'listitem');
    card.setAttribute('aria-label',
      `${kw.label}: ${kw.message}${kw.is_urgent ? ' (Urgent)' : ''}`);
    card.setAttribute('tabindex', '0');

    if (kw.icon) {
      const iconSpan = document.createElement('span');
      iconSpan.className = 'keyword-card__icon';
      iconSpan.textContent = kw.icon;
      iconSpan.setAttribute('aria-hidden', 'true');
      card.appendChild(iconSpan);
    }

    const labelSpan = document.createElement('span');
    labelSpan.className = 'keyword-card__label';
    labelSpan.textContent = kw.label;
    card.appendChild(labelSpan);

    card.addEventListener('click', () => selectKeyword(kw));
    grid.appendChild(card);
  });
}

function selectKeyword(kw) {
  _selectedMsg = kw.message;
  const display = document.getElementById('speech-display');
  if (display) {
    display.textContent = kw.message;
    display.classList.remove('speech-display--empty');
  }
  updateSpeechButtons(true);
  announce(`Selected: ${kw.label}`);

  if (_prefs.speakOnSelect) {
    speakMessage(kw.message);
  }
}

// ── TTS controls ──────────────────────────────────────────────────────

function initSpeechButtons() {
  const btnSpeak  = document.getElementById('btn-speak');
  const btnStop   = document.getElementById('btn-stop');
  const btnRepeat = document.getElementById('btn-repeat');

  if (!('speechSynthesis' in window)) {
    const panel = document.getElementById('speech-panel');
    if (panel) {
      const notice = document.createElement('div');
      notice.className = 'alert alert-warning';
      notice.setAttribute('role', 'note');
      notice.textContent =
        'Text-to-speech is not available in this browser. ' +
        'Please use a modern browser such as Chrome, Edge, or Safari.';
      panel.prepend(notice);
    }
    if (btnSpeak) btnSpeak.disabled = true;
    return;
  }

  if (btnSpeak)  btnSpeak.addEventListener('click',  () => speakMessage(_selectedMsg));
  if (btnStop)   btnStop.addEventListener('click',   stopSpeaking);
  if (btnRepeat) btnRepeat.addEventListener('click', () => speakMessage(_lastMsg));
}

function speakMessage(text) {
  if (!text || !('speechSynthesis' in window)) return;
  stopSpeaking();

  _lastMsg = text;
  _utterance = new SpeechSynthesisUtterance(text);
  _utterance.rate  = _prefs.speechRate  ?? 1.0;
  _utterance.pitch = _prefs.speechPitch ?? 1.0;

  // Try to match preferred voice
  if (_prefs.preferredVoice) {
    const voices = speechSynthesis.getVoices();
    const match = voices.find(v => v.name === _prefs.preferredVoice);
    if (match) _utterance.voice = match;
  }

  _utterance.onstart = () => {
    updateSpeechButtons(true, true);
    announce('Speaking…');
  };
  _utterance.onend = _utterance.onerror = () => {
    updateSpeechButtons(!!_selectedMsg, false);
    announce('Done speaking.');
  };

  speechSynthesis.speak(_utterance);
}

function stopSpeaking() {
  if ('speechSynthesis' in window) {
    speechSynthesis.cancel();
  }
  updateSpeechButtons(!!_selectedMsg, false);
}

function updateSpeechButtons(hasMessage, isSpeaking = false) {
  const btnSpeak  = document.getElementById('btn-speak');
  const btnStop   = document.getElementById('btn-stop');
  const btnRepeat = document.getElementById('btn-repeat');

  if (btnSpeak)  btnSpeak.disabled  = !hasMessage || isSpeaking;
  if (btnStop)   btnStop.disabled   = !isSpeaking;
  if (btnRepeat) btnRepeat.disabled = !_lastMsg;
}

// ── Preferences panel ─────────────────────────────────────────────────

function initPreferences() {
  _prefs = loadPrefs();
  applyDisplayPrefs();
}

function initPreferencesPanel() {
  const toggleBtn = document.getElementById('btn-prefs-toggle');
  const panel     = document.getElementById('prefs-panel');
  if (!toggleBtn || !panel) return;

  toggleBtn.addEventListener('click', () => {
    const expanded = toggleBtn.getAttribute('aria-expanded') === 'true';
    toggleBtn.setAttribute('aria-expanded', String(!expanded));
    panel.classList.toggle('hidden', expanded);
  });

  // High contrast
  const hcToggle = document.getElementById('pref-high-contrast');
  if (hcToggle) {
    hcToggle.checked = _prefs.highContrast;
    hcToggle.addEventListener('change', () => {
      _prefs.highContrast = hcToggle.checked;
      savePrefs({ highContrast: hcToggle.checked });
      applyDisplayPrefs();
    });
  }

  // Large text
  const ltToggle = document.getElementById('pref-large-text');
  if (ltToggle) {
    ltToggle.checked = _prefs.largeText;
    ltToggle.addEventListener('change', () => {
      _prefs.largeText = ltToggle.checked;
      savePrefs({ largeText: ltToggle.checked });
      applyDisplayPrefs();
    });
  }

  // Speak on select
  const sosToggle = document.getElementById('pref-speak-on-select');
  if (sosToggle) {
    sosToggle.checked = _prefs.speakOnSelect;
    sosToggle.addEventListener('change', () => {
      _prefs.speakOnSelect = sosToggle.checked;
      savePrefs({ speakOnSelect: sosToggle.checked });
    });
  }

  // Speech rate
  const rateInput = document.getElementById('pref-rate');
  const rateLabel = document.getElementById('pref-rate-val');
  if (rateInput) {
    rateInput.value = _prefs.speechRate ?? 1.0;
    if (rateLabel) rateLabel.textContent = rateInput.value + 'x';
    rateInput.addEventListener('input', () => {
      _prefs.speechRate = +rateInput.value;
      savePrefs({ speechRate: +rateInput.value });
      if (rateLabel) rateLabel.textContent = rateInput.value + 'x';
    });
  }

  // Voice selector
  const voiceSel = document.getElementById('pref-voice');
  if (voiceSel && 'speechSynthesis' in window) {
    const populateVoices = () => {
      const voices = speechSynthesis.getVoices();
      voiceSel.innerHTML = '<option value="">Default voice</option>' +
        voices.map(v =>
          `<option value="${escHtml(v.name)}"${v.name === _prefs.preferredVoice ? ' selected' : ''}>
             ${escHtml(v.name)} (${v.lang})
           </option>`).join('');
    };
    populateVoices();
    speechSynthesis.onvoiceschanged = populateVoices;
    voiceSel.addEventListener('change', () => {
      _prefs.preferredVoice = voiceSel.value;
      savePrefs({ preferredVoice: voiceSel.value });
    });
  }
}

// ── Phase 4: AI Type & Speak ──────────────────────────────────────────

async function checkAiStatus() {
  const section = document.getElementById('ai-section');
  try {
    const status = await api.get('/api/ai/status');
    _aiAvailable = status.configured;
    if (section) {
      if (!status.configured) {
        section.querySelector('#ai-unavailable')?.classList.remove('hidden');
        section.querySelector('#ai-form-area')?.classList.add('hidden');
      }
    }
  } catch (_) {
    _aiAvailable = false;
    if (section) {
      section.querySelector('#ai-unavailable')?.classList.remove('hidden');
      section.querySelector('#ai-form-area')?.classList.add('hidden');
    }
  }
  initAiForm();
}

function initAiForm() {
  const form = document.getElementById('ai-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('ai-input');
    const fragments = input?.value.trim();
    if (!fragments) return;

    const resultsEl = document.getElementById('ai-results');
    resultsEl.innerHTML = `<div class="flex items-center gap-3 text-secondary">
      <div class="spinner"></div> Generating suggestions…
    </div>`;

    const btn = form.querySelector('[type="submit"]');
    btn.disabled = true;

    try {
      const data = await api.post('/api/ai/suggest', { fragments });
      renderAiSuggestions(data.suggestions, fragments);
    } catch (err) {
      resultsEl.innerHTML =
        `<div class="alert alert-error" role="alert">
          <span aria-hidden="true">⚠️</span>
          <span>${escHtml(err.message)}<br/>
          <small>Your saved keywords are still available.</small></span>
        </div>`;
    } finally {
      btn.disabled = false;
    }
  });
}

function renderAiSuggestions(suggestions, originalInput) {
  const resultsEl = document.getElementById('ai-results');
  if (!resultsEl) return;

  resultsEl.innerHTML = `
    <p class="text-xs text-secondary mb-3" aria-live="polite">
      ${suggestions.length} suggestion${suggestions.length !== 1 ? 's' : ''} for:
      <em>${escHtml(originalInput)}</em>
    </p>
    <div class="grid" style="gap:var(--space-3);" id="ai-suggestion-list">
      ${suggestions.map((s, i) => `
        <div class="card card-padded" style="gap:var(--space-3);">
          <textarea class="ai-suggestion-text"
                    id="ai-sug-${i}"
                    rows="2"
                    aria-label="Suggestion ${i + 1}, editable"
                    style="width:100%;font-size:var(--font-size-base);
                           border:none;resize:vertical;background:transparent;
                           font-family:var(--font-family);outline:none;"
          >${escHtml(s)}</textarea>
          <div class="flex gap-2 justify-end">
            <button class="btn btn-sm btn-ghost"
                    onclick="selectAiSuggestion(${i})"
                    aria-label="Use suggestion ${i + 1}">
              📋 Use this
            </button>
            <button class="btn btn-sm btn-primary"
                    onclick="speakAiSuggestion(${i})"
                    aria-label="Speak suggestion ${i + 1}">
              🔊 Speak
            </button>
          </div>
        </div>`).join('')}
    </div>`;
}

// Called from inline event handlers — available on window
window.selectAiSuggestion = function(i) {
  const text = document.getElementById(`ai-sug-${i}`)?.value;
  if (!text) return;
  _selectedMsg = text;
  const display = document.getElementById('speech-display');
  if (display) {
    display.textContent = text;
    display.classList.remove('speech-display--empty');
  }
  updateSpeechButtons(true);
  announce(`AI suggestion selected.`);
  // Scroll to speech panel
  document.getElementById('speech-panel')?.scrollIntoView({ behavior: 'smooth' });
};

window.speakAiSuggestion = function(i) {
  const text = document.getElementById(`ai-sug-${i}`)?.value;
  if (!text) return;
  // Require explicit click — never auto-speaks
  speakMessage(text);
};

// ── Accessibility ─────────────────────────────────────────────────────

function announce(msg) {
  const el = document.getElementById('sr-announcer');
  if (el) {
    el.textContent = '';
    // brief delay ensures screen readers re-announce identical strings
    setTimeout(() => { el.textContent = msg; }, 50);
  }
}

// ── Utility ───────────────────────────────────────────────────────────

function escHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
