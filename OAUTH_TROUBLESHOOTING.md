# Google OAuth Redirect URI Mismatch - Troubleshooting

## Error: `Error 400: redirect_uri_mismatch`

You're still seeing this. The fix is deployed, but **Render may not have redeployed yet**.

## CRITICAL: Force Redeploy on Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click on "adaptive-learning" service**
3. **Scroll to bottom, click "Manual Deploy"**
4. **Select branch: "main"**
5. **Wait 3-5 minutes for deployment**
6. **Check deployment logs** to confirm success

## During Redeployment
You'll see something like:
```
Building Docker image...
Installing dependencies...
Deploying...
[Your service] is live
```

## After Redeployment: Test

1. **Clear browser cookies** (Important!)
   - Go to Settings > Privacy > Cookies
   - Clear all for lms-k2f0.onrender.com

2. **Visit**: https://lms-k2f0.onrender.com
3. **Click "Login with Google"**
4. **Should see Google login screen** (not the error)

## If Still Getting Error

The issue might be in Google Cloud Console. Check:

### Step 1: Verify Redirect URI in Google Console
1. Go to: https://console.cloud.google.com/
2. Select your project
3. Go to: **APIs & Services > Credentials**
4. Click your OAuth 2.0 Client ID
5. Under **Authorized Redirect URIs**, ensure you have:
   ```
   https://lms-k2f0.onrender.com/auth/callback
   ```
   
   ⚠️ Important:
   - Must be HTTPS (not HTTP)
   - Must match exactly
   - No trailing slash

### Step 2: Check Client ID & Secret
In your Render environment variables, verify:
- `GOOGLE_CLIENT_ID` is correct
- `GOOGLE_CLIENT_SECRET` is correct

To fix:
1. Go to Render Service Settings
2. Find Environment Variables
3. Double-check the values

### Step 3: Create New OAuth Credentials (If Needed)

If you think the credentials are wrong:
1. Go to Google Cloud Console
2. Create a **new OAuth 2.0 Client ID**
3. Add Authorized Redirect URI: `https://lms-k2f0.onrender.com/auth/callback`
4. Copy the new Client ID and Secret
5. Update in Render environment variables
6. Manual deploy again

## Debug: Check What URI App is Sending

The app now sends redirect URI like:
```
https://lms-k2f0.onrender.com/auth/callback
```

This should match **exactly** what's in Google Console.

## If Everything Looks Good

Sometimes Google takes a few minutes to sync. Try:
1. **Wait 5 minutes**
2. **Clear ALL browser cache**
   - Cmd+Shift+Delete
   - Select "All time"
   - Check all boxes
   - Clear
3. **Try again**

## Still Stuck?

Check Render logs:
1. Dashboard > Select service
2. Click "Logs" tab
3. Look for any error messages
4. Copy the error and fix accordingly

The OAuth should work now! ✅
