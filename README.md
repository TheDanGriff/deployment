# Running Biomechanics Comparison App

Streamlit Cloud deployment for running biomechanics video comparison.

## Quick Start

1. **Deploy to Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set Main file: `app.py`
   - Set Python version: 3.11
   - Set Requirements file: `requirements-app.txt`
   - Click Deploy

2. **Add Processed Videos:**
   - Upload processed videos to `data/processed_videos/videos_with_overlay/`
   - Upload pose data JSON to `data/processed_videos/pose_data/`
   - Use Git LFS for large files, or upload via external storage

## Files Included

- `app.py` - Main Streamlit application
- `requirements-app.txt` - Minimal dependencies (no pose estimation libraries)
- `.streamlit/config.toml` - Streamlit configuration with Syracuse theme

## Directory Structure

```
deployment/
├── app.py
├── requirements-app.txt
├── .gitignore
├── .streamlit/
│   └── config.toml
└── data/
    └── processed_videos/
        ├── videos_with_overlay/    # Processed videos with pose overlay
        ├── videos_keypoints_only/  # Skeleton-only videos
        └── pose_data/              # Pose estimation JSON files
```

## Notes

- This deployment package contains **only the app** - no video processing
- Videos must be processed separately using `process_all_videos.py`
- The app displays pre-processed videos only
- Use Git LFS for large video files or external cloud storage

