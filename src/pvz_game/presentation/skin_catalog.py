"""Validated appearance data; this module never owns gameplay values."""
from pathlib import Path
import json
import threading
import time
import pygame
from ..resources import asset_root

REQUIRED = {
    'sunflower': ('idle','produce','hit','die'),
    'peashooter': ('idle','attack','hit','die'),
    'wallnut': ('idle','hit','die'),
    'jalapeno': ('plant','ignite','hit','die'),
    'zombie_basic': ('walk','bite','hit','die'),
}
REQUIRED_BY_SKIN = {
    'dogs': {
        'pangbaobao': ('idle','attack','hit','die'),
        'huanghuang': ('idle','attack','hit','die'),
    },
}
SKIN_IDS = ('default', 'dogs', 'dogs_photo')
ZOMBIE_ROLE_IDS=frozenset(('zombie_basic','zombie_fast','zombie_tough'))


class AssetError(RuntimeError):
    pass


def safe_path(directory,relative):
    if not isinstance(relative,str):raise AssetError('素材路径必须为文本')
    path=(directory/relative).resolve()
    if not path.is_relative_to(directory.resolve()) or not path.is_file():
        raise AssetError('皮肤素材缺失：'+Path(relative).name)
    return path


class Skin:
    def __init__(self,path,sources):
        self.directory=Path(path).parent
        self.manifest_path=Path(path)
        self.cache={}
        try:
            self.data=json.loads(Path(path).read_text(encoding='utf-8-sig'))
            if self.data['schema_version']!=1:raise AssetError('不支持的皮肤版本')
            self.pixel_scale=self.data.get('pixel_scale',1)
            if type(self.pixel_scale) is not int or self.pixel_scale not in (1,2):
                raise AssetError('素材pixel_scale必须为1或2')
            if not all(isinstance(self.data[k],str) and self.data[k] for k in ('skin_id','display_name')):
                raise AssetError('皮肤名称或标识为空')
            if not self.data['source_refs'] or any(ref not in sources for ref in self.data['source_refs']):
                raise AssetError('皮肤来源记录缺失')
            self.atlas=pygame.image.load(str(safe_path(self.directory,self.data['atlas'])))
            self.file_signatures=self._file_signatures()
            required_roles=dict(REQUIRED)
            required_roles.update(REQUIRED_BY_SKIN.get(self.data['skin_id'],{}))
            for role,states in required_roles.items():
                info=self.data['roles'][role]
                for field in ('card','preview'):self.validate_frame(info[field])
                for state in states:
                    clip=info['clips'][state]
                    if type(clip['loop']) is not bool or not clip['frames']:
                        raise AssetError('动作必须有帧和循环设置')
                    for frame in clip['frames']:self.validate_frame(frame)
            self.ui={}
            ui_atlas=pygame.image.load(str(safe_path(self.directory,self.data['ui_atlas']))) if 'ui_atlas' in self.data else None
            for name,relative in self.data.get('ui',{}).items():
                if isinstance(relative,dict):
                    rect=pygame.Rect(*relative['rect'])
                    if ui_atlas is None or rect.w<=0 or rect.h<=0 or not ui_atlas.get_rect().contains(rect):
                        raise AssetError('界面图集矩形超出边界')
                    self.ui[name]=ui_atlas.subsurface(rect).copy()
                else:self.ui[name]=pygame.image.load(str(safe_path(self.directory,relative)))
        except AssetError:
            raise
        except (KeyError,TypeError,ValueError,OSError,pygame.error,IndexError) as exc:
            raise AssetError('皮肤清单或图集无效：'+Path(path).parent.name) from exc

    def _file_signatures(self):
        return tuple((path.stat().st_size,path.stat().st_mtime_ns) for path in
                     (self.manifest_path,self.directory/self.data['atlas']))

    def changed_on_disk(self):
        try:return self._file_signatures()!=self.file_signatures
        except OSError:return True

    def validate_frame(self,frame):
        rect=frame['rect']
        if len(rect)!=4 or any(type(v) is not int for v in rect):raise AssetError('帧矩形必须为整数')
        x,y,w,h=rect
        if x<0 or y<0 or w<=0 or h<=0 or x+w>self.atlas.get_width() or y+h>self.atlas.get_height():
            raise AssetError('帧矩形超出图集')
        size,offset=frame['source_size'],frame['trim_offset']
        if len(size)!=2 or len(offset)!=2 or any(type(v) is not int for v in size+offset):
            raise AssetError('画布与裁切偏移必须为整数')
        if min(size)<=0 or min(offset)<0 or offset[0]+w>size[0] or offset[1]+h>size[1]:
            raise AssetError('裁切偏移超出原始画布')
        for key in ('anchor','muzzle','contact'):
            a=frame[key]
            if len(a)!=2 or any(type(v) not in (int,float) for v in a) or not (0<=a[0]<=size[0] and 0<=a[1]<=size[1]):
                raise AssetError('动作锚点超出画布')
        if type(frame['duration_ticks']) is not int or frame['duration_ticks']<1:
            raise AssetError('帧时长必须为正整数tick')

    def clip(self,role,state):
        return self.data['roles'][role]['clips'][state]

    def surface(self,frame):
        key=tuple(frame['rect'])
        if key not in self.cache:
            surface=self.atlas.subsurface(pygame.Rect(*key)).copy()
            if pygame.display.get_init() and pygame.display.get_surface() is not None:
                surface=surface.convert_alpha()
            self.cache[key]=surface
        return self.cache[key]


