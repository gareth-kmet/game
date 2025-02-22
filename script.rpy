﻿init -10 python:
    from enum import Flag, auto, Enum
    import builtins
    from math import floor, ceil

    IMAGE_SIZE = 48
    FRAME_LENGTH = 0.16

    class Direction(Enum):
        NONE = 0
        RIGHT = 1, "#ff0000"
        UP = 2
        LEFT = 3, "#84AD48"
        DOWN = 4

        def __new__(cls, val, *args):
            self = builtins.object.__new__(cls)
            self._value_ = val
            return self

        def __init__(self, val, colour="#ffffff"):
            self.textColour = colour


    def setDefault(d, **kwargs):
        for k in kwargs:
            if k not in d:
                d[k] = kwargs[k]
        return d

    class SourceFile(Enum):
        def __new__(cls, tag, file):
            obj = builtins.object.__new__(cls)
            obj._value_ = tag
            return obj
            
        def __init__(self, tag, file):
            self.file = f"{IMAGE_SIZE}/{file}"
            self.tag = tag

    class CharacterSourceFiles(SourceFile):
        CHARACTER_PREMADE_17 = "premade 17", "character/Premade_Character_17.png"
    
    class RoomSourceFiles(SourceFile):
        WALLS = "walls", "room/Room_Builder_3d_walls.png"
        FLOORS = "floors", "room/Room_Builder_Floors.png"
        BORDERS = "borders", "room/Room_Builder_borders.png"
        INTERIOR = "interior", "room/Condominium_Black_Shadow.png"
        SHADOW = "shadow", "room/Room_Builder_shadow.png"
    
    class ObjectSourceFiles(SourceFile):
        FIREPLACE = "fireplace", "room/objects/fireplace.png"
        CAT = "cat", "room/objects/cat.png"
        CLOSED_SIGN = "closed", "room/objects/closed.png"
        OPEN_SIGN = "open", "room/objects/open.png"
        SMALL_FERN = "small fern", "room/objects/smallfern.png"
        MEDIUM_FERN = "med fern", "room/objects/mediumfern.png"
        LARGE_FERN = "large fern", "room/objects/largefern.png"
        BASEMENT = "basement", "room/objects/basement.png"

    class DoorSourceFiles(SourceFile):
        GLASS_LEFT = "glass left", "room/doors/glass_left.png"
        GLASS_RIGHT = "glass right", "room/doors/glass_right.png"

    class SpriteTheme(Enum):
        def __new__(cls, tag, kwargs):
            value = len(cls.__members__) + 1
            obj = builtins.object.__new__(cls)
            obj._value_ = value
            return obj

        def __init__(self, tag, kwargs):
            self.tag = tag
            self.__setup(**kwargs)

        def __setup(self, x = 0, y = 0, r = 0, c = 0, src = None):
            self.x = x + c * IMAGE_SIZE
            self.y = y + r * IMAGE_SIZE
            self.source = src

    class VoidTheme(SpriteTheme):
        VOID = '', dict() # This one will cause image to not be drawn

    class StaticSpriteThemes(SpriteTheme):
        NONE = "none", dict() # This one will cause image to use source

    class Sprite(Enum):
        
        def __new__(cls, char, kwargs):
            obj = builtins.object.__new__(cls)
            obj._value_ = char
            return obj

        def __init__(self, char, kwargs):
            self.c = char
            self.__setup(**kwargs)
        
        def __setup(self, 
                x=0, y=0, r=0, c=0, w=IMAGE_SIZE, h=IMAGE_SIZE, anchorx=0, anchory=0,
                f = 1, df = (1,0), themes = StaticSpriteThemes, src = None, isVoid = False,
                up=0, down=0, left=0, right=0, none=0,
                upy=0, downy=0, lefty=0, righty=0, noney=0,
                upx=0, downx=0, leftx=0, rightx=0, nonex=0
            ):
            self.x = x + c * IMAGE_SIZE
            self.y = y + r * IMAGE_SIZE
            self.isVoid = isVoid
            self.src_override = src

            self.width = w if not isVoid else 0
            self.height = h if not isVoid else 0
            self.themes = themes if not isVoid else VoidTheme
            self.frames = f if not isVoid else 1
            self.dframe = df
            self.directional_offsets = {
                Direction.NONE: (nonex + df[0] * none * f, noney + df[1] * none * f),
                Direction.UP:   (upx + df[0] * up * f, upy + df[1] * up * f),
                Direction.DOWN: (downx + df[0] * down * f, downy + df[1] * down * f),
                Direction.LEFT: (leftx + df[0] * left * f, lefty + df[1] * left * f),
                Direction.RIGHT:(rightx + df[0] * right * f, righty + df[1] * right * f)
            }
            self.anchorx=int(anchorx)
            self.anchory=int(anchory)

        def position(self, fromPos=(0,0)):
            return fromPos[0]-self.anchorx, fromPos[1]-self.anchory

        def buildNull(self, *args, **kwargs):
            return Null(self.width, self.height)

        def buildStaticHandler(self):
            return StaticSpriteRenderHandler(self)

        def buildStatic(self, theme, frame = 0, direction=Direction.NONE, nullable=True):
            if self.isVoid or self.themes == VoidTheme or theme == VoidTheme.VOID or theme is None:
                if nullable:
                    return None
                else:
                    return Null(self.width, self.height)

            x = theme.x + self.x + frame * self.width * self.dframe[0] + self.directional_offsets[direction][0] * self.width
            y = theme.y + self.y + frame * self.height * self.dframe[1] + self.directional_offsets[direction][1] * self.height
            source = self.src_override.file if self.src_override is not None else theme.source.file
            img = Crop((x,y, self.width, self.height), source)
            return img
            
        @classmethod
        def _missing_(cls, value):
            return None

    class StaticSpriteTiles(Sprite):
        VOID = ' ', dict(isVoid=True)
        FIREPLACE = 'f', dict(h=IMAGE_SIZE*3,w=IMAGE_SIZE*2,anchory=IMAGE_SIZE*2,f=4,themes=StaticSpriteThemes,src=ObjectSourceFiles.FIREPLACE)
        CAT = 'c', dict(w=IMAGE_SIZE*3,f=12,themes=StaticSpriteThemes,src=ObjectSourceFiles.CAT)
        EXIT_SHADOW = 's', dict(r=2,c=10,themes=StaticSpriteThemes,src=RoomSourceFiles.SHADOW)
        CLOSED_SIGN = 'O', dict(themes=StaticSpriteThemes,src=ObjectSourceFiles.CLOSED_SIGN, anchorx = 0.2*IMAGE_SIZE)
        OPEN_SIGN = 'o', dict(themes=StaticSpriteThemes,src=ObjectSourceFiles.OPEN_SIGN, anchorx = -0.2*IMAGE_SIZE)
        SMALL_FERN = 'p', dict(themes=StaticSpriteThemes,src=ObjectSourceFiles.SMALL_FERN,h=IMAGE_SIZE*2)
        MEDIUM_FERN = 'P', dict(themes=StaticSpriteThemes,src=ObjectSourceFiles.MEDIUM_FERN,h=IMAGE_SIZE*3)
        LARGE_FERN = 'L', dict(themes=StaticSpriteThemes,src=ObjectSourceFiles.LARGE_FERN,h=IMAGE_SIZE*3,w=IMAGE_SIZE*2)
        RUGL = '1', dict(themes=StaticSpriteThemes, src=ObjectSourceFiles.BASEMENT, r=44,c=9,h=IMAGE_SIZE*3)
        RUGM = '2', dict(themes=StaticSpriteThemes, src=ObjectSourceFiles.BASEMENT, r=44,c=10,h=IMAGE_SIZE*3)
        RUGR = '3', dict(themes=StaticSpriteThemes, src=ObjectSourceFiles.BASEMENT, r=44,c=12,h=IMAGE_SIZE*3)

    class StairTopThemes(SpriteTheme):
        GREY    = "grey",   dict(r=0,c=0)
        SILVER  = "silver", dict(r=6,c=0)
        BEIGE   = "beige",  dict(r=0,c=6)
        BROWN   = "brown",  dict(r=6,c=6)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, src = RoomSourceFiles.INTERIOR)) 
    
    class StairBotThemes(SpriteTheme):
        GREY    = "grey",   dict(c=0)
        SILVER  = "silver", dict(c=6)
        BEIGE   = "beige",  dict(c=3)
        BROWN   = "brown",  dict(c=9)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, r=4, src = RoomSourceFiles.INTERIOR)) 
    
    class StairCarpetThemes(SpriteTheme):
        RED = "red", dict(c=12)
        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, src = RoomSourceFiles.INTERIOR)) 

    class FloorMatThemes(SpriteTheme):
        LIGHT   = "light",  dict(r=6,c=13)
        MID     = "mid",    dict(r=7,c=13)
        DARK    = "dark",   dict(r=8,c=13)
        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, src = RoomSourceFiles.INTERIOR)) 

    class CondoInteriorTiles(Sprite):
        VOID = ' ', dict(isVoid=True)
        STAIR_U4_LEFT   = 'r', dict(r=0,c=1,h=IMAGE_SIZE*4,themes=StairTopThemes)
        STAIR_U4_MID    = 'f', dict(r=0,c=0,h=IMAGE_SIZE*4,themes=StairTopThemes)
        STAIR_U4_RIGHT  = 'v', dict(r=0,c=2,h=IMAGE_SIZE*4,themes=StairTopThemes)
        STAIR_U3_LEFT   = 'e', dict(r=1,c=4,h=IMAGE_SIZE*3,themes=StairTopThemes)
        STAIR_U3_MID    = 'd', dict(r=1,c=3,h=IMAGE_SIZE*3,themes=StairTopThemes)
        STAIR_U3_RIGHT  = 'c', dict(r=1,c=5,h=IMAGE_SIZE*3,themes=StairTopThemes)
        STAIR_D2_LEFT   = 'w', dict(r=0,c=1,h=IMAGE_SIZE*2,themes=StairBotThemes)
        STAIR_D2_MID    = 's', dict(r=0,c=0,h=IMAGE_SIZE*2,themes=StairBotThemes)
        STAIR_D2_RIGHT  = 'x', dict(r=0,c=2,h=IMAGE_SIZE*2,themes=StairBotThemes)

        STMAT_U4        = 'R', dict(r=0,c=0,w=IMAGE_SIZE*2,h=IMAGE_SIZE*4,themes=StairCarpetThemes)
        STMAT_U3        = 'E', dict(r=1,c=2,w=IMAGE_SIZE*2,h=IMAGE_SIZE*3,themes=StairCarpetThemes)
        STMAT_D2        = 'W', dict(r=4,c=0,w=IMAGE_SIZE*2,h=IMAGE_SIZE*2,themes=StairCarpetThemes)

        FLOORMAT_1      = 'm', dict(c=0,themes=FloorMatThemes)
        FLOORMAT_2      = 'M', dict(c=1,w=IMAGE_SIZE*2,themes=FloorMatThemes)

    class FloorThemes(SpriteTheme):
        WOOD = 'wood', dict(c=0,r=10)
        BEIGE = "beige", dict(r=22,c=0)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, src = RoomSourceFiles.FLOORS))   

    """
    012
    345
    """
    class FloorTiles(Sprite):
        VOID = ' ', dict(isVoid=True)

        TOP_LEFT    = '0', dict(c= 0,r= 0)
        TOP         = '1', dict(c= 1,r= 0)
        TOP_RIGHT   = '2', dict(c= 2,r= 0)
        LEFT        = '3', dict(c= 0,r= 1)
        MID         = '4', dict(c= 1,r= 1)
        DARK        = '5', dict(c= 2,r= 1)

        def __init__(self, char, kwargs):
            super().__init__(char, setDefault(kwargs, themes=FloorThemes))
    
    class BorderThemes(SpriteTheme):
        WHITE = "white", dict(c=0,r=0)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, src = RoomSourceFiles.BORDERS,x=2*IMAGE_SIZE))
    
    class BorderTiles(Sprite):
        VOID = ' ', dict(isVoid=True)
        
        WALL_R_OPEN_TB          = 'a', dict(r=0,c=0)
        WALL_L_OPEN_TB          = 'b', dict(r=0,c=1)
        BLOCK_CLOSED            = 'f', dict(r=0,c=5)
        BLOCK_T_OPEN_BL         = 'h', dict(r=0,c=7)
        BLOCK_T_OPEN_BLR        = 'i', dict(r=0,c=8)
        BLOCK_T_OPEN_BR         = 'j', dict(r=0,c=9)
        WALL_T_OPEN_L           = 'k', dict(r=1,c=0)
        WALL_T_OPEN_R           = 'l', dict(r=1,c=1)
        WALL_TR_OPEN_BL_TOP_T   = 'm', dict(r=1,c=2)
        WALL_TL_OPEN_BR_TOP_T   = 'n', dict(r=1,c=3)
        WALL_R_OPEN_B_CORNER_T  = 'o', dict(r=1,c=4)
        WALL_T_OPEN_LR          = 'p', dict(r=1,c=5)
        WALL_L_OPEN_B_CORNER_T  = 'q', dict(r=1,c=6)
        BLOCK_OPEN_TB           = 's', dict(r=1,c=8)
        BLOCK_OPEN_B            = 't', dict(r=1,c=9)
        BLOCK_OPEN_B_1          = 'A', dict(r=2,c=0)
        BLOCK_OPEN_B_2          = 'B', dict(r=2,c=1)
        BLOCK_OPEN_B_3          = 'C', dict(r=2,c=2)
        WALL_L_OPEN_TB_1        = 'E', dict(r=2,c=4)
        WALL_R_OPEN_TB_1        = 'G', dict(r=2,c=6)
        BLOCK_OPEN_BR_OWALL_L   = 'H', dict(r=2,c=7)
        BLOCK_OPEN_BRL          = 'I', dict(r=2,c=8)
        BLOCK_OPEN_BL_OWALL_R   = 'J', dict(r=2,c=9)
        WALL_TL_OPEN_TBR_TOP_T  = 'K', dict(r=3,c=0)
        WALL_TR_OPEN_TBL_TOP_T  = 'L', dict(r=3,c=1)
        WALL_T_OPEN_T           = 'M', dict(r=3,c=2)
        WALL_CORNER_TR_OPEN_TR  = 'O', dict(r=3,c=4)
        WALL_T_OPEN_LR_1        = 'P', dict(r=3,c=5)
        WALL_CORNER_TL_OPEN_TL  = 'Q', dict(r=3,c=6)
        BLOCK_OPEN_TBR          = 'R', dict(r=3,c=7)
        BLOCK_OPEN              = 'S', dict(r=3,c=8)
        BLOCK_OPEN_TBL          = 'T', dict(r=3,c=9)


        def __init__(self, char, kwargs):
            super().__init__(char, setDefault(kwargs, themes=BorderThemes))

    class WallThemes(SpriteTheme):
        BROWN = 'brown', dict(c=0,r=0)
        LIGHT_GREY = "light grey", dict(c=8,r=0)
        GREY_PATTERNED = "grey patterned", dict(c=16,r=0)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, src = RoomSourceFiles.WALLS))

    """
    adjpPJDV
    bekqQKEW
    cflrRLFX
    AgmsSMGv
    BhntTNHw
    CiouUOIx
    """
    class WallTiles(Sprite):
        VOID = ' ', dict(isVoid=True)

        TOP_END_LEFT                    = 'a', dict(c= 0,r= 0)
        BOT_END_LEFT                    = 'b', dict(c= 0,r= 1)
        MID_END_LEFT                    = 'c', dict(c= 0,r= 2)
        TOP_END_RIGHT                   = 'A', dict(c= 0,r= 3)
        BOT_END_RIGHT                   = 'B', dict(c= 0,r= 4)
        MID_END_RIGHT                   = 'C', dict(c= 0,r= 5)
        TOP_LEFT_CORNER_OVERLAP_SHALLOW = 'd', dict(c= 1,r= 0)
        TOP_LEFT_CORNER_SHALLOW         = 'e', dict(c= 1,r= 1)
        MID_LEFT_CORNER_SHALLOW         = 'f', dict(c= 1,r= 2)
        BOT_LEFT_CORNER_SHALLOW         = 'g', dict(c= 1,r= 3)
        TOP_LEFT_EXTRUDE                = 'h', dict(c= 1,r= 4)
        BOT_LEFT_EXTRUDE                = 'i', dict(c= 1,r= 5)
        TOP_LEFT_CORNER                 = 'j', dict(c= 2,r= 0)
        BOT_LEFT_CORNER                 = 'k', dict(c= 2,r= 1)
        LEFT                            = 'l', dict(c= 2,r= 2)
        TOP_LEFT_ISLAND                 = 'm', dict(c= 2,r= 3)
        BOT_LEFT_ISLAND                 = 'n', dict(c= 2,r= 4)
        LEFT_BOT_CORNER                 = 'o', dict(c= 2,r= 5)
        TOP_LEFT_CORNER_OVERLAP         = 'p', dict(c= 3,r= 0)
        LEFT_BOT_CORNER_OVERLAP         = 'q', dict(c= 3,r= 1)
        TOP                             = 'r', dict(c= 3,r= 2)
        BOT                             = 's', dict(c= 3,r= 3)
        MID_END                         = 't', dict(c= 3,r= 4)
        BOT_B                           = 'u', dict(c= 3,r= 5)
        TOP_RIGHT_CORNER_OVERLAP        = 'P', dict(c= 4,r= 0)
        BOT_RIGHT_CORNER_OVERLAP        = 'Q', dict(c= 4,r= 1)
        TOP_1                           = 'R', dict(c= 4,r= 2)
        BOT_1                           = 'S', dict(c= 4,r= 3)
        MID                             = 'T', dict(c= 4,r= 4)
        BOT_B_1                         = 'U', dict(c= 4,r= 5)
        TOP_RIGHT_CORNER                = 'J', dict(c= 5,r= 0)
        BOT_RIGHT_CORNER                = 'K', dict(c= 5,r= 1)
        RIGHT                           = 'L', dict(c= 5,r= 2)
        TOP_RIGHT_ISLAND                = 'M', dict(c= 5,r= 3)
        BOT_RIGHT_ISLAND                = 'N', dict(c= 5,r= 4)
        RIGHT_BOT_CORNER                = 'O', dict(c= 5,r= 5)
        TOP_RIGHT_CORNER_OVERLAP_SHALLOW= 'D', dict(c= 6,r= 0)
        TOP_RIGHT_CORNER_SHALLOW        = 'E', dict(c= 6,r= 1)
        MID_RIGHT_CORNER_SHALLOW        = 'F', dict(c= 6,r= 2)
        BOT_RIGHT_CORNER_SHALLOW        = 'G', dict(c= 6,r= 3)
        TOP_RIGHT_EXTRUDE               = 'H', dict(c= 6,r= 4)
        BOT_RIGHT_EXTRUDE               = 'I', dict(c= 6,r= 5)
        TOP_RIGHT_ISLAND_SHALLOW        = 'V', dict(c= 7,r= 0)
        MID_RIGHT_ISLAND_SHALLOW        = 'W', dict(c= 7,r= 1) 
        BOT_RIGHT_ISLAND_SHALLOW        = 'X', dict(c= 7,r= 2)
        TOP_LEFT_ISLAND_SHALLOW         = 'v', dict(c= 7,r= 3)
        MID_LEFT_ISLAND_SHALLOW         = 'w', dict(c= 7,r= 4) 
        BOT_LEFT_ISLAND_SHALLOW         = 'x', dict(c= 7,r= 5)

        def __init__(self, char, kwargs):
            super().__init__(char, setDefault(kwargs, themes=WallThemes))

    class DoorThemes(SpriteTheme):
        GLASS_LEFT = "glass left", dict(src=DoorSourceFiles.GLASS_LEFT)
        GLASS_RIGHT = "glass right", dict(src=DoorSourceFiles.GLASS_RIGHT)

    class DoorSprites(Sprite):
        VOID = ' ', dict(isVoid=True)

        OPEN = "open", dict(c=4)
        CLOSED = "closed", dict(c=0)
        OPENING = "opening", dict(c=0, f=4)
        CLOSING = "closing", dict(c=4, f=4)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs, h=IMAGE_SIZE*3, themes=DoorThemes, anchory=IMAGE_SIZE*2))

    class CharacterThemes(SpriteTheme):
        PREMADE_17 = 'premade 17', dict(src=CharacterSourceFiles.CHARACTER_PREMADE_17)

        def __init__(self, tag, kwargs):
            super().__init__(tag, setDefault(kwargs)) 

    class CharacterAnimations(Sprite):
        VOID = ' ', dict(isVoid=True)

        DEFAULT     = "default",        dict()
        IDLE        = "idle",           dict(f=6, r=1)
        WALK        = "walk",           dict(f=6, r=2)
        SLEEP       = "sleep",          dict(f=6, r=3, right=0, up=0, left=0, down=0)
        SITTING     = "sitting",        dict(f=6, r=4, right=0, up=0, left=1, down=1)
        SIT         = "sit",            dict(f=6, r=5, right=0, up=0, left=1, down=1)
        PHONE       = "phone",          dict(f=12, r=6, right=0, up=0, left=0, down=0)
        PHONE_START = "phone start",    dict(f=3, r=6, right=0, up=0, left=0, down=0)
        PHONE_LOOP  = "phone loop",     dict(f=6, r=6, c=3, right=0, up=0, left=0, down=0)
        PHONE_END   = "phone end",      dict(f=3, r=6, c=9, right=0, up=0, left=0, down=0)
        BOOK        = "book",           dict(f=12, r=7, right=0, up=0, left=0, down=0)
        BOOK_LOOP   = "book loop",      dict(f=6, r=7, right=0, up=0, left=0, down=0)
        BOOK_FLIP   = "book flip",      dict(f=6, r=7, right=0, up=0, left=0, down=0)
        PUSH_TROLLEY= "push_trolley",   dict(f=6, r=8)
        # TROLLEY     = "trolley",        dict(f=3, r=8, c=12, width=IMAGE_SIZE*2, yoffset=IMAGE_SIZE, xoffset=IMAGE_SIZE)
        PICK_UP     = "pick_up",        dict(f=12, r=9)
        GIFT        = "gift",           dict(f=10, r=10)
        LIFT        = "lift",           dict(f=14, r=11)
        THROW       = "throw",          dict(f=14, r=12)
        HIT         = "hit",            dict(f=6, r=13)
        PUNCH       = "punch",          dict(f=6, r=14)
        STAB        = "stab",           dict(f=6, r=15)
        KNIFE       = "knife",          dict(f=6, r=15, c=24)
        GUN_GRAB    = "gun grab",       dict(f=4, r=16)
        GUN_IDLE    = "gun idle",       dict(f=6, r=17)
        GUN_SHOOT   = "gun shoot",      dict(f=3, r=18)
        HURT        = "hurt",           dict(f=3, r=19)

        def __init__(self, tag, kwargs):
            kwargs = setDefault(kwargs, themes=CharacterThemes, r=0, h=2*IMAGE_SIZE, none=0, right=0, up=1, left=2, down=3)
            kwargs['r'] *= 2
            super().__init__(tag, kwargs) 

    class SpriteRenderHandler:
        def __init__(self, sprite):
            self.frame = 0
            self.theme = VoidTheme.VOID
            self.direction = Direction.NONE
            self.dir_offset = sprite.directional_offsets[self.direction]
            self.displayable = None
            self.sprite = sprite

        def build(self, frame=0, theme=VoidTheme.VOID, direction=Direction.NONE, position=(0,0)):
            self.sprite, self.theme, self.direction, self.dir_offset, self.frame, pos, change = self.subBuild(frame, theme, direction, position)
            if change: 
                self.displayable = self.sprite.buildStatic(self.theme,self.frame,self.direction,nullable=False)
            return (self.sprite.position(pos), self.displayable), change

        def subBuild(self, frame, theme, direction, position):
            return (position, None), False

    class StaticSpriteRenderHandler(SpriteRenderHandler):
        def __init__(self, sprite):
            super().__init__(sprite)
            self.isNone = sprite.themes == VoidTheme
            self.notDynamic = sprite.frames <= 1 and len(sprite.themes) <= 1
            if self.notDynamic:
                for i in list(Direction):
                    if sprite.directional_offsets[i] != self.dir_offset:
                        self.notDynamic = False
                        break
        
        def subBuild(self, frame, theme, direction, position):
            if self.notDynamic and (self.isNone or self.displayable != None):
                return self.sprite, self.theme, self.direction, self.dir_offset, self.frame, position, False
            frame %= self.sprite.frames
            dir_offset = self.sprite.directional_offsets[direction]
            same = (theme,frame,dir_offset) == (self.theme,self.frame,self.dir_offset) and self.displayable is not None
            return self.sprite, theme, direction, dir_offset, frame, position, (not same)
    
    class DynamicSpriteRenderHandler(SpriteRenderHandler):
        def __init__(self, default=StaticSpriteTiles.VOID, getTheme=None, getFrame=None, getDirection=None, getSprite=None, getPosition=None, **kwargs):
            super().__init__(default)
            self.default = default
            self.getTheme = getTheme
            self.getFrame = getFrame
            self.getDirection = getDirection
            self.getSprite = getSprite
            self.getPosition = getPosition
            self.kwargs = kwargs
        
        def subBuild(self, frame, theme, direction, position=(0,0)):
            s = self.default if self.getSprite is None else self.getSprite(**self.kwargs)
            if s == None: s = self.default
            t = theme if self.getTheme is None else self.getTheme(sprite=s, **self.kwargs)
            d = direction if self.getDirection is None else self.getDirection(sprite=s, theme=t, **self.kwargs)
            f = frame if self.getFrame is None else self.getFrame(sprite=s, theme=t, direction=d, **self.kwargs)
            p = position if self.getPosition is None else self.getPosition(sprite=s, theme=t, direction=d, frame=f, **self.kwargs)
            dir_offset = s.directional_offsets[d]
            f %= s.frames
            same = (s,t,dir_offset,f) == (self.sprite, self.theme, self.dir_offset, self.frame) and self.displayable is not None
            return s, t, d, dir_offset, f, p, (not same)

    class Director:
        def __init__(self, dt=None):
            self.dt = dt
            self.running = True
        
        def resume(self):
            self.running = True
            return self

        def pause(self):
            self.running = False
            return self

        def onLoop(self, trans, st, at):
            if not self.running: return
            self.onLoopSub(trans, st, at)
        
        def onLoopSub(self, trans, st, at):
            pass

    DEFAULT_DISPLAYABLE = Null()

    class AnimationDirector(Director):
        def __init__(self, getPosition=None, x=0,y=0,r=0,c=0):
            super().__init__(FRAME_LENGTH)
            self.theme = VoidTheme.VOID
            self.frame = 0
            self.dir = Direction.NONE
            self.anims = []
            self.position = (x + c*IMAGE_SIZE, y + r*IMAGE_SIZE)
            self.getPos = getPosition
            self.finishing = False
            self.handler = DynamicSpriteRenderHandler(
                getTheme=self.getTheme, 
                getFrame=self.getFrame, 
                getDirection=self.getDirection, 
                getSprite=self.getSprite, 
                getPosition=self.getPosition
            )
            self.listener = None
            self.listenerKwargs = dict()
        
        def getPosition(self, **kwargs):
            if self.getPos is not None:
                return self.getPos()
            else:
                return self.position

        def getHandler(self):
            return self.handler

        def getDirection(self, **kwargs):
            return self.dir

        def getFrame(self, **kwargs):
            return self.frame

        def getTheme(self, **kwargs):
            return self.theme

        def getSprite(self, **kwargs):
            return (self.anims[0] if len(self.anims) > 0 else StaticSpriteTiles.VOID)

        def setDirection(self, direction):
            self.dir = direction
            return self
        
        def setTheme(self, theme):
            self.theme = theme
            return self

        def setAnimations(self, *anims):
            self.onCompleteAnim(self.getSprite(), False)
            self.anims = list(anims)
            self.frame = 0
            self.onStartAnim()
            return self
        
        def addAnimations(self, *anims):
            self.anims += list(anims)
            return self
        
        def reset(self):
            self.onCompleteAnim(False)
            self.frame = 0
            self.onStartAnim()
            return self

        def onCompleteAnim(self, anim, finished=False):
            if self.finishing:
                return
            self.finishing = True
            if self.listener is not None:
                self.listener(anim, start=False, complete=True, finished=finished, **self.listenerKwargs)
            self.finishing = False

        def onStartAnim(self):
            if self.finishing:
                return
            anim = self.getSprite()
            if self.listener is not None:
                self.listener(anim, start=True, complete=False, **self.listenerKwargs)

        def setListener(self, listener=None, **kwargs):
            self.listener=listener
            self.listenerKwargs = kwargs
            return self

        def clearListener(self):
            self.setListener()
            return self

        def interupt(self, anim):
            oldanim = self.getSprite()
            self.anims.insert(0,anim)
            self.onCompleteAnim(oldanim, False)
            self.frame = 0
            self.onStartAnim()
            return self

        def incrementFrames(self, frames=1):
            anim = self.getSprite()
            frame = self.frame + frames
            if not anim is None:
                frame %= anim.frames
            if frame < self.frame:
                if len(self.anims) > 1:
                    self.anims.pop(0)
                self.onCompleteAnim(anim, True)
                self.onStartAnim()
                self.frame = 0
            else:
                self.frame = frame
            return self

        def onLoopSub(self, trans, st, at):
            self.incrementFrames()

    renpy.add_layer("above", above="master")
    renpy.add_layer("dynamic", above="master")
    renpy.add_layer("below", above="master")

    class MapReferenceLayer(Enum):
        DYNAMIC=0
        ABOVE=1,
        BELOW=2

    class MapReference:
        def __init__(self, m, handler, layer, refId):
            self.map = m
            self.handler = handler
            self.layer = layer
            self.refId = refId
            self.active = True
        
        def remove(self):
            m.removeReference(self)
    

    class InteractingType(Flag):
        NONE                = 0
        STATIC              = auto()
        ENTER               = auto()
        ON                  = STATIC | ENTER
        LEAVE               = auto()
        KEY_PRESSED         = auto()
        KEY_STATIC_DOWN     = auto()
        KEY_DOWN            = KEY_PRESSED | KEY_STATIC_DOWN
        KEY_RELEASE         = auto()
        COLLISION           = auto()
        BEFORE_ANIMATION    = auto()
        AFTER_ANIMATION     = auto()

    class Interactions(Enum):
        VOID        = ' ', dict(w=True)
        WALL        = '0', dict(w=False)
        LDOOR_L     = 'l', dict(d=Direction.LEFT, sub_d=Direction.LEFT, isDoor=True)
        LDOOR_R     = 'L', dict(d=Direction.LEFT, sub_d=Direction.RIGHT, isDoor=True)
        RDOOR_L     = 'r', dict(d=Direction.RIGHT, sub_d=Direction.LEFT, isDoor=True)
        RDOOR_R     = 'R', dict(d=Direction.RIGHT, sub_d=Direction.RIGHT, isDoor=True)
        I_LDOOR_L   = 'i', dict(w=True, d=Direction.LEFT, sub_d=Direction.LEFT, isDoorInteract=True)
        I_LDOOR_R   = 'I', dict(w=True, d=Direction.LEFT, sub_d=Direction.RIGHT, isDoorInteract=True)
        I_RDOOR_L   = 'j', dict(w=True, d=Direction.RIGHT, sub_d=Direction.LEFT, isDoorInteract=True)
        I_RDOOR_R   = 'J', dict(w=True, d=Direction.RIGHT, sub_d=Direction.RIGHT, isDoorInteract=True)
        NAV_LEFT    = 'n', dict(w=True, d=Direction.LEFT, isNavPoint=True)
        NAV_RIGHT   = 'N', dict(w=True, d=Direction.RIGHT, isNavPoint=True)
        CLOSE_L     = 'c', dict(w=True, d=Direction.LEFT, isDoorClose=True)
        CLOSE_R     = 'C', dict(w=True, d=Direction.RIGHT, isDoorClose=True)

        def __new__(cls, char, *args):
            obj = builtins.object.__new__(cls)
            obj._value_ = char
            return obj

        def __init__(self, char, kwargs):
            self.__setup(**kwargs)

        def __setup(self, w=None, d=Direction.NONE, sub_d = Direction.NONE, isDoor=False, isDoorInteract=False, isNavPoint=False, isDoorClose=False):
            self.walkable = w
            self.isDoor = isDoor
            self.isDoorInteract = isDoorInteract
            self.direction = d
            self.subDirection = sub_d
            self.isNavPoint = isNavPoint
            self.isDoorClose = isDoorClose

        def door(self):
            return doors[self.direction]

        def isWalkable(self, clipping=False):
            if self.isDoor:
                return self.door().isOpen(self.subDirection, clipping=clipping)
            return self.walkable

        def interact(self, intType, interactionID=None, **kwargs):
            if self.isDoorInteract:
                return self.door().interact(self.subDirection, intType, interactionID, **kwargs)
            elif self.isNavPoint:
                return doors.navigate(self.direction, intType, interactionID, **kwargs)
            elif self.isDoorClose:
                return self.door().closeInteraction(intType, interactionID, **kwargs)
            else:
                return False

    MAP_FRAME_RATE = 0.03

    class Map(Director):

        def __init__(self):
            super().__init__(FRAME_LENGTH)
            self.dynams = dict()
            self.frame = 0

        def init(self, rows, columns, b=None, d=None, a=None, i=None, s=(0,0), t=dict()):
            self.rows = rows
            self.columns = columns
            self.belows = b
            self.aboves = a
            self.startLocation = s
            if d is not None:
                self.dynams = d
            self.interactions = i
            self.themes = t
            self.belowDis = DynamicDisplayable(self.build, MapReferenceLayer.BELOW)
            self.aboveDis = DynamicDisplayable(self.build, MapReferenceLayer.ABOVE)
            self.dynamDis = DynamicDisplayable(self.build, MapReferenceLayer.DYNAMIC)

        def addToLayer(self, layerRef, i=0, j=0, sprite=None, handler=None, refId=""):
            if layerRef == MapReferenceLayer.DYNAMIC:
                return self.addDynamic(handler, refId)
            layer = self.belows if layerRef == MapReferenceLayer.BELOW else self.aboves if layerRef == MapReferenceLayer.ABOVE else None
            if layer is None: None
            if handler is None: handler = sprite.buildStaticHandler()
            ref = MapReference(self, handler, layerRef, (i,j))
            layer.append([(i,j,handler)])
            return ref
        
        def addDynamic(self, handler, refId):
            ref = MapReference(self, handler, MapReferenceLayer.DYNAMIC, refId)
            self.dynams[refId] = handler
            return ref

        def removeReference(self, ref):
            if not ref.active:
                return
            ref.active = False
            if ref.layer == MapReferenceLayer.BELOW:
                self.belows[ref.refId[0]][ref.refId[1]].remove(ref.handler)
            elif ref.layer == MapReferenceLayer.ABOVE:
                self.aboves[ref.refId[0]][ref.refId[1]].remove(ref.handler)
            elif ref.layer == MapReferenceLayer.DYNAMIC:
                self.dynams.pop(ref.refId)

        def getLayer(self, layerRef):
            if layerRef == MapReferenceLayer.BELOW:
                return self.belowDis
            elif layerRef == MapReferenceLayer.ABOVE:
                return self.aboveDis
            elif layerRef == MapReferenceLayer.DYNAMIC:
                return self.dynamDis

        def getTheme(self, handler):
            if handler.sprite.themes is None:
                return StaticSpriteThemes.NONE
            if handler.sprite.themes in self.themes:
                return self.themes[handler.sprite.themes]
            return list(handler.sprite.themes)[0]

        def getInteraction(self, i, j):
            return self.interactions[i][j]

        def setInteraction(self, i, j, interaction):
            self.interactions[i][j] = interaction

        def getStartLocation(self):
            return self.startLocation

        def build(self, st, at, layerRef):
            if layerRef == MapReferenceLayer.DYNAMIC:
                return self.buildDynamics(st, at)

            layer = self.belows if layerRef == MapReferenceLayer.BELOW else self.aboves if layerRef == MapReferenceLayer.ABOVE else None
            if layer is None: return Null(), None
            
            compose = []
            for l in layer:
                for i,j,handler in l:
                    offset = (j * IMAGE_SIZE, i * IMAGE_SIZE)
                    img,change = handler.build(
                        theme=self.getTheme(handler),
                        frame=self.frame,
                        position = offset
                    )
                    if img is None or img[1] is None: continue
                    compose.extend(img)
            return Composite((self.columns * IMAGE_SIZE, self.rows*IMAGE_SIZE), *compose), MAP_FRAME_RATE
        
        def buildDynamics(self, st, at):
            compose = []
            for refId in self.dynams:
                handler = self.dynams[refId]
                img,change = handler.build(frame=self.frame)
                if img is None or img[1] is None: continue
                compose.extend(img)
            return Composite((self.columns * IMAGE_SIZE, self.rows*IMAGE_SIZE), *compose), MAP_FRAME_RATE


        def onLoopSub(self, trans, st, at):
            self.frame += 1

        def getCollisions(self, px, py, pw, ph, fromCollisions=set()): 
            x = px / IMAGE_SIZE
            y = py / IMAGE_SIZE
            x2 = (px + pw) / IMAGE_SIZE
            y2 = (py + ph) / IMAGE_SIZE
            
            tl = int(x),int(y)
            br = int(x2), int(y2)
            collisions = set()
            walkable = True
            for i in range(tl[1], min(br[1]+1, self.rows)):
                for j in range(tl[0], min(br[0]+1, self.columns)):
                    inter = self.interactions[i][j]
                    if inter == Interactions.VOID:
                        continue
                    clipping = (i,j,inter) in fromCollisions
                    walkable &= inter.isWalkable(clipping=clipping)
                    collisions.add((i,j,inter))
            
            return collisions, walkable

    class MapFactory:
        def __init__(self, rows, columns):
            self.rows = rows
            self.columns = columns
            self.belows = []
            self.aboves = []
            self.startLocation = (0,0)
            self.themes = dict()
            self.interactions = [[Interactions.VOID for _ in range(columns)] for _ in range(rows)]

        def addBelowLayer(self, fromCls, *values):
            self.__addLayer(self.belows, *values, fromCls=fromCls)
            return self
        
        def addAboveLayer(self, fromCls, *values):
            self.__addLayer(self.aboves, *values, fromCls=fromCls)
            return self
        
        def addAbove(self, i, j, sprite):
            self.aboves.append([(i,j,sprite)])
            return self
        
        def addBelow(self, i, j, sprite):
            self.belows.append([(i,j,sprite)])
            return self

        def __addLayer(self, layer, *values, fromCls=None):
            l = []
            for i in range(self.rows):
                for j in range(self.columns):
                    img = None
                    if fromCls is not None:
                        img = fromCls(values[i][j])
                    else:
                        img = values[i][j]
                    if img.themes != VoidTheme and not img.isVoid:
                        l.append((i,j,img))
            layer.append(l)

        def setStartLocation(self, x=0,y=0,r=0,c=0):
            self.startLocation = (x + c * IMAGE_SIZE, y + r * IMAGE_SIZE)
            return self

        def setInteractions(self, *values):
            for i in range(self.rows):
                for j in range(self.columns):
                    self.interactions[i][j] = Interactions(values[i][j])
            return self

        def setThemes(self, *values):
            for i in values:
                self.themes[i.__class__] = i
            return self

        def build(self, m=None):
            if m is None:
                m = Map()
            
            belows = [[(i,j,sprite.buildStaticHandler()) for (i,j,sprite) in layer] for layer in self.belows]
            aboves = [[(i,j,sprite.buildStaticHandler()) for (i,j,sprite) in layer] for layer in self.aboves]

            m.init(
                self.rows, self.columns, 
                i=self.interactions, 
                b=belows,
                a=aboves,
                s=self.startLocation,
                t=self.themes
            )
            return m



    class MovementDirector(Director):
        def __init__(self, m):
            super().__init__(0.02)
            self.x = 4 * IMAGE_SIZE
            self.y = 4 * IMAGE_SIZE
            self.speed = 0
            self.dirs = []
            self.map = m
            self.cxoffset = 0
            self.cyoffset = 0
            self.cwidth = IMAGE_SIZE
            self.cheight = IMAGE_SIZE

            self.resetCollList = False
            self.lastOn = set()
            self.on = set()
            self.collisions = set()

        def setDirection(self, *dirs):
            self.dirs = list(dirs)
        
        def setSpeed(self, pixelsPerSecond=0):
            self.speed = pixelsPerSecond
        
        def setCollisionBox(self, xoffset = 0, yoffset = 0, width = IMAGE_SIZE, height = IMAGE_SIZE):
            self.cxoffset = int(xoffset)
            self.cyoffset = int(yoffset)
            self.cwidth = int(width)
            self.cheight = int(height)
            return self

        def getPosition(self, **kwargs):
            return int(self.x), int(self.y)

        def reset(self, m):
            self.map = m if m is not None else self.map
            self.x, self.y = self.map.getStartLocation()
            self.dirs = set()
            self.lastOn = set()
            self.on = set()
            self.collisions = set()
            self.resetCollList = False

        def fetchInteractions(self, reset=False):
            c = self.collisions.copy()
            l = self.lastOn.copy()
            o = self.on.copy()
            if reset:
                self.collisions = set()
                self.lastOn = self.on
                self.on = set()
                self.resetCollList = True
            return c,l,o

        def move(self):
            sx = sy = 0
            s = self.speed * self.dt
            if self.speed != 0:
                if Direction.UP in self.dirs:
                    sy -= s
                if Direction.DOWN in self.dirs:
                    sy += s
                if Direction.RIGHT in self.dirs:
                    sx += s
                if Direction.LEFT in self.dirs:
                    sx -= s

                if sx != 0 and sy != 0:
                    sx *= 0.7
                    sy *= 0.7
            
            newx = self.x + sx
            newy = self.y + sy
            
            c,w = self.map.getCollisions(newx + self.cxoffset, newy + self.cyoffset, self.cwidth, self.cheight, fromCollisions=(self.lastOn if self.resetCollList else self.on))
            
            o = set()
            if w:
                self.x = newx
                self.y = newy
                o = c
                c = set()
            else:
                c = c - o

            self.on |= o
            self.collisions |= c

        def __getInteracting(self):
            return self.map.getCollisions(self.x + self.cxoffset, self.y + self.cyoffset, self.cwidth, self.cheight)[0]

        def onLoopSub(self, trans, st, at):
            self.move()
            trans.pos = (int(self.x), int(self.y))
            return None
    
    class Keyboard(Enum):
        ANY = 0
        MOVE_LEFT = 1, 'a'
        MOVE_RIGHT = 2, 'd'
        MOVE_UP = 3, 'w'
        MOVE_DOWN = 4, 's'
        INTERACT = 5, 'e'

        def __new__(cls, key, *args):
            obj = builtins.object.__new__(cls)
            obj._value_ = key
            return obj

        def __init__(self, val, *keys):
            self.keys = keys
            self.reset_key()
        
        def reset_key(self):
            self.isDown = None
            self.viewedSinceChange = set()

        @classmethod
        def reset(cls):
            for k in list(cls):
                k.reset_key()
        
        @classmethod
        def _missing_(cls, key):
            for k in list(cls):
                if key in k.keys:
                    return k
            return KeyInputs.ANY

        def __view(self, viewedBy):
            if viewedBy is not None:
                self.viewedSinceChange.add(viewedBy)

        def down(self, viewedBy=None):
            self.__view(viewedBy)
            return self.isDown is True

        def up(self, viewedBy=None):
            return not self.down(viewedBy)

        def static(self, viewedBy=None):
            b = viewedBy in self.viewedSinceChange or self.isDown is None
            self.__view(viewedBy)
            return b

        def changed(self, viewedBy=None):
            return not self.static(viewedBy)
            
        def pressed(self, viewedBy=None):
            return self.changed(viewedBy) and self.down()

        def released(self, viewedBy=None):
            return self.changed(viewedBy) and self.up()

        def setIsDown(self, isDown):
            self.isDown = isDown
            self.viewedSinceChange.clear()

        @staticmethod
        def action(up=False, down=False, key=''):
            Keyboard(key).setIsDown(False if up else down)
            Keyboard.ANY.setIsDown(False if up else down)

    class CharacterDirector(Director):
        def __init__(self, movementDirector, animationDirector):
            super().__init__(0.02)
            self.move = movementDirector
            self.anim = animationDirector
            self.facing = Direction.DOWN
            self.move.setSpeed(IMAGE_SIZE * 3)
            self.anim.setDirection(self.facing)
            self.moving = False
            self.dirs = set()
            self.disableKeyPress = False
            self.anim.setAnimations(CharacterAnimations.IDLE)
            self.interactions = 0
            self.interacting = set(),set(),set()
    
        def onLoopSub(self, trans, st, at):
            if self.disableKeyPress:
                return

            dirs = set()
            face = self.facing
            moving = False
            if Keyboard.MOVE_LEFT.down():
                face = Direction.LEFT
                moving=True
                dirs.add(face)
            elif Keyboard.MOVE_RIGHT.down():
                face = Direction.RIGHT
                moving=True
                dirs.add(face)
            if Keyboard.MOVE_UP.down():
                face = Direction.UP
                moving=True
                dirs.add(face)
            elif Keyboard.MOVE_DOWN.down():
                face = Direction.DOWN
                moving=True
                dirs.add(face)

            self.interacting = self.move.fetchInteractions(True)
            c = Keyboard.INTERACT.changed("player")
            d = Keyboard.INTERACT.down("player")
            t2 = InteractingType.KEY_PRESSED if c and d else (
                    InteractingType.KEY_RELEASE if c else (
                        InteractingType.KEY_STATIC_DOWN if d else InteractingType.NONE
                    )
                )

            showInteractionAnimation = self.__runInteractions(InteractingType.BEFORE_ANIMATION | t2, True)

            if showInteractionAnimation:
                self.anim.interupt(CharacterAnimations.HIT)
                self.disableKeyPress = True
                self.anim.setListener(self.onAnimationTrigger, action="interaction")

            if dirs == self.dirs:
                return

            self.dirs = dirs
            self.move.setDirection(*self.dirs)

            if not self.facing in self.dirs:
                self.facing = face
                self.anim.setDirection(self.facing)

            if not moving and self.moving:
                self.anim.setAnimations(CharacterAnimations.IDLE)
            elif moving and not self.moving:
                self.anim.setAnimations(CharacterAnimations.WALK)
            
            self.moving = moving

        def queryCollision(self):
            return self.interacting

        def cutscene(self, direction=Direction.NONE, start=True):
            if start:
                self.disableKeyPress = True
                self.dirs = []
                self.facing = direction
                self.anim.setAnimations(CharacterAnimations.WALK)
                self.move.setDirection(direction)
                self.anim.setDirection(direction)
                self.moving = True
            else:
                self.disableKeyPress = False
                self.dirs = []
                self.anim.setAnimations(CharacterAnimations.IDLE)
                self.move.setDirection()
                self.moving = False

        def reset(self, m=None):
            self.anim.setAnimations(CharacterAnimations.IDLE)
            self.dirs = set()
            self.facing = Direction.UP
            self.anim.setDirection(self.facing)
            self.interactions = 0
            self.move.reset(m)
            self.moving = False
            self.disableKeyPress = False

        def __runInteractions(self, baseType=InteractingType.NONE, withCollisions=False, isInteraction=False):
            showInteractionAnimation = False
            self.interactions += 1
            collisions, lastOn, on = self.interacting

            t1 = baseType

            for x,y,i in on:
                t4 = InteractingType.STATIC if (x,y,i) in lastOn else InteractingType.ENTER 
                showInteractionAnimation = i.interact(t1 | t4, interactionID=("player", self.interactions)) or showInteractionAnimation

            for x,y,i in lastOn - on:
                t4 = InteractingType.LEAVE
                showInteractionAnimation = i.interact(t1 | t4, interactionID=("player", self.interactions)) or showInteractionAnimation

            if withCollisions:
                for x,y,i in collisions - on:
                    t4 = InteractingType.COLLISION
                    showInteractionAnimation = i.interact(t1 | t4, interactionID=("player", self.interactions)) or showInteractionAnimation
            
            return showInteractionAnimation

        def onAnimationTrigger(self, anim, start=False, complete=False, finished=False, action=None, **kwargs):
            if not complete:
                return
            if action != "interaction":
                return
            self.anim.clearListener()
            self.disableKeyPress = False
            self.interactions += 1
            self.__runInteractions(InteractingType.AFTER_ANIMATION | InteractingType.KEY_PRESSED)
    
    
    class Params(Flag):
        NONE = 0
        IS_INTERACT                     = auto()
        HAS_OPEN_ANIM                   = auto()
        PLAYER_HAS_OPEN_ANIM            = auto()
        IS_OPEN_BEFORE_ANIM             = auto()
        START_OPEN_AFTER_PLAYER_ANIM    = auto()
        IS_PORTAL                       = auto()
        CAN_OPEN_INDIVIDUAL             = auto()
        CAN_OPEN_INDIVIDUAL_BOTH        = auto() 
        TOGGLES_INDIVIDUAL              = auto() 
        CAN_CLOSE                       = auto()
        IS_CLOSED_BEFORE_ANIM           = auto()
        CLIP_IF_COLLIDING               = auto() 
        NO_CLOSE_ON_COLLIDING           = auto() 
        HAS_COOLDOWN                    = auto()
        CLOSE_BEHIND                    = auto()
        CUTSCENE                        = auto()
        LOADING_SCREEN                  = auto() 
        DEFAULT = IS_PORTAL | HAS_OPEN_ANIM | CLIP_IF_COLLIDING | LOADING_SCREEN

    class DoorStates(Enum):
        CLOSED = 0, True, False, DoorSprites.CLOSED
        CLOSING = 1, True, False, DoorSprites.CLOSING
        OPENING = 2, False, True, DoorSprites.OPENING
        OPEN = 3, False, True, DoorSprites.OPEN

        def __new__(cls, val, *args):
            obj = builtins.object.__new__(cls)
            obj._value_ = val
            return obj

        def __init__(self, val, closeState, openState, *anims):
            self.anims = anims
            self.isCloseState = closeState
            self.isOpenState = openState


    class Doors(Director):
        def __init__(self):
            super().__init__(FRAME_LENGTH)
            self.params = Params.DEFAULT
            self.left = Door(Direction.LEFT, self.params)
            self.right = Door(Direction.RIGHT, self.params)
        
        def __getitem__(self, side):
            if side == Direction.LEFT:
                return self.left
            elif side == Direction.RIGHT:
                return self.right
            raise KeyError(f"{side} is not a valid door direction")

        def __default(self, label="", add=Params.NONE, remove=Params.NONE, toggle=Params.NONE):
            return label,add,remove,toggle
        
        def __setitem__(self, side, val):
            label,add,remove,toggle = self.__default(*val)
            params = ((self.params | add) & (~remove)) ^ toggle
            self[side].reset(label, params)
                

        def onLoopSub(self, trans, st, at):
            self.left.onLoop(trans, st, at)
            self.right.onLoop(trans, st, at)

        def navigate(self, side, intType=InteractingType.NONE, interactionID=None, **kwargs):
            if not InteractingType.ENTER in intType or room.navigating:
                return False
            self.params = self[side].params
            renpy.jump(self[side].label)
            return False
    
    DOOR_COOLDOWN = 1.0

    class Door(Director):

        def __init__(self, side: Direction, params = Params.DEFAULT):
            super().__init__(FRAME_LENGTH)
            self.side = side
            self.params = params
            self.label=""
            self.states = {
                Direction.LEFT: DoorStates.CLOSED,
                Direction.RIGHT: DoorStates.CLOSED
            }
            o = 2
            if side == Direction.RIGHT:
                o = 10
            self.anims = {
                Direction.LEFT: AnimationDirector(r=4,c=o).setTheme(DoorThemes.GLASS_LEFT),
                Direction.RIGHT: AnimationDirector(r=4,c=o+1).setTheme(DoorThemes.GLASS_RIGHT)
            }
            self.anims[Direction.LEFT].setListener(self.onAnimationTrigger, subSide=Direction.LEFT)
            self.anims[Direction.RIGHT].setListener(self.onAnimationTrigger, subSide=Direction.RIGHT)
            self.lastInteraction = dict()
            self.reset(self.label, self.params)
            self.sinceLast = 0

        def getPosition(self, **kwargs):
            return (0,0)

        def reset(self, label, params):
            self.label=label
            self.params = params
            self[Direction.LEFT] = DoorStates.CLOSED
            self[Direction.RIGHT] = DoorStates.CLOSED
            self.sinceLast = 0

        def __getitem__(self, side):
            return self.states[side]

        def __setitem__(self, side, state):
            if side not in self.states:
                raise KeyError(f"{side} is not a valid side")
            self.states[side] = state
            self.anims[side].setAnimations(*state.anims)

        def isOpen(self, subSide, clipping=False):
            return self[subSide] == DoorStates.OPEN or (
                    self[subSide] == DoorStates.OPENING and Params.IS_OPEN_BEFORE_ANIM in self.params
                ) or (
                    self[subSide] == DoorStates.CLOSING and not Params.IS_CLOSED_BEFORE_ANIM in self.params
                ) or (
                    clipping and Params.CLIP_IF_COLLIDING in self.params and self[subSide] == DoorStates.CLOSED
                )
        
        def interact(self, subSide, intType, interactionID=None, **kwargs):
            if InteractingType.COLLISION in intType: return False
            if Params.IS_INTERACT in self.params:
                if not InteractingType.KEY_PRESSED in intType: return False
                if Params.HAS_COOLDOWN in self.params and self.sinceLast > 0: return False
            else: 
                if not InteractingType.ENTER in intType: return False
            
            anim = Params.PLAYER_HAS_OPEN_ANIM in self.params
            if anim and Params.START_OPEN_AFTER_PLAYER_ANIM in self.params and not InteractingType.AFTER_ANIMATION in intType:
                return True
            if anim and not Params.START_OPEN_AFTER_PLAYER_ANIM in self.params and not InteractingType.BEFORE_ANIMATION in intType:
                return True
            if interactionID is not None:
                if interactionID[0] in self.lastInteraction and interactionID[1] == self.lastInteraction[interactionID[0]]:
                    if not Params.CAN_OPEN_INDIVIDUAL_BOTH in self.params:
                        return anim
                    if self[Direction.LEFT].isOpenState == self[Direction.RIGHT].isOpenState and not Params.TOGGLES_INDIVIDUAL in self.params:
                        return anim
                self.lastInteraction[interactionID[0]] = interactionID[1]
            
            if Params.NO_CLOSE_ON_COLLIDING in self.params and self[subSide] == DoorStates.OPEN:
                coll = player.queryCollision()[2]
                if len([i for x,y,i in coll if i.isDoor and i.direction == self.side]) > 0:
                    return False
            
            self.sinceLast = DOOR_COOLDOWN

            if Params.CAN_OPEN_INDIVIDUAL in self.params:
                self.switchState(subSide)
            else:
                self.switchState(Direction.LEFT)
                self.switchState(Direction.RIGHT)

            return anim
        
        def closeInteraction(self, intType, interactionID=None, **kwargs):
            if Params.CLOSE_BEHIND not in self.params: return False
            if self[Direction.LEFT] == DoorStates.OPEN:
                self.switchState(Direction.LEFT)
            if self[Direction.RIGHT] == DoorStates.OPEN:
                self.switchState(Direction.RIGHT)
            return False

        def switchState(self, subSide):
            if self[subSide] == DoorStates.OPEN and Params.CAN_CLOSE in self.params:
                self[subSide] = DoorStates.CLOSING if Params.HAS_OPEN_ANIM in self.params else DoorStates.CLOSED
            elif self[subSide] == DoorStates.CLOSED:
                self[subSide] = DoorStates.OPENING if Params.HAS_OPEN_ANIM in self.params else DoorStates.OPEN

        def onAnimationTrigger(self, anim, start=False, complete=False, finished=False, subSide=Direction.NONE, **kwargs):
            if start and anim == DoorSprites.OPEN and Params.IS_PORTAL in self.params:
                doors.navigate(self.side, intType=InteractingType.ENTER)
                return

            if not finished:
                return

            if anim == DoorSprites.CLOSING:
                self[subSide] = DoorStates.CLOSED
                return
            elif anim == DoorSprites.OPENING:
                self[subSide] = DoorStates.OPEN
                return

        def onLoopSub(self, trans, st, at):
            self.anims[Direction.LEFT].onLoop(trans,st,at)
            self.anims[Direction.RIGHT].onLoop(trans,st,at)
            self.sinceLast -= FRAME_LENGTH
            self.sinceLast = max(0, self.sinceLast)

        def select(self):
            return ((self.params | self.add) & (~self.remove)) ^ self.toggle

    doors = Doors()
        
    thisMap = MapFactory(12,14).addBelowLayer(FloorTiles,
        "              ",
        "              ",
        "              ",
        "  34      34  ",
        "  34      34  ",
        " 024111111241 ",
        " 344444444444 ",
        " 344444444444 ",
        " 344444444444 ",
        " 3444 34 3444 ",
        " 3444 34 3444 ",
        "              "
    ).addBelowLayer(WallTiles,
        "              ",
        " jrRJ    jrRJ ",
        " k  K    k  K ",
        "jA  arrrrA  aJ",
        "kB  bssssB  bK",
        "l            L",
        "l            L",
        "l            L",
        "l            L",
        "l            L",
        "l            L",
        "ouuuu   uuuuuO"
    ).addBelowLayer(CondoInteriorTiles,
        "  rv      rv  ",
        "              ",
        "              ",
        "              ",
        "              ",
        "  M       M   ",
        "              ",
        "              ",
        "              ",
        "      wx      ",
        "              ",
        "              "
    ).addBelowLayer(CondoInteriorTiles,
        "  R       R   ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "      W       ",
        "              ",
        "              "
    ).addAboveLayer(WallTiles,
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "     h  H     ",
        "     i  I     ",
        "     i  I     ",
        "     ouuO     "
    ).addAboveLayer(StaticSpriteTiles,
        "  ss      ss  ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              ",
        "              "
    ).addBelowLayer(StaticSpriteTiles,
        "              ",
        "              ",
        "              ",
        "              ",
        "    o    O    ",
        "      f       ",
        "    122223    ",
        "              ",
        "           L  ",
        "              ",
        " c            ",
        "              "
    ).setInteractions(
        "00  000000  00",
        "00nn000000NN00",
        "00cc000000CC00",
        "00  000000  00",
        "00lL000000rR00",
        "0 iI  00  jJ 0",
        "0            0",
        "0            0",
        "0          000",
        "0    0  0  000",
        "0000 0  0    0",
        "00000000000000"
    ).setThemes(
        WallThemes.GREY_PATTERNED, 
        StairTopThemes.BROWN, 
        StairBotThemes.BROWN, 
        FloorMatThemes.DARK, 
        FloorThemes.BEIGE
    ).setStartLocation(r=9,c=6.5).build()
    playerMove = MovementDirector(thisMap).setCollisionBox(0, IMAGE_SIZE * 1.5, IMAGE_SIZE, IMAGE_SIZE * 0.5)
    playerAnim = AnimationDirector(playerMove.getPosition).setTheme(CharacterThemes.PREMADE_17)

    doorLeftAnimLeftRef = thisMap.addDynamic(doors[Direction.LEFT].anims[Direction.LEFT].getHandler(), "doorLeftAnimLeft")
    doorLeftAnimRightRef = thisMap.addDynamic(doors[Direction.LEFT].anims[Direction.RIGHT].getHandler(), "doorLeftAnimRight")
    doorRightAnimLeftRef = thisMap.addDynamic(doors[Direction.RIGHT].anims[Direction.LEFT].getHandler(), "doorRightAnimLeft")
    doorRightAnimRightRef = thisMap.addDynamic(doors[Direction.RIGHT].anims[Direction.RIGHT].getHandler(), "doorRightAnimRight")

    playerDisplayableReference = thisMap.addDynamic(playerAnim.getHandler(), "player")
    player = CharacterDirector(playerMove, playerAnim)

    def reset_room(trans, st, at):
        player.reset()
        Keyboard.reset()
        doors[room.yes] = room.yes_init
        doors[room.no] = room.no_init
        room.reset = True
        return None

