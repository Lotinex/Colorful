import pygame as PG
import sys, math, random, os
import time, threading
import asyncio
from threading import Timer
PG.init()
PG.mixer.init()
PG.font.init()
class setInterval:
    def __init__(self,interval,action):
        self.interval=interval
        self.action=action
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self):
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()):
            nextTime+=self.interval
            self.action(self)

    def cancel(self):
        self.stopEvent.set()
class CounterInterval:
    def __init__(self, action):
        self._count = 0
        self.action = action
    def start(self, time):
        def _action(interval):
            self.action(self._count)
            self._count += 1
        self.interval = setInterval(time, lambda _: _action(self.interval))
        return self.interval
    def cancel(self):
        self.interval.cancel()
        
class _: 
    @staticmethod
    def loop(num, func):
        R = None
        for i in range(num):
            R = func(i)
            if R is False:
                return None
        return R
    @staticmethod
    def iterateDic(dic, func):
        R = None
        for k, value in list(dic.items()):
            R = func(k, value)
            if R is False:
                return None
        return R
    @staticmethod
    def iterate(list, func):
        R = None
        for e in list:
            R = func(e)
            if R is False:
                return None
        return R
class App:
    w = 1280
    h = 720
    @staticmethod
    def init(title):
        
        PG.display.set_caption(title)
        App.screen = PG.display.set_mode((App.w, App.h))
        App.clock = PG.time.Clock()
        Renderer.startGame()
    movingKeys = [PG.K_a, PG.K_d, PG.K_w, PG.K_s]
class Sound:
    fire = PG.mixer.Sound('sfxs/tap.wav')
    nextWave = PG.mixer.Sound('sfxs/nextWave.wav')
    build = PG.mixer.Sound('sfxs/build.wav')
    @staticmethod
    def play(sound):
        PG.mixer.Sound.play(sound)
    @staticmethod
    def stopMusic():
        PG.mixer.music.stop()
    @staticmethod
    def loopSound(sound):
        PG.mixer.music.load(sound)
        PG.mixer.music.set_volume(0.2)
        PG.mixer.music.play(-1)

Sound.fire.set_volume(0.1) # init
Sound.nextWave.set_volume(0.35)
Sound.build.set_volume(0.35)

class Game:
    money = 0
    bosses = [
        {'id': 'Marbas', 'hp': 20000, 'speed': 1, 'w': 70,'h': 70, 'x': -700, 'y': 0, 'bossType': 'Marbas', 'color': (0, 153, 0)},
        {'id': 'Dantalion', 'hp': 100000, 'speed': 0.4, 'w': 100,'h': 100, 'x': -700, 'y': 0, 'bossType': 'Dantalion', 'color': (70, 73, 100)},
        {'id': 'Decarabia', 'hp': 400000, 'speed': 1.5, 'w': 100,'h': 100, 'x': -700, 'y': 0, 'bossType': 'Decarabia', 'color': (70, 73, 100)}
    ]
    bossNames = {
        'Marbas': '마르바스',
        'Dantalion': '단탈리온',
        'Decarabia': '데카라비아'
    }
    wave = 0
    currentBoss = 'Marbas'
    remainMob = 0
    currentWaveTime = 0
    waveData = [
        {
            'mobNumber': 10,
            'mobBaseHp': 300,
            'mobIncreaseHp': 50,

            'mobSpawnSpeed': 1,
            'bossTime': 15
        },
        {
            'mobNumber': 30,
            'mobBaseHp': 700,
            'mobIncreaseHp': 100,

            'mobSpawnSpeed': 0.7,
            'bossTime': 20
        },
        {
            'mobNumber': 50,
            'mobBaseHp': 1000,
            'mobIncreaseHp': 200,

            'mobSpawnSpeed': 0.5,
            'bossTime': 45
        }
    ]
    turrets = {
        'red': {
            'name': '빨강',
            'atk': 500,
            'attackSpeed': 1,
            'color': (255, 0, 0)
        },
        'cyan': {
            'name': '시안',
            'atk': 150,
            'attackSpeed': 0.3,
            'color': (0, 168, 210)
        },
        'lime': {
            'name': '라임',
            'atk': 90,
            'attackSpeed': 0.12,
            'color': (191, 255, 0)
        },
        'crimson': {
            'name': '진홍',
            'atk': 1000,
            'attackSpeed': 1.5,
            'color': (220, 20, 60)
        }
    }
    map1 = [ 
        # 0: 빈자리 1: 길 2: 터렛설치장소 3: 엔드라인
        # 4: 오른쪽 5: 왼쪽 6: 위쪽 7: 아래쪽
        
        2, 2, 2, 2, 0, 0, 2, 2, 2, 0,
        1, 1, 1, 7, 2, 2, 4, 1, 1, 3,
        2, 2, 2, 1, 2, 2, 1, 2, 2, 0,
        0, 0, 2, 4, 1, 1, 6, 2, 0, 0,
        0, 0, 0, 2, 2, 2, 2, 0, 0, 0
    ]
    map = [
        0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 2, 4, 1, 7, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 
        0, 2, 2, 1, 2, 1, 2, 4, 1, 7, 2, 2, 4, 1, 1, 7, 2, 0, 0, 0, 
        1, 1, 1, 6, 2, 1, 2, 1, 2, 1, 2, 2, 1, 2, 2, 1, 2, 2, 2, 0, 
        0, 2, 2, 2, 2, 1, 2, 1, 2, 1, 2, 2, 1, 2, 2, 4, 1, 1, 1, 3, 
        0, 0, 0, 0, 2, 4, 1, 6, 2, 4, 1, 1, 6, 2, 0, 2, 2, 2, 2, 0,
        0, 0, 0, 0, 0, 2, 2, 2, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0 

    ]
    direction = {
        '4': 'right',
        '5': 'left',
        '6': 'up',
        '7': 'down'
    } 

