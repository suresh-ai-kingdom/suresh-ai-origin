/**
 * Content Script - Injected into all pages
 * Handles rarity warnings and UI overlays
 */

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'show_rarity_warning') {
    showRarityWarning(message.data);
    sendResponse({ success: true });
  }
});

/**
 * Show rarity warning overlay on low-rarity sites
 */
function showRarityWarning(data) {
  // Create overlay
  const overlay = document.createElement('div');
  overlay.id = 'suresh-ai-rarity-warning';
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px;
    z-index: 999999;
    font-family: system-ui, -apple-system, sans-serif;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    animation: slideDown 0.3s ease-out;
  `;
  
  overlay.innerHTML = `
    <style>
      @keyframes slideDown {
        from { transform: translateY(-100%); }
        to { transform: translateY(0); }
      }
      #suresh-ai-rarity-warning button {
        background: white;
        color: #667eea;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 600;
        margin-left: 10px;
      }
      #suresh-ai-rarity-warning button:hover {
        background: #f0f0f0;
      }
    </style>
    <div style="max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between;">
      <div style="flex: 1;">
        <strong>⚠️ Low Rarity Content (${data.rarity_score.toFixed(1)}/100)</strong>
        <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;">
          This content doesn't meet your ${data.required_score} rarity threshold. 
          ${data.ai_alternative ? 'Try our AI-powered alternative for rare insights!' : ''}
        </p>
      </div>
      <div>
        ${data.ai_alternative ? `<button id="suresh-ai-try-alternative">🤖 Try AI Alternative</button>` : ''}
        ${data.upsell_tier ? `<button id="suresh-ai-upgrade">⭐ Upgrade to ${data.upsell_tier.toUpperCase()} (₹${data.upsell_price/100}/mo)</button>` : ''}
        <button id="suresh-ai-dismiss">Dismiss</button>
      </div>
    </div>
  `;
  
  document.body.prepend(overlay);
  
  // Add event listeners
  const dismissBtn = document.getElementById('suresh-ai-dismiss');
  dismissBtn?.addEventListener('click', () => {
    overlay.style.animation = 'slideDown 0.3s ease-out reverse';
    setTimeout(() => overlay.remove(), 300);
  });
  
  const alternativeBtn = document.getElementById('suresh-ai-try-alternative');
  alternativeBtn?.addEventListener('click', () => {
    chrome.runtime.sendMessage({
      action: 'get_ai_alternative',
      url: window.location.href
    }, (response) => {
      if (response.success && response.data) {
        window.location.href = response.data.ai_url;
      }
    });
  });
  
  const upgradeBtn = document.getElementById('suresh-ai-upgrade');
  upgradeBtn?.addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'open_upgrade_page' });
  });
  
  // Auto-dismiss after 10 seconds
  setTimeout(() => {
    if (document.getElementById('suresh-ai-rarity-warning')) {
      overlay.style.animation = 'slideDown 0.3s ease-out reverse';
      setTimeout(() => overlay.remove(), 300);
    }
  }, 10000);
}

console.log('✅ Suresh AI Origin content script loaded');
