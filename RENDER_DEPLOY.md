# 🎨 Render.com Deployment Guide - Complete Setup

Your backend is **100% ready** for Render deployment!

---

## 🎯 **DEPLOY IN 3 SIMPLE STEPS**

### **Step 1: Push to GitHub** (1 minute)

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

---

### **Step 2: Deploy on Render** (5 minutes)

#### **Option A: Using Blueprint (Automatic - RECOMMENDED)**

1. Go to: **https://render.com/**
2. Click: **"Sign Up"** (use GitHub)
3. Click: **"New +"** → **"Blueprint"**
4. Connect your GitHub repository
5. Render reads `render.yaml` and:
   - ✅ Creates web service
   - ✅ Creates PostgreSQL database
   - ✅ Links them together
   - ✅ Auto-configures everything!

**Click "Apply" and you're done!** 🎉

---

#### **Option B: Manual Setup**

If Blueprint doesn't work:

1. **Create Web Service:**
   - New + → Web Service
   - Connect GitHub repo
   - Name: `backend-api`
   - Runtime: Python 3
   - Build Command: 
     ```
     pip install -r requirements.txt && python manage.py collectstatic --no-input
     ```
   - Start Command:
     ```
     python manage.py migrate && python manage.py populate_categories && gunicorn backend_api.wsgi:application
     ```

2. **Create PostgreSQL Database:**
   - New + → PostgreSQL
   - Name: `postgres`
   - Plan: Free

3. **Link Database to Web Service:**
   - In Web Service → Environment
   - Add: `DATABASE_URL` = (Internal Database URL from PostgreSQL)

---

### **Step 3: Configure Environment Variables** (2 minutes)

In Render dashboard → **Web Service** → **Environment** tab:

**Add these variables:**

| Key | Value |
|-----|-------|
| `SECRET_KEY` | `5h@=t_o07&y^k54i)ysx*y2))hu8s8+&g=#fxooi(383nwr9@u` |
| `DEBUG` | `False` |
| `PYTHON_VERSION` | `3.12.1` |
| `ALLOWED_HOSTS` | `.onrender.com,localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | `https://your-frontend.vercel.app,http://localhost:3000` |

**Note:** `DATABASE_URL` is auto-provided by PostgreSQL database!

Click **"Save Changes"** → Render auto-redeploys!

---

## ✅ **YOUR API IS NOW LIVE!**

**URL:** `https://backend-api.onrender.com/api/`

**Test it:**
```bash
# Get categories (no auth needed)
https://backend-api.onrender.com/api/categories/

# Should return 27 categories! ✅
```

---

## 🔗 **CONNECT TO VERCEL FRONTEND**

### **Step 1: Get Your Render URL**

From Render dashboard, copy your service URL:
```
https://backend-api.onrender.com
```

### **Step 2: Update CORS in Render**

Go back to Render → **Environment** tab:

Update `CORS_ALLOWED_ORIGINS`:
```
https://your-actual-frontend-url.vercel.app,http://localhost:3000
```

**Save Changes** (auto-redeploys)

### **Step 3: Add to Vercel**

In Vercel project → **Settings** → **Environment Variables**:

**Add:**
```
NEXT_PUBLIC_API_URL = https://backend-api.onrender.com
```

**Redeploy frontend** → Done! 🎉

---

## ⚠️ **IMPORTANT: Render Free Tier Limitations**

### **Sleep After 15 Minutes Inactivity:**

**Problem:**
- Free tier spins down after 15 min of no requests
- First request after sleep takes ~30 seconds (cold start)

**Solution:**
Use a ping service to keep it awake:

1. **UptimeRobot** (Free): https://uptimerobot.com/
   - Add monitor: `https://backend-api.onrender.com/api/categories/`
   - Ping every 5 minutes
   - Keeps your API awake! ✅

2. **Cron-job.org** (Free): https://cron-job.org/
   - Create job to ping your API every 10 minutes

**Or:** Accept the cold start (30 sec delay after inactivity)

---

## 📊 **WHAT RENDER WILL DO**

When you deploy:

1. ✅ Read `render.yaml` configuration
2. ✅ Create PostgreSQL database (free tier)
3. ✅ Install Python 3.12.1
4. ✅ Install dependencies from requirements.txt
5. ✅ Collect static files
6. ✅ Run database migrations
7. ✅ Populate 27 event categories
8. ✅ Start Gunicorn server
9. ✅ Assign public URL with HTTPS
10. ✅ Auto-redeploy on Git push

---

## 🧪 **TESTING YOUR DEPLOYMENT**

### **Test 1: Categories (No Auth)**
```bash
curl https://backend-api.onrender.com/api/categories/
```

**Expected:** JSON with 27 categories

---

### **Test 2: Events (Requires Auth)**
```bash
# Should return 401 Unauthorized
curl https://backend-api.onrender.com/api/events/
```