class StaticText:
    def __init__(self, options):
       self.model = options['model']
       self.x = options['x']
       self.y = options['y']
       self.text = options['text']
       self.color = options['color']
       self.id = options['id']
    def render(self):
        self.model.render({
            'text': self.text,
            'color': self.color,
            'x': self.x,
            'y': self.y
        })
class DynamicText:
    def __init__(self, options):
       self.model = options['model']
       self.x = options['x']
       self.y = options['y']
       self.color = options['color']
       self.id = options['id']
    def render(self, text):
        self.model.render({
            'text': text,
            'color': self.color,
            'x': self.x,
            'y': self.y
        })
class FontModel:
    def __init__(self, options):
        self.font = options['font']
        self.size = options['size']
        self.body = PG.font.SysFont(self.font, self.size)
    def render(self, options):
        model = self.body.render(options['text'], True, options['color'])
        App.screen.blit(model, (options['x'], options['y']))
    def process(self, options):
        return self.body.render(options['text'], True, options['color'])
class Text:
    models = {
        'default30': FontModel({'font': None, 'size': 30}),
        'default20': FontModel({'font': None, 'size': 20}),
        'gothic15': FontModel({'font': 'malgungothic', 'size': 15}),
        'gothic20': FontModel({'font': 'malgungothic', 'size': 20}),
        'default45': FontModel({'font': None, 'size': 45}),

        'gothic50': FontModel({'font': 'malgungothic', 'size': 50}),
        'gothic40': FontModel({'font': 'malgungothic', 'size': 40}),
        'unicode20': FontModel({'font': 'segoe-ui-symbol.ttf', 'size': 20})
    }
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def getDistance(self, point2):
        return math.sqrt((point2.x - self.x) ** 2 + (point2.y - self.y) ** 2)
class Camera:
    x = 0
    y = 0
    @staticmethod
    def follow(entity):
        Camera.x = entity.x
        Camera.y = -entity.y
    @staticmethod
    def fix(x, y):
        Camera.x = x
        Camera.y = y
    @staticmethod
    def getDisplayCoords(x, y):
        return Point(x - Camera.x + App.w / 2, App.h - y - Camera.y - App.h / 2)

