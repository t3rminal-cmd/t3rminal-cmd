document.documentElement.classList.add("js");

const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// ===== Mobile nav =====
const toggle = document.querySelector(".nav-toggle");
const menu = document.querySelector(".nav-menu");

function setMenu(open) {
  toggle.setAttribute("aria-expanded", String(open));
  menu.classList.toggle("open", open);
}

toggle.addEventListener("click", () => {
  setMenu(toggle.getAttribute("aria-expanded") !== "true");
});

// Close the menu after picking a link or pressing Escape
menu.addEventListener("click", (e) => {
  if (e.target.closest("a")) setMenu(false);
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") setMenu(false);
});

// ===== Typing effect =====
const typed = document.querySelector(".typed");
const lines = typed.dataset.lines.split("|");

if (reduceMotion) {
  typed.textContent = lines[lines.length - 1];
} else {
  let line = 0;
  let char = 0;
  let deleting = false;

  function tick() {
    // Array.from keeps emoji (surrogate pairs) intact while typing
    const current = Array.from(lines[line]);
    typed.textContent = current.slice(0, char).join("");

    if (!deleting && char < current.length) {
      char++;
      setTimeout(tick, 70);
    } else if (!deleting) {
      deleting = true;
      setTimeout(tick, 1600);
    } else if (char > 0) {
      char--;
      setTimeout(tick, 35);
    } else {
      deleting = false;
      line = (line + 1) % lines.length;
      setTimeout(tick, 300);
    }
  }

  tick();
}

// ===== Scroll reveal =====
const revealEls = document.querySelectorAll(".section");
revealEls.forEach((el) => el.classList.add("reveal"));

if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 }
  );
  revealEls.forEach((el) => observer.observe(el));
} else {
  revealEls.forEach((el) => el.classList.add("visible"));
}

// ===== Footer year =====
document.getElementById("year").textContent = new Date().getFullYear();
