"""Check rendered dog frames for role scale and neighboring-cell overlap."""
from itertools import combinations_with_replacement, product
import pygame
from .animation import DOG_SCALE, display_scale_for_role
from .skin_catalog import REQUIRED


def _frames(skin,role):
    for state in sorted(skin.data['roles'][role]['clips']):
        for index,frame in enumerate(skin.clip(role,state)['frames']):
            yield state,index,frame


def _runtime_mask(skin,frame,scale):
    """Build a tight visible mask and its offset using blit_frame's anchor math."""
    image=skin.surface(frame)
    bounds=image.get_bounding_rect(min_alpha=1)
    if bounds.w==0 or bounds.h==0:
        return pygame.mask.Mask((1,1)),(0,0),0
    visible=image.subsurface(bounds).copy()
    logical_scale=scale/skin.pixel_scale
    size=(max(1,round(visible.get_width()*logical_scale)),
          max(1,round(visible.get_height()*logical_scale)))
    if visible.get_size()!=size:
        visible=pygame.transform.smoothscale(visible,size)
    offset=frame['trim_offset'];anchor=frame['anchor']
    origin=(round((offset[0]+bounds.x-anchor[0])*logical_scale),
            round((offset[1]+bounds.y-anchor[1])*logical_scale))
    return pygame.mask.from_surface(visible,1),origin,visible.get_height()


def validate_dog_non_overlap(dog_skin,default_skin,cell_width=72,scale=None):
    """Return diagnostics for undersized or overlapping dog actors.

    Every atlas frame is placed at its actor anchor exactly as the renderer does.
    Pairwise tests cover all roles, animation states and frames.
    """
    if cell_width<=0 or (scale is not None and scale<=0):raise ValueError('cell_width and scale must be positive')
    frames_by_role={};diagnostics=[]
    for role in REQUIRED:
        reference=max(default_skin.surface(frame).get_bounding_rect(min_alpha=1).height
                      for _,_,frame in _frames(default_skin,role))/default_skin.pixel_scale
        frames=[];max_height=0;max_frame=('none',-1)
        role_scale=scale if scale is not None else display_scale_for_role(dog_skin,role,DOG_SCALE)
        for state,index,frame in _frames(dog_skin,role):
            mask,origin,height=_runtime_mask(dog_skin,frame,role_scale)
            if height>max_height:max_height=height;max_frame=(state,index)
            frames.append((state,index,mask,origin))
        if max_height<reference*.75:
            diagnostics.append(f'height_below_75_percent role={role} state={max_frame[0]} frame={max_frame[1]} rendered={max_height:g} minimum={reference*.75:g}')
        frames_by_role[role]=frames
    roles=tuple(REQUIRED)
    for left_index,left_role in enumerate(roles):
        for right_role in roles[left_index:]:
            left_states=sorted({frame[0] for frame in frames_by_role[left_role]})
            right_states=sorted({frame[0] for frame in frames_by_role[right_role]})
            for left_state in left_states:
                for right_state in right_states:
                    if left_role==right_role and right_state<left_state:continue
                    left_frames=[f for f in frames_by_role[left_role] if f[0]==left_state]
                    right_frames=[f for f in frames_by_role[right_role] if f[0]==right_state]
                    pairs=(combinations_with_replacement(left_frames,2)
                           if left_role==right_role and left_state==right_state
                           else product(left_frames,right_frames))
                    for left,right in pairs:
                        ls,li,lmask,lo=left;rs,ri,rmask,ro=right
                        offset=(cell_width+ro[0]-lo[0],ro[1]-lo[1])
                        overlap=lmask.overlap(rmask,offset)
                        if overlap is not None:
                            diagnostics.append(f'overlap left={left_role}.{ls}[{li}] right={right_role}.{rs}[{ri}] pixel={overlap}')
                            break
    return diagnostics
