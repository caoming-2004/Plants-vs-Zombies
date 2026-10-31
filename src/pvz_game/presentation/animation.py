"""Atlas sampling and stable anchors, with no gameplay callbacks."""
from bisect import bisect_right
from functools import lru_cache
import math
import pygame

DOG_SCALE=0.68
POSE_RATE_MIN_HZ=12
POSE_RATE_MAX_HZ=18
JALAPENO_IGNITE_DURATION_TICKS=120
ZOMBIE_ROLE_IDS=frozenset(('zombie_basic','zombie_fast','zombie_tough'))


def pose_rate_hz(unique_pose_count,duration_ticks,tick_hz):
    """Return the distinct-pose rate using the simulation's configured clock."""
    if unique_pose_count<1 or duration_ticks<1 or tick_hz<1:
        raise ValueError('姿势数、动作tick和模拟频率必须为正数')
    return unique_pose_count*tick_hz/duration_ticks


def assign_clip_durations(frames,pose_signatures,tick_hz,loop,target_rate=15):
    """Distribute integer simulation ticks so every distinct-pose clip meets cadence bounds."""
    if not frames or len(frames)!=len(pose_signatures):
        raise ValueError('动作帧与姿势签名数量必须相同且非空')
    unique_count=len(set(pose_signatures))
    minimum=max(math.ceil(unique_count*tick_hz/POSE_RATE_MAX_HZ),len(frames),60 if loop else 1)
    maximum=math.floor(unique_count*tick_hz/POSE_RATE_MIN_HZ)
    if minimum>maximum:
        raise ValueError(f'{unique_count}个不同姿势无法同时满足姿势速率与循环时长要求')
    total_ticks=min(max(round(unique_count*tick_hz/target_rate),minimum),maximum)
    each,remainder=divmod(total_ticks,len(frames))
    for index,frame in enumerate(frames):
        frame['duration_ticks']=each+(index<remainder)
    return pose_rate_hz(unique_count,total_ticks,tick_hz)


def display_scale_for_role(skin,role,base_scale=None):
    """Apply a role's manifest multiplier to a context-specific base scale."""
    if base_scale is None:base_scale=1.0
    if isinstance(base_scale,bool) or not isinstance(base_scale,(int,float)) or not math.isfinite(base_scale) or base_scale<=0:
        raise ValueError('base_scale must be a positive finite number')
    if skin.data.get('skin_id') not in ('dogs','dogs_photo'):
        return base_scale
    multiplier=skin.data['roles'][role].get('display_scale_multiplier',1.0)
    if isinstance(multiplier,bool) or not isinstance(multiplier,(int,float)) or not math.isfinite(multiplier) or multiplier<=0:
        raise ValueError(f'{role} display_scale_multiplier must be a positive finite number')
    return base_scale*multiplier


def is_dog_skin(skin):
    return skin.data.get('skin_id') in ('dogs','dogs_photo')


def dog_secondary_motion(tick,entity_id,state):
    """Small deterministic bob/sway so dog poses read continuously at 60 Hz."""
    phase=(entity_id%17)*1.7
    if state=='walk':
        speed,amp=0.24,3.0
    elif state in ('attack','bite'):
        speed,amp=0.20,2.0
    else:
        speed,amp=0.16,2.0
    dx=math.sin(tick*speed*0.55+phase)*1.2
    dy=math.sin(tick*speed+phase)*amp
    if state=='hit':
        dx+=math.sin(tick*0.9+phase)*1.5
        dy+=math.cos(tick*0.8+phase)*1.0
    return dx,dy

@lru_cache(maxsize=1024)
def _scaled(image,size):
    return pygame.transform.smoothscale(image,size)


@lru_cache(maxsize=1024)
def _flipped(image):
    return pygame.transform.flip(image,True,False)


@lru_cache(maxsize=4096)
def _visible_alpha_bounds(skin,rect):
    visible=skin.atlas.subsurface(pygame.Rect(*rect)).get_bounding_rect(min_alpha=1)
    return visible.x,visible.y,visible.w,visible.h


def clip_duration(clip):
    timing = clip.get("_frame_timing")
    if timing is None:
        ends=[]
        duration=0
        for frame in clip['frames']:
            duration+=frame['duration_ticks']
            ends.append(duration)
        timing=(duration,tuple(ends))
        clip['_frame_timing']=timing
    return timing[0]


def frame_at(clip,elapsed,cycle_ticks=None):
    frames=clip['frames']
    duration,ends=clip.get('_frame_timing',(None,None))
    if duration is None:
        duration=clip_duration(clip)
        ends=clip['_frame_timing'][1]
    if cycle_ticks:
        elapsed=(max(elapsed,0)%cycle_ticks)*duration/cycle_ticks
    elif clip['loop']:
        elapsed=max(elapsed,0)%duration
    else:
        elapsed=min(max(elapsed,0),duration-1)
    return frames[bisect_right(ends,elapsed)]


