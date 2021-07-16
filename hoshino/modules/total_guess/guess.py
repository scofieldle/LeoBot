from hoshino.modules.priconne import chara
from hoshino.modules.priconne import _pcr_data as pcr_data
from hoshino.util import pic2b64
import base64, json
from io import BytesIO
from PIL import Image
import math, os, random
from . import mrfz_data
from . import mrfz_chara_data
from ._chara import *
from . import pcr_chara_data
from nonebot import MessageSegment
  
def pcr_img_guess():
    try:
        PIC_SIDE_LENGTH = 25 
        LH_SIDE_LENGTH = 75
        BLACKLIST_ID = [1072, 1908, 4031, 9000]
        head = {'flag':True,'answer':[], 'img':'','game_type':'img','question_list':[]}
        
        chara_id_list = list(pcr_data.CHARA_NAME.keys())
        while True:
            random.shuffle(chara_id_list)
            if chara_id_list[0] not in BLACKLIST_ID: break
        head['answer'] = pcr_data.CHARA_NAME[chara_id_list[0]]
        
        c = chara.fromid(chara_id_list[0])
        PIC_PATH = os.path.join(os.path.dirname(__file__),'fullcard')
        big_path = os.path.join(PIC_PATH,f'{chara_id_list[0]}31.png')
        
        lh_flag=0
        if  os.path.exists(big_path):
            img = Image.open(big_path)
            bio = BytesIO()
            img.save(bio, format='PNG')
            base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
            head['img'] = f"[CQ:image,file={base64_str}]"
            lh_flag = 1
        else:
            head['img'] = c.icon.cqcode
            img = c.icon.open()
        if lh_flag==1:
            left = math.floor(random.random()*(705-LH_SIDE_LENGTH))
            upper = math.floor(random.random()*(397-LH_SIDE_LENGTH))
            cropped = img.crop((left, upper, left+LH_SIDE_LENGTH, upper+LH_SIDE_LENGTH))
            pic_type = '立绘'
        else:
            left = math.floor(random.random()*(129-PIC_SIDE_LENGTH))
            upper = math.floor(random.random()*(129-PIC_SIDE_LENGTH))
            cropped = img.crop((left, upper, left+PIC_SIDE_LENGTH, upper+PIC_SIDE_LENGTH))
            pic_type = '头像'
            
        buf = BytesIO()
        cropped.save(buf,format='PNG')
        base64_str = 'base64://' + base64.b64encode(buf.getvalue()).decode()
        image = f"[CQ:image,file={base64_str}]"
        head['question_list'] = f'猜猜这个图片是哪位pcr角色{pic_type}的一部分?(20s后公布答案){image}'
        return head
    except Exception as e:
        print('pcr_img', e)

def mrfz_img_guess():
    try:
        BLACKLIST_ID = [1000]
        PIC_SIDE_LENGTH = 60
        head = {'flag':True,'answer':[], 'img':'','game_type':'img','question_list':[]}

        chara_id_list = list(mrfz_data.CHARA_NAME.keys())
        while True:
            random.shuffle(chara_id_list)
            if chara_id_list[0] not in BLACKLIST_ID: break
        c = OtherChara(chara_id_list[0])
        head['answer'].append(c.name)
        head['img'] = c.icon.cqcode
        
        img = c.icon.open()
        left = math.floor(random.random() * (129 - PIC_SIDE_LENGTH))
        upper = math.floor(random.random() * (230 - PIC_SIDE_LENGTH))
        cropped = img.crop((left, upper, left + PIC_SIDE_LENGTH, upper + PIC_SIDE_LENGTH))
        
        buf = BytesIO()
        cropped.save(buf,format='PNG')
        base64_str = 'base64://' + base64.b64encode(buf.getvalue()).decode()
        image = f"[CQ:image,file={base64_str}]"
        head['question_list'] = f'猜猜这个图片是哪位干员头像的一部分?(20s后公布答案){image}'
        return head
    except Exception as e:
        print('mrfz_img', e)

