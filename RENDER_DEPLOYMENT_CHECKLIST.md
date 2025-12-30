# Quick Render Deployment Checklist

## Pre-Deployment

- [ ] All code committed and pushed to GitHub
- [ ] `.env.example` created with required variables
- [ ] `render.yaml` and `Procfile` are configured
- [ ] `requirements.txt` has all dependencies

## Deployment Steps

### 1. Prepare Google OAuth
- [ ] Have Google Client ID ready
- [ ] Have Google Client Secret ready
- [ ] Note your future Render URL

### 2. Create Render Account
- [ ] Go to https://render.com
- [ ] Sign up with GitHub
- [ ] Connect your GitHub repository

### 3. Deploy on Render
- [ ] Click "New +" → "Web Service"
- [ ] Select your LMS repository
- [ ] Set Name: `adaptive-learning-poc`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Click "Create Web Service"
- [ ] Wait for deployment (2-5 minutes)

### 4. Configure Environment Variables
Go to Settings → Environment Variables and add:

```
SESSION_SECRET = [generate with: python -c "import secrets; print(secrets.token_hex(32))"]
GOOGLE_CLIENT_ID = [your client ID]
GOOGLE_CLIENT_SECRET = [your client secret]
```

- [ ] SESSION_SECRET added
- [ ] GOOGLE_CLIENT_ID added
- [ ] GOOGLE_CLIENT_SECRET added

### 5. Update Google OAuth Settings
- [ ] Go to Google Cloud Console
- [ ] Add to Authorized Redirect URIs: `https://your-app-name.onrender.com/auth/callback`
- [ ] Save changes

### 6. Test Deployment
- [ ] Visit your Render URL
- [ ] Test Google login with teacher account
- [ ] Test Google login with student account
- [ ] Create a learning flow
- [ ] Answer questions to test adaptive learning

### 7. Prepare for Assignment Submission
- [ ] Verify your deployed URL is working
- [ ] Test all features (login, create flow, answer questions)
- [ ] Note your Render URL for submission

## Your Deployed URL
(You'll get this from Render after deployment)
```
https://adaptive-learning-poc.onrender.com
```

## Troubleshooting

### Application won't start?
- Check logs in Render dashboard
- Verify environment variables are set
- Check that Python version is 3.11

### Google login not working?
- Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
- Verify redirect URI in Google Cloud Console
- Check that app is using https

### Database issues?
- Click "Manual Deploy" to reinitialize
- Database is ephemeral on free plan (resets after restart)

## Support

- Render docs: https://render.com/docs
- FastAPI docs: https://fastapi.tiangolo.com
- Google OAuth: https://developers.google.com/identity/protocols/oauth2
