'use strict';

const { api, showToast, checkHealth, applyDisplayPrefs } = window.EchoAid;

// ── State ────────────────────────────────────────────────────────────

let _categories = [];
let _keywords   = [];
let _editingKeyword   = null;  // keyword object being edited (null = create mode)
let _editingCategory  = null;

// ── Init ─────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
  applyDisplayPrefs();
  checkHealth();
  await checkAuthAndRender();
});

async function checkAuthAndRender() {
  try {
    await api.get('/api/auth/check');
    // If we get here, we're authenticated
    renderDashboard();
    loadDashboardData();
  } catch (_) {
    renderPinScreen();
  }
}

// ── PIN screen ───────────────────────────────────────────────────────

function renderPinScreen() {
  document.getElementById('guardian-app').innerHTML = `
    <div class="pin-screen container container-sm">
      <div aria-hidden="true" style="font-size:3rem;">⚙️</div>
      <div class="text-center">
        <h1 class="text-2xl mb-2">Guardian Mode</h1>
        <p class="text-secondary">Enter your PIN to manage keywords and preferences.</p>
      </div>
      <form id="pin-form" autocomplete="off" novalidate style="width:100%;max-width:320px;">
        <div class="form-group">
          <label for="pin-field" class="form-label text-center">Guardian PIN</label>
          <input type="password" id="pin-field" inputmode="numeric"
                 pattern="[0-9]*" maxlength="8" autocomplete="current-password"
                 placeholder="Enter PIN"
                 style="text-align:center;font-size:var(--font-size-2xl);letter-spacing:0.4em;" />
          <p class="form-hint text-center">Default PIN is set in your <code>.env</code> file.</p>
        </div>
        <div id="pin-error" class="form-error justify-center mt-2 hidden" role="alert" aria-live="polite">
          ✗ Incorrect PIN. Please try again.
        </div>
        <div class="mt-6">
          <button type="submit" class="btn btn-primary btn-lg btn-full" id="btn-unlock">
            🔓 Unlock Guardian Mode
          </button>
        </div>
      </form>
    </div>`;

  document.getElementById('pin-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const pin = document.getElementById('pin-field').value.trim();
    const errEl = document.getElementById('pin-error');
    const btn   = document.getElementById('btn-unlock');

    errEl.classList.add('hidden');
    btn.disabled = true;
    btn.textContent = '…';

    try {
      await api.post('/api/auth/login', { pin });
      renderDashboard();
      loadDashboardData();
    } catch (_) {
      errEl.classList.remove('hidden');
      document.getElementById('pin-field').value = '';
      document.getElementById('pin-field').focus();
    } finally {
      btn.disabled = false;
      btn.textContent = '🔓 Unlock Guardian Mode';
    }
  });
}

// ── Dashboard shell ──────────────────────────────────────────────────

function renderDashboard() {
  document.getElementById('guardian-app').innerHTML = `
    <div class="guardian-layout">

      <!-- Sidebar -->
      <nav class="guardian-sidebar" aria-label="Guardian sections">
        <div class="guardian-sidebar__label">Management</div>
        <div class="guardian-sidebar__section" id="sidebar-nav">
          <button class="guardian-nav-item active" data-section="keywords">
            🗂️ Keywords
          </button>
          <button class="guardian-nav-item" data-section="categories">
            📁 Categories
          </button>
          <button class="guardian-nav-item" data-section="seed">
            🌱 Sample Phrases
          </button>
        </div>
        <div class="guardian-sidebar__label">Danger</div>
        <div class="guardian-sidebar__section">
          <button class="guardian-nav-item" id="btn-logout"
                  style="color:var(--color-error);">
            🔒 Lock Guardian Mode
          </button>
        </div>
      </nav>

      <!-- Main area -->
      <main class="guardian-main" id="guardian-section-area" aria-live="polite">
        <div class="flex items-center" style="min-height:200px;">
          <div class="spinner" aria-label="Loading…"></div>
        </div>
      </main>

    </div>`;

  // Sidebar navigation
  document.getElementById('sidebar-nav').addEventListener('click', (e) => {
    const btn = e.target.closest('[data-section]');
    if (!btn) return;
    document.querySelectorAll('.guardian-nav-item').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderSection(btn.dataset.section);
  });

  document.getElementById('btn-logout').addEventListener('click', async () => {
    await api.post('/api/auth/logout', {});
    renderPinScreen();
  });
}

