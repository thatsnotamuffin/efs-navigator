// Simple animation manager for fade and slide effects
export default class AnimationManager {
  static fadeIn(element, duration = 300) {
    if (!element) return;
    element.style.opacity = 0;
    element.style.display = "block";

    let last = +new Date();
    const tick = function () {
      const now = +new Date();
      element.style.opacity = +element.style.opacity + (now - last) / duration;
      last = now;

      if (+element.style.opacity < 1) {
        window.requestAnimationFrame(tick);
      }
    };
    tick();
  }

  static fadeOut(element, duration = 300) {
    if (!element) return;
    element.style.opacity = 1;

    let last = +new Date();
    const tick = function () {
      const now = +new Date();
      element.style.opacity -= (now - last) / duration;
      last = now;

      if (+element.style.opacity > 0) {
        window.requestAnimationFrame(tick);
      } else {
        element.style.display = "none";
      }
    };
    tick();
  }

  static slideDown(element, duration = 300) {
    if (!element) return;
    element.style.maxHeight = "0px";
    element.style.display = "block";
    element.style.overflow = "hidden";

    const totalHeight = element.scrollHeight;
    let start = null;

    function animateSlideDown(timestamp) {
      if (!start) start = timestamp;
      const progress = timestamp - start;
      const height = Math.min((progress / duration) * totalHeight, totalHeight);
      element.style.maxHeight = `${height}px`;

      if (progress < duration) {
        window.requestAnimationFrame(animateSlideDown);
      } else {
        element.style.maxHeight = "";
      }
    }

    window.requestAnimationFrame(animateSlideDown);
  }

  static slideUp(element, duration = 300) {
    if (!element) return;
    const totalHeight = element.scrollHeight;
    element.style.maxHeight = `${totalHeight}px`;
    element.style.overflow = "hidden";

    let start = null;

    function animateSlideUp(timestamp) {
      if (!start) start = timestamp;
      const progress = timestamp - start;
      const height = Math.max(totalHeight - (progress / duration) * totalHeight, 0);
      element.style.maxHeight = `${height}px`;

      if (progress < duration) {
        window.requestAnimationFrame(animateSlideUp);
      } else {
        element.style.display = "none";
        element.style.maxHeight = "";
      }
    }

    window.requestAnimationFrame(animateSlideUp);
  }
}
