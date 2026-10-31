"""Measure rendered dog body overlap and minimum visible actor size."""
from itertools import combinations_with_replacement, product
import pygame

from .animation import DOG_SCALE, display_scale_for_role
from .skin_catalog import REQUIRED, REQUIRED_BY_SKIN

BODY_ALPHA_THRESHOLD = 96
MAX_OVERLAP_RATIO = 0.35


def _roles(skin):
    roles=dict(REQUIRED)
    roles.update(REQUIRED_BY_SKIN.get(skin.data.get('skin_id'),{}))
    return roles


def _frames(skin, role):
    for state in sorted(_roles(skin)[role]):
        for index, frame in enumerate(skin.clip(role, state)["frames"]):
            yield state, index, frame


def _runtime_mask(skin, frame, scale):
    """Build an anchored body mask, dropping disconnected effects and shadows."""
    image = skin.surface(frame)
    visible = image.subsurface(
        image.get_bounding_rect(min_alpha=BODY_ALPHA_THRESHOLD)
    ).copy()
    source_mask = pygame.mask.from_surface(visible, BODY_ALPHA_THRESHOLD)
    components = source_mask.connected_components()
    if not components:
        return pygame.mask.Mask((1, 1)), (0, 0), 0
    body = max(components, key=lambda component: component.count())
    clean = body.to_surface(
        setcolor=(255, 255, 255, 255),
        unsetcolor=(0, 0, 0, 0),
    )
    logical_scale = scale / skin.pixel_scale
    size = (max(1, round(clean.get_width() * logical_scale)),
            max(1, round(clean.get_height() * logical_scale)))
    if clean.get_size() != size:
        clean = pygame.transform.smoothscale(clean, size)
    mask = pygame.mask.from_surface(clean, BODY_ALPHA_THRESHOLD)
    offset = frame["trim_offset"]
    anchor = frame["anchor"]
    origin = (round((offset[0] + image.get_bounding_rect(
        min_alpha=BODY_ALPHA_THRESHOLD
    ).x - anchor[0]) * logical_scale),
              round((offset[1] + image.get_bounding_rect(
                  min_alpha=BODY_ALPHA_THRESHOLD
              ).y - anchor[1]) * logical_scale))
    return mask, origin, mask.get_size()[1]


def measure_dog_overlap(dog_skin, cell_width=72, cell_height=76, scale=None):
    """Return the worst horizontal/vertical neighboring body overlap ratio."""
    if cell_width <= 0 or cell_height <= 0 or (scale is not None and scale <= 0):
        raise ValueError("cell dimensions and scale must be positive")

    actors = {}
    roles=_roles(dog_skin)
    for role in roles:
        role_scale = scale if scale is not None else display_scale_for_role(
            dog_skin, role, DOG_SCALE
        )
        actors[role] = [
            (state, index, *_runtime_mask(dog_skin, frame, role_scale))
            for state, index, frame in _frames(dog_skin, role)
        ]

    worst_ratio = 0.0
    worst_pair = None
    roles = tuple(actors)
    for left_index, left_role in enumerate(roles):
        for right_role in roles[left_index:]:
            left_frames = actors[left_role]
            right_frames = actors[right_role]
            pairs = (combinations_with_replacement(left_frames, 2)
                     if left_role == right_role else product(left_frames, right_frames))
            for left, right in pairs:
                left_state, left_frame, left_mask, left_origin, _ = left
                right_state, right_frame, right_mask, right_origin, _ = right
                denominator = min(left_mask.count(), right_mask.count())
                if denominator == 0:
                    continue
                for offset in (
                    (cell_width + right_origin[0] - left_origin[0],
                     right_origin[1] - left_origin[1]),
                    (right_origin[0] - left_origin[0],
                     cell_height + right_origin[1] - left_origin[1]),
                ):
                    overlap = left_mask.overlap_area(right_mask, offset)
                    ratio = overlap / denominator
                    if ratio > worst_ratio:
                        worst_ratio = ratio
                        worst_pair = (left_role, left_state, left_frame,
                                      right_role, right_state, right_frame,
                                      offset, overlap, denominator)

    return dict(max_overlap_ratio=worst_ratio, worst_pair=worst_pair,
                alpha_threshold=BODY_ALPHA_THRESHOLD,
                excluded_effects="disconnected components")


def validate_dog_non_overlap(dog_skin, default_skin, cell_width=72,
                             cell_height=76, scale=None):
    """Report oversized overlaps and roles rendered below the visibility floor."""
    diagnostics = []
    for role in _roles(dog_skin):
        role_scale = scale if scale is not None else display_scale_for_role(
            dog_skin, role, DOG_SCALE
        )
        heights = [
            (_runtime_mask(dog_skin, frame, role_scale)[2], state, index)
            for state, index, frame in _frames(dog_skin, role)
        ]
        rendered_height, state, index = max(heights, default=(0, "none", -1))
        if rendered_height < 48:
            diagnostics.append(
                f"height_below_visibility_floor role={role} state={state}[{index}] "
                f"rendered={rendered_height:g} minimum=48"
            )

    report = measure_dog_overlap(dog_skin, cell_width, cell_height, scale)
    if report["max_overlap_ratio"] > MAX_OVERLAP_RATIO:
        pair = report["worst_pair"]
        left_role, left_state, left_frame, right_role, right_state, right_frame, offset, overlap, denominator = pair
        diagnostics.append(
            f"overlap left={left_role}.{left_state}[{left_frame}] "
            f"right={right_role}.{right_state}[{right_frame}] "
            f"ratio={report['max_overlap_ratio']:.3f} pixels={overlap}/{denominator} "
            f"offset={offset}"
        )
    return diagnostics


def dog_visual_bounds(skin, role, frame, position, scale):
    """Return the rendered non-transparent body bounds in logical pixels."""
    image=skin.surface(frame)
    visible=image.get_bounding_rect(min_alpha=1)
    factor=scale/skin.pixel_scale
    offset,anchor=frame['trim_offset'],frame['anchor']
    left=position[0]+(offset[0]+visible.x-anchor[0])*factor
    top=position[1]+(offset[1]+visible.y-anchor[1])*factor
    return (left,top,left+visible.w*factor,top+visible.h*factor)


def validate_dog_canvas_bounds(skin, canvas=(1050,600)):
    """Ensure every required dog pose can be placed fully inside the window."""
    from .animation import fit_visible_frame
    roles=_roles(skin)
    failures=[]
    for role,states in roles.items():
        scale=display_scale_for_role(skin,role,DOG_SCALE)
        for state in states:
            for index,frame in enumerate(skin.clip(role,state)['frames']):
                for position in ((0,0),(canvas[0],canvas[1])):
                    fitted=fit_visible_frame(_BoundsTarget(canvas),skin,frame,position,scale)
                    left,top,right,bottom=dog_visual_bounds(skin,role,frame,fitted,scale)
                    if left < -1 or top < -1 or right > canvas[0]+1 or bottom > canvas[1]+1:
                        failures.append(f"{role}.{state}[{index}] bounds={(left,top,right,bottom)}")
                        break
                if failures and failures[-1].startswith(role+'.'+state+'['):
                    break
            if failures and failures[-1].startswith(role+'.'+state+'['):
                break
    return failures


class _BoundsTarget:
    def __init__(self,size):self.size=size
    def get_size(self):return self.size
