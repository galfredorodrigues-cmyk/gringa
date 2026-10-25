"""HER POV visual collection: five brand-consistent public marketing PNGs only.

These assets depict covers; private PDF contents NEVER appear in public routes.
"""
from functools import lru_cache
from io import BytesIO
from math import sin, cos, pi
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SIZE = 1000
INK = (13, 18, 27)
GOLD = (212, 177, 113)
PALE = (244, 235, 219)
MUTED = (179, 171, 158)

PRODUCTS = {
    "first-message-formula": dict(vol="01", title=["THE FIRST", "MESSAGE", "FORMULA"],
        subtitle="START NATURAL CONVERSATIONS", detail="56-PAGE DIGITAL GUIDE", symbol="message", accent=(195, 154, 89)),
    "reply-decoder": dict(vol="02", title=["THE REPLY", "DECODER"],
        subtitle="READ THE CONVERSATION, NOT YOUR FEARS", detail="19-PAGE DIGITAL GUIDE", symbol="reply", accent=(162, 143, 182)),
    "profile-makeover": dict(vol="03", title=["THE PROFILE", "MAKEOVER"],
        subtitle="PRESENT YOUR AUTHENTIC SELF", detail="19-PAGE DIGITAL GUIDE", symbol="profile", accent=(155, 192, 179)),
    "from-chat-to-first-date": dict(vol="04", title=["FROM CHAT", "TO FIRST", "DATE"],
        subtitle="TURN MESSAGES INTO REAL PLANS", detail="19-PAGE DIGITAL GUIDE", symbol="date", accent=(209, 160, 138)),
    "complete-library": dict(vol="COLLECTION", title=["THE COMPLETE", "HER POV", "LIBRARY"],
        subtitle="FROM FIRST HELLO TO FIRST DATE", detail="FOUR DIGITAL GUIDES + BONUS", symbol="bundle", accent=(218, 188, 120)),
}

def _font(size, serif=False, italic=False, bold=False):
    candidates = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
         "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"] if serif
        else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
    )
    if serif and italic:
        candidates = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
                      "/usr/share/fonts/truetype/liberation2/LiberationSerif-Italic.ttf"] + candidates
    if bold and not serif:
        candidates = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                      "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"] + candidates
    for f in candidates:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()

def _text(draw, xy, message, size, color=PALE, serif=False, bold=False, italic=False, anchor=None):
    draw.text(xy, message, font=_font(size,serif,italic,bold), fill=color,
              anchor=anchor, stroke_width=0)

def _tracked(draw, xy, message, size=15, space=3, color=GOLD):
    f=_font(size,bold=True)
    x,y=xy
    for c in message:
        draw.text((x,y),c,font=f,fill=color)
        x += draw.textlength(c,font=f) + space

def _line(draw, path, fill=GOLD, width=3, joint="curve"):
    draw.line(path, fill=fill, width=width, joint=joint)

def _symbol(img, name, color, center=(696, 570)):
    d=ImageDraw.Draw(img,"RGBA")
    x,y=center
    light=tuple(color)+(175,)
    if name == "message":
        d.rounded_rectangle((x-120,y-62,x+98,y+52),radius=30,outline=light,width=5)
        d.polygon([(x-60,y+50),(x-94,y+82),(x-84,y+46)],fill=light)
        for i,w in enumerate([138,115,74]):
            yy=y-30+27*i
            d.line((x-72,yy,x-72+w,yy),fill=light,width=4)
    elif name == "reply":
        d.arc((x-119,y-94,x+108,y+103),start=177,end=345,fill=light,width=6)
        d.polygon([(x+98,y-89),(x+123,y-31),(x+55,y-44)],fill=light)
        d.arc((x-80,y-50,x+78,y+79),start=0,end=176,fill=light,width=5)
        d.polygon([(x-81,y+43),(x-52,y+89),(x-12,y+44)],fill=light)
    elif name == "profile":
        d.ellipse((x-44,y-95,x+45,y-6),outline=light,width=6)
        d.arc((x-111,y-7,x+114,y+154),start=181,end=359,fill=light,width=6)
        d.rounded_rectangle((x-133,y-115,x+135,y+129),radius=18,outline=light,width=4)
    elif name == "date":
        d.rounded_rectangle((x-101,y-93,x+104,y+115),radius=10,outline=light,width=5)
        d.line((x-99,y-35,x+103,y-35),fill=light,width=5)
        d.line((x-61,y-117,x-61,y-72),fill=light,width=6)
        d.line((x+64,y-117,x+64,y-72),fill=light,width=6)
        d.ellipse((x-56,y-1,x-14,y+41),outline=light,width=4)
        d.arc((x-20,y-17,x+62,y+70),start=180,end=356,fill=light,width=5)
    else:
        for dx,dy,angle in [(-66,-24,-11),(-18,-42,-4),(31,-34,5),(79,-11,11)]:
            bx=x+dx;by=y+dy
            d.polygon([(bx-46,by-82),(bx+17,by-82),(bx+39,by+100),(bx-26,by+100)],outline=light)
            d.line((bx-25,by-40,bx+22,by-40),fill=light,width=2)
            d.line((bx-18,by+49,bx+28,by+49),fill=light,width=2)

