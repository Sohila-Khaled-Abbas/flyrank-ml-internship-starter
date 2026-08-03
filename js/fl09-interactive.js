/* ==========================================================================
   FL-09 DEMO INTERACTIVE SCRIPT
   Author: Sohila Khaled Abbas (Applied ML Intern & Search Intelligence Engineer)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initTimestampItems();
    initCopyButtons();
    initTabbedInstallation();
});

/**
 * Interactive Video Timestamp Click Handler
 */
function initTimestampItems() {
    const items = document.querySelectorAll('.timestamp-item');
    items.forEach(item => {
        item.addEventListener('click', () => {
            items.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            
            // Scroll to video box smoothly if needed
            const videoCard = document.querySelector('.video-showcase-card');
            if (videoCard) {
                videoCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        });
    });
}

/**
 * One-Click Terminal Code Block Copying
 */
function initCopyButtons() {
    const copyBtns = document.querySelectorAll('.copy-btn');
    copyBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const container = btn.closest('.code-block-container');
            const code = container ? container.querySelector('pre.code-block').innerText : '';

            if (code) {
                navigator.clipboard.writeText(code).then(() => {
                    const originalText = btn.innerText;
                    btn.innerText = '✓ Copied!';
                    btn.style.borderColor = '#10b981';
                    btn.style.color = '#10b981';

                    setTimeout(() => {
                        btn.innerText = originalText;
                        btn.style.borderColor = '';
                        btn.style.color = '';
                    }, 2000);
                });
            }
        });
    });
}

/**
 * Installation Step Tabs Switcher
 */
function initTabbedInstallation() {
    const tabBtns = document.querySelectorAll('.install-tab-btn');
    const tabContents = document.querySelectorAll('.install-tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-tab');

            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.style.display = 'none');

            btn.classList.add('active');
            const activeContent = document.getElementById(target);
            if (activeContent) {
                activeContent.style.display = 'block';
            }
        });
    });
}