def blit_frame(target,skin,frame,position,scale=1,alpha=255,hit=False,flip_x=False):
    scale=scale/skin.pixel_scale
    image=skin.surface(frame)
    if flip_x:image=_flipped(image)
    if scale!=1:
        image=_scaled(image,(max(1,round(image.get_width()*scale)),max(1,round(image.get_height()*scale))))
    if alpha!=255 or hit:
        image=image.copy()
        if hit:image.fill((70,70,70,0),special_flags=pygame.BLEND_RGBA_ADD)
        image.set_alpha(alpha)
    offset=frame['trim_offset'];anchor=frame['anchor']
    offset_x=frame['source_size'][0]-offset[0]-frame['rect'][2] if flip_x else offset[0]
    anchor_x=frame['source_size'][0]-anchor[0] if flip_x else anchor[0]
    target.blit(image,(round(position[0]+(offset_x-anchor_x)*scale),
                       round(position[1]+(offset[1]-anchor[1])*scale)))


def fit_visible_frame(target,skin,frame,position,scale=1,flip_x=False):
    """Shift an actor anchor just enough to keep every visible pixel on canvas."""
    bx,by,bw,bh=_visible_alpha_bounds(skin,tuple(frame['rect']))
    if flip_x:bx=frame['rect'][2]-bx-bw
    logical_scale=scale/skin.pixel_scale
    offset=frame['trim_offset'];anchor=frame['anchor']
    offset_x=frame['source_size'][0]-offset[0]-frame['rect'][2] if flip_x else offset[0]
    anchor_x=frame['source_size'][0]-anchor[0] if flip_x else anchor[0]
    left=position[0]+(offset_x+bx-anchor_x)*logical_scale
    top=position[1]+(offset[1]+by-anchor[1])*logical_scale
    right=left+bw*logical_scale
    bottom=top+bh*logical_scale
    width,height=target.get_size()
    dx=max(0,-left)+min(0,width-right)
    dy=max(0,-top)+min(0,height-bottom)
    return position[0]+dx,position[1]+dy


def anchor_position(frame,position,key='muzzle',scale=1):
    # Kept for callers without a Skin object; use anchor_position_for_skin for
    # high-density source frames so authored coordinates map to logical units.
    a=frame['anchor'];point=frame[key]
    return position[0]+(point[0]-a[0])*scale,position[1]+(point[1]-a[1])*scale


def anchor_position_for_skin(skin,frame,position,key='muzzle',scale=1):
    return anchor_position(frame,position,key,scale/skin.pixel_scale)


