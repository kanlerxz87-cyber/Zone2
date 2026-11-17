/* Zone2 privacy-preserving counter — assets/js/analytics.js
 *
 * What this is: the client half of the measurement layer designed in
 * docs/measurement-t40.json (EV-01 page_view, EV-02 product_link_click,
 * EV-03 disclosure_view). The server half is tools/analytics_server.py.
 *
 * What it is not: a tracker. There is no cookie, no local storage, no visitor
 * identifier, no fingerprinting, no full referrer, no exact resolution. Each
 * beacon carries the event's own fields and a UTC calendar day — nothing that
 * can single out a person. The endpoint meta tag ships EMPTY, so on a stock
 * build this file is a no-op: it exists, it fires nothing, and no data exists.
 * EV-04 (conversion) and EV-05 (health) are deliberately not implemented here —
 * EV-04 can only come from Amazon's Associates reporting and nothing on this
 * site may invent it.
 *
 * Config (owner, when a sink is deployed):
 *   <meta name="zone2-analytics-endpoint" content="https://your-collector.example/collect">
 */
(function () {
  "use strict";

  var meta = document.querySelector('meta[name="zone2-analytics-endpoint"]');
  var endpoint = (meta && meta.getAttribute("content")) || "";

  // No endpoint configured -> strict no-op. This is the shipped state.
  if (!endpoint || !/^https?:\/\//.test(endpoint)) {
    return;
  }

  var DAY = function () {
    // A calendar day, not a timestamp. The one time field this layer keeps.
    return new Date().toISOString().slice(0, 10);
  };

  // viewport_class is a coarse bucket ("small" | "medium" | "large"),
  // never a resolution — see MP-01 and EV-01's deliberately_not_collected.
  var VIEWPORT_CLASS = (function () {
    var w = window.innerWidth || 0;
    if (w < 640) { return "small"; }
    if (w < 1024) { return "medium"; }
    return "large";
  })();

  // referrer_host is a host name only (example.org), never a URL, path or
  // query string. A full referrer can carry tokens and user ids.
  var REFERRER_HOST = (function () {
    var raw = document.referrer || "";
    if (!raw) { return "direct"; }
    try {
      var host = new URL(raw).hostname;
      return host || "direct";
    } catch (err) {
      return "direct";
    }
  })();

  var send = function (payload) {
    var body = JSON.stringify(payload);
    try {
      if (navigator.sendBeacon && navigator.sendBeacon(endpoint, body)) {
        return;
      }
    } catch (err) { /* fall through */ }
    try {
      fetch(endpoint, {
        method: "POST",
        body: body,
        keepalive: true,
        headers: { "Content-Type": "application/json" }
      }).catch(function () { /* the sink is not deployed — nothing is lost */ });
    } catch (err) { /* no-op */ }
  };

  var record = function (event, fields) {
    var payload = { event: event, day: DAY() };
    for (var key in fields) {
      if (Object.prototype.hasOwnProperty.call(fields, key)) {
        payload[key] = fields[key];
      }
    }
    send(payload);
  };

  // ---- EV-01 page_view -------------------------------------------------
  record("page_view", {
    page_path: location.pathname,
    referrer_host: REFERRER_HOST,
    viewport_class: VIEWPORT_CLASS
  });

  // ---- EV-02 product_link_click ---------------------------------------
  // Fired from clicks on outbound product links. The link carries
  // data-product-key (the ASIN), data-link-state and data-placement so the
  // event reports what the link IS, never who clicked it.
  document.addEventListener("click", function (ev) {
    var target = ev.target;
    while (target && target !== document.body && target.tagName !== "A") {
      target = target.parentNode;
    }
    if (!target || target.tagName !== "A") { return; }
    if (!target.getAttribute("data-product-key")) { return; }
    record("product_link_click", {
      page_path: location.pathname,
      product_key: target.getAttribute("data-product-key"),
      link_state: target.getAttribute("data-link-state") || "unknown",
      placement: target.getAttribute("data-placement") || "unspecified"
    });
  });

  // ---- EV-03 disclosure_view ------------------------------------------
  // The disclosure strip publishes with each page; this reports that a
  // disclosure entered the viewport (and at which position), not who read it.
  var disclosure = document.querySelector("[data-disclosure-position]");
  if (disclosure && "IntersectionObserver" in window) {
    var fired = false;
    var observer = new IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i++) {
        if (!fired && entries[i].isIntersecting) {
          fired = true;
          record("disclosure_view", {
            page_path: location.pathname,
            disclosure_position: disclosure.getAttribute("data-disclosure-position") || "unspecified"
          });
          observer.disconnect();
        }
      }
    });
    observer.observe(disclosure);
  }
})();
