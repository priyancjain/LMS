# Fix Google OAuth Redirect URI Mismatch Error

## The Problem

You got error: `Error 400: redirect_uri_mismatch`

This happens because:
1. Your Render app uses HTTPS (https://lms-k2f0.onrender.com)
2. But the app was generating HTTP redirect URIs internally
3. Google OAuth requires the redirect URI to match **exactly**

## The Solution

I've fixed the code in `auth.py` to:
1. Detect when running on Render (or Heroku)
2. Automatically convert HTTP to HTTPS
3. Send the correct redirect URI to Google

## Steps to Deploy the Fix

1. **Render will auto-deploy** from the Git push, OR manually:
   - Go to https://dashboard.render.com
   - Select your "adaptive-learning" service
   - Click "Manual Deploy"
   - Select "main" branch

2. **Wait for deployment** (2-5 minutes)

3. **Test Google login:**
   - Go to https://lms-k2f0.onrender.com
   - Click login with Google
   - You should see Google login screen (not the error)

## What Was Added to Google OAuth

In Google Cloud Console, make sure these Authorized Redirect URIs are set:

```
https://lms-k2f0.onrender.com/auth/callback
```

(The app now automatically converts to HTTPS, so this should match)

## If It Still Doesn't Work

1. **Check Google Console** - Go to:
   - https://console.cloud.google.com/
   - Select your project
   - APIs & Services > Credentials
   - Click on your OAuth 2.0 Client ID
   - Under "Authorized redirect URIs", verify:
     ```
     https://lms-k2f0.onrender.com/auth/callback
     ```

2. **Check Render Logs** - In Render dashboard:
   - Click on your service
   - Click "Logs"
   - Look for any error messages

3. **Manual test locally** (before deploying):
   ```bash
   # Run locally
   python -m uvicorn main:app --reload
   
   # Visit http://localhost:8000
   # Try logging in - should work with local redirect URI
   ```

## Technical Details

The fix detects:
- `onrender.com` domain → Use HTTPS
- `herokuapp.com` domain → Use HTTPS
- `localhost` → Use HTTP (for local development)

This ensures the redirect URI sent to Google matches what you've registered in Google Cloud Console.