class Renderer:
    entities = {}
    floatTooltips = {}
    mobs = {}
    directionTiles = []
    texts = {}
    bossBar = None
    dynamicTexts = {
        'remainMob': DynamicText({
            'id': 'remainMob',
            'x': 0,
            'y': 25,
            'model': Text.models['gothic20'],
            'color': 'black'
        }),
        'bossTime': DynamicText({
            'id': 'remainMob',
            'x': 0,
            'y': 0,
            'model': Text.models['gothic20'],
            'color': 'red'
        }),
        'money': DynamicText({
            'id': 'remainMob',
            'x': 0,
            'y': 50,
            'model': Text.models['gothic20'],
            'color': 'yellow'
        })
    }
    spawnMobInterval = None
    bossTimeInterval = None
    @staticmethod
    def addStaticText(text):
        Renderer.texts[text.id] = text
    @staticmethod
    def removeText(id):
        del Renderer.texts[id]
    @staticmethod
    def spawn(entity):
        Renderer.entities[entity.id] = entity
        if entity.type == 'mob':
            Renderer.mobs[entity.id] = entity
    @staticmethod
    def multipleSpawn(*entities):
        _.iterate(entities, lambda e: Renderer.spawn(e))
    @staticmethod
    def addTooltip(tooltip):
        Renderer.floatTooltips[tooltip.id] = tooltip
    @staticmethod
    def kill(id):
        del Renderer.entities[id]
        if id in Renderer.mobs:
            del Renderer.mobs[id]
    @staticmethod
    def nextWave():
        Sound.play(Sound.nextWave)
        Sound.stopMusic()
        Game.currentWaveTime = 0
        Game.wave += 1
        Game.currentBoss = Game.bosses[Game.wave - 1]['id']
        Game.remainMob = Game.waveData[Game.wave - 1]['mobNumber']
        Sound.loopSound(f'musics/{Game.currentBoss}.wav')
        Renderer.addStaticText(
            StaticText({
                'id': 'waveText',
                'x': 490,
                'y': 100,
                'model': Text.models['gothic40'],
                'color': 'black',
                'text': f'~ 웨이브 {str(Game.wave)} ~ '
            })
        )
        Renderer.addStaticText(
            StaticText({
                'id': 'waveBoss',
                'x': 520,
                'y': 150,
                'model': Text.models['gothic20'],
                'color': 'black',
                'text': f'보스 < {Game.bossNames[Game.currentBoss]} >'
            })
        )
        def timeCount(i):
            if i == Game.waveData[Game.wave - 1]['bossTime']:
                Renderer.bossTimeInterval.cancel()
                boss = Boss(Game.bosses[Game.wave - 1])
                boss.spawn()
                Renderer.bossBar = BossBar({'limit': boss.hp})
                Renderer.spawn(Renderer.bossBar)
                return None
            Game.currentWaveTime += 1

        def mobSpawnStart():
            Renderer.bossTimeInterval = CounterInterval(timeCount)
            Renderer.bossTimeInterval.start(1)
            def spawnMob(i):
                if i == Game.waveData[Game.wave - 1]['mobNumber']:
                    return Renderer.spawnMobInterval.cancel()
                mob = Mob({'id': f'mob-{i}', 'x': -700, 'y': 0, 'w': 40, 'h': 40, 'color': (125, 125, 125), 'hp': Game.waveData[Game.wave - 1]['mobBaseHp'] + Game.waveData[Game.wave - 1]['mobIncreaseHp'] * i, 'speed': 1})
                Mob.mobCounter += 1
                Renderer.spawn(mob)
            Renderer.spawnMobInterval = CounterInterval(spawnMob)
            Renderer.spawnMobInterval.start(Game.waveData[Game.wave - 1]['mobSpawnSpeed'])

        def removeTexts():
            Renderer.removeText('waveText')
            Renderer.removeText('waveBoss')
            mobSpawnStart()
        textTimer = Timer(3, removeTexts)
        textTimer.start()
        
    @staticmethod
    def startGame():
        turretTileTooltip = FloatTooltip({
            'id': 'turretTileTooltip',
            'x': 100,
            'y': 100,
            'texts': [
                Text.models['gothic15'].process({'text': '빈 터렛 타일', 'color': 'red'}),
                Text.models['gothic15'].process({'text': '클릭하여 터렛 추가', 'color': 'cyan'})
            ],
            'w': 200,
            'h': 100
        })
        Renderer.addTooltip(turretTileTooltip)
        
        def initTiles():
            for i in range(25):
                line = Rect({'id': f'line-{i}', 'x': -650 + 50 * i, 'y': 0, 'w': 50, 'h': 50, 'color': (30, 30, 30)})
                Renderer.spawn(line)

            baseY = -50
            for i in range(2):
                for j in range(25):
                    turretTile = TurretTile({'id': f'turretTile-{i}-{j}', 'x': -650 + 50 * j, 'y': baseY})
                    Renderer.spawn(turretTile)
                baseY += 100

        endPoint = Rect({'id': 'endPoint', 'x': 600, 'y': 0, 'w': 50, 'h': 50, 'color': 'red'})
        Renderer.spawn(endPoint)


        def getMapIdx(value):
            point = None
            if value < 10:
                point = Point(
                    value,
                    1
                )
            if value < 100:
                point = Point(
                    value - (20 * math.trunc(value / 20)) + 1,
                    math.trunc(value / 20) + 1
                )
            else:
                x = value - 100 + 1
                if value > 120:
                    x -= 20
                point = Point(
                    x,
                    math.trunc(value / 20) + 1
                )  
            return point
        def getPosition(posType, value):
            if posType == 'x':
                return -700 + 50 * (value + 1)
            elif posType == 'y':
                return 200 - 50 * (value)
        for i, tile in enumerate(Game.map):
            if tile == 0:
                continue
            elif tile == 1:
                idx = getMapIdx(i)
                line = Rect({'id': f'line-{i}', 'x': getPosition('x', idx.x), 'y': getPosition('y', idx.y), 'w': 50, 'h': 50, 'color': (30, 30, 30)})
                Renderer.spawn(line)
            elif tile == 2:
                idx = getMapIdx(i)
                turretTile = TurretTile({'id': f'turretTile-{i}', 'x': getPosition('x', idx.x), 'y': getPosition('y', idx.y)})
                Renderer.spawn(turretTile)
            elif tile == 3:
                idx = getMapIdx(i)
                endPoint = Rect({'id': 'endPoint', 'x': getPosition('x', idx.x), 'y': getPosition('y', idx.y), 'w': 50, 'h': 50, 'color': 'red'})
                Renderer.spawn(endPoint)

            elif tile == 4 or tile == 5 or tile == 6 or tile == 7:
                idx = getMapIdx(i)
                line = DirectionTile({'id': f'line-{i}', 'x': getPosition('x', idx.x), 'y': getPosition('y', idx.y), 'w': 50, 'h': 50, 'color': (30, 30, 30), 'direction': Game.direction[str(tile)]})
                Renderer.spawn(line)    


        Renderer.spawn(turretTileTooltip)

        Renderer.nextWave()       
        Renderer._internalThread() # required
    @staticmethod
    def _internalThread():
        while 1:
            App.clock.tick(60)
            Renderer.update()
            Renderer.render()
            PG.display.update()
    @staticmethod
    def update():

        def entityProcess(entity):
            if entity.type == 'rect':
                pos = PG.mouse.get_pos()
                if entity.checkMouseOverlap(pos):
                    entity.hover(pos)
                elif entity.hovered:
                    entity.unHover()
            if entity.type == 'mob':
                entity.move()
        _.iterateDic(Renderer.entities, lambda _, entity: entityProcess(entity))

        def renderFloatTooltip(tooltip):
            if tooltip.show:
                pos = PG.mouse.get_pos()
                tooltip.x = pos[0] - Camera.x - App.w / 2 + tooltip.w / 2 + 10
                tooltip.y = App.h - pos[1] - Camera.y - App.h / 2 - tooltip.h / 2 - 10
        _.iterateDic(Renderer.floatTooltips, lambda _, tooltip: renderFloatTooltip(tooltip))
        for event in PG.event.get():
            if event.type == PG.QUIT:
                os._exit(1)
            if event.type == PG.MOUSEBUTTONDOWN:
                Renderer.onClick(PG.mouse.get_pos())

        keys = PG.key.get_pressed()
        Renderer.onKeyboardEvent(keys)
        #Camera.follow(Renderer.get('player'))
    @staticmethod
    def onKeyboardEvent(keyEvent):
        pass
    @staticmethod
    def onClick(pos):
        def rectAction(entity):
            if entity.type == 'rect':
                res = entity.checkMouseOverlap(pos)
                if res:
                    entity.onClick(pos)
        _.iterateDic(Renderer.entities, lambda _, entity: rectAction(entity))
    @staticmethod
    def render():
        App.screen.fill('gray')
        if len(Renderer.texts) > 0:
            _.iterateDic(Renderer.texts, lambda _, text: text.render())
        Renderer.dynamicTexts['bossTime'].render(f'보스 남은 시간: {Game.waveData[Game.wave - 1]["bossTime"] - Game.currentWaveTime}초')
        Renderer.dynamicTexts['remainMob'].render(f'남은 적 수: {Game.remainMob} / {Game.waveData[Game.wave - 1]["mobNumber"]}')
        Renderer.dynamicTexts['money'].render(f'종이: {Game.money}')
        _.iterateDic(Renderer.entities, lambda _, entity: entity.render())
        _.iterateDic(Renderer.floatTooltips, lambda _, tooltip: tooltip.render())
    @staticmethod
    def get(id):
        return Renderer.entities[id] 
    @staticmethod
    def getFloatTooltip(id):
        return Renderer.floatTooltips[id]

