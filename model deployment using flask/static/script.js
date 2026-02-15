function toggleNotifications() {
    const dropdown = document.getElementById("notificationDropdown");
    dropdown.classList.toggle("show");
}

function toggleSidebar() {
    document.getElementById("sidebar").classList.toggle("collapsed");
}

function toggleTheme() {
    document.body.classList.toggle("light-mode");
}

function showLoader() {
    document.getElementById("loader").classList.remove("hidden");
}

function clearNotifications() {
    alert("Notifications cleared (demo)");
}

function updateClock() {
    const clock = document.getElementById("clock");
    const now = new Date();
    clock.innerText = now.toLocaleTimeString();
}
setInterval(updateClock, 1000);

document.addEventListener("DOMContentLoaded", () => {
    updateClock();

    const counters = document.querySelectorAll('.counter');
    counters.forEach(counter => {
        const updateCount = () => {
            const target = +counter.getAttribute('data-target');
            const count = +counter.innerText;
            const increment = target / 50;

            if (count < target) {
                counter.innerText = Math.ceil(count + increment);
                setTimeout(updateCount, 20);
            } else {
                counter.innerText = target;
            }
        };
        updateCount();
    });
});
