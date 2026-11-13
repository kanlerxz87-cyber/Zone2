/* Zone2 — renders dashboard tables from window.ZONE2_DATA.
 * No backend, no fetch: data is inlined in data.js so the site works
 * statically on GitHub Pages with no broken internal links. */
(function () {
  "use strict";
  var D = window.ZONE2_DATA;

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === "class") node.className = attrs[k];
        else if (k === "html") node.innerHTML = attrs[k];
        else if (k.indexOf("on") === 0) node.addEventListener(k.slice(2), attrs[k]);
        else node.setAttribute(k, attrs[k]);
      });
    }
    var kids = children ? (Array.isArray(children) ? children : [children]) : [];
    kids.forEach(function (c) {
      if (c === null || c === undefined) return;
      node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return node;
  }

  function val(v) {
    return v === "" || v === null || v === undefined ? "" : String(v);
  }

  function cell(v, cls) {
    if (val(v) === "") {
      return el("span", { class: "empty", title: "Not confirmed from an official source" }, "— unverified");
    }
    return el("span", { class: cls || "" }, val(v));
  }

  function link(href, text) {
    return el("a", { href: href, target: "_blank", rel: "noopener noreferrer", class: "src-link" }, text);
  }

  /* ---------- Product catalog table ---------- */
  function renderProductTable() {
    var host = document.getElementById("productTable");
    if (!host) return;
    var thead = el("thead", null, [
      el("tr", null, [
        el("th", null, ["Product"]),
        el("th", null, ["Brand / ASIN"]),
        el("th", null, ["Category"]),
        el("th", null, ["Price (USD)"]),
        el("th", null, ["Rating"]),
        el("th", null, ["Reviews"]),
        el("th", null, ["Best Sellers Rank"]),
        el("th", null, ["Commission"]),
        el("th", null, ["Source"]),
        el("th", null, ["Status"]),
      ]),
    ]);
    var tbody = el("tbody");
    D.products.forEach(function (p) {
      var pct = p.commissionPerSale
        ? "4.5% · $" + p.commissionPerSale
        : p.commissionRate + " · —";
      var status = p.verification.indexOf("Unverified") !== -1
        ? el("span", { class: "pill unverified" }, "Needs review")
        : el("span", { class: "pill verified" }, "Verified");
      var row = el("tr", null, [
        el("td", null, [el("strong", null, [p.brand]), document.createTextNode(" "),
          el("span", { class: "mono" }, p.asin)]),
        el("td", null, [el("div", null, [cell(p.brand)]),
          el("div", { class: "mono muted" }, p.partNumber ? p.partNumber : "")]),
        el("td", null, [el("div", null, [cell(p.subcategory)]),
          el("div", { class: "muted" }, p.category)]),
        el("td", null, [cell(p.priceUsd ? "$" + p.priceUsd : "")]),
        el("td", null, [cell(p.ratingStars ? p.ratingStars + " ★" : "")]),
        el("td", null, [cell(p.reviewCount)]),
        el("td", null, [cell(p.bsrRank)]),
        el("td", null, [cell(pct)]),
        el("td", null, [link(p.sourceUrl, "Amazon listing")]),
        el("td", null, [status]),
      ]);
      tbody.appendChild(row);
    });
    var table = el("table", null, [thead, tbody]);
    host.appendChild(table);
  }

  /* ---------- Full product detail table ---------- */
  function renderDetailTable() {
    var host = document.getElementById("detailTable");
    if (!host) return;
    var rows = [
      ["Product", function (p) { return p.brand + " — " + p.title; }],
      ["Short affiliate link", function (p) { return link(p.shortLink, p.shortLink); }],
      ["Canonical Amazon URL", function (p) { return link(p.canonicalUrl, p.canonicalUrl); }],
      ["Brand", function (p) { return cell(p.brand); }],
      ["ASIN (redirect target)", function (p) { return el("span", { class: "mono" }, p.asin); }],
      ["Category", function (p) { return cell(p.subcategory); }],
      ["Part number", function (p) { return el("span", { class: "mono" }, val(p.partNumber)); }],
      ["UPC", function (p) { return el("span", { class: "mono" }, val(p.upc)); }],
      ["Model", function (p) { return cell(p.model); }],
      ["Color", function (p) { return cell(p.color); }],
      ["Capacity", function (p) { return cell(p.capacity); }],
      ["Power", function (p) { return cell(p.power); }],
      ["Temperature range", function (p) { return cell(p.tempRange); }],
      ["Dimensions", function (p) { return cell(p.dimensions); }],
      ["Weight", function (p) { return cell(p.weight); }],
      ["Price (USD)", function (p) { return p.priceUsd ? "$" + p.priceUsd : cell(""); }],
      ["List price (USD)", function (p) { return p.listPriceUsd ? "$" + p.listPriceUsd : cell(""); }],
      ["Star rating", function (p) { return p.ratingStars ? p.ratingStars + " ★" : cell(""); }],
      ["Review count", function (p) { return cell(p.reviewCount); }],
      ["Best Sellers Rank", function (p) { return cell(p.bsrRank); }],
      ["Buy-velocity signal", function (p) { return cell(p.boughtSignal); }],
      ["Commission category / rate", function (p) { return p.commissionCategory + " · " + p.commissionRate; }],
      ["Est. commission / sale", function (p) { return p.commissionPerSale ? "$" + p.commissionPerSale : cell(""); }],
      ["Verification", function (p) { return cell(p.verification); }],
      ["Source", function (p) { return link(p.sourceUrl, "Amazon.com listing"); }],
    ];
    var thead = el("thead", null, [
      el("tr", null, [el("th", null, ["Field"]), el("th", null, ["P1 — Chefman 6Qt Dual"]),
        el("th", null, ["P2 — Emeril 26QT"]), el("th", null, ["P3 — Chefman 8Qt"])]),
    ]);
    var tbody = el("tbody");
    rows.forEach(function (r) {
      var label = r[0];
      var fn = r[1];
      var tr = el("tr", null, [el("th", null, [label])]);
      D.products.forEach(function (p) { tr.appendChild(el("td", null, [fn(p)])); });
      tbody.appendChild(tr);
    });
    host.appendChild(el("table", null, [thead, tbody]));
  }

  /* ---------- Analysis: commission table ---------- */
  function renderCommission() {
    var host = document.getElementById("commissionTable");
    if (!host) return;
    var thead = el("thead", null, [el("tr", null, [el("th", null, ["US category"]), el("th", null, ["Standard commission rate"])])]);
    var tbody = el("tbody");
    D.commission.rates.forEach(function (r) {
      tbody.appendChild(el("tr", null, [el("td", null, [r.category]), el("td", null, [r.rate])]));
    });
    host.appendChild(el("table", null, [thead, tbody]));
  }

  /* ---------- Flagged for review ---------- */
  function renderFlagged() {
    var host = document.getElementById("flaggedList");
    if (!host) return;
    D.flagged.forEach(function (f) {
      var pill = f.status === "unverified"
        ? el("span", { class: "pill unverified" }, "Unverified")
        : el("span", { class: "pill irregularity" }, "Irregularity");
      host.appendChild(el("div", { class: "card", style: "margin-bottom:14px" }, [
        el("div", { style: "display:flex;gap:10px;align-items:center;flex-wrap:wrap" }, [
          pill,
          el("strong", null, [f.item]),
        ]),
        el("p", { style: "margin:10px 0;color:#374151" }, [f.detail]),
        el("div", null, [link(f.sourceUrl, "View source")]),
      ]));
    });
  }

  /* ---------- Compliance ---------- */
  function renderCompliance() {
    var host = document.getElementById("complianceList");
    if (!host) return;
    D.compliance.rules.forEach(function (r) {
      host.appendChild(el("div", { class: "card", style: "margin-bottom:12px" }, [
        el("h3", null, [r.rule]),
        el("p", { style: "margin:0" }, [r.requirement]),
      ]));
    });
  }

  function renderSources() {
    var host = document.getElementById("sourcesList");
    if (!host) return;
    var seen = {};
    var items = [];
    D.products.forEach(function (p) {
      if (!seen[p.sourceUrl]) { seen[p.sourceUrl] = p.sourceName; }
    });
    items.push({ name: "Amazon Associates — Operating Agreement", url: D.compliance.operatingAgreementUrl });
    items.push({ name: "Amazon Associates — Program Policies", url: D.compliance.policiesUrl });
    items.push({ name: "Amazon Associates — Disclosure (official Amazon page)", url: D.compliance.disclosureSourceUrl });
    Object.keys(seen).forEach(function (u) { items.push({ name: seen[u], url: u }); });
    items.forEach(function (s) {
      host.appendChild(el("li", null, [el("a", { href: s.url, target: "_blank", rel: "noopener noreferrer" }, [s.name]), document.createTextNode(" — " + s.url)]));
    });
  }

  function renderProductCards() {
    var host = document.getElementById("productCards");
    if (!host) return;
    D.products.forEach(function (p) {
      var price = p.priceUsd ? "$" + p.priceUsd : "unverified";
      var rating = p.ratingStars ? p.ratingStars + "★" : "unverified";
      host.appendChild(el("a", { class: "card", href: "products.html", style: "text-decoration:none;color:inherit" }, [
        el("div", { style: "display:flex;justify-content:space-between;align-items:center" }, [
          el("strong", null, [p.brand]),
          el("span", { class: "mono muted" }, p.asin),
        ]),
        el("div", { style: "font-size:13px;color:#374151;margin:8px 0;min-height:38px" }, [p.title]),
        el("div", { class: "grid cols-3", style: "gap:10px;font-size:13px" }, [
          el("div", { class: "kpi" }, [el("span", { class: "num", style: "font-size:18px" }, [price]), el("span", { class: "lbl" }, ["Price"])]),
          el("div", { class: "kpi" }, [el("span", { class: "num", style: "font-size:18px" }, [rating]), el("span", { class: "lbl" }, ["Rating"])]),
          el("div", { class: "kpi" }, [el("span", { class: "num", style: "font-size:18px" }, [p.commissionRate]), el("span", { class: "lbl" }, ["Commission"])]),
        ]),
        el("div", { style: "margin-top:12px;font-size:12.5px" }, [link(p.sourceUrl, "Verify on Amazon →")]),
      ]));
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    renderProductTable();
    renderDetailTable();
    renderCommission();
    renderFlagged();
    renderCompliance();
    renderSources();
    renderProductCards();
    // active nav
    var path = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".nav a").forEach(function (a) {
      var href = a.getAttribute("href");
      if (href === path) a.classList.add("active");
    });
  });
})();
