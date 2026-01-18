/**
 * Suresh AI Origin - Rare AI Internet Extension
 * Background Service Worker
 * 
 * Features:
 * - Intercepts web requests and reroutes to ai_gateway.py
 * - Rarity mode: Blocks non-rare sites, suggests AI alternatives
 * - Referral program integration for viral growth
 * - Tracks user behavior for rarity scoring
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
  // API Gateway endpoint (replace with your production URL)
  API_GATEWAY_URL: 'https://suresh-ai-origin.onrender.com/api',
  
  // Rarity thresholds
  MIN_RARITY_SCORE: 95.0,  // Top 1%
  GRACE_BUFFER: 20,         // Allow sites within 20 points
  
  // User tier (sync from backend)
  DEFAULT_TIER: 'free',     // free, basic, pro, enterprise, elite
  
  // Referral program
  REFERRAL_REWARD: 10,      // Days of free PRO access per referral
  REFERRAL_CODE_LENGTH: 8,
  
  // Rarity mode settings
  RARITY_MODE_ENABLED: true, // Block non-rare sites
  BLOCK_REDIRECT_DELAY: 2000 // Show block message for 2s before redirect
};

// Tier rarity thresholds
const TIER_THRESHOLDS = {
  free: 50,
  basic: 70,
  pro: 85,
  enterprise: 95,
  elite: 100
};

// Common non-rare sites to block (expandable)
const NON_RARE_SITES = [
  'facebook.com',
  'twitter.com',
  'instagram.com',
  'tiktok.com',
  'reddit.com',
  'youtube.com',
  '9gag.com',
  'buzzfeed.com'
];

// ============================================================================
// STORAGE & STATE MANAGEMENT
// ============================================================================

let userState = {
  userId: null,
  tier: CONFIG.DEFAULT_TIER,
  referralCode: null,
  referralCount: 0,
  rarityAdjustment: 0.0,
  blockedSitesCount: 0,
  aiAlternativesUsed: 0
};

/**
 * Initialize extension on install
 */
chrome.runtime.onInstalled.addListener(async (details) => {
  console.log('🚀 Suresh AI Origin extension installed');
  
  // Generate unique user ID and referral code
  if (!userState.userId) {
    userState.userId = generateUserId();
    userState.referralCode = generateReferralCode();
  }
  
  // Save to storage
  await chrome.storage.local.set({ userState });
  
  // Send installation event to backend
  await sendAnalytics('extension_installed', {
    version: chrome.runtime.getManifest().version,
    reason: details.reason
  });
  
  // Show welcome page on first install
  if (details.reason === 'install') {
    chrome.tabs.create({ url: 'welcome.html' });
  }
});

/**
 * Load user state on startup
 */
chrome.runtime.onStartup.addListener(async () => {
  const stored = await chrome.storage.local.get('userState');
  if (stored.userState) {
    userState = { ...userState, ...stored.userState };
  }
  console.log('🔄 User state loaded:', userState);
});

/**
 * Save user state to storage
 */
async function saveUserState() {
  await chrome.storage.local.set({ userState });
}

// ============================================================================
// WEB REQUEST INTERCEPTION
// ============================================================================

/**
 * Intercept web requests before they are sent
 * Route through AI Gateway for rarity scoring
 */
chrome.webRequest.onBeforeRequest.addListener(
  async (details) => {
    // Skip extension pages and API calls
    if (details.url.includes('chrome-extension://') || 
        details.url.includes(CONFIG.API_GATEWAY_URL)) {
      return { cancel: false };
    }
    
    // Skip non-navigation requests (images, scripts, etc.)
    if (details.type !== 'main_frame') {
      return { cancel: false };
    }
    
    console.log('🌐 Intercepted request:', details.url);
    
    // Check if rarity mode is enabled
    const settings = await chrome.storage.local.get('rarityModeEnabled');
    const rarityModeEnabled = settings.rarityModeEnabled !== false; // Default true
    
    if (!rarityModeEnabled) {
      return { cancel: false }; // Pass through
    }
    
    // Check if site is in non-rare list
    const hostname = new URL(details.url).hostname;
    const isNonRare = NON_RARE_SITES.some(site => hostname.includes(site));
    
    if (isNonRare) {
      console.log('🚫 Blocking non-rare site:', hostname);
      
      // Increment blocked counter
      userState.blockedSitesCount++;
      await saveUserState();
      
      // Redirect to block page with AI alternative
      const blockUrl = chrome.runtime.getURL('blocked.html') + 
        `?url=${encodeURIComponent(details.url)}&hostname=${encodeURIComponent(hostname)}`;
      
      return { redirectUrl: blockUrl };
    }
    
    // For rare/unknown sites, check rarity via API (async)
    checkSiteRarity(details.url, details.tabId);
    
    return { cancel: false }; // Allow initially, may inject warning later
  },
  { urls: ["<all_urls>"] },
  ["blocking"]
);

