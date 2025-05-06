
import logging

import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

def combine_audio_images_subtitles(
    audio_file_path: Path,
    subtitle_file_path: Path,
    image_timeline: list[dict],
    output_file_path: Path,
    resolution: str = "640x1152",
):
    for p in (audio_file_path, subtitle_file_path):
        if not p.exists():
            raise FileNotFoundError(f"{p} not found")

    def to_secs(ts: str) -> float:
        h, m, s = map(float, ts.split(":"))
        return h * 3600 + m * 60 + s

    # get audio duration
    proc = subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","default=noprint_wrappers=1:nokey=1", str(audio_file_path)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
    )
    total_dur = float(proc.stdout.strip())

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=black:size={resolution}:duration={total_dur}",
        "-i", str(audio_file_path),
    ]

    for img in image_timeline:
        dur = to_secs(img["end_time"]) - to_secs(img["start_time"])
        cmd += ["-loop","1","-t",str(dur),"-i", img["image_url"]]

    # build filter_complex: overlay images, then subtitles on top
    fc_parts = []
    current = "[0:v]"
    for idx, img in enumerate(image_timeline, start=2):
        s, e = to_secs(img["start_time"]), to_secs(img["end_time"])
        out = f"[o{idx}]"
        fc_parts.append(
            f"{current}[{idx}:v]overlay="
            f"enable='between(t,{s},{e})':x=(W-w)/2:y=(H-h)/2{out}"
        )
        current = out

    # subtitles last so they sit above everything
    fc_parts.append(f"{current}subtitles='{subtitle_file_path}'[v]")

    filter_complex = ";".join(fc_parts)

    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest", str(output_file_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,  # Raises error if FFmpeg fails
        )

        logger.info(f"FFmpeg Output: {result.stdout}")
        logger.info(f"Created and saved processed video to {output_file_path}")

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed with error: {e.stderr}")
        raise RuntimeError(f"FFmpeg process failed: {e.stderr}")