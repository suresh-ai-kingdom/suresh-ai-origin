#!/usr/bin/env pwsh
# Quick setup script for SURESH AI ORIGIN workspace

Write-Host "🚀 Starting workspace setup..." -ForegroundColor Cyan

# Step 1: Create virtual environment
if (!(Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
} else {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
}

# Step 2: Activate and install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
& .\venv\Scripts\python.exe -m pip install --upgrade pip --quiet
& .\venv\Scripts\pip.exe install -r requirements.txt --quiet

# Step 3: Create .env if needed
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "📝 Creating .env from .env.example..." -ForegroundColor Yellow
        Copy-Item .env.example .env
        Write-Host "⚠️  Remember to fill in your secrets in .env" -ForegroundColor Red
    }
} else {
    Write-Host "✓ .env exists" -ForegroundColor Green
}

# Step 4: Run migrations
Write-Host "🗄️  Running database migrations..." -ForegroundColor Yellow
$env:PYTHONPATH = "."
& .\venv\Scripts\alembic.exe upgrade head 2>$null
if ($LASTEXITCODE -ne 0) {
    & .\venv\Scripts\alembic.exe stamp head
}

# Step 5: Run tests
Write-Host "🧪 Running tests..." -ForegroundColor Yellow
& .\venv\Scripts\python.exe -m pytest -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests failed - please check output" -ForegroundColor Red
    exit 1
}

# Step 6: Seed demo data (optional)
$seed = Read-Host "Seed demo data for testing? (y/N)"
if ($seed -eq "y" -or $seed -eq "Y") {
    Write-Host "🌱 Seeding demo data..." -ForegroundColor Yellow
    & .\venv\Scripts\python.exe scripts/seed_demo.py seed
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Edit .env and add your secrets (Razorpay keys, email, etc.)" -ForegroundColor White
Write-Host "  2. Run the app: .\venv\Scripts\python.exe app.py" -ForegroundColor White
Write-Host "  3. Visit: http://localhost:5000" -ForegroundColor White
Write-Host ""
