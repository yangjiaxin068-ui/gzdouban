(function () {
    if (!window.gsap) {
        return;
    }

    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    gsap.defaults({ duration: 0.58, ease: "power3.out", overwrite: "auto" });
    document.documentElement.classList.add("gsap-ready");

    function all(selector) {
        return Array.prototype.slice.call(document.querySelectorAll(selector));
    }

    function animateNumbers(selector) {
        all(selector).forEach(function (node) {
            var rawText = node.textContent.trim();
            if (!/^\d+(\.\d+)?$/.test(rawText)) {
                return;
            }
            var target = Number(rawText);
            var decimals = rawText.indexOf(".") === -1 ? 0 : rawText.split(".")[1].length;
            var state = { value: 0 };
            gsap.to(state, {
                value: target,
                duration: reduceMotion ? 0 : 1.1,
                ease: "power2.out",
                onUpdate: function () {
                    node.textContent = state.value.toFixed(decimals);
                }
            });
        });
    }

    function bindHoverLift(selector) {
        if (reduceMotion) {
            return;
        }
        all(selector).forEach(function (node) {
            node.addEventListener("pointerenter", function () {
                gsap.to(node, { y: -5, scale: 1.004, duration: 0.24, ease: "power2.out" });
            });
            node.addEventListener("pointerleave", function () {
                gsap.to(node, { y: 0, scale: 1, duration: 0.28, ease: "power2.out" });
            });
        });
    }

    function bindNavMotion() {
        if (reduceMotion) {
            return;
        }
        all(".sb-sidenav .nav-link").forEach(function (link) {
            var icon = link.querySelector(".sb-nav-link-icon");
            link.addEventListener("pointerenter", function () {
                gsap.to(link, { x: 4, duration: 0.2, ease: "power2.out" });
                if (icon) {
                    gsap.to(icon, { scale: 1.12, duration: 0.2, ease: "power2.out" });
                }
            });
            link.addEventListener("pointerleave", function () {
                gsap.to(link, { x: 0, duration: 0.22, ease: "power2.out" });
                if (icon) {
                    gsap.to(icon, { scale: 1, duration: 0.22, ease: "power2.out" });
                }
            });
        });
    }

    function animateAppShell() {
        if (!document.querySelector(".app-shell")) {
            return;
        }

        if (reduceMotion) {
            gsap.set(".app-topbar, .app-sidebar, .workbench-hero, .page-head, .stat-card, .toolbar-card, .panel-card, .movie-result, .empty-state", { clearProps: "all" });
            return;
        }

        gsap.timeline({ defaults: { duration: 0.46, ease: "power3.out" } })
            .from(".app-topbar", { autoAlpha: 0, y: -14 }, 0)
            .from(".app-sidebar", { autoAlpha: 0, x: -24 }, 0.05)
            .from(".sidebar-head, .sb-sidenav .nav-link", {
                autoAlpha: 0,
                x: -14,
                stagger: 0.018
            }, 0.16)
            .from(".workbench-hero, .page-head", {
                autoAlpha: 0,
                y: 18
            }, 0.18)
            .from(".stat-card", {
                autoAlpha: 0,
                y: 18,
                scale: 0.986,
                stagger: 0.035
            }, 0.28)
            .from(".toolbar-card, .panel-card, .movie-result, .empty-state", {
                autoAlpha: 0,
                y: 16,
                scale: 0.99,
                stagger: 0.03
            }, 0.38);
    }

    function animateAuth() {
        if (!document.querySelector(".auth-shell")) {
            return;
        }

        if (reduceMotion) {
            return;
        }

        gsap.timeline({ defaults: { duration: 0.58, ease: "power3.out" } })
            .from(".auth-shell", { autoAlpha: 0, y: 22, scale: 0.985 })
            .from(".auth-visual .brand-mark, .auth-visual h1, .auth-visual p, .auth-metric-row span", {
                autoAlpha: 0,
                y: 18,
                stagger: 0.055
            }, "-=0.28")
            .from(".auth-card-head, .field-label, .auth-form .form-control, .auth-actions", {
                autoAlpha: 0,
                y: 14,
                stagger: 0.045
            }, "-=0.36");
    }

    function animateBigScreen() {
        if (!document.querySelector(".screen-body")) {
            return;
        }

        if (reduceMotion) {
            return;
        }

        gsap.timeline({ defaults: { duration: 0.5, ease: "power3.out" } })
            .from(".screen-header", { autoAlpha: 0, y: -18 }, 0)
            .from(".return-button, .screen-title span, .screen-title h1, .showTime", {
                autoAlpha: 0,
                y: -12,
                stagger: 0.04
            }, 0.1)
            .from(".metric-console article", {
                autoAlpha: 0,
                y: 18,
                stagger: 0.04
            }, 0.18)
            .from(".globe-panel", {
                autoAlpha: 0,
                scale: 0.965,
                duration: 0.7
            }, 0.22)
            .from(".globe-title, .globe-hud, .globe-rank li", {
                autoAlpha: 0,
                y: 14,
                stagger: 0.035
            }, 0.42)
            .from(".screen-card", {
                autoAlpha: 0,
                y: 20,
                scale: 0.986,
                stagger: { amount: 0.18, from: "center" }
            }, 0.26)
            .from(".process-strip article", {
                autoAlpha: 0,
                y: 12,
                stagger: 0.04
            }, 0.54);
    }

    function init() {
        animateAuth();
        animateAppShell();
        animateBigScreen();
        animateNumbers(".stat-value, .metric-console strong");
        bindNavMotion();
        bindHoverLift(".stat-card, .panel-card, .movie-result, .toolbar-card, .screen-card, .globe-panel");
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
