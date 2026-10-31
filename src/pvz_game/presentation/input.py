import math
from dataclasses import dataclass
from .scenes import BUTTONS, HUD_SUN_RECT
from ..domain.commands import Command
from ..config import LOGICAL_WIDTH, LOGICAL_HEIGHT
from ..domain.plant_rules import placement_reason

PLANT_CARDS=("sunflower","peashooter","wallnut","jalapeno")
DOG_PLANT_CARDS=PLANT_CARDS+("pangbaobao","huanghuang")


def visible_plant_cards(skin_id='default', level=None):
    cards = DOG_PLANT_CARDS if skin_id=='dogs' else PLANT_CARDS
    if level is not None and level.get("available_plants"):
        allowed = set(level["available_plants"])
        cards = tuple(card for card in cards if card in allowed)
    return cards


@dataclass
class DragState:
    plant_type_id: str
    pointer: tuple[float,float]
    tool_kind: str="plant"
    hover_cell: tuple[int,int] | None=None
    preview_valid: bool=False
    reason_code: str | None="out_of_bounds"


def card_at(point,skin_id='default',level=None):
    if point is None:return None
    return next((kind for kind in visible_plant_cards(skin_id,level) if inside(point,BUTTONS[kind])),None)


def cell_at(point,config,rows,cols):
    if point is None:return None
    x,y=point
    col=int((x-config["grid_x"])//config["cell_width"])
    row=int((y-config["grid_y"])//config["cell_height"])
    if 0<=row<rows and 0<=col<cols:return row,col
    return None


def nearest_cell_at(point,config,rows,cols):
    """Return the closest valid cell center; ties resolve by row then column."""
    if point is None:return None
    x,y=point
    left,top=config['grid_x'],config['grid_y']
    width,height=config['cell_width'],config['cell_height']
    if not (left<=x<left+cols*width and top<=y<top+rows*height):return None
    return min(((x-(left+(col+.5)*width))**2+
                (y-(top+(row+.5)*height))**2,row,col)
               for row in range(rows) for col in range(cols))[1:]


def begin_drag(plant_type_id,point):
    return DragState(plant_type_id,point,"shovel" if plant_type_id=="shovel" else "plant")


def update_drag(state,point,snapshot,config,level,plant_types):
    if state is None:return None
    state.pointer=point
    state.hover_cell=nearest_cell_at(point,config,level["rows"],level["cols"])
    if state.hover_cell is None:
        state.preview_valid=False
        state.reason_code="out_of_bounds"
    else:
        row,col=state.hover_cell
        if state.tool_kind=="shovel":
            state.reason_code=None if any(p["row"]==row and p["col"]==col and p["hp"]>0
                                          for p in snapshot["plants"]) else "no_plant"
        else:
            if level.get("available_plants") and state.plant_type_id not in level["available_plants"]:
                state.reason_code="unavailable"
            else:
                state.reason_code=placement_reason(snapshot,plant_types,level["rows"],
                                                   level["cols"],state.plant_type_id,row,col)
        state.preview_valid=state.reason_code is None
    return state


def finish_drag(state,point,phase,config,level,snapshot=None,plant_types=None,skin_id='default'):
    if state is None or phase!="playing" or point is None:return []
    card=card_at(point,skin_id,level)
    if card is not None:return [Command("SelectPlant",(card,))]
    if inside(point,BUTTONS["shovel"]):return [Command("SelectShovel")]
    cell=nearest_cell_at(point,config,level["rows"],level["cols"])
    if cell is None:return []
    row,col=cell
    if snapshot is not None:
        if state.tool_kind=="shovel":
            if not any(p["row"]==row and p["col"]==col and p["hp"]>0 for p in snapshot["plants"]):return []
            return [Command("SelectShovel"),Command("ShovelAt",(row,col),sequence=1)]
        if plant_types is not None:
            if level.get("available_plants") and state.plant_type_id not in level["available_plants"]:
                return []
            reason=placement_reason(snapshot,plant_types,level["rows"],level["cols"],state.plant_type_id,row,col)
            if reason is not None:return []
        elif not state.preview_valid or state.hover_cell!=(row,col):return []
    elif not state.preview_valid or state.hover_cell!=(row,col):
        return []
    if state.tool_kind=="shovel":return [Command("SelectShovel"),Command("ShovelAt",(row,col),sequence=1)]
    return [Command("SelectPlant",(state.plant_type_id,)),
            Command("PlantAt",(row,col),sequence=1)]


def cancel_drag(state):
    return None


def logical_position(position, window_size):
    w,h = window_size
    if w <= 0 or h <= 0:
        return None
    scale = min(w/LOGICAL_WIDTH,h/LOGICAL_HEIGHT)
    x = (position[0]-(w-LOGICAL_WIDTH*scale)/2)/scale
    y = (position[1]-(h-LOGICAL_HEIGHT*scale)/2)/scale
    return (x,y) if 0 <= x < LOGICAL_WIDTH and 0 <= y < LOGICAL_HEIGHT else None


def inside(point, rect):
    x,y = point
    a,b,w,h = rect
    return a <= x < a+w and b <= y < b+h


def click(point, snapshot, config, help_open=False, button=1, skins_open=False,skin_id='default',view='main',level=None):
    if point is None:
        return None
    phase = snapshot["phase"]
    if button == 3:
        return Command("CancelSelection") if phase == "playing" else None
    if button != 1:
        return None
    def hit(key): return inside(point,BUTTONS[key])
    if phase == "menu":
        if view == "levels":
            if hit("back_levels"): return "close_levels"
            for index in range(1, 6):
                if hit(f"level_{index}"): return f"select_stage_{index}"
            if hit("endless"): return "select_endless"
            return None
        if view == "backgrounds":
            if hit("back_backgrounds"): return "close_backgrounds"
            for index in range(1, 4):
                if hit(f"background_{index}"): return f"select_background_{index}"
            return None
        if skins_open:
            if hit('back_skins'): return 'close_skins'
            for role in ('pangbaobao','huanghuang'):
                if hit('role_preview_'+role):return 'preview_role_'+role
            for side in ('plant','zombie'):
                for skin in (('default','dogs','dogs_photo') if side=='plant' else ('default','dogs')):
                    if hit(side+'_'+skin):return 'choose_'+side+'_'+skin
            return None
        if help_open:
            return "close_help" if hit("back_help") else None
        if hit("start"): return Command("Start")
        if hit("help"): return "open_help"
        if hit("skins"): return "open_skins"
        if hit("backgrounds"): return "open_backgrounds"
        if hit("music_toggle"): return "toggle_music"
        if hit("music_volume_down"): return "music_volume_down"
        if hit("music_volume_up"): return "music_volume_up"
        if hit("exit_menu"): return Command("Quit")
        return None
    if phase == "paused":
        if hit("resume"): return Command("Resume")
        if hit("quit_pause"): return Command("Quit")
        return None
    if phase in ("won","lost"):
        if hit("next_level"): return "next_level"
        if hit("restart"): return Command("Restart")
        if hit("menu"): return Command("ReturnToMenu")
        if hit("exit_result"): return Command("Quit")
        return None
    if phase != "playing": return None
    if hit("pause"): return Command("Pause")
    if inside(point,HUD_SUN_RECT): return None
    for kind in visible_plant_cards(skin_id,level):
        if hit(kind):return Command("SelectPlant",(kind,))
    if hit("shovel"): return Command("SelectShovel")
    for s in reversed(snapshot["suns"]):
        if math.dist(point,(s["x"],s["y"])) <= config["sun_radius"]+6:
            return Command("CollectSun",(s["id"],))
    x,y = point
    col = int((x-config["grid_x"])//config["cell_width"])
    row = int((y-config["grid_y"])//config["cell_height"])
    if not (0 <= row < 5 and 0 <= col < 12):
        return None
    kind = "ShovelAt" if snapshot["selection"]["kind"] == "shovel" else "PlantAt"
    return Command(kind,(row,col))