class Animator:
    def __init__(self,appearance):
        self.appearance=appearance
        self.session_id=None
        self.deaths=[]
        self.actions={}
        self.hits={}
        self.state_since={}
        self.row_clears=[]
        self.squash_hits=[]
        self.sun_collects=[]
        self.sun_positions={}

    def consume(self,snapshot,events):
        if self.session_id is None:
            self.session_id=snapshot['session_id']
        elif self.session_id!=snapshot['session_id']:
            self.session_id=snapshot['session_id']
            self.deaths.clear();self.actions.clear();self.hits.clear();self.state_since.clear();self.row_clears.clear();self.squash_hits.clear();self.sun_collects.clear();self.sun_positions.clear()
        for event in events:
            kind=event['kind']
            if kind=='hit':
                current=self.hits.get(event['id'])
                if current is None or event['tick']>current:self.hits[event['id']]=event['tick']
            if kind in ('shot','bite','action_started'):
                action='attack' if kind=='shot' else 'bite' if kind=='bite' else event.get('action','produce')
                self.actions[event['id']]=(action,event['tick'])
            if kind=='died':
                self.hits.pop(event['id'],None)
                self.deaths.append(dict(event))
            if kind=='row_clear_started':
                self.row_clears.append(dict(event))
            if kind=='squash_hit':
                self.squash_hits.append(dict(event))
            if kind=='collected':
                position=self.sun_positions.get(event['id'])
                if position is not None:
                    self.sun_collects.append(dict(event,x=position[0],y=position[1]))
        self.sun_positions={sun['id']:(sun['x'],sun['y']) for sun in snapshot['suns']}

    def draw_actor(self,target,entity,position,tick):
        role=entity['type_id'];asset_role='zombie_basic' if role in ZOMBIE_ROLE_IDS else role
        skin=self.appearance.skin_for(role)
        if is_dog_skin(skin) and role in ('peashooter','wallnut','jalapeno','pangbaobao','huanghuang'):
            position=(position[0],position[1]+12)
        state='walk' if asset_role=='zombie_basic' else (
            'attack' if role=='pangbaobao' and entity.get('action')=='attacking' else
            'plant' if role=='jalapeno' else 'idle')
        if asset_role=='zombie_basic' and entity['action']=='biting':state='bite'
        old=self.state_since.get(entity['id'])
        if old is None or old[0]!=state:
            old=(state,tick);self.state_since[entity['id']]=old
        elapsed=tick-old[1]
        cycle=None
        if state=='bite':cycle=60
        action=self.actions.get(entity['id'])
        if action:
            action_name,start=action
            duration=clip_duration(skin.clip(asset_role,action_name))
            if 0<=tick-start<duration and not (asset_role=='zombie_basic' and entity['action']!='biting'):
                state=action_name;elapsed=tick-start
        hit_start=self.hits.get(entity['id'])
        if hit_start is not None:
            hit_clip=skin.clip(asset_role,'hit')
            hit_elapsed=tick-hit_start
            hit_duration=clip_duration(hit_clip)
            if 0<=hit_elapsed<hit_duration:
                state='hit';elapsed=hit_elapsed;cycle=None
            elif hit_elapsed>=hit_duration:
                self.hits.pop(entity['id'],None)
        frame=frame_at(skin.clip(asset_role,state),elapsed,cycle)
        scale=display_scale_for_role(skin,asset_role,DOG_SCALE if is_dog_skin(skin) else 1)
        flip_x=is_dog_skin(skin) and asset_role=='zombie_basic'
        if is_dog_skin(skin):
            dx,dy=dog_secondary_motion(tick,entity['id'],state)
            position=(position[0]+dx,position[1]+dy)
        position=fit_visible_frame(target,skin,frame,position,scale,flip_x)
        blit_frame(target,skin,frame,position,scale,flip_x=flip_x)
        return frame

    def draw_deaths(self,target,tick,row_y):
        remaining=[]
        for death in self.deaths:
            role=death['type_id'];asset_role='zombie_basic' if role in ZOMBIE_ROLE_IDS else role
            skin=self.appearance.skin_for(role)
            clip=skin.clip(asset_role,'die')
            age=tick-death['tick']
            duration=clip_duration(clip)
            if age<duration:
                offset=12 if is_dog_skin(skin) and role in ('peashooter','wallnut','jalapeno','pangbaobao','huanghuang') else 0
                scale=display_scale_for_role(skin,asset_role,DOG_SCALE if is_dog_skin(skin) else 1)
                frame=frame_at(clip,age)
                flip_x=is_dog_skin(skin) and asset_role=='zombie_basic'
                position=fit_visible_frame(target,skin,frame,(death['x'],row_y(death['row'])+28+offset),scale,flip_x)
                blit_frame(target,skin,frame,position,scale,flip_x=flip_x)
                remaining.append(death)
        self.deaths=remaining

    def draw_row_clear_effects(self,target,tick,grid_x,row_y,cell_width=72,board_width=864):
        remaining=[]
        for effect in self.row_clears:
            age=tick-effect['tick'];role='jalapeno'
            skin=self.appearance.skin_for(role)
            clip=skin.clip(role,'ignite')
            duration=clip_duration(clip)
            if age>=duration:continue
            x=grid_x+(effect['col']+.5)*cell_width
            y=row_y(effect['row'])+(40 if is_dog_skin(skin) else 28)
            blit_frame(target,skin,frame_at(clip,age),(x,y),
                       display_scale_for_role(skin,role,DOG_SCALE if is_dog_skin(skin) else 1))
            alpha=max(0,round(210*(1-age/duration)))
            band=pygame.Surface((board_width,40),pygame.SRCALPHA)
            band.fill((245,82,24,alpha//2))
            target.blit(band,(grid_x,row_y(effect['row'])+4))
            for index in range(0,board_width,28):
                height=14+(index*7+age*5)%22
                color=(255, min(224,125+age%80), 28, alpha)
                pygame.draw.polygon(target,color,[(grid_x+index,row_y(effect['row'])+9),
                    (grid_x+index+8,row_y(effect['row'])+9-height),
                    (grid_x+index+16,row_y(effect['row'])+9)])
            remaining.append(effect)
        self.row_clears=remaining

    def draw_squash_effects(self,target,tick,row_y):
        remaining=[]
        for effect in self.squash_hits:
            age=tick-effect['tick']
            if age<0 or age>=18:continue
            progress=age/18
            radius=round(10+28*progress)
            alpha=max(0,round(220*(1-progress)))
            width=radius*2+6
            height=max(12,round(20*(1-progress)))
            burst=pygame.Surface((width,height),pygame.SRCALPHA)
            pygame.draw.ellipse(burst,(255,205,80,alpha),(2,2,width-4,height-4),3)
            target.blit(burst,(round(effect['x']-width/2),round(row_y(effect['row'])+29-height/2)))
            remaining.append(effect)
        self.squash_hits=remaining

    def draw_sun_collect_effects(self,target,tick):
        remaining=[]
        for effect in self.sun_collects:
            age=tick-effect['tick']
            if age<0 or age>=18:continue
            progress=age/18
            radius=round(5+15*progress)
            alpha=round(210*(1-progress))
            diameter=radius*2+4
            flash=pygame.Surface((diameter,diameter),pygame.SRCALPHA)
            pygame.draw.circle(flash,(255,235,116,alpha),(diameter//2,diameter//2),radius,2)
            target.blit(flash,(round(effect['x']-diameter/2),round(effect['y']-diameter/2)))
            remaining.append(effect)
        self.sun_collects=remaining
