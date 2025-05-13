import logging

import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def combine_audio_video_images_subtitles(
    audio_file_path: Path,
    video_file_path: Path,
    subtitle_file_path: Path,
    image_timeline: list[dict],
    reddit_card_path: Path,
    reddit_title_card_start_ts: str,
    reddit_title_card_end_ts: str,
    output_file_path: Path,
    resolution: str = "640x1152",
    fps: int = 120,
    vertical_offset_pct: float = 0.0,
):
    for p in (audio_file_path, video_file_path, subtitle_file_path, reddit_card_path):
        if not p.exists():
            raise FileNotFoundError(f"{p} not found")

    w, h = map(int, resolution.split("x"))
    half_h = h // 2

    def to_secs(ts: str) -> float:
        h_, m_, s_ = map(float, ts.split(":"))
        return h_ * 3600 + m_ * 60 + s_

    # total audio duration
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_file_path),
        ],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    total_dur = float(proc.stdout.strip())

    # 1) pre-scale reddit card to 80% of width
    tmp_card = reddit_card_path.with_name(reddit_card_path.stem + "_scaled.png")
    if not tmp_card.exists():
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(reddit_card_path),
                "-vf",
                f"scale={int(0.8 * w)}:-1",
                str(tmp_card),
            ],
            check=True,
        )

    # inputs: video, black, audio, pre-scaled card, other images
    cmd = [
        "ffmpeg",
        "-y",
        "-thread_queue_size",
        "512",
        "-threads",
        "auto",
        "-i",
        str(video_file_path),
        "-f",
        "lavfi",
        "-i",
        f"color=black:size={w}x{h}:duration={total_dur}",
        "-i",
        str(audio_file_path),
        "-loop",
        "1",
        "-t",
        str(to_secs(reddit_title_card_end_ts) - to_secs(reddit_title_card_start_ts)),
        "-i",
        str(tmp_card),
    ]
    for img in image_timeline:
        dur = to_secs(img["end_time"]) - to_secs(img["start_time"])
        cmd += ["-loop", "1", "-t", str(dur), "-i", img["image_url"]]

    # probe video size
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0:s=x",
            str(video_file_path),
        ],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    inp_w, inp_h = map(int, proc.stdout.strip().split("x"))

    ar = w / half_h
    if inp_w / inp_h > ar:
        crop_h = inp_h
        crop_w = int(inp_h * ar)
    else:
        crop_w = inp_w
        crop_h = int(inp_w / ar)

    x = (inp_w - crop_w) // 2
    y_base = (inp_h - crop_h) / 2 + vertical_offset_pct * (inp_h - crop_h)
    y = int(max(0, min(inp_h - crop_h, y_base)))

    parts = [
        f"[0:v]setpts=PTS-STARTPTS,fps={fps},crop={crop_w}:{crop_h}:{x}:{y},scale={w}:{half_h}[vid]",
        f"[1:v][vid]overlay=0:{half_h}[base]",
    ]
    cur = "[base]"

    # overlay images
    for idx, img in enumerate(image_timeline, start=4):
        s, e = to_secs(img["start_time"]), to_secs(img["end_time"])
        out = f"[img{idx}]"
        parts.append(
            f"{cur}[{idx}:v]overlay=enable='between(t,{s},{e})':x=(W-w)/2:y=0{out}"
        )
        cur = out

    # 3) overlay pre-scaled reddit card
    s_card, e_card = to_secs(reddit_title_card_start_ts), to_secs(reddit_title_card_end_ts)
    parts.append(
        f"{cur}[3:v]overlay=enable='between(t,{s_card},{e_card})'"
        f":x='(W-overlay_w)/2':y='(H-overlay_h)/2'[card]"
    )
    cur = "[card]"

    # burn in subtitles
    parts.append(f"{cur}subtitles='{subtitle_file_path}'[v]")

    filter_complex = ";".join(parts)

    cmd += [
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-map",
        "2:a",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-vsync",
        "1",
        "-async",
        "1",
        "-shortest",
        str(output_file_path),
    ]

    try:
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        logger.info(result.stdout)
        logger.info(f"Created video at {output_file_path}")
    except subprocess.CalledProcessError as e:
        logger.error(e.stderr)
        raise RuntimeError(f"FFmpeg failed: {e.stderr}")


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
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_file_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    total_dur = float(proc.stdout.strip())

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=black:size={resolution}:duration={total_dur}",
        "-i",
        str(audio_file_path),
    ]

    for img in image_timeline:
        dur = to_secs(img["end_time"]) - to_secs(img["start_time"])
        cmd += ["-loop", "1", "-t", str(dur), "-i", img["image_url"]]

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
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-map",
        "1:a",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-shortest",
        str(output_file_path),
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
