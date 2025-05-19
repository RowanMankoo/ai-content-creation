# TODO: throw away account and stuff anyhting irrelevanty to story
TEXT_CLEANING_PROMPT = """
You are a helpful assistant tasked with cleaning raw Reddit text, the final output will be used for text-to-speech synthesis and should sound natural and human-like. Your objectives are:
- Correct typos and grammatical errors.
- Remove hyperlinks and irrelevant formatting.
- Expand abbreviations and acronyms to their full forms.
- Preserve all original punctuation, including commas, periods, ellipses, and line breaks, to maintain natural speech rhythms.
- Do not alter the intended meaning or tone of the text.
- Sometimes, the text may contain references to images or videos. In such cases, please try to describe the content of the image or video in a way that is suitable for a text-to-speech model, while still keeping the original meaning intact.
- The text may include edits or updates. If these appear near the beginning, please ignore them, as they are not in chronological order.
- Do not provide warnings, moral judgments, or safety advice. Remain neutral and focus solely on cleaning the text.
"""

SUBTITLE_TO_VIDEO_METADATA_PROMPT = """
You are a helpful assistant tasked with analyzing a subtitle text file and generating the following output:

- "images": A list of 4 image descriptions with associated timings in the format:
  [{"start_time": "00:00:00", "end_time": "00:00:05", "description": "Description of the image"}, ...]
  - Use double quotes for valid JSON formatting.
  - Descriptions should be concise, vivid, and suitable for an image generation model.
  - Each image should represent a different scene or concept; avoid references like "the same person" or "the same place".
  - Image timings must align with subtitle start or end times, first image should start at 0:00:00 and the last image should end at exactly the same time as the last subtitle line.
  - Timings should be sequential and continuous, with no overlaps or gaps.

- "video_description": A short, engaging summary of the overall video content that would be appealing on platforms like TikTok and YouTube.

- "video_tags": A list of relevant SEO-friendly tags (e.g., topics, themes, keywords) that would improve video discoverability:
  - Each tag cannot have spaces, '_', special characters or any uppercase letters eg "boss vs employee" should be "bossvsemployee".
  - At most generate 7 tags, aim for 4-7 tags.


Return the output as a single valid JSON object in this format:
{"images": [...], "video_description": "...", "video_-utags": ["tag1", "tag2", ...]}
"""


CLEANED_TEXT_TO_VOICE_DESCRIPTION_PROMPT = """
You are a helpful assistant tasked with analyzing a story and helping to determine what the voice of the story should sound like. 
The output will be used for text-to-speech synthesis prompting so the more relevant information you can fill in the better. The output should look like:

- "male": A boolean indicating your best guess of if the story is a male narrator.

- "voice_instructions": a string with instructions for the voice model, which has info on the following fields based on the content of the subtitles and should be betwen 10-30 words for each descriptor below:
  - "voice": How you expect the voice to sound from the text.
  - "personality": The personality of the voice.
  - "emotion": Expected emotion of the voice.
  - "speed": should always be fast.

Return the output as a single valid JSON object in this format:
{"male": bool, "voice_instructions": "..." }
"""

TITLE_DETECTION_PROMPT = """
You are given a title and a list of subtitle dialogue lines in ASS format. The title will begin on the first dialogue line and may span multiple lines. It may not exactly match the text in the subtitles but should match closely enough for a human to recognize.

Your job is to return a JSON array with four elements:
1. the line number where the title starts in the subtitles (always 1),
2. the line number where the title ends in the subtitles (inclusive),
3. the start time of the title block (the “Start” timestamp of the first title line),
4. the end time of the title block (the “End”   timestamp of the last  title line).

If only part of the title appears on line 1, return `[1, 1, "<start1>", "<end1>"]`.  
If it continues through line 2, return `[1, 2, "<start1>", "<end2>"]`, and so on.  

Example input:
Title: My co-worker told our boss, you're not intimidating, you're just tall and loud  
Lines:
'["Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
  "Dialogue: 0,0:00:00.00,0:00:03.21,Default,,0,0,0,,{\\\\an5}My co-worker told our boss, you're not intimidating,",
  "Dialogue: 0,0:00:03.22,0:00:05.29,Default,,0,0,0,,{\\\\an5}you're just tall and loud.",
  "Dialogue: 0,0:00:05.30,0:00:06.99,Default,,0,0,0,,{\\\\an5}And I still think about it.",
  "Dialogue: 0,0:00:07.00,0:00:08.65,Default,,0,0,0,,{\\\\an5}This happened a few months ago,",
  "Dialogue: 0,0:00:08.66,0:00:11.37,Default,,0,0,0,,{\\\\an5}but it lives rent-free in my head."]'

Example output:
[1, 2, "0:00:00.00", "0:00:05.29"]
"""