// ── Section router ────────────────────────────────────────────────────

function renderSection(name) {
  switch (name) {
    case 'keywords':   renderKeywordsSection(); break;
    case 'categories': renderCategoriesSection(); break;
    case 'seed':       renderSeedSection(); break;
  }
}

async function loadDashboardData() {
  try {
    [_categories, _keywords] = await Promise.all([
      api.get('/api/categories/all'),
      api.get('/api/keywords/all'),
    ]);
    renderSection('keywords');
  } catch (err) {
    showToast('Failed to load data: ' + err.message, 'error');
  }
}

// ── Keywords section ─────────────────────────────────────────────────

function renderKeywordsSection() {
  const area = document.getElementById('guardian-section-area');
  area.innerHTML = `
    <div class="flex items-center justify-between mb-6 flex-wrap gap-4">
      <h2 class="text-xl">Keywords</h2>
      <button class="btn btn-primary" id="btn-new-keyword">+ New Keyword</button>
    </div>

    <!-- Filters -->
    <div class="flex gap-3 mb-4 flex-wrap">
      <select id="filter-category" class="form-control" style="max-width:200px;">
        <option value="">All categories</option>
        ${_categories.map(c => `<option value="${c.id}">${escHtml(c.name)}</option>`).join('')}
      </select>
      <label class="flex items-center gap-2 text-sm">
        <input type="checkbox" id="filter-disabled" /> Show disabled
      </label>
    </div>

    <!-- Keywords table -->
    <div id="keywords-list"></div>

    <!-- Keyword form modal -->
    <div id="keyword-modal" class="modal-overlay hidden" role="dialog"
         aria-modal="true" aria-labelledby="modal-title">
      <div class="modal-box card card-padded" style="max-width:520px;width:100%;">
        <h3 id="modal-title" class="text-lg mb-4">Add Keyword</h3>
        <form id="keyword-form" novalidate>
          <div class="form-group mb-4">
            <label class="form-label">Label <span class="required" aria-hidden="true">*</span></label>
            <input type="text" id="kf-label" maxlength="100" required placeholder="e.g. Water" />
          </div>
          <div class="form-group mb-4">
            <label class="form-label">Message <span class="required" aria-hidden="true">*</span></label>
            <textarea id="kf-message" rows="3" required
                      placeholder="e.g. I would like some water, please."></textarea>
          </div>
          <div class="flex gap-4 mb-4 flex-wrap">
            <div class="form-group flex-1" style="min-width:140px;">
              <label class="form-label">Category</label>
              <select id="kf-category">
                <option value="">— None —</option>
                ${_categories.map(c => `<option value="${c.id}">${escHtml(c.name)}</option>`).join('')}
              </select>
            </div>
            <div class="form-group" style="min-width:80px;">
              <label class="form-label">Icon</label>
              <input type="text" id="kf-icon" maxlength="10" placeholder="💧" style="text-align:center;" />
            </div>
          </div>
          <div class="flex gap-6 mb-6">
            <label class="flex items-center gap-2 text-sm">
              <input type="checkbox" id="kf-urgent" /> Urgent
            </label>
            <label class="flex items-center gap-2 text-sm">
              <input type="checkbox" id="kf-enabled" checked /> Enabled
            </label>
          </div>
          <div id="kf-error" class="form-error mb-3 hidden" role="alert"></div>
          <div class="flex gap-3 justify-end flex-wrap">
            <button type="button" class="btn btn-ghost" id="btn-modal-cancel">Cancel</button>
            <button type="submit" class="btn btn-primary" id="btn-modal-save">Save</button>
          </div>
        </form>
      </div>
    </div>`;

  renderKeywordsList();

  document.getElementById('btn-new-keyword').addEventListener('click', () => openKeywordModal(null));
  document.getElementById('btn-modal-cancel').addEventListener('click', closeKeywordModal);
  document.getElementById('filter-category').addEventListener('change', renderKeywordsList);
  document.getElementById('filter-disabled').addEventListener('change', renderKeywordsList);
  document.getElementById('keyword-form').addEventListener('submit', saveKeyword);
}

