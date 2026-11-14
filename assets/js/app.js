/* Zone2 — render verified data into dashboard tables
 *
 * T23 (final integration): the renderer was rewritten to match the canonical dataset in
 * assets/js/data.js, whose product, specification, evidence and flag blocks are generated from
 * ledger/*.json by tools/build_root_data.py. The tables below are the reader-facing view of that
 * ledger: every row carries a link to the official source it was read from, and every value that
 * could not be confirmed from an official source renders as an explicit blank, never as a guess.
 */
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

  function badge(status) {
    if (status === "verified") return '<span class="badge ok">Verified</span>';
    if (status === "conflict") return '<span class="badge warn">Conflict</span>';
    if (status === "observed" || status === "OBSERVED" || status === "evidence" || status === "EVIDENCE_ONLY")
      return '<span class="badge ok">Observed</span>';
    if (status === "unverified") return '<span class="badge flag">Unverified</span>';
    if (status === "blocked") return '<span class="badge flag">Blocked</span>';
    if (status === "planned") return '<span class="badge warn">Planned</span>';
    return esc(status || "");
  }

  function severityBadge(sev) {
    if (sev === "high") return '<span class="badge flag">High</span>';
    if (sev === "medium") return '<span class="badge warn">Medium</span>';
    return '<span class="badge">Low</span>';
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

  function pidLabel(pid) {
    const found = PRODUCTS.filter(function (p) { return p.id === pid; })[0];
    if (!found) return esc(pid);
    return esc(found.brand + " " + found.resolvesToAsin + " · " + found.shortCode);
  }

  /* ---- the supplied links, exactly as supplied ------------------------------------------- */
  function renderProducts() {
    renderTable(
      "productsTable",
      [
        { key: "shortCode", label: "Provided link code" },
        { key: "codeLength", label: "Code length", render: function (r) { return r.codeLength + " chars (ASIN is 10)"; } },
        { key: "asinFormatValid", label: "Valid ASIN?", render: function (r) { return r.asinFormatValid ? "Yes" : "No"; } },
        { key: "canonicalDpResult", label: "amazon.com/dp/&lt;code&gt; result" },
        {
          key: "identityStatus",
          label: "Status of the token as supplied",
          render: function (r) { return badge("unverified"); },
        },
        { key: "source", label: "Source", link: true },
      ],
      PRODUCTS
    );
  }

  /* ---- what each supplied link resolves to ------------------------------------------------ */
  function renderResolved() {
    renderTable(
      "resolvedTable",
      [
        { key: "shortCode", label: "Provided link code" },
        {
          key: "resolvesToAsin",
          label: "Resolves to (ASIN)",
          render: function (r) { return link(r.resolvesToUrl, r.resolvesToAsin); },
        },
        { key: "brand", label: "Brand" },
        { key: "title", label: "Listing title as published on Amazon" },
        { key: "categoryPath", label: "Category path" },
        { key: "price", label: "Price", render: function (r) { return cell(r.price); } },
        { key: "rating", label: "Rating", render: function (r) { return cell(r.rating); } },
        { key: "reviewCount", label: "Reviews", render: function (r) { return cell(r.reviewCount); } },
        { key: "availability", label: "Availability", render: function (r) { return cell(r.availability); } },
        { key: "identityStatus", label: "Status", render: function (r) { return badge(r.identityStatus); } },
        { key: "source", label: "Source", link: true },
      ],
      PRODUCTS
    );
  }

  /* ---- verified specifications, one source link per row ----------------------------------- */
  function renderSpecs() {
    renderTable(
      "specsTable",
      [
        { key: "pid", label: "Product", render: function (r) { return pidLabel(r.pid); } },
        { key: "attribute", label: "Attribute" },
        {
          key: "value",
          label: "Value",
          render: function (r) {
            let v = cell(r.value);
            if (r.sourceLabel) v += '<div class="note" style="font-size:12px;color:var(--muted)">' + esc(r.sourceLabel) + "</div>";
            return v;
          },
        },
        { key: "status", label: "Status", render: function (r) { return badge(r.status); } },
        { key: "source", label: "Official source", link: true },
      ],
      SPECS
    );
  }

  /* ---- the resolution evidence and the controls that decide how to read it ---------------- */
  function renderResolution() {
    renderTable(
      "resolutionTable",
      [
        { key: "id", label: "ID" },
        { key: "observation", label: "Observation (reproducible by hand)" },
        { key: "interpretation", label: "What it shows" },
        { key: "status", label: "Status", render: function (r) { return badge(r.status); } },
        { key: "source", label: "Source", link: true },
      ],
      RESOLUTION_EVIDENCE
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
        { key: "status", label: "Status", render: function (r) { return badge(String(r.status).split(" ")[0].toLowerCase()); } },
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
        { key: "severity", label: "Severity", render: function (r) { return severityBadge(r.severity); } },
        { key: "detail", label: "What was found" },
        { key: "impact", label: "Why it matters" },
        { key: "actionRequired", label: "What is needed" },
        {
          key: "ledgerFlag",
          label: "Ledger flag",
          render: function (r) {
            if (!r.ledgerFlag) return cell(null);
            return '<a href="' + esc(r.ledgerUrl) + '">' + esc(r.ledgerFlag) + "</a>";
          },
        },
        { key: "source", label: "Source", link: true },
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
        '<div class="card"><h3>' + esc(p.brand) + " — " + esc(p.resolvesToAsin) + "</h3>" +
        "<p><strong>The product this link resolves to:</strong> " + esc(p.title) + "</p>" +
        "<p><strong>Provided code:</strong> " + esc(p.shortCode) + " (" + esc(p.codeLength) + " chars; an ASIN is 10, and <code>amazon.com/dp/&lt;code&gt;</code> returns " + esc(p.canonicalDpResult) + ") — " + badge("unverified") + " as a brief item, " + badge(p.identityStatus) + " as a link destination.</p>" +
        "<p><strong>Supplied short link:</strong> <code>" + esc(p.shortLink) + "</code> — cited, not embedded as a purchase link: Amazon's Program Policies treat an intermediate redirect that forwards the customer as a disqualifying link (research-hub compliance L3), so only the canonical destination is linked.</p>" +
        "<p>" + link(p.resolvesToUrl, "Amazon product page (canonical destination)") + " · " + link(p.canonicalDpUrl, "Canonical /dp/ lookup for the supplied code") + "</p></div>"
      );
    }).join("");
  }

  document.addEventListener("DOMContentLoaded", function () {
    // KPI strip: the flag count is derived, never typed, so it cannot drift from the data (F-17).
    // FLAGGED_ROWS is the reader-facing subset; the canonical register in ledger/flags.json is larger.
    // Show the canonical total so the dashboard cannot understate what pages/flags.html publishes.
    var fc = document.getElementById("flagCount");
    if (fc) fc.textContent = String(CANONICAL_FLAG_COUNT || FLAGGED_ROWS.length);

    renderProducts();
    renderResolved();
    renderSpecs();
    renderResolution();
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
