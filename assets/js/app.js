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

  /* ---- T30 redesign: rich product cards on the landing page -----------------
   * Same PRODUCTS dataset as the tables — nothing new is stated, only presented
   * as cards. The Amazon listing link is marked rel="sponsored" per Google's
   * paid-link guidance (page carries the required disclosure). */
  function shopLink(url, label) {
    return '<a href="' + esc(url) + '" target="_blank" rel="sponsored noopener noreferrer">' + esc(label) + "</a>";
  }

  function renderProductCards() {
    const el = document.getElementById("productCards");
    if (!el) return;
    el.innerHTML = PRODUCTS.map(function (p) {
      return (
        '<div class="product-card">' +
        '<div class="product-brand-row"><span class="product-brand">' + esc(p.brand) + '</span><span class="asin-chip">' + esc(p.resolvesToAsin) + "</span></div>" +
        '<div class="product-title">' + esc(p.title) + "</div>" +
        '<div class="product-meta">' +
        '<div class="row"><span class="k">Category path</span><span class="v">' + esc(p.categoryPath) + "</span></div>" +
        '<div class="row"><span class="k">Price</span><span class="v">' + cell(p.price) + "</span></div>" +
        '<div class="row"><span class="k">Rating</span><span class="v">' + cell(p.rating) + "</span></div>" +
        '<div class="row"><span class="k">Availability</span><span class="v">' + cell(p.availability) + "</span></div>" +
        '<div class="row"><span class="k">Code as supplied</span><span class="v"><code>' + esc(p.shortCode) + "</code> · " + esc(p.codeLength) + " chars — " + badge("unverified") + "</span></div>" +
        '<div class="row"><span class="k">As a link destination</span><span class="v">' + badge(p.identityStatus) + "</span></div>" +
        "</div>" +
        '<div class="product-actions">' +
        shopLink(p.resolvesToUrl, "Open the listing — official source") +
        '<a class="btn btn-outline btn-sm" href="products.html">Full evidence &amp; specs</a>' +
        "</div>" +
        "</div>"
      );
    }).join("");
  }

  /* ---- T30 redesign: compact flagged preview for the landing page -----------
   * Rendered from FLAGGED_ROWS (the reader-facing subset) so the landing can
   * never disagree with the flagged page. */
  function renderFlagPreview() {
    const el = document.getElementById("flagPreview");
    if (!el) return;
    const rows = FLAGGED_ROWS.slice(0, 9);
    let html = '<div class="table-wrap"><table><thead><tr><th>Flag</th><th>Severity</th><th>What was found</th><th>Owner action</th></tr></thead><tbody>';
    rows.forEach(function (r) {
      html += "<tr>";
      html += "<td>" + (r.ledgerFlag ? '<a href="' + esc(r.ledgerUrl) + '">' + esc(r.ledgerFlag) + "</a>" : cell(null)) + "</td>";
      html += "<td>" + severityBadge(r.severity) + "</td>";
      html += "<td>" + esc(r.detail) + "</td>";
      html += "<td>" + esc(r.actionRequired) + "</td>";
      html += "</tr>";
    });
    html += "</tbody></table></div>";
    el.innerHTML = html;
  }

  /* ---- T31: editorial topic ideas — suggestions, not published claims -------
   * Every factual anchor in a topic is verified on the official page linked in
   * its row (re-fetched 2026-11-15, see docs/verification-2b257b2e.md). Demand
   * metrics (search volume, trend slope, difficulty) are NOT known from any
   * official source, so the demand column stays blank — never estimated. A
   * topic is drafted only for the decision board; nothing is published until
   * the owner records a choice on pages/suggestions.html. */
  const TOPIC_IDEAS = [
    {
      id: "T-01",
      topic: "Dual-basket vs single-basket air fryers: when two baskets actually beat one big one",
      format: "Comparison",
      intent: "Commercial investigation",
      demand: null,
      anchors: "Chefman 6 Qt dual basket (B0CDY277D3) vs Chefman 8 Qt TurboFry (B08DKYBTPH)",
      status: "suggestion",
      source: "https://www.amazon.com/dp/B0CDY277D3",
      sourceLabel: "Amazon listing — B0CDY277D3 (title: dual basket, 2 independent baskets)",
    },
    {
      id: "T-02",
      topic: "Sync-finish cooking explained: how two dishes finish at the same time",
      format: "Feature explainer",
      intent: "Informational → product",
      demand: null,
      anchors: "Chefman 6 Qt dual basket — 'Sync Finish' is stated in the listing title",
      status: "suggestion",
      source: "https://www.amazon.com/dp/B0CDY277D3",
      sourceLabel: "Amazon listing — B0CDY277D3",
    },
    {
      id: "T-03",
      topic: "The 450°F Hi-Fry setting: what extra heat does to frozen food",
      format: "Feature explainer",
      intent: "Informational → product",
      demand: null,
      anchors: "Chefman 8 Qt TurboFry — '450°F Hi-Fry Option' is stated in the listing title",
      status: "suggestion",
      source: "https://www.amazon.com/dp/B08DKYBTPH",
      sourceLabel: "Amazon listing — B08DKYBTPH",
    },
    {
      id: "T-04",
      topic: "26-quart French-door oven vs countertop air fryer: which one replaces your toaster?",
      format: "Buying guide",
      intent: "Commercial investigation",
      demand: null,
      anchors: "Emeril Lagasse 26QT French Door multi-function oven (B09B7SB46R)",
      status: "suggestion",
      source: "https://www.amazon.com/dp/B09B7SB46R",
      sourceLabel: "Amazon listing — B09B7SB46R",
    },
    {
      id: "T-05",
      topic: "Preset buttons demystified: getting real results from one-touch modes",
      format: "Evergreen educational",
      intent: "Informational",
      demand: null,
      anchors: "Emeril Lagasse 26QT — '24 One-Touch Preset Options' is stated in the listing title",
      status: "suggestion",
      source: "https://www.amazon.com/dp/B09B7SB46R",
      sourceLabel: "Amazon listing — B09B7SB46R",
    },
    {
      id: "T-06",
      topic: "Sizing an air fryer to your household: quarts, servings and counter space",
      format: "Buying guide",
      intent: "Commercial investigation",
      demand: null,
      anchors: "All three resolved listings (6 Qt dual basket · 8 Qt TurboFry · 26 QT oven)",
      status: "suggestion",
      source: "https://www.amazon.com/dp/B08DKYBTPH",
      sourceLabel: "Amazon listing — B08DKYBTPH (8 Qt capacity in title)",
    },
    {
      id: "T-07",
      topic: "Air-fryer windows: why seeing your food changes how you cook",
      format: "Feature explainer",
      intent: "Informational → product",
      demand: null,
      anchors: "Chefman 6 Qt dual basket — 'Easy View Windows' is stated in the listing title",
      status: "suggestion",
      source: "https://www.amazon.com/dp/B0CDY277D3",
      sourceLabel: "Amazon listing — B0CDY277D3",
    },
    {
      id: "T-08",
      topic: "What you may and may not say when you earn from Amazon links",
      format: "Compliance explainer",
      intent: "Trust-building editorial",
      demand: null,
      anchors: "Operating Agreement §5 disclosure; display rules in the Program Policies",
      status: "suggestion",
      source: "https://affiliate-program.amazon.com/help/operating/agreement",
      sourceLabel: "Associates Program Operating Agreement",
    },
  ];

  function renderTopics() {
    const el = document.getElementById("topicsTable");
    if (!el) return;
    let html = '<div class="table-wrap"><table><thead><tr><th>ID</th><th>Topic idea</th><th>Format</th><th>Reader intent</th><th>Search demand</th><th>Factual anchor (verified)</th><th>Status</th><th>Official source</th></tr></thead><tbody>';
    TOPIC_IDEAS.forEach(function (t) {
      html += "<tr>";
      html += "<td>" + esc(t.id) + "</td>";
      html += "<td><strong>" + esc(t.topic) + "</strong></td>";
      html += "<td>" + esc(t.format) + "</td>";
      html += "<td>" + esc(t.intent) + "</td>";
      html += "<td>" + cell(t.demand) + "</td>";
      html += "<td>" + esc(t.anchors) + "</td>";
      html += '<td><span class="badge warn">Suggestion</span></td>';
      html += '<td><a href="' + esc(t.source) + '" target="_blank" rel="noopener noreferrer">' + esc(t.sourceLabel) + "</a></td>";
      html += "</tr>";
    });
    html += "</tbody></table></div>";
    el.innerHTML = html;
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
    var canonical = CANONICAL_FLAG_COUNT || FLAGGED_ROWS.length;
    if (fc) fc.textContent = String(canonical);

    // T26 (F-17 / F-26 class): these three captions used to hard-code "26 items" in the
    // HTML, so they drifted the moment a flag was added — the exact defect F-26 closed for
    // the KPI. Derive them from the same generated constant so the prose cannot disagree
    // with the register it describes.
    var reg = document.getElementById("flagRegisterCount");
    if (reg) reg.textContent = String(canonical);
    var regMax = document.getElementById("flagRegisterMax");
    if (regMax) regMax.textContent = String(canonical);
    var heading = document.getElementById("flagCountHeading");
    if (heading) heading.textContent = String(canonical);
    Array.prototype.forEach.call(document.querySelectorAll(".flag-count-inline"), function (el) {
      el.textContent = String(canonical);
    });

    // NOTE (session ba8b2d38, T27): this session independently made the same fix as T26 above and
    // wired a second handler to #flagRegisterRange. The T26 block above is kept as the single
    // implementation — it already fills #flagRegisterCount and #flagRegisterMax, which is what
    // flagged.html now renders — so the duplicate was removed rather than left as dead code.
    // T27's contribution here is instead the gate that stops a typed count reappearing in the
    // generated subpages and the hand-written docs: tools/validate_data.py::check_no_typed_flag_counts.

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
    renderProductCards();
    renderFlagPreview();
    renderTopics();
  });
})();
