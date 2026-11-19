#!/usr/bin/env python3
"""Build-time renderer for THE WORLD TODAY -- Thursday, 19 November 2026.

Draws the 1024x1024 newspaper front page with Pillow + DejaVu and writes
preview.png. This script runs ONLY at build time: the entry's main.py is
stdlib-only and copies the committed preview.png, because the grading
sandbox is a bare python:3.13 with no Pillow and no fonts.
"""
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "preview.png")

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (17, 17, 17)
RED = (176, 32, 32)
GREY = (90, 90, 90)
NAVY = (28, 43, 74)
SKY = (38, 58, 96)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines that fit `width` px."""
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_block(draw, x, y, width, kicker, headline, body,
               kick_f, head_f, body_f, head_leading, body_leading,
               max_head_lines=3):
    """Kicker + headline + body; returns the y just below the block."""
    draw.text((x, y), kicker, font=kick_f, fill=RED)
    y += kick_f.size + 8
    hl = wrap(draw, headline, head_f, width)[:max_head_lines]
    for ln in hl:
        draw.text((x, y), ln, font=head_f, fill=INK)
        y += head_leading
    y += 6
    for ln in wrap(draw, body, body_f, width):
        draw.text((x, y), ln, font=body_f, fill=INK)
        y += body_leading
    return y


def draw_flag(draw, x, y, w, h, kind):
    """Simplified US / China / Russia flag on a pole at (x, y)."""
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    if kind == "us":
        for i in range(7):
            if i % 2 == 0:
                draw.rectangle([x + 1, y + 1 + i * h // 7,
                                x + w - 1, y + (i + 1) * h // 7],
                               fill=(178, 34, 52))
        draw.rectangle([x + 1, y + 1, x + int(w * 0.4), y + int(h * 0.54)],
                       fill=(60, 59, 110))
        for r in range(3):
            for c in range(4):
                cx = x + 6 + c * 13
                cy = y + 6 + r * 11
                draw.ellipse([cx, cy, cx + 3, cy + 3], fill=(255, 255, 255))
    elif kind == "cn":
        draw.rectangle([x + 1, y + 1, x + w - 1, y + h - 1], fill=(222, 41, 16))
        cx, cy = x + 12, y + 12
        for dx, dy in [(0, 0), (16, -4), (20, 6), (12, 12), (4, 6)]:
            draw.ellipse([cx + dx - 2, cy + dy - 2, cx + dx + 2, cy + dy + 2],
                         fill=(255, 222, 0))
    elif kind == "ru":
        draw.rectangle([x + 1, y + 1, x + w - 1, y + h // 3],
                       fill=(255, 255, 255))
        draw.rectangle([x + 1, y + h // 3, x + w - 1, y + 2 * h // 3],
                       fill=(0, 57, 166))
        draw.rectangle([x + 1, y + 2 * h // 3, x + w - 1, y + h - 1],
                       fill=(213, 0, 50))
    draw.rectangle([x - 2, y - 6, x + 2, y + 150], fill=(60, 60, 60))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- Masthead -------------------------------------------------------
    mast = font(SERIF_B, 82)
    d.text((W // 2, 18), "THE WORLD TODAY", font=mast, fill=INK, anchor="ma")
    d.line([(36, 128), (988, 128)], fill=INK, width=4)

    # --- Dateline -------------------------------------------------------
    date_f = font(SANS_B, 23)
    d.text((36, 140), "THURSDAY, 19 NOVEMBER 2026", font=date_f, fill=INK)
    tag = "WORLD NEWS IN ONE IMAGE"
    d.text((988, 140), tag, font=date_f, fill=RED, anchor="ra")
    d.line([(36, 174), (988, 174)], fill=INK, width=2)

    # --- Lead story (left) + illustration (right) ----------------------
    lead_x, lead_w = 36, 560
    y = 196
    y = draw_block(
        d, lead_x, y, lead_w,
        kicker="SHENZHEN SUMMIT",
        headline="Trump, Xi and Putin hold first three-way summit",
        body=("The three leaders met for 90 minutes on the sidelines of the "
              "APEC forum and issued a joint \u201cpeace declaration\u201d \u2014 "
              "pledging UN reform, nuclear talks and more oil output. "
              "No breakthrough on Ukraine or Iran."),
        kick_f=font(SANS_B, 25),
        head_f=font(SERIF_B, 54),
        body_f=font(SERIF, 23),
        head_leading=62, body_leading=30,
        max_head_lines=3,
    )
    assert y <= 585, f"lead overflows: ends at y={y}"

    # --- Illustration: three flags over the Shenzhen skyline -----------
    px0, py0, px1, py1 = 624, 196, 988, 548
    d.rectangle([px0, py0, px1, py1], fill=NAVY)
    # stars
    for sx, sy in [(660, 220), (740, 250), (860, 215), (950, 280),
                   (700, 300), (900, 320), (800, 235)]:
        d.ellipse([sx, sy, sx + 3, sy + 3], fill=(255, 255, 255))
    # skyline silhouette
    base = py1 - 58
    skyline = [(624, base), (660, base), (660, base - 60), (690, base - 60),
               (690, base - 110), (700, base - 110), (700, base - 60),
               (740, base - 60), (740, base - 40), (790, base - 40),
               (790, base - 140), (800, base - 140), (800, base - 40),
               (850, base - 40), (850, base - 80), (890, base - 80),
               (890, base - 50), (940, base - 50), (940, base - 90),
               (960, base - 90), (960, base), (988, base)]
    d.polygon(skyline, fill=(12, 20, 40))
    # windows
    for wx in range(668, 980, 22):
        for wy in range(base - 120, base - 8, 18):
            if (wx * 7 + wy * 13) % 5 == 0:
                d.rectangle([wx, wy, wx + 4, wy + 6], fill=(255, 214, 120))
    # flags
    draw_flag(d, 660, 250, 64, 40, "us")
    draw_flag(d, 780, 235, 64, 40, "cn")
    draw_flag(d, 900, 250, 64, 40, "ru")
    # caption bar
    d.rectangle([px0, py1 - 34, px1, py1], fill=(0, 0, 0))
    d.text((px0 + 10, py1 - 28), "Shenzhen, China",
           font=font(SANS, 19), fill=(255, 255, 255))

    d.line([(36, 600), (988, 600)], fill=INK, width=3)

    # --- Secondary stories, 2 x 2 --------------------------------------
    col_w = 452
    kick_f = font(SANS_B, 21)
    head_f = font(SERIF_B, 33)
    body_f = font(SERIF, 20)
    stories = [
        (36, 622, "UKRAINE",
         "Kerch Bridge hit for a third time",
         "Ukraine hit the Crimea bridge a third time; part of its span "
         "fell. Putin vows revenge."),
        (536, 622, "IRAN WAR",
         "Iran hits Gulf states; Riyadh tower damaged",
         "Tehran hit Gulf neighbours after the US strike on Qeshm; "
         "a missile hit Riyadh."),
        (36, 800, "JUSTICE",
         "UN court: Myanmar committed genocide",
         "The court ruled Myanmar committed genocide against "
         "the Rohingya."),
        (536, 800, "GAZA",
         "Israeli tanks push into central Gaza",
         "Israel sent tanks beyond the ceasefire line near Nuseirat; "
         "Hamas calls it a violation."),
    ]
    for x, yy, kicker, headline, body in stories:
        end = draw_block(d, x, yy, col_w, kicker, headline, body,
                         kick_f, head_f, body_f, 37, 25,
                         max_head_lines=2)
        assert end <= 968, f"story '{kicker}' overflows: ends at y={end}"
    # column divider
    d.line([(512, 622), (512, 955)], fill=(200, 195, 185), width=1)

    # --- Also today strip ------------------------------------------------
    d.line([(36, 972), (988, 972)], fill=INK, width=2)
    d.text((36, 982),
           "ALSO TODAY:  North Korea expands uranium enrichment, IAEA says"
           "  \u00b7  Denmark approves Greenland deal",
           font=font(SANS, 17), fill=GREY)
    d.text((36, 1004),
           "Sources: Reuters \u00b7 BBC \u00b7 AP \u00b7 Just Security \u2014 compiled 19 Nov 2026",
           font=font(SANS, 14), fill=GREY)
    d.text((988, 1004), "THE WORLD TODAY",
           font=font(SANS_B, 14), fill=GREY, anchor="ra")

    img.save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    main()