function renderKeywordsList() {
  const catFilter  = document.getElementById('filter-category')?.value;
  const showDisabled = document.getElementById('filter-disabled')?.checked;

  let filtered = _keywords.filter(kw => {
    if (catFilter && String(kw.category_id) !== catFilter) return false;
    if (!showDisabled && !kw.is_enabled) return false;
    return true;
  });

  const list = document.getElementById('keywords-list');
  if (!list) return;

  if (filtered.length === 0) {
    list.innerHTML = `<div class="empty-state">
      <div class="empty-state__icon" aria-hidden="true">🗂️</div>
      <p class="empty-state__body">No keywords yet. Click "+ New Keyword" to add one,
      or use "Sample Phrases" to seed the defaults.</p>
    </div>`;
    return;
  }

  list.innerHTML = `<div class="card" style="overflow:auto;">
    <table class="kw-table" style="width:100%;border-collapse:collapse;" aria-label="Keywords">
      <thead>
        <tr style="border-bottom:2px solid var(--color-border);text-align:left;">
          <th style="padding:var(--space-3) var(--space-4);font-size:var(--font-size-xs);letter-spacing:var(--letter-spacing-widest);text-transform:uppercase;color:var(--color-text-tertiary);">Label</th>
          <th style="padding:var(--space-3) var(--space-4);" class="hide-mobile">Message</th>
          <th style="padding:var(--space-3) var(--space-4);" class="hide-mobile">Category</th>
          <th style="padding:var(--space-3) var(--space-4);">Flags</th>
          <th style="padding:var(--space-3) var(--space-4);">Actions</th>
        </tr>
      </thead>
      <tbody id="kw-tbody">
        ${filtered.map(kw => renderKeywordRow(kw)).join('')}
      </tbody>
    </table>
  </div>`;

  list.querySelectorAll('[data-edit]').forEach(btn =>
    btn.addEventListener('click', () => openKeywordModal(_keywords.find(k => k.id === +btn.dataset.edit))));
  list.querySelectorAll('[data-toggle]').forEach(btn =>
    btn.addEventListener('click', () => toggleKeyword(+btn.dataset.toggle)));
  list.querySelectorAll('[data-delete]').forEach(btn =>
    btn.addEventListener('click', () => deleteKeyword(+btn.dataset.delete)));
}

function renderKeywordRow(kw) {
  const catName = _categories.find(c => c.id === kw.category_id)?.name || '—';
  const disabledStyle = kw.is_enabled ? '' : 'opacity:0.5;';
  return `<tr style="border-bottom:1px solid var(--color-border);${disabledStyle}">
    <td style="padding:var(--space-3) var(--space-4);">
      <span style="font-size:1.2em;margin-right:4px;">${escHtml(kw.icon || '')}</span>
      <strong>${escHtml(kw.label)}</strong>
    </td>
    <td style="padding:var(--space-3) var(--space-4);max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" class="hide-mobile">
      ${escHtml(kw.message)}
    </td>
    <td style="padding:var(--space-3) var(--space-4);" class="hide-mobile">${escHtml(catName)}</td>
    <td style="padding:var(--space-3) var(--space-4);">
      ${kw.is_urgent  ? '<span class="badge badge-urgent">Urgent</span>' : ''}
      ${!kw.is_enabled ? '<span class="badge badge-neutral">Off</span>' : ''}
    </td>
    <td style="padding:var(--space-3) var(--space-4);">
      <div class="flex gap-2">
        <button class="btn btn-sm btn-ghost" data-edit="${kw.id}" aria-label="Edit ${escHtml(kw.label)}">✏️</button>
        <button class="btn btn-sm btn-ghost" data-toggle="${kw.id}"
                aria-label="${kw.is_enabled ? 'Disable' : 'Enable'} ${escHtml(kw.label)}">
          ${kw.is_enabled ? '⏸' : '▶'}
        </button>
        <button class="btn btn-sm btn-ghost" data-delete="${kw.id}"
                aria-label="Delete ${escHtml(kw.label)}"
                style="color:var(--color-error);">🗑️</button>
      </div>
    </td>
  </tr>`;
}

