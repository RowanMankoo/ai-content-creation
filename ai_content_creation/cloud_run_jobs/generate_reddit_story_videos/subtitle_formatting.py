import re

def format_ass_time(srt_time):
    """
    Converts an SRT timestamp (HH:MM:SS,mmm) to an ASS timestamp (H:MM:SS.CS)
    where CS represents centiseconds.
    """
    hours, minutes, rest = srt_time.split(':')
    seconds, millis = rest.split(',')
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000.0
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

def convert_srt_to_ass(srt_string, gap=0.01)-> str:

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
        "Alignment": "5",
        "MarginL": "10",
        "MarginR": "10",
        "MarginV": "30",
        "Encoding": "1",
    }
    
    srt_blocks = re.findall(
        r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\n|\Z)",
        srt_string,
        re.DOTALL
    )
    
    ass_lines = []
    
    ass_lines.append("[Script Info]\n")
    ass_lines.append("Title: Generated ASS Subtitle\n")
    ass_lines.append("ScriptType: v4.00+\n")
    ass_lines.append("PlayDepth: 0\n")
    ass_lines.append("ScaledBorderAndShadow: yes\n\n")
    
    ass_lines.append("[V4+ Styles]\n")
    ass_lines.append("Format: " + ", ".join(subtitle_style.keys()) + "\n")
    ass_lines.append("Style: " + ",".join(subtitle_style.values()) + "\n\n")
    
    ass_lines.append("[Events]\n")
    ass_lines.append("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    
    for _, start, end, text in srt_blocks:
        ass_start = format_ass_time(start)
        parts = end.replace(",", ":").split(":")
        # Calculate total seconds: [hours, minutes, seconds, milliseconds]
        end_seconds = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2]) + float(parts[3]) * 0.001
        end_seconds = max(end_seconds - gap, 0)
        ass_end = seconds_to_ass_time(end_seconds)
        
        # Remove newlines within text and ensure centered alignment with {\an5}
        formatted_text = f"{{\\an5}}{' '.join(text.splitlines())}"
        ass_line = f"Dialogue: 0,{ass_start},{ass_end},Default,,0,0,0,,{formatted_text}\n"
        ass_lines.append(ass_line)
    
    ass_string = "".join(ass_lines)
    return ass_string