transform loop(director):
    function director.onLoop
    pause director.dt
    repeat

transform characterLoop(cd):
    parallel:
        loop(cd.move)
    parallel:
        loop(cd.anim)
    parallel:
        loop(cd)

transform reset_room_transition(p=0.5):
    truecenter
    pause p
    function reset_room

image a = thisMap.getLayer(MapReferenceLayer.ABOVE)
image b = thisMap.getLayer(MapReferenceLayer.BELOW)
image d = thisMap.getLayer(MapReferenceLayer.DYNAMIC)
image null = Null()

screen keymap_screen():
    zorder 9999
    key "keydown_K_d"   action Function(Keyboard.action, down=True, key="d", _update_screens=False)
    key "keyup_K_d"     action Function(Keyboard.action, up=True,   key="d", _update_screens=False)
    key "keydown_K_a"   action Function(Keyboard.action, down=True, key="a", _update_screens=False)
    key "keyup_K_a"     action Function(Keyboard.action, up=True,   key="a", _update_screens=False)
    key "keydown_K_w"   action Function(Keyboard.action, down=True, key="w", _update_screens=False)
    key "keyup_K_w"     action Function(Keyboard.action, up=True,   key="w", _update_screens=False)
    key "keydown_K_s"   action Function(Keyboard.action, down=True, key="s", _update_screens=False)
    key "keyup_K_s"     action Function(Keyboard.action, up=True,   key="s", _update_screens=False)
    key "keydown_K_e"   action Function(Keyboard.action, down=True, key="e", _update_screens=False)
    key "keyup_K_e"     action Function(Keyboard.action, up=True,   key="e", _update_screens=False)

