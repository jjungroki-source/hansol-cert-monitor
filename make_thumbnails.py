"""
한솔제지 인증 모니터링 시스템 - Apple 스타일 썸네일 5종 생성
출력: thumbnails/ 폴더에 PNG (1920x1080, 16:9)
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math

W, H = 1920, 1080
OUT  = "thumbnails"
os.makedirs(OUT, exist_ok=True)

FONT_DIR = r"C:\Windows\Fonts"
def F(name, size):
    paths = {
        "bold_kr":  "malgunbd.ttf",
        "reg_kr":   "malgun.ttf",
        "bold_en":  "arialbd.ttf",
        "reg_en":   "arial.ttf",
        "ui_bold":  "segoeuib.ttf",
        "ui_reg":   "segoeui.ttf",
    }
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, paths[name]), size)
    except Exception:
        return ImageFont.load_default()

def center_text(draw, text, font, y, color, W=W):
    bb   = draw.textbbox((0, 0), text, font=font)
    tw   = bb[2] - bb[0]
    draw.text(((W - tw) / 2, y), text, font=font, fill=color)

def rounded_rect(draw, xy, radius, fill, outline=None, width=2):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                           outline=outline, width=width)

def gradient_bg(img, color_top, color_bot):
    px = img.load()
    r0,g0,b0 = color_top
    r1,g1,b1 = color_bot
    for y in range(H):
        t = y / H
        r = int(r0 + (r1-r0)*t)
        g = int(g0 + (g1-g0)*t)
        b = int(b0 + (b1-b0)*t)
        for x in range(W):
            px[x, y] = (r, g, b, 255)

def shadow_rect(img, draw, xy, radius, fill, shadow_color=(0,0,0,50), blur=18, offset=(0,8)):
    # Draw shadow
    sx, sy = offset
    x0,y0,x1,y1 = xy
    sh = Image.new("RGBA", img.size, (0,0,0,0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle([x0+sx, y0+sy, x1+sx, y1+sy], radius=radius,
                         fill=shadow_color)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB"), (0,0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([x0,y0,x1,y1], radius=radius, fill=fill)
    return draw


# ══════════════════════════════════════════════════════════
# Thumbnail 1 — Hero / 메인 대시보드
# ══════════════════════════════════════════════════════════
def make_thumb1():
    img  = Image.new("RGB", (W, H))
    gradient_bg(img, (15, 15, 25), (25, 20, 50))
    draw = ImageDraw.Draw(img)

    # Subtle grid lines
    for x in range(0, W, 80):
        draw.line([(x, 0), (x, H)], fill=(255,255,255,10), width=1)
    for y in range(0, H, 80):
        draw.line([(0, y), (W, y)], fill=(255,255,255,10), width=1)

    # Glow circle background
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd   = ImageDraw.Draw(glow)
    for r in range(320, 0, -20):
        alpha = int(18 * (1 - r/320))
        gd.ellipse([W//2-r, H//2-r, W//2+r, H//2+r], fill=(100,120,255,alpha))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Brand pill
    pill_w = 320
    rounded_rect(draw, [W//2-pill_w//2, 120, W//2+pill_w//2, 168],
                 radius=24, fill=(255,255,255,25))
    center_text(draw, "HANSOL PAPER · CHEONAN", F("ui_bold",22), 131, (180,190,220))

    # Main title
    center_text(draw, "인증 모니터링 시스템", F("bold_kr", 88), 200, (255,255,255))
    center_text(draw, "Certification Monitoring System", F("ui_bold",32), 310, (160,170,200))

    # Divider
    draw.line([(W//2-200, 372), (W//2+200, 372)], fill=(100,120,255,180), width=2)

    # 4 cert badges
    badges = [
        ("🌲", "FSC CoC", "#34C759"),
        ("♻️", "환경표지", "#007AFF"),
        ("📋", "ISO 9001/14001", "#FF9500"),
        ("🌱", "Vegan", "#AF52DE"),
    ]
    bw, bh = 280, 130
    gap    = 40
    total  = len(badges) * bw + (len(badges)-1) * gap
    sx     = (W - total) // 2
    by     = 420

    for i, (icon, label, color) in enumerate(badges):
        bx = sx + i * (bw + gap)
        r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
        rounded_rect(draw, [bx, by, bx+bw, by+bh], radius=20,
                     fill=(r,g,b,40), outline=(r,g,b,120), width=2)
        draw.text((bx+28, by+22), icon, font=F("bold_en",36), fill=(255,255,255))
        draw.text((bx+28, by+68), label, font=F("bold_kr",22), fill=(255,255,255))

    # Status strip
    statuses = [
        ("FSC CoC", "D+312", "#34C759"),
        ("EL 5건", "D-127", "#FF9500"),
        ("ISO 9001", "D-83", "#FF3B30"),
        ("ISO 14001", "D+275", "#34C759"),
        ("KV Vegan", "D-24", "#FF3B30"),
    ]
    sy2 = 620
    sw2 = 280
    sx2 = (W - (len(statuses)*sw2 + 4*gap)) // 2
    for i, (name, dday, color) in enumerate(statuses):
        rx = sx2 + i*(sw2+gap)
        r,g,b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
        rounded_rect(draw, [rx, sy2, rx+sw2, sy2+90], radius=16,
                     fill=(255,255,255,12))
        draw.text((rx+20, sy2+12), name, font=F("reg_kr",18), fill=(200,210,230))
        draw.text((rx+20, sy2+44), dday, font=F("bold_en",28), fill=(r,g,b))

    # Bottom label
    center_text(draw, "한솔제지(주) 천안공장 품질환경팀", F("reg_kr",24), H-80, (120,130,160))

    img.save(f"{OUT}/thumb1_hero.png", "PNG", optimize=True)
    print("thumb1 done")


# ══════════════════════════════════════════════════════════
# Thumbnail 2 — Apple 대시보드 카드 레이아웃
# ══════════════════════════════════════════════════════════
def make_thumb2():
    img  = Image.new("RGB", (W, H), (245, 245, 247))
    draw = ImageDraw.Draw(img)

    # Top bar
    draw.rectangle([0, 0, W, 90], fill=(255,255,255))
    draw.line([(0,90),(W,90)], fill=(210,210,215), width=1)
    draw.text((60, 24), "한솔제지 천안공장 인증 모니터링", font=F("bold_kr",34), fill=(29,29,31))
    draw.text((60, 64), "Certification Dashboard · 실시간 현황", font=F("reg_kr",20), fill=(110,110,115))

    # Sidebar strip
    draw.rectangle([0,0,8,H], fill=(52,199,89))

    # Big KPI cards top row
    cards_top = [
        ("🌲 FSC CoC", "D+312", "갱신심사까지", "#34C759", (240,255,245)),
        ("♻️ 환경표지인증", "5건 관리중", "D-90 이내 2건", "#007AFF", (240,247,255)),
        ("📋 ISO 인증", "2종 운영", "9001 · 14001", "#FF9500", (255,250,240)),
        ("🌱 Vegan 인증", "2종 운영", "KV · TVS", "#AF52DE", (250,240,255)),
    ]
    cw, ch = 400, 200
    cgap   = 28
    ctx    = (W - (len(cards_top)*cw + (len(cards_top)-1)*cgap)) // 2
    cty    = 130

    for i, (title, value, sub, color, bg) in enumerate(cards_top):
        cx = ctx + i*(cw+cgap)
        r,g,b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)

        # Shadow
        sh = Image.new("RGBA", (W,H), (0,0,0,0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle([cx+4, cty+8, cx+cw+4, cty+ch+8], radius=20, fill=(0,0,0,30))
        sh = sh.filter(ImageFilter.GaussianBlur(12))
        img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
        draw = ImageDraw.Draw(img)

        draw.rounded_rectangle([cx, cty, cx+cw, cty+ch], radius=20, fill=bg)
        draw.rounded_rectangle([cx, cty, cx+cw, cty+6], radius=20, fill=(r,g,b))
        draw.rectangle([cx, cty+3, cx+cw, cty+9], fill=bg)
        draw.text((cx+24, cty+28), title, font=F("bold_kr",22), fill=(29,29,31))
        draw.text((cx+24, cty+78), value, font=F("bold_kr",40), fill=(r,g,b))
        draw.text((cx+24, cty+132), sub, font=F("reg_kr",20), fill=(110,110,115))

    # Bottom large panel
    py = cty + ch + 50
    ph = H - py - 60

    sh2 = Image.new("RGBA", (W,H), (0,0,0,0))
    sd2 = ImageDraw.Draw(sh2)
    sd2.rounded_rectangle([60+4, py+8, W-60+4, py+ph+8], radius=24, fill=(0,0,0,25))
    sh2 = sh2.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img.convert("RGBA"), sh2).convert("RGB")
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([60, py, W-60, py+ph], radius=24, fill=(255,255,255))

    # Table header
    draw.rectangle([60, py, W-60, py+52], fill=(245,245,247))
    draw.rounded_rectangle([60, py, W-60, py+52], radius=24, fill=(245,245,247))
    draw.rectangle([60, py+26, W-60, py+52], fill=(245,245,247))

    cols = [("인증명",200),("인증번호",260),("인증기간",380),("다음심사",280),("D-day",180),("상태",160)]
    hx = 100
    for col, cw2 in cols:
        draw.text((hx, py+16), col, font=F("bold_kr",18), fill=(110,110,115))
        hx += cw2

    rows = [
        ("🌲 FSC CoC",        "FSC-C012345",     "2026~2031",  "2027-02-11", "D+312", "#34C759"),
        ("♻️ 인쇄용지 A4",    "EL-2023-001",     "2023~2026",  "2026-03-15", "D-283", "#34C759"),
        ("♻️ 복사용지 80g",   "EL-2022-008",     "2022~2025",  "2025-06-30", "D-19",  "#FF3B30"),
        ("📋 ISO 9001",       "QMS-2022-00123", "2022~2025",  "2025-09-01", "D-83",  "#FF9500"),
        ("📋 ISO 14001",      "EMS-2023-00456", "2023~2026",  "2025-03-15", "D+275", "#34C759"),
    ]
    for ri, row in enumerate(rows):
        ry = py + 60 + ri*58
        if ri % 2 == 0:
            draw.rectangle([62, ry, W-62, ry+57], fill=(252,252,254))
        rx = 100
        for ci, (col, cw2) in enumerate(cols):
            val = row[ci] if ci < len(row)-1 else ""
            color_val = (29,29,31)
            if ci == 4:  # D-day
                dcolor = row[5]
                r2,g2,b2 = int(dcolor[1:3],16), int(dcolor[3:5],16), int(dcolor[5:7],16)
                draw.rounded_rectangle([rx-4, ry+10, rx+cw2-16, ry+42], radius=8,
                                       fill=(r2,g2,b2,30))
                draw.text((rx+4, ry+14), row[4], font=F("bold_en",20), fill=(r2,g2,b2))
            elif ci == 5:
                pass
            else:
                draw.text((rx, ry+18), val, font=F("reg_kr",18), fill=color_val)
            rx += cw2

    img.save(f"{OUT}/thumb2_dashboard.png", "PNG", optimize=True)
    print("thumb2 done")


# ══════════════════════════════════════════════════════════
# Thumbnail 3 — 자동 이메일 알림 시스템
# ══════════════════════════════════════════════════════════
def make_thumb3():
    img  = Image.new("RGB", (W, H), (255,255,255))
    draw = ImageDraw.Draw(img)

    # Left panel - dark
    draw.rectangle([0, 0, W//2, H], fill=(18,18,28))

    # Left content
    draw.text((100, 130), "심사 전날까지", font=F("bold_kr",78), fill=(200,210,230))
    draw.text((100, 224), "까먹어도 괜찮아.", font=F("bold_kr",78), fill=(255,255,255))

    # accent underline
    draw.line([(100, 316), (570, 316)], fill=(100,120,255), width=4)

    draw.text((100, 338), "D-90부터 D-3까지, 알아서 챙겨드립니다", font=F("bold_kr",32), fill=(100,120,255))
    draw.text((100, 392), "FSC · ISO · 환경표지 · Vegan  전 인증 커버", font=F("ui_reg",22), fill=(160,170,200))

    draw.line([(100,444),(480,444)], fill=(60,60,100), width=1)

    draw.text((100, 464), "매일 오전 자동 체크  →  해당 담당자에게 즉시 발송",   font=F("reg_kr",20), fill=(180,190,220))
    draw.text((100, 498), "놓친 심사 0건.  당신은 그냥 준비만 하세요.",           font=F("bold_kr",20), fill=(255,255,255))

    # Timeline
    stages = [
        ("D-90", "3개월 전\n일정 안내",  "#34C759"),
        ("D-60", "2개월 전\n자료 요청",  "#FF9500"),
        ("D-30", "1개월 전\n내부심사",   "#FF9F0A"),
        ("D-3",  "3일 전\n최종점검",     "#FF3B30"),
    ]
    ty = 600
    for i, (dday, label, color) in enumerate(stages):
        tx = 100 + i * 190
        r,g,b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
        draw.ellipse([tx, ty, tx+68, ty+68], fill=(r,g,b))
        draw.text((tx+6, ty+14), dday, font=F("bold_en",20), fill=(255,255,255))
        for li, line in enumerate(label.split("\n")):
            draw.text((tx-6, ty+80+li*26), line, font=F("reg_kr",18), fill=(200,210,230))
        if i < 3:
            draw.line([(tx+68, ty+34),(tx+190, ty+34)], fill=(80,80,120), width=2)

    # Right panel - email preview cards (실제 이메일 제목 기반)
    rx = W//2 + 60
    emails = [
        ("[FSC CoC] 사후심사까지 90일 남았습니다",        "지금 시작하면 딱 맞아요. 일정 미리 공유드려요.",  "#34C759"),
        ("[ISO 9001] 서류 준비, 지금이 적기입니다",        "60일 후 심사. 체크리스트 같이 확인해볼까요?",     "#007AFF"),
        ("[환경표지] 내부심사 한 달 전, 잊지 않으셨죠?",  "담당자분들, 오늘 딱 한 번만 확인해주세요.",      "#FF9500"),
        ("[FSC CoC] D-3. 이제 진짜 막판입니다 ⚠️",       "준비물 최종 체크 · 심사 당일 타임라인 안내",      "#FF3B30"),
    ]
    ey = 100
    for i, (title, body, color) in enumerate(emails):
        r,g,b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)

        sh = Image.new("RGBA", (W,H), (0,0,0,0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle([rx+4, ey+8, rx+760+4, ey+124+8], radius=16, fill=(0,0,0,30))
        sh = sh.filter(ImageFilter.GaussianBlur(10))
        img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
        draw = ImageDraw.Draw(img)

        draw.rounded_rectangle([rx, ey, rx+760, ey+124], radius=16, fill=(255,255,255))
        draw.rounded_rectangle([rx, ey, rx+6, ey+124], radius=16, fill=(r,g,b))
        draw.rectangle([rx+3, ey, rx+9, ey+124], fill=(r,g,b))
        draw.rectangle([rx+6, ey, rx+12, ey+124], fill=(255,255,255))

        # 태그 뱃지
        tag_labels = ["D-90", "D-60", "D-30", "D-3"]
        tag = tag_labels[i]
        tbb = draw.textbbox((0,0), tag, font=F("bold_en",16))
        tw2 = tbb[2]-tbb[0]
        draw.rounded_rectangle([rx+680, ey+16, rx+680+tw2+20, ey+42], radius=10, fill=(r,g,b,40))
        draw.text((rx+690, ey+20), tag, font=F("bold_en",16), fill=(r,g,b))

        draw.text((rx+28, ey+18), title, font=F("bold_kr",20), fill=(29,29,31))
        draw.text((rx+28, ey+58), body, font=F("reg_kr",17), fill=(110,110,115))
        draw.text((rx+28, ey+90), "자동 발송  ·  수신: 품질환경팀 · 생산팀 · 구매팀", font=F("reg_kr",15), fill=(180,180,190))
        ey += 154

    # Bottom brand
    draw.text((rx, H-60), "한솔제지(주) 천안공장  ·  인증 모니터링 시스템  ·  자동 발송 기능", font=F("reg_kr",20), fill=(160,160,180))

    img.save(f"{OUT}/thumb3_email.png", "PNG", optimize=True)
    print("thumb3 done")


# ══════════════════════════════════════════════════════════
# Thumbnail 4 — ROKI AI 챗봇
# ══════════════════════════════════════════════════════════
def make_thumb4():
    img = Image.new("RGB", (W, H), (8, 8, 16))
    gradient_bg(img, (8,8,20), (20,12,40))
    draw = ImageDraw.Draw(img)

    # Particle dots
    import random
    random.seed(42)
    for _ in range(120):
        x = random.randint(0, W)
        y = random.randint(0, H)
        r2 = random.randint(1, 3)
        a  = random.randint(40, 140)
        draw.ellipse([x-r2, y-r2, x+r2, y+r2], fill=(200,200,255,a))

    # Large ROKI logo
    roki_colors = [(0,122,255),(175,82,222),(52,199,89)]
    logo_y = 120
    draw.text((W//2 - 380, logo_y), "ROKI", font=F("bold_en", 300), fill=(255,255,255,15))

    # Gradient text effect (3 colored layers)
    for offset, color in [(-2, (0,122,255)), (0, (175,82,222)), (2, (52,199,89))]:
        bb = draw.textbbox((0,0), "ROKI", font=F("bold_en",220))
        tw = bb[2]-bb[0]
        draw.text(((W-tw)//2+offset, logo_y+offset), "ROKI",
                  font=F("bold_en",220), fill=(*color, 180))

    # Main ROKI text (white)
    bb = draw.textbbox((0,0), "ROKI", font=F("bold_en",220))
    tw = bb[2]-bb[0]
    draw.text(((W-tw)//2, logo_y), "ROKI", font=F("bold_en",220), fill=(255,255,255))

    center_text(draw, "Recognition & Certification Knowledge Intelligence",
                F("ui_bold",26), logo_y+248, (160,170,200))

    # Chat bubbles
    bubbles = [
        ("FSC 다음 심사일이 언제야?",    True,  550),
        ("2027년 2월 11일입니다.",        False, 640),
        ("ISO 9001 인증서 갱신 서류?",   True,  740),
        ("22종 준비 서류 안내해 드릴게요.", False, 830),
    ]
    for text, is_user, by in bubbles:
        bb = draw.textbbox((0,0), text, font=F("reg_kr",22))
        tw = bb[2]-bb[0]
        pad = 28
        bw2 = tw + pad*2
        bh2 = 60

        if is_user:
            bx = W - bw2 - 160
            fill   = (0,122,255)
            tcolor = (255,255,255)
        else:
            bx = 160
            fill   = (40,40,60)
            tcolor = (240,240,255)

        draw.rounded_rectangle([bx, by, bx+bw2, by+bh2], radius=bh2//2, fill=fill)
        draw.text((bx+pad, by+18), text, font=F("reg_kr",22), fill=tcolor)

    # Keywords strip
    kws = ["FSC CoC", "환경표지", "ISO 9001", "ISO 14001", "Vegan KV", "Vegan TVS"]
    kw_total = sum(draw.textbbox((0,0),k,font=F("reg_en",18))[2]+48 for k in kws) + 16*(len(kws)-1)
    kx = (W-kw_total)//2
    ky = H - 80
    for kw in kws:
        bbt = draw.textbbox((0,0), kw, font=F("reg_en",18))
        kw2 = bbt[2]-bbt[0]+48
        draw.rounded_rectangle([kx, ky, kx+kw2, ky+44], radius=22,
                                fill=(255,255,255,20), outline=(255,255,255,60), width=1)
        draw.text((kx+24, ky+12), kw, font=F("reg_en",18), fill=(200,210,230))
        kx += kw2 + 16

    img.save(f"{OUT}/thumb4_roki.png", "PNG", optimize=True)
    print("thumb4 done")


# ══════════════════════════════════════════════════════════
# Thumbnail 5 — 팀 배포 / 동료 공유
# ══════════════════════════════════════════════════════════
def make_thumb5():
    img  = Image.new("RGB", (W, H), (245,245,247))
    draw = ImageDraw.Draw(img)

    # Top accent bar
    for x in range(W):
        t = x / W
        r = int(0   + (175-0)*t)
        g = int(122 + (82-122)*t)
        b = int(255 + (222-255)*t)
        draw.line([(x,0),(x,8)], fill=(r,g,b))

    # Left: Feature list
    draw.text((100, 90), "한솔제지 천안공장", font=F("bold_kr",36), fill=(29,29,31))
    draw.text((100, 140), "인증 모니터링 시스템", font=F("bold_kr",60), fill=(29,29,31))
    draw.text((100, 218), "팀 전체가 함께 사용하는 인증 관리 플랫폼", font=F("reg_kr",26), fill=(110,110,115))

    draw.line([(100,278),(560,278)], fill=(210,210,215), width=1)

    features = [
        ("✅", "6개 인증 통합 현황 실시간 모니터링"),
        ("✅", "D-90/D-60/D-30/D-3 자동 이메일 알림"),
        ("✅", "부서별 수신자 관리 및 맞춤 발송"),
        ("✅", "ROKI AI 인증 전문 챗봇"),
        ("✅", "인증서 디지털 보관 및 조회"),
        ("✅", "FSC 심사 준비 체크리스트"),
    ]
    fy = 300
    for icon, text in features:
        draw.text((100, fy), icon + "  " + text, font=F("reg_kr",24), fill=(29,29,31))
        fy += 52

    # Streamlit badge
    rounded_rect(draw, [100, fy+20, 340, fy+68], radius=34,
                 fill=(255,75,75,220))
    draw.text((126, fy+30), "Streamlit Cloud", font=F("ui_bold",22), fill=(255,255,255))

    rounded_rect(draw, [360, fy+20, 560, fy+68], radius=34,
                 fill=(29,29,31))
    draw.text((385, fy+30), "GitHub 연동", font=F("bold_kr",22), fill=(255,255,255))

    # Right: Mock app screen
    sx, sy, sw, sh2 = W//2+60, 60, 820, 960

    # Screen shadow
    shs = Image.new("RGBA", (W,H), (0,0,0,0))
    sds = ImageDraw.Draw(shs)
    sds.rounded_rectangle([sx+8, sy+12, sx+sw+8, sy+sh2+12], radius=24, fill=(0,0,0,50))
    shs = shs.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img.convert("RGBA"), shs).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Screen frame
    draw.rounded_rectangle([sx, sy, sx+sw, sy+sh2], radius=24, fill=(255,255,255))

    # Browser bar
    draw.rounded_rectangle([sx, sy, sx+sw, sy+sh2], radius=24, fill=(248,248,250))
    draw.rectangle([sx, sy+36, sx+sw, sy+sh2], fill=(248,248,250))
    draw.rounded_rectangle([sx, sy, sx+sw, sy+50], radius=24, fill=(255,255,255))
    draw.rectangle([sx, sy+36, sx+sw, sy+50], fill=(255,255,255))

    # Browser dots
    for di, dc in enumerate([(255,95,87),(255,189,68),(40,205,65)]):
        draw.ellipse([sx+20+di*22, sy+16, sx+34+di*22, sy+30], fill=dc)

    # URL bar
    draw.rounded_rectangle([sx+120, sy+10, sx+sw-20, sy+42], radius=10, fill=(245,245,247))
    draw.text((sx+134, sy+16), "hansol-cert-monitor.streamlit.app", font=F("reg_en",16), fill=(110,110,115))

    # App content
    content_y = sy + 60

    # Sidebar
    draw.rectangle([sx, content_y, sx+160, sy+sh2], fill=(255,255,255))
    draw.line([(sx+160, content_y),(sx+160, sy+sh2)], fill=(210,210,215), width=1)

    nav_items = [("Summary","#34C759"), ("FSC","#34C759"), ("EL","#007AFF"),
                 ("ISO","#FF9500"), ("Vegan","#AF52DE"), ("알림","#FF3B30")]
    nav_y = content_y + 20
    for ni, (name, color) in enumerate(nav_items):
        if ni == 0:
            r2,g2,b2 = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
            draw.rectangle([sx, nav_y-4, sx+160, nav_y+30], fill=(r2,g2,b2,30))
        draw.text((sx+20, nav_y), name, font=F("reg_kr",16), fill=(29,29,31))
        nav_y += 48

    # Main content area
    mx = sx + 172
    mw = sw - 172 - 16

    # Title
    draw.text((mx, content_y+16), "전체 현황 요약", font=F("bold_kr",22), fill=(29,29,31))

    # Mini cards
    mc_y = content_y + 60
    mc_w = (mw - 32) // 2
    for i, (label, val, color) in enumerate([
        ("FSC CoC", "D+312", "#34C759"),
        ("환경표지", "2건 주의", "#FF9500"),
        ("ISO 9001", "D-83", "#FF3B30"),
        ("ISO 14001", "D+275", "#34C759"),
    ]):
        mx2 = mx + (i % 2) * (mc_w + 16)
        my2 = mc_y + (i // 2) * 90
        r3,g3,b3 = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
        draw.rounded_rectangle([mx2, my2, mx2+mc_w, my2+72], radius=10, fill=(245,245,247))
        draw.text((mx2+14, my2+10), label, font=F("reg_kr",13), fill=(110,110,115))
        draw.text((mx2+14, my2+36), val, font=F("bold_en",18), fill=(r3,g3,b3))

    img.save(f"{OUT}/thumb5_team.png", "PNG", optimize=True)
    print("thumb5 done")


if __name__ == "__main__":
    make_thumb1()
    make_thumb2()
    make_thumb3()
    make_thumb4()
    make_thumb5()
    print("\nAll thumbnails saved to:", OUT)
