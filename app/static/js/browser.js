// Handles functionality for the browse page (search and grid view toggle)
class BrowserManager {
  constructor() {
    this.initializeSearch();
    this.initializeGridToggle();
    this.initializeGridCardClicks();
  }


  // Initialize file search functionality
  initializeSearch() {
    const searchInput = document.getElementById("file-search-input");
    if (!searchInput) return;

    // Get all file rows from both table and grid views
    const tableRows = document.querySelectorAll("#table-view .file-row");
    const gridCards = document.querySelectorAll("#grid-view .file-card");

    const performSearch = (searchTerm) => {
      // Filter table view rows
      tableRows.forEach(row => {
        const fileName = row.querySelector("td:first-child").innerText.toLowerCase();
        row.style.display = fileName.includes(searchTerm) ? "" : "none";
      });
      
      // Filter grid view cards
      gridCards.forEach(card => {
        const fileName = card.innerText.toLowerCase();
        card.style.display = fileName.includes(searchTerm) ? "" : "none";
      });
    };

    const clearSearch = () => {
      searchInput.value = "";
      performSearch("");
      console.log("[browser] Search cleared");
    };

    searchInput.addEventListener("input", () => {
      const searchTerm = searchInput.value.toLowerCase();
      performSearch(searchTerm);
    });

    // Add keyboard shortcuts for search
    document.addEventListener("keydown", (e) => {
      // Ctrl+F or Cmd+F to focus search
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

    console.log("[browser] Search functionality initialized with Escape key support");
  }


  // Initialize grid view toggle functionality
  initializeGridToggle() {
    const viewToggle = document.getElementById("view-toggle");
    const tableView = document.getElementById("table-view");
    const gridView = document.getElementById("grid-view");

    if (!viewToggle || !tableView || !gridView) {
      console.log("[browser] Grid toggle elements not found (not on browse page)");
      return;
    }

    // Get saved preference from localStorage (defaults to false for table view)
    let isGridView = localStorage.getItem('browserViewMode') === 'grid';
    console.log("[browser] Loaded view preference:", localStorage.getItem('browserViewMode'), "-> isGridView:", isGridView);

    // Apply initial view state
    this.setViewMode(viewToggle, tableView, gridView, isGridView);

    viewToggle.addEventListener("click", () => {
      isGridView = !isGridView;
      
      // Save preference to localStorage
      const newMode = isGridView ? 'grid' : 'table';
      localStorage.setItem('browserViewMode', newMode);
      console.log("[browser] Saved view preference:", newMode);
      
      // Apply the view change
      this.setViewMode(viewToggle, tableView, gridView, isGridView);
      
      console.log(`[browser] Switched to ${isGridView ? 'grid' : 'table'} view`);
    });

    console.log(`[browser] Grid toggle functionality initialized (initial mode: ${isGridView ? 'grid' : 'table'})`);
  }

  // Set the view mode (grid or table) and update UI accordingly
  setViewMode(viewToggle, tableView, gridView, isGridView) {
    if (isGridView) {
      // Switch to grid view
      tableView.style.display = "none";
      gridView.style.display = "grid";
      viewToggle.innerHTML = '<i class="fas fa-list"></i> Table View';
      viewToggle.title = "Switch to table view";
      viewToggle.setAttribute("aria-pressed", "true");
    } else {
      // Switch to table view
      tableView.style.display = "block";
      gridView.style.display = "none";
      viewToggle.innerHTML = '<i class="fas fa-th-large"></i> Grid View';
      viewToggle.title = "Switch to grid view";
      viewToggle.setAttribute("aria-pressed", "false");
    }
  }

  
  // Initialize clickable grid cards for directories and files   
  initializeGridCardClicks() {
    const gridCards = document.querySelectorAll("#grid-view .file-card");
    
    if (!gridCards.length) {
      console.log("[browser] No grid cards found");
      return;
    }

    gridCards.forEach(card => {
      // Check if this card represents a directory or file
      const directoryLink = card.querySelector('a.directory-link');
      const viewButton = card.querySelector('a.view-btn');
      const downloadButton = card.querySelector('a[href*="/download/"]');
      
      if (directoryLink) {
        this.makeCardClickable(card, directoryLink.href, 'directory');
      } else if (viewButton) {
        this.makeCardClickable(card, viewButton.href, 'file-view');
      } else if (downloadButton) {
        this.makeCardClickable(card, downloadButton.href, 'file-download');
      }
    });

    console.log("[browser] Grid card click functionality initialized");
  }

  // Make a grid card clickable with proper styling and behavior
  makeCardClickable(card, url, type) {
    card.style.cursor = 'pointer';
    card.setAttribute('title', this.getCardTitle(type));
    
    card.addEventListener('click', (e) => {
      if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON' || e.target.closest('a, button')) {
        return;
      }
      
      if (type === 'file-download') {
        const link = document.createElement('a');
        link.href = url;
        link.download = '';
        link.click();
        console.log("[browser] Grid card download triggered:", url);
      } else {
        window.location.href = url;
        console.log("[browser] Grid card navigation triggered:", url);
      }
    });

    card.addEventListener('mouseenter', () => {
      card.style.transform = 'translateY(-4px)';
    });
    
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'translateY(-2px)';
    });
  }

  getCardTitle(type) {
    switch (type) {
      case 'directory':
        return 'Click to open directory';
      case 'file-view':
        return 'Click to view file';
      case 'file-download':
        return 'Click to download file';
      default:
        return 'Click to open';
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new BrowserManager();
});
