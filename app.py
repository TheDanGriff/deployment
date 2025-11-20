"""
Visual Pose Comparison App for Running Analysis

This Streamlit app displays pre-processed videos with pose estimation overlays.
Videos are processed offline using process_all_videos.py for fast playback.
"""

import streamlit as st
import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, Dict
import sys
from PIL import Image
import json
import re
import time

# Page config
st.set_page_config(
    page_title="Running Pose Comparison",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Syracuse colors and styling
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        background-color: #D44500;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #B23900;
        color: white;
    }
    h1 {
        color: #D44500;
        text-align: center;
    }
    h2, h3 {
        color: #002D72;
    }
    .video-container {
        border: 2px solid #D44500;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .metric-card {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #D44500;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'left_frame_idx' not in st.session_state:
    st.session_state.left_frame_idx = 0
if 'right_frame_idx' not in st.session_state:
    st.session_state.right_frame_idx = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'left_playing' not in st.session_state:
    st.session_state.left_playing = False
if 'right_playing' not in st.session_state:
    st.session_state.right_playing = False
if 'playback_speed' not in st.session_state:
    st.session_state.playback_speed = 0.2
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = 0

# Setup paths
BASE_DIR = Path(__file__).parent
RAW_VIDEOS_DIR = BASE_DIR / "data" / "raw_videos"
PROCESSED_DIR = BASE_DIR / "data" / "processed_videos"
OVERLAY_DIR = PROCESSED_DIR / "videos_with_overlay"
KEYPOINTS_DIR = PROCESSED_DIR / "videos_keypoints_only"
POSE_DATA_DIR = PROCESSED_DIR / "pose_data"


def parse_video_name(video_name: str) -> Dict:
    """Parse video name to extract year, athlete name, and gender."""
    # Extract year
    year_match = re.search(r'(\d{4})', video_name)
    year = year_match.group(1) if year_match else "Unknown"
    
    # Extract athlete name and determine gender - remove location references
    video_lower = video_name.lower()
    gender_letter = "?"
    athlete_name = "Unknown"
    
    # Remove location keywords first
    locations = ['london', 'monza', 'berlin', 'chicago', 'new york', 'boston', 'mosop']
    clean_name = video_lower
    for loc in locations:
        clean_name = clean_name.replace(loc, '')
    
    # Determine athlete and gender - simplified names
    if 'kiplagat' in clean_name or 'mosop' in video_lower:
        gender_letter = "F"
        athlete_name = "Kiplagat"
    elif 'kipchoge' in clean_name:
        gender_letter = "M"
        athlete_name = "Kipchoge"
    else:
        # Fallback: try to parse from filename
        parts = video_name.replace('_', ' ').split()
        # Remove year and locations
        name_parts = [p for p in parts if not p.isdigit() and p.lower() not in locations]
        if name_parts:
            athlete_name = name_parts[0].title()
    
    return {
        'year': year,
        'name': athlete_name,
        'gender': gender_letter,
        'display_name': f"{athlete_name} ({year}) ({gender_letter})"
    }


def get_video_files(video_dir: Path) -> list:
    """Get list of video files from directory."""
    video_extensions = ['.mov', '.mp4', '.avi', '.mkv', '.MOV', '.MP4']
    videos = []
    for ext in video_extensions:
        videos.extend(video_dir.glob(f"*{ext}"))
    return sorted([v.stem for v in videos])


def get_processed_video_path(video_name: str, view_type: str = 'overlay') -> Optional[Path]:
    """
    Get path to processed video.
    
    Args:
        video_name: Name of video (without extension)
        view_type: 'overlay' or 'keypoints'
    """
    if view_type == 'overlay':
        overlay_path = OVERLAY_DIR / f"{video_name}_overlay.mp4"
        if overlay_path.exists():
            return overlay_path
        # Fallback to keypoints if overlay doesn't exist
        keypoints_path = KEYPOINTS_DIR / f"{video_name}_keypoints.mp4"
        if keypoints_path.exists():
            return keypoints_path
    elif view_type == 'keypoints':
        keypoints_path = KEYPOINTS_DIR / f"{video_name}_keypoints.mp4"
        if keypoints_path.exists():
            return keypoints_path
        # Fallback to overlay if keypoints doesn't exist
        overlay_path = OVERLAY_DIR / f"{video_name}_overlay.mp4"
        if overlay_path.exists():
            return overlay_path
    
    return None


@st.cache_data(show_spinner=False)
def load_video_frame_cached(video_path_str: str, frame_number: int) -> Optional[np.ndarray]:
    """Load a video frame with caching."""
    video_path = Path(video_path_str)
    if not video_path or not video_path.exists():
        return None
    
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        cap.release()
        return None
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_number = min(frame_number, total_frames - 1) if total_frames > 0 else 0
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    cap.release()
    
    if not ret or frame is None:
        return None
    
    # Resize to standard height for consistent display
    standard_height = 500
    height, width = frame.shape[:2]
    if height != standard_height:
        scale = standard_height / height
        new_width = int(width * scale)
        frame = cv2.resize(frame, (new_width, standard_height), interpolation=cv2.INTER_AREA)
    
    return frame


def get_video_frame(video_path: Path, frame_number: int) -> Optional[np.ndarray]:
    """Get a specific frame from video (wrapper with caching)."""
    if video_path is None:
        return None
    return load_video_frame_cached(str(video_path), frame_number)


def get_video_info(video_path: Path) -> Dict:
    """Get video information."""
    if not video_path or not video_path.exists():
        return {'fps': 30, 'frame_count': 0, 'width': 0, 'height': 0}
    
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return {'fps': 30, 'frame_count': 0, 'width': 0, 'height': 0}
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    cap.release()
    
    return {
        'fps': fps,
        'frame_count': frame_count,
        'width': width,
        'height': height
    }


def load_pose_data(video_name: str) -> Optional[Dict]:
    """Load pose data JSON for a video."""
    pose_data_path = POSE_DATA_DIR / f"{video_name}_pose_data.json"
    if not pose_data_path.exists():
        return None
    
    try:
        with open(pose_data_path, 'r') as f:
            return json.load(f)
    except Exception:
        return None


# Check if processed videos exist
processed_videos_exist = OVERLAY_DIR.exists() and any(OVERLAY_DIR.glob("*_overlay.mp4"))

# Header with Syracuse logo/colors
col_header1, col_header2, col_header3 = st.columns([1, 2, 1])
with col_header2:
    st.markdown("<h1 style='text-align: center; color: #D44500; margin-bottom: 0;'> Running Biomechanics Comparison</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #002D72; font-size: 1.1em; margin-top: 0;'>Syracuse University David B. Falk College of Sport</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 2px solid #D44500; margin: 1rem 0;'>", unsafe_allow_html=True)

# Check for processed videos
if not processed_videos_exist:
    st.warning("⚠️ **No processed videos found!**")
    st.info(
        "Please run the batch processing script first:\n\n"
        "```bash\npython process_all_videos.py\n```\n\n"
        "This will process all videos in `data/raw_videos` and create the overlay videos."
    )
    if st.button("Check for Raw Videos"):
        if RAW_VIDEOS_DIR.exists():
            raw_videos = get_video_files(RAW_VIDEOS_DIR)
            if raw_videos:
                st.success(f"Found {len(raw_videos)} raw video(s) ready to process:")
                for v in raw_videos:
                    st.write(f"  - {v}")
            else:
                st.error("No raw videos found in data/raw_videos directory")
        else:
            st.error("Raw videos directory not found")
    st.stop()

# Sidebar
st.sidebar.markdown("<h2 style='color: #002D72;'>Video Selection</h2>", unsafe_allow_html=True)

# Get available processed videos
processed_video_names = []
for overlay_file in OVERLAY_DIR.glob("*_overlay.mp4"):
    video_name = overlay_file.stem.replace("_overlay", "")
    processed_video_names.append(video_name)
processed_video_names = sorted(processed_video_names)

if not processed_video_names:
    st.error("No processed videos found. Please run process_all_videos.py first.")
    st.stop()

# Create video display names with parsed info
video_options = []
video_map = {}  # Maps display name to actual video name
for vname in processed_video_names:
    info = parse_video_name(vname)
    display_name = info['display_name']
    video_options.append(display_name)
    video_map[display_name] = vname

# Default videos - use parsed display names
default_left = None
default_right = None
for vname in processed_video_names:
    info = parse_video_name(vname)
    if info['name'] == 'Kiplagat' and info['year'] == '2009':
        default_left = info['display_name']
    if info['name'] == 'Kipchoge' and info['year'] == '2017':
        default_right = info['display_name']

if default_left is None:
    default_left = video_options[0]
if default_right is None:
    default_right = video_options[1] if len(video_options) > 1 else video_options[0]

# Video selection
selected_left = st.sidebar.selectbox(
    "Video 1:",
    video_options,
    index=video_options.index(default_left) if default_left in video_options else 0,
    key="left_video_select"
)

selected_right = st.sidebar.selectbox(
    "Video 2:",
    video_options,
    index=video_options.index(default_right) if default_right in video_options else (1 if len(video_options) > 1 else 0),
    key="right_video_select"
)

left_video_name = video_map[selected_left]
right_video_name = video_map[selected_right]

# Display settings
st.sidebar.markdown("<h3 style='color: #002D72; margin-top: 2rem;'>Display Settings</h3>", unsafe_allow_html=True)
background_mode = st.sidebar.radio(
    "Background:",
    ["Video Background", "Blank Background"],
    index=0,
    key="background_mode"
)

# Playback controls
st.sidebar.markdown("<h3 style='color: #002D72; margin-top: 1.5rem;'>Playback Controls</h3>", unsafe_allow_html=True)

# Global play/pause for both videos (will use left_info and right_info after they're defined)
play_all_button = st.sidebar.button("▶️ Play All" if not st.session_state.is_playing else "⏸️ Pause All", key="play_all")
if play_all_button:
    st.session_state.is_playing = not st.session_state.is_playing
    st.session_state.left_playing = st.session_state.is_playing
    st.session_state.right_playing = st.session_state.is_playing
    # Time calculation will happen in the display section after left_info/right_info are defined
    st.rerun()

playback_speed = st.sidebar.slider(
    "Playback Speed",
    0.1,
    1.0,
    st.session_state.playback_speed,
    0.05,
    key="speed_slider",
    help="Control how fast videos play back (0.1x = slow, 1.0x = real speed)"
)
st.session_state.playback_speed = playback_speed

# Reset frames button
if st.sidebar.button("Reset to Frame 0"):
    st.session_state.left_frame_idx = 0
    st.session_state.right_frame_idx = 0
    st.session_state.is_playing = False
    st.session_state.left_playing = False
    st.session_state.right_playing = False
    st.session_state.last_update_time = 0
    st.rerun()

# Get video paths based on background mode
left_overlay_path = get_processed_video_path(left_video_name, 'overlay')
left_keypoints_path = get_processed_video_path(left_video_name, 'keypoints')
right_overlay_path = get_processed_video_path(right_video_name, 'overlay')
right_keypoints_path = get_processed_video_path(right_video_name, 'keypoints')

# Parse video info for display
left_info_parsed = parse_video_name(left_video_name)
right_info_parsed = parse_video_name(right_video_name)

# Get video information
left_video_path = left_overlay_path if background_mode == "Video Background" else left_keypoints_path
right_video_path = right_overlay_path if background_mode == "Video Background" else right_keypoints_path

left_info = get_video_info(left_video_path) if left_video_path else {}
right_info = get_video_info(right_video_path) if right_video_path else {}

# Main content area
if not left_video_path or not right_video_path:
    missing = []
    if not left_video_path:
        missing.append(selected_left)
    if not right_video_path:
        missing.append(selected_right)
    st.error(f"Processed video(s) not found: {', '.join(missing)}")
    st.info("Please run process_all_videos.py to process these videos.")
    st.stop()

# Video info cards
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <h4 style='color: #002D72; margin-top: 0;'>{left_info_parsed['display_name']}</h4>
        <p style='margin: 0.25rem 0;'><strong>Frames:</strong> {left_info.get('frame_count', 0)} @ {left_info.get('fps', 30):.1f} fps</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <h4 style='color: #002D72; margin-top: 0;'>{right_info_parsed['display_name']}</h4>
        <p style='margin: 0.25rem 0;'><strong>Frames:</strong> {right_info.get('frame_count', 0)} @ {right_info.get('fps', 30):.1f} fps</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Calculate video limits (after left_info and right_info are defined)
left_max = max(0, left_info.get('frame_count', 0) - 1)
right_max = max(0, right_info.get('frame_count', 0) - 1)
fps_left = left_info.get('fps', 30)
fps_right = right_info.get('fps', 30)

# Handle play all button timing if it was clicked (after fps values are calculated)
if st.session_state.is_playing and 'left_start_time' not in st.session_state:
    st.session_state.left_start_time = time.time() - (st.session_state.left_frame_idx / (fps_left * st.session_state.playback_speed))
    st.session_state.right_start_time = time.time() - (st.session_state.right_frame_idx / (fps_right * st.session_state.playback_speed))

# Create side-by-side columns
col_v1, col_v2 = st.columns(2)

with col_v1:
    st.markdown(f"### {left_info_parsed['display_name']}")
    
    left_frames = left_info.get('frame_count', 0)
    if left_frames > 0:
        left_max = max(0, left_frames - 1)
        
        # Individual play/pause for left video
        col_play_left, col_status_left = st.columns([3, 1])
        with col_play_left:
            left_play_btn = st.button(
                "▶️ Play" if not st.session_state.left_playing else "⏸️ Pause",
                key="left_play_pause"
            )
            if left_play_btn:
                st.session_state.left_playing = not st.session_state.left_playing
                if st.session_state.left_playing:
                    fps_left_val = left_info.get('fps', 30)
                    st.session_state.left_start_time = time.time() - (st.session_state.left_frame_idx / (fps_left_val * st.session_state.playback_speed))
                st.rerun()
        with col_status_left:
            if st.session_state.left_playing:
                st.markdown("<p style='color: #D44500;'>▶️</p>", unsafe_allow_html=True)
        
        # Individual slider for left video
        left_frame_idx = st.slider(
            "Frame",
            0,
            left_max,
            st.session_state.left_frame_idx,
            key="left_frame_slider",
            help=f"Navigate through {left_info_parsed['display_name']}"
        )
        st.session_state.left_frame_idx = left_frame_idx
        
        # Playback controls for left
        col_l1, col_l2, col_l3, col_l4 = st.columns(4)
        with col_l1:
            if st.button("⏮️", key="left_first"):
                st.session_state.left_frame_idx = 0
                st.session_state.left_playing = False
                st.rerun()
        with col_l2:
            if st.button("⏪ -10", key="left_prev10"):
                st.session_state.left_frame_idx = max(0, st.session_state.left_frame_idx - 10)
                st.rerun()
        with col_l3:
            if st.button("⏩ +10", key="left_next10"):
                st.session_state.left_frame_idx = min(left_max, st.session_state.left_frame_idx + 10)
                st.rerun()
        with col_l4:
            if st.button("⏭️", key="left_last"):
                st.session_state.left_frame_idx = left_max
                st.session_state.left_playing = False
                st.rerun()
        
        # Advance frame if playing
        if st.session_state.left_playing and left_max > 0:
            # Calculate frames to advance based on real-time playback
            time_since_start = time.time() if 'left_start_time' not in st.session_state else (time.time() - st.session_state.left_start_time)
            fps_left_val = left_info.get('fps', 30)
            expected_frame = int(time_since_start * fps_left_val * st.session_state.playback_speed) % (left_max + 1)
            st.session_state.left_frame_idx = expected_frame
        else:
            if 'left_start_time' in st.session_state:
                del st.session_state.left_start_time
        
        # Display left video frame
        left_frame = get_video_frame(left_video_path, st.session_state.left_frame_idx)
        
        if left_frame is not None:
            height, width = left_frame.shape[:2]
            st.image(left_frame, use_container_width=False, channels="BGR", width=width)
            
            # Show pose data
            left_pose_data = load_pose_data(left_video_name)
            if left_pose_data and st.session_state.left_frame_idx < len(left_pose_data.get('frames', [])):
                frame_data = left_pose_data['frames'][st.session_state.left_frame_idx]
                if frame_data.get('has_pose'):
                    confidence = frame_data.get('confidence', 0.0)
                    st.caption(f"✓ Pose detected (confidence: {confidence:.2f}) | Frame: {st.session_state.left_frame_idx}/{left_max}")
                else:
                    st.caption(f"✗ No pose detected | Frame: {st.session_state.left_frame_idx}/{left_max}")
        else:
            st.error("Could not load frame")
    else:
        st.info("Video processing in progress...")

with col_v2:
    st.markdown(f"### {right_info_parsed['display_name']}")
    
    right_frames = right_info.get('frame_count', 0)
    if right_frames > 0:
        right_max = max(0, right_frames - 1)
        
        # Individual play/pause for right video
        col_play_right, col_status_right = st.columns([3, 1])
        with col_play_right:
            right_play_btn = st.button(
                "▶️ Play" if not st.session_state.right_playing else "⏸️ Pause",
                key="right_play_pause"
            )
            if right_play_btn:
                st.session_state.right_playing = not st.session_state.right_playing
                if st.session_state.right_playing:
                    st.session_state.right_start_time = time.time() - (st.session_state.right_frame_idx / (fps_right * st.session_state.playback_speed))
                st.rerun()
        with col_status_right:
            if st.session_state.right_playing:
                st.markdown("<p style='color: #D44500;'>▶️</p>", unsafe_allow_html=True)
        
        # Individual slider for right video
        right_frame_idx = st.slider(
            "Frame",
            0,
            right_max,
            st.session_state.right_frame_idx,
            key="right_frame_slider",
            help=f"Navigate through {right_info_parsed['display_name']}"
        )
        st.session_state.right_frame_idx = right_frame_idx
        
        # Playback controls for right
        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        with col_r1:
            if st.button("⏮️", key="right_first"):
                st.session_state.right_frame_idx = 0
                st.session_state.right_playing = False
                st.rerun()
        with col_r2:
            if st.button("⏪ -10", key="right_prev10"):
                st.session_state.right_frame_idx = max(0, st.session_state.right_frame_idx - 10)
                st.rerun()
        with col_r3:
            if st.button("⏩ +10", key="right_next10"):
                st.session_state.right_frame_idx = min(right_max, st.session_state.right_frame_idx + 10)
                st.rerun()
        with col_r4:
            if st.button("⏭️", key="right_last"):
                st.session_state.right_frame_idx = right_max
                st.session_state.right_playing = False
                st.rerun()
        
        # Advance frame if playing
        if st.session_state.right_playing and right_max > 0:
            # Calculate frames to advance based on real-time playback
            time_since_start = time.time() if 'right_start_time' not in st.session_state else (time.time() - st.session_state.right_start_time)
            fps_right_val = right_info.get('fps', 30)
            expected_frame = int(time_since_start * fps_right_val * st.session_state.playback_speed) % (right_max + 1)
            st.session_state.right_frame_idx = expected_frame
        else:
            if 'right_start_time' in st.session_state:
                del st.session_state.right_start_time
        
        # Display right video frame
        right_frame = get_video_frame(right_video_path, st.session_state.right_frame_idx)
        
        if right_frame is not None:
            height, width = right_frame.shape[:2]
            st.image(right_frame, use_container_width=False, channels="BGR", width=width)
            
            # Show pose data
            right_pose_data = load_pose_data(right_video_name)
            if right_pose_data and st.session_state.right_frame_idx < len(right_pose_data.get('frames', [])):
                frame_data = right_pose_data['frames'][st.session_state.right_frame_idx]
                if frame_data.get('has_pose'):
                    confidence = frame_data.get('confidence', 0.0)
                    st.caption(f"✓ Pose detected (confidence: {confidence:.2f}) | Frame: {st.session_state.right_frame_idx}/{right_max}")
                else:
                    st.caption(f"✗ No pose detected | Frame: {st.session_state.right_frame_idx}/{right_max}")
        else:
            st.error("Could not load frame")
    else:
        st.info("Video processing in progress...")

# Pose statistics (collapsible)
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📊 Pose Detection Statistics", expanded=False):
    left_pose_data = load_pose_data(left_video_name)
    right_pose_data = load_pose_data(right_video_name)
    
    stat_col1, stat_col2 = st.columns(2)
    
    with stat_col1:
        st.markdown(f"**{left_info_parsed['display_name']}**")
        if left_pose_data:
            total_frames = left_pose_data.get('total_frames', 0)
            successful = sum(1 for f in left_pose_data.get('frames', []) if f.get('has_pose'))
            success_rate = successful / total_frames if total_frames > 0 else 0
            avg_confidence = np.mean([
                f.get('confidence', 0) for f in left_pose_data.get('frames', [])
                if f.get('has_pose')
            ]) if successful > 0 else 0
            
            st.metric("Detection Rate", f"{success_rate:.1%}")
            st.metric("Avg Confidence", f"{avg_confidence:.2f}")
            st.metric("Total Frames", total_frames)
        else:
            st.info("Statistics not available")
    
    with stat_col2:
        st.markdown(f"**{right_info_parsed['display_name']}**")
        if right_pose_data:
            total_frames = right_pose_data.get('total_frames', 0)
            successful = sum(1 for f in right_pose_data.get('frames', []) if f.get('has_pose'))
            success_rate = successful / total_frames if total_frames > 0 else 0
            avg_confidence = np.mean([
                f.get('confidence', 0) for f in right_pose_data.get('frames', [])
                if f.get('has_pose')
            ]) if successful > 0 else 0
            
            st.metric("Detection Rate", f"{success_rate:.1%}")
            st.metric("Avg Confidence", f"{avg_confidence:.2f}")
            st.metric("Total Frames", total_frames)
        else:
            st.info("Statistics not available")

# Footer
st.sidebar.markdown("<hr style='border: 1px solid #D44500; margin: 2rem 0;'>", unsafe_allow_html=True)
st.sidebar.markdown(f"<p style='color: #002D72;'><strong>{len(processed_video_names)}</strong> video(s) available</p>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size: 0.9em; color: #666;'>Biomechanics Analysis Tool<br>Syracuse University</p>", unsafe_allow_html=True)

# Auto-refresh if any video is playing
if st.session_state.left_playing or st.session_state.right_playing or st.session_state.is_playing:
    # Refresh at ~30fps for smooth playback
    refresh_rate = 0.033  # 30fps
    time.sleep(refresh_rate)
    st.rerun()

