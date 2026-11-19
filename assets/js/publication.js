/* Progressive enhancement only: shopping links and guide navigation work without JS.
   Review-draft storage is user-triggered functional storage, not analytics. */
(function () {
  'use strict';
  var buttons = Array.prototype.slice.call(document.querySelectorAll('[data-filter]'));
  var cards = Array.prototype.slice.call(document.querySelectorAll('[data-product-category]'));
  var productStatus = document.querySelector('[data-product-status]');
  buttons.forEach(function (button) {
    button.addEventListener('click', function () {
      var filter = button.getAttribute('data-filter');
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b === button)); });
      var visible = 0;
      cards.forEach(function (card) {
        card.hidden = filter !== 'all' && card.getAttribute('data-product-category') !== filter;
        if (!card.hidden) { visible += 1; }
      });
      if (productStatus) { productStatus.textContent = visible + ' products shown'; }
    });
  });

  var search = document.querySelector('[data-tool-search]');
  if (search) {
    var tools = Array.prototype.slice.call(document.querySelectorAll('[data-tool-directory] > a'));
    var toolStatus = document.querySelector('[data-tool-status]');
    search.addEventListener('input', function () {
      var term = search.value.trim().toLowerCase();
      var visible = 0;
      tools.forEach(function (link) {
        link.hidden = link.textContent.toLowerCase().indexOf(term) === -1;
        if (!link.hidden) { visible += 1; }
      });
      if (toolStatus) { toolStatus.textContent = visible ? visible + ' operator areas' : 'No match. Try “source”, “tracking” or “decision”.'; }
    });
  }

  var options = Array.prototype.slice.call(document.querySelectorAll('[data-decision-option]'));
  if (!options.length) { return; }
  var key = 'counter-notes-review-v1';
  var status = document.querySelector('[data-decision-status]');
  function note(message) { if (status) { status.textContent = message; } }
  function record() {
    var choices = {};
    options.forEach(function (option) { if (option.checked) { choices[option.name] = option.value; } });
    return { schema: 1, created_at_utc: new Date().toISOString(), status: 'review_draft_only', applied: false, choices: choices };
  }
  try {
    var saved = JSON.parse(window.localStorage.getItem(key) || 'null');
    if (saved && saved.schema === 1 && saved.status === 'review_draft_only' && saved.choices && !saved.applied) {
      options.forEach(function (option) { option.checked = saved.choices[option.name] === option.value; });
      note('Saved local review draft restored. Nothing has been applied.');
    }
  } catch (error) { note('Browser storage unavailable. You can still choose options and export a draft.'); }
  options.forEach(function (option) {
    option.addEventListener('change', function () { note('Unsaved review choices. Nothing has been applied.'); });
  });
  document.querySelector('[data-save-decisions]').addEventListener('click', function () {
    try {
      window.localStorage.setItem(key, JSON.stringify(record()));
      note('Review draft saved in this browser only. No change has been approved or applied.');
    } catch (error) { note('Could not save in this browser. Export JSON to keep a copy instead.'); }
  });
  document.querySelector('[data-export-decisions]').addEventListener('click', function () {
    var data = record();
    var blob = new Blob([JSON.stringify(data, null, 2) + '\n'], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'counter-notes-review-' + data.created_at_utc.slice(0, 10) + '.json';
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    note('Review draft exported. It is not an implementation approval.');
  });
  document.querySelector('[data-reset-decisions]').addEventListener('click', function () {
    var cleared = true;
    try { window.localStorage.removeItem(key); } catch (error) { cleared = false; }
    options.forEach(function (option) { option.checked = false; });
    note(cleared ? 'Local draft cleared. No choices selected; no changes applied.' : 'Choices cleared on this page. Browser storage could not be cleared; check your browser settings.');
  });
}());