class Entity: # abstract class
    def __init__(self, options):
        self.id = options['id']
        self.x = options['x']
        self.y = options['y']
    def render(self): #override this
        return None
class Circle(Entity):
    def __init__(self, options):
        super().__init__(options)
        self.type = 'circle'
        self.color = options['color']
        self.radius = options['radius']
    def render(self): # override
        PG.draw.circle(
            App.screen, 
            self.color, 
            (self.x - Camera.x + App.w / 2, App.h - self.y - Camera.y - App.h / 2),
            self.radius
        )
class Bullet(Circle):
    bulletCounter = 0
    def __init__(self, options):
        super().__init__(options)
        self.turret = options['turret']
    def fire(self, target):
        tx = target.x - self.x
        ty = target.y - self.y
        dist = math.sqrt(tx * tx + ty * ty)
        def getDist():
            return math.sqrt((target.x - self.x) ** 2 + (target.y - self.y) ** 2)
        rad = math.atan2(ty, tx)

        velX = (tx/dist) * 8
        velY = (ty/dist) * 8

        def move(interval):
            self.x += 0.8 / dist * tx
            self.y += 0.8 / dist * ty
            if getDist() <= 5 or not(target.id in Renderer.entities) or abs(target.x - self.x) <= 5 or abs(target.y - self.y) <=5:
                self.turret.target = Mob.getFirstMob()
                interval.cancel()
                target.onHit(self.turret.atk)
                Renderer.kill(self.id)
        interval = setInterval(0.001, move)
    def render(self): # override
        super().render()
    def attackAction(self):
        pass


