# Static Files on Render

## Overview

Your FastAPI application automatically serves static files from the `static/` directory. On Render, no additional configuration is needed beyond what's already in place.

## How Static Files Are Served

In `main.py`, this line handles static files:
```python
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
```

This automatically serves:
- CSS files: `/static/style.css`
- Images (if added): `/static/images/*`
- JavaScript (if added): `/static/js/*`

## File Structure

```
project/
├── static/
│   └── style.css          ← Served at /static/style.css
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── question.html
│   ├── student_dashboard.html
│   ├── teacher_dashboard.html
│   └── summary.html
├── main.py                ← Mounts static files
└── render.yaml            ← Render configuration
```

## On Render

### Start Command
```
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
```

The `--workers 1` is important for free tier to avoid memory issues.

### Static Files Behavior
- Automatically cached by browser with versioning
- Served with correct MIME types
- CORS headers are handled correctly

## Adding New Static Files

1. **Add files to `static/` directory:**
   ```
   static/
   ├── style.css
   ├── js/
   │   └── script.js
   ├── images/
   │   └── logo.png
   ```

2. **Reference in templates:**
   ```html
   <!-- CSS -->
   <link rel="stylesheet" href="/static/style.css">
   
   <!-- JavaScript -->
   <script src="/static/js/script.js"></script>
   
   <!-- Images -->
   <img src="/static/images/logo.png" alt="Logo">
   ```

3. **Push to GitHub:**
   ```bash
   git add static/
   git commit -m "Add new static assets"
   git push origin main
   ```

4. **Render auto-deploys** - Static files are included automatically

## For Production with Large Assets

If you have large assets or many files:

1. **Use CDN (recommended):**
   - AWS CloudFront
   - Cloudflare
   - Bunny CDN
   
2. **Configure in templates:**
   ```html
   <link rel="stylesheet" href="https://cdn.example.com/style.css">
   ```

3. **Environment variable approach:**
   ```python
   import os
   CDN_URL = os.getenv("CDN_URL", "/static")
   
   # In templates:
   <!-- <link rel="stylesheet" href="{{ CDN_URL }}/style.css"> -->
   ```

## Troubleshooting Static Files on Render

### CSS/Images not loading?

1. **Check browser console** for 404 errors
2. **Verify file exists** in `static/` directory
3. **Check file path** in template:
   ```html
   <!-- ✅ Correct -->
   <link rel="stylesheet" href="/static/style.css">
   
   <!-- ❌ Wrong -->
   <link rel="stylesheet" href="static/style.css">
   <link rel="stylesheet" href="./style.css">
   ```

4. **Check Render logs** for any errors during build

### Files were added but not showing?

1. Ensure files are committed to Git:
   ```bash
   git status
   git add static/
   git commit -m "Add static files"
   git push origin main
   ```

2. Trigger manual deploy on Render:
   - Go to Service Settings
   - Click "Manual Deploy"
   - Select "main" branch

### Performance Issues?

1. **Compress CSS/Images:**
   ```bash
   # Minimize CSS
   npm install -g cssnano-cli
   cssnano style.css -o style.min.css
   ```

2. **Use cache headers:**
   - FastAPI automatically handles caching
   - Browser caches static assets

3. **Lazy load images:**
   ```html
   <img src="/static/image.png" loading="lazy" alt="Description">
   ```

## Current Static Files

Your project includes:
- ✅ `style.css` - Styling for all pages

## Adding More Static Files

Examples of what you can add:

1. **JavaScript** - Add interactivity:
   ```bash
   mkdir -p static/js
   # Create static/js/main.js
   ```

2. **Images** - Logos, icons:
   ```bash
   mkdir -p static/images
   # Add PNG, JPG, SVG files
   ```

3. **Icons** - Bootstrap Icons or similar:
   ```html
   <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css">
   ```

## Summary

✅ Static files are automatically served from the `static/` directory
✅ No additional Render configuration needed
✅ All files in `static/` are deployed automatically
✅ Use `/static/filename` path in templates
✅ Push changes to Git for auto-deployment on Render
