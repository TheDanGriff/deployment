"""Simple script to copy processed videos to deployment folder."""
import shutil
from pathlib import Path

# Get the deployment folder (where this script is)
deployment_dir = Path(__file__).parent
source_dir = deployment_dir.parent / "data" / "processed_videos"

# Destination in deployment folder
dest_dir = deployment_dir / "data" / "processed_videos"

# Create directories
(dest_dir / "videos_with_overlay").mkdir(parents=True, exist_ok=True)
(dest_dir / "videos_keypoints_only").mkdir(parents=True, exist_ok=True)
(dest_dir / "pose_data").mkdir(parents=True, exist_ok=True)

print("Copying processed videos...")

# Copy overlay videos
overlay_source = source_dir / "videos_with_overlay"
overlay_dest = dest_dir / "videos_with_overlay"
if overlay_source.exists():
    for video_file in overlay_source.glob("*.mp4"):
        dest_file = overlay_dest / video_file.name
        shutil.copy2(video_file, dest_file)
        print(f"  Copied: {video_file.name}")

# Copy keypoints videos
keypoints_source = source_dir / "videos_keypoints_only"
keypoints_dest = dest_dir / "videos_keypoints_only"
if keypoints_source.exists():
    for video_file in keypoints_source.glob("*.mp4"):
        dest_file = keypoints_dest / video_file.name
        shutil.copy2(video_file, dest_file)
        print(f"  Copied: {video_file.name}")

# Copy pose data JSON files
pose_source = source_dir / "pose_data"
pose_dest = dest_dir / "pose_data"
if pose_source.exists():
    for json_file in pose_source.glob("*.json"):
        dest_file = pose_dest / json_file.name
        shutil.copy2(json_file, dest_file)
        print(f"  Copied: {json_file.name}")

print("\nDone! All processed videos copied to deployment folder.")

