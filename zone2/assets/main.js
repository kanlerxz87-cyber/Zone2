// Zone2 — small UI helpers. No dependencies.
(function () {
  "use strict";

  // Mark the current nav link as active based on the current file.
  function markActiveNav() {
    var path = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll("nav.main a").forEach(function (a) {
      var target = a.getAttribute("href");
      if (target === path) {
        a.classList.add("active");
      }
    });
  }

  // Render the shared footer year.
  function stampYear() {
    var el = document.getElementById("year");
    if (el) el.textContent = new Date().getFullYear();
  }

  // Render a table from a data object. Rows must carry their own sources.
  function renderTable(id, opts) {
    var host = document.getElementById(id);
    if (!host || !opts.columns || !opts.rows) return;

    var html = "<div class=\"table-wrap\"><table><thead><tr>";
    opts.columns.forEach(function (c) { html += "<th>" + c + "</th>"; });
    html += "</tr></thead><tbody>";

    opts.rows.forEach(function (row) {
      html += "<tr>";
      opts.columns.forEach(function (c, i) {
        html += "<td>" + (row[c] != null ? row[c] : "") + "</td>";
      });
      html += "</tr>";
    });
    html += "</tbody></table></div>";
    host.innerHTML = html;
  }

  document.addEventListener("DOMContentLoaded", function () {
    markActiveNav();
    stampYear();
  });

  window.Zone2 = { renderTable: renderTable };
})();