class Rect(Entity):
    def __init__(self, options):
        super().__init__(options)
        self.type = 'rect'
        self.color = options['color']
        self.w = options['w']
        self.h = options['h']
        self.hovered = False
        self.alpha = 255
        self.show = True
    def checkMouseOverlap(self, pos):
        x = self.x - self.w / 2 - Camera.x + App.w / 2
        y = App.h - self.y - self.h / 2 - Camera.y - App.h / 2
        if pos[0] >= x and pos[0] <= x + self.w and pos[1] >= y and pos[1] <= y + self.h:
            return True
    def onClick(self, pos): # override this
        print(1)
    def hover(self, pos): # override this
        pass
    def unHover(self): # override this
        pass
    def getDisplayCoords(self):
        return Point(self.x - self.w / 2 - Camera.x + App.w / 2, App.h - self.y - self.h / 2 - Camera.y - App.h / 2)
    def render(self): # override
        if not self.show:
            return None
        surface = PG.Surface((self.w, self.h))
        surface.set_alpha(self.alpha)
        surface.fill(self.color)
        PG.draw.rect(
            surface, self.color,
            [
                self.x - self.w / 2 - Camera.x + App.w / 2,
                App.h - self.y - self.h / 2 - Camera.y - App.h / 2, 
                self.w, 
                self.h
            ]
        )
        App.screen.blit(surface, (self.x - self.w / 2 - Camera.x + App.w / 2, App.h - self.y - self.h / 2 - Camera.y - App.h / 2))