define question = Character("", advance=False)
default init = False
default room.yes = Direction.LEFT
default room.yes_init = ("",)
default room.no_init = ("",)
default room.no = Direction.RIGHT
default room.navigating = False
default room.reset = False

label after_load:
    $ print("loading")

label start:
    show screen keymap_screen
    #camera player:
    #    perspective True
    #    zzoom True
    show b at truecenter onlayer below
    show d at truecenter onlayer dynamic
    show a at truecenter onlayer above
    show null at characterLoop(player) as player
    show null at loop(thisMap) as map
    show null at loop(doors) as doors
    
    jump isInteract

label setup():
    $ room.navigating = True
    $ l = [Direction.LEFT, Direction.RIGHT]
    $ renpy.random.shuffle(l)
    $ room.yes, room.no = l
    if Params.CUTSCENE in doors.params and init:
        $ player.cutscene(Direction.UP)    
        pause 1.0
    if Params.LOADING_SCREEN in doors.params:
        show null at reset_room_transition(0.5) as loading
        with Fade(0.5,1.0,0.5)
        hide loading
    else:
        show null at reset_room_transition(0.0) as loading
        pause 0.1
        hide loading
    if not room.reset:
        $ reset_room(None, None, None)
    $ init = True
    $ player.cutscene(Direction.UP) 
    pause 0.5
    $ player.cutscene(start=False)
    $ room.reset = False
    $ room.navigating = False
    return

