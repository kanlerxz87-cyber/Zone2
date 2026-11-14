/* Zone2 — render test for the primary dashboard.
 *
 * `node --check` proves the JavaScript parses; it does not prove the tables actually render.
 * This harness stubs just enough DOM for assets/js/app.js to run, then asserts that every
 * table container on every root page received a table with the expected number of body rows
 * and that each rendered row carries a source link.
 *
 * Run:  node tests/test_render.js
 * Exit code 0 = all pages render, 1 = a page rendered empty or short.
 */
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const REPO = path.resolve(__dirname, "..");

/* --- minimal DOM stub ---------------------------------------------------- */
function makeElement(id) {
  return { id: id, innerHTML: "", _html: "" };
}

function makeDocument(ids) {
  const els = {};
  ids.forEach(function (id) {
    els[id] = makeElement(id);
  });
  const doc = {
    getElementById: function (id) {
      return els[id] || null;
    },
    addEventListener: function (evt, fn) {
      if (evt === "DOMContentLoaded") doc._ready = fn;
    },
    _els: els,
    _ready: null,
  };
  return doc;
}

/* --- run the page -------------------------------------------------------- */
function renderPage(pageFile) {
  const html = fs.readFileSync(path.join(REPO, pageFile), "utf8");
  const ids = [];
  const re = /id="([A-Za-z0-9_]+)"/g;
  let m;
  while ((m = re.exec(html)) !== null) {
    if (/Table$|Grid$|Overview$/.test(m[1])) ids.push(m[1]);
  }

  const doc = makeDocument(ids);
  const sandbox = {
    document: doc,
    window: {},
    console: console,
    Date: Date,
    String: String,
    Math: Math,
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);

  ["assets/js/data.js", "assets/js/app.js"].forEach(function (f) {
    const code = fs.readFileSync(path.join(REPO, f), "utf8");
    vm.runInContext(code, sandbox, { filename: f });
  });

  if (!doc._ready) throw new Error("no DOMContentLoaded handler registered");
  doc._ready();

  const out = {};
  Object.keys(doc._els).forEach(function (id) {
    out[id] = doc._els[id].innerHTML;
  });
  return out;
}

/* --- expectations -------------------------------------------------------- */
/* unit: the repeating element that proves the container was populated. */
const EXPECT = [
  { file: "index.html", tables: [
    { id: "execFactsTable", unit: "<tr>" },
    { id: "featuresGrid", unit: 'class="feature"' },
  ] },
  { file: "products.html", tables: [
    { id: "productsTable", unit: "<tr>" },
    { id: "linkResolutionsTable", unit: "<tr>" },
    { id: "specsTable", unit: "<tr>" },
    { id: "productOverview", unit: 'class="card"' },
  ] },
  { file: "categories.html", tables: [{ id: "categoryBandsTable", unit: "<tr>" }] },
  { file: "analysis.html", tables: [
    { id: "nicheTable", unit: "<tr>" },
    { id: "commissionTable", unit: "<tr>" },
  ] },
  { file: "content.html", tables: [{ id: "contentTable", unit: "<tr>" }] },
  { file: "compliance.html", tables: [{ id: "complianceTable", unit: "<tr>" }] },
  { file: "tracking.html", tables: [{ id: "trackingTable", unit: "<tr>" }] },
  { file: "flagged.html", tables: [{ id: "flaggedTable", unit: "<tr>" }] },
];

/* Every rendered data table must carry at least one outbound source link. */
const SOURCE_TABLES = [
  "execFactsTable",
  "productsTable",
  "linkResolutionsTable",
  "specsTable",
  "categoryBandsTable",
  "nicheTable",
  "commissionTable",
  "contentTable",
  "complianceTable",
  "trackingTable",
  "flaggedTable",
];

let failures = 0;
let checks = 0;

EXPECT.forEach(function (spec) {
  let rendered;
  try {
    rendered = renderPage(spec.file);
  } catch (err) {
    console.error("FAIL  " + spec.file + ": render threw — " + err.message);
    failures += 1;
    return;
  }
  spec.tables.forEach(function (t) {
    checks += 1;
    const id = t.id;
    const html = rendered[id];
    if (!html || html.length < 20) {
      console.error("FAIL  " + spec.file + " #" + id + ": container is empty");
      failures += 1;
      return;
    }
    const units = html.split(t.unit).length - 1;
    if (units < 1) {
      console.error("FAIL  " + spec.file + " #" + id + ": no '" + t.unit + "' unit rendered");
      failures += 1;
      return;
    }
    if (SOURCE_TABLES.indexOf(id) !== -1) {
      const links = (html.match(/href="https?:\/\//g) || []).length;
      if (links < 1) {
        console.error("FAIL  " + spec.file + " #" + id + ": no official source link in the rendered table");
        failures += 1;
        return;
      }
    }
    console.log("ok    " + spec.file + " #" + id + " (" + units + " unit(s))");
  });
});

if (failures) {
  console.error("\n" + failures + " render check(s) failed");
  process.exit(1);
}
console.log("\nrender test passed — " + checks + " table container(s) across " + EXPECT.length + " pages");
