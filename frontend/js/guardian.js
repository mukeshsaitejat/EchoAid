/**
 * EchoAid — Guardian Mode
 *
 * Phase 1: Placeholder that confirms the page loads.
 * Phase 2 will implement PIN auth, keyword management, and category CRUD.
 */

'use strict';

document.addEventListener('DOMContentLoaded', () => {
  window.EchoAid.applyDisplayPrefs();
  window.EchoAid.checkHealth();

  // Phase 2 will mount the PIN entry form and dashboard here.
  console.log('[EchoAid] Guardian Mode loaded (Phase 1 placeholder).');
});