label isInteract:
    $ room.yes_init = "hasOpenAnim", Params.IS_INTERACT, Params.NONE
    $ room.no_init = "hasOpenAnim", Params.NONE, Params.IS_INTERACT
    call setup from _call_setup
    "Doors are pretty simple right? {w}Implementing one in a game should be the quickest thing ever, right?"
    "Only a couple decisions to make..."
    question "Does the player need to {color=[room.yes.textColour]}interact{/color} with the door or can they just {color=[room.no.textColour]}walk up{/color} to the door?\n\n{size=*0.5}Use [[{i}W,A,S,D{/i}] to move and [[{i}E{/i}] to interact{/size}"

label hasOpenAnim:
    $ room.yes_init = "isOpenBeforeAnim", Params.HAS_OPEN_ANIM, Params.NONE
    $ room.no_init = "playerHasOpenAnim", Params.NONE, Params.HAS_OPEN_ANIM
    call setup from _call_setup_1
    "Well done!"
    "One decision down! ...{w} Only a few more to go"
    question "Does the door have an {color=[room.yes.textColour]}opening animation{/color} or does it just have an {color=[room.no.textColour]}open and closed sprited{/color}?"

label isOpenBeforeAnim:
    $ room.yes_init = "playerHasOpenAnim", Params.IS_OPEN_BEFORE_ANIM, Params.NONE
    $ room.no_init = "playerHasOpenAnim", Params.NONE, Params.IS_OPEN_BEFORE_ANIM
    call setup from _call_setup_2
    "If it has an animation then when is it no longer a wall and becomes an entrance?"
    question "Is the door open when the animation {color=[room.yes.textColour]}starts{/color} or is it closed until the {color=[room.no.textColour]}end{/color} of the animtion?"

