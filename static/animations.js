/**
 * Premium UI Animations & Interactions
 * Handles form validation, scroll effects, loading states, and micro-interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    initScrollEffects();
    initFormAnimations();
    initTouchFeedback();
    initSmoothCounters();
});

/**
 * Scroll effects - navbar blur, parallax, reveal on scroll
 */
function initScrollEffects() {
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar?.classList.add('scroll-active');
        } else {
            navbar?.classList.remove('scroll-active');
        }
    });
    
    // Reveal animations on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fade-in-up 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.feature-card, .pricing-card, .stat-item').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Form animations and real-time validation
 */
function initFormAnimations() {
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], input[type="number"], textarea');
    
    inputs.forEach(input => {
        // Add validation on blur
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        // Real-time validation on input
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
        
        // Floating label effect
        input.addEventListener('focus', function() {
            this.parentElement?.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement?.classList.remove('focused');
            }
        });
    });
}

/**
 * Validate individual field
 */
function validateField(field) {
    const type = field.type;
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Required check
    if (!value && field.hasAttribute('required')) {
        isValid = false;
        errorMessage = 'This field is required';
    }
    
    // Email validation
    if (type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
    }
    
    // Password validation (minimum 8 chars)
    if (type === 'password' && value) {
        if (value.length < 8) {
            isValid = false;
            errorMessage = 'Password must be at least 8 characters';
        }
    }
    
    // Update field state
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        
        // Remove error message
        const existingError = field.parentElement?.querySelector('.form-error');
        if (existingError) {
            existingError.style.animation = 'fade-out 0.3s ease forwards';
            setTimeout(() => existingError.remove(), 300);
        }
        
        // Show success message
        const successMsg = field.parentElement?.querySelector('.form-success');
        if (!successMsg) {
            const msg = document.createElement('div');
            msg.className = 'form-success';
            msg.textContent = 'Looks good!';
            field.parentElement?.appendChild(msg);
            setTimeout(() => msg.style.opacity = '0.8', 100);
        }
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        
        // Remove success message
        const existingSuccess = field.parentElement?.querySelector('.form-success');
        if (existingSuccess) {
            existingSuccess.style.animation = 'fade-out 0.3s ease forwards';
            setTimeout(() => existingSuccess.remove(), 300);
        }
        
        // Show error message
        const errorMsg = field.parentElement?.querySelector('.form-error');
        if (!errorMsg) {
            const msg = document.createElement('div');
            msg.className = 'form-error';
            msg.textContent = errorMessage;
            field.parentElement?.appendChild(msg);
        }
    }
}

/**
 * Touch feedback for mobile
 */
function initTouchFeedback() {
    const buttons = document.querySelectorAll('.btn, button, a.link');
    
    buttons.forEach(btn => {
        btn.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.96)';
        });
        
        btn.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

/**
 * Smooth number counter animations
 */
function initSmoothCounters() {
    const observerOptions = {
        threshold: 0.5
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const stat = entry.target;
                const target = parseInt(stat.textContent) || 0;
                
                if (target > 0) {
                    animateCounter(stat, target);
                }
                
                observer.unobserve(stat);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.stat-value').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Animate counter from 0 to target
 */
function animateCounter(element, target) {
    let current = 0;
    const increment = target / 30; // 30 frames
    const duration = 1000;
    const startTime = Date.now();
    
    function update() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        current = Math.floor(target * progress);
        element.textContent = current.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = target.toLocaleString();
        }
    }
    
    requestAnimationFrame(update);
}

/**
 * Loading states
 */
function showLoadingState(element, text = 'Loading...') {
    const originalContent = element.innerHTML;
    element.disabled = true;
    element.innerHTML = `
        <span class="loading-spinner" style="margin-right: 8px;"></span>
        ${text}
    `;
    element.style.opacity = '0.7';
    element.dataset.originalContent = originalContent;
}

function hideLoadingState(element, text = 'Done!') {
    element.disabled = false;
    element.innerHTML = text;
    element.style.opacity = '1';
    
    // Restore original after 2 seconds
    setTimeout(() => {
        if (element.dataset.originalContent) {
            element.innerHTML = element.dataset.originalContent;
        }
    }, 2000);
}

/**
 * Toast notifications
 */
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('slide-out');
        setTimeout(() => toast.remove(), 400);
    }, duration);
}

/**
 * Ripple effect on click
 */
function initRippleEffect() {
    const buttons = document.querySelectorAll('.btn, button');
    
    buttons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.className = 'ripple';
            
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

// Initialize ripple effects when DOM loads
document.addEventListener('DOMContentLoaded', initRippleEffect);

/**
 * Smooth scroll behavior
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

/**
 * Export functions for external use
 */
window.AnimationUtils = {
    showLoadingState,
    hideLoadingState,
    showToast,
    validateField
};
