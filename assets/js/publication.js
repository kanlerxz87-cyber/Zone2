/* Progressive enhancements only: every product and guide remains accessible without JS. */
(function () {
  'use strict';
  document.querySelectorAll('.cn-workspace-menu').forEach(function (menu) {
    menu.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') { menu.open = false; menu.querySelector('summary').focus(); }
    });
    document.addEventListener('click', function (ev) { if (!menu.contains(ev.target)) { menu.open = false; } });
  });

  var filters = document.querySelectorAll('[data-filter]');
  var products = document.querySelectorAll('.cn-product[data-category]');
  var status = document.getElementById('filter-status');
  filters.forEach(function (button) {
    button.addEventListener('click', function () {
      var category = button.dataset.filter;
      var count = 0;
      filters.forEach(function (item) { item.setAttribute('aria-pressed', String(item === button)); });
      products.forEach(function (product) {
        product.hidden = category !== 'all' && product.dataset.category !== category;
        if (!product.hidden) { count += 1; }
      });
      if (status) { status.textContent = count + ' product notes shown'; }
    });
  });

  var finder = document.getElementById('kitchen-finder');
  var result = document.getElementById('finder-result');
  if (finder && result) {
    var choices = {
      two: ['guides/chefman-dual-basket.html', 'Explore the dual-basket format', 'Compare the split cooking space and Sync Finish claim.'],
      one: ['guides/chefman-single-basket.html', 'Explore the single-basket format', 'Check the exact model and unresolved temperature wording.'],
      oven: ['guides/emeril-french-door.html', 'Explore the countertop-oven format', 'Compare the footprint, functions and accessory questions.'],
      temperature: ['guides/instant-read-or-wireless.html', 'Compare temperature-tool formats', 'Start with spot checks versus connected monitoring.']
    };
    finder.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var value = document.getElementById('kitchen-priority').value;
      var choice = choices[value];
      if (!choice) { return; }
      result.replaceChildren();
      var link = document.createElement('a');
      link.href = choice[0];
      link.textContent = choice[1] + ' →';
      result.append(link, document.createElement('br'), document.createTextNode(choice[2] + ' A starting point, not a tested recommendation.'));
    });
  }

  var chooserForm = document.getElementById('chooser-form');
  var chooserResult = document.getElementById('chooser-result');
  if (chooserForm && chooserResult) {
    var payload = {};
    try { payload = JSON.parse(chooserForm.dataset.chooserMap || '{}'); } catch (err) { payload = {}; }
    var cmap = payload.map || { q1: {}, q2: {}, notes: {} };
    var cguides = payload.guides || {};
    var ctemperature = payload.temperature || ['#compare-list', 'Temperature-tool guide'];
    var ccaveat = payload.caveat || 'A starting point, not a tested recommendation.';
    chooserForm.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var q1 = document.querySelector('input[name="chooser-q1"]:checked');
      var q2 = document.querySelector('input[name="chooser-q2"]:checked');
      var q3 = document.querySelector('input[name="chooser-q3"]:checked');
      if (!q1) { chooserResult.textContent = 'Choose a job first to get a starting point.'; return; }
      var key = cmap.q1[q1.value];
      if (key === 'temperature') { key = q2 ? cmap.q2[q2.value] : 'temperature'; }
      var g = cguides[key] || ctemperature;
      var note = q3 ? (cmap.notes[q3.value] || '') : '';
      chooserResult.replaceChildren();
      var lead = document.createElement('strong');
      lead.textContent = 'A starting point: ' + g[1] + '. ';
      chooserResult.append(lead);
      var ln = document.createElement('a');
      ln.href = g[0];
      ln.textContent = 'Read the guide →';
      chooserResult.append(ln, document.createElement('br'));
      var cp = document.createElement('a');
      cp.href = key === 'temperature' ? '#compare-list' : '#' + key;
      cp.textContent = 'See it in the comparison →';
      chooserResult.append(cp);
      if (note) {
        chooserResult.append(document.createElement('br'));
        chooserResult.append(document.createTextNode(note + ' '));
      }
      chooserResult.append(document.createTextNode(ccaveat));
    });
  }
}());