label playerHasOpenAnim:
    $ room.yes_init = "openAfterPlayerAnim", Params.PLAYER_HAS_OPEN_ANIM, Params.NONE
    $ room.no_init = "openIndividual", Params.NONE, Params.PLAYER_HAS_OPEN_ANIM
    call setup from _call_setup_3
    "How about the player?{w} We can't forget about the player..."
    question "Does the player get an {color=[room.yes.textColour]}animation{/color} when they're opening the door or is the player just their {color=[room.no.textColour]}static idle{/color} sprite?"

label openAfterPlayerAnim:
    $ room.yes_init = "openIndividual", Params.START_OPEN_AFTER_PLAYER_ANIM, Params.NONE
    $ room.no_init = "openIndividual", Params.NONE, Params.START_OPEN_AFTER_PLAYER_ANIM
    call setup from _call_setup_4
    "In that case, when does the door open?"
    question "Does the door start opening when the player's animation {color=[room.no.textColour]}starts{/color} or does it have to wait until the player's animation {color=[room.yes.textColour]}ends{/color}?"

label openIndividual:
    $ room.yes_init = "openBothIndividual", Params.CAN_OPEN_INDIVIDUAL, Params.NONE
    $ room.no_init = "loadingScreen", Params.NONE, Params.CAN_OPEN_INDIVIDUAL
    call setup from _call_setup_5
    "Great answers! {w}Just a few more to go...{w}\n\n{size=*0.5}As long as you don't choose hard stuff{/size}"
    "Our door here is actualy two doors!!! {w} ... {w} or is it?"
    question "Can the two halves been opened {color=[room.yes.textColour]}individually{/color} or is opening one the same as opening {color=[room.no.textColour]}both{/color}?"

