import json
import math
import os
import struct
import sys
import wave
import io

import pygame

pygame.init()
try:
    pygame.mixer.init()
    AUDIO = True
except pygame.error:
    AUDIO = False

WIDTH, HEIGHT = 960, 540
FPS = 60
GROUND_Y = 455
PLAYER_SIZE = (34, 44)
MOVE_SPEED = 5
JUMP = -12
GRAVITY = 0.62
SAVE_FILE = os.path.join(os.path.dirname(__file__), "highscore.json")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Skybound Quest - Week 4")
clock = pygame.time.Clock()
FONT = pygame.font.Font(None, 28)
SMALL = pygame.font.Font(None, 23)
TITLE = pygame.font.Font(None, 64)

LEVELS = [
    {"name": "Meadow", "length": 2600, "coins": [(500,390),(760,330),(1050,390),(1400,300),(1750,380),(2200,320)],
     "enemies": [(850,390,820,1000,2),(1550,405,1500,1800,2.2)], "powerups": [(1200,350,"shield")]},
    {"name": "Canyon", "length": 3000, "coins": [(450,370),(700,300),(1050,380),(1350,330),(1750,280),(2100,360),(2500,300)],
     "enemies": [(620,405,550,850,2.5),(1250,400,1150,1500,2.8),(2050,400,1950,2400,3)],
     "powerups": [(900,350,"speed"),(1850,300,"shield")]},
    {"name": "Sky Temple", "length": 3400, "coins": [(450,380),(780,300),(1100,240),(1450,360),(1800,290),(2200,210),(2600,340),(3000,260)],
     "enemies": [(700,400,600,900,3),(1300,400,1150,1600,3.2),(2000,400,1850,2300,3.4),(2750,400,2550,3100,3.6)],
     "powerups": [(1000,200,"shield"),(2350,300,"speed"),(2900,220,"shield")]}
]

