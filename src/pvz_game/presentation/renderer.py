"""Classic-frame rendering with independently selected dog appearances."""
import pygame
from .prototype_renderer import Renderer as PrototypeRenderer, INK, CREAM, GOLD, GREEN
from .skin_catalog import Catalog, AppearanceController
from .animation import (Animator, frame_at, blit_frame, anchor_position_for_skin,
                       DOG_SCALE, display_scale_for_role, is_dog_skin)
from .scenes import BUTTONS, HUD_SUN_RECT, MESSAGES
from ..config import LOGICAL_WIDTH, LOGICAL_HEIGHT


class Renderer(PrototypeRenderer):
    def __init__(self,config,appearance=None):
        super().__init__(config)
        self.catalog=appearance.catalog if appearance else Catalog()
        self.appearance=appearance or AppearanceController(self.catalog)
        self.animator=Animator(self.appearance)
        self.default=self.catalog.load('default')
        self.scene_tick=0
        self.scaled={}
        self.result_elapsed=0
        self.shot_offsets={}
        self.shot_session=None
        self.background_surface=None

    def ui(self,name,rect,key=None):
        image=self.default.ui.get(name)
        if image is None:return
        cache_key=(name,rect[2],rect[3])
        if cache_key not in self.scaled:
            source=image.copy()
            if name in ('mower','sun','seedbank'):
                source.set_colorkey((0,0,0) if name=='mower' else (255,255,255))
            converted=pygame.Surface(source.get_size(),pygame.SRCALPHA)
            converted.blit(source,(0,0))
            self.scaled[cache_key]=pygame.transform.smoothscale(converted,(rect[2],rect[3]))
        self.canvas.blit(self.scaled[cache_key],rect[:2])

    def button(self,key,label,primary=False):
        x,y,w,h=BUTTONS[key]
        self.rounded((x,y+3,w,h),(47,40,27),8)
        self.rounded((x,y,w,h),(187,159,103) if primary else (219,206,166),8,(91,79,54))
        self.text(label,(x+w/2,y+h/2-1),18,(49,57,35),True)

    def background(self):
        if self.background_surface is None:
            background=pygame.Surface((LOGICAL_WIDTH,LOGICAL_HEIGHT))
            background.fill((57,87,39))
            image=self.default.ui['background']
            source_scale=image.get_width()/1400
            parts=[(0,0,250,600),(250,0,735,600),(985,0,415,600)]
            destinations=[(0,0,105,600),(105,0,864,600),(969,0,81,600)]
            for source,dest in zip(parts,destinations):
                source_rect=pygame.Rect(*(round(value*source_scale) for value in source))
                column=image.subsurface(source_rect)
                if source[0]==250:
                    for sr,dr in [((0,0,735,90),(105,0,864,160)),((0,90,735,480),(105,160,864,380)),((0,570,735,30),(105,540,864,60))]:
                        crop=pygame.Rect(*(round(value*source_scale) for value in sr))
                        background.blit(pygame.transform.smoothscale(column.subsurface(crop),(dr[2],dr[3])),dr[:2])
                else:background.blit(pygame.transform.smoothscale(column,(dest[2],dest[3])),dest[:2])
            grid=pygame.Surface((864,380),pygame.SRCALPHA)
            for col in range(1,12):
                pygame.draw.line(grid,(55,91,43,44),(col*72,0),(col*72,380),1)
            for row in range(1,5):
                pygame.draw.line(grid,(55,91,43,44),(0,row*76),(864,row*76),1)
            pygame.draw.rect(grid,(55,91,43,72),(0,0,864,380),1)
            background.blit(grid,(105,160))
            self.background_surface=background
        self.canvas.blit(self.background_surface,(0,0))

    def preview(self,role,position,tick,scale=.8):
        skin=self.appearance.skin_for(role)
        state='walk' if role=='zombie_basic' else ('plant' if role=='jalapeno' else 'idle')
        frame=frame_at(skin.clip(role,state),tick)
        blit_frame(self.canvas,skin,frame,position,display_scale_for_role(skin,role,scale))

    def draw_hud(self,snapshot,types):
        s=self.canvas
        self.rounded((15,10,635,116),(64,78,43),10,(102,105,62))
        for role in ('sunflower','peashooter','wallnut','jalapeno'):
            x,y,w,h=BUTTONS[role]
            skin=self.appearance.skin_for(role)
            self.rounded((x,y,w,h),(238,226,181),7,(143,123,72))
            frame=skin.data['roles'][role]['preview']
            self.rounded((x+4,y+4,w-8,62),(225,217,177),5)
            base=.65 if skin.data['skin_id']=='default' else .61
            blit_frame(s,skin,frame,(x+w/2,y+62),display_scale_for_role(skin,role,base))
            self.rounded((x+3,y+h-24,w-6,21),(238,226,181),4)
            self.text(str(types[role]['price']),(x+w/2,y+h-14),14,INK,True)
            self.text(types[role]['name'],(x+w/2,y+h+13),11,CREAM,True)
            if snapshot['selection']['type_id']==role:
                pygame.draw.rect(s,GOLD,(x-2,y-2,w+4,h+4),3,border_radius=5)
            remaining=max(0,snapshot['ready_tick'][role]-snapshot['tick'])
            if remaining:
                cover=pygame.Surface((w,h),pygame.SRCALPHA);cover.fill((28,41,25,140));s.blit(cover,(x,y))
                self.text(f'{remaining/60:.1f}s',(x+w/2,y+42),16,CREAM,True)
            elif snapshot['sun']<types[role]['price']:
                self.text('阳光不足',(x+w/2,y+43),11,(139,47,31),True)
        x,y,w,h=BUTTONS['shovel']
        self.rounded((x,y,w,h),(118,111,73),8,GOLD if snapshot['selection']['kind']=='shovel' else None)
        self.ui('shovelbank',(x,y,w,h))
        self.ui('shovel',(x+6,y+1,w-12,h-18))
        if snapshot['selection']['kind']=='shovel':pygame.draw.rect(s,GOLD,(x,y,w,h),2,border_radius=6)
        self.text('铲子',(x+w/2,y+68),13,CREAM,True)
        self.rounded((650,120,130,31),(64,78,43),7,(102,105,62))
        self.text(f"出怪 {snapshot['next_spawn_index']}/{snapshot['total_spawns']}",(715,127),10,CREAM,True)
        self.text(f"消灭 {snapshot['kills']}",(715,141),10,CREAM,True)
        self.rounded(HUD_SUN_RECT,(64,78,43),10,(102,105,62))
        self.ui('sun',(24,19,42,42))
        self.text(snapshot['sun'],(89,31),21,CREAM,True)
        self.text('阳光',(90,59),12,CREAM,True)
        self.button('pause','暂停')

    def draw(self,snapshot,events=(),mouse=None,help_open=False,message='',message_time=0,skins_open=False,drag_state=None):
        self.scene_tick+=1
        s=self.canvas;t=snapshot['tick']
        if snapshot['phase'] in ('won','lost'):
            self.result_elapsed+=1
        else:self.result_elapsed=0
        self.animator.consume(snapshot,events)
        if self.shot_session!=snapshot['session_id']:
            self.shot_offsets.clear();self.shot_session=snapshot['session_id']
        if snapshot['phase']=='menu':
            self.menu(self.scene_tick,help_open,skins_open)
            return s
        self.background()
        types={p['id']:p for p in self.config['plant_types']}
        for m in snapshot['mowers']:
            if m['state']!='spent':self.ui('mower',(round(m['x']-30),round(self.row_y(m['row'])-6),55,44))
        if mouse and snapshot['phase']=='playing' and snapshot['selection']['kind']!='none':
            col=int((mouse[0]-self.config['grid_x'])//self.config['cell_width'])
            row=int((mouse[1]-self.config['grid_y'])//self.config['cell_height'])
            if 0<=row<5 and 0<=col<12:
                rect=(self.config['grid_x']+col*self.config['cell_width'],self.config['grid_y']+row*self.config['cell_height'],self.config['cell_width'],self.config['cell_height'])
                pygame.draw.rect(s,(250,236,160),rect,2)
        for p in snapshot['plants']:
            x=self.config['grid_x']+(p['col']+.5)*self.config['cell_width']
            y=self.row_y(p['row'])+28
            self.animator.draw_actor(s,p,(x,y),t)
            hp=types[p['type_id']]['hp']
            if p['hp']<hp:
                pygame.draw.rect(s,(64,66,37),(x-18,y+2,36,4))
                pygame.draw.rect(s,(208,213,86),(x-18,y+2,36*p['hp']/hp,4))
        for shot in snapshot['projectiles']:
            if shot['id'] not in self.shot_offsets:
                source=next((p for p in snapshot['plants'] if p['id']==shot['source_id']),None)
                if source:
                    skin=self.appearance.skin_for('peashooter')
                    emission=frame_at(skin.clip('peashooter','attack'),0)
                    px=self.config['grid_x']+(source['col']+.5)*self.config['cell_width']
                    mx,my=anchor_position_for_skin(
                        skin,emission,(px,self.row_y(source['row'])+28),
                        scale=display_scale_for_role(skin,'peashooter',DOG_SCALE if is_dog_skin(skin) else 1))
                    self.shot_offsets[shot['id']]=(mx-(px+22),my-(self.row_y(source['row'])-15))
                else:self.shot_offsets[shot['id']]=(0,0)
            dx,dy=self.shot_offsets[shot['id']]
            self.ui('projectile',(round(shot['x']+dx-8),round(self.row_y(shot['row'])-15+dy-8),16,16))
        active_shots={p['id'] for p in snapshot['projectiles']}
        self.shot_offsets={key:value for key,value in self.shot_offsets.items() if key in active_shots}
        for z in snapshot['zombies']:
            self.animator.draw_actor(s,z,(z['x'],self.row_y(z['row'])+28),t)
        self.animator.draw_deaths(s,t+self.result_elapsed,self.row_y)
        self.animator.draw_row_clear_effects(s,t,self.config['grid_x'],self.row_y,
                                             self.config['cell_width'],
                                             self.config['cell_width']*12)
        for sun in snapshot['suns']:
            self.ui('sun',(round(sun['x']-24),round(sun['y']-24),48,48))
        self.draw_drag_preview(drag_state,snapshot)
        self.draw_hud(snapshot,types)
        self.rounded((105,544,648,28),(230,221,175),6)
        hint='点击阳光收集 → 点击或拖动植物卡种植  |  右键取消  |  空格暂停'
        if snapshot['selection']['kind']=='shovel':hint='铲子已选中：点击植物移除，不退阳光；右键取消。'
        elif snapshot['selection']['kind']=='plant':hint='植物已选中：点击空格种植，失败不会扣费。'
        self.text(hint,(120,550),13,INK)
        names=self.appearance.selection()
        labels={'default':'经典','dogs':'狗狗卡通','dogs_photo':'狗狗照片'}
        self.text('植物：'+labels[names[0]]+'  /  进攻方：'+labels[names[1]],(114,579),12,CREAM)
        if message and message_time>0:
            self.rounded((178,130,494,28),(249,231,163),6)
            self.text(message,(425,143),14,(104,58,34),True)
        if snapshot['phase'] in ('paused','won','lost'):self.overlay(snapshot)
        return s

    def draw_drag_preview(self,drag_state,snapshot):
        if drag_state is None or snapshot['phase']!='playing':return
        point=drag_state.pointer
        if drag_state.hover_cell is not None:
            row,col=drag_state.hover_cell
            rect=(self.config['grid_x']+col*self.config['cell_width'],
                  self.config['grid_y']+row*self.config['cell_height'],
                  self.config['cell_width'],self.config['cell_height'])
            veil=pygame.Surface((rect[2],rect[3]),pygame.SRCALPHA)
            veil.fill((82,196,92,80) if drag_state.preview_valid else (219,60,42,82))
            self.canvas.blit(veil,rect[:2])
            pygame.draw.rect(self.canvas,(106,229,118) if drag_state.preview_valid else (255,109,86),rect,2)
            point=(rect[0]+rect[2]/2,self.config['grid_y']+(row+.5)*self.config['cell_height'])
        if point is None:return
        from .input import inside
        obscured=inside(point,HUD_SUN_RECT) or any(inside(point,BUTTONS[key])
            for key in ('sunflower','peashooter','wallnut','jalapeno','shovel','pause'))
        if not obscured:
            if drag_state.tool_kind=='shovel':
                image=self.default.ui.get('shovel')
                if image is not None:
                    ghost=image.copy();ghost.set_alpha(190)
                    self.canvas.blit(ghost,(round(point[0]-24),round(point[1]-22)))
            else:
                role=drag_state.plant_type_id
                skin=self.appearance.skin_for(role)
                frame=skin.data['roles'][role]['preview']
                y=point[1] if drag_state.hover_cell is None else point[1]+28
                base=DOG_SCALE if is_dog_skin(skin) else .85
                blit_frame(self.canvas,skin,frame,(point[0],y),
                           display_scale_for_role(skin,role,base),alpha=145)
        if drag_state.reason_code and drag_state.reason_code!='out_of_bounds' and not obscured:
            self.rounded((point[0]+14,point[1]-24,190,26),(249,231,163),5)
            self.text(MESSAGES.get(drag_state.reason_code,drag_state.reason_code),
                      (point[0]+109,point[1]-11),11,(104,58,34),True)

    def menu(self,t,help_open,skins_open=False):
        self.canvas.fill((57,87,39))
        self.ui('menu',((LOGICAL_WIDTH-800)//2,0,800,600))
        if help_open:
            super().menu(t,True)
            return
        if skins_open:
            self.skin_menu(t)
            return
        self.text('植物大战僵尸',(695,113),36,(224,221,182),True)
        self.text('经典角色 · 门头沟小狗换肤',(695,164),16,(220,220,186),True)
        self.button('start','开始游戏',True)
        self.button('skins','选择外观')
        self.button('help','怎么玩？')
        self.button('exit_menu','退出')
        self.preview('sunflower',(289,546),t)
        self.preview('peashooter',(374,547),t)
        self.text('本地离线小游戏 / v0.2.0',(160,572),12,CREAM)
        if self.appearance.notice:self.text(self.appearance.notice,(525,550),13,GOLD,True)

    def skin_menu(self,t):
        veil=pygame.Surface((LOGICAL_WIDTH,LOGICAL_HEIGHT),pygame.SRCALPHA);veil.fill((22,37,23,170));self.canvas.blit(veil,(0,0))
        self.rounded((183,47,684,510),(239,228,193),18,(112,105,66))
        self.text('选择外观',(525,86),30,INK,True)
        self.text('只改变外观，价格、伤害和冷却保持不变。',(525,125),15,GREEN,True)
        self.text('植物方',(350,168),21,INK,True)
        self.text('进攻方',(700,168),21,INK,True)
        portraits=[('sunflower',(292,248),264),('peashooter',(410,248),264),
                   ('wallnut',(292,350),358),('jalapeno',(410,350),358),
                   ('zombie_basic',(700,300),326)]
        for role,pos,label_y in portraits:
            skin=self.appearance.skin_for(role)
            self.preview(role,pos,t,.56 if skin.pixel_scale==2 else .42)
            name=skin.data['roles'][role]['name'].split(' · ')[0]
            if role=='zombie_basic':name+='（红背心）'
            self.text(name,(pos[0],label_y),13,GREEN,True)
        for side,x in [('plant',235),('zombie',585)]:
            selected=getattr(self.appearance,side+'_skin_id')
            choices=(('default','经典外观'),('dogs','狗狗卡通'),('dogs_photo','狗狗照片')) if side=='plant' else (
                ('default','经典外观'),('dogs','狗狗卡通'))
            for skin_id,label in choices:
                key=side+'_'+skin_id
                self.button(key,('✓ ' if selected==skin_id else '')+label,selected==skin_id)
                if skin_id!='default' and not self.catalog.available(skin_id):
                    self.text('资源未就绪',(x+115,492 if skin_id=='dogs_photo' else 451),11,(144,65,40),True)
        self.text('植物：被窝 / 好孩子 / 小宝 / 小杜  ·  进攻方：嗷嗷嗷',(525,495),12,GREEN,True)
        if self.appearance.notice:self.text(self.appearance.notice,(525,505),12,(144,65,40),True)
        self.button('back_skins','完成，返回主菜单',True)
