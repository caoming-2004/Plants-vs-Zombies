"""Original code-drawn prototype art. No third-party character images."""
from functools import lru_cache
import math
import pygame
from .scenes import BUTTONS, HELP_LINES
from ..resources import resource
from ..config import LOGICAL_WIDTH, LOGICAL_HEIGHT

INK = (39,57,39)
CREAM = (248,242,217)
GOLD = (255,205,71)
GREEN = (66,107,58)

@lru_cache(maxsize=512)
def _rendered_text(font,text,color):
    return font.render(text,True,color)


class Renderer:
    def __init__(self, config):
        self.config = config
        self.canvas = pygame.Surface((LOGICAL_WIDTH,LOGICAL_HEIGHT))
        self.fonts = {}
        self.font_path = str(resource("fonts/NotoSansSC.ttf"))
        self.effects = []
        self.flash = {}
        self.last_session = None

    def text(self, text, pos, size=18, color=INK, center=False):
        if size not in self.fonts:
            self.fonts[size] = pygame.font.Font(self.font_path,size)
            self.fonts[size].set_bold(True)
        rendered = _rendered_text(self.fonts[size],str(text),tuple(color))
        rect = rendered.get_rect(center=pos) if center else rendered.get_rect(topleft=pos)
        self.canvas.blit(rendered,rect)

    def rounded(self, rect, color, radius=12, border=None):
        pygame.draw.rect(self.canvas,color,rect,border_radius=radius)
        if border:
            pygame.draw.rect(self.canvas,border,rect,2,border_radius=radius)

    def button(self,key,label,primary=False):
        x,y,w,h = BUTTONS[key]
        self.rounded((x,y+4,w,h),(26,43,29),12)
        self.rounded((x,y,w,h),GOLD if primary else CREAM,12)
        self.text(label,(x+w/2,y+h/2-1),20,INK,True)

    def sunflower(self,x,y,t,scale=1,hit=False):
        s = self.canvas
        def pt(a,b): return (round(x+a*scale),round(y+b*scale))
        sway = math.sin(t/24)*2
        pygame.draw.line(s,(38,107,47),pt(0,20),pt(sway,-12),max(2,int(6*scale)))
        pygame.draw.ellipse(s,(57,145,64),(x-23*scale,y+6*scale,23*scale,11*scale))
        pygame.draw.ellipse(s,(74,165,68),(x+1*scale,y+1*scale,23*scale,12*scale))
        for i in range(10):
            angle=i*math.tau/10+t/350
            cx=x+sway*scale+math.cos(angle)*20*scale
            cy=y-20*scale+math.sin(angle)*20*scale
            pygame.draw.circle(s,(255,215,85) if hit else (250,184,45),(round(cx),round(cy)),max(2,int(10*scale)))
        pygame.draw.circle(s,(130,78,38),pt(sway,-20),int(18*scale))
        pygame.draw.circle(s,(177,117,54),pt(sway,-22),int(15*scale))
        for eye in (-6,6):
            pygame.draw.circle(s,(30,43,27),pt(sway+eye,-25),max(1,int(2*scale)))
        pygame.draw.arc(s,INK,(x+(sway-7)*scale,y-24*scale,14*scale,12*scale),math.pi,math.tau,max(1,int(2*scale)))

    def peashooter(self,x,y,t,scale=1,hit=False,attack=False):
        s=self.canvas
        sway=math.sin(t/25)*1.5
        recoil = -3*max(0,1-(t%90)/12) if attack else 0
        def pt(a,b): return (round(x+a*scale),round(y+b*scale))
        pygame.draw.line(s,(39,108,54),pt(0,21),pt(0,-13),max(2,int(6*scale)))
        for a in (-20,0):
            pygame.draw.ellipse(s,(52,144,67),(x+a*scale,y+9*scale,23*scale,12*scale))
        color=(179,233,126) if hit else (104,184,72)
        pygame.draw.circle(s,color,pt(recoil,sway-20),int(21*scale))
        pygame.draw.ellipse(s,color,(x+(9+recoil)*scale,y+(sway-29)*scale,29*scale,20*scale))
        pygame.draw.ellipse(s,(35,91,43),(x+(29+recoil)*scale,y+(sway-27)*scale,9*scale,16*scale))
        pygame.draw.circle(s,(27,50,28),pt(recoil-3,sway-27),max(1,int(3*scale)))
        pygame.draw.circle(s,(242,251,222),pt(recoil-4,sway-28),max(1,int(scale)))
        pygame.draw.ellipse(s,(47,126,56),(x-23*scale,y-29*scale,13*scale,10*scale))

    def zombie(self,x,y,t,state,hit=False):
        s=self.canvas
        step = math.sin(t/12)*7 if state=="walking" else math.sin(t/6)*2
        skin=(198,222,168) if hit else (147,170,125)
        pygame.draw.line(s,(54,60,67),(int(x-6),int(y+9)),(int(x-12+step),int(y+30)),8)
        pygame.draw.line(s,(54,60,67),(int(x+7),int(y+9)),(int(x+12-step),int(y+30)),8)
        pygame.draw.ellipse(s,(35,43,46),(x-22+step,y+26,19,8))
        pygame.draw.ellipse(s,(35,43,46),(x+2-step,y+26,19,8))
        pygame.draw.polygon(s,(120,76,56),[(x-16,y-18),(x+13,y-15),(x+17,y+12),(x-13,y+13)])
        pygame.draw.polygon(s,(226,218,178),[(x-5,y-18),(x+5,y-18),(x+3,y+10)])
        pygame.draw.line(s,(169,64,50),(int(x),int(y-12)),(int(x-4),int(y+8)),4)
        reach=4 if state=="biting" else 0
        pygame.draw.line(s,(120,76,56),(int(x-10),int(y-11)),(int(x-31-reach),int(y-7)),7)
        pygame.draw.circle(s,skin,(int(x-32-reach),int(y-7)),5)
        pygame.draw.ellipse(s,skin,(x-20,y-53,34,37))
        pygame.draw.circle(s,(243,242,216),(int(x-14),int(y-40)),6)
        pygame.draw.circle(s,(243,242,216),(int(x+1),int(y-41)),6)
        for ex in (-15,0): pygame.draw.circle(s,INK,(int(x+ex-1),int(y-40)),2)
        pygame.draw.line(s,(64,72,48),(int(x-18),int(y-25)),(int(x+3),int(y-26)),3)
        pygame.draw.rect(s,(244,235,198),(x-13,y-26,4,5))
        pygame.draw.line(s,(53,65,47),(int(x-1),int(y-54)),(int(x+3),int(y-60)),2)

    def sun(self,x,y,t,r=18):
        s=self.canvas
        for i in range(10):
            a=i*math.tau/10+t/160
            inner=(x+math.cos(a)*(r+2),y+math.sin(a)*(r+2))
            outer=(x+math.cos(a)*(r+8),y+math.sin(a)*(r+8))
            pygame.draw.line(s,(255,211,81),inner,outer,3)
        pygame.draw.circle(s,(234,154,38),(int(x),int(y)),r)
        pygame.draw.circle(s,(255,216,82),(int(x),int(y-1)),r-3)
        pygame.draw.circle(s,(255,236,152),(int(x-4),int(y-5)),max(2,r//3))

    def mower(self,x,y,state):
        s=self.canvas
        pygame.draw.line(s,(58,67,61),(int(x-4),int(y-6)),(int(x-16),int(y-29)),3)
        pygame.draw.line(s,(58,67,61),(int(x-16),int(y-29)),(int(x-28),int(y-29)),4)
        pygame.draw.rect(s,(188,71,48),(x-23,y-7,44,22),border_radius=6)
        pygame.draw.rect(s,(222,109,65),(x-8,y-15,19,13),border_radius=3)
        for a in (-14,14):
            pygame.draw.circle(s,(40,47,40),(int(x+a),int(y+15)),8)
            pygame.draw.circle(s,(170,166,136),(int(x+a),int(y+15)),3)
        if state=="sweeping":
            pygame.draw.line(s,(223,226,174),(int(x-40),int(y)),(int(x-28),int(y)),3)

    def background(self):
        s=self.canvas
        s.fill((224,231,201))
        pygame.draw.rect(s,(40,65,43),(0,0,LOGICAL_WIDTH,132))
        pygame.draw.rect(s,(64,89,52),(0,132,LOGICAL_WIDTH,22))
        pygame.draw.rect(s,(113,125,77),(22,160,65,380),border_radius=9)
        gx,gy,cw,ch=(self.config[k] for k in ("grid_x","grid_y","cell_width","cell_height"))
        for row in range(5):
            for col in range(12):
                rect=(gx+col*cw,gy+row*ch,cw,ch)
                pygame.draw.rect(s,(118,163,79) if (row+col)%2==0 else (130,175,86),rect)
                for i in range(3):
                    xx=rect[0]+(col*11+row*17+i*21)%65+4
                    yy=rect[1]+(i*19+row*9)%65+5
                    pygame.draw.line(s,(111,155,72),(xx,yy),(xx+2,yy-4),1)
        self.text("守住草坪",(25,548),16,GREEN)
        self.text("US1 原型试玩 · 程序绘制美术",(480,575),12,(91,110,76))

    def draw(self,snapshot,events=(),mouse=None,help_open=False,message="",message_time=0):
        s=self.canvas
        t=snapshot["tick"]
        if self.last_session != snapshot["session_id"]:
            self.effects.clear()
            self.flash.clear()
            self.last_session=snapshot["session_id"]
        for e in events:
            if e["kind"]=="hit": self.flash[e["id"]]=t+8
            if e["kind"] in ("died","shot","collected","planted"):
                self.effects.append(dict(e,until=t+24))
        self.effects=[e for e in self.effects if e["until"]>t]
        self.background()
        if snapshot["phase"]=="menu":
            self.menu(t,help_open)
            return s
        self.sun(64,49,t,21)
        self.text(snapshot["sun"],(64,91),28,CREAM,True)
        self.text("阳光",(64,120),11,(196,212,170),True)
        types={p["id"]:p for p in self.config["plant_types"]}
        for name in ("sunflower","peashooter"):
            x,y,w,h=BUTTONS[name]
            selected=snapshot["selection"]["type_id"]==name
            self.rounded((x,y,w,h),(238,224,175),9,GOLD if selected else (135,151,92))
            self.rounded((x+5,y+5,w-10,52),(201,215,150),6)
            if name=="sunflower": self.sunflower(x+48,y+42,t,.62)
            else: self.peashooter(x+47,y+42,t,.62)
            self.text(types[name]["name"],(x+w/2,y+67),14,INK,True)
            self.text(str(types[name]["price"]),(x+w/2,y+87),15,(85,91,46),True)
            remaining=max(0,snapshot["ready_tick"][name]-t)
            if remaining:
                shade=pygame.Surface((w,h),pygame.SRCALPHA)
                shade.fill((27,48,32,155))
                s.blit(shade,(x,y))
                self.text(f"{remaining/60:.1f}s",(x+w/2,y+45),21,CREAM,True)
            elif snapshot["sun"]<types[name]["price"]:
                self.text("阳光不足",(x+w/2,y+43),13,(145,54,40),True)
        x,y,w,h=BUTTONS["shovel"]
        self.rounded((x,y,w,h),(89,114,66),10,GOLD if snapshot["selection"]["kind"]=="shovel" else None)
        pygame.draw.line(s,(198,159,97),(x+45,y+13),(x+28,y+43),5)
        pygame.draw.polygon(s,(196,203,175),[(x+18,y+36),(x+38,y+44),(x+29,y+58),(x+16,y+53)])
        self.text("铲子",(x+w/2,y+67),13,CREAM,True)
        self.text("白天草坪 / 01",(504,35),18,CREAM)
        self.text(f"已出现 {snapshot['next_spawn_index']} / {snapshot['total_spawns']}",(505,66),14,(190,209,161))
        self.text(f"消灭 {snapshot['kills']} 只",(505,89),14,(190,209,161))
        self.button("pause","暂停")
        # Progress bar reflects scheduled waves, not arbitrary wall time.
        pygame.draw.rect(s,(38,56,35),(548,118,224,5),border_radius=2)
        pygame.draw.rect(s,(217,191,83),(548,118,int(224*snapshot["next_spawn_index"]/snapshot["total_spawns"]),5),border_radius=2)
        for m in snapshot["mowers"]:
            if m["state"]!="spent": self.mower(m["x"]-12,self.row_y(m["row"])+8,m["state"])
        if mouse and snapshot["phase"]=="playing" and snapshot["selection"]["kind"]!="none":
            col=int((mouse[0]-self.config["grid_x"])//self.config["cell_width"])
            row=int((mouse[1]-self.config["grid_y"])//self.config["cell_height"])
            if 0<=row<5 and 0<=col<12:
                pygame.draw.rect(s,(247,225,137),(self.config["grid_x"]+col*72,self.config["grid_y"]+row*76,72,76),3)
        for p in snapshot["plants"]:
            x=self.config["grid_x"]+(p["col"]+.5)*self.config["cell_width"]
            y=self.row_y(p["row"])+5
            pygame.draw.ellipse(s,(92,134,62),(x-26,y+19,52,12))
            hit=self.flash.get(p["id"],0)>t
            if p["type_id"]=="sunflower": self.sunflower(x,y,t,hit=hit)
            else: self.peashooter(x,y,t,hit=hit,attack=p["action"]=="attacking")
            if p["hp"]<types[p["type_id"]]["hp"]:
                pygame.draw.rect(s,(78,89,52),(x-20,y+31,40,4))
                pygame.draw.rect(s,(213,211,98),(x-20,y+31,40*p["hp"]/types[p["type_id"]]["hp"],4))
        for shot in snapshot["projectiles"]:
            pygame.draw.circle(s,(52,113,48),(int(shot["x"]),int(self.row_y(shot["row"])-15)),6)
            pygame.draw.circle(s,(161,218,94),(int(shot["x"]-1),int(self.row_y(shot["row"])-17)),4)
        for z in snapshot["zombies"]:
            x,y=z["x"],self.row_y(z["row"])
            pygame.draw.ellipse(s,(92,134,62),(x-24,y+26,48,10))
            self.zombie(x,y,t+z["id"]*7,z["action"],self.flash.get(z["id"],0)>t)
        for e in self.effects:
            if e["kind"]=="died":
                life=(e["until"]-t)/24
                pygame.draw.circle(s,(207,217,152),(int(e["x"]),int(self.row_y(e["row"])-8)),max(1,int((1-life)*28)),2)
            elif e["kind"]=="collected":
                self.text(f"+{e['amount']}",(94,72-(24-(e["until"]-t))),17,GOLD)
        for sun in snapshot["suns"]:
            self.sun(sun["x"],sun["y"],t)
            if sun["expires_tick"]-t<120:
                pygame.draw.circle(s,(255,240,183),(int(sun["x"]),int(sun["y"])),26,1)
        hint="点击阳光收集 → 选卡 → 点击草坪种植   |   右键取消   空格暂停"
        if snapshot["selection"]["kind"]=="shovel": hint="铲子已选中：点击植物移除，不返还阳光。右键 / Esc 取消。"
        elif snapshot["selection"]["kind"]=="plant": hint="点击空白草坪种植。卡片冷却或阳光不足时不会扣费。右键取消。"
        self.text(hint,(192,549),13,(54,77,43))
        if message and message_time>0:
            self.rounded((183,132,480,27),(248,225,161),8)
            self.text(message,(423,144),14,(102,63,37),True)
        if snapshot["phase"] in ("paused","won","lost"):
            self.overlay(snapshot)
        return s

    def row_y(self,row):
        return self.config["grid_y"]+(row+.5)*self.config["cell_height"]

    def menu(self,t,help_open):
        s=self.canvas
        veil=pygame.Surface((LOGICAL_WIDTH,LOGICAL_HEIGHT),pygame.SRCALPHA)
        veil.fill((30,57,35,145))
        s.blit(veil,(0,0))
        self.rounded((281,48,488,508),(244,238,211),22,(194,199,155))
        if help_open:
            self.text("第一次守护草坪",(525,95),30,INK,True)
            self.text("不需要键盘也能玩，鼠标点一点即可。",(525,138),16,GREEN,True)
            for i,line in enumerate(HELP_LINES):
                self.text(line,(310,185+i*34),15,INK)
            self.button("back_help","我知道了",True)
            return
        self.text("LAWN DEFENSE",(525,93),14,GREEN,True)
        self.text("草坪保卫战",(525,142),42,INK,True)
        self.text("植物大战僵尸小游戏 · US1 原型试玩",(525,188),16,(96,114,76),True)
        self.sunflower(450,267,t,1.18)
        self.peashooter(550,267,t,1.18)
        self.sun(626,248,t,15)
        self.button("start","开始游戏",True)
        self.button("help","怎么玩？")
        self.button("exit_menu","退出")
        self.text("本版验证玩法，暂未接入原版美术与小狗皮肤。",(525,531),12,(108,115,85),True)

    def overlay(self,snapshot):
        s=self.canvas
        veil=pygame.Surface((LOGICAL_WIDTH,LOGICAL_HEIGHT),pygame.SRCALPHA)
        veil.fill((20,37,27,170))
        s.blit(veil,(0,0))
        phase=snapshot["phase"]
        self.rounded((349,172,352,310),(244,238,211),20)
        title={"paused":"休息一下","won":"草坪守住了！","lost":"防线被突破了"}[phase]
        self.text(title,(525,218),32,INK,True)
        if phase=="paused":
            self.text("时间已停止，准备好再继续。",(525,259),15,GREEN,True)
            self.button("resume","继续游戏",True)
            self.button("quit_pause","退出游戏")
            self.text("也可以按空格继续",(525,425),13,GREEN,True)
        else:
            subtitle="12只僵尸已全部清除，来再玩一局吧。" if phase=="won" else "多种向日葵，并为每一行安排射手。"
            self.text(subtitle,(525,260),14,GREEN,True)
            self.button("restart","再玩一局",True)
            self.button("menu","返回主菜单")
            self.button("exit_result","退出")
