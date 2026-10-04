#!/usr/bin/env python3
"""Generate terminal-style blog covers matching haryo.id theme (IBM Plex-ish mono look).

Light theme: bg #f6f4ee, ink #1b1f23, accent #0f7b6c
Dark theme:  bg #14171b, ink #e7e4dc, accent #4fbbac
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

# Dark theme like the site default
bg = (20, 23, 27)        # #14171b
ink = (231, 228, 220)    # #e7e4dc
muted = (144, 153, 163)  # #9099a3
accent = (79, 187, 172)  # #4fbbac
line = (42, 46, 51)      # #2a2e33


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def make_cover(path, prompt_line, lines, title):
    global bg, ink, muted, accent, line
    # Dark theme like the site default
    bg = (20, 23, 27)        # #14171b
    ink = (231, 228, 220)    # #e7e4dc
    muted = (144, 153, 163)  # #9099a3
    accent = (79, 187, 172)  # #4fbbac
    line = (42, 46, 51)      # #2a2e33

    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    # Subtle grid dots
    for x in range(0, W, 40):
        for y in range(0, H, 40):
            d.point((x, y), fill=line)

    # Browser window frame
    mx, my, mw, mh = 80, 70, W - 160, H - 140
    d.rounded_rectangle([mx, my, mx + mw, my + mh], radius=14, fill=(26, 30, 35), outline=line, width=2)
    # Title bar
    d.line([mx, my + 48, mx + mw, my + 48], fill=line, width=2)
    # Traffic lights
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = mx + 28 + i * 30
        d.ellipse([cx - 8, my + 24 - 8, cx + 8, my + 24 + 8], fill=c)

    # Prompt line
    f_prompt = font(MONO, 22)
    d.text((mx + 32, my + 72), "$ " + prompt_line, font=f_prompt, fill=accent)

    # Output lines
    f_body = font(MONO, 26)
    y = my + 130
    for text, color in lines:
        d.text((mx + 32, y), text, font=f_body, fill=color)
        y += 44

    # Blinking cursor block at the end
    d.rectangle([mx + 32, y + 6, mx + 52, y + 32], fill=accent)

    # Title badge bottom-left
    f_title = font(MONO_BOLD, 20)
    tw = d.textlength(title, font=f_title)
    bx, by = 80, H - 76
    d.rounded_rectangle([bx, by, bx + tw + 40, by + 44], radius=8, fill=(15, 123, 108))
    d.text((bx + 20, by + 10), title, font=f_title, fill=(255, 255, 255))

    # Footer url
    f_url = font(MONO, 18)
    url = "haryo.id"
    uw = d.textlength(url, font=f_url)
    d.text((W - 80 - uw, H - 62), url, font=f_url, fill=muted)

    img.save(path, "PNG")
    print("saved", path)


if __name__ == "__main__":
    make_cover(
        "/root/haryo-id/public/images/security-headers-cover.png",
        "curl -sI https://haryo.id | grep -i security",
        [
            ("strict-transport-security: max-age=31536000", muted),
            ("x-frame-options: DENY", muted),
            ("x-content-type-options: nosniff", muted),
            ("referrer-policy: strict-origin-when-cross-origin", muted),
            ("# grade: A", accent),
        ],
        "security headers",
    )
    make_cover(
        "/root/haryo-id/public/images/cpanel-email-backup-cover.png",
        "tar -czf mail-backup.tar.gz ~/mail/haryo.id/info",
        [
            ("mail/haryo.id/info/cur/   412 messages", muted),
            ("mail/haryo.id/info/new/    23 messages", muted),
            ("compressing... done", muted),
            ("sha256sum mail-backup.tar.gz", muted),
            ("# backup OK", accent),
        ],
        "email backup",
    )
    make_cover(
        "/root/haryo-id/public/images/spamexpert-exchange-cover.png",
        "New-SendConnector -SmartHosts smtp.antispamcloud.com",
        [
            ("AddressSpaces        : {*}", muted),
            ("SmartHostAuthMechanism : BasicAuth", muted),
            ("MX  10 mx.spamexperts.com", muted),
            ("relay: exchange -> spamexpert -> internet", muted),
            ("# mail flow OK", accent),
        ],
        "spamexpert x exchange",
    )
    make_cover(
        "/root/haryo-id/public/images/fstab-emergency-mode-cover.png",
        "systemctl status dev-mapper-vg\\x2dold.device",
        [
            ("You are in emergency mode...", muted),
            ("Timed out waiting for device /dev/mapper/vg-old", muted),
            ("nano /etc/fstab   # hapus/komen entry lama", muted),
            ("systemctl reboot", muted),
            ("# boot normal kembali", accent),
        ],
        "emergency mode fstab",
    )
