// Handles browsing and file navigation interactions
import AlertManager from "./alerts.js";
import AnimationManager from "./animations.js";

// Highlight the active file/folder
function setActiveRow(target) {
  document.querySelectorAll(".file-row").forEach((el) => el.classList.remove("active"));
  if (target.classList.contains("file-row")) {
    target.classList.add("active");
  } else {
    target.closest(".file-row")?.classList.add("active");
  }
}

// Navigate to file or folder
function handleFileClick(event) {
  const target = event.currentTarget;
  const isDirectory = target.dataset.type === "dir";
  const path = target.dataset.path;

  if (isDirectory) {
    window.location.href = `/browse/${path}`;
  } else {
    window.location.href = `/view/${path}`;
  }
}

// Hover effect
function handleHover(event) {
  const target = event.currentTarget;
  target.classList.toggle("hover", event.type === "mouseenter");
}

// Show toast on copy
async function handleCopyClick(event) {
  event.stopPropagation();

  const input = event.currentTarget.previousElementSibling;
  if (!input) return;

  try {
    await navigator.clipboard.writeText(input.value || input.textContent);
    AlertManager.showToast("Copied path to clipboard!", "success", 1500);
  } catch (err) {
    // Fallback for older browsers or when clipboard API fails
    console.warn("Clipboard API failed, trying fallback:", err);
    
    try {
      input.select();
      const success = document.execCommand("copy");
      if (success) {
        AlertManager.showToast("Copied path to clipboard!", "success", 1500);
      } else {
        throw new Error("execCommand failed");
      }
    } catch (fallbackErr) {
      console.error("Both clipboard methods failed:", fallbackErr);
      AlertManager.showToast("Failed to copy to clipboard", "error", 2000);
    }
  }
}

// Toggle path view
function setupPathToggle() {
  const toggleBtn = document.getElementById("toggle-paths");
  const allPaths = document.querySelectorAll(".file-path");

  toggleBtn?.addEventListener("click", () => {
    allPaths.forEach((el) => el.classList.toggle("visible"));
  });
}

function initFileBrowser() {
  const fileRows = document.querySelectorAll(".file-row");

  fileRows.forEach((row) => {
    row.addEventListener("click", handleFileClick);
    row.addEventListener("mouseenter", handleHover);
    row.addEventListener("mouseleave", handleHover);
  });

  document.querySelectorAll(".copy-btn").forEach((btn) => {
    btn.addEventListener("click", handleCopyClick);
  });

  setupPathToggle();
}

document.addEventListener("DOMContentLoaded", initFileBrowser);
