/**
 * Enhanced Popup Script - Suresh AI Origin v4
 * Features: Rarity Mode + Drone Delivery Integration
 */

const API_BASE = 'https://suresh-ai-origin.onrender.com/api';
const API_FALLBACK = 'http://localhost:5000/api';

// ==================== UTILITY FUNCTIONS ====================

async function fetchAPI(endpoint, method = 'GET', body = null) {
  const urls = [API_BASE, API_FALLBACK];
  
  for (const baseURL of urls) {
    try {
      const options = {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        }
      };
      
      if (body && method !== 'GET') {
        options.body = JSON.stringify(body);
      }
      
      const response = await fetch(`${baseURL}${endpoint}`, options);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.log(`Trying next API endpoint... (${error.message})`);
      continue;
    }
  }
  
  throw new Error('All API endpoints failed');
}

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', () => {
  initializePopup();
  setupDroneDeliveryHandlers();
  setupModalHandlers();
});

function initializePopup() {
  // Load user state
  chrome.runtime.sendMessage({ action: 'get_user_state' }, (response) => {
    if (response && response.success) {
      const state = response.data;
      
      // Update stats
      document.getElementById('blockedCount').textContent = state.blockedSitesCount || 0;
      document.getElementById('aiCount').textContent = state.aiAlternativesUsed || 0;
      
      // Update tier badge
      const tier = state.tier || 'free';
      document.getElementById('tierBadge').textContent = tier.toUpperCase() + ' TIER';
      
      // Update referral code
      chrome.runtime.sendMessage({ action: 'get_referral_code' }, (codeResponse) => {
        if (codeResponse && codeResponse.success) {
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
      if (response && response.success) {
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
}

// ==================== DRONE DELIVERY v4 ====================

function setupDroneDeliveryHandlers() {
  const droneBtn = document.getElementById('droneDeliveryBtn');
  
  droneBtn.addEventListener('click', async () => {
    droneBtn.disabled = true;
    const originalText = document.getElementById('droneButtonText').textContent;
    document.getElementById('droneButtonText').textContent = 'Detecting...';
    
    try {
      // Step 1: Detect delivery opportunity
      const opportunity = await detectDeliveryOpportunity();
      
      if (opportunity) {
        // Step 2: Display rarity popup with score
        showRarityPopup(opportunity);
      } else {
        alert('No rare delivery opportunity detected. Try again in a few moments!');
      }
    } catch (error) {
      console.error('Drone delivery error:', error);
      alert('Failed to initiate delivery. Please try again.');
    } finally {
      droneBtn.disabled = false;
      document.getElementById('droneButtonText').textContent = originalText;
    }
  });
}

async function detectDeliveryOpportunity() {
  try {
    console.log('🚁 Detecting delivery opportunity...');
    
    // Call backend to detect opportunities
    const response = await fetchAPI('/drone/opportunities', 'POST', {
      source: 'chrome_extension',
      timestamp: Date.now()
    });
    
    console.log('🎯 Opportunity detection response:', response);
    
    if (response.opportunities && response.opportunities.length > 0) {
      const opp = response.opportunities[0];
      
      // Store in Chrome storage for tracking
      await chrome.storage.local.set({
        currentDeliveryOpportunity: {
          id: opp.opp_id,
          rarity_score: opp.rarity_score,
          elite_tier: opp.elite_tier,
          is_cross_border: opp.is_cross_border,
          destination_region: opp.destination_region,
          detected_at: Date.now()
        }
      });
      
      return opp;
    }
    
    return null;
  } catch (error) {
    console.error('❌ Opportunity detection failed:', error);
    throw error;
  }
}

function showRarityPopup(opportunity) {
  const modal = document.getElementById('rarityModal');
  
  // Set rarity score
  const rarityScore = opportunity.rarity_score || 0;
  document.getElementById('rarityScoreValue').textContent = rarityScore.toFixed(1);
  
  // Set tier
  const tier = opportunity.elite_tier || 'CALCULATING...';
  const tierColors = {
    'ELITE': '🏆 ELITE (95-100)',
    'ENTERPRISE': '💎 ENTERPRISE (85-95)',
    'PRO': '⭐ PRO (70-85)',
    'BASIC': '✓ BASIC (50-70)',
    'FREE': 'FREE (0-50)'
  };
  document.getElementById('rarityTierValue').textContent = tierColors[tier] || tier;
  
  // Set delivery info
  const isElite = rarityScore >= 95;
  const statusText = isElite ? '✅ Elite Package Detected' : '📦 Package Detected';
  const statusClass = isElite ? 'status-success' : 'status-pending';
  
  document.getElementById('deliveryStatus').textContent = statusText;
  document.getElementById('statusIndicator').className = `status-indicator ${statusClass}`;
  
  // Set delivery time (mock estimation)
  const deliveryTimeMin = opportunity.is_cross_border ? 45 : 25;
  document.getElementById('deliveryTime').textContent = deliveryTimeMin;
  
  // Show modal
  modal.style.display = 'block';
  
  // Start polling for status updates
  startStatusPolling(opportunity.opp_id);
}

function startStatusPolling(opportunityId) {
  const pollInterval = setInterval(async () => {
    try {
      // Poll for delivery status
      const statusResponse = await fetchAPI(`/drone/opportunities/${opportunityId}/status`);
      
      if (statusResponse.status === 'dispatched') {
        document.getElementById('deliveryStatus').textContent = '🚁 In Transit...';
        document.getElementById('statusIndicator').className = 'status-indicator status-pending';
      } else if (statusResponse.status === 'delivered') {
        document.getElementById('deliveryStatus').textContent = '✅ Delivered!';
        document.getElementById('statusIndicator').className = 'status-indicator status-success';
        clearInterval(pollInterval);
      }
    } catch (error) {
      console.log('Status polling: API not yet available or delivery complete');
      // Continue polling - API might not be ready yet
    }
  }, 3000); // Poll every 3 seconds
  
  // Store pollInterval for cleanup
  window.currentPollInterval = pollInterval;
}

// ==================== MODAL HANDLERS ====================

function setupModalHandlers() {
  const modal = document.getElementById('rarityModal');
  const closeBtn = document.getElementById('closeModal');
  const confirmBtn = document.getElementById('confirmDelivery');
  const cancelBtn = document.getElementById('cancelDelivery');
  
  // Close button
  closeBtn.addEventListener('click', () => {
    closeRarityModal();
  });
  
  // Cancel button
  cancelBtn.addEventListener('click', () => {
    closeRarityModal();
  });
  
  // Confirm button
  confirmBtn.addEventListener('click', async () => {
    await proceedWithDelivery();
  });
  
  // Click outside modal to close
  window.addEventListener('click', (event) => {
    if (event.target === modal) {
      closeRarityModal();
    }
  });
}

function closeRarityModal() {
  const modal = document.getElementById('rarityModal');
  modal.style.display = 'none';
  
  // Stop polling
  if (window.currentPollInterval) {
    clearInterval(window.currentPollInterval);
    window.currentPollInterval = null;
  }
}

async function proceedWithDelivery() {
  try {
    // Get current opportunity from storage
    chrome.storage.local.get('currentDeliveryOpportunity', async (result) => {
      if (!result.currentDeliveryOpportunity) {
        alert('No opportunity stored. Please try again.');
        return;
      }
      
      const opp = result.currentDeliveryOpportunity;
      
      // Call backend to initiate drone delivery action
      const response = await fetchAPI('/drone/actions', 'POST', {
        opportunity_id: opp.id,
        rarity_score: opp.rarity_score,
        elite_tier: opp.elite_tier,
        is_cross_border: opp.is_cross_border,
        destination_region: opp.destination_region,
        source: 'chrome_extension',
        timestamp: Date.now()
      });
      
      console.log('🎯 Delivery action initiated:', response);
      
      if (response.success || response.action_id) {
        // Update UI
        document.getElementById('deliveryStatus').textContent = '✅ Order Confirmed!';
        document.getElementById('statusIndicator').className = 'status-indicator status-success';
        
        // Store action for tracking
        await chrome.storage.local.set({
          lastDeliveryAction: {
            action_id: response.action_id || response.id,
            initiated_at: Date.now(),
            elite_tier: opp.elite_tier,
            bundle_price: 500000 // ₹5000
          }
        });
        
        // Show success notification (if permitted)
        if (chrome.notifications) {
          chrome.notifications.create('drone_delivery_' + Date.now(), {
            type: 'basic',
            iconUrl: 'icons/icon128.png',
            title: '🚁 Rare Drone Delivery Initiated',
            message: `Your ₹5000 elite bundle is being prepared! Est. ${opp.is_cross_border ? '45' : '25'} min delivery.`,
            priority: 2
          });
        }
        
        // Close modal after 2 seconds
        setTimeout(() => {
          closeRarityModal();
        }, 2000);
      } else {
        alert('Failed to initiate delivery. Please try again.');
      }
    });
  } catch (error) {
    console.error('❌ Delivery confirmation failed:', error);
    alert('Error: ' + error.message);
  }
}

// ==================== TRACKING & MONITORING ====================

function getDeliveryStatus() {
  return new Promise((resolve) => {
    chrome.storage.local.get('lastDeliveryAction', (result) => {
      resolve(result.lastDeliveryAction || null);
    });
  });
}

// Periodically update delivery status in background
setInterval(async () => {
  const status = await getDeliveryStatus();
  
  if (status) {
    // Update background with current status
    chrome.runtime.sendMessage({
      action: 'update_delivery_status',
      status: status
    }).catch(() => {
      // Background script not ready, ignore
    });
  }
}, 5000);

// ==================== ERROR HANDLING ====================

window.addEventListener('error', (event) => {
  console.error('Popup error:', event.error);
});

// Handle messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'delivery_status_update') {
    console.log('📡 Delivery status update:', request.status);
    sendResponse({ received: true });
  }
});

console.log('✅ Popup script loaded - Drone delivery v4 ready');