label openBothIndividual:
    $ room.yes_init = "loadingScreen", Params.CAN_OPEN_INDIVIDUAL_BOTH, Params.NONE
    $ room.no_init = "loadingScreen", Params.NONE, Params.CAN_OPEN_INDIVIDUAL_BOTH
    call setup from _call_setup_6
    "There ya go...{w} No need to conform to the masses here {w} Being unique is the best thing possible"
    "But what if those want to fit in and not be left out?"
    question "Can the two halves been opened {color=[room.yes.textColour]}at the same time{/color} or must they be opened {color=[room.no.textColour]}one after the other{/color}?"

label loadingScreen:
    $ room.yes_init = "isPortal", Params.LOADING_SCREEN, Params.NONE
    $ room.no_init = "isPortal", Params.NONE, Params.LOADING_SCREEN
    call setup from _call_setup_7
    "On a complety different note, do the doors need to be annoying?"
    "As you've seen, the doors need to load the next room after you enter them {w}\n Is this always the case?"
    question "Do the doors need to have a {color=[room.yes.textColour]}loading screen{/color} after entering them or do they just switch (or not even need to switch in some cases) {color=[room.no.textColour]}immediately{/color} to the next location?"

label isPortal:
    $ room.yes_init = "hasCutscene", Params.IS_PORTAL, Params.NONE
    $ room.no_init = "canClose", Params.NONE, Params.IS_PORTAL
    call setup from _call_setup_8
    question "Furthermore, do we even need to {color=[room.no.textColour]}walk through the doors{/color} or can they just {color=[room.yes.textColour]}teleport{/color} us once opened?"

