/* Optional OPERATOR preferences only. No implementation, network submission, account data or reader IDs. */
(function () {
  'use strict';
  var key = 'cn-review-choices-v1';
  var proposals = Array.from(document.querySelectorAll('[data-proposal]'));
  var status = document.getElementById('review-status');
  if (!proposals.length || !status) { return; }
  var choices = {};
  try { choices = JSON.parse(localStorage.getItem(key) || '{}'); } catch (e) { choices = {}; }
  if (!choices || typeof choices !== 'object' || Array.isArray(choices)) { choices = {}; }

  function selectedRecords() {
    return proposals.flatMap(function (proposal) {
      var id = proposal.dataset.proposal;
      var selected = proposal.querySelector('input:checked');
      return selected ? [{ suggestion_id: id, preferred_option: selected.value }] : [];
    });
  }
  function update(proposal) {
    var selected = proposal.querySelector('input:checked');
    proposal.querySelector('[data-choice-state]').textContent = selected
      ? 'Local preference: option ' + selected.value + '. Review only—not approval or implementation.'
      : 'No local preference recorded.';
  }
  proposals.forEach(function (proposal) {
    var id = proposal.dataset.proposal;
    proposal.querySelectorAll('input[type="radio"]').forEach(function (input) {
      input.checked = input.value === choices[id];
      input.addEventListener('change', function () {
        var safe = Object.fromEntries(selectedRecords().map(function (record) { return [record.suggestion_id, record.preferred_option]; }));
        try { localStorage.setItem(key, JSON.stringify(safe)); status.textContent = 'Preference saved in this browser only.'; }
        catch (e) { status.textContent = 'Browser storage unavailable. You can still export this review.'; }
        update(proposal);
      });
    });
    update(proposal);
  });
  document.getElementById('clear-choices').addEventListener('click', function () {
    try { localStorage.removeItem(key); } catch (e) { /* no backend fallback */ }
    proposals.forEach(function (proposal) {
      proposal.querySelectorAll('input').forEach(function (input) { input.checked = false; });
      update(proposal);
    });
    status.textContent = 'Local preferences cleared. The website was not changed.';
  });
  document.getElementById('export-choices').addEventListener('click', function () {
    var doc = { scope: 'review_preferences_only', notice: 'Not an approval, server record, enrollment confirmation or implementation request.', exported_at: new Date().toISOString(), choices: selectedRecords() };
    var url = URL.createObjectURL(new Blob([JSON.stringify(doc, null, 2) + '\n'], { type: 'application/json' }));
    var link = document.createElement('a');
    link.href = url;
    link.download = 'counter-notes-review-choices.json';
    link.click();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    status.textContent = 'Review record exported. No changes were applied.';
  });
}());
