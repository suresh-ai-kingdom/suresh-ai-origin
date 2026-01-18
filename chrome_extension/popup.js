/**
 * Popup script
 */

// Load user state
chrome.runtime.sendMessage({ action: 'get_user_state' }, (response) => {
  if (response.success) {
    const state = response.data;
    
    // Update stats
    document.getElementById('blockedCount').textContent = state.blockedSitesCount || 0;
    document.getElementById('aiCount').textContent = state.aiAlternativesUsed || 0;
    
    // Update tier badge
    const tier = state.tier || 'free';
    document.getElementById('tierBadge').textContent = tier.toUpperCase() + ' TIER';
    
    // Update referral code
    chrome.runtime.sendMessage({ action: 'get_referral_code' }, (codeResponse) => {
      if (codeResponse.success) {
        document.getElementById('referralCode').textContent = codeResponse.referral_code;
      }
    });
  }
});

// Load rarity mode state
chrome.storage.local.get('rarityModeEnabled', (result) => {
  const enabled = result.rarityModeEnabled !== false; // Default true
  document.getElementById('rarityToggle').checked = enabled;
});

// Rarity toggle
document.getElementById('rarityToggle').addEventListener('change', (e) => {
  const enabled = e.target.checked;
  
  chrome.runtime.sendMessage({
    action: 'toggle_rarity_mode',
    enabled: enabled
  }, (response) => {
    if (response.success) {
      console.log('Rarity mode:', enabled ? 'enabled' : 'disabled');
    }
  });
});

// Referral code click to copy
document.getElementById('referralCode').addEventListener('click', async () => {
  const code = document.getElementById('referralCode').textContent;
  
  try {
    await navigator.clipboard.writeText(code);
    
    // Show feedback
    const original = document.getElementById('referralCode').textContent;
    document.getElementById('referralCode').textContent = '✓ COPIED!';
    setTimeout(() => {
      document.getElementById('referralCode').textContent = original;
    }, 1000);
  } catch (error) {
    console.error('Copy failed:', error);
  }
});

// Upgrade button
document.getElementById('upgradeBtn').addEventListener('click', () => {
  chrome.tabs.create({ 
    url: 'https://suresh-ai-origin.onrender.com/pricing' 
  });
});

// Dashboard button
document.getElementById('dashboardBtn').addEventListener('click', () => {
  chrome.tabs.create({ 
    url: 'https://suresh-ai-origin.onrender.com/admin/dashboard' 
  });
});
