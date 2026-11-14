/* Zone2 — render verified data into dashboard tables */
(function () {
  "use strict";

  function esc(s) {
    if (s === null || s === undefined || s === "") return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function cell(v) {
    if (v === null || v === undefined || v === "") {
      return '<span class="blank">— unverified —</span>';
    }
    return esc(v);
  }

  function link(url, label) {
    return '<a href="' + esc(url) + '" target="_blank" rel="noopener noreferrer">' + esc(label || url) + "</a>";
  }

  /* A source cell may name one official page or several (a value assembled from two
     official pages must link to both). Accepts a string or an array of strings. */
  function sourceCell(value, label) {
    if (Array.isArray(value)) {
      return value
        .map(function (u, i) {
          var text = label;
          if (Array.isArray(label)) text = label[i];
          return link(u, text || u.replace("https://", ""));
        })
        .join("<br>");
    }
    return link(value, label);
  }

  function badge(status) {
    if (status === "verified") return '<span class="badge ok">Verified</span>';
    if (status === "conflict") return '<span class="badge warn">Conflict</span>';
    if (status === "unverified") return '<span class="badge flag">Unverified</span>';
    return "";
  }

  function renderTable(id, columns, rows, opts) {
    opts = opts || {};
    const el = document.getElementById(id);
    if (!el) return;
    let html = '<div class="table-wrap"><table><thead><tr>';
    columns.forEach(function (c) { html += "<th>" + esc(c.label) + "</th>"; });
    html += "</tr></thead><tbody>";
    rows.forEach(function (r) {
      html += "<tr>";
      columns.forEach(function (c) {
        let v = r[c.key];
        if (c.render) v = c.render(r);
        else if (c.link && v) v = link(v, opts.linkLabels && opts.linkLabels[c.key] ? opts.linkLabels[c.key] : v);
        html += "<td>" + v + "</td>";
      });
      html += "</tr>";
    });
    html += "</tbody></table></div>";
    el.innerHTML = html;
  }

  function renderProducts() {
    renderTable(
      "productsTable",
      [
        { key: "shortCode", label: "Provided link code" },
        { key: "asin", label: "Destination ASIN" },
        { key: "brand", label: "Brand" },
        { key: "title", label: "Product title (verified on Amazon)" },
        { key: "category", label: "Category" },
        { key: "price", label: "Price", render: function (r) { return cell(r.price); } },
        { key: "rating", label: "Rating", render: function (r) { return cell(r.rating); } },
        { key: "reviewCount", label: "Reviews", render: function (r) { return cell(r.reviewCount); } },
        { key: "availability", label: "Availability", render: function (r) { return cell(r.availability); } },
        { key: "source", label: "Source", link: true, linkLabels: {} },
      ],
      PRODUCTS
    );
  }

  function renderLinkResolutions() {
    renderTable(
      "linkResolutionsTable",
      [
        { key: "submittedLink", label: "Supplied link", render: function (r) { return link(r.submittedLink, r.token); } },
        { key: "tokenLength", label: "Code length vs ASIN" },
        { key: "dpResult", label: "amazon.com/dp/&lt;code&gt;" },
        {
          key: "resolvedAsin",
          label: "Resolves to (ASIN)",
          render: function (r) { return link("https://www.amazon.com/dp/" + r.resolvedAsin, r.resolvedAsin); },
        },
        { key: "resolvedTitle", label: "Destination title (read from the live product page)" },
        { key: "categoryPath", label: "Category path" },
        { key: "identity", label: "Identity status" },
        {
          key: "evidence",
          label: "Evidence",
          render: function (r) {
            return r.evidence
              .map(function (u) { return link(u, u.replace("https://", "").replace("www.amazon.com", "amazon.com")); })
              .join("<br>");
          },
        },
      ],
      LINK_RESOLUTIONS
    );
  }

  function renderCategoryBands() {
    renderTable(
      "categoryBandsTable",
      [
        { key: "band", label: "Band" },
        { key: "categories", label: "Categories in the published band" },
        { key: "rate", label: "Published fixed rate" },
        {
          key: "products",
          label: "Verified products in this band",
          render: function (r) {
            if (!r.products) return '<span class="blank">\u2014 none verified \u2014</span>';
            return link(r.productSource, r.products);
          },
        },
        { key: "note", label: "Commercial reading" },
        { key: "subpage", label: "Detail page", render: function (r) { return link(r.subpage, "Open"); } },
        { key: "source", label: "Official source", render: function (r) { return link(ASIN_SOURCE.rateCard, "Rate card"); } },
      ],
      CATEGORY_BANDS
    );
  }

  function renderSpecs() {
    const el = document.getElementById("specsTable");
    if (!el) return;
    const prodName = {};
    PRODUCTS.forEach(function (p) { prodName[p.id] = p.brand + " · " + p.asin; });
    renderTable(
      "specsTable",
      [
        { key: "pid", label: "Product", render: function (r) { return esc(prodName[r.pid] || r.pid); } },
        { key: "attribute", label: "Attribute" },
        { key: "value", label: "Value" },
        { key: "status", label: "Status", render: function (r) { return badge(r.status); } },
        { key: "source", label: "Official source", render: function (r) { return sourceCell(r.source, r.sourceLabel); } },
      ],
      SPECS
    );
  }

  function renderExecFacts() {
    renderTable(
      "execFactsTable",
      [
        { key: "label", label: "Item" },
        { key: "value", label: "Verified detail" },
        { key: "source", label: "Official source", link: true },
      ],
      EXEC_FACTS
    );
  }

  function renderNiche() {
    renderTable(
      "nicheTable",
      [
        { key: "item", label: "Analysis area" },
        { key: "finding", label: "Finding" },
        { key: "detail", label: "Detail / basis" },
        { key: "status", label: "Status", render: function (r) { return badge(r.status); } },
        { key: "source", label: "Source", link: true },
      ],
      NICHE_ANALYSIS
    );
  }

  function renderCommission() {
    renderTable(
      "commissionTable",
      [
        { key: "item", label: "Item" },
        { key: "value", label: "Value", render: function (r) { return cell(r.value); } },
        { key: "note", label: "Note" },
        { key: "status", label: "Status", render: function (r) { return badge(r.status); } },
        { key: "source", label: "Source", link: true },
      ],
      COMMISSION_ROWS
    );
  }

  function renderCompliance() {
    renderTable(
      "complianceTable",
      [
        { key: "requirement", label: "Requirement" },
        { key: "detail", label: "Verified rule" },
        { key: "ref", label: "Reference" },
        { key: "source", label: "Official source", link: true },
      ],
      COMPLIANCE_ROWS
    );
  }

  function renderContent() {
    renderTable(
      "contentTable",
      [
        { key: "content", label: "Content type" },
        { key: "target", label: "Target product / topic" },
        { key: "format", label: "Format" },
        { key: "status", label: "Status" },
        { key: "source", label: "Product source", link: true },
      ],
      CONTENT_ROWS
    );
  }

  function renderTracking() {
    renderTable(
      "trackingTable",
      [
        { key: "campaign", label: "Campaign" },
        { key: "product", label: "Products" },
        { key: "linkType", label: "Link / tracking setup" },
        { key: "status", label: "Status" },
        { key: "source", label: "Source", link: true },
      ],
      TRACKING_ROWS
    );
  }

  function renderFlagged() {
    renderTable(
      "flaggedTable",
      [
        { key: "item", label: "Flagged item" },
        { key: "detail", label: "Details" },
        { key: "source", label: "Source", render: function (r) { return sourceCell(r.source, r.sourceLabel); } },
      ],
      FLAGGED_ROWS
    );
  }

  function renderFeatures() {
    const el = document.getElementById("featuresGrid");
    if (!el) return;
    el.innerHTML = PLATFORM_FEATURES.map(function (f) {
      return '<div class="feature"><h4>' + esc(f.name) + "</h4><p>" + esc(f.desc) + "</p></div>";
    }).join("");
  }

  function renderProductOverview() {
    const el = document.getElementById("productOverview");
    if (!el) return;
    el.innerHTML = PRODUCTS.map(function (p) {
      return (
        '<div class="card"><h3>' + esc(p.brand) + "</h3>" +
        "<p><strong>ASIN:</strong> " + esc(p.asin) + " · <strong>Category:</strong> " + esc(p.category) + "</p>" +
        "<p>" + esc(p.title) + "</p>" +
        '<p>' + link(p.source, "View on Amazon") + " · " + link(p.shortLink, "Provided short link") + "</p></div>"
      );
    }).join("");
  }

  document.addEventListener("DOMContentLoaded", function () {
    renderProducts();
    renderLinkResolutions();
    renderCategoryBands();
    renderSpecs();
    renderExecFacts();
    renderNiche();
    renderCommission();
    renderCompliance();
    renderContent();
    renderTracking();
    renderFlagged();
    renderFeatures();
    renderProductOverview();
  });
})();
