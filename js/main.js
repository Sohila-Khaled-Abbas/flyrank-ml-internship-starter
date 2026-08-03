/* ==========================================================================
   PORTFOLIO JS: Sohila Khaled — Main Interactivity & Theme Handler
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initMobileMenu();
    initChecklistPersistence();
    initMermaidDiagrams();
    initPriorityCalculator();
});

/**
 * Theme Toggle Handler (Dark / Light Mode)
 */
function initTheme() {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const savedTheme = localStorage.getItem('portfolio-theme') || 'dark';
    
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButtonText(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('portfolio-theme', newTheme);
            updateThemeButtonText(newTheme);
            
            if (window.mermaid) {
                initMermaidDiagrams();
            }
        });
    }
}

function updateThemeButtonText(theme) {
    const btn = document.getElementById('theme-toggle');
    if (btn) {
        btn.innerHTML = theme === 'dark' 
            ? '☀️ Light Mode' 
            : '🌙 Dark Mode';
    }
}

/**
 * Mobile Navigation Drawer Menu Toggle
 */
function initMobileMenu() {
    const mobileBtn = document.getElementById('mobile-menu-btn');
    const navLinks = document.getElementById('nav-links');

    if (mobileBtn && navLinks) {
        mobileBtn.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });

        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
            });
        });
    }
}

/**
 * Checklist State Persistence (localStorage) for dns-walkthrough.html
 */
function initChecklistPersistence() {
    const checkboxes = document.querySelectorAll('.checklist-box input[type="checkbox"]');
    
    checkboxes.forEach((cb, index) => {
        const storageKey = `dns-check-${index}`;
        const savedState = localStorage.getItem(storageKey);

        if (savedState !== null) {
            cb.checked = savedState === 'true';
        }

        cb.addEventListener('change', (e) => {
            localStorage.setItem(storageKey, e.target.checked);
        });
    });
}

/**
 * Dynamic Mermaid.js Flowchart Initialization
 */
function initMermaidDiagrams() {
    if (typeof mermaid !== 'undefined') {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        mermaid.initialize({
            startOnLoad: true,
            theme: currentTheme === 'dark' ? 'dark' : 'default',
            securityLevel: 'loose'
        });
    }
}

/**
 * LIVE DYNAMIC FEATURE: FlyRank Content Priority Calculator Playground
 */
function initPriorityCalculator() {
    const form = document.getElementById('priority-calc-form');
    const resultBox = document.getElementById('calc-result-box');

    if (form && resultBox) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            const impressions = parseFloat(document.getElementById('calc-impressions').value) || 0;
            const prevClicks = parseFloat(document.getElementById('calc-prev-clicks').value) || 0;
            const lastClicks = parseFloat(document.getElementById('calc-last-clicks').value) || 0;
            const pos = parseFloat(document.getElementById('calc-position').value) || 50.0;

            const clickDrop = Math.max(0, prevClicks - lastClicks);
            const ctr = impressions > 0 ? (lastClicks / impressions) * 100 : 0;

            // Compute score using leak-free feature weights
            const z = (clickDrop * 0.035) + (impressions * 0.00015) - (pos * 0.08) + (ctr * 0.12);
            const score = 1 / (1 + Math.exp(-z));
            const clampedScore = Math.min(0.985, Math.max(0.120, score));

            // Reason Code & Action Label Mapping
            let reasonCode = 'MONITOR_PERFORMANCE';
            let actionLabel = 'NO_ACTION_NEEDED';

            if (clickDrop > 50 && impressions > 1000) {
                reasonCode = 'STEEP_DROP_HIGH_VOLUME';
                actionLabel = 'REFRESH_AND_EXPAND_CONTENT';
            } else if (pos >= 4 && pos <= 10 && ctr < 1.0) {
                reasonCode = 'CTR_POSITION_UNDERPERFORMER';
                actionLabel = 'OPTIMIZE_TITLE_AND_META_TAGS';
            } else if (clickDrop > 0) {
                reasonCode = 'MODERATE_TRAFFIC_DECAY';
                actionLabel = 'UPDATE_STATISTICS_AND_FRESHNESS';
            }

            // Update DOM Elements
            document.getElementById('res-score').textContent = clampedScore.toFixed(4);
            document.getElementById('res-drop').textContent = `${clickDrop} clicks`;
            document.getElementById('res-reason').textContent = reasonCode;
            document.getElementById('res-action').textContent = actionLabel;

            resultBox.style.display = 'block';
            resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        });
    }
}
