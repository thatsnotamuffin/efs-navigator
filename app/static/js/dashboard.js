// Handles functionality for the dashboard/index page (mount search)
class DashboardManager {
  constructor() {
    this.initializeMountSearch();
  }

  // Initialize mount search functionality
  initializeMountSearch() {
    const searchInput = document.getElementById("search-input");
    const tableRows = document.querySelectorAll("tbody tr");

    if (!searchInput || !tableRows.length) {
      console.log("[dashboard] Search elements not found (not on dashboard page)");
      return;
    }

    const performSearch = (searchTerm) => {
      tableRows.forEach(row => {
        const mountId = row.cells[0].innerText.toLowerCase();
        row.style.display = mountId.includes(searchTerm) ? "" : "none";
      });
    };

    const clearSearch = () => {
      searchInput.value = "";
      performSearch("");
      console.log("[dashboard] Mount search cleared");
    };

    // Search on input
    searchInput.addEventListener("input", () => {
      const searchTerm = searchInput.value.toLowerCase();
      performSearch(searchTerm);
    });

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
      
      // Escape to clear search (only when search input is focused)
      if (e.key === 'Escape' && document.activeElement === searchInput) {
        clearSearch();
        searchInput.blur();
      }
    });

    console.log("[dashboard] Mount search initialized with Escape key support");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new DashboardManager();
});
