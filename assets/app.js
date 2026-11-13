/* Zone2 dashboard — tiny progressive enhancement: highlight active nav link. */
document.addEventListener('DOMContentLoaded', function () {
  var path = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  document.querySelectorAll('nav.main a').forEach(function (a) {
    var href = (a.getAttribute('href') || '').toLowerCase();
    if (href === path) { a.classList.add('active'); a.setAttribute('aria-current', 'page'); }
  });
});
