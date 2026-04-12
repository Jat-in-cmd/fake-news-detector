function toggleNotifications() {
    const dropdown = document.getElementById("notificationDropdown");
    if (dropdown) {
        dropdown.classList.toggle("show");
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    if (sidebar) {
        sidebar.classList.toggle("collapsed");
    }
}

function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.toggle("dark-mode");
    body.classList.toggle("light-mode", !isDark);
    localStorage.setItem("signaldesk-theme", isDark ? "dark" : "light");
}

function showLoader() {
    const loader = document.getElementById("loader");
    if (loader) {
        loader.classList.remove("hidden");
    }
}

function updateClock() {
    const clock = document.getElementById("clock");
    if (!clock) {
        return;
    }

    const now = new Date();
    clock.innerText = now.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
    });
}

function animateCounters() {
    const counters = document.querySelectorAll(".counter");

    counters.forEach((counter) => {
        const target = Number(counter.getAttribute("data-target")) || 0;
        let current = 0;
        const increment = Math.max(1, Math.ceil(target / 40));

        const updateCount = () => {
            current += increment;
            if (current >= target) {
                counter.innerText = target;
                return;
            }

            counter.innerText = current;
            window.requestAnimationFrame(updateCount);
        };

        updateCount();
    });
}

function hydrateConfidenceBars() {
    document.querySelectorAll(".confidence-fill").forEach((bar) => {
        const width = bar.dataset.width || 0;
        window.setTimeout(() => {
            bar.style.width = `${width}%`;
        }, 160);
    });
}

function syncCharacterCount() {
    const input = document.getElementById("newsInput");
    const count = document.getElementById("charCount");

    if (!input || !count) {
        return;
    }

    const update = () => {
        count.innerText = input.value.trim().length;
    };

    input.addEventListener("input", update);
    update();
}

document.addEventListener("click", (event) => {
    const dropdown = document.getElementById("notificationDropdown");
    const trigger = document.querySelector(".notification-btn");

    if (!dropdown || !trigger) {
        return;
    }

    if (!dropdown.contains(event.target) && !trigger.contains(event.target)) {
        dropdown.classList.remove("show");
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const storedTheme = localStorage.getItem("signaldesk-theme");
    if (storedTheme === "dark") {
        document.body.classList.add("dark-mode");
    } else {
        document.body.classList.add("light-mode");
    }

    if (window.innerWidth <= 860) {
        document.getElementById("sidebar")?.classList.add("collapsed");
    }

    updateClock();
    window.setInterval(updateClock, 1000);
    animateCounters();
    hydrateConfidenceBars();
    syncCharacterCount();
});
