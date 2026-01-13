/**
 * CRYPTO 1% RARE EFFECTS - Bitcoin & Blockchain Integration
 * Ultra-premium crypto features with rare visual flows
 */

document.addEventListener('DOMContentLoaded', function() {
    initCryptoTicker();
    initBlockchainBackground();
    initCryptoFloatingParticles();
    initCryptoPaymentModal();
    initBitcoinRain();
});

/**
 * Live Crypto Price Ticker - Top Rare Feature
 */
function initCryptoTicker() {
    const ticker = document.createElement('div');
    ticker.className = 'crypto-ticker';
    ticker.innerHTML = `
        <div class="ticker-wrapper">
            <div class="ticker-item">
                <span class="crypto-icon">₿</span>
                <span class="crypto-name">BTC</span>
                <span class="crypto-price" data-crypto="bitcoin">$--,---</span>
                <span class="crypto-change positive">+0.00%</span>
            </div>
            <div class="ticker-item">
                <span class="crypto-icon">Ξ</span>
                <span class="crypto-name">ETH</span>
                <span class="crypto-price" data-crypto="ethereum">$--,---</span>
                <span class="crypto-change positive">+0.00%</span>
            </div>
            <div class="ticker-item">
                <span class="crypto-icon">◎</span>
                <span class="crypto-name">SOL</span>
                <span class="crypto-price" data-crypto="solana">$---</span>
                <span class="crypto-change positive">+0.00%</span>
            </div>
            <div class="ticker-item">
                <span class="crypto-icon">▲</span>
                <span class="crypto-name">BNB</span>
                <span class="crypto-price" data-crypto="binancecoin">$---</span>
                <span class="crypto-change positive">+0.00%</span>
            </div>
        </div>
    `;
    document.body.appendChild(ticker);
    
    // Fetch real-time crypto prices
    fetchCryptoPrices();
    setInterval(fetchCryptoPrices, 60000); // Update every minute
}

async function fetchCryptoPrices() {
    try {
        const response = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,binancecoin&vs_currencies=usd&include_24hr_change=true');
        const data = await response.json();
        
        // Update Bitcoin
        const btcPrice = document.querySelector('[data-crypto="bitcoin"]');
        const btcChange = btcPrice.nextElementSibling;
        if (data.bitcoin) {
            btcPrice.textContent = `$${data.bitcoin.usd.toLocaleString()}`;
            const change = data.bitcoin.usd_24h_change;
            btcChange.textContent = `${change > 0 ? '+' : ''}${change.toFixed(2)}%`;
            btcChange.className = `crypto-change ${change > 0 ? 'positive' : 'negative'}`;
        }
        
        // Update Ethereum
        const ethPrice = document.querySelector('[data-crypto="ethereum"]');
        const ethChange = ethPrice.nextElementSibling;
        if (data.ethereum) {
            ethPrice.textContent = `$${data.ethereum.usd.toLocaleString()}`;
            const change = data.ethereum.usd_24h_change;
            ethChange.textContent = `${change > 0 ? '+' : ''}${change.toFixed(2)}%`;
            ethChange.className = `crypto-change ${change > 0 ? 'positive' : 'negative'}`;
        }
        
        // Update Solana
        const solPrice = document.querySelector('[data-crypto="solana"]');
        const solChange = solPrice.nextElementSibling;
        if (data.solana) {
            solPrice.textContent = `$${data.solana.usd.toFixed(2)}`;
            const change = data.solana.usd_24h_change;
            solChange.textContent = `${change > 0 ? '+' : ''}${change.toFixed(2)}%`;
            solChange.className = `crypto-change ${change > 0 ? 'positive' : 'negative'}`;
        }
        
        // Update BNB
        const bnbPrice = document.querySelector('[data-crypto="binancecoin"]');
        const bnbChange = bnbPrice.nextElementSibling;
        if (data.binancecoin) {
            bnbPrice.textContent = `$${data.binancecoin.usd.toFixed(2)}`;
            const change = data.binancecoin.usd_24h_change;
            bnbChange.textContent = `${change > 0 ? '+' : ''}${change.toFixed(2)}%`;
            bnbChange.className = `crypto-change ${change > 0 ? 'positive' : 'negative'}`;
        }
    } catch (error) {
        console.log('Crypto prices loading...');
    }
}

/**
 * Blockchain Matrix Background - Rare Flow Animation
 */
