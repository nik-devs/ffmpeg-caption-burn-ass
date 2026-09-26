# ffmpeg-caption-burn-ass

Styled captions for shorts — word-level, or one phrase per rounded plate — as a
generated `.ass` (libass) file, burned into video with a **single ffmpeg pass**:
no browser renderers, no per-frame compositing. The word modes need nothing but
Python's stdlib + ffmpeg with libass; `phrases` also uses Pillow and fontconfig
(`fc-match`) to measure the text so the plate fits it.

Actively used in production by the [bridex.app](https://bridex.app) agent
orchestrator's render workers.

## Modes

- **`karaoke-highlight`** — groups of 3–5 words on screen; the active word is
  tinted and scaled (`{\c}{\fscx110}` override tags per word — more reliable
  than `\k` karaoke timing and gives full per-word control).
- **`word-carousel`** — one word at a time, centered, with an 80→100 pop-in
  (`\t()` transform).
- **`phrases`** — one given phrase per event, shown exactly from its `start` to
  its `end`, on a rounded plate drawn to fit the text (long phrases wrap inside
  it). Plate colour, opacity, corner radius and padding are configurable; the
  defaults are a white plate with black text, bottom-centre, above the Reels UI.

## Input

`words.json` — `[{"word": "...", "start": 1.23, "end": 1.61}, ...]`
(e.g. whisper word timings), for the word modes.

`phrases.json` — `[{"text": "No way, it's been ages.", "start": 2.32, "end": 4.14}, ...]`
for `phrases`. Phrase style (all optional, on top of `font`, `fontSize`,
`primaryColor`, `bold`, `uppercase`, `position`, `marginV`):

```json
{
  "plate": {"color": "#FFFFFF", "opacity": 1.0, "radius": 28, "padX": 36, "padY": 20},
  "maxWidth": 0.84,
  "lineSpacing": 1.15
}
```

Style (all optional):

```json
{
  "font": "Liberation Sans",
  "fontSize": 88,
  "primaryColor": "#FFFFFF",
  "highlightColor": "#FFE600",
  "outline": 4,
  "outlineColor": "#000000",
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
- `outlineColor` — the outline around the letters when there is no `box`
  (black by default; white for dark text on a busy background).

## Usage

```sh
python3 cli.py --words words.json --mode karaoke-highlight \
  --style '{"highlightColor":"#FFE600"}' --out captions.ass \
  --burn input.mp4 --video-out captioned.mp4

python3 cli.py --phrases phrases.json --mode phrases \
  --style '{"plate":{"color":"#FFFFFF","radius":28}}' --out captions.ass \
  --burn input.mp4 --video-out captioned.mp4
```

Or as a library:

```python
from ass_captions import build_ass
open("captions.ass", "w").write(build_ass(words, "word-carousel"))
# ffmpeg -i in.mp4 -vf subtitles=filename=captions.ass -c:a copy out.mp4
```

## Built-in placement rules

A canvas 1080 wide and as tall as the video's aspect (1080×1920 for 9:16; pass
`video_size` so square and 16:9 are not stretched — the CLI reads it from the
video); bottom mode keeps text above the lower 25% (TikTok/Reels UI safe-zone); groups capped at ~30 chars; bold + black outline by default —
readable over bright footage without a background box.

## When to use it (and when not)

This is the fast path for PLAIN word captions: one libass pass at re-encode
speed. If you need designed caption cards, scroll layers, per-speaker
layouts or brand typography animations — use a real compositor (Remotion or
similar); this tool deliberately stays inside what `.ass` override tags do
well.

MIT.
