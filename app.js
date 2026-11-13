// Small progressive enhancement for the static research tables.
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-table-search]').forEach((input) => {
    const table = document.getElementById(input.dataset.tableSearch);
    if (!table) return;
    input.addEventListener('input', () => {
      const query = input.value.trim().toLocaleLowerCase();
      table.querySelectorAll('tbody tr').forEach((row) => {
        row.hidden = !row.textContent.toLocaleLowerCase().includes(query);
      });
    });
  });
});
