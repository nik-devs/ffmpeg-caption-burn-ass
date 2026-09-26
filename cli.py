#!/usr/bin/env python3
"""CLI: words.json / phrases.json -> captions.ass (and optionally burn it with ffmpeg).

  python3 cli.py --words words.json --mode karaoke-highlight \
      --style '{"font":"Liberation Sans","highlightColor":"#FFE600"}' \
      --out captions.ass [--burn input.mp4 --video-out captioned.mp4]

  python3 cli.py --phrases phrases.json --mode phrases \
      --style '{"plate":{"color":"#FFFFFF","radius":28}}' \
      --out captions.ass --burn input.mp4 --video-out captioned.mp4
"""
import argparse, json, subprocess
from ass_captions import build_ass

def video_size(path):
    w, h = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                           "stream=width,height", "-of", "csv=p=0:s=x", path],
                          capture_output=True, text=True, check=True).stdout.strip().split("x")
    return int(w), int(h)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", help="[{word,start,end}] for karaoke-highlight / word-carousel")
    ap.add_argument("--phrases", help="[{text,start,end}] for mode phrases")
    ap.add_argument("--mode", required=True, choices=["karaoke-highlight", "word-carousel", "phrases"])
    ap.add_argument("--style", default="{}")
    ap.add_argument("--fonts-dir", action="append", default=[], help="extra font files (also passed to libass)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--burn", help="input video: burn captions in one libass pass")
    ap.add_argument("--video-out", default="captioned.mp4")
    a = ap.parse_args()
    if a.mode == "phrases" and not a.phrases: ap.error("--mode phrases needs --phrases")
    if a.mode != "phrases" and not a.words: ap.error(f"--mode {a.mode} needs --words")
    size = video_size(a.burn) if a.burn else None
    ass = build_ass(json.load(open(a.words)) if a.words else None, a.mode, json.loads(a.style),
                    phrases=json.load(open(a.phrases)) if a.phrases else None,
                    video_size=size, font_dirs=a.fonts_dir)
    open(a.out, "w").write(ass)
    print(f"{a.out}: {ass.count(chr(10) + 'Dialogue:')} dialogues, mode {a.mode}")
    if a.burn:
        vf = f"subtitles=filename={a.out}" + (f":fontsdir={a.fonts_dir[0]}" if a.fonts_dir else "")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.burn, "-vf", vf,
                        "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "copy", a.video_out], check=True)
        print(f"burned -> {a.video_out}")

if __name__ == "__main__":
    main()