function openKeywordModal(kw) {
  _editingKeyword = kw;
  const modal = document.getElementById('keyword-modal');
  document.getElementById('modal-title').textContent = kw ? 'Edit Keyword' : 'Add Keyword';
  document.getElementById('kf-label').value    = kw?.label   || '';
  document.getElementById('kf-message').value  = kw?.message || '';
  document.getElementById('kf-icon').value     = kw?.icon    || '';
  document.getElementById('kf-urgent').checked = kw?.is_urgent  ?? false;
  document.getElementById('kf-enabled').checked= kw?.is_enabled ?? true;
  const catSel = document.getElementById('kf-category');
  catSel.value = kw?.category_id ?? '';
  document.getElementById('kf-error').classList.add('hidden');
  modal.classList.remove('hidden');
  document.getElementById('kf-label').focus();
}

function closeKeywordModal() {
  document.getElementById('keyword-modal').classList.add('hidden');
  _editingKeyword = null;
}

async function saveKeyword(e) {
  e.preventDefault();
  const errEl = document.getElementById('kf-error');
  errEl.classList.add('hidden');

  const label   = document.getElementById('kf-label').value.trim();
  const message = document.getElementById('kf-message').value.trim();
  const icon    = document.getElementById('kf-icon').value.trim();
  const catId   = document.getElementById('kf-category').value;
  const urgent  = document.getElementById('kf-urgent').checked;
  const enabled = document.getElementById('kf-enabled').checked;

  if (!label || !message) {
    errEl.textContent = 'Label and message are required.';
    errEl.classList.remove('hidden');
    return;
  }

  const payload = {
    label, message,
    icon: icon || null,
    category_id: catId ? +catId : null,
    is_urgent: urgent,
    is_enabled: enabled,
  };

  const btn = document.getElementById('btn-modal-save');
  btn.disabled = true;

  try {
    if (_editingKeyword) {
      const updated = await api.patch(`/api/keywords/${_editingKeyword.id}`, payload);
      _keywords = _keywords.map(k => k.id === updated.id ? updated : k);
      showToast(`"${updated.label}" updated.`, 'success');
    } else {
      const created = await api.post('/api/keywords/', payload);
      _keywords.push(created);
      showToast(`"${created.label}" added.`, 'success');
    }
    closeKeywordModal();
    renderKeywordsList();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  } finally {
    btn.disabled = false;
  }
}

async function toggleKeyword(id) {
  const kw = _keywords.find(k => k.id === id);
  if (!kw) return;
  try {
    const updated = await api.patch(`/api/keywords/${id}`, { is_enabled: !kw.is_enabled });
    _keywords = _keywords.map(k => k.id === id ? updated : k);
    renderKeywordsList();
  } catch (err) {
    showToast('Toggle failed: ' + err.message, 'error');
  }
}

async function deleteKeyword(id) {
  const kw = _keywords.find(k => k.id === id);
  if (!kw) return;
  if (!confirm(`Delete keyword "${kw.label}"? This cannot be undone.`)) return;
  try {
    await api.delete(`/api/keywords/${id}`);
    _keywords = _keywords.filter(k => k.id !== id);
    renderKeywordsList();
    showToast(`"${kw.label}" deleted.`, 'success');
  } catch (err) {
    showToast('Delete failed: ' + err.message, 'error');
  }
}

