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
  - Image timings must align with subtitle start or end times.
  - Timings should be sequential and continuous, with no overlaps or gaps.

- "video_description": A short, engaging summary of the overall video content that would be appealing on platforms like TikTok and YouTube.

- "video_tags": A list of relevant SEO-friendly tags (e.g., topics, themes, keywords) that would improve video discoverability:
  - Each tag cannot have spaces or special characters eg "boss vs employee" should be "boss_vs_employee".
  - At most generate 10 tags, aim for 5-7 tags.


Return the output as a single valid JSON object in this format:
{"images": [...], "video_description": "...", "video_tags": ["tag1", "tag2", ...]}
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