class Catalog:
    def __init__(self,root=None):
        self.root=Path(root) if root else asset_root()
        try:
            self.sources=json.loads((self.root/'sources.json').read_text(encoding='utf-8-sig'))
        except (OSError,ValueError) as exc:
            raise AssetError('缺少素材来源清单，请完整解压。') from exc
        self.skins={}
        self.signature_checked_at={}
        self._loading=set()
        self._load_errors={}
        self._load_lock=threading.Lock()
        self._installed_cache={}
        try:self.load('default',refresh=True)
        except AssetError as exc:raise AssetError('默认外观不可用，请完整解压资源。'+str(exc)) from exc

    def load(self,skin_id,refresh=False):
        if skin_id not in SKIN_IDS:raise AssetError('未知皮肤')
        now=time.monotonic()
        first_load=skin_id not in self.skins
        should_check=now-self.signature_checked_at.get(skin_id,0)>=1.0
        if refresh or first_load or (should_check and self.skins[skin_id].changed_on_disk()):
            self.skins[skin_id]=Skin(self.root/'skins'/skin_id/'manifest.json',self.sources)
        if refresh or first_load or should_check:
            self.signature_checked_at[skin_id]=now
        return self.skins[skin_id]

    def available(self,skin_id):
        try:
            self.load(skin_id)
            return True
        except AssetError:
            return False

    def installed(self,skin_id):
        """Check menu-ready asset files without decoding the large atlas."""
        if skin_id not in SKIN_IDS:
            return False
        if skin_id in self._installed_cache:return self._installed_cache[skin_id]
        directory=self.root/'skins'/skin_id
        manifest=directory/'manifest.json'
        if not manifest.is_file():
            self._installed_cache[skin_id]=False
            return False
        try:
            data=json.loads(manifest.read_text(encoding='utf-8-sig'))
            safe_path(directory,data['atlas'])
            for relative in data.get('ui',{}).values():
                if isinstance(relative,str):safe_path(directory,relative)
            self._installed_cache[skin_id]=True
            return True
        except (AssetError,KeyError,TypeError,ValueError,OSError):
            self._installed_cache[skin_id]=False
            return False

    def is_loaded(self,skin_id):
        return skin_id in self.skins

    def is_loading(self,skin_id):
        with self._load_lock:return skin_id in self._loading

    def preload_async(self,skin_id):
        """Decode and validate an optional skin off the UI event/render path."""
        if skin_id not in SKIN_IDS or self.is_loaded(skin_id):
            return
        with self._load_lock:
            if skin_id in self._loading:return
            self._loading.add(skin_id)
            self._load_errors.pop(skin_id,None)
        def load_skin():
            try:
                self.load(skin_id,refresh=True)
            except Exception as exc:
                with self._load_lock:self._load_errors[skin_id]=exc
            finally:
                with self._load_lock:self._loading.discard(skin_id)
        threading.Thread(target=load_skin,name='skin-'+skin_id,daemon=True).start()

    def load_error(self,skin_id):
        with self._load_lock:return self._load_errors.get(skin_id)


class AppearanceController:
    def __init__(self,catalog):
        self.catalog=catalog
        self.plant_skin_id=self.zombie_skin_id='default'
        self.notice=''
        self.pending_selection=None

    def selection(self):return self.plant_skin_id,self.zombie_skin_id

    def select(self,side,skin_id,phase):
        if phase!='menu' or side not in ('plant','zombie'):return False
        if skin_id not in (SKIN_IDS if side=='plant' else ('default','dogs')):
            self.notice='该阵营不支持此外观。'
            return False
        if not self.catalog.available(skin_id):
            self.notice='小狗外观未完整安装，请保留全部资源文件。'
            return False
        setattr(self,side+'_skin_id',skin_id)
        self.notice=''
        self.pending_selection=None
        return True

    def select_async(self,side,skin_id,phase):
        """Acknowledge a skin choice immediately and apply it after background load."""
        if phase!='menu' or side not in ('plant','zombie'):
            return False
        choices=SKIN_IDS if side=='plant' else ('default','dogs')
        if skin_id not in choices:
            self.notice='该阵营不支持此外观。'
            return False
        if not self.catalog.installed(skin_id):
            self.notice='小狗外观未完整安装，请保留全部资源文件。'
            return False
        if self.catalog.is_loaded(skin_id):
            setattr(self,side+'_skin_id',skin_id)
            self.pending_selection=None
            self.notice=''
            return True
        self.pending_selection=(side,skin_id)
        self.notice='外观正在加载，请稍候…'
        self.catalog.preload_async(skin_id)
        return True

    def pending_for(self,side):
        return self.pending_selection[1] if self.pending_selection and self.pending_selection[0]==side else None

    def poll_pending(self):
        if self.pending_selection is None:return False
        side,skin_id=self.pending_selection
        if self.catalog.is_loading(skin_id):return False
        if self.catalog.is_loaded(skin_id):
            setattr(self,side+'_skin_id',skin_id)
            self.pending_selection=None
            self.notice=''
            return True
        if self.catalog.load_error(skin_id) is not None:
            self.pending_selection=None
            self.notice='小狗资源缺失或损坏，请保留完整资源文件。'
        return False

    def validate_selection(self,force=True):
        self.catalog.load('default')
        for side in ('plant','zombie'):
            selected=getattr(self,side+'_skin_id')
            if selected!='default':
                try:self.catalog.load(selected,refresh=force)
                except AssetError:
                    setattr(self,side+'_skin_id','default')
                    self.notice='小狗资源缺失或损坏，已将对应阵营恢复为默认外观。'

    def on_restart(self):
        self.poll_pending()
        self.validate_selection(force=False)

    def skin_for(self,role):
        selected=self.zombie_skin_id if role in ZOMBIE_ROLE_IDS else self.plant_skin_id
        return self.catalog.load(selected)
