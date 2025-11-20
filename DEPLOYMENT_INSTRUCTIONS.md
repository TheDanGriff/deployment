# Deployment Instructions

## Minimal Deployment Folder Ready for GitHub

The `deployment/` folder contains everything needed for Streamlit Cloud deployment with minimal file size.

### What's Included

✅ **Essential files only:**
- `app.py` - Streamlit application (no pose estimation libraries needed)
- `requirements-app.txt` - Minimal dependencies (OpenCV, Streamlit, NumPy, Pillow)
- `.streamlit/config.toml` - Syracuse theme configuration
- `.gitignore` - Excludes large video files
- Directory structure with `.gitkeep` files

❌ **Not included (to save space):**
- Video files (excluded by .gitignore)
- Source code for pose estimation (not needed at runtime)
- Processing scripts (not needed for deployment)
- Raw videos (too large)

### Steps to Deploy

1. **Navigate to deployment folder:**
   ```bash
   cd deployment
   ```

2. **Initialize Git repository (if not already):**
   ```bash
   git init
   ```

3. **Add files:**
   ```bash
   git add .
   git commit -m "Initial commit: Streamlit deployment ready"
   ```

4. **Create GitHub repository and push:**
   ```bash
   git remote add origin https://github.com/TheDanGriff/running-shoe-comparison.git
   git branch -M main
   git push -u origin main
   ```

5. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select repository: `TheDanGriff/running-shoe-comparison`
   - Main file path: `app.py`
   - Python version: 3.11
   - Requirements file: `requirements-app.txt`
   - Click "Deploy"

### Adding Videos Later

**Option 1: Git LFS (Recommended)**
```bash
git lfs install
git lfs track "data/processed_videos/**/*.mp4"
git add .gitattributes
git add data/processed_videos/
git commit -m "Add processed videos via Git LFS"
git push
```

**Option 2: External Storage**
- Store videos in cloud storage (S3, Google Cloud, etc.)
- Update app.py to download from cloud storage

**Option 3: Manual Upload**
- After deployment, upload videos via Streamlit's file uploader

### File Size Comparison

- **Original folder:** ~hundreds of MBs (with videos)
- **Deployment folder:** ~50-100 KB (without videos)
- **Saves significant space for Git/GitHub**

### Verification

After deployment, check:
- ✅ App loads at Streamlit Cloud URL
- ✅ Directory structure exists
- ✅ Videos can be added via Git LFS or external storage