function initBlockchainBackground() {
    const canvas = document.createElement('canvas');
    canvas.className = 'blockchain-canvas';
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    document.body.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    const columns = Math.floor(canvas.width / 20);
    const drops = Array(columns).fill(1);
    
    const blockchainChars = '₿ΞΘΔΣΠΩ0123456789ABCDEF';
    
    function drawBlockchain() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = '#00FFFF';
        ctx.font = '14px monospace';
        
        for (let i = 0; i < drops.length; i++) {
            const char = blockchainChars[Math.floor(Math.random() * blockchainChars.length)];
            const x = i * 20;
            const y = drops[i] * 20;
            
            // Gradient effect
            const gradient = ctx.createLinearGradient(x, y - 20, x, y);
            gradient.addColorStop(0, 'rgba(0, 255, 255, 0.1)');
            gradient.addColorStop(1, 'rgba(0, 255, 255, 0.8)');
            ctx.fillStyle = gradient;
            
            ctx.fillText(char, x, y);
            
            if (y > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }
    
    setInterval(drawBlockchain, 50);
    
    // Resize handler
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

/**
 * Floating Crypto Particles - Bitcoin/Ethereum logos
 */
function initCryptoFloatingParticles() {
    const container = document.createElement('div');
    container.className = 'crypto-particles';
    document.body.appendChild(container);
    
    const cryptoSymbols = ['₿', 'Ξ', '◎', '▲', '◆', '●'];
    const colors = ['#00FFFF', '#FF00FF', '#00FF41', '#39FF14', '#FF10F0'];
    
    function createParticle() {
        const particle = document.createElement('div');
        particle.className = 'crypto-particle';
        particle.textContent = cryptoSymbols[Math.floor(Math.random() * cryptoSymbols.length)];
        particle.style.color = colors[Math.floor(Math.random() * colors.length)];
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDuration = (Math.random() * 10 + 15) + 's';
        particle.style.fontSize = (Math.random() * 20 + 20) + 'px';
        particle.style.opacity = Math.random() * 0.5 + 0.3;
        
        container.appendChild(particle);
        
        setTimeout(() => particle.remove(), 25000);
    }
    
    // Create initial particles
    for (let i = 0; i < 15; i++) {
        setTimeout(createParticle, i * 1000);
    }
    
    // Continuous creation
    setInterval(createParticle, 3000);
}

/**
 * Bitcoin Rain Effect - Rare 1% Feature
 */
function initBitcoinRain() {
    let isRaining = false;
    
    // Konami-style trigger: Click Bitcoin ticker 5 times fast
    let clickCount = 0;
    let clickTimer;
    
    document.addEventListener('click', (e) => {
        if (e.target.closest('.crypto-ticker')) {
            clickCount++;
            clearTimeout(clickTimer);
            
            if (clickCount === 5) {
                triggerBitcoinRain();
                clickCount = 0;
            }
            
            clickTimer = setTimeout(() => clickCount = 0, 2000);
        }
    });
    
    function triggerBitcoinRain() {
        if (isRaining) return;
        isRaining = true;
        
        // Voice announcement
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance('Bitcoin rain activated. Top one percent mode engaged.');
            utterance.rate = 1.1;
            utterance.pitch = 0.9;
            speechSynthesis.speak(utterance);
        }
        
        const rainContainer = document.createElement('div');
        rainContainer.className = 'bitcoin-rain-container';
        document.body.appendChild(rainContainer);
        
        for (let i = 0; i < 50; i++) {
            setTimeout(() => {
                const coin = document.createElement('div');
                coin.className = 'bitcoin-coin';
                coin.innerHTML = '₿';
                coin.style.left = Math.random() * 100 + '%';
                coin.style.animationDuration = (Math.random() * 2 + 3) + 's';
                coin.style.animationDelay = Math.random() * 0.5 + 's';
                rainContainer.appendChild(coin);
                
                setTimeout(() => coin.remove(), 5000);
            }, i * 100);
        }
        
        setTimeout(() => {
            rainContainer.remove();
            isRaining = false;
        }, 8000);
    }
}

/**
 * Crypto Payment Modal - Premium Integration
 */
function initCryptoPaymentModal() {
    // Add crypto payment buttons to existing product sections
    const productButtons = document.querySelectorAll('.hero-buttons, .pricing-actions');
    
    productButtons.forEach(buttonContainer => {
        const cryptoBtn = document.createElement('button');
        cryptoBtn.className = 'btn-crypto';
        cryptoBtn.innerHTML = '₿ Pay with Crypto';
        cryptoBtn.onclick = openCryptoModal;
        
        // Insert after primary button if exists
        const primaryBtn = buttonContainer.querySelector('.btn-primary');
        if (primaryBtn) {
            primaryBtn.parentNode.insertBefore(cryptoBtn, primaryBtn.nextSibling);
        } else {
            buttonContainer.appendChild(cryptoBtn);
        }
    });
}

function openCryptoModal() {
    const modal = document.createElement('div');
    modal.className = 'crypto-modal';
    modal.innerHTML = `
        <div class="crypto-modal-content">
            <button class="crypto-modal-close">&times;</button>
            <h2 class="text-holographic">Pay with Cryptocurrency</h2>
            <p style="color: rgba(255,255,255,0.7); margin-bottom: 30px;">Choose your preferred crypto payment method</p>
            
            <div class="crypto-payment-options">
                <div class="crypto-option" data-crypto="bitcoin">
                    <span class="crypto-logo">₿</span>
                    <span class="crypto-label">Bitcoin</span>
                    <span class="crypto-network">BTC Network</span>
                </div>
                <div class="crypto-option" data-crypto="ethereum">
                    <span class="crypto-logo">Ξ</span>
                    <span class="crypto-label">Ethereum</span>
                    <span class="crypto-network">ERC-20</span>
                </div>
                <div class="crypto-option" data-crypto="usdt">
                    <span class="crypto-logo">₮</span>
                    <span class="crypto-label">USDT</span>
                    <span class="crypto-network">TRC-20/ERC-20</span>
                </div>
                <div class="crypto-option" data-crypto="solana">
                    <span class="crypto-logo">◎</span>
                    <span class="crypto-label">Solana</span>
                    <span class="crypto-network">SOL Network</span>
                </div>
            </div>
            
            <div class="crypto-wallet-info" style="display: none;">
                <h3>Send Payment To:</h3>
                <div class="wallet-address-container">
                    <input type="text" class="wallet-address" readonly>
                    <button class="btn-copy-wallet">Copy</button>
                </div>
                <div class="qr-code-placeholder">
                    <div class="qr-icon">📱</div>
                    <p>Scan QR Code</p>
                </div>
                <p class="wallet-warning">⚠️ Send exact amount. Contact support after payment with transaction ID.</p>
            </div>
            
            <div class="crypto-advantages">
                <div class="advantage-item">⚡ Instant Processing</div>
                <div class="advantage-item">🔒 Secure & Private</div>
                <div class="advantage-item">🌍 Global Access</div>
                <div class="advantage-item">💎 Top 1% Method</div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close modal handlers
    modal.querySelector('.crypto-modal-close').onclick = () => modal.remove();
    modal.onclick = (e) => {
        if (e.target === modal) modal.remove();
    };
    
    // Crypto option selection
    const options = modal.querySelectorAll('.crypto-option');
    const walletInfo = modal.querySelector('.crypto-wallet-info');
    const walletInput = modal.querySelector('.wallet-address');
    
    // Demo wallet addresses (replace with real ones)
    const walletAddresses = {
        bitcoin: 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
        ethereum: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
        usdt: 'TXYZuBkjf5hAcPBH7M9qV8rW3nN2pL5kD9',
        solana: 'DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK'
    };
    
    options.forEach(option => {
        option.onclick = () => {
            const crypto = option.dataset.crypto;
            options.forEach(o => o.classList.remove('selected'));
            option.classList.add('selected');
            
            walletInput.value = walletAddresses[crypto];
            walletInfo.style.display = 'block';
            
            // Animate reveal
            setTimeout(() => walletInfo.style.opacity = '1', 10);
        };
    });
    
    // Copy wallet address
    modal.querySelector('.btn-copy-wallet').onclick = () => {
        walletInput.select();
        document.execCommand('copy');
        
        const btn = modal.querySelector('.btn-copy-wallet');
        const originalText = btn.textContent;
        btn.textContent = '✓ Copied!';
        btn.style.background = '#00FF41';
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
        }, 2000);
    };
}

// Disable heavy effects on mobile for performance
if (window.innerWidth <= 768) {
    const originalInit = window.initBlockchainBackground;
    window.initBlockchainBackground = () => {}; // Disable blockchain canvas on mobile
    
    const originalParticles = window.initCryptoFloatingParticles;
    window.initCryptoFloatingParticles = function() {
        // Reduce particles to 5 on mobile
        const container = document.createElement('div');
        container.className = 'crypto-particles';
        document.body.appendChild(container);
        
        for (let i = 0; i < 5; i++) {
            setTimeout(() => {
                const particle = document.createElement('div');
                particle.className = 'crypto-particle';
                particle.textContent = '₿';
                particle.style.color = '#00FFFF';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.animationDuration = '20s';
                container.appendChild(particle);
            }, i * 2000);
        }
    };
}