// ── Categories section ────────────────────────────────────────────────

function renderCategoriesSection() {
  const area = document.getElementById('guardian-section-area');
  area.innerHTML = `
    <div class="flex items-center justify-between mb-6 flex-wrap gap-4">
      <h2 class="text-xl">Categories</h2>
      <button class="btn btn-primary" id="btn-new-category">+ New Category</button>
    </div>
    <div id="categories-list"></div>

    <div id="category-modal" class="modal-overlay hidden" role="dialog"
         aria-modal="true" aria-labelledby="cat-modal-title">
      <div class="modal-box card card-padded" style="max-width:420px;width:100%;">
        <h3 id="cat-modal-title" class="text-lg mb-4">Add Category</h3>
        <form id="category-form" novalidate>
          <div class="form-group mb-4">
            <label class="form-label">Name <span class="required" aria-hidden="true">*</span></label>
            <input type="text" id="cf-name" maxlength="100" required placeholder="e.g. Daily Needs" />
          </div>
          <div class="form-group mb-4">
            <label class="form-label">Description</label>
            <input type="text" id="cf-desc" maxlength="255" placeholder="Optional description" />
          </div>
          <div class="form-group mb-4">
            <label class="form-label">Icon</label>
            <input type="text" id="cf-icon" maxlength="10" placeholder="🏠" style="text-align:center;" />
          </div>
          <label class="flex items-center gap-2 text-sm mb-6">
            <input type="checkbox" id="cf-enabled" checked /> Enabled
          </label>
          <div id="cf-error" class="form-error mb-3 hidden" role="alert"></div>
          <div class="flex gap-3 justify-end">
            <button type="button" class="btn btn-ghost" id="btn-cat-cancel">Cancel</button>
            <button type="submit" class="btn btn-primary" id="btn-cat-save">Save</button>
          </div>
        </form>
      </div>
    </div>`;

  renderCategoryList();
  document.getElementById('btn-new-category').addEventListener('click', () => openCategoryModal(null));
  document.getElementById('btn-cat-cancel').addEventListener('click', closeCategoryModal);
  document.getElementById('category-form').addEventListener('submit', saveCategory);
}

function renderCategoryList() {
  const list = document.getElementById('categories-list');
  if (!list) return;
  if (_categories.length === 0) {
    list.innerHTML = `<div class="empty-state">
      <div class="empty-state__icon" aria-hidden="true">📁</div>
      <p class="empty-state__body">No categories yet.</p>
    </div>`;
    return;
  }
  list.innerHTML = `<div class="grid" style="gap:var(--space-3);">
    ${_categories.map(cat => `
      <div class="card card-padded flex items-center justify-between gap-4"
           style="${cat.is_enabled ? '' : 'opacity:0.5;'}">
        <div class="flex items-center gap-3">
          <span style="font-size:1.5rem;">${escHtml(cat.icon || '📁')}</span>
          <div>
            <strong class="text-base">${escHtml(cat.name)}</strong>
            <p class="text-xs text-secondary">${escHtml(cat.description || '')}</p>
          </div>
        </div>
        <div class="flex gap-2">
          <button class="btn btn-sm btn-ghost" data-cat-edit="${cat.id}"
                  aria-label="Edit ${escHtml(cat.name)}">✏️</button>
          <button class="btn btn-sm btn-ghost" data-cat-delete="${cat.id}"
                  aria-label="Delete ${escHtml(cat.name)}"
                  style="color:var(--color-error);">🗑️</button>
        </div>
      </div>`).join('')}
  </div>`;
  list.querySelectorAll('[data-cat-edit]').forEach(b =>
    b.addEventListener('click', () => openCategoryModal(_categories.find(c => c.id === +b.dataset.catEdit))));
  list.querySelectorAll('[data-cat-delete]').forEach(b =>
    b.addEventListener('click', () => deleteCategory(+b.dataset.catDelete)));
}