class DirectionTile(Rect):
    def __init__(self, options):
        super().__init__(options)
        self.direction = options['direction']
        Renderer.directionTiles.append({
            'x': self.x,
            'y': self.y,
            'direction': self.direction
        })
class TurretTile(Rect):
    turretCounter = 0
    def hover(self, pos): # override
        self.hovered = True
        self.color = (200, 200, 200)
        if(self.turret is not None):
            data =  Game.turrets[self.turret]
            Renderer.getFloatTooltip('turretTileTooltip').texts = [
                Text.models['gothic15'].process({'text': data['name'] + '색 색종이', 'color': data['color']}),
                Text.models['gothic15'].process({'text': '공격력 ' + str(data['atk']), 'color': 'cyan'}),
                Text.models['gothic15'].process({'text': '공격 속도 ' + str(data['attackSpeed']), 'color': 'cyan'})
            ]
        else:
            Renderer.getFloatTooltip('turretTileTooltip').texts = [
                Text.models['gothic15'].process({'text': '빈 터렛 타일', 'color': 'red'}),
                Text.models['gothic15'].process({'text': '클릭하여 터렛 추가', 'color': 'cyan'})
            ]
        Renderer.getFloatTooltip('turretTileTooltip').show = True
    def unHover(self): # override
        self.hovered = False
        self.color = (180, 180, 180)
        Renderer.getFloatTooltip('turretTileTooltip').show = False
    def onClick(self, pos): # override
        if self.turret is None:
            turretType = random.choice(list(Game.turrets.keys()))
            self.turret = turretType
            turret = Turret({
                'id': f'turret-{turretType}-{TurretTile.turretCounter}',
                'tile': self,
                'color': Game.turrets[turretType]["color"],
                'w': 50,
                'h': 50,
                'name': f'{Game.turrets[turretType]["name"]}색 색종이',
                'atk': Game.turrets[turretType]["atk"],
                'attackSpeed': Game.turrets[turretType]["attackSpeed"]
            })
            Renderer.spawn(turret)
            turret.attack()
            TurretTile.turretCounter += 1
    def __init__(self, options):
        super().__init__({
            'id': options['id'],
            'x': options['x'],
            'y': options['y'],
            'color': (180, 180, 180),
            'w': 50,
            'h': 50
        })
        self.turret = None

class Tooltip(Rect):
    def __init__(self, options):
        super().__init__({
            'id': options['id'],
            'x': options['x'],
            'y': options['y'],
            'color': 'black',
            'w': options['w'],
            'h': options['h']
        })
        self.texts = options['texts']
        self.type = 'tooltip'
        self.alpha = 180
        self.show = False

class FloatTooltip(Tooltip):
    def __init__(self, options):
        super().__init__(options)
        self.type = 'floatTooltip'
    def render(self): # override
        super().render()
        if self.show:
            pos = self.getDisplayCoords()
            idx = 0
            for textModel in self.texts:
                App.screen.blit(textModel, (pos.x + 10, pos.y + 10 + idx * 25))
                idx += 1