/**
 * Check site rarity via AI Gateway API
 */
async function checkSiteRarity(url, tabId) {
  try {
    const response = await fetch(`${CONFIG.API_GATEWAY_URL}/rarity/check-site`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': userState.userId,
        'X-User-Tier': userState.tier
      },
      body: JSON.stringify({
        url: url,
        rarity_threshold: TIER_THRESHOLDS[userState.tier] + userState.rarityAdjustment
      })
    });
    
    if (!response.ok) {
      console.warn('⚠️ Rarity check failed:', response.status);
      return;
    }
    
    const result = await response.json();
    console.log('✨ Rarity score:', result.rarity_score, 'for', url);
    
    // If below user's threshold, inject warning overlay
    const userThreshold = TIER_THRESHOLDS[userState.tier] + CONFIG.GRACE_BUFFER;
    
    if (result.rarity_score < userThreshold) {
      // Inject low-rarity warning
      chrome.tabs.sendMessage(tabId, {
        action: 'show_rarity_warning',
        data: {
          rarity_score: result.rarity_score,
          required_score: userThreshold,
          ai_alternative: result.ai_alternative,
          upsell_tier: result.upsell_tier,
          upsell_price: result.upsell_price
        }
      });
    }
    
    // Track analytics
    await sendAnalytics('site_rarity_checked', {
      url: url,
      rarity_score: result.rarity_score,
      user_tier: userState.tier,
      blocked: result.rarity_score < userThreshold
    });
    
  } catch (error) {
    console.error('❌ Rarity check error:', error);
  }
}

// ============================================================================
// AI ALTERNATIVE SUGGESTIONS
// ============================================================================

/**
 * Get AI-powered alternative for blocked site
 */
async function getAIAlternative(url, query = null) {
  try {
    const response = await fetch(`${CONFIG.API_GATEWAY_URL}/ai/alternative`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': userState.userId,
        'X-User-Tier': userState.tier
      },
      body: JSON.stringify({
        url: url,
        query: query || extractQueryFromUrl(url),
        rarity_threshold: CONFIG.MIN_RARITY_SCORE
      })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('🤖 AI alternative generated:', result);
    
    // Increment AI alternatives counter
    userState.aiAlternativesUsed++;
    await saveUserState();
    
    return result;
    
  } catch (error) {
    console.error('❌ AI alternative error:', error);
    return null;
  }
}

/**
 * Extract search query from URL
 */
function extractQueryFromUrl(url) {
  try {
    const urlObj = new URL(url);
    
    // Common search parameter names
    const queryParams = ['q', 'query', 's', 'search', 'keywords'];
    
    for (const param of queryParams) {
      const value = urlObj.searchParams.get(param);
      if (value) return value;
    }
    
    // Fallback: use pathname
    return urlObj.pathname.split('/').filter(p => p).join(' ');
    
  } catch (error) {
    return url;
  }
}

// ============================================================================
// REFERRAL PROGRAM
// ============================================================================

/**
 * Handle referral code submission
 */
