/* Keep late-rendered archive anchors qualified too. Never rewrites hrefs/tags or sends data. */
(function () {
  'use strict';
  function qualify(anchor) {
    if (!anchor || anchor.tagName !== 'A' || !anchor.hasAttribute('href')) { return; }
    var url;
    try { url = new URL(anchor.getAttribute('href'), location.href); } catch (error) { return; }
    var host = url.hostname.toLowerCase();
    if (url.protocol !== 'https:' && url.protocol !== 'http:') { return; }
    if (!/^(?:www\.)?amazon\.(?:com|ca|co\.uk|de|fr|it|es|nl|com\.au|co\.jp|in)$/.test(host) && host !== 'link.amazon' && host !== 'amzn.to') { return; }
    ['sponsored', 'nofollow', 'noopener', 'noreferrer'].forEach(function (value) { anchor.relList.add(value); });
  }
  function scan(node) {
    if (!node || node.nodeType !== 1) { return; }
    qualify(node);
    Array.prototype.forEach.call(node.querySelectorAll('a[href]'), qualify);
  }
  scan(document.documentElement);
  if ('MutationObserver' in window) {
    new MutationObserver(function (records) {
      records.forEach(function (record) {
        if (record.type === 'attributes') { qualify(record.target); }
        else { Array.prototype.forEach.call(record.addedNodes, scan); }
      });
    }).observe(document.documentElement, { childList: true, subtree: true, attributes: true, attributeFilter: ['href'] });
  }
}());
