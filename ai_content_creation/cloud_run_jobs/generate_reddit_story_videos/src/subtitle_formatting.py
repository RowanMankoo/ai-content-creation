import re


def format_ass_time(srt_time):
    """
    Converts an SRT timestamp (HH:MM:SS,mmm) to an ASS timestamp (H:MM:SS.CS)
    where CS represents centiseconds.
    """
    hours, minutes, rest = srt_time.split(":")
    seconds, millis = rest.split(",")
    total_seconds = (
        int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000.0
    )
    return seconds_to_ass_time(total_seconds)


def seconds_to_ass_time(total_seconds):
    """
    Converts a time value in seconds (float) to an ASS time string in the format H:MM:SS.CS.
    This function handles negative values (by clamping them to 0) and ensures proper rounding.
    """
    if total_seconds < 0:
        total_seconds = 0
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = total_seconds % 60
    return f"{hours}:{minutes:02d}:{seconds:05.2f}"


def convert_srt_to_ass(srt_string, gap=0.01, target_w=720, target_h=1280) -> str:

    subtitle_style = {
        "Name": "Default",
        "Fontname": "Arial",
        "Fontsize": "50",
        "PrimaryColour": "&H00FFFFFF",
        "SecondaryColour": "&H00000000",
        "OutlineColour": "&H00000000",
        "BackColour": "&H80000000",
        "Bold": "1",
        "Italic": "0",
        "Underline": "0",
        "StrikeOut": "0",
        "ScaleX": "100",
        "ScaleY": "100",
        "Spacing": "0",
        "Angle": "0",
        "BorderStyle": "1",
        "Outline": "3",
        "Shadow": "1",
        "Alignment": "5",  # middle-center
        "MarginL": "10",
        "MarginR": "10",
        "MarginV": "30",
        "Encoding": "1",
    }

    # parse SRT…
    srt_blocks = re.findall(
        r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\n|\Z)",
        srt_string,
        re.DOTALL,
    )

    ass = []
    # Script Info with real resolution
    ass.append("[Script Info]\n")
    ass.append("Title: Generated ASS Subtitle\n")
    ass.append("ScriptType: v4.00+\n")
    ass.append(f"PlayResX: {target_w}\n")
    ass.append(f"PlayResY: {target_h}\n")
    ass.append("ScaledBorderAndShadow: yes\n\n")

    # Styles
    ass.append("[V4+ Styles]\n")
    ass.append("Format: " + ", ".join(subtitle_style.keys()) + "\n")
    ass.append("Style: " + ",".join(subtitle_style.values()) + "\n\n")

    # Events
    ass.append("[Events]\n")
    ass.append(
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

    for _, start, end, text in srt_blocks:
        ass_start = format_ass_time(start)
        # subtract gap…
        parts = end.replace(",", ":").split(":")
        end_s = (
            float(parts[0]) * 3600
            + float(parts[1]) * 60
            + float(parts[2])
            + float(parts[3]) * 0.001
        )
        ass_end = seconds_to_ass_time(max(end_s - gap, 0))

        # center/center override — margins not used
        clean = " ".join(text.splitlines())
        override = "{\\an5}"
        ass.append(
            f"Dialogue: 0,{ass_start},{ass_end},Default,,0,0,0,,{override}{clean}\n"
        )

    return "".join(ass)