async function submitReferral(referralCode) {
  try {
    const response = await fetch(`${CONFIG.API_GATEWAY_URL}/referral/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': userState.userId
      },
      body: JSON.stringify({
        referral_code: referralCode,
        user_id: userState.userId
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Referral submission failed');
    }
    
    const result = await response.json();
    console.log('🎉 Referral accepted:', result);
    
    // Update user tier if reward granted
    if (result.reward_granted) {
      userState.tier = result.new_tier || userState.tier;
      await saveUserState();
    }
    
    return result;
    
  } catch (error) {
    console.error('❌ Referral error:', error);
    throw error;
  }
}

/**
 * Track referral conversion (when referred user upgrades)
 */
async function trackReferralConversion(action) {
  try {
    await fetch(`${CONFIG.API_GATEWAY_URL}/referral/track`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': userState.userId
      },
      body: JSON.stringify({
        referral_code: userState.referralCode,
        action: action, // 'install', 'upgrade', 'subscribe'
        user_id: userState.userId
      })
    });
    
    // Increment referral count
    userState.referralCount++;
    await saveUserState();
    
  } catch (error) {
    console.error('❌ Referral tracking error:', error);
  }
}

/**
 * Generate unique referral code
 */
function generateReferralCode() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let code = '';
  for (let i = 0; i < CONFIG.REFERRAL_CODE_LENGTH; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return code;
}

// ============================================================================
// MESSAGE HANDLERS
// ============================================================================

/**
 * Handle messages from popup, content scripts, and other parts
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('📨 Message received:', message.action);
  
  switch (message.action) {
    case 'get_user_state':
      sendResponse({ success: true, data: userState });
      break;
      
    case 'update_tier':
      userState.tier = message.tier;
      saveUserState().then(() => {
        sendResponse({ success: true });
      });
      return true; // Keep channel open for async
      
    case 'toggle_rarity_mode':
      chrome.storage.local.set({ 
        rarityModeEnabled: message.enabled 
      }).then(() => {
        sendResponse({ success: true, enabled: message.enabled });
      });
      return true;
      
    case 'get_ai_alternative':
      getAIAlternative(message.url, message.query).then(result => {
        sendResponse({ success: true, data: result });
      });
      return true;
      
    case 'submit_referral':
      submitReferral(message.referral_code).then(result => {
        sendResponse({ success: true, data: result });
      }).catch(error => {
        sendResponse({ success: false, error: error.message });
      });
      return true;
      
    case 'get_referral_code':
      sendResponse({ success: true, referral_code: userState.referralCode });
      break;
      
    case 'submit_feedback':
      submitUserFeedback(message.feedback).then(() => {
        sendResponse({ success: true });
      });
      return true;
      
    default:
      sendResponse({ success: false, error: 'Unknown action' });
  }
});

// ============================================================================
// ANALYTICS & FEEDBACK
// ============================================================================

/**
 * Send analytics event to backend
 */
async function sendAnalytics(event, data = {}) {
  try {
    await fetch(`${CONFIG.API_GATEWAY_URL}/analytics/track`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': userState.userId
      },
      body: JSON.stringify({
        event: event,
        data: data,
        timestamp: Date.now(),
        user_tier: userState.tier
      })
    });
  } catch (error) {
    console.error('❌ Analytics error:', error);
  }
}

/**
 * Submit user feedback to autonomous engine
 */
async function submitUserFeedback(feedback) {
  try {
    const response = await fetch(`${CONFIG.API_GATEWAY_URL}/v3/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': userState.userId
      },
      body: JSON.stringify({
        user_id: userState.userId,
        task_id: feedback.task_id || 'extension_feedback',
        rating: feedback.rating,
        rarity_satisfied: feedback.rarity_satisfied,
        comments: feedback.comments || ''
      })
    });
    
    if (!response.ok) {
      throw new Error('Feedback submission failed');
    }
    
    console.log('✅ Feedback submitted');
    
    // Track analytics
    await sendAnalytics('feedback_submitted', feedback);
    
  } catch (error) {
    console.error('❌ Feedback error:', error);
  }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Generate unique user ID
 */
function generateUserId() {
  return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Check if site is whitelisted (always allow)
 */
function isWhitelisted(hostname) {
  const whitelist = [
    'github.com',
    'stackoverflow.com',
    'arxiv.org',
    'scholar.google.com'
  ];
  
  return whitelist.some(site => hostname.includes(site));
}

// ============================================================================
// CONTEXT MENU (Right-click actions)
// ============================================================================

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'get_ai_alternative',
    title: 'Get AI Alternative (Rare Content)',
    contexts: ['page', 'link']
  });
  
  chrome.contextMenus.create({
    id: 'check_rarity',
    title: 'Check Rarity Score',
    contexts: ['page', 'link']
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'get_ai_alternative') {
    const url = info.linkUrl || info.pageUrl;
    getAIAlternative(url).then(result => {
      if (result) {
        chrome.tabs.create({ url: result.ai_url });
      }
    });
  } else if (info.menuItemId === 'check_rarity') {
    const url = info.linkUrl || info.pageUrl;
    checkSiteRarity(url, tab.id);
  }
});

// ============================================================================
// PERIODIC SYNC (Update user tier from backend)
// ============================================================================

/**
 * Sync user state with backend every 1 hour
 */
chrome.alarms.create('sync_user_state', { periodInMinutes: 60 });

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === 'sync_user_state') {
    try {
      const response = await fetch(`${CONFIG.API_GATEWAY_URL}/user/state`, {
        headers: {
          'X-User-Id': userState.userId
        }
      });
      
      if (response.ok) {
        const serverState = await response.json();
        
        // Update tier if changed
        if (serverState.tier !== userState.tier) {
          console.log('🔄 Tier updated:', userState.tier, '→', serverState.tier);
          userState.tier = serverState.tier;
          await saveUserState();
        }
      }
    } catch (error) {
      console.error('❌ Sync error:', error);
    }
  }
});

// ============================================================================
// INITIALIZATION
// ============================================================================

console.log('🚀 Suresh AI Origin - Rare AI Internet Extension loaded');
console.log('📊 User ID:', userState.userId);
console.log('🎟️  Referral Code:', userState.referralCode);
console.log('⭐ Current Tier:', userState.tier);
