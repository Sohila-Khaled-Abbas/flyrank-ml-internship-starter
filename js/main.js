/* ==========================================================================
   PORTFOLIO JS: Sohila Khaled — Main Interactivity & Theme Handler
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initMobileMenu();
    initChecklistPersistence();
    initMermaidDiagrams();
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
            
            // Re-render Mermaid diagrams if present
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

        // Close menu on link click
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
