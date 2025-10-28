import os
import shutil
import tempfile
import ffmpeg
import cv2
import requests
import numpy as np
import librosa
from typing import List, Dict

from .job_manager import job_manager
from .cloudinary_upload import upload_to_cloudinary

def download_file(url: str, temp_dir: str) -> str:
    """Downloads a file from a URL to a temporary directory."""
    local_filename = os.path.join(temp_dir, url.split('/')[-1])
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def trim_silences(video_path: str) -> str:
    """Trims silences from a video clip using ffmpeg-python."""
    output_path = video_path.replace(".mp4", "_trimmed.mp4")

    # Use ffmpeg to detect silences. This is a complex operation and this
    # implementation is a simplified version. A more robust solution would
    # parse the output of silencedetect to find all silent segments.
    (
        ffmpeg
        .input(video_path)
        .filter('silenceremove', start_periods=1, start_duration=0.5, start_threshold='-50dB')
        .output(output_path)
        .run(overwrite_output=True)
    )
    return output_path


def detect_highlights(video_path: str) -> List[Dict[str, float]]:
    """Detects highlight sections in a video clip based on motion."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Error opening video file: {video_path}")

    highlights = []
    prev_frame = None
    frame_diffs = []
    fps = cap.get(cv2.CAP_PROP_FPS)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if prev_frame is not None:
            diff_frame = cv2.absdiff(prev_frame, gray)
            frame_diffs.append(np.sum(diff_frame))
        prev_frame = gray
    cap.release()

    if not frame_diffs:
        return []

    threshold = np.percentile(frame_diffs, 90)
    in_highlight = False
    start_time = 0.0
    for i, diff in enumerate(frame_diffs):
        current_time = i / fps
        if diff > threshold and not in_highlight:
            in_highlight = True
            start_time = current_time
        elif diff <= threshold and in_highlight:
            in_highlight = False
            end_time = current_time
            if end_time - start_time > 1:  # Min highlight duration
                highlights.append({"start": start_time, "end": end_time})
    if in_highlight:
        highlights.append({"start": start_time, "end": len(frame_diffs) / fps})
    return highlights


def detect_beats(music_path: str) -> List[float]:
    """Detects beats in a music file using librosa."""
    y, sr = librosa.load(music_path)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    return beat_times.tolist()


def create_final_reel(video_clips: List[Dict], music_path: str, beats: List[float], output_path: str):
    """Creates the final reel by syncing video highlights to music beats."""
    input_streams = []
    clip_duration = beats[1] - beats[0] if len(beats) > 1 else 2.0

    beat_index = 0
    for clip_info in video_clips:
        if not clip_info['highlights']:
            continue

        # Take the first highlight of each clip
        highlight = clip_info['highlights'][0]
        start_time = highlight['start']

        # Cut the clip to match the beat
        stream = ffmpeg.input(clip_info['path'], ss=start_time, t=clip_duration)
        # Convert to 9:16 aspect ratio
        stream = ffmpeg.filter(stream, 'scale', '1080', '1920', force_original_aspect_ratio='decrease')
        stream = ffmpeg.filter(stream, 'pad', '1080', '1920', '-1', '-1', 'black')
        input_streams.append(stream)

        beat_index += 1
        if beat_index >= len(beats):
            break

    if not input_streams:
        raise ValueError("No highlights found to create a reel.")

    video_stream = ffmpeg.concat(*input_streams, v=1, a=0)
    music_stream = ffmpeg.input(music_path).filter('volume', 0.6)

    final_duration = clip_duration * len(input_streams)
    music_stream = ffmpeg.filter(music_stream, 'atrim', duration=final_duration)

    ffmpeg.output(video_stream, music_stream, output_path, vcodec='libx264', acodec='aac', strict='experimental').run(overwrite_output=True)


def process_reel_task(job_id: str, video_urls: List[str], music_url: str, niche: str):
    temp_dir = tempfile.mkdtemp()
    try:
        job_manager.update_job_status(job_id, "processing")
        downloaded_videos = [download_file(url, temp_dir) for url in video_urls]
        downloaded_music = download_file(music_url, temp_dir)

        processed_clips_info = []
        for video_path in downloaded_videos:
            trimmed_clip_path = trim_silences(video_path)
            highlights = detect_highlights(trimmed_clip_path)
            if highlights:
                processed_clips_info.append({"path": trimmed_clip_path, "highlights": highlights})

        beats = detect_beats(downloaded_music)
        final_reel_path = os.path.join(temp_dir, "final_reel.mp4")

        create_final_reel(processed_clips_info, downloaded_music, beats, final_reel_path)

        final_video_url = upload_to_cloudinary(final_reel_path)
        job_manager.update_job_status(job_id, "completed")
        job_manager.jobs[job_id]["finalVideoUrl"] = final_video_url

    except Exception as e:
        print(f"Error processing reel for job {job_id}: {e}")
        job_manager.update_job_status(job_id, "failed", error=str(e))
    finally:
        shutil.rmtree(temp_dir)