label hasCutscene:
    $ room.yes_init = "end", Params.CUTSCENE, Params.NONE
    $ room.no_init = "end", Params.NONE, Params.CUTSCENE
    call setup from _call_setup_9
    question "Should we show the player a {color=[room.yes.textColour]}cutscene{/color} when they're being teleported or should they just move {color=[room.no.textColour]}immediately{/color}?"

label canClose:
    $ room.yes_init = "intermediate1", Params.CAN_CLOSE, Params.NONE
    $ room.no_init = "closeDoorsBehind", Params.NONE, Params.CAN_CLOSE
    call setup from _call_setup_10
    "Good point! Doors are doors not portals"
    "On that note, doors usually don't get stuck in one direction..."
    question "Can doors be {color=[room.yes.textColour]}closed{/color} after being opened or are they forever {color=[room.no.textColour]}stuck{/color}?"

label intermediate1:
    if Params.CAN_OPEN_INDIVIDUAL in doors.params and Params.CAN_OPEN_INDIVIDUAL_BOTH in doors.params:
        jump oppositeActions
    else:
        jump intermediate2

label oppositeActions:
    $ room.yes_init = "intermediate2", Params.TOGGLES_INDIVIDUAL, Params.NONE
    $ room.no_init = "intermediate2", Params.NONE, Params.TOGGLES_INDIVIDUAL
    call setup from _call_setup_11
    "But we said that the doors can be opened individually and opened at the same time... {w} So can we we open/close at the same time?"
    question "Can the doors be opening and closing at {color=[room.yes.textColour]}the same time{/color} or if one is open we should {color=[room.no.textColour]}only be able to open{/color} the other?"

