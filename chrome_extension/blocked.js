/**
 * Blocked page script
 */

// Get URL parameters
const urlParams = new URLSearchParams(window.location.search);
const blockedUrl = urlParams.get('url');
const hostname = urlParams.get('hostname');

// Display blocked site
document.getElementById('blockedSite').textContent = hostname || blockedUrl;

// Load user stats
chrome.runtime.sendMessage({ action: 'get_user_state' }, (response) => {
  if (response.success) {
    const state = response.data;
    document.getElementById('blockedCount').textContent = state.blockedSitesCount || 0;
    document.getElementById('aiUsedCount').textContent = state.aiAlternativesUsed || 0;
    
    // Estimate time saved (5 min per blocked site)
    const timeSaved = Math.floor((state.blockedSitesCount || 0) * 5 / 60);
    document.getElementById('timeSaved').textContent = timeSaved + 'h';
  }
});

// AI Alternative button
document.getElementById('aiAlternative').addEventListener('click', async () => {
  const button = document.getElementById('aiAlternative');
  const loading = document.getElementById('loading');
  
  button.disabled = true;
  loading.style.display = 'inline-block';
  
  chrome.runtime.sendMessage({
    action: 'get_ai_alternative',
    url: blockedUrl
  }, (response) => {
    button.disabled = false;
    loading.style.display = 'none';
    
    if (response.success && response.data) {
      // Redirect to AI alternative
      window.location.href = response.data.ai_url || response.data.content_url;
    } else {
      alert('Failed to generate AI alternative. Please try again.');
    }
  });
});

// Allow once button
document.getElementById('allowOnce').addEventListener('click', () => {
  window.location.href = blockedUrl;
});

// Disable rarity mode button
document.getElementById('disableRarity').addEventListener('click', () => {
  const confirm = window.confirm(
    'Are you sure you want to disable Rarity Mode?\n\n' +
    'This will allow access to all sites, including non-rare content.'
  );
  
  if (confirm) {
    chrome.runtime.sendMessage({
      action: 'toggle_rarity_mode',
      enabled: false
    }, (response) => {
      if (response.success) {
        alert('Rarity Mode disabled. You can re-enable it in the extension popup.');
        window.location.href = blockedUrl;
      }
    });
  }
});
