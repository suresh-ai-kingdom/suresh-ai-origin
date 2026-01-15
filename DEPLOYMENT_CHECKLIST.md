# RENDER DEPLOYMENT CHECKLIST
Generated: 2026-01-15T09:29:25.706619

BEFORE DEPLOYMENT:
  [ ] All environment variables obtained:
      - RAZORPAY_KEY_ID (Live key)
      - RAZORPAY_KEY_SECRET
      - RAZORPAY_WEBHOOK_SECRET
      - GOOGLE_API_KEY (Gemini)
      - EMAIL_USER (Outlook)
      - EMAIL_PASS (App password)
      - ADMIN_PASSWORD (Strong)
  
  [ ] GitHub repository configured
  [ ] Code pushed to main branch
  [ ] All tests passing (pytest)
  [ ] requirements.txt up to date
  [ ] Database migrations created (alembic)

DURING DEPLOYMENT (Render Dashboard):
  [ ] Create new Web Service
  [ ] Connect GitHub repository
  [ ] Configure environment variables
  [ ] Add persistent disk (/app/data, 10GB)
  [ ] Set build & start commands
  [ ] Enable auto-deploy
  [ ] Review and deploy

POST-DEPLOYMENT (First 24 Hours):
  [ ] Verify service health at /health endpoint
  [ ] Test admin login
  [ ] Verify database connectivity
  [ ] Configure Razorpay webhook
  [ ] Test payment flow (test transaction)
  [ ] Verify email notifications
  [ ] Monitor metrics dashboard
  [ ] Check real-time monitoring active
  [ ] Set up log collection
  [ ] Document live URL

PHASE 1 TARGETS:
  [ ] Track Day 1 users: 50K target
  [ ] Monitor revenue: ₹3-5M target
  [ ] Verify infrastructure: 65 satellites, 36 DCs
  [ ] Confirm marketing campaigns live
  [ ] Ensure 24/7 operations centers active