label intermediate2:
    if Params.HAS_OPEN_ANIM in doors.params:
        jump closedBeforeAnim
    else:
        jump hasCooldown

label closedBeforeAnim:
    $ room.yes_init = "noCloseOnColiding", Params.IS_CLOSED_BEFORE_ANIM, Params.NONE
    $ room.no_init = "noCloseOnColiding", Params.NONE, Params.IS_CLOSED_BEFORE_ANIM
    call setup from _call_setup_12
    "On to the next point..."
    "You said earlier that the door has an opening animation..."
    "Well that means the door has a closing animation too..."
    "So when is the door closed?"
    question "Is the door closed when the animation {color=[room.yes.textColour]}begins{/color} or when it {color=[room.no.textColour]}ends{/color}?"

label hasCooldown:
    $ room.yes_init = "noCloseOnColiding", Params.HAS_COOLDOWN, Params.NONE
    $ room.no_init = "noCloseOnColiding", Params.NONE, Params.HAS_COOLDOWN
    call setup from _call_setup_13
    "On to the next point..."
    "You said earlier that the door does not have an opening animation..."
    "Well that means the door doesn't have a closing animation either..."
    "But this means the door has no cooldown period"
    question "Is there a {color=[room.yes.textColour]}cooldown period{/color} between opening and closing the door, or can the player just {color=[room.no.textColour]}spam{/color} the living crap out of the door?"

label noCloseOnColiding:
    $ room.yes_init = "closeDoorsBehind", Params.NO_CLOSE_ON_COLLIDING, Params.NONE
    $ room.no_init = "clipThroughDoors", Params.NONE, Params.NO_CLOSE_ON_COLLIDING
    call setup from _call_setup_14
    "As you may have seen, the doors were nicely put at the front of the walls opening backwards so that we wouldn't have to deal with small collision boxes"
    "But now you've gone ahead and messed that all up by saying the player can close the door"
    "So what now?"
    "..."
    "The player's going to be an idiot and close the door whilst they're standing on it"
    "..."
    question "If the player closes the door whilst colliding with where the door will be, do we just {color=[room.yes.textColour]}reject the player's wishes{/color} and keep the door close or let them {color=[room.no.textColour]}suffer{/color}?"

label clipThroughDoors:
    $ room.yes_init = "closeDoorsBehind", Params.CLIP_IF_COLLIDING, Params.NONE
    $ room.no_init = "closeDoorsBehind", Params.NONE, Params.CLIP_IF_COLLIDING
    call setup from _call_setup_15
    "That was a joke... Please don't select that choice"
    "I'll give you another option..."
    question "How about we just give them god mod and allow them to {color=[room.yes.textColour]}clip through the door{/color} instead of {color=[room.no.textColour]}soft locking{/color} themselves?"

label closeDoorsBehind:
    $ room.yes_init = "end", Params.CLOSE_BEHIND, Params.NONE
    $ room.no_init = "end", Params.NONE, Params.CLOSE_BEHIND
    call setup from _call_setup_16
    "Fine."
    "What about some automation"
    question "Should the doors {color=[room.yes.textColour]}close behind you{/color} or {color=[room.no.textColour]}stay open{/color} when you walk past?\n\n{size=*0.1}I don't care if you say yes, I'm not actualy adding this... the amount of bugs this would cause...{/size}"

label end:
    $ room.yes_init = "end", Params.NONE, Params.NONE
    $ room.no_init = "end", Params.NONE, Params.NONE
    call setup from _call_setup_17
    "Well done"
    "You've made some pretty good choices"
    "Not nearly enough to actually implement but enough for now"
    question "Take a look"

