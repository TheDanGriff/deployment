# Quick Fix for ModuleNotFoundError: cv2

## The Problem
Streamlit Cloud can't find OpenCV (`cv2`) because the requirements file is missing or incorrect.

## The Solution
I've created `deployment/requirements.txt` with all necessary dependencies.

## What You Need to Do

1. **Push the new requirements.txt file to GitHub:**
   ```bash
   cd deployment
   git add requirements.txt
   git commit -m "Add requirements.txt with OpenCV dependencies"
   git push
   ```

2. **Update Streamlit Cloud Settings (if needed):**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click on your app → "Manage app"
   - Click "Settings" → "Advanced settings"
   - Under "Requirements file", make sure it's set to:
     - `deployment/requirements.txt` (if your app is in deployment folder)
     - OR `requirements.txt` (if in root)
   - Click "Save"

3. **Redeploy:**
   - Streamlit Cloud will automatically redeploy when you push changes
   - Or manually trigger a redeploy from the app dashboard

## Why This Works

- `opencv-python-headless>=4.9.0` - Headless version perfect for cloud (no GUI dependencies)
- All other dependencies are minimal and necessary
- `requirements.txt` is the standard name Streamlit Cloud looks for

## Verify It Works

After redeploying, check:
- ✅ App loads without errors
- ✅ No more `ModuleNotFoundError: cv2`
- ✅ Videos can be loaded and displayed

