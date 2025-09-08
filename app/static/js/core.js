export function onReady(callback) {
  if (document.readyState !== "loading") {
    callback();
  } else {
    document.addEventListener("DOMContentLoaded", callback);
  }
}

export function flashClass(element, className, duration = 500) {
  if (!element) return;

  element.classList.add(className);
  setTimeout(() => {
    element.classList.remove(className);
  }, duration);
}
