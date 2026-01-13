/**
 * PREMIUM 1% RARE EFFECTS
 * Advanced UI interactions for ultra-premium experience
 */

document.addEventListener('DOMContentLoaded', function() {
    initCursorTrail();
    initCustomCursor();
    init3DCardTilt();
    initMagneticButtons();
    initParallaxScroll();
    initPremiumLoader();
    initHolographicText();
    initScanlines();
});

/**
 * Cursor Trail Effect
 */
function initCursorTrail() {
    let trails = [];
    const maxTrails = 10;
    
    document.addEventListener('mousemove', (e) => {
        // Create trail element
        const trail = document.createElement('div');
        trail.className = 'cursor-trail';
        trail.style.left = e.clientX + 'px';
        trail.style.top = e.clientY + 'px';
        document.body.appendChild(trail);
        
        trails.push(trail);
        
        // Remove old trails
        if (trails.length > maxTrails) {
            const oldTrail = trails.shift();
            oldTrail.remove();
        }
        
        // Auto-remove after animation
        setTimeout(() => {
            trail.remove();
            trails = trails.filter(t => t !== trail);
        }, 800);
    });
}

/**
 * Custom Cursor
 */
function initCustomCursor() {
    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    document.body.appendChild(cursor);
    
    let mouseX = 0, mouseY = 0;
    let cursorX = 0, cursorY = 0;
    
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });
    
    // Smooth cursor follow
    function updateCursor() {
        cursorX += (mouseX - cursorX) * 0.15;
        cursorY += (mouseY - cursorY) * 0.15;
        
        cursor.style.transform = `translate(${cursorX - 12}px, ${cursorY - 12}px)`;
        requestAnimationFrame(updateCursor);
    }
    updateCursor();
    
    // Hover effect on interactive elements
    const interactiveElements = document.querySelectorAll('a, button, .btn, input, textarea');
    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', () => cursor.classList.add('hover'));
        el.addEventListener('mouseleave', () => cursor.classList.remove('hover'));
    });
}

/**
 * 3D Card Tilt Effect
 */
function init3DCardTilt() {
    const cards = document.querySelectorAll('.feature-card, .pricing-card, .service-box, .service-card');
    
    cards.forEach(card => {
        card.classList.add('card-3d');
        
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;
            
            card.style.setProperty('--rotate-x', `${rotateX}deg`);
            card.style.setProperty('--rotate-y', `${rotateY}deg`);
            card.style.setProperty('--mouse-x', `${(x / rect.width) * 100}%`);
            card.style.setProperty('--mouse-y', `${(y / rect.height) * 100}%`);
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.setProperty('--rotate-x', '0deg');
            card.style.setProperty('--rotate-y', '0deg');
        });
    });
}

/**
 * Magnetic Button Effect
 */
function initMagneticButtons() {
    const buttons = document.querySelectorAll('.btn, button');
    
    buttons.forEach(btn => {
        btn.classList.add('btn-magnetic');
        btn.classList.add('btn-liquid');
        
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            const strength = 0.3;
            btn.style.setProperty('--magnetic-x', `${x * strength}px`);
            btn.style.setProperty('--magnetic-y', `${y * strength}px`);
        });
        
        btn.addEventListener('mouseleave', () => {
            btn.style.setProperty('--magnetic-x', '0px');
            btn.style.setProperty('--magnetic-y', '0px');
        });
    });
}

/**
 * Parallax Scroll Effect
 */
function initParallaxScroll() {
    let ticking = false;
    
    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                const scrollY = window.scrollY;
                document.documentElement.style.setProperty('--scroll-y', scrollY);
                
                // Apply to hero elements
                const hero = document.querySelector('.hero');
                if (hero) {
                    hero.style.transform = `translateY(${scrollY * 0.5}px)`;
                }
                
                ticking = false;
            });
            ticking = true;
        }
    });
}

/**
 * Premium Loader
 */
function initPremiumLoader() {
    // Only show on first load
    if (!sessionStorage.getItem('loaderShown')) {
        const loader = document.createElement('div');
        loader.className = 'premium-loader';
        loader.innerHTML = `
            <div class="loader-ring"></div>
            <div class="loader-text">SURESH AI ORIGIN</div>
        `;
        document.body.appendChild(loader);
        
        sessionStorage.setItem('loaderShown', 'true');
        
        setTimeout(() => {
            loader.remove();
        }, 3500);
    }
}

/**
 * Holographic Text Effect
 */
function initHolographicText() {
    // Apply to main headings
    const headings = document.querySelectorAll('h1, .gradient');
    headings.forEach(heading => {
        if (!heading.classList.contains('gradient')) {
            heading.classList.add('text-holographic');
        }
    });
}

/**
 * Scanlines Overlay
 */
function initScanlines() {
    const scanlines = document.createElement('div');
    scanlines.className = 'scanline-overlay';
    document.body.appendChild(scanlines);
}

/**
 * Glitch Effect on Hover
 */
function initGlitchEffect() {
    const badges = document.querySelectorAll('.badge, .premium-badge');
    badges.forEach(badge => {
        const text = badge.textContent;
        badge.classList.add('text-glitch');
        badge.setAttribute('data-text', text);
    });
}

// Initialize glitch effect
document.addEventListener('DOMContentLoaded', initGlitchEffect);

/**
 * Neon Glow on Specific Elements
 */
function initNeonGlow() {
    const accent = document.querySelectorAll('.stat strong, .service-icon');
    accent.forEach(el => {
        if (el.textContent.length < 10) { // Only short text
            el.classList.add('text-neon');
        }
    });
}

// Initialize neon glow
document.addEventListener('DOMContentLoaded', initNeonGlow);

/**
 * Performance optimization - disable on mobile
 */
if (window.innerWidth <= 768) {
    // Disable heavy effects on mobile
    document.body.style.cursor = 'auto';
    const cursorElements = document.querySelectorAll('.custom-cursor, .cursor-trail');
    cursorElements.forEach(el => el.remove());
}

/**
 * Easter egg - Konami code
 */
let konamiCode = [];
const konamiSequence = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]; // ↑↑↓↓←→←→BA

document.addEventListener('keydown', (e) => {
    konamiCode.push(e.keyCode);
    konamiCode = konamiCode.slice(-10);
    
    if (konamiCode.join(',') === konamiSequence.join(',')) {
        // Activate ultra mode
        document.body.style.animation = 'gradient-shift 2s ease infinite, rotate 20s linear infinite';
        
        if ('speechSynthesis' in window) {
            const msg = new SpeechSynthesisUtterance("Top 1 percent rare mode activated. Welcome to the future.");
            msg.rate = 0.9;
            msg.pitch = 0.7;
            speechSynthesis.speak(msg);
        }
        
        // Show celebration
        for (let i = 0; i < 50; i++) {
            setTimeout(() => {
                const sparkle = document.createElement('div');
                sparkle.style.position = 'fixed';
                sparkle.style.left = Math.random() * 100 + 'vw';
                sparkle.style.top = Math.random() * 100 + 'vh';
                sparkle.style.width = '4px';
                sparkle.style.height = '4px';
                sparkle.style.background = '#00FF9F';
                sparkle.style.borderRadius = '50%';
                sparkle.style.animation = 'fade-out 2s ease forwards';
                sparkle.style.zIndex = '99999';
                document.body.appendChild(sparkle);
                setTimeout(() => sparkle.remove(), 2000);
            }, i * 50);
        }
        
        konamiCode = [];
    }
});
