(function () {
    if (!window.gsap) {
        return;
    }

    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    gsap.defaults({ duration: 0.64, ease: "power3.out", overwrite: "auto" });
    document.documentElement.classList.add("gsap-ready");

    function selectAll(selector) {
        return Array.prototype.slice.call(document.querySelectorAll(selector));
    }

    function animateNumbers() {
        selectAll(".stat-value").forEach(function (node) {
            var rawText = node.textContent.trim();
            if (!/^\d+(\.\d+)?$/.test(rawText)) {
                return;
            }
            var target = Number(rawText);
            var decimals = rawText.indexOf(".") === -1 ? 0 : rawText.split(".")[1].length;
            var state = { value: 0 };
            gsap.to(state, {
                value: target,
                duration: reduceMotion ? 0 : 1.15,
                ease: "power2.out",
                onUpdate: function () {
                    node.textContent = state.value.toFixed(decimals);
                }
            });
        });
    }

    function bindHoverLift(selector) {
        selectAll(selector).forEach(function (node) {
            node.addEventListener("pointerenter", function () {
                gsap.to(node, {
                    y: -5,
                    scale: 1.006,
                    duration: 0.28,
                    ease: "power2.out"
                });
            });
            node.addEventListener("pointerleave", function () {
                gsap.to(node, {
                    y: 0,
                    scale: 1,
                    duration: 0.32,
                    ease: "power2.out"
                });
            });
        });
    }

    function bindNavMotion() {
        selectAll(".sb-sidenav .nav-link").forEach(function (link) {
            var icon = link.querySelector(".sb-nav-link-icon");
            link.addEventListener("pointerenter", function () {
                gsap.to(link, { x: 3, duration: 0.22, ease: "power2.out" });
                if (icon) {
                    gsap.to(icon, { scale: 1.12, duration: 0.22, ease: "power2.out" });
                }
            });
            link.addEventListener("pointerleave", function () {
                gsap.to(link, { x: 0, duration: 0.24, ease: "power2.out" });
                if (icon) {
                    gsap.to(icon, { scale: 1, duration: 0.24, ease: "power2.out" });
                }
            });
        });
    }

    function animateAppShell() {
        if (reduceMotion) {
            gsap.set(".sb-topnav, .sb-sidenav .nav-link, .page-kicker, .page-title, .page-subtitle, .stat-card, .toolbar-card, .card, .movie-result, .empty-state, .wordcloud-stage img", {
                clearProps: "all"
            });
            return;
        }

        gsap.timeline()
            .from(".sb-topnav", { autoAlpha: 0, y: -12, duration: 0.36 }, 0)
            .from(".sb-sidenav .nav-link", {
                autoAlpha: 0,
                x: -14,
                duration: 0.34,
                stagger: 0.014
            }, 0.05)
            .from(".page-kicker, .page-title, .page-subtitle", {
                autoAlpha: 0,
                y: 12,
                duration: 0.38,
                stagger: 0.035
            }, 0.12)
            .from(".stat-card", {
                autoAlpha: 0,
                y: 18,
                scale: 0.985,
                duration: 0.42,
                stagger: 0.028
            }, 0.22)
            .from(".toolbar-card, .card, .movie-result, .empty-state", {
                autoAlpha: 0,
                y: 16,
                scale: 0.99,
                duration: 0.42,
                stagger: 0.026
            }, 0.34)
            .from(".wordcloud-stage img", {
                autoAlpha: 0,
                y: 12,
                scale: 0.96,
                duration: 0.42
            }, 0.44);
    }

    function animateAuth() {
        if (!document.querySelector(".auth-card")) {
            return;
        }

        if (reduceMotion) {
            return;
        }

        gsap.timeline()
            .from(".auth-card", {
                autoAlpha: 0,
                y: 28,
                scale: 0.98,
                duration: 0.76
            })
            .from(".auth-card .brand-mark", {
                autoAlpha: 0,
                y: 8,
                rotation: -10,
                duration: 0.42
            }, "-=0.42")
            .from(".auth-title, .auth-subtitle, .auth-card .mb-3, .auth-actions", {
                autoAlpha: 0,
                y: 14,
                duration: 0.42,
                stagger: 0.055
            }, "-=0.3");
    }

    function animateBigScreen() {
        if (!document.getElementById("globeCanvas")) {
            return;
        }

        if (reduceMotion) {
            return;
        }

        gsap.timeline()
            .from("header h1", { autoAlpha: 0, y: -14, duration: 0.42 }, 0)
            .from(".return-button, .showTime", {
                autoAlpha: 0,
                y: -10,
                duration: 0.32,
                stagger: 0.04
            }, 0.05)
            .from(".panel", {
                autoAlpha: 0,
                y: 22,
                scale: 0.985,
                duration: 0.48,
                stagger: { amount: 0.18, from: "center" }
            }, 0.12)
            .from(".no", {
                autoAlpha: 0,
                y: 16,
                scale: 0.985,
                duration: 0.44
            }, 0.16)
            .from(".no .no-hd li", {
                autoAlpha: 0,
                y: 12,
                duration: 0.34,
                stagger: 0.028
            }, 0.28)
            .from(".map", {
                autoAlpha: 0,
                scale: 0.955,
                duration: 0.54
            }, 0.22)
            .from(".globe-rank li", {
                autoAlpha: 0,
                x: 18,
                duration: 0.32,
                stagger: 0.03
            }, 0.46)
            .from(".no-bd li", {
                autoAlpha: 0,
                y: 10,
                duration: 0.3,
                stagger: 0.028
            }, 0.4);
    }

    function init() {
        animateAuth();
        animateAppShell();
        animateBigScreen();
        animateNumbers();
        bindNavMotion();
        bindHoverLift(".stat-card, .card, .movie-result, .toolbar-card, .panel, .map, .no");
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