def pcr_word_guess():
    try:
        BLACKLIST_ID = [1072, 1908, 4031, 9000]
        head = {'flag':True,'answer':[], 'img':'','game_type':'word','question_list':[]}
        desc_lable = ['名字', '声优', '身高', '体重', '年龄', '生日', '星座', '血型', '种族', '喜好', '公会', 'ub', '一技能', '二技能', 'ex技能']
        index_list = list(range(1,15))
        random.shuffle(index_list)
        
        chara_id_list = list(pcr_chara_data.CHARA_DATA.keys())
        while True:
            random.shuffle(chara_id_list)
            if chara_id_list[0] not in BLACKLIST_ID: break
        
        c = chara.fromid(chara_id_list[0])
        head['answer'] = pcr_data.CHARA_NAME[chara_id_list[0]]
        head['img'] = c.icon.cqcode
        
        chara_desc_list = pcr_chara_data.CHARA_DATA[chara_id_list[0]]
        for i in range(5):
            desc_index = index_list[i]
            head['question_list'].append(f'提示{i+1}/5:\n她的{desc_lable[desc_index]}是 {chara_desc_list[desc_index]}')
            
        return head
    except Exception as e:
        print('pcr_word', e)
    
def mrfz_word_guess():
    try:
        head = {'flag':True,'answer':[], 'img':'','game_type':'word','question_list':[]}
        desc_lable = ['代号', '战斗经验', '出身地', '生日', '种族', '身高', '职业', '标签', '阻挡数', '配音', '画师', '一技能', '二技能', '三技能']
        
        chara_id_list = list(mrfz_data.CHARA_NAME.keys())
        random.shuffle(chara_id_list)
        
        c = OtherChara(chara_id_list[0])
        head['answer'].append(c.name)
        head['img'] = c.icon.cqcode
        
        chara_desc_list = mrfz_chara_data.CHARA_DATA[chara_id_list[0]]
        index_list = list(range(1,len(chara_desc_list)))
        random.shuffle(index_list)
        for i in range(5):
            desc_index = index_list[i]
            head['question_list'].append(f'提示{i+1}/5:\n她的{desc_lable[desc_index]}是 {chara_desc_list[desc_index]}')
        
        return head
    except Exception as e:
        print('mrfz_word', e)
        
def load_config():
    try:
        config_path = '/home/ubuntu/HoshinoBot/hoshino/modules/total_guess/Genshin_chara.json'
        with open(config_path, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)
    except Exception as e:
        return {}
        
def get_cqcode(name):
    path = '/home/ubuntu/HoshinoBot/hoshino/modules/total_guess/pic/' + name + '.jpg'
    img = Image.open(path)
    image = MessageSegment.image(pic2b64(img))
    return image
    
def genshin_word_guess():
    try:
        head = {'flag':True,'answer':[], 'img':'','game_type':'word','question_list':[]}
            
        chara_list = load_config()
        chara_name_list = list(chara_list.keys())
        random.shuffle(chara_name_list)
        answer = chara_name_list[0]
        
        head['answer'] = [answer]
        head['img'] = get_cqcode(answer)
        
        data_label = list(chara_list[answer].keys())
        data_label.remove('故事')
        for i in range(3):
            random.shuffle(data_label)
            index_list = chara_list[answer][data_label[0]]
            random.shuffle(index_list)
            if data_label[0] == '命之座':
                head['question_list'].append(f'提示{i+1}/3:\n{data_label[0]}有 {index_list[0][0]}')
                del(chara_list[answer][data_label[0]][0])
            else:
                head['question_list'].append(f'提示{i+1}/3:\n{data_label[0]}有 {index_list[0][1]}')
                del(chara_list[answer][data_label[0]][0])
        
        return head
    except Exception as e:
        print('genshin', e)
