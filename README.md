# ffmpeg-caption-burn-ass

Styled word-level captions for vertical shorts (1080×1920) as a generated
`.ass` (libass) file, burned into video with a **single ffmpeg pass** — no
browser renderers, no per-frame compositing, no dependencies (pure Python
stdlib + ffmpeg with libass).

Actively used in production by the [bridex.app](https://bridex.app) agent
orchestrator's render workers.

## Modes

- **`karaoke-highlight`** — groups of 3–5 words on screen; the active word is
  tinted and scaled (`{\c}{\fscx110}` override tags per word — more reliable
  than `\k` karaoke timing and gives full per-word control).
- **`word-carousel`** — one word at a time, centered, with an 80→100 pop-in
  (`\t()` transform).

## Input

`words.json` — `[{"word": "...", "start": 1.23, "end": 1.61}, ...]`
(e.g. whisper word timings).

Style (all optional):

```json
{
  "font": "Liberation Sans",
  "fontSize": 88,
  "primaryColor": "#FFFFFF",
  "highlightColor": "#FFE600",
  "outline": 4,
  "position": "bottom | center | top",
  "marginV": 480,
  "maxWordsPerGroup": 4,
  "bold": true,
  "uppercase": false,
  "box": {"color": "#000000", "opacity": 0.85, "padding": 16}
}
```

- `marginV` — distance in px (on the 1080×1920 canvas) from the bottom for
  `bottom`, from the top for `top`; defaults keep the text out of the Reels UI.
- `box` — a solid plate behind each line (libass `BorderStyle 3`): the
  «white word in a black box» caption. Omit it for outlined text.

## Usage

```sh
python3 cli.py --words words.json --mode karaoke-highlight \
  --style '{"highlightColor":"#FFE600"}' --out captions.ass \
  --burn input.mp4 --video-out captioned.mp4
```

Or as a library:

```python
from ass_captions import build_ass
open("captions.ass", "w").write(build_ass(words, "word-carousel"))
# ffmpeg -i in.mp4 -vf subtitles=filename=captions.ass -c:a copy out.mp4
```

## Built-in placement rules

1080×1920 PlayRes; bottom mode keeps text above the lower 25% (TikTok/Reels
UI safe-zone); groups capped at ~30 chars; bold + black outline by default —
readable over bright footage without a background box.

## When to use it (and when not)

This is the fast path for PLAIN word captions: one libass pass at re-encode
speed. If you need designed caption cards, scroll layers, per-speaker
layouts or brand typography animations — use a real compositor (Remotion or
similar); this tool deliberately stays inside what `.ass` override tags do
well.

MIT.