class Mob(Rect):
    mobCounter = 0
    @staticmethod
    def getFirstMob():
        target = None
        biggest = 0
        for k in list(Renderer.mobs):
            mob = Renderer.mobs[k]
            if mob.moveCounter > biggest:
                biggest = mob.moveCounter
                target = mob
        return target
    def __init__(self, options):
        super().__init__({
            'id': options['id'],
            'x': options['x'],
            'y': options['y'],
            'color': options['color'],
            'w': options['w'],
            'h': options['h']
        })
        self.moveSpeed = options['speed']
        self.hp = options['hp']
        self.type = 'mob'
        self.moveCounter = 0
        self.moveDirection = 'right'
    def onDeath(self):
        Game.money += Game.wave * 10
    def move(self):
        def checkDirectionTile(tile):
            x = self.x
            y = self.y
            # x >= tile['x'] and x <= tile['x'] + 50 and y >= tile['y'] - 50 and y <= tile['y'] 
            if math.sqrt((tile['x'] - x) ** 2 + (tile['y'] - y) ** 2) <= self.moveSpeed:
                self.moveDirection = tile['direction']
        _.iterate(Renderer.directionTiles, lambda tileData: checkDirectionTile(tileData))

        if self.moveDirection == 'right':
            self.x += self.moveSpeed
        elif self.moveDirection == 'left':
            self.x -= self.moveSpeed
        elif self.moveDirection == 'up':
            self.y += self.moveSpeed
        elif self.moveDirection == 'down':
            self.y -= self.moveSpeed
        self.moveCounter += self.moveSpeed
    def onHit(self, damage):
        self.hp -= damage
    def render(self):
        if self.hp <= 0:
            Renderer.kill(self.id)
            if not hasattr(self, 'bossType'):
                Mob.mobCounter -= 1
                Game.remainMob -= 1
            self.onDeath()
            return None
        super().render()
        PG.draw.rect(
            App.screen, (200, 200, 200),
            [
                self.x - self.w / 2 - Camera.x + App.w / 2,
                App.h - self.y - self.h / 2 - Camera.y - App.h / 2, 
                self.w, 
                self.h
            ],
            2
        )
        pos = self.getDisplayCoords()
        Text.models['default20'].render({
            'text': str(self.hp), 
            'x': pos.x + self.w / 4, 
            'y': pos.y + 15, 
            'color': 'white'
        })
class BossBar(Entity):
    def __init__(self, options):
        super().__init__({
            'id': 'bossBar',
            'x': 0,
            'y': 270
        })
        self.limit = options['limit']
        self.w = 500
        self.h = 30
        self.current = self.limit
        self.type = 'bossBar'
    def render(self): # override
        PG.draw.rect(
            App.screen, (25, 25, 25),
            [
                self.x - self.w / 2 - Camera.x + App.w / 2,
                App.h - self.y - self.h / 2 - Camera.y - App.h / 2, 
                self.w, 
                self.h
            ]
        )
        PG.draw.rect(
            App.screen, 'red',
            [
                self.x - self.w / 2 - Camera.x + App.w / 2,
                App.h - self.y - self.h / 2 - Camera.y - App.h / 2, 
                self.w * (self.current / self.limit), 
                self.h
            ]
        )
        Text.models['gothic20'].render({
            'color': 'white',
            'text': Game.bossNames[Game.currentBoss],
            'x': (self.x - self.w / 2 - Camera.x + App.w / 2),
            'y': (App.h - self.y - self.h / 2 - Camera.y - App.h / 2) - 25
        })
    def setHp(self, hp):
        self.current = hp
class Boss(Mob):
    def __init__(self, options):
        super().__init__(options)
        self.bossType = options['bossType']
    def spawn(self):
        Renderer.spawn(self)
        Game.currentBoss = self.bossType
        Sound.loopSound(f'musics/{self.bossType}.wav')
    def onDeath(self):
        Renderer.kill('bossBar')
        Renderer.nextWave()
    def onHit(self, damage): # override
        super().onHit(damage)
        Renderer.bossBar.current -= damage
class Turret(Rect):
    def __init__(self, options):
        super().__init__({
            'id': options['id'],
            'x': options['tile'].x,
            'y': options['tile'].y,
            'color': options['color'],
            'w': options['w'],
            'h': options['h']
        })
        self.attackSpeed = options['attackSpeed']
        self.type = 'turret'
        self.atk = options['atk']
        self.name = options['name']
    def action(self, interval):
        if len(Renderer.mobs) != 0 and Mob.getFirstMob() != None:
            self.target = Mob.getFirstMob()
            if not(self.target.id in Renderer.mobs):
                self.action()
            bullet = Bullet({'turret': self, 'id': f'bullet-{Bullet.bulletCounter}', 'x': self.x, 'y': self.y, 'radius': 5, 'color': self.color})

            Renderer.spawn(bullet)
            Bullet.bulletCounter += 1
            bullet.fire(self.target)
    def attack(self):
        self.interval = setInterval(self.attackSpeed, self.action)

App.init('Colorless v1.0')