def _background(accent):
    img=Image.new("RGB",(SIZE,SIZE),INK)
    # Efficient vertical light falloff (no per-pixel Python loops).
    d=ImageDraw.Draw(img)
    for y in range(SIZE):
        t=y/(SIZE-1)
        d.line((0,y,SIZE,y),fill=(int(20-7*t),int(25-7*t),int(36-9*t)),width=1)
    glow=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0))
    gd=ImageDraw.Draw(glow)
    gd.ellipse((390,50,1380,1100),fill=accent+(37,))
    gd.ellipse((-430,-490,530,490),fill=(220,173,102,28))
    glow=glow.filter(ImageFilter.GaussianBlur(125))
    img=Image.alpha_composite(img.convert("RGBA"),glow).convert("RGB")
    return img

def _cover(slug):
    data=PRODUCTS[slug];accent=data["accent"];img=_background(accent)
    g=ImageDraw.Draw(img,"RGBA")
    # Visual book body: a deliberate cover mockup without implying a hardcover purchase.
    g.rounded_rectangle((63,53,938,955),radius=18,fill=(21,27,36,255),
                        outline=(82,70,52,255),width=2)
    g.rectangle((73,55,91,953),fill=(80,66,48,180))
    g.line((93,58,93,947),fill=(224,187,119,190),width=3)
    g.rounded_rectangle((111,80,911,925),radius=8,outline=GOLD+(130,),width=2)
    g.rounded_rectangle((126,95,894,909),radius=3,outline=GOLD+(55,),width=1)
    # Soft orbital motif: elegant, not a cheap default card.
    for j in range(5):
        r=175+j*43
        g.arc((710-r,552-r,710+r,552+r),start=234,end=442,
              fill=accent+(60 if j<2 else 35,),width=2)
    g.ellipse((607,445,855,693),fill=accent+(16,))
    _tracked(g,(156,144),"HER POV",22,space=6,color=GOLD)
    _tracked(g,(157,191),"THE CONVERSATION SERIES",12,space=3,color=(170,159,140))
    _line(g,[(156,245),(848,245)],fill=(145,113,65),width=2)
    if slug == "complete-library":
        _tracked(g,(157,292),"EXCLUSIVE COLLECTION",15,space=3,color=accent)
    else:
        _tracked(g,(157,292),"DIGITAL GUIDE / VOLUME "+data["vol"],15,space=3,color=accent)
    title=data["title"];title_font=_font(69 if max(map(len,title))<=14 else 59,serif=True)
    ty=338
    for line in title:
        g.text((149,ty),line,font=title_font,fill=PALE)
        ty+=92
    _line(g,[(156,ty+18),(397,ty+18)],fill=accent,width=4)
    sub=data["subtitle"]
    sf=17 if len(sub)>37 else 19
    _tracked(g,(156,ty+43),sub,sf,space=0.7,color=accent)
    _symbol(img,data["symbol"],accent,(689,689 if slug=="complete-library" else 702))
    g=ImageDraw.Draw(img,"RGBA")
    _line(g,[(157,823),(849,823)],fill=(144,118,79),width=2)
    _tracked(g,(157,845),data["detail"],13,space=2,color=PALE)
    _tracked(g,(157,879),"HER POV / 2026",11,space=2,color=(170,163,151))
    # A thin foil rule catches the viewer's eye at thumbnail scale.
    g.line((137,101,882,101),fill=(232,197,127),width=2)
    return img

@lru_cache(maxsize=10)
def cover_png(slug):
    if slug not in PRODUCTS:
        raise KeyError(slug)
    img=_cover(slug)
    buffer=BytesIO()
    img.save(buffer,format="PNG",optimize=True)
    return buffer.getvalue()
