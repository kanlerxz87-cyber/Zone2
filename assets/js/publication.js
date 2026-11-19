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
}());