function openCategoryModal(cat) {
  _editingCategory = cat;
  document.getElementById('cat-modal-title').textContent = cat ? 'Edit Category' : 'Add Category';
  document.getElementById('cf-name').value = cat?.name        || '';
  document.getElementById('cf-desc').value = cat?.description || '';
  document.getElementById('cf-icon').value = cat?.icon        || '';
  document.getElementById('cf-enabled').checked = cat?.is_enabled ?? true;
  document.getElementById('cf-error').classList.add('hidden');
  document.getElementById('category-modal').classList.remove('hidden');
  document.getElementById('cf-name').focus();
}

function closeCategoryModal() {
  document.getElementById('category-modal').classList.add('hidden');
  _editingCategory = null;
}

async function saveCategory(e) {
  e.preventDefault();
  const errEl = document.getElementById('cf-error');
  errEl.classList.add('hidden');

  const name    = document.getElementById('cf-name').value.trim();
  const desc    = document.getElementById('cf-desc').value.trim();
  const icon    = document.getElementById('cf-icon').value.trim();
  const enabled = document.getElementById('cf-enabled').checked;

  if (!name) {
    errEl.textContent = 'Name is required.';
    errEl.classList.remove('hidden');
    return;
  }

  const payload = { name, description: desc || null, icon: icon || null, is_enabled: enabled };
  const btn = document.getElementById('btn-cat-save');
  btn.disabled = true;

  try {
    if (_editingCategory) {
      const updated = await api.patch(`/api/categories/${_editingCategory.id}`, payload);
      _categories = _categories.map(c => c.id === updated.id ? updated : c);
      showToast(`Category "${updated.name}" updated.`, 'success');
    } else {
      const created = await api.post('/api/categories/', payload);
      _categories.push(created);
      showToast(`Category "${created.name}" created.`, 'success');
    }
    closeCategoryModal();
    renderCategoryList();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  } finally {
    btn.disabled = false;
  }
}

async function deleteCategory(id) {
  const cat = _categories.find(c => c.id === id);
  if (!cat) return;
  if (!confirm(`Delete category "${cat.name}"? All keywords must be reassigned first.`)) return;
  try {
    await api.delete(`/api/categories/${id}`);
    _categories = _categories.filter(c => c.id !== id);
    renderCategoryList();
    showToast(`Category "${cat.name}" deleted.`, 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ── Seed section ──────────────────────────────────────────────────────

function renderSeedSection() {
  const area = document.getElementById('guardian-section-area');
  area.innerHTML = `
    <h2 class="text-xl mb-4">Sample Phrases</h2>
    <div class="card card-padded" style="max-width:560px;">
      <p class="text-secondary mb-4">
        Seed EchoAid with starter categories and phrases covering daily needs,
        health, emotions, people, and urgent communication.
        Existing keywords with the same label won't be duplicated.
        All seeded phrases are fully editable.
      </p>
      <div id="seed-result" class="mb-4"></div>
      <button class="btn btn-primary" id="btn-seed">🌱 Seed Sample Phrases</button>
    </div>`;

  document.getElementById('btn-seed').addEventListener('click', async () => {
    const btn = document.getElementById('btn-seed');
    btn.disabled = true;
    btn.textContent = '…seeding';
    try {
      const result = await api.post('/api/keywords/seed', {});
      document.getElementById('seed-result').innerHTML =
        `<div class="alert alert-success" role="status">
           ✓ Done — ${result.categories_created} categories and
           ${result.keywords_created} keywords created.
         </div>`;
      // Refresh local data
      [_categories, _keywords] = await Promise.all([
        api.get('/api/categories/all'),
        api.get('/api/keywords/all'),
      ]);
      showToast('Sample phrases seeded!', 'success');
    } catch (err) {
      document.getElementById('seed-result').innerHTML =
        `<div class="alert alert-error" role="alert">✗ ${escHtml(err.message)}</div>`;
    } finally {
      btn.disabled = false;
      btn.textContent = '🌱 Seed Sample Phrases';
    }
  });
}

// ── Shared helpers ────────────────────────────────────────────────────

function escHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
