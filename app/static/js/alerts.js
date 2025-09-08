// Manages alert messages in the UI with animations and auto-dismissal
class AlertManager {
  constructor(containerId = "alert-container") {
    this.container = document.getElementById(containerId);
    if (!this.container) {
      this.container = document.createElement("div");
      this.container.id = containerId;
      this.container.className = "alert-container";
      document.body.appendChild(this.container);
    }
  }

  showAlert(message, type = "info", duration = 5000) {
    const alert = document.createElement("div");
    alert.classList.add("alert", `alert-${type}`, "slide-in");

    const icon = this.getIcon(type);
    alert.innerHTML = `
      <span class="alert-icon">${icon}</span>
      <span class="alert-message">${message}</span>
      <button class="alert-close" aria-label="Close alert">&times;</button>
    `;

    const alertId = `alert-${Date.now()}`;
    alert.id = alertId;
    this.container.appendChild(alert);

    // Close button listener
    alert.querySelector(".alert-close").addEventListener("click", () => {
      this.closeAlert(alertId);
    });

    // Auto-dismiss after duration
    if (duration > 0) {
      setTimeout(() => this.closeAlert(alertId), duration);
    }
  }

  showToast(message, type = "info", duration = 3000) {
    this.showAlert(message, type, duration);
  }

  closeAlert(alertId) {
    const alert = document.getElementById(alertId);
    if (alert) {
      alert.classList.remove("slide-in");
      alert.classList.add("slide-out");
      setTimeout(() => {
        alert.remove();
      }, 300);
    }
  }

  getIcon(type) {
    const icons = {
      success: '<i class="fas fa-check-circle"></i>',
      error: '<i class="fas fa-times-circle"></i>',
      warning: '<i class="fas fa-exclamation-triangle"></i>',
      info: '<i class="fas fa-info-circle"></i>'
    };
    return icons[type] || icons.info;
  }
}

export default AlertManager;

export const alertManager = new AlertManager();
