#!/usr/bin/env python3
"""CLI: words.json -> captions.ass (and optionally burn it with ffmpeg).

  python3 cli.py --words words.json --mode karaoke-highlight \
      --style '{"font":"Liberation Sans","highlightColor":"#FFE600"}' \
      --out captions.ass [--burn input.mp4 --video-out captioned.mp4]
"""
import argparse, json, subprocess, sys
from ass_captions import build_ass

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", required=True)
    ap.add_argument("--mode", required=True, choices=["karaoke-highlight", "word-carousel"])
    ap.add_argument("--style", default="{}")
    ap.add_argument("--out", required=True)
    ap.add_argument("--burn", help="input video: burn captions in one libass pass")
    ap.add_argument("--video-out", default="captioned.mp4")
    a = ap.parse_args()
    words = json.load(open(a.words))
    ass = build_ass(words, a.mode, json.loads(a.style))
    open(a.out, "w").write(ass)
    print(f"{a.out}: {ass.count(chr(10)+'Dialogue:') + 1} dialogues, mode {a.mode}")
    if a.burn:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.burn,
                        "-vf", f"subtitles=filename={a.out}", "-c:a", "copy", a.video_out], check=True)
        print(f"burned -> {a.video_out}")

if __name__ == "__main__":
    main()
