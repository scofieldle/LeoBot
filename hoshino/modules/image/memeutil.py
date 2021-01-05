import requests
import hoshino
from os import path
from io import BytesIO
from PIL import Image,ImageFont,ImageDraw

font_path = path.abspath("./simhei.ttf")
img_dir = path.join(path.abspath(path.dirname(__file__)),"meme/")

offset = 5 #文字与表情之间的留白

def get_width(text): #ASCII字符宽0.5，其它宽1
    w = 0
    for s in text:
        w += 0.5 if ord(s)<=127 else 1
    return w 

def add_text(img: Image,text:str,textsize:int,font=font_path,textfill='black',position:tuple=(0,0)):
    #textfill 文字颜色，默认黑色
    #position 文字位置，图片左上角为起点
    img_font = ImageFont.truetype(font=font,size=textsize)
    draw = ImageDraw.Draw(img)
    draw.text(xy=position,text=text,font=img_font,fill=textfill)
    return img

def draw_meme(img: Image, text:str):
    text_l = text.split('\n')
    rows = len(text_l)
    text_len = max([get_width(s) for s in text_l])

    tsize = int(img.width / text_len)
    tsize = min(tsize,100) #太大了
    position = ((img.width - text_len*tsize)//2,img.height+offset)
    meme_width = img.width
    meme_height = img.height + tsize*rows + offset*2 #底部留白
    meme = Image.new(mode="RGB",size=(meme_width,meme_height),color="white")
    meme.paste(img,(0,0,img.width,img.height))
    add_text(meme,text,textsize=tsize,position=position)
    return meme

def download_meme(url:str, file_name:str): 
	try:
		rsp = requests.get(url, stream=True, timeout=5)
		save_path = path.join(img_dir, file_name + '.jpg')
	except:
		return ""
	if 200 == rsp.status_code:
		img = Image.open(BytesIO(rsp.content))
		img.save(save_path)
		return save_path
	else:
		return ""