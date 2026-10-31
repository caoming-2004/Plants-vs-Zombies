"""Classic-frame rendering with independently selected dog appearances."""
import math
import pygame
from .prototype_renderer import Renderer as PrototypeRenderer, INK, CREAM, GOLD, GREEN
from .skin_catalog import Catalog, AppearanceController
from .animation import (Animator, frame_at, blit_frame, fit_visible_frame, anchor_position_for_skin,
                       DOG_SCALE, display_scale_for_role, is_dog_skin)
from .scenes import BUTTONS, HUD_SUN_RECT, HUD_STATUS_RECT, MESSAGES
from .input import visible_plant_cards
from .backgrounds import BackgroundCatalog
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
        self.backgrounds=BackgroundCatalog()
        self.background_id=self.backgrounds.default_id
        self.preview_focus_role=None
        self.wave_announcement=None
        self.level=None
        self.campaign=None
        self.levels={}
        self.progress=None
        self.wave_preview_data=None
        self.result_stars=[]
        self.next_level_id=None
        self.level_select_open=False
        self.shot_trails={}
        self.shot_positions={}
        self.muzzle_effects=[]
        self.impact_effects=[]

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

    def set_background(self, background_id):
        chosen = self.backgrounds.resolve(background_id)
        if chosen:
            self.background_id = chosen

    def draw_grid(self):
        grid = pygame.Surface((864, 380), pygame.SRCALPHA)
        for col in range(1, 12):
            pygame.draw.line(grid, (55, 91, 43, 44), (col * 72, 0), (col * 72, 380), 1)
        for row in range(1, 5):
            pygame.draw.line(grid, (55, 91, 43, 44), (0, row * 76), (864, row * 76), 1)
        pygame.draw.rect(grid, (55, 91, 43, 72), (0, 0, 864, 380), 1)
        self.canvas.blit(grid, (105, 160))

    def background(self):
        surface = self.backgrounds.surface(self.background_id)
        if surface is not None:
            self.background_surface = surface
            self.canvas.blit(surface, (0, 0))
            self.draw_grid()
            return
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
        asset_role='zombie_basic' if role in ('zombie_basic','zombie_fast','zombie_tough') else role
        state='walk' if asset_role=='zombie_basic' else ('plant' if role=='jalapeno' else 'idle')
        frame=frame_at(skin.clip(asset_role,state),tick)
        scale=display_scale_for_role(skin,asset_role,scale)
        flip_x=is_dog_skin(skin) and asset_role=='zombie_basic'
        position=fit_visible_frame(self.canvas,skin,frame,position,scale,flip_x)
        blit_frame(self.canvas,skin,frame,position,scale,flip_x=flip_x)

    def focus_role_preview(self,role):
        if role not in ('pangbaobao','huanghuang'):return False
        self.preview_focus_role=role
        return True

    def _special_role_preview(self,role,rect,tick):
        label={'pangbaobao':'胖宝宝·倭瓜','huanghuang':'黄黄·寒冰射手'}[role]
        skin=self.catalog.skins.get('dogs')
        if skin is None:
            if self.catalog.installed('dogs'):self.catalog.preload_async('dogs')
            self.rounded(rect,(225,217,177),6,GOLD if self.preview_focus_role==role else (143,123,72))
            self.text('素材加载中…',(rect[0]+rect[2]/2,rect[1]+rect[3]/2),11,GREEN,True)
            self.text(label,(rect[0]+rect[2]/2,rect[1]+rect[3]-7),9,INK,True)
            return
        self.rounded(rect,(225,217,177),6,GOLD if self.preview_focus_role==role else (143,123,72))
        frame=frame_at(skin.clip(role,'idle'),tick)
        position=(rect[0]+rect[2]/2,rect[1]+29)
        scale=display_scale_for_role(skin,role,.30)
        position=fit_visible_frame(self.canvas,skin,frame,position,scale)
        blit_frame(self.canvas,skin,frame,position,scale)
        self.text(label,(rect[0]+rect[2]/2,rect[1]+rect[3]-7),9,INK,True)

    def draw_hud(self,snapshot,types,level=None,preview=None):
        s=self.canvas
        cards=visible_plant_cards(self.appearance.plant_skin_id,level)
        self.rounded((15,10,830 if len(cards)>4 else 635,116),(64,78,43),10,(102,105,62))
        for role in cards:
            x,y,w,h=BUTTONS[role]
            skin=self.appearance.skin_for(role)
            self.rounded((x,y,w,h),(238,226,181),7,(143,123,72))
            frame=skin.data['roles'][role]['preview']
            self.rounded((x+4,y+4,w-8,54),(225,217,177),5)
            base=.65 if skin.data['skin_id']=='default' else (.55 if role in ('sunflower','pangbaobao','huanghuang') else .61)
            blit_frame(s,skin,frame,(x+w/2,y+58),display_scale_for_role(skin,role,base))
            self.rounded((x+3,y+59,w-6,18),(238,226,181),4)
            label={'pangbaobao':'胖宝宝·倭瓜','huanghuang':'黄黄·寒冰射手'}.get(role,types[role]['name'])
            self.text(label,(x+w/2,y+68),10,INK,True)
            self.text(str(types[role]['price']),(x+w/2,y+h-8),12,INK,True)
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
        x,y,w,h=HUD_STATUS_RECT
        self.rounded((x,y,w,h),(64,78,43),5,(102,105,62))
        stage=(level.get('name','') if level else '')[:12]
        status=f"{stage}  ·  波次 {snapshot['wave_index']}/{snapshot['wave_count']} · 出怪 {snapshot['next_spawn_index']}/{snapshot['total_spawns']}"
        if preview:
            lead=max(0,round(preview.get('lead_ticks',0)/60))
            status+=f"  ·  下一波 {preview['name']} {preview['total']}只 {lead}s"
        else:
            status+="  ·  最后一波/清场中"
        self.text(status,(x+8,y+3),9,CREAM)
        self.rounded(HUD_SUN_RECT,(64,78,43),10,(102,105,62))
        self.ui('sun',(24,19,42,42))
        self.text(snapshot['sun'],(89,31),21,CREAM,True)
        self.text('阳光',(90,59),12,CREAM,True)
        self.button('pause','暂停')

    def draw(self,snapshot,events=(),mouse=None,help_open=False,message='',message_time=0,skins_open=False,drag_state=None,level=None,campaign=None,levels=None,progress=None,preview=None,result_stars=None,next_level_id=None,level_select_open=False,backgrounds_open=False):
        self.scene_tick+=1
        s=self.canvas;t=snapshot['tick']
        for event in events:
            if event.get('kind')=='wave_started':
                self.wave_announcement=(event['name'],event['wave_index'],event['wave_count'],event['tick'])
            if event.get('kind')=='shot':
                self.muzzle_effects.append(dict(x=event['x'],row=event['row'],born=event['tick']))
                if len(self.muzzle_effects)>64:self.muzzle_effects.pop(0)
        if snapshot['phase'] in ('won','lost'):
            self.result_elapsed+=1
        else:self.result_elapsed=0
        self.animator.consume(snapshot,events)
        if self.shot_session!=snapshot['session_id']:
            self.shot_offsets.clear();self.shot_trails.clear();self.shot_positions.clear()
            self.muzzle_effects.clear();self.impact_effects.clear()
            self.shot_session=snapshot['session_id']
        if level is not None:self.level=level
        if campaign is not None:self.campaign=campaign
        if levels is not None:self.levels=levels
        if progress is not None:self.progress=progress
        self.wave_preview_data=preview
        self.result_stars=result_stars if result_stars is not None else []
        self.next_level_id=next_level_id
        if snapshot['phase']=='menu':
            self.menu(self.scene_tick,help_open,skins_open,level_select_open,backgrounds_open,progress)
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
            if p['type_id']=='pangbaobao' and p['action']=='attacking':
                ready=max(0,p['next_action_tick']-t)
                total=max(1,types[p['type_id']]['attack_duration_ticks'])
                progress=max(0,1-ready/total)
                pygame.draw.rect(s,(60,48,30),(x-20,y-86,40,6),border_radius=3)
                pygame.draw.rect(s,(244,172,60),(x-19,y-85,round(38*progress),4),border_radius=2)
                self.text('蓄势',(x,y-96),9,(255,238,177),True)
            hp=types[p['type_id']]['hp']
            if p['hp']<hp:
                pygame.draw.rect(s,(64,66,37),(x-18,y+2,36,4))
                pygame.draw.rect(s,(208,213,86),(x-18,y+2,36*p['hp']/hp,4))
        for shot in snapshot['projectiles']:
            if shot['id'] not in self.shot_offsets:
                source=next((p for p in snapshot['plants'] if p['id']==shot['source_id']),None)
                if source:
                    role=source['type_id']
                    skin=self.appearance.skin_for(role)
                    emission=frame_at(skin.clip(role,'attack'),0)
                    px=self.config['grid_x']+(source['col']+.5)*self.config['cell_width']
                    mx,my=anchor_position_for_skin(
                        skin,emission,(px,self.row_y(source['row'])+(40 if is_dog_skin(skin) else 28)),
                        scale=display_scale_for_role(skin,role,DOG_SCALE if is_dog_skin(skin) else 1))
                    self.shot_offsets[shot['id']]=(mx-(px+22),my-(self.row_y(source['row'])-15))
                else:self.shot_offsets[shot['id']]=(0,0)
            dx,dy=self.shot_offsets[shot['id']]
            px,py=round(shot['x']+dx),round(self.row_y(shot['row'])-15+dy)
            trail=self.shot_trails.setdefault(shot['id'],[])
            if not trail or trail[-1]!=(px,py):
                trail.append((px,py))
                if len(trail)>3:trail.pop(0)
            trail_color=(150,215,255) if shot.get('slow_factor') is not None else (145,205,100)
            for index,(tx,ty) in enumerate(trail[:-1]):
                radius=2+index
                pygame.draw.circle(s,trail_color,(tx,ty),radius)
            if shot.get('slow_factor') is not None:
                pygame.draw.circle(s,(167,231,255),(px,py),12)
                pygame.draw.circle(s,(91,190,243),(px,py),8)
                pygame.draw.circle(s,(235,252,255),(px-2,py-3),3)
            else:
                self.ui('projectile',(px-8,py-8,16,16))
            self.shot_positions[shot['id']]=(px,py)
        active_shots={p['id'] for p in snapshot['projectiles']}
        for shot_id,position in list(self.shot_positions.items()):
            if shot_id not in active_shots:
                self.impact_effects.append(dict(x=position[0],y=position[1],born=t))
                self.shot_trails.pop(shot_id,None)
                del self.shot_positions[shot_id]
        if len(self.impact_effects)>64:self.impact_effects=self.impact_effects[-64:]
        self.shot_offsets={key:value for key,value in self.shot_offsets.items() if key in active_shots}
        for z in snapshot['zombies']:
            if z.get('slow_until_tick',0)>t:
                glow=pygame.Surface((68,84),pygame.SRCALPHA)
                pygame.draw.ellipse(glow,(95,196,255,58),(4,8,60,70))
                s.blit(glow,(round(z['x']-34),round(self.row_y(z['row'])-42)))
            self.animator.draw_actor(s,z,(z['x'],self.row_y(z['row'])+28),t)
            if z['type_id'] in ('zombie_fast','zombie_tough'):
                badge='快' if z['type_id']=='zombie_fast' else '厚'
                color=(194,106,48) if badge=='快' else (101,111,130)
                badge_rect=(round(z['x']+19),round(self.row_y(z['row'])-50),25,19)
                self.rounded(badge_rect,color,5,(238,220,163))
                self.text(badge,(badge_rect[0]+badge_rect[2]/2,badge_rect[1]+10),11,CREAM,True)
        self.animator.draw_deaths(s,t+self.result_elapsed,self.row_y)
        self.animator.draw_squash_effects(s,t,self.row_y)
        self.animator.draw_row_clear_effects(s,t,self.config['grid_x'],self.row_y,
                                             self.config['cell_width'],
                                             self.config['cell_width']*12)
        for sun in snapshot['suns']:
            self.draw_sun(sun,t)
        self.draw_projectile_effects(s,t)
        self.animator.draw_sun_collect_effects(s,t)
        self.draw_drag_preview(drag_state,snapshot)
        self.draw_hud(snapshot,types,self.level,self.wave_preview_data)
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
        if point is None:return
        from .input import inside
        obscured=inside(point,HUD_SUN_RECT) or any(inside(point,BUTTONS[key])
            for key in (*visible_plant_cards(self.appearance.plant_skin_id,self.level),'shovel','pause'))
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

    def menu(self,t,help_open,skins_open=False,level_select_open=False,backgrounds_open=False,progress=None):
        self.level_select_open=level_select_open
        scene=self.backgrounds.surface(self.background_id)
        if scene is None:
            scene=self.backgrounds.surface(self.backgrounds.default_id)
        if scene is not None:
            self.canvas.blit(scene,(0,0))
        else:
            self.canvas.fill((37,55,39))
            pygame.draw.rect(self.canvas,(48,68,46),(0,360,LOGICAL_WIDTH,240))
        veil=pygame.Surface((LOGICAL_WIDTH,LOGICAL_HEIGHT),pygame.SRCALPHA)
        veil.fill((7,16,12,88))
        self.canvas.blit(veil,(0,0))
        panel=pygame.Surface((400,510),pygame.SRCALPHA)
        pygame.draw.rect(panel,(18,30,25,218),(0,0,400,510),border_radius=20)
        pygame.draw.rect(panel,(192,166,112,225),(0,0,400,510),2,border_radius=20)
        self.canvas.blit(panel,(520,45))
        if help_open:
            super().menu(t,True)
            return
        if level_select_open:
            self.level_menu(t)
            return
        if skins_open:
            self.skin_menu(t)
            return
        if backgrounds_open:
            self.background_menu(t)
            return
        self.text('植物大战僵尸',(695,113),36,(224,221,182),True)
        self.text('经典角色 · 门头沟小狗换肤',(695,164),16,(220,220,186),True)
        self.button('start','开始游戏',True)
        self.button('skins','选择外观')
        self.button('backgrounds','更换背景')
        self.button('help','怎么玩？')
        self.button('music_toggle','音乐：开' if progress is None or progress.music_enabled else '音乐：关')
        self.button('music_volume_down','−')
        self.button('music_volume_up','+')
        volume=0.55 if progress is None else progress.music_volume
        self.rounded((751,418,52,38),(239,228,193),6,(143,123,72))
        self.text(f'{round(volume*100)}%',(777,437),14,INK,True)
        self.button('exit_menu','退出')
        self.preview('sunflower',(289,546),t)
        self.preview('peashooter',(374,547),t)
        self.text('本地离线小游戏 / v0.7.1',(160,572),12,CREAM)
        if self.appearance.notice:self.text(self.appearance.notice,(525,550),13,GOLD,True)

    def draw_sun(self,sun,t):
        x,y=round(sun['x']),round(sun['y'])
        age=max(0,t-sun.get('born_tick',0))
        remaining=max(0,sun.get('expires_tick',t+100)-t)
        alpha=round(255*min(1,age/12,remaining/20))
        if alpha<255:
            image=self.default.ui.get('sun')
            if image is not None:
                base=pygame.transform.smoothscale(image,(48,48)).copy()
                base.set_alpha(alpha)
                self.canvas.blit(base,(x-24,y-24))
            else:
                self.ui('sun',(x-24,y-24,48,48))
        else:
            self.ui('sun',(x-24,y-24,48,48))
        pulse=0.5+0.5*math.sin(t*0.16+sun['id'])
        glow=pygame.Surface((64,64),pygame.SRCALPHA)
        pygame.draw.circle(glow,(255,226,120,round(30+20*pulse)),(32,32),round(25+3*pulse),2)
        self.canvas.blit(glow,(x-32,y-32))

    def draw_projectile_effects(self,s,t):
        remaining=[]
        for effect in self.muzzle_effects:
            age=t-effect['born']
            if 0<=age<6:
                px,py=round(effect['x']),round(self.row_y(effect['row'])-15)
                radius=round(5+age)
                pygame.draw.circle(s,(255,241,160),(px,py),radius,2)
                remaining.append(effect)
        self.muzzle_effects=remaining
        remaining=[]
        for effect in self.impact_effects:
            age=t-effect['born']
            if 0<=age<10:
                radius=round(3+age*1.5)
                pygame.draw.circle(s,(255,235,150),(effect['x'],effect['y']),radius,2)
                pygame.draw.circle(s,(255,255,220),(effect['x'],effect['y']),max(1,radius//2))
                remaining.append(effect)
        self.impact_effects=remaining

    def background_menu(self,t):
        veil=pygame.Surface((LOGICAL_WIDTH,LOGICAL_HEIGHT),pygame.SRCALPHA);veil.fill((22,37,23,185));self.canvas.blit(veil,(0,0))
        self.rounded((140,55,770,490),(239,228,193),18,(112,105,66))
        self.text('更换背景',(525,92),30,INK,True)
        self.text('背景只改变画面，不改变草坪、角色或胜负。',(525,126),14,GREEN,True)
        for index,background_id in enumerate(self.backgrounds.order[:3],start=1):
            rect=BUTTONS[f'background_{index}']
            selected=(background_id==self.background_id)
            self.rounded(rect,(225,217,177),8,GOLD if selected else (143,123,72))
            thumb=self.backgrounds.thumbnail(background_id)
            if thumb is not None:
                thumb=pygame.transform.smoothscale(thumb,(220,100))
                self.canvas.blit(thumb,(rect[0]+10,rect[1]+8))
            item=self.backgrounds.options.get(background_id,{})
            self.text(item.get('name',background_id),(rect[0]+rect[2]/2,rect[1]+122),12,INK,True)
            if selected:
                self.text('✓',(rect[0]+rect[2]-16,rect[1]+12),18,GOLD,True)
        if self.backgrounds.error:
            self.text('背景资源不可用，已使用默认背景',(525,430),12,(144,65,40),True)
        self.button('back_backgrounds','返回主菜单',True)

    def level_menu(self,t):
        veil=pygame.Surface((LOGICAL_WIDTH,LOGICAL_HEIGHT),pygame.SRCALPHA);veil.fill((22,37,23,185));self.canvas.blit(veil,(0,0))
        self.rounded((130,55,790,490),(239,228,193),18,(112,105,66))
        self.text('选择关卡',(525,92),30,INK,True)
        self.text('通关后解锁下一关；星级只记录挑战成果。',(525,126),14,GREEN,True)
        stages=list(self.campaign['stages']) if self.campaign else []
        for index,level_id in enumerate(stages[:5],start=1):
            rect=BUTTONS[f'level_{index}']
            unlocked=bool(self.progress and self.progress.is_unlocked(level_id))
            record=(self.progress.data['levels'].get(level_id,{}) if self.progress else {})
            level=self.levels.get(level_id,{})
            self.rounded(rect,(225,217,177) if unlocked else (189,184,160),10,GOLD if record.get('cleared') else (143,123,72))
            label=level.get('name','第 %d 关'%index).split(' · ')[0]
            self.text(label,(rect[0]+rect[2]/2,rect[1]+22),14,INK,True)
            if unlocked:
                goals=len(level.get('star_goals',[]))
                stars=min(goals,record.get('best_stars',0))
                self.text('★'*stars+'☆'*(goals-stars),(rect[0]+rect[2]/2,rect[1]+58),16,GOLD,True)
                self.text('已通关' if record.get('cleared') else '可挑战',(rect[0]+rect[2]/2,rect[1]+88),11,GREEN,True)
            else:
                self.text('锁定',(rect[0]+rect[2]/2,rect[1]+58),16,(144,65,40),True)
                self.text('先通关前一关',(rect[0]+rect[2]/2,rect[1]+88),10,GREEN,True)
        endless=BUTTONS['endless']
        unlocked=bool(self.progress and self.progress.endless_unlocked)
        self.rounded(endless,(225,217,177) if unlocked else (189,184,160),10,(143,123,72))
        self.text('无尽模式',(endless[0]+endless[2]/2,endless[1]+24),18,INK,True)
        if unlocked:
            best=self.progress.data['endless']['best_wave'] if self.progress else 0
            self.text('最佳 %d 波'%best,(endless[0]+endless[2]/2,endless[1]+50),12,GREEN,True)
        else:
            self.text('通关最后一关解锁',(endless[0]+endless[2]/2,endless[1]+50),12,(144,65,40),True)
        self.button('back_levels','返回主菜单',True)
        if self.appearance.notice:self.text(self.appearance.notice,(525,548),12,(144,65,40),True)

    def overlay(self,snapshot):
        if snapshot['phase']=='paused':
            super().overlay(snapshot)
            return
        s=self.canvas
        veil=pygame.Surface((LOGICAL_WIDTH,LOGICAL_HEIGHT),pygame.SRCALPHA)
        veil.fill((20,37,27,175));s.blit(veil,(0,0))
        won=snapshot['phase']=='won'
        self.rounded((349,150,352,350),(244,238,211),20)
        self.text('草坪守住了！' if won else '防线被突破了',(525,200),32,INK,True)
        if won:
            self.text('本关完成，继续下一关或重玩。',(525,240),14,GREEN,True)
            goals=len(self.level.get('star_goals',[])) if self.level else 0
            stars=min(goals,len(self.result_stars))
            self.text('星级 ' + '★'*stars + '☆'*(goals-stars),(525,274),18,GOLD,True)
        else:
            self.text('调整植物位置和阳光分配，再试一次。',(525,240),14,GREEN,True)
            if self.level and self.level.get('mode')=='endless':
                best=self.progress.data['endless']['best_wave'] if self.progress else 0
                self.text(f"本次 {snapshot['wave_index']} 波 · 击杀 {snapshot['kills']} · 最佳 {best}",(525,268),13,GREEN,True)
        if won and self.next_level_id:
            self.button('next_level','下一关',True)
        self.button('restart','再玩一局',not (won and self.next_level_id))
        self.button('menu','返回主菜单')
        self.button('exit_result','退出')

    def skin_menu(self,t):
        veil=pygame.Surface((LOGICAL_WIDTH,LOGICAL_HEIGHT),pygame.SRCALPHA);veil.fill((22,37,23,170));self.canvas.blit(veil,(0,0))
        self.rounded((183,47,684,510),(239,228,193),18,(112,105,66))
        self.text('选择外观',(525,86),30,INK,True)
        self.text('只改变外观，价格、伤害和冷却保持不变。',(525,125),15,GREEN,True)
        self.text('植物方',(350,168),21,INK,True)
        self.text('进攻方',(700,168),21,INK,True)
        portraits=[('sunflower',(292,226),248),('peashooter',(410,226),248),
                   ('wallnut',(292,279),301),('jalapeno',(410,279),301),
                   ('zombie_basic',(700,300),326)]
        for role,pos,label_y in portraits:
            skin=self.appearance.skin_for(role)
            self.preview(role,pos,t,.56 if skin.pixel_scale==2 else .42)
            name=skin.data['roles'][role]['name'].split(' · ')[0]
            if role=='zombie_basic':name+='（红背心）'
            self.text(name,(pos[0],label_y),13,GREEN,True)
        for role,rect in (('pangbaobao',BUTTONS['role_preview_pangbaobao']),
                          ('huanghuang',BUTTONS['role_preview_huanghuang'])):
            self._special_role_preview(role,rect,t)
        for side,x in [('plant',235),('zombie',585)]:
            selected=getattr(self.appearance,side+'_skin_id')
            selected=self.appearance.pending_for(side) or selected
            choices=(('default','经典外观'),('dogs','狗狗卡通'),('dogs_photo','狗狗照片')) if side=='plant' else (
                ('default','经典外观'),('dogs','狗狗卡通'))
            for skin_id,label in choices:
                key=side+'_'+skin_id
                self.button(key,('✓ ' if selected==skin_id else '')+label,selected==skin_id)
                if skin_id!='default' and not self.catalog.installed(skin_id):
                    self.text('资源未就绪',(x+115,492 if skin_id=='dogs_photo' else 451),11,(144,65,40),True)
        self.text('植物：被窝 / 好孩子 / 小宝 / 小杜  ·  进攻方：嗷嗷嗷',(525,495),12,GREEN,True)
        if self.appearance.notice:self.text(self.appearance.notice,(525,505),12,(144,65,40),True)
        self.button('back_skins','完成，返回主菜单',True)
