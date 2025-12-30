# Deployment Guide - Render.com

This guide will help you deploy the Adaptive Learning System POC to Render.

## Prerequisites

1. GitHub account with the repository pushed
2. Render account (free tier available)
3. Google OAuth credentials

## Step-by-Step Deployment

### 1. Prepare Your Repository

Make sure all files are pushed to GitHub:

```bash
git add render.yaml Procfile
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Create Render Account

1. Go to https://render.com
2. Sign up with your GitHub account (recommended)
3. Connect your GitHub account to Render

### 3. Deploy the Application

1. **Click "New +"** button in Render dashboard
2. **Select "Web Service"**
3. **Connect your GitHub repository**
   - Search for "LMS" repository
   - Click "Connect"
4. **Configure the Web Service:**
   - **Name**: `adaptive-learning-poc`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or upgraded if needed)
5. **Click "Deploy Web Service"**

### 4. Set Environment Variables

After deployment is created, go to **Settings** and add these environment variables:

```
SESSION_SECRET = (generate a secure key: `python -c "import secrets; print(secrets.token_hex(32))"`)
GOOGLE_CLIENT_ID = your_google_client_id
GOOGLE_CLIENT_SECRET = your_google_client_secret
```

To generate SESSION_SECRET locally:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as SESSION_SECRET value.

### 5. Configure Google OAuth

1. Update your Google OAuth app to accept Render URL:
   - Go to Google Cloud Console
   - In your OAuth app settings, add the Render URL to **Authorized redirect URIs**
   - Format: `https://your-app-name.onrender.com/auth/callback`

2. Update environment variables with your Google credentials:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`

### 6. Monitor Deployment

1. In Render dashboard, you'll see deployment logs
2. Wait for build to complete (usually 2-5 minutes)
3. Once successful, you'll get a public URL: `https://your-app-name.onrender.com`

### 7. Initialize Database

The release command in Procfile will automatically initialize the database.

If you need to reinitialize:
1. Go to your Render service settings
2. Click "Manual Deploy"
3. Then restart the service

### 8. Add Sample Data

After deployment is live, run the seed script:

```bash
# Locally, use your deployed URL to add sample data
# Or SSH into Render shell and run:
python seed_flow.py
```

## Important Notes

### Free Tier Limitations

- Application spins down after 15 minutes of inactivity
- First request after spin-down may take 30 seconds
- Limited to 0.5 GB RAM
- Database is ephemeral (data resets when service restarts)

### For Production Use

For production deployment, consider:

1. **Upgrade to Paid Plan**
   - No spin-down
   - More resources
   - Better reliability

2. **Use PostgreSQL Database**
   ```bash
   pip install psycopg2-binary
   ```
   - Replace SQLite with PostgreSQL in models.py
   - Render offers free PostgreSQL tier

3. **Add Error Tracking**
   - Sentry integration
   - Better logging

4. **Enable HTTPS**
   - Render provides automatic HTTPS

### Database Persistence

Currently using SQLite stored locally. For production:

1. Set up Render PostgreSQL addon
2. Update connection string in models.py
3. Data will persist across deployments

## Troubleshooting

### Deployment Fails

1. **Check build logs** in Render dashboard
2. Common issues:
   - Missing requirements - ensure all packages in `requirements.txt`
   - Python version mismatch - check render.yaml
   - Port binding issue - ensure using `$PORT` environment variable

### Application Won't Start

1. Check service logs
2. Verify environment variables are set correctly
3. Check that Google OAuth credentials are valid

### Database Issues

1. Run manual deploy to reinitialize
2. Check Procfile release command

### Google OAuth Not Working

1. Verify redirect URI matches Render URL
2. Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
3. Ensure SSL is working (Render provides free SSL)

## Testing Your Deployment

1. Visit: `https://your-app-name.onrender.com`
2. Test Google login
3. Create a flow as teacher
4. Answer questions as student
5. Verify adaptive learning works

## Monitoring

In Render dashboard:
- View live logs
- Monitor CPU and memory usage
- Check deployment history
- Set up notifications for crashes

## Your Deployment URL

Once deployed, share this URL:
```
https://your-app-name.onrender.com
```

This is what you'll submit for the assignment!

## Next Steps

After successful deployment:
1. Test with teacher and student accounts
2. Create sample flows
3. Verify adaptive learning works
4. Record video walkthrough
5. Submit URL + video to assignment contact
