// Handles functionality for file viewing and metadata panel
import AlertManager, { alertManager } from "./alerts.js";
import AnimationManager from "./animations.js";

// Toggle file metadata panel
function toggleMetadataPanel() {
  const metadataPanel = document.getElementById("metadata-panel");
  const toggleButton = document.getElementById("toggle-metadata-btn");

  if (!metadataPanel || !toggleButton) return;

  metadataPanel.classList.toggle("visible");
  const isVisible = metadataPanel.classList.contains("visible");

  toggleButton.textContent = isVisible ? "Hide Metadata" : "Show Metadata";
  toggleButton.setAttribute("aria-expanded", isVisible);
}

// Fetch and display metadata
async function loadFileMetadata(filePath) {
  try {
    const response = await fetch(`/metadata/${filePath}`);
    if (!response.ok) throw new Error("Failed to fetch metadata");

    const data = await response.json();
    updateMetadataPanel(data);
  } catch (error) {
    alertManager.showToast("Failed to load metadata", "error", 2500);
    console.error("[metadata] Error loading file metadata:", error);
  }
}

// Update metadata panel content
function updateMetadataPanel(data) {
  document.getElementById("meta-name").textContent = data.name;
  document.getElementById("meta-size").textContent = `${data.size} bytes`;
  document.getElementById("meta-modified").textContent = new Date(data.modified * 1000).toLocaleString();
  document.getElementById("meta-type").textContent = data.is_dir ? "Directory" : "File";
  document.getElementById("meta-permissions").textContent = data.permissions;
}

// Copy code to clipboard
function copyCodeToClipboard() {
  const codeElement = document.querySelector('#code-block code');
  if (!codeElement) return;

  const text = codeElement.textContent;
  navigator.clipboard.writeText(text).then(() => {
    alertManager.showToast("Code copied to clipboard!", "success", 2000);
  }).catch((err) => {
    console.error('Failed to copy text: ', err);
    alertManager.showToast("Failed to copy code", "error", 2000);
  });
}

// Initialize file viewer interactions
function initFileViewer() {
  const toggleButton = document.getElementById("toggle-metadata-btn");
  const filePath = document.body.dataset.path;

  if (toggleButton) {
    toggleButton.addEventListener("click", toggleMetadataPanel);
  }

  if (filePath) {
    loadFileMetadata(filePath);
  }

  // Copy button functionality
  const copyButton = document.getElementById("copy-clipboard");
  if (copyButton) {
    copyButton.addEventListener("click", copyCodeToClipboard);
  }

  // === Word Wrap Support ===
  const wrapToggle = document.getElementById("wrap-toggle");
  const codeWrapper = document.querySelector(".code-wrap-container");

  if (wrapToggle && codeWrapper) {
    console.log("[wrap] Button and container found");

    // Set initial state
    let wrapEnabled = false;
    wrapToggle.setAttribute("aria-pressed", "false");

    wrapToggle.addEventListener("click", () => {
      wrapEnabled = !wrapEnabled;
      
      if (wrapEnabled) {
        codeWrapper.classList.add("wrap-enabled");
        wrapToggle.setAttribute("aria-pressed", "true");
        wrapToggle.innerHTML = '<i class="fas fa-align-left"></i> Wrap Off';
        console.log("[wrap] Word wrap enabled");
      } else {
        codeWrapper.classList.remove("wrap-enabled");
        wrapToggle.setAttribute("aria-pressed", "false");
        wrapToggle.innerHTML = '<i class="fas fa-align-center"></i> Word Wrap';
        console.log("[wrap] Word wrap disabled");
      }
    });

    // Keyboard shortcut for word wrap
    document.addEventListener("keydown", (e) => {
      // Only trigger if no modifier keys are pressed and we're not in an input
      if (e.key.toLowerCase() === "w" && 
          !e.ctrlKey && !e.metaKey && !e.altKey && !e.shiftKey &&
          !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
        e.preventDefault();
        console.log("[wrap] 'W' key pressed");
        wrapToggle.click();
      }
    });
  } else {
    // Only log if we're actually on a file viewer page
    const isFileViewerPage = document.body.dataset.page === "view" || 
                           document.querySelector('#code-block') !== null;
    if (isFileViewerPage) {
      console.warn("[wrap] Wrap toggle or code wrapper not found on file viewer page");
      console.log("[wrap] wrapToggle:", wrapToggle);
      console.log("[wrap] codeWrapper:", codeWrapper);
    }
  }

  // Keyboard shortcut for copy
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "c" && 
        !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
      const selection = window.getSelection();
      if (selection.toString().length === 0) {
        // No text selected, copy entire code block
        e.preventDefault();
        copyCodeToClipboard();
      }
    }
  });
}

document.addEventListener("DOMContentLoaded", initFileViewer);