def tone(freq, duration=.1, volume=.15):
    if not AUDIO:
        return None
    rate=22050
    raw=bytearray()
    for i in range(int(rate*duration)):
        env=1-i/(rate*duration)
        sample=int(32767*volume*env*math.sin(2*math.pi*freq*i/rate))
        raw.extend(struct.pack("<h",sample))
    bio=io.BytesIO()
    with wave.open(bio,"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(raw)
    bio.seek(0)
    return pygame.mixer.Sound(file=bio)

SOUNDS={"coin":tone(880,.08,.18),"power":tone(1040,.12,.18),"hit":tone(180,.18,.2),"finish":tone(1320,.3,.2)}

def load_highscore():
    try:
        with open(SAVE_FILE,"r",encoding="utf-8") as f:
            return int(json.load(f).get("high_score",0))
    except (OSError,ValueError,TypeError):
        return 0

def save_highscore(score):
    try:
        with open(SAVE_FILE,"w",encoding="utf-8") as f:
            json.dump({"high_score":score},f)
    except OSError:
        pass

class Enemy:
    def __init__(self,x,y,left,right,speed):
        self.rect=pygame.Rect(x,y,34,34); self.left=left; self.right=right; self.speed=speed; self.dir=1
    def update(self):
        self.rect.x += self.speed*self.dir
        if self.rect.left<=self.left: self.rect.left=self.left; self.dir=1
        if self.rect.right>=self.right: self.rect.right=self.right; self.dir=-1
    def draw(self,cam):
        r=self.rect.move(-cam,0); pygame.draw.rect(screen,(210,65,80),r,border_radius=8)
        pygame.draw.circle(screen,(255,255,255),(r.x+10,r.y+10),4); pygame.draw.circle(screen,(255,255,255),(r.x+24,r.y+10),4)

def make_level(index):
    data=LEVELS[index]
    coins=[pygame.Rect(x-9,y-9,18,18) for x,y in data["coins"]]
    enemies=[Enemy(x,y,l,r,s) for x,y,l,r,s in data["enemies"]]
    powers=[{"rect":pygame.Rect(x-12,y-12,24,24),"kind":kind,"taken":False} for x,y,kind in data["powerups"]]
    platforms=[
        pygame.Rect(0,GROUND_Y,data["length"],85),
        pygame.Rect(350,390,180,18),pygame.Rect(650,320,160,18),
        pygame.Rect(950,400,180,18),pygame.Rect(1180,350,180,18),
        pygame.Rect(1450,300,190,18),pygame.Rect(1720,390,190,18),
        pygame.Rect(2050,320,170,18),pygame.Rect(2350,380,190,18),
        pygame.Rect(2650,280,180,18),pygame.Rect(2950,350,180,18)
    ]
    return platforms,coins,enemies,powers

def draw_background(index,cam):
    sky=[(70,155,210),(95,115,175),(65,75,130)][index]
    screen.fill(sky)
    # Parallax hills
    for i in range(-2,8):
        x=i*220-(cam*.25%220)
        pygame.draw.circle(screen,(55,105,125),(int(x),470),150)
        pygame.draw.circle(screen,(65,120,135),(int(x+100),475),130)

def draw_ui(level,lives,score,high,power):
    pygame.draw.rect(screen,(15,20,35),(0,0,WIDTH,68))
    screen.blit(FONT.render(f"LEVEL {level+1}: {LEVELS[level]['name']}",True,(245,245,245)),(16,12))
    screen.blit(FONT.render(f"Lives: {lives}",True,(245,245,245)),(230,12))
    screen.blit(FONT.render(f"Score: {score}",True,(245,245,245)),(350,12))
    screen.blit(FONT.render(f"High Score: {high}",True,(245,245,245)),(500,12))
    status=f"Power: {power.upper()}" if power else "Power: none"
    screen.blit(SMALL.render(status,True,(255,225,100)),(16,43))
    screen.blit(SMALL.render("A/D or ←/→  •  W/↑/Space jump",True,(220,230,245)),(400,43))

def main():
    high=load_highscore(); total_score=0; level=0; lives=3
    player=pygame.Rect(90,400,*PLAYER_SIZE); vx=vy=0; grounded=False
    power=None; power_timer=0; state="play"

    platforms,coins,enemies,powers=make_level(level)
    while True:
        dt=clock.tick(FPS)/1000
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_r and state in ("gameover","win"):
                high=load_highscore(); total_score=0; level=0; lives=3; power=None; power_timer=0
                player=pygame.Rect(90,400,*PLAYER_SIZE); platforms,coins,enemies,powers=make_level(level); state="play"

        if state=="play":
            keys=pygame.key.get_pressed()
            speed=MOVE_SPEED*(1.5 if power=="speed" else 1)
            vx=0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: vx-=speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: vx+=speed
            if (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]) and grounded:
                vy=JUMP; grounded=False

            player.x += int(vx)
            for p in platforms:
                if player.colliderect(p):
                    if vx>0: player.right=p.left
                    elif vx<0: player.left=p.right
            vy += GRAVITY; old_bottom=player.bottom; player.y += int(vy); grounded=False
            for p in platforms:
                if player.colliderect(p):
                    if vy>0 and old_bottom<=p.top:
                        player.bottom=p.top; vy=0; grounded=True
                    elif vy<0:
                        player.top=p.bottom; vy=0

            player.x=max(0,min(LEVELS[level]["length"]-player.width,player.x))
            for e in enemies: e.update()

            for c in coins[:]:
                if player.colliderect(c):
                    coins.remove(c); total_score+=100
                    if SOUNDS["coin"]: SOUNDS["coin"].play()
            for p in powers:
                if not p["taken"] and player.colliderect(p["rect"]):
                    p["taken"]=True; power=p["kind"]; power_timer=7
                    total_score+=50
                    if SOUNDS["power"]: SOUNDS["power"].play()
            if power:
                power_timer-=dt
                if power_timer<=0: power=None

            hit=any(player.colliderect(e.rect) for e in enemies)
            if hit and power=="shield":
                power=None; power_timer=0
                if SOUNDS["power"]: SOUNDS["power"].play()
                player.x=max(50,player.x-100)
            elif hit:
                lives-=1
                if SOUNDS["hit"]: SOUNDS["hit"].play()
                player.topleft=(90,400); vy=0; power=None; power_timer=0
                if lives<=0:
                    high=max(high,total_score); save_highscore(high); state="gameover"

            finish_x=LEVELS[level]["length"]-120
            if player.x>=finish_x:
                total_score+=500
                if SOUNDS["finish"]: SOUNDS["finish"].play()
                if level<2:
                    level+=1; player=pygame.Rect(90,400,*PLAYER_SIZE); vy=0; power=None; power_timer=0
                    platforms,coins,enemies,powers=make_level(level)
                else:
                    high=max(high,total_score); save_highscore(high); state="win"

            if player.top>HEIGHT:
                lives-=1; player.topleft=(90,400); vy=0
                if lives<=0:
                    high=max(high,total_score); save_highscore(high); state="gameover"

        cam=max(0,min(LEVELS[level]["length"]-WIDTH,player.centerx-WIDTH//2))
        draw_background(level,cam)
        for p in platforms: pygame.draw.rect(screen,(85,65,50),p.move(-cam,0),border_radius=4)
        for c in coins: pygame.draw.circle(screen,(255,215,45),(c.centerx-int(cam),c.centery),10)
        for p in powers:
            if not p["taken"]:
                col=(80,220,250) if p["kind"]=="shield" else (255,140,50)
                pygame.draw.circle(screen,col,(p["rect"].centerx-int(cam),p["rect"].centery),12)
        for e in enemies: e.draw(cam)

        door=pygame.Rect(LEVELS[level]["length"]-100,GROUND_Y-80,48,80).move(-cam,0)
        pygame.draw.rect(screen,(90,210,125),door,border_radius=6)
        pygame.draw.circle(screen,(255,220,80),(door.right-12,door.centery),4)
        pygame.draw.rect(screen,(65,215,120),player.move(-cam,0),border_radius=7)

        draw_ui(level,lives,total_score,high,power)

        if state in ("gameover","win"):
            overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,175)); screen.blit(overlay,(0,0))
            title="YOU WIN!" if state=="win" else "GAME OVER"
            t=TITLE.render(title,True,(255,255,255)); screen.blit(t,t.get_rect(center=(WIDTH//2,HEIGHT//2-35)))
            s=FONT.render(f"Score: {total_score}   High Score: {high}",True,(255,225,100))
            screen.blit(s,s.get_rect(center=(WIDTH//2,HEIGHT//2+20)))
            r=SMALL.render("Press R to play again",True,(235,240,250))
            screen.blit(r,r.get_rect(center=(WIDTH//2,HEIGHT//2+60)))

        pygame.display.flip()

if __name__=="__main__":
    main()
