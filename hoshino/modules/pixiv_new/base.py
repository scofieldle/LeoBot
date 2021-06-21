import random
import string
import base64
from io import BytesIO
from PIL import Image
from hoshino.util import pic2b64
from .pixiv import download_image, native_get, pixiv_init

def add_salt(data):
    salt = ''.join(random.sample(string.ascii_letters + string.digits, 6))
    return data + bytes(salt, encoding="utf8")

def format_setu_msg(image, item):
    base64_str = f"base64://{base64.b64encode(add_salt(image)).decode()}"
    temp = ''
    for name in item['tags']:
        temp = temp + name + '\t'
    msg = f'id:{item["id"]}\ntitle:{item["title"]}\nauthor_id:{item["author_id"]}\nauthor:{item["author"]}\nlove:{item["bookmarks"]}\ndate:{item["date"]}\ntags:{temp}\n[CQ:image,file={base64_str}]'
    return msg

async def get_setu(item):
    path = './res/img/pixiv/' + str(item['id']) + '.jpg'
    if not native_get(item['id']):
        await download_image(item['url'], item['id'])
    im = Image.open(path)
    img_byte = BytesIO()
    im.save(img_byte, format='JPEG') # format: PNG or JPEG
    binary_content = img_byte.getvalue()  # im对象转为二进制流
    msg = format_setu_msg(binary_content, item)
    return msg

pixiv_init()