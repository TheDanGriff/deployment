# Deployment Folder - Ready to Deploy!

This folder contains everything needed to deploy the Running Biomechanics Comparison app to Streamlit Cloud.

## Setup Videos

To copy processed videos to this folder, run from the deployment folder:

```bash
cd deployment
python copy_videos.py
```

This will copy all processed videos from `../data/processed_videos/` to `deployment/data/processed_videos/`.

## Files Included

- `app.py` - Streamlit application
- `requirements.txt` - Dependencies
- `copy_videos.py` - Script to copy videos

## After Copying Videos

1. Use Git LFS for large files:
   ```bash
   git lfs install
   git lfs track "deployment/data/**/*.mp4"
   git lfs track "deployment/data/**/*.json"
   git add .gitattributes deployment/
   git commit -m "Add deployment with videos"
   git push
   ```

2. Deploy on Streamlit Cloud with main file: `deployment/app.py`
