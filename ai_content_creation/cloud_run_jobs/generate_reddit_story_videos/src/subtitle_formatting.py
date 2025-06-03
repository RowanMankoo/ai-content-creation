import re

# Shared style dict
subtitle_style = {
    "Name": "Default",
    "Fontname": "Arial",
    "Fontsize": "100",
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



def make_ass_event_lines(entries, style_name="Default", gap=0.0):
    lines = []
    for start_sec, end_sec, text in entries:
        # Apply gap if provided
        adjusted_end = max(end_sec - gap, 0.0)
        start_tc = seconds_to_ass_time(start_sec)
        end_tc = seconds_to_ass_time(adjusted_end)
        clean_text = text.replace(",", "")
        # Center override "\an5" if desired; can be parameterized later
        override = "{\\an5}"
        line = f"Dialogue: 0,{start_tc},{end_tc},{style_name},,0,0,0,,{override}{clean_text}"
        lines.append(line)
    return lines


def convert_srt_to_ass(srt_string, gap=0.01, target_w=720, target_h=1280) -> str:
    # 1. Extract SRT blocks: (index, start_str, end_str, text)
    srt_blocks = re.findall(
        r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\n|\Z)",
        srt_string,
        re.DOTALL,
    )

    # 2. Convert SRT time strings "HH:MM:SS,mmm" to seconds floats
    def srt_time_to_seconds(t):
        hh, mm, ss_ms = t.split(":", 2)
        ss, ms = ss_ms.split(",", 1)
        return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) * 0.001

    # 3. Build list of entries (start_sec, end_sec, text)
    entries = []
    for _, start_str, end_str, text in srt_blocks:
        start_sec = srt_time_to_seconds(start_str)
        end_sec = srt_time_to_seconds(end_str)
        clean_text = " ".join(text.splitlines())
        entries.append((start_sec, end_sec, clean_text))

    # 4. Build ASS header & styles once
    ass_lines = build_ass_header_and_styles(target_w, target_h, subtitle_style)

    # 5. Create ASS dialogue lines with gap
    ass_lines += make_ass_event_lines(entries, style_name="Default", gap=gap)

    # 6. Return full ASS content
    return "\n".join(ass_lines)


def build_ass_header_and_styles(
    target_w: int, target_h: int, subtitle_style: dict
) -> list:
    header = [
        "[Script Info]",
        "Title: Generated ASS Subtitle",
        "ScriptType: v4.00+",
        f"PlayResX: {target_w}",
        f"PlayResY: {target_h}",
        "ScaledBorderAndShadow: yes",
        "",  # blank line separates sections
    ]
    styles = [
        "[V4+ Styles]",
        "Format: " + ", ".join(subtitle_style.keys()),
        "Style: " + ",".join(subtitle_style.values()),
        "",
    ]
    events_header = [
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    return header + styles + events_header


def make_ass_from_words(
    words, target_w=720, target_h=1280
) -> str:
    # 1. Convert TranscriptionWord objects to entries list
    # Each w has attributes: w.start (float), w.end (float), w.word (str)
    entries = [(w.start, w.end, w.word) for w in words]

    # 2. Build ASS header & styles once
    ass_lines = build_ass_header_and_styles(target_w, target_h, subtitle_style)

    # 3. Create ASS dialogue lines without gap
    ass_lines += make_ass_event_lines(entries, style_name="Default", gap=0.0)

    return "\n".join(ass_lines)


def time_to_seconds(ts):
    return ts.total_seconds()

def make_ass_from_google_response(response, target_w=720, target_h=1280):
    words = []
    for result in response.results:
        alt = result.alternatives[0]
        for w in alt.words:
            start = time_to_seconds(w.start_time)
            end = time_to_seconds(w.end_time)
            words.append((start, end, w.word))
    ass_lines = build_ass_header_and_styles(target_w, target_h, subtitle_style)
    ass_lines += make_ass_event_lines(words, style_name="Default", gap=0.0)
    return "\n".join(ass_lines)