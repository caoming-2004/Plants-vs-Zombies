"""Atlas sampling and stable anchors, with no gameplay callbacks."""
from functools import lru_cache
import math
import pygame

DOG_SCALE=0.68
POSE_RATE_MIN_HZ=12
POSE_RATE_MAX_HZ=18
JALAPENO_IGNITE_DURATION_TICKS=120


def pose_rate_hz(unique_pose_count,duration_ticks,tick_hz):
    """Return the distinct-pose rate using the simulation's configured clock."""
    if unique_pose_count<1 or duration_ticks<1 or tick_hz<1:
        raise ValueError('姿势数、动作tick和模拟频率必须为正数')
    return unique_pose_count*tick_hz/duration_ticks


def assign_clip_durations(frames,pose_signatures,tick_hz,loop):
    """Distribute integer simulation ticks so every distinct-pose clip meets cadence bounds."""
    if not frames or len(frames)!=len(pose_signatures):
        raise ValueError('动作帧与姿势签名数量必须相同且非空')
    unique_count=len(set(pose_signatures))
    minimum=max(math.ceil(unique_count*tick_hz/POSE_RATE_MAX_HZ),len(frames),60 if loop else 1)
    maximum=math.floor(unique_count*tick_hz/POSE_RATE_MIN_HZ)
    if minimum>maximum:
        raise ValueError(f'{unique_count}个不同姿势无法同时满足姿势速率与循环时长要求')
    target_rate=(POSE_RATE_MIN_HZ+POSE_RATE_MAX_HZ)/2
    total_ticks=min(max(round(unique_count*tick_hz/target_rate),minimum),maximum)
    each,remainder=divmod(total_ticks,len(frames))
    for index,frame in enumerate(frames):
        frame['duration_ticks']=each+(index<remainder)
    return pose_rate_hz(unique_count,total_ticks,tick_hz)


def display_scale_for_role(skin,role,base_scale=None):
    """Apply a role's manifest multiplier to a context-specific base scale."""
    if base_scale is None:base_scale=1.0
    if skin.data.get('skin_id')!='dogs':
        return base_scale
    multiplier=skin.data['roles'][role].get('display_scale_multiplier',1.0)
    if isinstance(multiplier,bool) or not isinstance(multiplier,(int,float)) or not math.isfinite(multiplier) or multiplier<=0:
        raise ValueError(f'{role} display_scale_multiplier must be a positive finite number')
    return base_scale*multiplier

@lru_cache(maxsize=256)
def _scaled(image,size):
    return pygame.transform.smoothscale(image,size)


def frame_at(clip,elapsed,cycle_ticks=None):
    frames=clip['frames']
    duration=sum(f['duration_ticks'] for f in frames)
    if cycle_ticks:
        elapsed=(max(elapsed,0)%cycle_ticks)*duration/cycle_ticks
    elif clip['loop']:
        elapsed=max(elapsed,0)%duration
    else:
        elapsed=min(max(elapsed,0),duration-1)
    cursor=0
    for frame in frames:
        cursor+=frame['duration_ticks']
        if elapsed<cursor:return frame
    return frames[-1]


def blit_frame(target,skin,frame,position,scale=1,alpha=255,hit=False):
    scale=scale/skin.pixel_scale
    image=skin.surface(frame)
    if scale!=1:
        image=_scaled(image,(max(1,round(image.get_width()*scale)),max(1,round(image.get_height()*scale))))
    if alpha!=255 or hit:
        image=image.copy()
        if hit:image.fill((70,70,70,0),special_flags=pygame.BLEND_RGBA_ADD)
        image.set_alpha(alpha)
    offset=frame['trim_offset'];anchor=frame['anchor']
    target.blit(image,(round(position[0]+(offset[0]-anchor[0])*scale),
                       round(position[1]+(offset[1]-anchor[1])*scale)))


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

    def consume(self,snapshot,events):
        if self.session_id!=snapshot['session_id']:
            self.session_id=snapshot['session_id']
            self.deaths.clear();self.actions.clear();self.hits.clear();self.state_since.clear();self.row_clears.clear()
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

    def draw_actor(self,target,entity,position,tick):
        role=entity['type_id'];skin=self.appearance.skin_for(role)
        state='walk' if role=='zombie_basic' else ('plant' if role=='jalapeno' else 'idle')
        if role=='zombie_basic' and entity['action']=='biting':state='bite'
        old=self.state_since.get(entity['id'])
        if old is None or old[0]!=state:
            old=(state,tick);self.state_since[entity['id']]=old
        elapsed=tick-old[1]
        cycle=None
        if state=='bite':cycle=60
        action=self.actions.get(entity['id'])
        if action:
            action_name,start=action
            duration=sum(f['duration_ticks'] for f in skin.clip(role,action_name)['frames'])
            if 0<=tick-start<duration and not (role=='zombie_basic' and entity['action']!='biting'):
                state=action_name;elapsed=tick-start
        hit_start=self.hits.get(entity['id'])
        if hit_start is not None:
            hit_clip=skin.clip(role,'hit')
            hit_elapsed=tick-hit_start
            hit_duration=sum(frame['duration_ticks'] for frame in hit_clip['frames'])
            if 0<=hit_elapsed<hit_duration:
                state='hit';elapsed=hit_elapsed;cycle=None
            elif hit_elapsed>=hit_duration:
                self.hits.pop(entity['id'],None)
        frame=frame_at(skin.clip(role,state),elapsed,cycle)
        blit_frame(target,skin,frame,position,
                   display_scale_for_role(skin,role,DOG_SCALE if skin.data['skin_id']=='dogs' else 1))
        return frame

    def draw_deaths(self,target,tick,row_y):
        remaining=[]
        for death in self.deaths:
            role=death['type_id'];skin=self.appearance.skin_for(role)
            clip=skin.clip(role,'die')
            age=tick-death['tick']
            duration=sum(f['duration_ticks'] for f in clip['frames'])
            if age<duration:
                blit_frame(target,skin,frame_at(clip,age),(death['x'],row_y(death['row'])+28),
                           display_scale_for_role(skin,role,DOG_SCALE if skin.data['skin_id']=='dogs' else 1))
                remaining.append(death)
        self.deaths=remaining

    def draw_row_clear_effects(self,target,tick,grid_x,row_y,cell_width=72,board_width=864):
        remaining=[]
        for effect in self.row_clears:
            age=tick-effect['tick'];role='jalapeno'
            skin=self.appearance.skin_for(role)
            clip=skin.clip(role,'ignite')
            duration=sum(frame['duration_ticks'] for frame in clip['frames'])
            if age>=duration:continue
            x=grid_x+(effect['col']+.5)*cell_width;y=row_y(effect['row'])+28
            blit_frame(target,skin,frame_at(clip,age),(x,y),
                       display_scale_for_role(skin,role,DOG_SCALE if skin.data['skin_id']=='dogs' else 1))
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
