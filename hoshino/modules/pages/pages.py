import os
import nonebot
from quart import request,session,redirect,Blueprint,url_for,render_template,jsonify,session
from nonebot.exceptions import CQHttpError
from hoshino import R, Service, priv, config
from pathlib import Path

public_address = '18.179.120.112'#修改为服务器公网ip


sv = Service('pages', manage_priv=priv.SUPERUSER, enable_on_default=True, visible=False)
work_env = Path(os.path.dirname(__file__))
homework_folder = work_env.joinpath('img')
static_folder = work_env.joinpath('static')
ma = Blueprint('ma',__name__,template_folder='templates',static_folder=static_folder)
hp = Blueprint('hp',__name__,template_folder='templates',static_folder=static_folder)
tk = Blueprint('tk',__name__,template_folder='templates',static_folder=static_folder)
ab = Blueprint('ab',__name__,template_folder='templates',static_folder=static_folder)
sc = Blueprint('sc',__name__,template_folder='templates',static_folder=static_folder)
js = Blueprint('js',__name__,template_folder='templates',static_folder=static_folder)
bot = nonebot.get_bot()
app = bot.server_app
sv.logger.info(homework_folder)



@ma.route('/main')
async def index():
    return await render_template('main.html')

@hp.route('/help')
async def index():
    return await render_template('help.html')
    
@tk.route('/thanks')
async def index():
    return await render_template('thanks.html')

@ab.route('/about')
async def index():
    return await render_template('about.html')

@sc.route('/manual')
async def index():
    return await render_template('manual.html')

@js.route('/404')
async def index():
    return await render_template('404.html')

@sv.on_fullmatch("主页",only_to_me=False)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev,f'http://{public_address}:{cfg.PORT}/main')

@sv.on_fullmatch(('帮助','机器人帮助'))
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev,f'http://{public_address}:{cfg.PORT}/help')
    
@sv.on_fullmatch("手册",only_to_me=False)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev,f'http://{public_address}:{cfg.PORT}/manual')