**Expected:** `{"detail": "Authentication credentials were not provided."}`

---

### **Test 3: Login**
```bash
curl -X POST https://backend-api.onrender.com/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'
```

---

### **Test 4: CORS from Vercel**

In browser console on your Vercel app:
```javascript
fetch('https://backend-api.onrender.com/api/categories/')
  .then(r => r.json())
  .then(console.log)
```

**Should work without CORS errors!** ✅

---

## 🔧 **TROUBLESHOOTING**

### **Issue: "Build failed"**

**Check Render logs:**
- Dashboard → Logs → Build Logs

**Common fixes:**
- Missing dependencies in requirements.txt
- Python version mismatch
- Syntax errors in code

---

### **Issue: "Service unavailable"**

**Cause:** App is sleeping (free tier)

**Solutions:**
1. First request after sleep takes 30 sec (be patient)
2. Set up UptimeRobot to ping every 5 min
3. Upgrade to paid plan ($7/month - no sleep)

---

### **Issue: CORS errors**

**Check:**
1. Is your Vercel URL in `CORS_ALLOWED_ORIGINS`?
2. Does it include `https://`?
3. No trailing slash in URL?

**Update in Render:**
```
CORS_ALLOWED_ORIGINS=https://your-exact-url.vercel.app,http://localhost:3000
```

---

### **Issue: Database errors**

**Solution:**
- Ensure PostgreSQL database is created
- Check `DATABASE_URL` is in environment variables
- View logs for migration errors

---

### **Issue: 500 Internal Server Error**

**Check:**
1. Render logs for actual error
2. SECRET_KEY is set
3. DEBUG=False
4. ALLOWED_HOSTS includes `.onrender.com`

---

## 📱 **RENDER DASHBOARD**

After deployment, you can:

- ✅ View logs (Build + Runtime)
- ✅ See deployment history
- ✅ Monitor resource usage
- ✅ Configure custom domains
- ✅ Set up environment variables
- ✅ Manually trigger redeployment

---

## 🔄 **AUTO-DEPLOYMENT**

Render auto-deploys when you:
- Push to main branch on GitHub
- Manually click "Manual Deploy" in dashboard

**No need to redeploy manually!** 🔄

---

## 💡 **PRO TIPS**

### **1. Keep It Awake (Free Tier)**

Create this in your frontend to ping backend every 10 minutes:

```javascript
// In your frontend (optional)
useEffect(() => {
  // Ping backend every 10 minutes to prevent sleep
  const interval = setInterval(() => {
    fetch(`${API_URL}/api/categories/`).catch(() => {});
  }, 10 * 60 * 1000); // 10 minutes

  return () => clearInterval(interval);
}, []);
```

### **2. Monitor Uptime**

Use UptimeRobot (free):
- Monitor URL: `https://backend-api.onrender.com/api/categories/`
- Check interval: 5 minutes
- Get email alerts if down

### **3. Custom Domain (Free!)**

In Render:
- Settings → Custom Domain
- Add: `api.yourdomain.com`
- Follow DNS instructions
- SSL auto-configured!

---

## 📊 **RENDER FREE TIER**

**What You Get:**
- ✅ 750 hours/month (enough for one app)
- ✅ PostgreSQL database (90 days, then expired)
- ✅ Automatic HTTPS
- ✅ Custom domains
- ✅ Auto-deploy from GitHub
- ✅ View logs

**Limitations:**
- ⚠️ Spins down after 15 min inactivity
- ⚠️ Cold start: ~30 seconds
- ⚠️ Database expires after 90 days (then need to upgrade or export data)

**For MVP/Testing:** Perfect! ✅  
**For Production:** Consider $7/month plan (no sleep)

---

## 🎉 **DEPLOYMENT CHECKLIST**

- [ ] Code pushed to GitHub
- [ ] Signed up on Render.com
- [ ] Created Blueprint or Web Service
- [ ] PostgreSQL database created
- [ ] Environment variables set
- [ ] Deployment succeeded
- [ ] Tested: `https://your-app.onrender.com/api/categories/`
- [ ] CORS works from Vercel
- [ ] Can login from frontend
- [ ] Can create events from frontend

---

## 🚀 **YOU'RE READY!**

**All files configured. Just:**

1. Push to GitHub
2. Go to Render.com
3. Connect repository
4. Deploy!

**See you on the other side!** 🎉

**Your API URL will be:** `https://[your-app-name].onrender.com/api/`

---

## 📞 **NEED HELP?**

**Common Issues:**
- Build errors → Check Render logs
- Database errors → Verify PostgreSQL is linked
- CORS errors → Check ALLOWED_ORIGINS
- 500 errors → Check SECRET_KEY is set

**Render Support:**
- Docs: https://render.com/docs
- Community: https://community.render.com/

---

**Good luck with Render! 🚀**

