/**
 * EchoAid — Patient Mode
 *
 * Phase 1: Placeholder that confirms the page loads.
 * Phase 3 will implement full keyword loading, TTS, and category navigation.
 */

'use strict';

document.addEventListener('DOMContentLoaded', () => {
  window.EchoAid.applyDisplayPrefs();
  window.EchoAid.checkHealth();

  // Phase 3 will initialize keyword grid, TTS controls, etc. here.
  console.log('[EchoAid] Patient Mode loaded (Phase 1 placeholder).');
});
