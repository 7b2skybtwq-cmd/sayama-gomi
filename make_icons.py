from PIL import Image, ImageDraw
from pathlib import Path
OUT = Path(__file__).resolve().parent / 'icons'
OUT.mkdir(exist_ok=True)
BLACK=(10,10,10,255)

def save(name, draw_fn):
    im=Image.new('RGBA',(512,512),(255,255,255,0)); d=ImageDraw.Draw(im); draw_fn(d); im.save(OUT/name)

def burnable(d):
    d.polygon([(210,75),(250,45),(290,75),(330,55),(370,88),(340,130),(172,130),(142,88),(182,55)], fill=BLACK)
    d.rounded_rectangle((125,135,387,420), radius=120, fill=BLACK)
    d.pieslice((190,220,330,405), 100, 430, fill=(255,255,255,0))
    d.pieslice((225,285,310,410), 100, 430, fill=BLACK)
    d.pieslice((170,260,260,410), 90, 440, fill=(255,255,255,0))

def none(d):
    d.ellipse((75,75,437,437), outline=BLACK, width=45)
    d.line((135,135,377,377), fill=BLACK, width=48)

def paper(d):
    for off in [45,25,5]:
        d.polygon([(95,250+off),(300,170+off),(430,245+off),(220,330+off)], fill=BLACK)
        d.line((110,260+off,220,315+off,420,248+off), fill=(255,255,255,0), width=12)
    d.line((130,205,380,315), fill=(255,255,255,0), width=12)
    d.ellipse((200,145,315,230), outline=BLACK, width=18)
    d.line((256,210,256,330), fill=BLACK, width=16)

def bin_can(d):
    d.rounded_rectangle((135,105,245,405), radius=35, fill=BLACK)
    d.rounded_rectangle((125,95,255,125), radius=8, fill=BLACK)
    d.ellipse((285,190,400,230), fill=BLACK)
    d.rectangle((285,210,400,380), fill=BLACK)
    d.ellipse((285,360,400,400), fill=BLACK)
    d.ellipse((315,200,370,218), fill=(255,255,255,0))

def pet(d):
    d.rounded_rectangle((220,55,292,100), radius=8, fill=BLACK)
    d.rounded_rectangle((195,100,317,440), radius=55, outline=BLACK, width=24)
    for y in [190,245,300]: d.line((205,y,307,y), fill=BLACK, width=18)
    d.arc((210,390,255,460),0,180,fill=BLACK,width=18); d.arc((255,390,302,460),0,180,fill=BLACK,width=18)

def plastic(d):
    d.rounded_rectangle((105,130,407,382), radius=55, outline=BLACK, width=38)
    d.polygon([(365,118),(435,180),(365,242)], fill=BLACK)
    d.polygon([(147,394),(77,332),(147,270)], fill=BLACK)
    # プラ as graphic blocks not actual text to avoid font dependency in icon
    d.ellipse((205,220,250,265), fill=BLACK)
    d.rectangle((190,260,320,300), fill=BLACK)
    d.rectangle((250,200,290,305), fill=BLACK)

def nonburn(d):
    d.rounded_rectangle((160,130,352,400), radius=35, fill=BLACK)
    d.rounded_rectangle((135,110,377,165), radius=12, fill=BLACK)
    d.rounded_rectangle((225,70,287,125), radius=12, fill=BLACK)
    for x in [205,256,307]: d.rounded_rectangle((x,205,x+20,350), radius=10, fill=(255,255,255,0))

save('burnable.png', burnable)
save('bottles_cans.png', bin_can)
save('pet.png', pet)
save('plastic.png', plastic)
save('paper_cloth.png', paper)
save('nonburnable.png', nonburn)
save('none.png', none)
