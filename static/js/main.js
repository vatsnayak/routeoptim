// ══════════════════════════════════════════
// RouteOptim — Modern UI Interactions
// ══════════════════════════════════════════

document.addEventListener('DOMContentLoaded', function () {

    // ── Initialize AOS (Animate on Scroll) ──
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 600,
            easing: 'ease-out-cubic',
            once: true,
            offset: 50,
        });
    }

    // ── Glass Navbar scroll effect ──
    const navbar = document.querySelector('.glass-nav');
    if (navbar) {
        window.addEventListener('scroll', function () {
            navbar.classList.toggle('scrolled', window.scrollY > 20);
        });
    }

    // ── Auto-dismiss toast notifications ──
    document.querySelectorAll('.toast').forEach(function (toast) {
        setTimeout(function () {
            toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(50px)';
            setTimeout(function () { toast.remove(); }, 400);
        }, 4000);
    });

    // ── Counter animation for stat values ──
    document.querySelectorAll('.stat-value').forEach(function (el) {
        const target = parseInt(el.textContent);
        if (isNaN(target)) return;

        const duration = 1000;
        const start = performance.now();
        el.textContent = '0';

        function update(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(target * eased);
            if (progress < 1) requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
    });

    // ── Stagger table row animations ──
    document.querySelectorAll('.table-modern tbody tr').forEach(function (row, i) {
        row.style.opacity = '0';
        row.style.transform = 'translateY(10px)';
        row.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        row.style.transitionDelay = (i * 0.05) + 's';
        setTimeout(function () {
            row.style.opacity = '1';
            row.style.transform = 'translateY(0)';
        }, 100);
    });

    // ── Active nav link highlighting ──
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-pill').forEach(function (link) {
        const href = link.getAttribute('href');
        if (href && currentPath.startsWith(href) && href !== '/') {
            link.style.color = 'var(--primary)';
            link.style.background = 'var(--primary-bg)';
        }
    });

    // ── Select all checkbox (optimize page) ──
    const checkboxes = document.querySelectorAll('.delivery-check-item input[type="checkbox"]');
    if (checkboxes.length > 0) {
        const container = checkboxes[0].closest('.mb-4');
        if (container) {
            const label = container.querySelector('.form-label');
            if (label) {
                const selectAll = document.createElement('button');
                selectAll.type = 'button';
                selectAll.className = 'btn btn-sm btn-outline-primary ms-2';
                selectAll.innerHTML = '<i class="bi bi-check-all me-1"></i>Select All';
                selectAll.addEventListener('click', function () {
                    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
                    checkboxes.forEach(cb => { cb.checked = !allChecked; });
                    selectAll.innerHTML = allChecked
                        ? '<i class="bi bi-check-all me-1"></i>Select All'
                        : '<i class="bi bi-x-lg me-1"></i>Deselect All';
                });
                label.appendChild(selectAll);
            }
        }
    }

    // ── Dark Mode Toggle ──
    const darkToggle = document.getElementById('darkModeToggle');
    const darkSwitch = document.getElementById('darkModeSwitch');
    if (darkToggle && darkSwitch) {
        darkToggle.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            darkSwitch.checked = !darkSwitch.checked;
            const isDark = darkSwitch.checked;

            // Update theme instantly
            document.documentElement.setAttribute('data-bs-theme', isDark ? 'dark' : 'light');

            // Persist to server
            fetch('/api/dark-mode/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
            });
        });
    }

    // ── Smooth page transitions ──
    document.querySelectorAll('a:not([target="_blank"]):not([href^="#"]):not([href^="javascript"])').forEach(function (link) {
        link.addEventListener('click', function (e) {
            const href = link.getAttribute('href');
            if (href && href.startsWith('/') && !e.ctrlKey && !e.metaKey) {
                e.preventDefault();
                document.body.style.opacity = '0.7';
                document.body.style.transition = 'opacity 0.15s ease';
                setTimeout(function () { window.location.href = href; }, 150);
            }
        });
    });

    // ── Fade in body on load ──
    document.body.style.opacity = '1';
    document.body.style.transition = 'opacity 0.3s ease';
});

// ── CSRF Cookie Helper ──
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
