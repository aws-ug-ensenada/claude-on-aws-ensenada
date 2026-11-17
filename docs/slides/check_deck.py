"""Check the built deck for a far-away audience: text size, colour contrast, and a speaker note with a time cue on every slide.

  python check_deck.py            # after: node build.js

Text under 12 pt and text/background pairs under 4.5:1 contrast (3:1 for text of 18 pt or larger) are reported.
The pairs are the deck's own palette combinations (see COLOR in build.js). Exit code 1 if anything fails.
"""

import pathlib
import re
import sys
import zipfile

HERE = pathlib.Path(__file__).parent
PPTX = HERE / "claude-on-aws-ensenada.pptx"
MIN_PT = 12

# (text colour, background, where it is used). Colours are read from build.js so the two can't drift apart.
PAIRS = [
    ("ink", "white", "body text on cards"),
    ("muted", "white", "secondary text on cards"),
    ("muted", "mist", "secondary text on tinted cards"),
    ("teal", "white", "headings on cards"),
    ("teal", "mist", "headings on tinted slides"),
    ("white", "coral", "icons on coral badges (graphics: 3 is enough)"),
    ("white", "teal", "icons on teal badges"),
    ("code", "ocean", "terminal and code text"),
    ("quote", "ocean", "the audience's typed question"),
    ("coral", "ocean", "prompts in the terminal"),
    ("foam", "ocean", "text on dark slides"),
]


def colors() -> dict[str, str]:
    """The deck palette (name to hex) parsed from the COLOR object in build.js."""
    block = re.search(r"const COLOR = \{(.*?)\};", (HERE / "build.js").read_text(), re.S).group(1)
    return dict(re.findall(r'(\w+):\s*"([0-9A-Fa-f]{6})"', block))


def luminance(hex_color: str) -> float:
    """WCAG relative luminance of a hex colour, from 0 (black) to 1 (white)."""
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    """WCAG contrast ratio between two hex colours, from 1 to 21."""
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def main() -> int:
    """Check palette contrast, text size and speaker-note time cues in the built .pptx; returns 1 if anything fails."""
    bad = 0
    palette = colors()
    print("Contrast (WCAG: 4.5 for body text, 3 for large text and icons):")
    for fg, bg, where in PAIRS:
        ratio = contrast(palette[fg], palette[bg])
        ok = ratio >= (3.0 if "graphics" in where else 4.5)
        bad += not ok
        print(f"  {'✅' if ok else '⚠️ '} {ratio:4.1f}  {fg} on {bg}: {where}")

    z = zipfile.ZipFile(PPTX)
    slides = sorted((n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)), key=lambda n: int(re.findall(r"\d+", n)[0]))
    small = []
    for n in slides:
        number = int(re.findall(r"\d+", n)[0])
        # Each run's font size (sz, in hundredths of a point) paired with its text.
        for size, text in re.findall(r'<a:rPr[^>]*\bsz="(\d+)"[^>]*>(?:(?!</a:r>).)*?<a:t>(.*?)</a:t>', z.read(n).decode(), re.S):
            if int(size) < MIN_PT * 100 and text.strip() and not re.fullmatch(r"\d+", text.strip()):
                small.append((number, int(size) / 100, text[:50]))
    print(f"\nText under {MIN_PT} pt (page numbers and the footer are ignored):")
    for number, pt, text in small:
        print(f"  ⚠️  slide {number}: {pt:g} pt  {text}")
    if not small:
        print("  ✅ none")
    bad += len(small)

    notes = [n for n in z.namelist() if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", n)]
    cued = sum(1 for n in notes if "⏱" in z.read(n).decode())
    print(f"\nSpeaker notes with a time cue: {cued} of {len(slides)} slides")
    bad += cued < len(slides) - 1  # the last slide (Q&A) is untimed
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
