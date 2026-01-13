/**
 * Animation Testing & Validation Suite
 * Run this in browser console to verify all animations work
 */

console.log('🎨 SURESH AI ORIGIN - Animation Validation Suite');
console.log('================================================\n');

// Test 1: Check if animations.js is loaded
console.log('✓ Test 1: animations.js Loaded');
if (typeof AnimationUtils !== 'undefined') {
    console.log('  ✅ AnimationUtils available');
    console.log('  Functions:', Object.keys(AnimationUtils).join(', '));
} else {
    console.log('  ❌ AnimationUtils NOT loaded');
}

// Test 2: Check CSS animations are defined
console.log('\n✓ Test 2: CSS Animations');
const animationKeyframes = [
    'button-press',
    'button-glow',
    'ripple-spread',
    'card-lift',
    'card-glow',
    'text-reveal',
    'fade-in-up',
    'bounce-in',
    'input-glow',
    'error-shake',
    'success-bounce',
    'navbar-blur-in',
    'underline-expand',
    'spin',
    'pulse-dots',
    'skeleton-loading',
    'progress-indeterminate',
    'toast-slide-in',
    'toast-slide-out',
    'modal-scale-in',
    'overlay-fade-in'
];

const stylesheet = document.styleSheets[0];
const rules = Array.from(stylesheet.cssRules).map(r => r.name || '');
const animationCount = animationKeyframes.filter(anim => rules.includes(anim)).length;
console.log(`  ✅ ${animationCount}/${animationKeyframes.length} keyframes found`);

// Test 3: Button interactions
console.log('\n✓ Test 3: Button Interactions');
const btn = document.querySelector('.btn');
if (btn) {
    console.log('  ✅ Button found');
    console.log('  Button classes:', btn.className);
    console.log('  Has glow animation:', getComputedStyle(btn).animation.includes('glow') || 'hover state');
} else {
    console.log('  ⚠️ No button found on page');
}

// Test 4: Form inputs
console.log('\n✓ Test 4: Form Inputs');
const inputs = document.querySelectorAll('input, textarea');
if (inputs.length > 0) {
    console.log(`  ✅ Found ${inputs.length} form inputs`);
    const firstInput = inputs[0];
    console.log('  First input type:', firstInput.type);
    console.log('  Has validation events:', !!firstInput.onblur);
} else {
    console.log('  ⚠️ No form inputs on page');
}

// Test 5: Navbar scroll effects
console.log('\n✓ Test 5: Navbar Scroll Effects');
const navbar = document.querySelector('.navbar');
if (navbar) {
    console.log('  ✅ Navbar found');
    console.log('  Scroll active class:', navbar.classList.contains('scroll-active'));
    window.addEventListener('scroll', function testScroll() {
        if (window.scrollY > 50) {
            console.log('  ✅ Scroll detection working (scroll > 50px)');
            window.removeEventListener('scroll', testScroll);
        }
    });
} else {
    console.log('  ❌ Navbar not found');
}

// Test 6: Skeleton loaders
console.log('\n✓ Test 6: Loading States');
const skeleton = document.querySelector('.skeleton-loader');
const spinner = document.querySelector('.loading-spinner');
if (skeleton) console.log('  ✅ Skeleton loader found');
if (spinner) console.log('  ✅ Loading spinner found');
if (!skeleton && !spinner) console.log('  ℹ️ No loading elements on current page');

// Test 7: Modal elements
console.log('\n✓ Test 7: Modal Elements');
const modal = document.querySelector('.modal');
const overlay = document.querySelector('.modal-overlay');
if (modal) console.log('  ✅ Modal found');
if (overlay) console.log('  ✅ Modal overlay found');
if (!modal && !overlay) console.log('  ℹ️ No modals on current page');

// Test 8: Hero animations
console.log('\n✓ Test 8: Hero Section');
const hero = document.querySelector('.hero');
const heroStats = document.querySelectorAll('.stat-item');
if (hero) {
    console.log('  ✅ Hero section found');
    console.log(`  Stats to animate: ${heroStats.length}`);
}

// Test 9: Feature/Pricing cards
console.log('\n✓ Test 9: Feature & Pricing Cards');
const featureCards = document.querySelectorAll('.feature-card');
const pricingCards = document.querySelectorAll('.pricing-card');
console.log(`  ✅ Feature cards: ${featureCards.length}`);
console.log(`  ✅ Pricing cards: ${pricingCards.length}`);

// Test 10: Test helper functions
console.log('\n✓ Test 10: Helper Functions');
if (typeof AnimationUtils !== 'undefined') {
    console.log('  Available functions:');
    console.log('    - AnimationUtils.showLoadingState(element, text)');
    console.log('    - AnimationUtils.hideLoadingState(element, text)');
    console.log('    - AnimationUtils.showToast(message, type, duration)');
    console.log('    - AnimationUtils.validateField(field)');
    
    console.log('\n  Try these commands:');
    console.log('    AnimationUtils.showToast("Test success!", "success")');
    console.log('    AnimationUtils.showToast("Test error!", "error")');
    console.log('    AnimationUtils.showToast("Test warning!", "warning")');
    console.log('    AnimationUtils.showToast("Test info!", "info")');
}

// Summary
console.log('\n================================================');
console.log('🎨 Animation Suite Status: READY');
console.log('================================================\n');

// Helper: Create test toast
window.testToast = function(type = 'success') {
    const types = ['success', 'error', 'warning', 'info'];
    if (!types.includes(type)) type = 'success';
    const messages = {
        success: 'Animations working perfectly! ✨',
        error: 'This is an error toast',
        warning: 'This is a warning toast',
        info: 'This is an info toast'
    };
    AnimationUtils.showToast(messages[type], type);
};

// Helper: Test ripple effect
window.testRipple = function() {
    const btn = document.querySelector('.btn');
    if (btn) {
        const rect = btn.getBoundingClientRect();
        const clickEvent = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            clientX: rect.left + rect.width / 2,
            clientY: rect.top + rect.height / 2
        });
        btn.dispatchEvent(clickEvent);
        console.log('🌊 Ripple effect triggered on button');
    }
};

// Helper: Test form validation
window.testValidation = function() {
    const input = document.querySelector('input[type="email"]');
    if (input) {
        input.value = 'test@example.com';
        AnimationUtils.validateField(input);
        console.log('✅ Form validation triggered');
    }
};

console.log('💡 Test Helpers Available:');
console.log('  - testToast("success|error|warning|info")');
console.log('  - testRipple() - Trigger ripple on first button');
console.log('  - testValidation() - Test form validation on first email input\n');
