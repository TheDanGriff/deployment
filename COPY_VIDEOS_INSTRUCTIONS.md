# Instructions to Copy Processed Videos to Deployment

## Quick Copy Script

I've created a PowerShell script to copy all processed videos to the deployment folder.

### Step 1: Run the Copy Script

From the project root directory:

```powershell
.\copy_processed_videos_to_deployment.ps1
```

This will:
- ✅ Copy all overlay videos (`*_overlay.mp4`)
- ✅ Copy all keypoints videos (`*_keypoints.mp4`)
- ✅ Copy all pose data JSON files (`*_pose_data.json`)
- ✅ Create the correct directory structure in `deployment/data/processed_videos/`

### Step 2: Use Git LFS for Large Files

**IMPORTANT:** Video files are large (tens to hundreds of MBs). You MUST use Git LFS to track them.

```bash
# Install Git LFS (if not already installed)
git lfs install

# Track video files
git lfs track "deployment/data/**/*.mp4"
git lfs track "deployment/data/**/*.json"

# Add .gitattributes file
git add .gitattributes

# Add the deployment folder
git add deployment/

# Commit
git commit -m "Add processed videos to deployment folder"

# Push (will upload via Git LFS)
git push
```

### Step 3: Deploy on Streamlit Cloud

After pushing to GitHub:
1. Streamlit Cloud will automatically detect the new files
2. Videos will be available via Git LFS
3. The app will find the processed videos in `deployment/data/processed_videos/`

## Alternative: Manual Copy

If you prefer to copy manually:

1. **Create directory structure:**
   ```
   deployment/data/processed_videos/
   ├── videos_with_overlay/
   ├── videos_keypoints_only/
   └── pose_data/
   ```

2. **Copy files:**
   - Copy `data/processed_videos/videos_with_overlay/*.mp4` → `deployment/data/processed_videos/videos_with_overlay/`
   - Copy `data/processed_videos/videos_keypoints_only/*.mp4` → `deployment/data/processed_videos/videos_keypoints_only/`
   - Copy `data/processed_videos/pose_data/*.json` → `deployment/data/processed_videos/pose_data/`

## File Sizes

- Each overlay video: ~5-50 MB
- Each keypoints video: ~5-50 MB  
- Each JSON file: ~1-10 MB
- **Total for all 6 videos: ~100-600 MB**

This is why Git LFS is essential!

## Verify After Copy

After copying, check:
```bash
ls deployment/data/processed_videos/videos_with_overlay/
ls deployment/data/processed_videos/videos_keypoints_only/
ls deployment/data/processed_videos/pose_data/
```

You should see:
- 6 overlay videos
- 6 keypoints videos
- 6 pose data JSON files

## Troubleshooting

### "No space left on device"
- Free up disk space before copying
- Copy files one at a time if needed

### Git LFS not installed
- Install from: https://git-lfs.github.com/
- Or use `winget install Git.GitLFS` on Windows

### Large file errors in Git
- Make sure Git LFS is installed and initialized
- Verify `.gitattributes` is tracked
- Check that files are being tracked: `git lfs ls-files`

