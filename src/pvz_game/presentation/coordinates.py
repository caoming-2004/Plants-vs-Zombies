"""Aspect-preserving mapping between logical game space and window pixels."""

LOGICAL_SIZE=(1050,600)


def viewport(window_size,logical_size=LOGICAL_SIZE):
    width,height=window_size
    logical_width,logical_height=logical_size
    if min(width,height,logical_width,logical_height)<=0:
        raise ValueError("窗口和逻辑画布尺寸必须为正数")
    scale=min(width/logical_width,height/logical_height)
    draw_width,draw_height=logical_width*scale,logical_height*scale
    return ((width-draw_width)/2,(height-draw_height)/2,scale)


def to_logical(position,window_size,logical_size=LOGICAL_SIZE):
    x,y=position
    offset_x,offset_y,scale=viewport(window_size,logical_size)
    logical_x=(x-offset_x)/scale
    logical_y=(y-offset_y)/scale
    if not (0<=logical_x<logical_size[0] and 0<=logical_y<logical_size[1]):
        return None
    return logical_x,logical_y


def to_window(position,window_size,logical_size=LOGICAL_SIZE):
    x,y=position
    offset_x,offset_y,scale=viewport(window_size,logical_size)
    return offset_x+x*scale,offset_y+y*scale
