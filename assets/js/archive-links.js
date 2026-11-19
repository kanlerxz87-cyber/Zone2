/* Preserve dated archive content while sponsoring runtime-generated product anchors.
   No tracking, storage, redirect, destination replacement or account assumption. */
(function () {
  'use strict';
  function qualify(anchor) {
    if (!anchor.matches || !anchor.matches('a[href]')) { return; }
    var url;
    try { url = new URL(anchor.getAttribute('href'), document.baseURI); } catch (e) { return; }
    if (!/^(?:(?:www\.)?amazon\.(?:com|ca|co\.uk|de|fr|it|es|co\.jp|com\.au)|link\.amazon|amzn\.to)$/.test(url.hostname)) { return; }
    anchor.relList.add('sponsored', 'nofollow', 'noopener');
    anchor.relList.remove('noreferrer');
  }
  function inspect(node) {
    if (node.nodeType !== 1) { return; }
    qualify(node);
    node.querySelectorAll('a[href]').forEach(qualify);
  }
  new MutationObserver(function (records) {
    records.forEach(function (record) {
      if (record.type === 'attributes') { qualify(record.target); }
      else { record.addedNodes.forEach(inspect); }
    });
  }).observe(document.documentElement, {childList: true, subtree: true, attributes: true, attributeFilter: ['href']});
  document.querySelectorAll('a[href]').forEach(qualify);
}());
