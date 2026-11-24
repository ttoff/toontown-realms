import math

from toontown.sandbox import PropGlobals
from toontown.char import CharGlobals
from otp.avatar import Avatar
from otp.avatar.Avatar import teleportNotify
from . import ToonDNA
from direct.task.Task import Task
from direct.showbase import Audio3DManager
from toontown.suit import SuitDNA
from direct.actor import Actor
import string
from .ToonHead import *
from panda3d.core import *
from panda3d.direct import *
from panda3d.toontown import *
from direct.interval.IntervalGlobal import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals
from otp.otpbase import OTPLocalizer
from toontown.toonbase import TTLocalizer
import random
from toontown.effects import Wake
from . import TTEmote
from otp.avatar import Emote
from . import Motion
from toontown.hood import ZoneUtil
from otp.otpbase.PythonUtil import cmp, cmp_to_key
from toontown.effects import DustCloud
from toontown.distributed import DelayDelete
from toontown.battle import BattleProps
from toontown.suit import SuitTimings
from toontown.battle import MovieUtil, BattleParticles, MovieLure
from toontown.fishing import FishGlobals, FishBase
from . import AccessoryGlobals
from . import LaughingManGlobals
import types
import importlib
from subprocess import Popen

from toontown.toonbase import ClientSettings
from ..datapack.DataPackManager import DataPackManager
from ..toonbase.ToonBaseGlobal import *
from ..toonbase.ToontownTypes import CogAppearanceIndex


def teleportDebug(requestStatus, msg, onlyIfToAv = True):
    if teleportNotify.getDebug():
        teleport = 'teleport'
        if 'how' in requestStatus and requestStatus['how'][:len(teleport)] == teleport:
            if not onlyIfToAv or 'avId' in requestStatus and requestStatus['avId'] > 0:
                teleportNotify.debug(msg)


DogDialogueArray = []
CatDialogueArray = []
HorseDialogueArray = []
RabbitDialogueArray = []
MouseDialogueArray = []
DuckDialogueArray = []
MonkeyDialogueArray = []
BearDialogueArray = []
PigDialogueArray = []
GyroDialogueArray = []
ScroogeDialogueArray = []
SkeletonDialogueArray = []
SuitDialogueArray = []
MickeyDialogueArray = []
MinnieDialogueArray = []
PlutoDialogueArray = []
GoofyDialogueArray = []
DonaldDialogueArray = []
DaisyDialogueArray = []
ChipDialogueArray = []
DaleDialogueArray = []
DoodleDialogueArray = []
BossDialogueArray = []
TrolleyDialogueArray = []
FishDialogueArrays = {}
LegsAnimDict = {}
TorsoAnimDict = {}
HeadAnimDict = {}
Preloaded = []
Phase3AnimList = (('neutral', 'neutral'), ('run', 'run'))
Phase3_5AnimList = (('walk', 'walk'),
 ('teleport', 'teleport'),
 ('book', 'book'),
 ('jump', 'jump'),
 ('running-jump', 'running-jump'),
 ('jump-squat', 'jump-zstart'),
 ('jump-idle', 'jump-zhang'),
 ('jump-land', 'jump-zend'),
 ('running-jump-squat', 'leap_zstart'),
 ('running-jump-idle', 'leap_zhang'),
 ('running-jump-land', 'leap_zend'),
 ('pushbutton', 'press-button'),
 ('throw', 'pie-throw'),
 ('victory', 'victory-dance'),
 ('sidestep-left', 'sidestep-left'),
 ('conked', 'conked'),
 ('cringe', 'cringe'),
 ('wave', 'wave'),
 ('shrug', 'shrug'),
 ('angry', 'angry'),
 ('tutorial-neutral', 'tutorial-neutral'),
 ('left-point', 'left-point'),
 ('right-point', 'right-point'),
 ('right-point-start', 'right-point-start'),
 ('give-props', 'give-props'),
 ('give-props-start', 'give-props-start'),
 ('right-hand', 'right-hand'),
 ('right-hand-start', 'right-hand-start'),
 ('duck', 'duck'),
 ('sidestep-right', 'jump-back-right'))
Phase4AnimList = (('sit', 'sit'),
 ('sit-start', 'intoSit'),
 ('swim', 'swim'),
 ('tug-o-war', 'tug-o-war'),
 ('sad-walk', 'losewalk'),
 ('sad-neutral', 'sad-neutral'),
 ('up', 'up'),
 ('down', 'down'),
 ('left', 'left'),
 ('right', 'right'),
 ('applause', 'applause'),
 ('confused', 'confused'),
 ('bow', 'bow'),
 ('curtsy', 'curtsy'),
 ('bored', 'bored'),
 ('think', 'think'),
 ('battlecast', 'fish'),
 ('cast', 'cast'),
 ('castlong', 'castlong'),
 ('fish-end', 'fishEND'),
 ('fish-neutral', 'fishneutral'),
 ('fish-again', 'fishAGAIN'),
 ('reel', 'reel'),
 ('reel-H', 'reelH'),
 ('reel-neutral', 'reelneutral'),
 ('pole', 'pole'),
 ('pole-neutral', 'poleneutral'),
 ('slip-forward', 'slip-forward'),
 ('slip-backward', 'slip-backward'),
 ('catch-neutral', 'gameneutral'),
 ('catch-run', 'gamerun'),
 ('catch-eatneutral', 'eat_neutral'),
 ('catch-eatnrun', 'eatnrun'),
 ('catch-intro-throw', 'gameThrow'),
 ('swing', 'swing'),
 ('pet-start', 'petin'),
 ('pet-loop', 'petloop'),
 ('pet-end', 'petend'),
 ('scientistJealous', 'scientistJealous'),
 ('scientistEmcee', 'scientistEmcee'),
 ('scientistWork', 'scientistWork'),
 ('scientistGame', 'scientistGame'),
 ('periscope', 'periscope'),
 ('taunt', 'taunt'),
 ('bounce', 'bounce'))
Phase5AnimList = (('water-gun', 'water-gun'),
 ('hold-bottle', 'hold-bottle'),
 ('firehose', 'firehose'),
 ('spit', 'spit'),
 ('tickle', 'tickle'),
 ('smooch', 'smooch'),
 ('happy-dance', 'happy-dance'),
 ('sprinkle-dust', 'sprinkle-dust'),
 ('juggle', 'juggle'),
 ('climb', 'climb'),
 ('sound', 'shout'),
 ('toss', 'toss'),
 ('hold-magnet', 'hold-magnet'),
 ('hypnotize', 'hypnotize'),
 ('struggle', 'struggle'),
 ('lose', 'lose'),
 ('melt', 'melt'))
Phase5_5AnimList = (('takePhone', 'takePhone'),
 ('phoneNeutral', 'phoneNeutral'),
 ('phoneBack', 'phoneBack'),
 ('bank', 'jellybeanJar'),
 ('callPet', 'callPet'),
 ('feedPet', 'feedPet'),
 ('start-dig', 'into_dig'),
 ('loop-dig', 'loop_dig'),
 ('water', 'water'))
Phase6AnimList = (('headdown-putt', 'headdown-putt'),
 ('into-putt', 'into-putt'),
 ('loop-putt', 'loop-putt'),
 ('rotateL-putt', 'rotateL-putt'),
 ('rotateR-putt', 'rotateR-putt'),
 ('swing-putt', 'swing-putt'),
 ('look-putt', 'look-putt'),
 ('lookloop-putt', 'lookloop-putt'),
 ('bad-putt', 'bad-putt'),
 ('badloop-putt', 'badloop-putt'),
 ('good-putt', 'good-putt'))
Phase9AnimList = (('push', 'push'),)
Phase10AnimList = (('leverReach', 'leverReach'), ('leverPull', 'leverPull'), ('leverNeutral', 'leverNeutral'))
Phase12AnimList = ()
if not base.config.GetBool('want-new-anims', 1):
    LegDict = {'s': '/models/char/dogSS_Shorts-legs-',
     'm': '/models/char/dogMM_Shorts-legs-',
     'l': '/models/char/dogLL_Shorts-legs-'}
    TorsoDict = {'s': '/models/char/dogSS_Naked-torso-',
     'm': '/models/char/dogMM_Naked-torso-',
     'l': '/models/char/dogLL_Naked-torso-',
     'ss': '/models/char/dogSS_Shorts-torso-',
     'ms': '/models/char/dogMM_Shorts-torso-',
     'ls': '/models/char/dogLL_Shorts-torso-',
     'sd': '/models/char/dogSS_Skirt-torso-',
     'md': '/models/char/dogMM_Skirt-torso-',
     'ld': '/models/char/dogLL_Skirt-torso-'}
else:
    LegDict = {'s': '/models/char/tt_a_chr_dgs_shorts_legs_',
     'm': '/models/char/tt_a_chr_dgm_shorts_legs_',
     'l': '/models/char/tt_a_chr_dgl_shorts_legs_'}
    TorsoDict = {'s': '/models/char/dogSS_Naked-torso-',
     'm': '/models/char/dogMM_Naked-torso-',
     'l': '/models/char/dogLL_Naked-torso-',
     'ss': '/models/char/tt_a_chr_dgs_shorts_torso_',
     'ms': '/models/char/tt_a_chr_dgm_shorts_torso_',
     'ls': '/models/char/tt_a_chr_dgl_shorts_torso_',
     'sd': '/models/char/tt_a_chr_dgs_skirt_torso_',
     'md': '/models/char/tt_a_chr_dgm_skirt_torso_',
     'ld': '/models/char/tt_a_chr_dgl_skirt_torso_'}


def loadModels():
    global Preloaded
    preloadAvatars = base.config.GetBool('preload-avatars', 0)
    if preloadAvatars:

        def loadTex(path):
            tex = loader.loadTexture(path)
            tex.setMinfilter(Texture.FTLinearMipmapLinear)
            tex.setMagfilter(Texture.FTLinear)
            Preloaded.append(tex)

        for shirt in ToonDNA.Shirts:
            loadTex(shirt)

        for sleeve in ToonDNA.Sleeves:
            loadTex(sleeve)

        for short in ToonDNA.BoyShorts:
            loadTex(short)

        for bottom in ToonDNA.GirlBottoms:
            loadTex(bottom[0])

        for key in list(LegDict.keys()):
            fileRoot = LegDict[key]
            model = loader.loadModel('phase_3' + fileRoot + '1000').node()
            Preloaded.append(model)
            model = loader.loadModel('phase_3' + fileRoot + '500').node()
            Preloaded.append(model)
            model = loader.loadModel('phase_3' + fileRoot + '250').node()
            Preloaded.append(model)

        for key in list(TorsoDict.keys()):
            fileRoot = TorsoDict[key]
            model = loader.loadModel('phase_3' + fileRoot + '1000').node()
            Preloaded.append(model)
            if len(key) > 1:
                model = loader.loadModel('phase_3' + fileRoot + '500').node()
                Preloaded.append(model)
                model = loader.loadModel('phase_3' + fileRoot + '250').node()
                Preloaded.append(model)

        for key in list(HeadDict.keys()):
            fileRoot = HeadDict[key]
            model = loader.loadModel('phase_3' + fileRoot + '1000').node()
            Preloaded.append(model)
            model = loader.loadModel('phase_3' + fileRoot + '500').node()
            Preloaded.append(model)
            model = loader.loadModel('phase_3' + fileRoot + '250').node()
            Preloaded.append(model)


def loadBasicAnims():
    loadPhaseAnims()


def unloadBasicAnims():
    loadPhaseAnims(0)


def loadTutorialBattleAnims():
    loadPhaseAnims('phase_3.5')


def unloadTutorialBattleAnims():
    loadPhaseAnims('phase_3.5', 0)


def loadMinigameAnims():
    loadPhaseAnims('phase_4')


def unloadMinigameAnims():
    loadPhaseAnims('phase_4', 0)


def loadBattleAnims():
    loadPhaseAnims('phase_5')


def unloadBattleAnims():
    loadPhaseAnims('phase_5', 0)


def loadSellbotHQAnims():
    loadPhaseAnims('phase_9')


def unloadSellbotHQAnims():
    loadPhaseAnims('phase_9', 0)


def loadCashbotHQAnims():
    loadPhaseAnims('phase_10')


def unloadCashbotHQAnims():
    loadPhaseAnims('phase_10', 0)


def loadBossbotHQAnims():
    loadPhaseAnims('phase_12')


def unloadBossbotHQAnims():
    loadPhaseAnims('phase_12', 0)


def loadPhaseAnims(phaseStr = 'phase_3', loadFlag = 1):
    if phaseStr == 'phase_3':
        animList = Phase3AnimList
    elif phaseStr == 'phase_3.5':
        animList = Phase3_5AnimList
    elif phaseStr == 'phase_4':
        animList = Phase4AnimList
    elif phaseStr == 'phase_5':
        animList = Phase5AnimList
    elif phaseStr == 'phase_5.5':
        animList = Phase5_5AnimList
    elif phaseStr == 'phase_6':
        animList = Phase6AnimList
    elif phaseStr == 'phase_9':
        animList = Phase9AnimList
    elif phaseStr == 'phase_10':
        animList = Phase10AnimList
    elif phaseStr == 'phase_12':
        animList = Phase12AnimList
    else:
        Toon.notify.error('Unknown phase string %s' % phaseStr)
    for key in list(LegDict.keys()):
        for anim in animList:
            if loadFlag:
                pass
            elif anim[0] in LegsAnimDict[key]:
                if base.localAvatar.style.legs == key:
                    base.localAvatar.unloadAnims([anim[0]], 'legs', None)

    for key in list(TorsoDict.keys()):
        for anim in animList:
            if loadFlag:
                pass
            elif anim[0] in TorsoAnimDict[key]:
                if base.localAvatar.style.torso == key:
                    base.localAvatar.unloadAnims([anim[0]], 'torso', None)

    for key in list(HeadDict.keys()):
        if key.find('d') >= 0:
            for anim in animList:
                if loadFlag:
                    pass
                elif anim[0] in HeadAnimDict[key]:
                    if base.localAvatar.style.head == key:
                        base.localAvatar.unloadAnims([anim[0]], 'head', None)

    return


def compileGlobalAnimList():
    phaseList = [Phase3AnimList,
     Phase3_5AnimList,
     Phase4AnimList,
     Phase5AnimList,
     Phase5_5AnimList,
     Phase6AnimList,
     Phase9AnimList,
     Phase10AnimList,
     Phase12AnimList]
    phaseStrList = ['phase_3',
     'phase_3.5',
     'phase_4',
     'phase_5',
     'phase_5.5',
     'phase_6',
     'phase_9',
     'phase_10',
     'phase_12']
    for animList in phaseList:
        phaseStr = phaseStrList[phaseList.index(animList)]
        for key in list(LegDict.keys()):
            LegsAnimDict.setdefault(key, {})
            for anim in animList:
                file = phaseStr + LegDict[key] + anim[1]
                LegsAnimDict[key][anim[0]] = file

        for key in list(TorsoDict.keys()):
            TorsoAnimDict.setdefault(key, {})
            for anim in animList:
                if len(key) == 1:
                    file = phaseStr + TorsoDict[key + "s"] + anim[1]
                else:
                    file = phaseStr + TorsoDict[key] + anim[1]
                TorsoAnimDict[key][anim[0]] = file

        for key in list(HeadDict.keys()):
            if key.find('d') >= 0:
                HeadAnimDict.setdefault(key, {})
                for anim in animList:
                    file = phaseStr + HeadDict[key] + anim[1]
                    HeadAnimDict[key][anim[0]] = file


def loadDialog():
    loadPath = 'phase_3.5/audio/dial/'

    # Save the AV_dog_med sound so the same AudioSound instance
    # can be used for both the Pluto transformation and the regular
    # dog noise
    dogMedDial = None

    dogMedFile = 'AV_dog_med'

    DogDialogueFiles = ('AV_dog_short', dogMedFile, 'AV_dog_long', 'AV_dog_question', 'AV_dog_exclaim', 'AV_dog_howl')
    global DogDialogueArray
    for file in DogDialogueFiles:
        audioFile = base.loader.loadSfx(loadPath + file + '.ogg', manager = 'dialog')
        if file == dogMedFile:
            dogMedDial = audioFile
        DogDialogueArray.append(audioFile)

    catDialogueFiles = ('AV_cat_short', 'AV_cat_med', 'AV_cat_long', 'AV_cat_question', 'AV_cat_exclaim', 'AV_cat_howl')
    global CatDialogueArray
    for file in catDialogueFiles:
        CatDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg', manager = 'dialog'))

    horseDialogueFiles = ('AV_horse_short', 'AV_horse_med', 'AV_horse_long', 'AV_horse_question', 'AV_horse_exclaim',
                          'AV_horse_howl')
    global HorseDialogueArray
    for file in horseDialogueFiles:
        HorseDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg', manager = 'dialog'))

    rabbitDialogueFiles = ('AV_rabbit_short', 'AV_rabbit_med', 'AV_rabbit_long', 'AV_rabbit_question',
                           'AV_rabbit_exclaim', 'AV_rabbit_howl')
    global RabbitDialogueArray
    for file in rabbitDialogueFiles:
        RabbitDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg', manager = 'dialog'))

    mouseDialogueFiles = ('AV_mouse_short', 'AV_mouse_med', 'AV_mouse_long', 'AV_mouse_question', 'AV_mouse_exclaim',
                          'AV_mouse_howl')
    global MouseDialogueArray
    for file in mouseDialogueFiles:
        MouseDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg', manager = 'dialog'))

    duckDialogueFiles = ('AV_duck_short', 'AV_duck_med', 'AV_duck_long', 'AV_duck_question', 'AV_duck_exclaim',
                         'AV_duck_howl')
    global DuckDialogueArray
    for file in duckDialogueFiles:
        DuckDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg', manager = 'dialog'))

    monkeyDialogueFiles = ('AV_monkey_short', 'AV_monkey_med', 'AV_monkey_long', 'AV_monkey_question',
                           'AV_monkey_exclaim', 'AV_monkey_howl')
    global MonkeyDialogueArray
    for file in monkeyDialogueFiles:
        MonkeyDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg', manager = 'dialog'))

    bearDialogueFiles = ('AV_bear_short', 'AV_bear_med', 'AV_bear_long', 'AV_bear_question', 'AV_bear_exclaim',
                         'AV_bear_howl')
    global BearDialogueArray
    for file in bearDialogueFiles:
        BearDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg', manager = 'dialog'))

    pigDialogueFiles = ('AV_pig_short', 'AV_pig_med', 'AV_pig_long', 'AV_pig_question', 'AV_pig_exclaim', 'AV_pig_howl')
    global PigDialogueArray
    for file in pigDialogueFiles:
        PigDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg', manager = 'dialog'))

    gyroDialogueFiles = ('AV_duck_short', 'AV_duck_med', 'AV_duck_long', 'AV_duck_question', 'AV_duck_exclaim',
                         'AV_duck_howl')
    global GyroDialogueArray
    for file in gyroDialogueFiles:
        GyroDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg', manager = 'dialog'))

    scroogeDialogueFiles = ('AV_duck_short', 'AV_duck_med', 'AV_duck_long', 'AV_duck_question', 'AV_duck_exclaim',
                            'AV_duck_howl')
    global ScroogeDialogueArray
    for file in scroogeDialogueFiles:
        ScroogeDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg', manager = 'dialog'))

    skeletonDialogueFiles = ('Skel_COG_VO_grunt', 'Skel_COG_VO_murmur', 'Skel_COG_VO_statement', 'Skel_COG_VO_question',
                             'Skel_COG_VO_grunt', 'Skel_COG_VO_murmur')
    global SkeletonDialogueArray
    for file in skeletonDialogueFiles:
        SkeletonDialogueArray.append(base.loader.loadSfx('phase_5/audio/sfx/' + file + '.ogg', manager = 'dialog'))

    if ClientSettings.ClassicSFX.get():
        suitDialogueFiles = ['COG_VO_grunt',
                             'COG_VO_murmur',
                             'COG_VO_statement',
                             'COG_VO_question_retro',
                             'COG_VO_grunt',
                             'COG_VO_murmur']
    else:
        suitDialogueFiles = ['COG_VO_grunt',
                             'COG_VO_murmur',
                             'COG_VO_statement',
                             'COG_VO_question',
                             'COG_VO_grunt',
                             'COG_VO_murmur']
    global SuitDialogueArray
    for file in suitDialogueFiles:
        SuitDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg', manager = 'dialog'))

    global MickeyDialogueArray
    mickeyDial = base.loader.loadSfx('phase_3/audio/dial/mickey.ogg', manager = 'dialog')
    for x in range(6):
        MickeyDialogueArray.append(mickeyDial)

    global MinnieDialogueArray
    minnieDial = base.loader.loadSfx('phase_3/audio/dial/minnie.ogg', manager = 'dialog')
    for x in range(6):
        MinnieDialogueArray.append(minnieDial)

    global PlutoDialogueArray
    for x in range(6):
        PlutoDialogueArray.append(dogMedDial)

    global DaisyDialogueArray
    daisyDial = base.loader.loadSfx('phase_4/audio/dial/daisy.ogg', manager = 'dialog')
    for x in range(6):
        DaisyDialogueArray.append(daisyDial)

    global GoofyDialogueArray
    goofyDial = base.loader.loadSfx('phase_6/audio/dial/goofy.ogg', manager = 'dialog')
    for x in range(6):
        GoofyDialogueArray.append(goofyDial)

    global DonaldDialogueArray
    donaldDial = base.loader.loadSfx('phase_6/audio/dial/donald.ogg', manager = 'dialog')
    for x in range(6):
        DonaldDialogueArray.append(donaldDial)

    global ChipDialogueArray
    chipDial = base.loader.loadSfx('phase_6/audio/dial/chip.ogg', manager = 'dialog')
    for x in range(6):
        ChipDialogueArray.append(chipDial)

    global DaleDialogueArray
    daleDial = base.loader.loadSfx('phase_6/audio/dial/dale.ogg', manager = 'dialog')
    for x in range(6):
        DaleDialogueArray.append(daleDial)

    global DoodleDialogueArray
    doodleDial = base.loader.loadSfx('phase_5/audio/sfx/speak_v1.ogg', manager = 'dialog')
    for x in range(6):
        DoodleDialogueArray.append(doodleDial)

    bossDialogueFiles = ('Boss_COG_VO_grunt', 'Boss_COG_VO_murmur', 'Boss_COG_VO_statement', 'Boss_COG_VO_question',
                         'Boss_COG_VO_statement', 'Boss_COG_VO_murmur')
    global BossDialogueArray
    for file in bossDialogueFiles:
        BossDialogueArray.append(base.loader.loadSfx('phase_9/audio/sfx/' + file + '.ogg', manager = 'dialog'))

    for key in list(TTLocalizer.FishGenusNames.keys()):
        info = FishGlobals.FishAudioFileDict.get(key)
        sfx = info[0]
        dialogueArray = []
        for file in range(6):
            dialogueArray.append(base.loader.loadSfx('phase_4/audio/sfx/' + sfx, manager = 'dialog'))
        FishDialogueArrays[key] = dialogueArray

    trolleySfx = base.loader.loadSfx('phase_4/audio/sfx/SZ_trolley_bell.ogg', manager = 'dialog')
    trolleyHowl = base.loader.loadSfx('phase_4/audio/sfx/MG_sfx_travel_game_bell_for_trolley.ogg', manager = 'dialog')
    global TrolleyDialogueArray
    while len(TrolleyDialogueArray) < 5:
        TrolleyDialogueArray.append(trolleySfx)
    TrolleyDialogueArray.append(trolleyHowl)


def unloadDialog():
    global CatDialogueArray
    global PigDialogueArray
    global BearDialogueArray
    global DuckDialogueArray
    global RabbitDialogueArray
    global MouseDialogueArray
    global DogDialogueArray
    global HorseDialogueArray
    global MonkeyDialogueArray
    global GyroDialogueArray
    global ScroogeDialogueArray
    global SkeletonDialogueArray
    global SuitDialogueArray
    global MickeyDialogueArray
    global MinnieDialogueArray
    global PlutoDialogueArray
    global DaisyDialogueArray
    global GoofyDialogueArray
    global DonaldDialogueArray
    global ChipDialogueArray
    global DaleDialogueArray
    global DoodleDialogueArray
    global BossDialogueArray
    global FishDialogueArrays
    global TrolleyDialogueArray
    DogDialogueArray = []
    CatDialogueArray = []
    HorseDialogueArray = []
    RabbitDialogueArray = []
    MouseDialogueArray = []
    DuckDialogueArray = []
    MonkeyDialogueArray = []
    BearDialogueArray = []
    PigDialogueArray = []
    GyroDialogueArray = []
    ScroogeDialogueArray = []
    SkeletonDialogueArray = []
    SuitDialogueArray = []
    MickeyDialogueArray = []
    MinnieDialogueArray = []
    PlutoDialogueArray = []
    GoofyDialogueArray = []
    DonaldDialogueArray = []
    DaisyDialogueArray = []
    ChipDialogueArray = []
    DaleDialogueArray = []
    DoodleDialogueArray = []
    BossDialogueArray = []
    FishDialogueArrays = {}
    TrolleyDialogueArray = []


class Toon(Avatar.Avatar, ToonHead):
    notify = DirectNotifyGlobal.directNotify.newCategory('Toon')
    afkTimeout = base.config.GetInt('afk-timeout', 600)

    def __init__(self):
        try:
            self.Toon_initialized
            return
        except:
            self.Toon_initialized = 1

        Avatar.Avatar.__init__(self)
        ToonHead.__init__(self)
        self.toonScale = 1.0
        self.forwardSpeed = 0.0
        self.rotateSpeed = 0.0
        self.avatarType = 'toon'
        self.motion = Motion.Motion(self)
        self.standWalkRunReverse = None
        self.playingAnim = None
        self.soundTeleport = None
        self.laffMeterTextColor = (0, 0, 0)
        self.cheesyEffect = ToontownGlobals.CENormal
        self.effectTrack = None
        self.emoteTrack = None
        self.emote = None
        self.stunTrack = None
        self.__bookActors = []
        self.cogBook = None
        self.__holeActors = []
        self.holeClipPath = None
        self.wake = None
        self.lastWakeTime = 0
        self.forceJumpIdle = False
        self.numPies = 0
        self.pieType = 0
        self.pieModel = None
        self.__pieModelType = None
        self.pieScale = 1.0
        self.featherModel = None
        self.featherScale = 1.0
        self.backpackNodes = []
        self.hat = (0, 0, 0)
        self.glasses = (0, 0, 0)
        self.backpack = (0, 0, 0)
        self.shoes = (0, 0, 0)
        self.isStunned = 0
        self.transformations = ['', 0, 0, 0, '', 0, 0, 0, 0, 0] # Cog, Char, Doodle, Goon, Boss, Prop, Fish, Butterfly, Misc, Street
        self.disguiseType = 0
        self.forcedRate = -1
        self.defaultColorScale = None
        self.jar = None
        self.bobSwim = None
        self.jump = None
        self.ival = None
        self.track = None
        self.tpose = False
        self.animalSound = ''
        self.setTag('pieCode', str(ToontownGlobals.PieCodeToon))
        self.setFont(ToontownGlobals.getToonFont())
        self.soundChatBubble = base.loader.loadSfx('phase_3/audio/sfx/GUI_balloon_popup.ogg', manager = 'gui')
        self.animFSM = ClassicFSM('Toon', [State('off', self.enterOff, self.exitOff),
         State('neutral', self.enterNeutral, self.exitNeutral),
         State('victory', self.enterVictory, self.exitVictory),
         State('Happy', self.enterHappy, self.exitHappy),
         State('Sad', self.enterSad, self.exitSad),
         State('Catching', self.enterCatching, self.exitCatching),
         State('CatchEating', self.enterCatchEating, self.exitCatchEating),
         State('Sleep', self.enterSleep, self.exitSleep),
         State('walk', self.enterWalk, self.exitWalk),
         State('jumpSquat', self.enterJumpSquat, self.exitJumpSquat),
         State('jump', self.enterJump, self.exitJump),
         State('jumpAirborne', self.enterJumpAirborne, self.exitJumpAirborne),
         State('jumpLand', self.enterJumpLand, self.exitJumpLand),
         State('run', self.enterRun, self.exitRun),
         State('swim', self.enterSwim, self.exitSwim),
         State('swimhold', self.enterSwimHold, self.exitSwimHold),
         State('dive', self.enterDive, self.exitDive),
         State('cringe', self.enterCringe, self.exitCringe),
         State('OpenBook', self.enterOpenBook, self.exitOpenBook, ['ReadBook', 'CloseBook']),
         State('ReadBook', self.enterReadBook, self.exitReadBook),
         State('CloseBook', self.enterCloseBook, self.exitCloseBook),
         State('TeleportOut', self.enterTeleportOut, self.exitTeleportOut),
         State('Died', self.enterDied, self.exitDied),
         State('TeleportedOut', self.enterTeleportedOut, self.exitTeleportedOut),
         State('TeleportIn', self.enterTeleportIn, self.exitTeleportIn),
         State('Emote', self.enterEmote, self.exitEmote),
         State('SitStart', self.enterSitStart, self.exitSitStart),
         State('Sit', self.enterSit, self.exitSit),
         State('Push', self.enterPush, self.exitPush),
         State('Squish', self.enterSquish, self.exitSquish),
         State('FallDown', self.enterFallDown, self.exitFallDown),
         State('GolfPuttLoop', self.enterGolfPuttLoop, self.exitGolfPuttLoop),
         State('GolfRotateLeft', self.enterGolfRotateLeft, self.exitGolfRotateLeft),
         State('GolfRotateRight', self.enterGolfRotateRight, self.exitGolfRotateRight),
         State('GolfPuttSwing', self.enterGolfPuttSwing, self.exitGolfPuttSwing),
         State('GolfGoodPutt', self.enterGolfGoodPutt, self.exitGolfGoodPutt),
         State('GolfBadPutt', self.enterGolfBadPutt, self.exitGolfBadPutt),
         State('Flattened', self.enterFlattened, self.exitFlattened),
         State('CogThiefRunning', self.enterCogThiefRunning, self.exitCogThiefRunning),
         State('ScientistJealous', self.enterScientistJealous, self.exitScientistJealous),
         State('ScientistEmcee', self.enterScientistEmcee, self.exitScientistEmcee),
         State('ScientistWork', self.enterScientistWork, self.exitScientistWork),
         State('ScientistLessWork', self.enterScientistLessWork, self.exitScientistLessWork),
         State('ScientistPlay', self.enterScientistPlay, self.enterScientistPlay),
         State('PortalOut', self.enterPortalOut, self.exitPortalOut),
         State('PortaledOut', self.enterPortaledOut, self.exitPortaledOut),
         State('PortalIn', self.enterPortalIn, self.exitPortalIn),
         State('Periscope', self.enterPeriscope, self.exitPeriscope)], 'off', 'off')
        self.animFSM.enterInitialState()
        self.fullToon = True
        self.sleepString = ''

    def stopAnimations(self):
        if hasattr(self, 'animFSM'):
            if not self.animFSM.isInternalStateInFlux():
                self.animFSM.request('off')
            else:
                self.notify.warning('animFSM in flux, state=%s, not requesting off' %
                                    self.animFSM.getCurrentState().getName())
        else:
            self.notify.warning('animFSM has been deleted')
        if self.effectTrack != None:
            self.effectTrack.pause()
            self.effectTrack = None
        if self.emoteTrack != None:
            self.emoteTrack.finish()
            self.emoteTrack = None
        if self.stunTrack != None:
            self.stunTrack.finish()
            self.stunTrack = None
        if self.wake:
            self.wake.stop()
            self.wake.destroy()
            self.wake = None
        if self.bobSwim:
            self.bobSwim.finish()
            self.bobSwim = None
        if self.jump:
            self.jump.finish()
            self.jump = None
        if self.ival:
            self.ival.finish()
            self.ival = None
        self.cleanupPieModel()
        self.cleanupFeatherModel()

    def delete(self):
        try:
            self.Toon_deleted
        except:
            self.Toon_deleted = 1
            self.stopAnimations()
            self.rightHands = None
            self.rightHand = None
            self.leftHands = None
            self.leftHand = None
            self.headParts = None
            self.torsoParts = None
            self.hipsParts = None
            self.legsParts = None
            del self.animFSM
            for bookActor in self.__bookActors:
                bookActor.delete()

            del self.__bookActors
            for holeActor in self.__holeActors:
                holeActor.delete()

            del self.__holeActors
            self.soundTeleport = None
            self.motion.delete()
            self.motion = None
            Avatar.Avatar.delete(self)
            ToonHead.delete(self)

        return

    def uniqueName(self, name):
        return name + '-{0}'.format(id(self))

    def updateToonDNA(self, newDNA, fForce = 0):
        self.style.gender = newDNA.getGender()
        oldDNA = self.style

        if self.getTPose():
            self.stop()
            self.unloadAnims()

        poof = False

        if fForce or newDNA.head != oldDNA.head:
            poof = True
            self.swapToonHead(newDNA.head)
            self.loop('neutral')
            if self.getTPose():
                self.stop()
                self.unloadAnims()

        if fForce or newDNA.torso != oldDNA.torso:
            poof = True
            self.swapToonTorso(newDNA.torso, genClothes=0)
            self.loop('neutral')
            if self.getTPose():
                self.stop()
                self.unloadAnims()

        if fForce or newDNA.legs != oldDNA.legs:
            poof = True
            self.swapToonLegs(newDNA.legs)
            self.loop('neutral')
            if self.getTPose():
                self.stop()
                self.unloadAnims()

        if (newDNA.headColor != oldDNA.headColor) or (newDNA.armColor != oldDNA.armColor) or (newDNA.legColor != oldDNA.legColor):
            poof = True

        self.swapToonColor(newDNA)
        self.__swapToonClothes(newDNA)

        if poof:
            if self.isLocal():
                self.initCameraPositions()
                self.resetCameraPosition()

            def getDustCloudIval():
                dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
                dustCloud.setBillboardAxis(2.0)
                dustCloud.setZ(3)
                dustCloud.setScale(0.4)
                dustCloud.createTrack()
                dustCloud.reparentTo(self)
                return Sequence(dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

            dust = getDustCloudIval()
            dust.start()

    def setDNAString(self, dnaString):
        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(dnaString)
        self.setDNA(newDNA)

    def setDNA(self, dna):
        oldHat = self.getHat()
        oldGlasses = self.getGlasses()
        oldBackpack = self.getBackpack()
        oldShoes = self.getShoes()
        self.setHat(0, 0, 0)
        self.setGlasses(0, 0, 0)
        self.setBackpack(0, 0, 0)
        self.setShoes(0, 0, 0)
        if hasattr(self, 'transformations'):
            if self.getTransformationsIndex(ToontownGlobals.TransformationCog):
                return
        if self.style:
            self.updateToonDNA(dna)
        else:
            self.style = dna
            self.generateToon()
            self.initializeDropShadow()
            self.initializeNametag3d()
        self.setHat(*oldHat)
        self.setGlasses(*oldGlasses)
        self.setBackpack(*oldBackpack)
        self.setShoes(*oldShoes)
        self.setBlend(frameBlend=ClientSettings.SmoothAnimations.get())
        self.setLODAnimation(750, 20, 0.4)

    def parentToonParts(self):
        if self.hasLOD():
            for lodName in self.getLODNames():
                if base.config.GetBool('want-new-anims', 1):
                    if not self.getPart('torso', lodName).find('**/def_head').isEmpty():
                        self.attach('head', 'torso', 'def_head', lodName)
                    else:
                        self.attach('head', 'torso', 'joint_head', lodName)
                else:
                    self.attach('head', 'torso', 'joint_head', lodName)
                self.attach('torso', 'legs', 'joint_hips', lodName)

        else:
            self.attach('head', 'torso', 'joint_head')
            self.attach('torso', 'legs', 'joint_hips')

    def unparentToonParts(self):
        if self.hasLOD():
            for lodName in self.getLODNames():
                self.getPart('head', lodName).reparentTo(self.getLOD(lodName))
                self.getPart('torso', lodName).reparentTo(self.getLOD(lodName))
                self.getPart('legs', lodName).reparentTo(self.getLOD(lodName))

        else:
            self.getPart('head').reparentTo(self.getGeomNode())
            self.getPart('torso').reparentTo(self.getGeomNode())
            self.getPart('legs').reparentTo(self.getGeomNode())

    def setLODs(self):
        self.setLODNode()
        if ClientSettings.AvatarLODs.get():
            levelOneIn = base.config.GetInt('lod1-in', 20)
            levelOneOut = base.config.GetInt('lod1-out', 0)
            levelTwoIn = base.config.GetInt('lod2-in', 80)
            levelTwoOut = base.config.GetInt('lod2-out', 20)
            levelThreeIn = base.config.GetInt('lod3-in', 280)
            levelThreeOut = base.config.GetInt('lod3-out', 80)
        else:
            levelOneIn = base.config.GetInt('lod1-in', 2000)
            levelOneOut = base.config.GetInt('lod1-out', 0)
            levelTwoIn = base.config.GetInt('lod2-in', 8000)
            levelTwoOut = base.config.GetInt('lod2-out', 2000)
            levelThreeIn = base.config.GetInt('lod3-in', 28000)
            levelThreeOut = base.config.GetInt('lod3-out', 8000)
        self.addLOD(1000, levelOneIn, levelOneOut)
        self.addLOD(500, levelTwoIn, levelTwoOut)
        self.addLOD(250, levelThreeIn, levelThreeOut)

    def generateToon(self):
        self.setLODs()
        self.generateToonLegs()
        self.generateToonHead()
        self.generateToonTorso()
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.setupToonNodes()

    def setupToonNodes(self):
        rightHand = NodePath('rightHand')
        self.rightHand = None
        self.rightHands = []
        leftHand = NodePath('leftHand')
        self.leftHands = []
        self.leftHand = None
        for lodName in self.getLODNames():
            hand = self.getPart('torso', lodName).find('**/joint_Rhold')
            if base.config.GetBool('want-new-anims', 1):
                if not self.getPart('torso', lodName).find('**/def_joint_right_hold').isEmpty():
                    hand = self.getPart('torso', lodName).find('**/def_joint_right_hold')
            else:
                hand = self.getPart('torso', lodName).find('**/joint_Rhold')
            self.rightHands.append(hand)
            rightHand = rightHand.instanceTo(hand)
            if base.config.GetBool('want-new-anims', 1):
                if not self.getPart('torso', lodName).find('**/def_joint_left_hold').isEmpty():
                    hand = self.getPart('torso', lodName).find('**/def_joint_left_hold')
            else:
                hand = self.getPart('torso', lodName).find('**/joint_Lhold')
            self.leftHands.append(hand)
            leftHand = leftHand.instanceTo(hand)
            if self.rightHand == None:
                self.rightHand = rightHand
            if self.leftHand == None:
                self.leftHand = leftHand

        self.headParts = self.findAllMatches('**/__Actor_head')
        self.legsParts = self.findAllMatches('**/__Actor_legs')
        self.hipsParts = self.legsParts.findAllMatches('**/joint_hips')
        self.torsoParts = self.hipsParts.findAllMatches('**/__Actor_torso')
        self.setBlend(frameBlend=ClientSettings.AvatarLODs.get())
        self.setLODAnimation(750, 20, 0.4)
        return

    def initializeBodyCollisions(self, collIdStr):
        Avatar.Avatar.initializeBodyCollisions(self, collIdStr)
        if not self.ghostMode:
            self.collNode.setCollideMask(self.collNode.getIntoCollideMask() | ToontownGlobals.PieBitmask)

    def getBookActors(self):
        if self.__bookActors:
            return self.__bookActors
        bookActor = Actor.Actor('phase_3.5/models/props/book-mod', {'book': 'phase_3.5/models/props/book-chan'})
        bookActor2 = Actor.Actor(other=bookActor)
        bookActor3 = Actor.Actor(other=bookActor)
        self.__bookActors = [bookActor, bookActor2, bookActor3]
        self.parentBooksToRightHands()

        return self.__bookActors

    def getHoleActors(self):
        if self.__holeActors:
            return self.__holeActors
        holeActor = Actor.Actor('phase_3.5/models/props/portal-mod', {'hole': 'phase_3.5/models/props/portal-chan'})
        holeActor2 = Actor.Actor(other=holeActor)
        holeActor3 = Actor.Actor(other=holeActor)
        self.__holeActors = [holeActor, holeActor2, holeActor3]
        for ha in self.__holeActors:
            if hasattr(self, 'uniqueName'):
                holeName = self.uniqueName('toon-portal')
            else:
                holeName = 'toon-portal'
            ha.setName(holeName)

        return self.__holeActors

    def rescaleToon(self):
        animalStyle = self.style.getAnimal()
        bodyScale = ToontownGlobals.toonBodyScales[animalStyle]
        headScale = ToontownGlobals.toonHeadScales[animalStyle]
        self.setAvatarScale(bodyScale)
        for lod in self.getLODNames():
            self.getPart('head', lod).setScale(headScale)

    def getBodyScale(self):
        animalStyle = self.style.getAnimal()
        bodyScale = ToontownGlobals.toonBodyScales[animalStyle]
        return bodyScale

    def resetHeight(self):
        # Create a default height for us to use as a fallback
        height = 1.0

        # Get the Toon's current transformation
        transformationIndex = self.getActiveTransformationIndex()

        # If the player is not transformed, get their height based on normal body proportions
        if hasattr(self, 'style') and self.style and transformationIndex == ToontownGlobals.TransformationToon:
            animal = self.style.getAnimal()
            bodyScale = ToontownGlobals.toonBodyScales[animal]
            headScale = ToontownGlobals.toonHeadScales[animal][2]
            shoulderHeight = ToontownGlobals.legHeightDict[self.style.legs] * bodyScale + \
                             ToontownGlobals.torsoHeightDict[self.style.torso] * bodyScale
            height = shoulderHeight + ToontownGlobals.headHeightDict[self.style.head] * headScale
            self.shoulderHeight = shoulderHeight

            # Adjust height for cheesy effects
            if self.cheesyEffect == ToontownGlobals.CEBigToon or self.cheesyEffect == ToontownGlobals.CEBigWhite:
                height *= ToontownGlobals.BigToonScale
            elif self.cheesyEffect == ToontownGlobals.CESmallToon:
                height *= ToontownGlobals.SmallToonScale
            elif self.cheesyEffect == ToontownGlobals.CELongLegs:
                height *= ToontownGlobals.LongLegsScale
            elif self.cheesyEffect == ToontownGlobals.CENoTorso:
                offset = ToontownGlobals.torsoToOffset[self.style.torso[0]]
                height += offset

        # If we're transformed as a cog, base height off of the suit height
        elif transformationIndex == ToontownGlobals.TransformationCog:
            height = self.suit.getHeight()

        # If we're transformed as a classic character, base height off of pre-defined values according to which character we are
        elif transformationIndex == ToontownGlobals.TransformationClassicChar:
            height = ToontownGlobals.TransformationCharExtra.get(self.char._name, 0)

        # If we're transformed as a doodle, base height off hardcoded doodle height
        elif transformationIndex == ToontownGlobals.TransformationDoodle:
            height = 2.0

        # If we're transformed as a goon, base height off hardcoded goon height
        elif transformationIndex == ToontownGlobals.TransformationGoon:
            height = 4.0

        # If we're transformed as a doodle, base height off hardcoded prop height
        # TODO: Get bounds of prop in future and base height off of that instead for consistency
        elif transformationIndex == ToontownGlobals.TransformationProp:
            height = 1.75

        # If we're transformed as a boss, base height off hardcoded boss height
        elif transformationIndex == ToontownGlobals.TransformationBoss:
            height = 4.5

        # If we're transformed as a fish, base height off of pre-defined values according to which fish we are
        elif transformationIndex == ToontownGlobals.TransformationFish:
            height = ToontownGlobals.TransformationFishExtra.get(self.getTransformationsIndex(ToontownGlobals.TransformationFish) - 2)[ToontownGlobals.TransformationExtraNametagHeight]

        # If we're transformed as a misc character, base height off of pre-defined values according to which character we are
        elif transformationIndex == ToontownGlobals.TransformationMisc:
            index = self.getTransformationsIndex(ToontownGlobals.TransformationMisc) - 1
            height = ToontownGlobals.TransformationMiscExtra.get(index)

        # If we're transformed as a butterfly, base height off hardcoded butterfly height
        elif transformationIndex == ToontownGlobals.TransformationButterfly:
            height = 2.0

        # If we're transformed as a street prop, base height off hardcoded height
        elif transformationIndex == ToontownGlobals.TransformationStreet:
            height = 2.0

        # Adjust height based off scale modified with Scale Magic Word
        if self.toonScale != 1:
            height *= self.toonScale

        # Set the height
        self.setHeight(height)

    def generateToonLegs(self, copy = 1):
        legStyle = self.style.legs
        filePrefix = LegDict.get(legStyle)
        if filePrefix is None:
            self.notify.error('unknown leg style: %s' % legStyle)
        self.loadModel('phase_3' + filePrefix + '1000', 'legs', '1000', copy)
        self.loadModel('phase_3' + filePrefix + '500', 'legs', '500', copy)
        self.loadModel('phase_3' + filePrefix + '250', 'legs', '250', copy)
        if not copy:
            self.showPart('legs', '1000')
            self.showPart('legs', '500')
            self.showPart('legs', '250')
        self.loadAnims(LegsAnimDict[legStyle], 'legs', '1000')
        self.loadAnims(LegsAnimDict[legStyle], 'legs', '500')
        self.loadAnims(LegsAnimDict[legStyle], 'legs', '250')
        self.findAllMatches('**/boots_short').stash()
        self.findAllMatches('**/boots_long').stash()
        self.findAllMatches('**/shoes').stash()
        return

    def swapToonLegs(self, legStyle, copy = 1):
        self.unparentToonParts()
        self.removePart('legs', '1000')
        self.removePart('legs', '500')
        self.removePart('legs', '250')
        if 'legs' in self._Actor__commonBundleHandles:
            del self._Actor__commonBundleHandles['legs']
        self.style.legs = legStyle
        self.generateToonLegs(copy)
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        del self.shadowJoint
        self.initializeDropShadow()
        self.initializeNametag3d()
        self.setBlend(frameBlend=ClientSettings.SmoothAnimations.get())
        self.setLODAnimation(750, 20, 0.4)

    def generateToonTorso(self, copy = 1, genClothes = 1):
        torsoStyle = self.style.torso
        filePrefix = TorsoDict.get(torsoStyle)
        if filePrefix is None:
            self.notify.error('unknown torso style: %s' % torsoStyle)
        self.loadModel('phase_3' + filePrefix + '1000', 'torso', '1000', copy)
        if len(torsoStyle) == 1:
            self.loadModel('phase_3' + filePrefix + '1000', 'torso', '500', copy)
            self.loadModel('phase_3' + filePrefix + '1000', 'torso', '250', copy)
        else:
            self.loadModel('phase_3' + filePrefix + '500', 'torso', '500', copy)
            self.loadModel('phase_3' + filePrefix + '250', 'torso', '250', copy)
        if not copy:
            self.showPart('torso', '1000')
            self.showPart('torso', '500')
            self.showPart('torso', '250')
        self.loadAnims(TorsoAnimDict[torsoStyle], 'torso', '1000')
        self.loadAnims(TorsoAnimDict[torsoStyle], 'torso', '500')
        self.loadAnims(TorsoAnimDict[torsoStyle], 'torso', '250')
        if genClothes == 1 and not len(torsoStyle) == 1:
            self.generateToonClothes()
        return

    def swapToonTorso(self, torsoStyle, copy = 1, genClothes = 1):
        self.unparentToonParts()
        self.removePart('torso', '1000')
        self.removePart('torso', '500')
        self.removePart('torso', '250')
        if 'torso' in self._Actor__commonBundleHandles:
            del self._Actor__commonBundleHandles['torso']
        self.style.torso = torsoStyle
        self.generateToonTorso(copy, genClothes)
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.setupToonNodes()
        self.parentBooksToRightHands()
        self.generateBackpack()

    def generateToonHead(self, copy = 1):
        headHeight = ToonHead.generateToonHead(self, copy, self.style, ('1000', '500', '250'))
        if self.style.getAnimal() == 'dog':
            self.loadAnims(HeadAnimDict[self.style.head], 'head', '1000')
            self.loadAnims(HeadAnimDict[self.style.head], 'head', '500')
            self.loadAnims(HeadAnimDict[self.style.head], 'head', '250')

    def swapToonHead(self, headStyle, copy = 1):
        self.stopLookAroundNow()
        self.eyelids.request('open')
        self.unparentToonParts()
        self.removePart('head', '1000')
        self.removePart('head', '500')
        self.removePart('head', '250')
        if 'head' in self._Actor__commonBundleHandles:
            del self._Actor__commonBundleHandles['head']
        self.style.head = headStyle
        self.generateToonHead(copy)
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.eyelids.request('open')
        self.startLookAround()

    def generateToonColor(self):
        ToonHead.generateToonColor(self, self.style)
        armColor = self.style.getArmColor()
        gloveColor = self.style.getGloveColor()
        legColor = self.style.getLegColor()
        for lodName in self.getLODNames():
            torso = self.getPart('torso', lodName)
            if len(self.style.torso) == 1:
                parts = torso.findAllMatches('**/torso*')
                parts.setColor(armColor)
            for pieceName in ('arms', 'neck'):
                piece = torso.find('**/' + pieceName)
                piece.setColor(armColor)

            hands = torso.find('**/hands')
            hands.setColor(gloveColor)
            legs = self.getPart('legs', lodName)
            for pieceName in ('legs', 'feet'):
                piece = legs.find('**/%s;+s' % pieceName)
                piece.setColor(legColor)

        if self.cheesyEffect == ToontownGlobals.CEGreenToon:
            self.reapplyCheesyEffect()

        torsoPieces = self.getPieces(('torso', ('arms', 'neck')))
        if len(self.style.torso) == 1:
            torsoPieces = self.getPieces(('torso', ('arms', 'neck', 'torso')))
        glovePieces = []
        for lodName in self.getLODNames():
            torso = self.getPart('torso', lodName)
            glovePieces.append(torso.find('**/hands'))
        legPieces = self.getPieces(('legs', ('legs', 'feet')))
        if self.style.head[0] == 'h' or self.style.head[0] == 'p':
            headPieces = self.getPieces(('head', '*head*'))
            if self.style.head[0] == 'd':
                for h in headPieces:
                    if str(h).lower().__contains__('muzzle'):
                        headPieces.remove(h)
        elif self.style.head[0] == 'd':
            headPieces = []
            for h in self.findAllMatches('**/head-front'):
                headPieces.append(h)
            for h in self.findAllMatches('**/head'):
                headPieces.append(h)
        else:
            headPieces = self.getPieces(('head', ('*head*', '*ear*')))


    def swapToonColor(self, dna):
        self.setStyle(dna)
        self.generateToonColor()

    def __swapToonClothes(self, dna):
        self.setStyle(dna)
        self.generateToonClothes(fromNet=1)

    def sendLogSuspiciousEvent(self, msg):
        pass

    def generateToonClothes(self, fromNet = 0):
        swappedTorso = 0
        if self.hasLOD():
            if len(self.style.torso) < 2:
                return 0
            if self.style.getGender() == 'f' and fromNet == 0:
                try:
                    bottomPair = ToonDNA.GirlBottoms[self.style.botTex]
                except:
                    bottomPair = ToonDNA.GirlBottoms[0]

                if self.style.torso[1] == 's' and bottomPair[1] == ToonDNA.SKIRT:
                    self.swapToonTorso(self.style.torso[0] + 'd', genClothes=0)
                    swappedTorso = 1
                elif self.style.torso[1] == 'd' and bottomPair[1] == ToonDNA.SHORTS:
                    self.swapToonTorso(self.style.torso[0] + 's', genClothes=0)
                    swappedTorso = 1
            try:
                texName = ToonDNA.Shirts[self.style.topTex]
            except:
                texName = ToonDNA.Shirts[0]

            shirtTex = loader.loadTexture(texName, okMissing = True)
            if shirtTex is None:
                self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                shirtTex = loader.loadTexture(ToonDNA.Shirts[0])
            shirtTex.setMinfilter(Texture.FTLinearMipmapLinear)
            shirtTex.setMagfilter(Texture.FTLinear)
            try:
                shirtColor = self.style.topTexColor
            except:
                shirtColor = ToonDNA.ClothesColors[0]

            try:
                texName = ToonDNA.Sleeves[self.style.sleeveTex]
            except:
                texName = ToonDNA.Sleeves[0]

            sleeveTex = loader.loadTexture(texName, okMissing = True)
            if sleeveTex is None:
                self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                sleeveTex = loader.loadTexture(ToonDNA.Sleeves[0])
            sleeveTex.setMinfilter(Texture.FTLinearMipmapLinear)
            sleeveTex.setMagfilter(Texture.FTLinear)
            try:
                sleeveColor = self.style.sleeveTexColor
            except:
                sleeveColor = ToonDNA.ClothesColors[0]

            if self.style.getGender() == 'm':
                try:
                    texName = ToonDNA.BoyShorts[self.style.botTex]
                except:
                    texName = ToonDNA.BoyShorts[0]

            else:
                try:
                    texName = ToonDNA.GirlBottoms[self.style.botTex][0]
                except:
                    texName = ToonDNA.GirlBottoms[0][0]

            bottomTex = loader.loadTexture(texName, okMissing = True)
            if bottomTex is None:
                self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                if self.style.getGender() == 'm':
                    bottomTex = loader.loadTexture(ToonDNA.BoyShorts[0])
                else:
                    bottomTex = loader.loadTexture(ToonDNA.GirlBottoms[0][0])
            bottomTex.setMinfilter(Texture.FTLinearMipmapLinear)
            bottomTex.setMagfilter(Texture.FTLinear)
            try:
                bottomColor = self.style.botTexColor
            except:
                bottomColor = ToonDNA.ClothesColors[0]

            darkBottomColor = Vec4(bottomColor) * 0.5
            darkBottomColor.setW(1.0)
            for lodName in self.getLODNames():
                thisPart = self.getPart('torso', lodName)
                top = thisPart.find('**/torso-top')
                top.setTexture(shirtTex, 1)
                top.setColor(shirtColor)
                sleeves = thisPart.find('**/sleeves')
                sleeves.setTexture(sleeveTex, 1)
                sleeves.setColor(sleeveColor)
                bottoms = thisPart.findAllMatches('**/torso-bot')
                for bottomNum in range(0, bottoms.getNumPaths()):
                    bottom = bottoms.getPath(bottomNum)
                    bottom.setTexture(bottomTex, 1)
                    bottom.setColor(bottomColor)

                caps = thisPart.findAllMatches('**/torso-bot-cap')
                caps.setColor(darkBottomColor)

        return swappedTorso

    def generateBackpack(self, fromRTM = False):
        backpack = self.getBackpack()
        if backpack[0] >= len(ToonDNA.BackpackModels):
            self.sendLogSuspiciousEvent('tried to put a wrong backpack idx %d' % backpack[0])
            return
        if len(self.backpackNodes) > 0:
            for backpackNode in self.backpackNodes:
                backpackNode.removeNode()

            self.backpackNodes = []
        if backpack[0] != 0:
            geom = loader.loadModel(ToonDNA.BackpackModels[backpack[0]], okMissing=True)
            if geom:
                if backpack[1] != 0:
                    texName = ToonDNA.BackpackTextures[backpack[1]]
                    tex = loader.loadTexture(texName, okMissing = True)
                    if tex is None:
                        self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                    else:
                        tex.setMinfilter(Texture.FTLinearMipmapLinear)
                        tex.setMagfilter(Texture.FTLinear)
                        geom.setTexture(tex, 1)
                if fromRTM:
                    importlib.reload(AccessoryGlobals)
                transOffset = None
                if AccessoryGlobals.ExtendedBackpackTransTable.get(backpack[0]):
                    transOffset = AccessoryGlobals.ExtendedBackpackTransTable[backpack[0]].get(self.style.torso[:1])
                if transOffset is None:
                    transOffset = AccessoryGlobals.BackpackTransTable.get(self.style.torso[:1])
                    if transOffset is None:
                        return
                geom.setPos(transOffset[0][0], transOffset[0][1], transOffset[0][2])
                geom.setHpr(transOffset[1][0], transOffset[1][1], transOffset[1][2])
                geom.setScale(transOffset[2][0], transOffset[2][1], transOffset[2][2])
                nodes = self.findAllMatches('**/def_joint_attachFlower')
                for node in nodes:
                    theNode = node.attachNewNode('backpackNode')
                    self.backpackNodes.append(theNode)
                    geom.instanceTo(theNode)

    def generateShoes(self):
        shoes = self.getShoes()
        if shoes[0] >= len(ToonDNA.ShoesModels):
            self.sendLogSuspiciousEvent('tried to put a wrong shoes idx %d' % shoes[0])
            return
        self.findAllMatches('**/feet;+s').stash()
        self.findAllMatches('**/boots_short;+s').stash()
        self.findAllMatches('**/boots_long;+s').stash()
        self.findAllMatches('**/shoes;+s').stash()
        geoms = self.findAllMatches('**/%s;+s' % ToonDNA.ShoesModels[shoes[0]])
        for geom in geoms:
            geom.unstash()

        if shoes[0] != 0:
            for geom in geoms:
                texName = ToonDNA.ShoesTextures[shoes[1]]
                if self.style.legs == 'l' and shoes[0] == 3:
                    texName = texName[:-4] + 'LL.png'
                tex = loader.loadTexture(texName, okMissing = True)
                if tex is None:
                    self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                else:
                    tex.setMinfilter(Texture.FTLinearMipmapLinear)
                    tex.setMagfilter(Texture.FTLinear)
                    geom.setTexture(tex, 1)

        return

    def generateToonAccessories(self):
        self.generateHat(*self.hat)
        self.generateGlasses(*self.glasses)
        self.generateBackpack()
        self.generateShoes()

    def setHat(self, hatIdx, textureIdx, colorIdx, fromRTM = False):
        self.hat = (hatIdx, textureIdx, colorIdx)
        self.generateHat(*self.hat)

    def getHat(self):
        return self.hat

    def setGlasses(self, glassesIdx, textureIdx, colorIdx, fromRTM = False):
        self.glasses = (glassesIdx, textureIdx, colorIdx)
        self.generateGlasses(*self.glasses)

    def getGlasses(self):
        return self.glasses

    def setBackpack(self, backpackIdx, textureIdx, colorIdx, fromRTM = False):
        self.backpack = (backpackIdx, textureIdx, colorIdx)
        self.generateBackpack(fromRTM=fromRTM)

    def getBackpack(self):
        return self.backpack

    def setShoes(self, shoesIdx, textureIdx, colorIdx):
        self.shoes = (shoesIdx, textureIdx, colorIdx)
        self.generateShoes()

    def getShoes(self):
        return self.shoes

    def getDialogueArray(self):
        animalType = self.style.getType()
        transformationIndex = self.getActiveTransformationIndex()
        animalSound = self.getAnimalSound()

        if animalSound in ToontownGlobals.ValidAnimalTypes:
            animalType = animalSound
        elif self.disguiseType in ToontownGlobals.PutOnSuitSkelecog:
            animalType = 'skeleton'
        elif self.disguiseType in ToontownGlobals.PutOnSuitCogs:
            animalType = 'suit'
        elif transformationIndex == ToontownGlobals.TransformationClassicChar:
            animalType = self.char.style.getCharName()
        elif transformationIndex == ToontownGlobals.TransformationDoodle:
            animalType = 'doodle'
        elif transformationIndex == ToontownGlobals.TransformationGoon:
            animalType = 'goon'
        elif transformationIndex == ToontownGlobals.TransformationBoss:
            animalType = 'boss'
        elif transformationIndex == ToontownGlobals.TransformationFish:
            animalType = self.getTransformationsIndex(ToontownGlobals.TransformationFish)
        elif transformationIndex == ToontownGlobals.TransformationMisc:
            index = self.getTransformationsIndex(ToontownGlobals.TransformationMisc) - 1
            if index == ToontownGlobals.TransformationMiscStatue:
                animalType = 'boss'
            elif index == ToontownGlobals.TransformationMiscPanda:
                animalType = 'bear'
            elif index == ToontownGlobals.TransformationMiscChaser:
                animalType = 'suit'
            elif index == ToontownGlobals.TransformationMiscCheese:
                animalType = 'suit'
            elif index == ToontownGlobals.TransformationMiscMickey:
                animalType = 'mickey'
        elif transformationIndex == ToontownGlobals.TransformationProp:
            if 'trolley' in self.propName:
                animalType = 'trolley'

        if animalType == 'dog':
            dialogueArray = DogDialogueArray
        elif animalType == 'cat':
            dialogueArray = CatDialogueArray
        elif animalType == 'horse':
            dialogueArray = HorseDialogueArray
        elif animalType == 'mouse':
            dialogueArray = MouseDialogueArray
        elif animalType == 'rabbit':
            dialogueArray = RabbitDialogueArray
        elif animalType == 'duck':
            dialogueArray = DuckDialogueArray
        elif animalType == 'monkey':
            dialogueArray = MonkeyDialogueArray
        elif animalType == 'bear':
            dialogueArray = BearDialogueArray
        elif animalType == 'pig':
            dialogueArray = PigDialogueArray
        elif animalType == 'gyro':
            dialogueArray = GyroDialogueArray
        elif animalType == 'scrooge':
            dialogueArray = ScroogeDialogueArray
        elif animalType in ('skelecog', 'skeleton', 'goon'):
            dialogueArray = SkeletonDialogueArray
        elif animalType in ('suit', 'cog'):
            dialogueArray = SuitDialogueArray
        elif animalType in ('mickey', 'vampire_mickey'):
            dialogueArray = MickeyDialogueArray
        elif animalType in ('minnie', 'witch_minnie'):
            dialogueArray = MinnieDialogueArray
        elif animalType in ('goofy', 'super_goofy'):
            dialogueArray = GoofyDialogueArray
        elif animalType in ('donald-wheel', 'franken_donald', 'donald_old'):
            dialogueArray = DonaldDialogueArray
        elif animalType in ('daisy', 'sockHop_daisy'):
            dialogueArray = DaisyDialogueArray
        elif animalType in ('pluto', 'western_pluto'):
            dialogueArray = PlutoDialogueArray
        elif animalType in ('chip', 'police_chip'):
            dialogueArray = ChipDialogueArray
        elif animalType in ('dale', 'jailbird_dale'):
            dialogueArray = DaleDialogueArray
        elif animalType in ('donald', 'clarabelle'):
            dialogueArray = None
        elif animalType == 'doodle':
            dialogueArray = DoodleDialogueArray
        elif animalType == 'boss':
            dialogueArray = BossDialogueArray
        elif transformationIndex == ToontownGlobals.TransformationFish:
            dialogueArray = FishDialogueArrays.get(animalType - 2)
        elif animalType == 'trolley':
            dialogueArray = TrolleyDialogueArray
        else:
            dialogueArray = None
        return dialogueArray

    def __getSpeciesTypeForTTS(self):
        if hasattr(self, 'style'):
            return self.style.getType()
        self.notify.warning("__getSpeciesTypeForTTS(): No attribute 'style'. Using default value.")
        return 'unknown'

    def playTTSDarwinVoice(self, chatString):
        species = self.__getSpeciesTypeForTTS()
        voice = self.getTTSDarwinVoice(species)
        self.curTTS = Popen(['say', voice, chatString])

    def playTTSVoice(self, chatString):
        species = self.__getSpeciesTypeForTTS()
        pitch = self.getTTSPitch(species)
        volume = '-a' + str(self.getTTSVolume())
        self.curTTS = Popen([base.textToSpeechPath, pitch, volume, '-ven', chatString])

    def getTTSDarwinVoice(self, species):
        if species in list(ToontownGlobals.Species2Voice.keys()):
            return ToontownGlobals.Species2Voice[species]
        return ToontownGlobals.DefaultVoice

    def getTTSPitch(self, species):
        if species in list(ToontownGlobals.Species2Pitch.keys()):
            return '-p' + str(ToontownGlobals.Species2Pitch[species])
        return Avatar.Avatar.getTTSPitch(self)

    def getShadowJoint(self):
        if hasattr(self, 'shadowJoint'):
            return self.shadowJoint
        shadowJoint = NodePath('shadowJoint')
        for lodName in self.getLODNames():
            joint = self.getPart('legs', lodName).find('**/joint_shadow')
            shadowJoint = shadowJoint.instanceTo(joint)

        self.shadowJoint = shadowJoint
        return shadowJoint

    def getNametagJoints(self):
        joints = []
        for lodName in self.getLODNames():
            bundle = self.getPartBundle('legs', lodName)
            joint = bundle.findChild('joint_nameTag')
            if joint:
                joints.append(joint)

        return joints

    def getRightHands(self):
        return self.rightHands

    def getLeftHands(self):
        return self.leftHands

    def getHeadParts(self):
        return self.headParts

    def getHipsParts(self):
        return self.hipsParts

    def getTorsoParts(self):
        return self.torsoParts

    def getLegsParts(self):
        return self.legsParts

    def findSomethingToLookAt(self):
        if self.randGen.random() < 0.1 or not hasattr(self, 'cr'):
            x = self.randGen.choice((-0.8,
             -0.5,
             0,
             0.5,
             0.8))
            y = self.randGen.choice((-0.5,
             0,
             0.5,
             0.8))
            self.lerpLookAt(Point3(x, 1.5, y), blink=1)
            return
        nodePathList = []
        for id, obj in list(self.cr.doId2do.items()):
            if hasattr(obj, 'getStareAtNodeAndOffset') and obj != self:
                node, offset = obj.getStareAtNodeAndOffset()
                if node.getY(self) > 0.0:
                    nodePathList.append((node, offset))

        if nodePathList:
            nodePathList.sort(key=cmp_to_key(lambda x, y: cmp(x[0].getDistance(self), y[0].getDistance(self))))
            if len(nodePathList) >= 2:
                if self.randGen.random() < 0.9:
                    chosenNodePath = nodePathList[0]
                else:
                    chosenNodePath = nodePathList[1]
            else:
                chosenNodePath = nodePathList[0]
            self.lerpLookAt(chosenNodePath[0].getPos(self), blink=1)
        else:
            ToonHead.findSomethingToLookAt(self)

    def setForceJumpIdle(self, value):
        self.forceJumpIdle = value

    def setupPickTrigger(self):
        Avatar.Avatar.setupPickTrigger(self)
        torso = self.getPart('torso', '1000')
        if torso == None:
            return 0
        self.pickTriggerNp.reparentTo(torso)
        size = self.style.getTorsoSize()
        if size == 'short':
            self.pickTriggerNp.setPosHprScale(0, 0, 0.5, 0, 0, 0, 1.5, 1.5, 2)
        elif size == 'medium':
            self.pickTriggerNp.setPosHprScale(0, 0, 0.5, 0, 0, 0, 1, 1, 2)
        else:
            self.pickTriggerNp.setPosHprScale(0, 0, 1, 0, 0, 0, 1, 1, 2)
        return 1

    def showBooks(self):
        for bookActor in self.getBookActors():
            bookActor.show()

    def hideBooks(self):
        for bookActor in self.getBookActors():
            bookActor.hide()

    def parentBooksToRightHands(self):
        hands: list[NodePath] = self.getRightHands()
        for bookActor, hand in zip(self.__bookActors, hands):
            bookActor.setBlend(frameBlend=ClientSettings.SmoothAnimations.get())
            bookActor.reparentTo(hand)
            bookActor.hide()

    def getWake(self):
        if not self.wake:
            self.wake = Wake.Wake(render, self)
        return self.wake

    def getJar(self):
        if not self.jar:
            self.jar = loader.loadModel('phase_5.5/models/estate/jellybeanJar')
            self.jar.setP(290.0)
            self.jar.setY(0.5)
            self.jar.setZ(0.5)
            self.jar.setScale(0.0)
        return self.jar

    def removeJar(self):
        if self.jar:
            self.jar.removeNode()
            self.jar = None
        return

    def setSpeed(self, forwardSpeed: float, rotateSpeed: float, slideSpeed: float = 0) -> int | None:
        # todo: instead of playing footestps at a fixed loop, play them when the feet are supposed to touch the ground
        pastRot = self.rotateSpeed
        self.forwardSpeed = forwardSpeed
        self.rotateSpeed = rotateSpeed
        self.slideSpeed = slideSpeed
        action = None
        rate: float = -1
        if self.standWalkRunReverse is not None:
            if forwardSpeed >= ToontownGlobals.RunCutOff:
                action = ToontownGlobals.RUN_INDEX
                # scale the play rate by how fast we're actually going compared ot the fwd speed
                # makes it faster if we're faster, slow if we're slower.
                rate = forwardSpeed / ToontownGlobals.ToonForwardSpeed
            elif forwardSpeed > ToontownGlobals.WalkCutOff:
                action = ToontownGlobals.WALK_INDEX
                rate = forwardSpeed / ToontownGlobals.ToonReverseSpeed
            elif forwardSpeed < -ToontownGlobals.WalkCutOff:
                action = ToontownGlobals.REVERSE_INDEX
            elif rotateSpeed != 0.0:
                action = ToontownGlobals.WALK_INDEX
            elif slideSpeed > ToontownGlobals.WalkCutOff:
                action = ToontownGlobals.STRAFE_RIGHT_INDEX
            elif slideSpeed < -ToontownGlobals.WalkCutOff:
                action = ToontownGlobals.STRAFE_LEFT_INDEX
            else:
                action = ToontownGlobals.STAND_INDEX

            self.forcedRate = rate

            if __debug__:
                onScreenDebug.add('toon adj LocomotionPlayRate', self.forcedRate)

            # =======================================
            # # Adjust strafe angle
            # if abs(slideSpeed) < ToontownGlobals.WalkCutOff:
            #     self.resetStrafeRotation()
            # else:
            #     # Calculate the angle based on the toon's velocity
            #     velVec = Vec2(slideSpeed, forwardSpeed)
            #     velVec.normalize()
            #     angle = rad2Deg(math.atan2(velVec.getY(), velVec.getX())) - 90.0
            #
            #     # We want to invert this if the toon is walking backwards
            #     if action == ToontownGlobals.REVERSE_INDEX:
            #         angle -= 180.0
            #
            #     self.setStrafeRotation(angle)
            # # =======================================

            anim, rate = self.standWalkRunReverse[action]
            if self.forcedRate != -1:
                rate = self.forcedRate
            pastAnim, pastRate = self.playingAnim, self.playingRate
            self.motion.enter()
            self.motion.setState(anim, rate)
            if anim != self.playingAnim and not self.tpose:
                transformationIndex = self.getActiveTransformationIndex()
                self.playingAnim = anim
                self.playingRate = rate
                self.stop()
                self.loop(anim)
                self.setPlayRate(rate, anim)
                if transformationIndex == ToontownGlobals.TransformationCog:
                    rightHand = self.suit.rightHand
                    numChildren = rightHand.getNumChildren()
                    if numChildren > 0:
                        anim = 'tray-' + anim
                        if anim == 'tray-run':
                            anim = 'tray-walk'
                    self.suit.stop()
                    self.suit.loop(anim)
                    self.suit.setPlayRate(rate, anim)
                elif transformationIndex == ToontownGlobals.TransformationClassicChar:
                    self.char.stop()
                    self.char.loop(anim)
                    self.char.setPlayRate(rate, anim)
                elif transformationIndex == ToontownGlobals.TransformationDoodle:
                    self.pet.stop()
                    self.pet.loop(anim)
                    self.pet.setPlayRate(rate, anim)
                elif transformationIndex == ToontownGlobals.TransformationGoon:
                    self.goon.stop()
                    if anim == 'neutral':
                        self.goon.pose(anim, 96)
                    else:
                        self.goon.loop(anim)
                    self.goon.setPlayRate(rate, anim)
                elif transformationIndex == ToontownGlobals.TransformationBoss:
                    if self.playingAnim != pastAnim or self.playingRate != pastRate or self.rotateSpeed != pastRot:
                        if self.track:
                            self.track.finish()
                        if rotateSpeed != 0:
                            self.track = Sequence(Parallel(self.boss.rollLeftTreads(0.25, rotateSpeed/25),
                                                           self.boss.rollRightTreads(0.25, -rotateSpeed/25)))
                        else:
                            self.track = Sequence(Parallel(self.boss.rollLeftTreads(0.5, -forwardSpeed/5),
                                                           self.boss.rollRightTreads(0.5, -forwardSpeed/5)))
                        self.track.loop()
                elif transformationIndex == ToontownGlobals.TransformationFish and not self.fish.getCurrentAnim():
                    self.fish.stop()
                    transformationIndex = self.getTransformationsIndex(ToontownGlobals.TransformationFish)
                    fishInfo = ToontownGlobals.TransformationFishExtra.get(transformationIndex)
                    if transformationIndex == 10:
                        self.fish.pingpong(fishInfo[ToontownGlobals.TransformationExtraAnimation], fromFrame=40, toFrame=55)
                    else:
                        self.fish.loop(fishInfo[ToontownGlobals.TransformationExtraAnimation])
                elif transformationIndex == ToontownGlobals.TransformationButterfly:
                    self.butterfly.stop()
                    self.butterfly.loop('glide')
                elif transformationIndex == ToontownGlobals.TransformationMisc:
                    self.misc.stop()
                    self.misc.loop(anim)
                    self.misc.setPlayRate(rate, anim)
            elif rate != self.playingRate:
                self.playingRate = rate
                if not self.getTransformationsIndex(ToontownGlobals.TransformationCog):
                    self.setPlayRate(rate, anim)
                else:
                    self.suit.setPlayRate(rate, anim)
            showWake, wakeWaterHeight = ZoneUtil.getWakeInfo()
            if showWake and self.getZ(render) < wakeWaterHeight and abs(forwardSpeed) > ToontownGlobals.WalkCutOff:
                currT = globalClock.getFrameTime()
                deltaT = currT - self.lastWakeTime
                if action == ToontownGlobals.RUN_INDEX and deltaT > ToontownGlobals.WakeRunDelta or deltaT > ToontownGlobals.WakeWalkDelta:
                    self.getWake().createRipple(wakeWaterHeight, rate=1, startFrame=4)
                    self.lastWakeTime = currT
        return action

    def setStrafeRotation(self, angle = 0.0):
        """
        Directly modify the avatar geom nodes to create a strafing animation
        This currently only does anything special for toons, transformations will just fully rotate the entire body
        :param angle: Angle of rotation
        :type angle: float
        """
        if not self.getTransformed():
            for lod in self.getLODNames():

                spine = self.find(f'**/def_spineB')
                if spine.isEmpty():
                    # If we haven't already, we need to create a control joint to adjust the rotation through the code
                    spine = self.controlJoint(None, "torso", "def_spineB", lodName = lod)
                spine.setH(-angle)

                self.getPart("legs", lod).setH(angle)
        else:
            # =======================================
            # Transformation Modifications

            # Transformations currently just set the rotation of the entire geom
            # in the future they should be detailed like the toons
            self.getActiveTransformationGeom().setH(angle)

            # Toon Mickey
            if self.getTransformationsIndex(ToontownGlobals.TransformationMisc) - 1 in (
                    ToontownGlobals.TransformationMiscMickey,
                    ToontownGlobals.TransformationMiscChaser):
                spine = self.getActiveTransformationGeom().find(f'**/def_spineB')
                if spine.isEmpty():
                    # If we haven't already, we need to create a control joint to adjust the rotation through the code
                    spine = self.getActiveTransformation().controlJoint(None, "torso", "def_spineB")
                spine.setH(-angle)

            # GOON
            if self.getActiveTransformationIndex() == ToontownGlobals.TransformationGoon:
                self.getActiveTransformationGeom().setH(angle-180)

            # COG
            # if self.getActiveTransformationIndex() == ToontownGlobals.TransformationCog:

            # Classic Char
            # if self.getActiveTransformationIndex() == ToontownGlobals.TransformationClassicChar:
            # etc

    def resetStrafeRotation(self):
        """ Resets the rotation of the torso + legs when strafing is not being used """
        if not self.isEmpty():
            spine = self.find(f'**/def_spineB')
            if not spine.isEmpty():
                spine.setH(0)
                spine.detachNode()
                # Release the joint to be able to be properly animated
                # if we don't release it, the toon looks dum dum
                self.releaseJoint("torso", "def_spineB")
            for lod in self.getLODNames():
                    self.getPart("legs", lod).setH(0)

        # =======================================
        # Transformation Modifications
        if self.getTransformed():
            # resetStrafeRotation might get called before the geom has been generated,
            # let's not crash!
            if not self.getActiveTransformationGeom():
                return
            # Transformations currently just set the rotation of the entire geom
            # in the future they should be detailed like the toons
            self.getActiveTransformationGeom().setH(0)

            # Toon Mickey
            if self.getTransformationsIndex(ToontownGlobals.TransformationMisc) - 1 in (
                    ToontownGlobals.TransformationMiscMickey,
                    ToontownGlobals.TransformationMiscChaser):
                spine = self.getActiveTransformationGeom().find(f'**/def_spineB')
                if not spine.isEmpty():
                    spine.setH(0)
                    spine.detachNode()
                self.getActiveTransformation().releaseJoint("torso", "def_spineB")

            # GOON
            if self.getActiveTransformationIndex() == ToontownGlobals.TransformationGoon:
                self.getActiveTransformationGeom().setH(180)

            # COG
            # if self.getActiveTransformationIndex() == ToontownGlobals.TransformationCog:

            # Classic Char
            # if self.getActiveTransformationIndex() == ToontownGlobals.TransformationClassicChar:
            # etc

    def enterOff(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.setActiveShadow(0)
        self.playingAnim = None
        return

    def exitOff(self):
        pass

    def enterNeutral(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        anim = 'neutral'
        if self.getTransformed() or self.getTPose():
            self.playTransformationAnim('neutral', [animMultiplier])
        else:
            self.pose(anim, int(self.getNumFrames(anim) * self.randGen.random()))
            self.loop(anim, restart=0)
            self.setPlayRate(animMultiplier, anim)
        self.playingAnim = anim
        self.setActiveShadow(0)

    def exitNeutral(self):
        self.stop()

    def enterVictory(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        anim = 'victory'
        frame = int(ts * self.getFrameRate(anim) * animMultiplier)
        if self.getTransformed() or self.getTPose():
            self.playTransformationAnim('victory', [animMultiplier])
        else:
            self.pose(anim, frame)
            self.loop('victory', restart=0)
            self.setPlayRate(animMultiplier, 'victory')
        self.playingAnim = anim
        self.setActiveShadow(0)

    def exitVictory(self):
        self.stop()

    def enterHappy(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = (('neutral', 1.0),
                                    ('walk', 1.0),
                                    ('run', 1.0),
                                    ('walk', -1.0),
                                    ('run', 1.0),
                                    ('run', 1.0)
                                    )
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        self.setActiveShadow(1)
        return

    def exitHappy(self):
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()
        return

    def enterSad(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.playingAnim = 'sad'
        self.playingRate = None
        self.standWalkRunReverse = (('sad-neutral', 1.0),
         ('sad-walk', 1.2),
         ('sad-walk', 1.2),
         ('sad-walk', -1.0),
         ('sad-walk', 1.0),
         ('sad-walk', 1.0))
        self.setSpeed(0, 0)
        Emote.globalEmote.disableBody(self, 'toon, enterSad')
        self.setActiveShadow(1)
        if self.isLocal():
            self.disableJump()
        return

    def exitSad(self):
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()
        Emote.globalEmote.releaseBody(self, 'toon, exitSad')
        if self.isLocal():
            if not (ZoneUtil.isBetaPlaygroundZone(self.zoneId) and ClientSettings.BetaPlaygroundMovement.get()):
                self.enableJump()

    def enterCatching(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = (('catch-neutral', 1.0),
         ('catch-run', 1.0),
         ('catch-run', 1.0),
         ('catch-run', -1.0),
         ('catch-run', 1.0),
         ('catch-run', 1.0))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        self.setActiveShadow(1)
        return

    def exitCatching(self):
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()
        return

    def enterCatchEating(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = (('catch-eatneutral', 1.0),
         ('catch-eatnrun', 1.0),
         ('catch-eatnrun', 1.0),
         ('catch-eatnrun', -1.0),
         ('catch-eatnrun', 1.0),
         ('catch-eatnrun', 1.0))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        self.setActiveShadow(0)
        return

    def exitCatchEating(self):
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()
        return

    def enterWalk(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        if self.getTransformed() or self.getTPose():
            self.playTransformationAnim('walk', [animMultiplier])
        else:
            self.loop('walk')
            self.setPlayRate(animMultiplier, 'walk')
        self.setActiveShadow(1)

    def exitWalk(self):
        self.stop()

    def getJumpDuration(self):
        if self.playingAnim == 'neutral':
            return self.getDuration('jump', 'legs')
        else:
            return self.getDuration('running-jump', 'legs')

    def enterJump(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        if self.playingAnim == 'neutral':
            anim = 'jump'
        else:
            anim = 'running-jump'

        if self.getTransformed() or self.getTPose():
            self.playTransformationAnim('jump')
        else:
            self.setPlayRate(animMultiplier, anim)
            self.play(anim)

        self.playingAnim = anim
        self.setActiveShadow(1)

    def exitJump(self):
        if self.getTransformed() or self.getTPose():
            self.stopTransformationAnim('jump')
        else:
            self.stop()
        self.playingAnim = 'neutral'

    def enterJumpSquat(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        if self.playingAnim == 'neutral':
            anim = 'jump-squat'
        else:
            anim = 'running-jump-squat'

        if self.getTransformed() or self.getTPose():
            self.playTransformationAnim('jump-squat')
        else:
            self.setPlayRate(animMultiplier, anim)
            self.play(anim)

        self.playingAnim = anim
        self.setActiveShadow(1)

    def exitJumpSquat(self):
        if self.getTransformed() or self.getTPose():
            self.stopTransformationAnim('jump-squat')
        else:
            self.stop()
        self.playingAnim = 'neutral'

    def enterJumpAirborne(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        if self.playingAnim == 'neutral' or self.forceJumpIdle:
            anim = 'jump-idle'
        else:
            anim = 'running-jump-idle'

        if self.getTransformed() or self.getTPose():
            self.playTransformationAnim('jump-idle')
        else:
            self.setPlayRate(animMultiplier, anim)
            self.loop(anim)

        self.playingAnim = anim
        self.setActiveShadow(1)

    def exitJumpAirborne(self):
        self.stop()
        self.playingAnim = 'neutral'

    def enterJumpLand(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        if self.playingAnim == 'running-jump-idle':
            anim = 'running-jump-land'
        else:
            anim = 'jump-land'

        if self.getTransformed() or self.getTPose():
            self.playTransformationAnim('jump-land')
        else:
            self.setPlayRate(animMultiplier, anim)
            self.play(anim)

        self.playingAnim = anim
        self.setActiveShadow(1)

    def exitJumpLand(self):
        if self.getTransformed() or self.getTPose():
            self.stopTransformationAnim('jump-land')
        else:
            self.stop()
        self.playingAnim = 'neutral'

    def enterRun(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        if self.getTransformed() or self.getTPose():
            self.playTransformationAnim('neutral')
        else:
            self.loop('run')
            self.setPlayRate(animMultiplier, 'run')
        Emote.globalEmote.disableBody(self, 'toon, enterRun')
        self.setActiveShadow(1)

    def exitRun(self):
        self.stop()
        Emote.globalEmote.releaseBody(self, 'toon, exitRun')

    def enterSwim(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        Emote.globalEmote.disableAll(self, 'enterSwim')
        self.playingAnim = 'swim'
        self.loop('swim')
        self.setPlayRate(animMultiplier, 'swim')
        self.getGeomNode().setP(-89.0)
        self.dropShadow.hide()
        if self.isLocal():
            self.useSwimControls()
        self.nametag3d.setPos(0, -2, 1)
        self.startBobSwimTask()
        self.setActiveShadow(0)

    def enterCringe(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        if self.getTransformed() or self.getTPose():
            self.playTransformationAnim('cringe')
        else:
            self.loop('cringe')
            self.getGeomNode().setPos(0, 0, -2)
            self.setPlayRate(animMultiplier, 'swim')

    def exitCringe(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        if self.getTransformed() or self.getTPose():
            self.stopTransformationAnim('cringe')
        else:
            self.stop()
            self.getGeomNode().setPos(0, 0, 0)
            self.playingAnim = 'neutral'
            self.setPlayRate(animMultiplier, 'swim')

    def enterDive(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.loop('swim')
        if hasattr(self.getGeomNode(), 'setPos'):
            self.getGeomNode().setPos(0, 0, -2)
            self.setPlayRate(animMultiplier, 'swim')
            self.setActiveShadow(0)
            self.dropShadow.hide()
            self.nametag3d.setPos(0, -2, 1)

    def exitDive(self):
        self.stop()
        self.getGeomNode().setPos(0, 0, 0)
        self.playingAnim = 'neutral'
        self.tryShowDropShadow()
        self.nametag3d.setPos(0, 0, self.height + 0.5)

    def enterSwimHold(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.getGeomNode().setPos(0, 0, -2)
        self.nametag3d.setPos(0, -2, 1)
        self.pose('swim', 55)

    def exitSwimHold(self):
        self.stop()
        self.getGeomNode().setPos(0, 0, 0)
        self.playingAnim = 'neutral'
        self.tryShowDropShadow()
        self.nametag3d.setPos(0, 0, self.height + 0.5)

    def exitSwim(self):
        self.stop()
        self.playingAnim = 'neutral'
        self.stopBobSwimTask()
        self.getGeomNode().setPosHpr(0, 0, 0, 0, 0, 0)
        self.setActiveShadow(1)
        # For some reason the above doesn't work, so we can just reset the drop shadow,
        # and figure out why at some point
        self.initializeDropShadow()
        self.tryShowDropShadow()
        if self.isLocal():
            self.useWalkControls()
        self.nametag3d.setPos(0, 0, self.height + 0.5)
        Emote.globalEmote.releaseAll(self, 'exitSwim')

    def startBobSwimTask(self):
        if hasattr(self, 'bobSwim') and self.bobSwim:
            self.bobSwim.finish()
            self.bobSwim = None

        self.nametag3d.setZ(5.0)
        geomNode = self.getGeomNode()
        geomNode.setZ(4.0)
        self.bobSwim = Sequence(
            geomNode.posInterval(1, Point3(0, -3, 3), startPos=Point3(0, -3, 4), blendType='easeInOut'),
            geomNode.posInterval(1, Point3(0, -3, 4), startPos=Point3(0, -3, 3), blendType='easeInOut')
        )
        self.bobSwim.loop()

    def stopBobSwimTask(self):
        if hasattr(self, 'bobSwim') and self.bobSwim:
            self.bobSwim.finish()

        self.getGeomNode().setPos(0, 0, 0)
        self.nametag3d.setZ(1.0)

    def enterOpenBook(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        Emote.globalEmote.disableAll(self, 'enterOpenBook')
        self.playingAnim = 'openBook'
        self.stopLookAround()
        self.lerpLookAt(Point3(0, 1, -2))
        if self.getTransformed() or self.getTPose():
            self.track = self.playTransformationAnim('openBook')
        else:
            bookTracks = Parallel()
            for bookActor in self.getBookActors():
                bookTracks.append(ActorInterval(bookActor, 'book', startTime=1.2, endTime=1.5))

            bookTracks.append(ActorInterval(self, 'book', startTime=1.2, endTime=1.5))
            if hasattr(self, 'uniqueName'):
                trackName = self.uniqueName('openBook')
            else:
                trackName = 'openBook'
            self.track = Sequence(Func(self.showBooks), bookTracks, Wait(0.1), name=trackName)
        if callback:
            self.track.setDoneEvent(self.track.getName())
            self.acceptOnce(self.track.getName(), callback, extraArgs)
        self.track.start(ts)
        self.setActiveShadow(0)

    def exitOpenBook(self):
        self.playingAnim = 'neutralob'
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if self.getTransformed() or self.getTPose():
            self.stopTransformationAnim('openBook')
        else:
            self.hideBooks()
        self.startLookAround()
        Emote.globalEmote.releaseAll(self, 'exitOpenBook')
        return

    def enterReadBook(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        Emote.globalEmote.disableBody(self, 'enterReadBook')
        self.playingAnim = 'readBook'
        self.stopLookAround()
        self.lerpLookAt(Point3(0, 1, -2))
        if self.getTransformed() or self.getTPose():
            self.playTransformationAnim('readBook')
        else:
            self.showBooks()
            for bookActor in self.getBookActors():
                bookActor.pingpong('book', fromFrame=38, toFrame=118)

            self.pingpong('book', fromFrame=38, toFrame=118)
        self.setActiveShadow(0)

    def exitReadBook(self):
        self.playingAnim = 'neutralrb'
        if self.getTransformed() or self.getTPose():
            self.stopTransformationAnim('readBook')
        else:
            self.hideBooks()
            for bookActor in self.getBookActors():
                bookActor.stop()

        self.startLookAround()
        Emote.globalEmote.releaseBody(self, 'exitReadBook')

    def enterCloseBook(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        Emote.globalEmote.disableAll(self, 'enterCloseBook')
        self.playingAnim = 'closeBook'
        if self.getTransformed() or self.getTPose():
            self.track = self.playTransformationAnim('closeBook')
        else:
            bookTracks = Parallel()
            for bookActor in self.getBookActors():
                bookTracks.append(ActorInterval(bookActor, 'book', startTime=4.96, endTime=6.5))

            bookTracks.append(ActorInterval(self, 'book', startTime=4.96, endTime=6.5))
            if hasattr(self, 'uniqueName'):
                trackName = self.uniqueName('closeBook')
            else:
                trackName = 'closeBook'
            self.track = Sequence(Func(self.showBooks), bookTracks, Func(self.hideBooks), name=trackName)
        if callback:
            self.track.setDoneEvent(self.track.getName())
            self.acceptOnce(self.track.getName(), callback, extraArgs)
        self.track.start(ts)
        self.setActiveShadow(0)

    def exitCloseBook(self):
        self.playingAnim = 'neutralcb'
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if self.getTransformed() or self.getTPose():
            self.stopTransformationAnim('closeBook')
        Emote.globalEmote.releaseAll(self, 'exitCloseBook')
        return

    def getSoundTeleport(self):
        if not self.soundTeleport:
            self.soundTeleport = base.loader.loadSfx('phase_3.5/audio/sfx/AV_teleport.ogg')
        return self.soundTeleport

    def getTeleportOutTrack(self, autoFinishTrack = 1):

        def showHoles(holes, hands):
            for hole, hand in zip(holes, hands):
                hole.reparentTo(hand)
                hole.setBlend(frameBlend=False)

        def reparentHoles(holes, toon):
            holes[0].reparentTo(toon)
            holes[1].detachNode()
            holes[2].detachNode()
            holes[0].setBin('shadow', 0)
            holes[0].setDepthTest(0)
            holes[0].setDepthWrite(0)
            holes[0].setBlend(frameBlend=ClientSettings.SmoothAnimations.get())

        def cleanupHoles(holes):
            holes[0].detachNode()
            holes[0].clearBin()
            holes[0].clearDepthTest()
            holes[0].clearDepthWrite()

        holes = self.getHoleActors()
        hands = self.getRightHands()
        holeTrack = Track((0.0, Func(showHoles, holes, hands)), (0.5, SoundInterval(self.getSoundTeleport(),
                                                                                    node=self)),
                          (1.708, Func(reparentHoles, holes, self)), (3.4, Func(cleanupHoles, holes)))
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('teleportOut')
        else:
            trackName = 'teleportOut'
        track = Parallel(holeTrack, name=trackName, autoFinish=autoFinishTrack)
        for hole in holes:
            track.append(ActorInterval(hole, 'hole', duration=3.4))

        track.append(ActorInterval(self, 'teleport', duration=3.4))
        return track

    def startQuestMap(self):
        pass

    def stopQuestMap(self):
        pass

    def enterTeleportOut(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        name = self.name
        if hasattr(self, 'doId'):
            name += '-' + str(self.doId)
        self.notify.debug('enterTeleportOut %s' % name)
        if self.ghostMode or (hasattr(self, 'locked') and self.locked) or base.cr.episodeManager.episode:
            if callback:
                callback(*extraArgs)
            return
        self.playingAnim = 'teleport'
        Emote.globalEmote.disableAll(self, 'enterTeleportOut')
        if self.getTransformed() or self.getTPose():
            self.track = self.playTransformationAnim('teleport')
        else:
            if self.isLocal():
                autoFinishTrack = 0
            else:
                autoFinishTrack = 1
            self.track = self.getTeleportOutTrack(autoFinishTrack)
            holeClip = PlaneNode('holeClip')
            self.holeClipPath = self.attachNewNode(holeClip)
            self.getGeomNode().setClipPlane(self.holeClipPath)
            self.nametag3d.setClipPlane(self.holeClipPath)
        if self.track:
            self.track.setDoneEvent(self.track.getName())
            self.acceptOnce(self.track.getName(), self.finishTeleportOut, [callback, extraArgs])
            self.track.start(ts)
        elif callback:
            callback(*extraArgs)
        self.setActiveShadow(0)

    def finishTeleportOut(self, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        name = self.name
        if hasattr(self, 'doId'):
            name += '-' + str(self.doId)
        self.notify.debug('finishTeleportOut %s' % name)
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if hasattr(self, 'animFSM'):
            self.animFSM.request('TeleportedOut')
        if callback:
            callback(*extraArgs)
        return

    def exitTeleportOut(self):
        name = self.name
        if hasattr(self, 'doId'):
            name += '-' + str(self.doId)
        self.notify.debug('exitTeleportOut %s' % name)
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            self.track = None
        if self.getTransformed() or self.getTPose():
            self.stopTransformationAnim('teleport')
        else:
            geomNode = self.getGeomNode()
            if geomNode and not geomNode.isEmpty():
                self.getGeomNode().clearClipPlane()
            if self.nametag3d and not self.nametag3d.isEmpty():
                self.nametag3d.clearClipPlane()
            if self.holeClipPath:
                self.holeClipPath.removeNode()
                self.holeClipPath = None
        Emote.globalEmote.releaseAll(self, 'exitTeleportOut')
        if self and not self.isEmpty():
            self.show()
        return

    def enterTeleportedOut(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.setActiveShadow(0)

    def exitTeleportedOut(self):
        pass

    def getDiedInterval(self, autoFinishTrack = 1):
        sound = loader.loadSfx('phase_5/audio/sfx/ENC_Lose.ogg')
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('died')
        else:
            trackName = 'died'
        ival = Sequence(Func(Emote.globalEmote.disableBody, self), Func(self.sadEyes), Func(self.blinkEyes),
                        Track((0, ActorInterval(self, 'lose')), (2, SoundInterval(sound, node=self)),
                              (5.333, self.scaleInterval(1.5, VBase3(0.01, 0.01, 0.01), blendType='easeInOut'))),
                        Func(self.detachNode), Func(self.setScale, 1, 1, 1), Func(self.normalEyes),
                        Func(self.blinkEyes), Func(Emote.globalEmote.releaseBody, self), name=trackName,
                        autoFinish=autoFinishTrack)
        return ival

    def enterDied(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        if self.ghostMode:
            if callback:
                callback(*extraArgs)
            return
        self.playingAnim = 'lose'
        Emote.globalEmote.disableAll(self, 'enterDied')
        if hasattr(self, 'jumpLandAnimFixTask') and self.jumpLandAnimFixTask:
            self.jumpLandAnimFixTask.remove()
            self.jumpLandAnimFixTask = None
        if self.isLocal():
            autoFinishTrack = 0
        else:
            autoFinishTrack = 1
        if self.getTransformed() or self.getTPose():
            self.track = self.playTransformationAnim('died')
        else:
            self.track = self.getDiedInterval(autoFinishTrack)
        if callback:
            self.track = Sequence(self.track, Func(callback, *extraArgs), autoFinish=autoFinishTrack)
        if self.track:
            self.track.start(ts)
        self.setActiveShadow(0)
        return

    def finishDied(self, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if hasattr(self, 'animFSM'):
            self.animFSM.request('TeleportedOut')
        if callback:
            callback(*extraArgs)
        return

    def exitDied(self):
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if self.getTransformed() or self.getTPose():
            self.stopTransformationAnim('died')
        Emote.globalEmote.releaseAll(self, 'exitDied')
        self.show()
        return

    def getTeleportInTrack(self):
        hole = self.getHoleActors()[0]
        hole.setBin('shadow', 0)
        hole.setDepthTest(0)
        hole.setDepthWrite(0)
        hole.setBlend(frameBlend=ClientSettings.SmoothAnimations.get())
        holeTrack = Sequence()
        holeTrack.append(Func(hole.reparentTo, self))
        pos = Point3(0, -2.4, 0)
        holeTrack.append(Func(hole.setPos, self, pos))
        holeTrack.append(ActorInterval(hole, 'hole', startTime=3.4, endTime=3.1))
        holeTrack.append(Wait(0.6))
        holeTrack.append(ActorInterval(hole, 'hole', startTime=3.1, endTime=3.4))

        def restoreHole(hole):
            hole.setPos(0, 0, 0)
            hole.detachNode()
            hole.clearBin()
            hole.clearDepthTest()
            hole.clearDepthWrite()

        holeTrack.append(Func(restoreHole, hole))
        toonTrack = Sequence(Wait(0.3), Func(self.tryShowGeom), Func(self.tryShowNametag),
                             ActorInterval(self, 'jump', startTime=0.45))
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('teleportIn')
        else:
            trackName = 'teleportIn'
        return Parallel(holeTrack, toonTrack, name=trackName)

    def enterTeleportIn(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        if self.ghostMode or base.cr.episodeManager.episode:
            if callback:
                callback(*extraArgs)
            return
        self.show()
        self.playingAnim = 'teleport'
        Emote.globalEmote.disableAll(self, 'enterTeleportIn')
        if self.getTransformed() or self.getTPose():
            self.track = self.playTransformationAnim('teleportIn')
        if not self.track:
            self.pose('teleport', self.getNumFrames('teleport') - 1)
            self.getGeomNode().hide()
            self.nametag3d.hide()
            self.track = self.getTeleportInTrack()
        if callback and self.track:
            self.track.setDoneEvent(self.track.getName())
            self.acceptOnce(self.track.getName(), callback, extraArgs)
        self.track.start(ts)
        self.setActiveShadow(0)

    def exitTeleportIn(self):
        self.playingAnim = None
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if self.getTransformed() or self.getTPose():
            self.stopTransformationAnim('teleportIn')
        else:
            self.tryShowGeom()
            self.tryShowNametag()
        Emote.globalEmote.releaseAll(self, 'exitTeleportIn')
        return

    def enterSitStart(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        Emote.globalEmote.disableBody(self)
        self.playingAnim = 'sit-start'
        if self.isLocal():
            self.track = Sequence(ActorInterval(self, 'sit-start'), Func(self.b_setAnimState, 'Sit', animMultiplier))
        else:
            self.track = Sequence(ActorInterval(self, 'sit-start'))
        self.track.start(ts)
        self.setActiveShadow(0)

    def exitSitStart(self):
        self.playingAnim = 'neutral'
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseBody(self)
        return

    def enterSit(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        Emote.globalEmote.disableBody(self)
        self.playingAnim = 'sit'
        if self.getTransformed() or self.getTPose():
            self.playTransformationAnim('sit')
        else:
            self.loop('sit')
        self.setActiveShadow(0)

    def exitSit(self):
        self.playingAnim = 'neutral'
        Emote.globalEmote.releaseBody(self)

    def enterSleep(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.stopLookAround()
        transformationIndex = self.getActiveTransformationIndex()
        if transformationIndex == ToontownGlobals.TransformationCog:
            self.sleepString = TTLocalizer.ToonSleepString
            self.stopBlink()
            self.closeEyes()
            self.suit.loop('lured')
        elif ZoneUtil.getCanonicalHoodId(self.zoneId) == ToontownGlobals.TheBrrrgh and not ZoneUtil.isInterior(self.zoneId):
            self.sleepString = TTLocalizer.ToonSleepStringBrrrgh
            self.sadEyes()
            self.blinkEyes()
            self.showAngryMuzzle()
            self.pingpong('bored', partName='torso', fromFrame=50, toFrame=51)
            self.setPlayRate(animMultiplier * 0.8, 'bored')
        else:
            self.sleepString = TTLocalizer.ToonSleepString
            self.stopBlink()
            self.closeEyes()
            self.lerpLookAt(Point3(0, 1, -4))
            self.loop('neutral')
            self.setPlayRate(animMultiplier * 0.4, 'neutral')
        # This should stop the spam of the sleep string
        # if a toon gets pushed around
        if self.nametag.getChat() != self.sleepString:
            self.setChatAbsolute(self.sleepString, CFThought)
        if self == base.localAvatar:
            self.notify.debug('adding timeout task')
            taskMgr.remove(self.uniqueName('afkTimeout'))   # remove any previous afkTimeouts before adding another
            taskMgr.doMethodLater(self.afkTimeout, self.__handleAfkTimeout, self.uniqueName('afkTimeout'))
        self.setActiveShadow(0)

    def __handleAfkTimeout(self, task):
        self.notify.debug('handling timeout')
        self.ignore('wakeup')
        self.takeOffTransformation()
        base.cr.playGame.getPlace().fsm.request('final')
        self.b_setAnimState('TeleportOut', 1, self.__handleAfkExitTeleport, [0])
        return Task.done

    def __handleAfkExitTeleport(self, requestStatus):
        self.notify.info('closing shard...')
        base.cr.gameFSM.request('closeShard', ['afkTimeout'])

    def exitSleep(self):
        taskMgr.remove(self.uniqueName('afkTimeout'))
        self.hideAngryMuzzle()
        self.normalEyes()
        self.startLookAround()
        self.openEyes()
        self.startBlink()
        if config.GetBool('stuck-sleep-fix', 1):
            doClear = self.sleepString in (self.nametag.getChat(), self.nametag.getStompText())
        else:
            doClear = self.nametag.getChat() == self.sleepString
        if doClear:
            self.clearChat()
        self.lerpLookAt(Point3(0, 1, 0), time=0.25)
        self.stop()

    def enterPush(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        Emote.globalEmote.disableBody(self)
        self.playingAnim = 'push'
        self.track = Sequence(ActorInterval(self, 'push'))
        self.track.loop()
        self.setActiveShadow(1)

    def exitPush(self):
        self.playingAnim = 'neutral'
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseBody(self)
        return

    def enterEmote(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        if len(extraArgs) > 0:
            emoteIndex = extraArgs[0]
        else:
            return
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = (('neutral', 1.0),
                                    ('walk', 1.0),
                                    ('run', 1.0),
                                    ('walk', -1.0),
                                    ('run', 1.0),
                                    ('run', 1.0))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        if self.isLocal() and emoteIndex != Emote.globalEmote.EmoteSleepIndex:
            if self.sleepFlag:
                self.b_setAnimState('Happy', self.animMultiplier)
            self.wakeUp()
        duration = 0
        self.emoteTrack, duration = Emote.globalEmote.doEmote(self, emoteIndex, ts)
        self.setActiveShadow(1)
        return

    def doEmote(self, emoteIndex, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        if not self.isLocal():
            if base.cr.avatarFriendsManager.checkIgnored(self.doId):
                return
        duration = 0
        if self.isLocal():
            self.wakeUp()
            if self.hasTrackAnimToSpeed():
                self.trackAnimToSpeed(None)
        self.emoteTrack, duration = Emote.globalEmote.doEmote(self, emoteIndex, ts)
        return

    def __returnToLastAnim(self, task):
        if self.playingAnim:
            self.loop(self.playingAnim)
        elif self.hp > 0:
            self.loop('neutral')
        else:
            self.loop('sad-neutral')
        return Task.done

    def __finishEmote(self, task):
        if self.isLocal():
            if self.hp > 0:
                self.b_setAnimState('Happy')
            else:
                self.b_setAnimState('Sad')
        return Task.done

    def exitEmote(self):
        self.stop()
        if self.emoteTrack != None:
            self.emoteTrack.finish()
            self.emoteTrack = None
        taskMgr.remove(self.taskName('finishEmote'))
        return

    def enterSquish(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        Emote.globalEmote.disableAll(self)
        audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)
        audio3d.setDropOffFactor(0.1)
        sound = audio3d.loadSfx('phase_9/audio/sfx/toon_decompress.ogg')
        lerpTime = 0.1
        node = self.getActiveTransformationGeom()
        audio3d.attachSoundToObject(sound, node)
        origScale = node.getScale()

        def cleanupSounds(sfx = sound, audioMgr = audio3d):
            audioMgr.detachSound(sfx)
            if sfx.status() == sfx.PLAYING:
                sfx.stop()
            
            audioMgr.disable()
            del audioMgr

        if self.getTransformed() or self.getTPose():
            self.track = self.playTransformationAnim('squish', [sound, lerpTime, node, origScale])
        if not self.track:
            self.track = Sequence(LerpScaleInterval(node, lerpTime, VBase3(2, 2, 0.025), blendType='easeInOut'),
                                  Wait(1.0),
                                  Parallel(Sequence(Wait(0.4),
                                                    LerpScaleInterval(node, lerpTime, VBase3(1.4, 1.4, 1.4),
                                                                      blendType='easeInOut'),
                                                    LerpScaleInterval(node, lerpTime / 2.0, VBase3(0.8, 0.8, 0.8),
                                                                      blendType='easeInOut'),
                                                    LerpScaleInterval(node, lerpTime / 3.0, origScale,
                                                                      blendType='easeInOut')),
                                           ActorInterval(self, 'jump', startTime=0.2), SoundInterval(sound)),
                                           Func(cleanupSounds))
        self.track.start(ts)
        self.setActiveShadow(1)

    def exitSquish(self):
        self.playingAnim = 'neutral'
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseAll(self)
        return

    def enterFallDown(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.playingAnim = 'fallDown'
        Emote.globalEmote.disableAll(self)
        if self.getTransformed() or self.getTPose():
            self.track = self.playTransformationAnim('fallDown')
        else:
            self.track = Sequence(ActorInterval(self, 'slip-backward'), name='fallTrack')
        if callback:
            self.track.setDoneEvent(self.track.getName())
            self.acceptOnce(self.track.getName(), callback, extraArgs)
        self.track.start(ts)

    def exitFallDown(self):
        self.playingAnim = 'neutral'
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseAll(self)
        return

    def stunToon(self, ts = 0, callback = None, knockdown = 0):
        if not self.isStunned:
            if self.stunTrack:
                self.stunTrack.finish()
                self.stunTrack = None

            def setStunned(stunned):
                self.isStunned = stunned
                if self == base.localAvatar:
                    messenger.send('toonStunned-' + str(self.doId), [self.isStunned])

            node = self.getGeomNode()
            lerpTime = 0.5
            down = self.doToonColorScale(VBase4(1, 1, 1, 0.6), lerpTime)
            up = self.doToonColorScale(VBase4(1, 1, 1, 0.9), lerpTime)
            clear = self.doToonColorScale(self.defaultColorScale, lerpTime)
            track = Sequence(Func(setStunned, 1), down, up, down, up, down, up, down, clear,
                             Func(self.restoreDefaultColorScale), Func(setStunned, 0))
            if knockdown:
                if self.getTransformed() or self.getTPose():
                    self.stunTrack = self.playTransformationAnim('stun', [track])
                else:
                    self.stunTrack = Parallel(ActorInterval(self, animName='slip-backward'), track)
            else:
                self.stunTrack = track
            self.stunTrack.start()
        return

    def getPieces(self, *pieces):
        results = []
        for lodName in self.getLODNames():
            for partName, pieceNames in pieces:
                part = self.getPart(partName, lodName)
                if part:
                    if isinstance(pieceNames, str):
                        pieceNames = (pieceNames,)
                    for pieceName in pieceNames:
                        npc = part.findAllMatches('**/%s;+s' % pieceName)
                        for i in range(npc.getNumPaths()):
                            results.append(npc[i])

        return results

    def applyCheesyEffect(self, effect, lerpTime = 0):
        if self.getActiveTransformationIndex() != ToontownGlobals.TransformationToon and not any(
                [hasattr(self, 'suitGeom'),
                 hasattr(self, 'charGeom'),
                 hasattr(self, 'petGeom'),
                 hasattr(self, 'goonGeom'),
                 hasattr(self, 'prop'),
                 hasattr(self, 'bossGeom'),
                 hasattr(self, 'fishGeom'),
                 hasattr(self, 'butterflyGeom'),
                 hasattr(self, 'misc'),
                 hasattr(self, 'streetGeom')]):
            self.acceptOnce(self.uniqueName('transformation-applied'), self.applyCheesyEffect,
                            [effect, lerpTime])
            return
        if self.ghostMode:
            lerpTime = 0.0  # override lerp time for ghosted toons

        if self.effectTrack != None:
            self.effectTrack.finish()
            self.effectTrack = None
        if self.cheesyEffect != effect:
            oldEffect = self.cheesyEffect
            self.cheesyEffect = effect
            if oldEffect == ToontownGlobals.CENormal:
                self.effectTrack = self.__doCheesyEffect(effect, lerpTime)
            elif effect == ToontownGlobals.CENormal:
                self.effectTrack = self.__undoCheesyEffect(oldEffect, lerpTime)
            else:
                self.effectTrack = Sequence(self.__undoCheesyEffect(oldEffect, lerpTime / 2.0),
                                            self.__doCheesyEffect(effect, lerpTime / 2.0))
            self.effectTrack.start()

    def reapplyCheesyEffect(self, lerpTime = 0):
        if self.effectTrack != None:
            self.effectTrack.finish()
            self.effectTrack = None
        effect = self.cheesyEffect
        self.effectTrack = Sequence(self.__undoCheesyEffect(effect, 0), self.__doCheesyEffect(effect, lerpTime))
        self.effectTrack.start()
        return

    def clearCheesyEffect(self, lerpTime = 0):
        self.applyCheesyEffect(ToontownGlobals.CENormal, lerpTime=lerpTime)
        if self.effectTrack != None:
            self.effectTrack.finish()
            self.effectTrack = None
        return

    def __doHeadScale(self, scale, lerpTime):
        if scale == None:
            scale = ToontownGlobals.toonHeadScales[self.style.getAnimal()]
        track = Parallel()
        for hi in range(self.headParts.getNumPaths()):
            head = self.headParts[hi]
            track.append(LerpScaleInterval(head, lerpTime, scale, blendType='easeInOut'))

        return track

    def __doLegsScale(self, scale, lerpTime):
        if scale == None:
            scale = 1
            invScale = 1
        elif isinstance(scale, tuple):
            invScale = (1.0, 1.0, 1.0 / scale[2])
        else:
            invScale = 1.0 / scale
        track = Parallel()
        for li in range(self.legsParts.getNumPaths()):
            legs = self.legsParts[li]
            torso = self.torsoParts[li]
            track.append(LerpScaleInterval(legs, lerpTime, scale, blendType='easeInOut'))
            track.append(LerpScaleInterval(torso, lerpTime, invScale, blendType='easeInOut'))

        track = Sequence(track, Func(self.resetHeight))

        return track

    def getToonScale(self):
        return self.toonScale

    def __doToonScale(self, scale, lerpTime):
        lerpH = 0
        node = self.getActiveTransformationGeom()
        activeTransformation = self.getActiveTransformationIndex()
        if activeTransformation == ToontownGlobals.TransformationGoon:
            lerpH = 180
        toonGeom = self.getGeomNode().getChild(0)

        scale = self.getToonScaleEffect(scale)

        track = Sequence()
        if node:
            if node != toonGeom:
                track.append(Parallel(Sequence(Parallel(LerpHprInterval(toonGeom, lerpTime, Vec3(0.0, 0.0, 0.0),
                                                                        blendType='easeInOut'),
                                                        LerpScaleInterval(toonGeom, lerpTime, scale,
                                                                          blendType='easeInOut'))),
                                      Sequence(Parallel(LerpHprInterval(node, lerpTime, Vec3(lerpH, 0.0, 0.0),
                                                                        blendType='easeInOut'),
                                                        LerpScaleInterval(node, lerpTime, scale,
                                                                          blendType='easeInOut')),
                                               Func(self.resetHeight))))
            else:
                track.append(Sequence(Parallel(LerpHprInterval(node, lerpTime, Vec3(0.0, 0.0, 0.0),
                                                               blendType='easeInOut'),
                                               LerpScaleInterval(node, lerpTime, scale,
                                                                 blendType='easeInOut')), Func(self.resetHeight)))
        return track

    def doToonColorScale(self, scale, lerpTime, keepDefault = 0):
        if keepDefault:
            self.defaultColorScale = scale
        if scale == None:
            scale = VBase4(1, 1, 1, 1)
        node = self.getGeomNode()
        caps = self.getPieces(('torso', 'torso-bot-cap'))

        def toonTransparency(node, clear=False):
            if node and not clear:
                node.setTransparency(1)
            elif node and clear:
                node.clearTransparency()

        track = Sequence()
        track.append(Func(toonTransparency, node))
        if scale[3] != 1:
            for cap in caps:
                track.append(HideInterval(cap))

        track.append(LerpColorScaleInterval(node, lerpTime, scale, blendType='easeInOut'))
        if scale[3] == 1:
            track.append(Func(toonTransparency, node, True))
            for cap in caps:
                track.append(ShowInterval(cap))

        elif scale[3] == 0:
            track.append(Func(toonTransparency, node, True))
        return track

    def __doPumpkinHeadSwitch(self, lerpTime, toPumpkin):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy),
                            name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toPumpkin:
            track.append(Func(self.stopBlink))
            track.append(Func(self.closeEyes))
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            def hideParts():
                self.notify.debug('hideParts')
                for head in self.headParts:
                    for p in head.getChildren():
                        if hasattr(self, 'pumpkins') and not self.pumpkins.hasPath(p):
                            p.hide()
                            p.setTag('pumpkin', 'enabled')

            track.append(Func(hideParts))
            track.append(Func(self.enablePumpkins, True))
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            def showHiddenParts():
                self.notify.debug('showHiddenParts')
                for head in self.headParts:
                    for p in head.getChildren():
                        if not self.pumpkins.hasPath(p) and p.getTag('pumpkin') == 'enabled':
                            p.show()
                            p.setTag('pumpkin', 'disabled')

            track.append(Func(showHiddenParts))
            track.append(Func(self.enablePumpkins, False))
            track.append(Func(self.startBlink))
        return track

    def __doSnowManHeadSwitch(self, lerpTime, toSnowMan):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy),
                            name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toSnowMan:
            track.append(Func(self.stopBlink))
            track.append(Func(self.closeEyes))
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            def hideParts():
                self.notify.debug('HidePaths')
                for hi in range(self.headParts.getNumPaths()):
                    head = self.headParts[hi]
                    parts = head.getChildren()
                    for pi in range(parts.getNumPaths()):
                        p = parts[pi]
                        if not p.isHidden():
                            p.hide()
                            p.setTag('snowman', 'enabled')

            track.append(Func(hideParts))
            track.append(Func(self.enableSnowMen, True))
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            def showHiddenParts():
                self.notify.debug('ShowHiddenPaths')
                for hi in range(self.headParts.getNumPaths()):
                    head = self.headParts[hi]
                    parts = head.getChildren()
                    for pi in range(parts.getNumPaths()):
                        p = parts[pi]
                        if not self.snowMen.hasPath(p) and p.getTag('snowman') == 'enabled':
                            p.show()
                            p.setTag('snowman', 'disabled')

            track.append(Func(showHiddenParts))
            track.append(Func(self.enableSnowMen, False))
            track.append(Func(self.startBlink))
        return track

    def __doGreenToon(self, lerpTime, toGreen):
        track = Sequence()
        greenTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy),
                            name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
        if toGreen:
            skinGreen = VBase4(76 / 255.0, 240 / 255.0, 84 / 255.0, 1)
            muzzleGreen = VBase4(4 / 255.0, 205 / 255.0, 90 / 255.0, 1)
            gloveGreen = VBase4(14 / 255.0, 173 / 255.0, 40 / 255.0, 1)
            greenTrack.append(self.__colorToonSkin(skinGreen, lerpTime))
            greenTrack.append(self.__colorToonEars(skinGreen, muzzleGreen, lerpTime))
            greenTrack.append(self.__colorScaleToonMuzzle(muzzleGreen, lerpTime))
            greenTrack.append(self.__colorToonGloves(gloveGreen, lerpTime))
        else:
            greenTrack.append(self.__colorToonSkin(None, lerpTime))
            greenTrack.append(self.__colorToonEars(None, None, lerpTime))
            greenTrack.append(self.__colorScaleToonMuzzle(None, lerpTime))
            greenTrack.append(self.__colorToonGloves(None, lerpTime))
        track.append(greenTrack)
        return track

    def __doWireFrameToon(self, lerpTime, toWireFrame):
        track = Sequence()
        wireFrameTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy),
                            name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
        if toWireFrame:
            wireFrameTrack.append(Func(self.getGeomNode().setAttrib, RenderModeAttrib.make(RenderModeAttrib.MWireframe, 1), 1))
        else:
            wireFrameTrack.append(Func(self.getGeomNode().clearRenderMode))
        track.append(wireFrameTrack)
        return track

    def __doNoTorsoToon(self, lerpTime, toNoTorso):
        track = Sequence()
        noTorsoTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy),
                            name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))

        parts = ('torso-bot', 'torso-bot-cap', 'torso-top', 'sleeves', 'neck', 'torso')

        if toNoTorso:
            for lod in self.getLODNames():
                # Lower the torso piece so the arms match up with the head
                torso = self.getPart('torso', lod)
                track.append(Func(torso.setPos, (0, 0, ToontownGlobals.torsoToOffset[self.style.torso[0]])))

                # Attach the head to the hips
                track.append(Func(self.attach, 'head', 'legs', 'joint_hips', lod))

            # Hide the torso pieces
            for piece in self.getPieces(('torso', parts)):
                track.append(Func(piece.hide))
        else:
            # Reset the hierarchy of the toon parts
            noTorsoTrack.append(Func(self.unparentToonParts))
            noTorsoTrack.append(Func(self.parentToonParts))

            # Show the torso pieces
            for piece in self.getPieces(('torso', parts)):
                noTorsoTrack.append(Func(piece.show))

            # Move the torso back up
            for lod in self.getLODNames():
                noTorsoTrack.append(Func(self.getPart('torso', lod).setPos, (0, 0, 0)))
        track.append(noTorsoTrack)
        track.append(Func(self.resetHeight))
        return track

    def __doMagicCat(self, lerpTime, toMagicCat):
        track = Sequence()
        magicCatTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy),
                            name='dustCloadIval')

        def safeRemoveNode(node):
            if not node.isEmpty():
                node.removeNode()

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))

        if toMagicCat:
            magicCatTrack.append(Func(LaughingManGlobals.addToonEffect, self))
        else:
            lods = self.getLODNames()
            for lod in lods:
                head = self.getPart('head', lod)
                for nodePath in head.getChildren():
                    doAppend = True
                    if self.isMuzzle(nodePath) and nodePath not in self.getMuzzles():
                        doAppend = False
                    if doAppend:
                        magicCatTrack.append(Func(nodePath.show))
                index = lods.index(lod)
                node = self.find('**/laughing-man-{}'.format(index))
                magicCatTrack.append(Func(safeRemoveNode, node))

        track.append(magicCatTrack)
        return track

    def __do20Dog(self, lerpTime, to20Dog):
        track = Sequence()
        _20DogTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy),
                            name='dustCloadIval')

        def safeRemoveNode(node):
            if not node.isEmpty():
                node.removeNode()

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))

        def makeHead(self):
            lods = self.getLODNames()
            for lod in lods:
                head = self.getPart('head', lod)
                index = lods.index(lod)
                for nodePath in head.getChildren():
                    nodePath.hide()
                a: Actor.Actor = Actor.Actor('phase_14.5/models/char/ttrm_m_chr_head_20dog')
                a.reparentTo(head)
                a.setScale(3)
                a.setH(180)
                a.setZ(0.1)
                j = a.controlJoint(None, 'modelRoot', 'muzzle')
                j.setX(-1.0)
                a.setName(f'20dog-{index}')

        if to20Dog:
            _20DogTrack.append(Func(makeHead, self))
            #p = Parallel()
            #for i, lod in enumerate(self.getLODNames()):


        else:
            lods = self.getLODNames()
            for lod in lods:
                head = self.getPart('head', lod)
                for nodePath in head.getChildren():
                    doAppend = True
                    if self.isMuzzle(nodePath) and nodePath not in self.getMuzzles():
                        doAppend = False
                    if doAppend:
                        _20DogTrack.append(Func(nodePath.show))
                index = lods.index(lod)
                node = self.find(f'**/20dog-{index}')
                _20DogTrack.append(Func(safeRemoveNode, node))

        track.append(_20DogTrack)
        return track

    def __colorToonSkin(self, color, lerpTime):
        track = Sequence()
        colorTrack = Parallel()
        torsoPieces = self.getPieces(('torso', ('arms', 'neck', 'torso')))
        legPieces = self.getPieces(('legs', ('legs', 'feet')))
        headPieces = self.getPieces(('head', '*head*'))
        if color == None:
            armColor = self.style.getArmColor()
            legColor = self.style.getLegColor()
            headColor = self.style.getHeadColor()
        else:
            armColor = color
            legColor = color
            headColor = color
        for piece in torsoPieces:
            colorTrack.append(Func(piece.setColor, armColor))

        for piece in legPieces:
            colorTrack.append(Func(piece.setColor, legColor))

        strsNotAllowed = ('hatNode', 'glassesNode', 'muzzle')
        for piece in headPieces:
            pieceNotAllowed = False

            for pieceStr in strsNotAllowed:
                if str(piece).__contains__(pieceStr):
                    pieceNotAllowed = True
                    break

            if not pieceNotAllowed:
                colorTrack.append(Func(piece.setColor, headColor))

        track.append(colorTrack)
        return track

    def __colorToonEars(self, color, colorScale, lerpTime):
        track = Sequence()
        earPieces = self.getPieces(('head', '*ear*'))
        if len(earPieces) == 0:
            return track
        colorTrack = Parallel()
        if earPieces[0].hasColor():
            if color == None:
                headColor = self.style.getHeadColor()
            else:
                headColor = color
            for piece in earPieces:
                colorTrack.append(Func(piece.setColor, headColor))

        else:
            if colorScale == None:
                colorScale = VBase4(1, 1, 1, 1)
            for piece in earPieces:
                colorTrack.append(Func(piece.setColorScale, colorScale))

        track.append(colorTrack)
        return track

    def __colorScaleToonMuzzle(self, scale, lerpTime):
        track = Sequence()
        colorTrack = Parallel()
        muzzlePieces = self.getPieces(('head', '*muzzle*'))
        if scale == None:
            scale = VBase4(1, 1, 1, 1)
        for piece in muzzlePieces:
            colorTrack.append(Func(piece.setColorScale, scale))

        track.append(colorTrack)
        return track

    def __colorToonGloves(self, color, lerpTime):
        track = Sequence()
        colorTrack = Parallel()
        glovePieces = self.getPieces(('torso', '*hands*'))
        if color == None:
            for piece in glovePieces:
                colorTrack.append(Func(piece.clearColor))

        else:
            for piece in glovePieces:
                colorTrack.append(Func(piece.setColor, color))

        track.append(colorTrack)
        return track

    def __doBigAndWhite(self, color, scale, lerpTime):
        track = Parallel()
        track.append(self.__doToonColor(color, lerpTime))
        track.append(self.__doToonScale(None, lerpTime))
        return track

    def __doVirtual(self):
        track = Parallel()
        track.append(self.__doToonColor(VBase4(0.25, 0.25, 1.0, 1), 0.0))
        self.setPartsAdd(self.getHeadParts())
        self.setPartsAdd(self.getTorsoParts())
        self.setPartsAdd(self.getHipsParts())
        self.setPartsAdd(self.getLegsParts())
        return track

    def __doUnVirtual(self):
        track = Parallel()
        track.append(self.__doToonColor(None, 0.0))
        self.setPartsNormal(self.getHeadParts(), 1)
        self.setPartsNormal(self.getTorsoParts(), 1)
        self.setPartsNormal(self.getHipsParts(), 1)
        self.setPartsNormal(self.getLegsParts(), 1)
        return track

    def setPartsAdd(self, parts):
        actorCollection = parts
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag'):
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                self.setBin('fixed', 1)

    def setPartsNormal(self, parts, alpha = 0):
        actorCollection = parts
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag'):
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MNone))
                thing.setDepthWrite(True)
                self.clearBin()
                if alpha:
                    thing.setTransparency(1)
                    thing.setBin('transparent', 0)

    def __doToonGhostColorScale(self, scale, lerpTime, keepDefault = 0):
        if keepDefault:
            self.defaultColorScale = scale
        if scale == None:
            scale = VBase4(1, 1, 1, 1)
        actor = self.getActiveTransformationGeom()
        caps = self.getPieces(('torso', 'torso-bot-cap'))
        track = Sequence()
        track.append(Func(actor.setTransparency, 1))
        track.append(ShowInterval(actor))
        if scale[3] != 1:
            for cap in caps:
                track.append(HideInterval(cap))

        track.append(LerpColorScaleInterval(actor, lerpTime, scale, blendType='easeInOut'))
        if scale[3] == 1:
            track.append(Func(actor.clearTransparency))
            for cap in caps:
                track.append(ShowInterval(cap))

        elif scale[3] == 0:
            track.append(Func(actor.clearTransparency))
            track.append(HideInterval(actor))
        return track

    def restoreDefaultColorScale(self):
        node = self.getGeomNode()
        if node:
            if self.defaultColorScale:
                node.setColorScale(self.defaultColorScale)
                if self.defaultColorScale[3] != 1:
                    node.setTransparency(1)
                else:
                    node.clearTransparency()
            else:
                node.clearColorScale()
                node.clearTransparency()

    def __doToonColor(self, color, lerpTime):
        node = self.getGeomNode()
        if color == None:
            return Func(node.clearColor)
        else:
            return Func(node.setColor, color, 1)
        return

    def __doPartsColorScale(self, scale, lerpTime):
        if scale == None:
            scale = VBase4(1, 1, 1, 1)
        node = self.getGeomNode()
        pieces = self.getPieces(('torso', ('arms', 'neck')), ('legs', ('legs', 'feet')), ('head', '+GeomNode'))
        track = Sequence()
        track.append(Func(node.setTransparency, 1))
        for piece in pieces:
            if piece.getName()[:7] == 'muzzle-' and piece.getName()[-8:] != '-neutral':
                continue
            track.append(ShowInterval(piece))

        p1 = Parallel()
        for piece in pieces:
            if piece.getName()[:7] == 'muzzle-' and piece.getName()[-8:] != '-neutral':
                continue
            p1.append(LerpColorScaleInterval(piece, lerpTime, scale, blendType='easeInOut'))

        track.append(p1)
        if scale[3] == 1:
            track.append(Func(node.clearTransparency))
        elif scale[3] == 0:
            track.append(Func(node.clearTransparency))
            for piece in pieces:
                if piece.getName()[:7] == 'muzzle-' and piece.getName()[-8:] != '-neutral':
                    continue
                track.append(HideInterval(piece))

        self.generateHat(*self.hat)
        self.generateGlasses(*self.glasses)
        return track

    def __doCheesyEffect(self, effect, lerpTime):
        if effect == ToontownGlobals.CEBigHead:
            return self.__doHeadScale(2.5, lerpTime)
        elif effect == ToontownGlobals.CESmallHead:
            return self.__doHeadScale(0.5, lerpTime)
        elif effect == ToontownGlobals.CEBigLegs:
            return self.__doLegsScale(1.4, lerpTime)
        elif effect == ToontownGlobals.CESmallLegs:
            return self.__doLegsScale(0.6, lerpTime)
        elif effect == ToontownGlobals.CEBigToon:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CESmallToon:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CEFlatPortrait:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CEFlatProfile:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CETransparent:
            return self.doToonColorScale(VBase4(1, 1, 1, 0.6), lerpTime, keepDefault=1)
        elif effect == ToontownGlobals.CENoColor:
            return self.__doToonColor(VBase4(1, 1, 1, 1), lerpTime)
        elif effect == ToontownGlobals.CEInvisible:
            return self.__doPartsColorScale(VBase4(1, 1, 1, 0), lerpTime)
        elif effect == ToontownGlobals.CEPumpkin:
            return self.__doPumpkinHeadSwitch(lerpTime, toPumpkin=True)
        elif effect == ToontownGlobals.CEBigWhite:
            return self.__doBigAndWhite(VBase4(1, 1, 1, 1), ToontownGlobals.BigToonScale, lerpTime)
        elif effect == ToontownGlobals.CESnowMan:
            return self.__doSnowManHeadSwitch(lerpTime, toSnowMan=True)
        elif effect == ToontownGlobals.CEGreenToon:
            return self.__doGreenToon(lerpTime, toGreen=True)
        elif effect == ToontownGlobals.CEWireFrame:
            return self.__doWireFrameToon(lerpTime, toWireFrame=True)
        elif effect == ToontownGlobals.CELongLegs:
            return self.__doLegsScale((1.0, 1.0, 5.5), lerpTime)
        elif effect == ToontownGlobals.CEWide:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CENoTorso:
            return self.__doNoTorsoToon(lerpTime, toNoTorso=True)
        elif effect == ToontownGlobals.CEMagicCat:
            return self.__doMagicCat(lerpTime, toMagicCat=True)
        elif effect == ToontownGlobals.CEVirtual:
            return self.__doVirtual()
        elif effect == ToontownGlobals.CE20Dog:
            return self.__do20Dog(lerpTime, to20Dog=True)
        elif effect == ToontownGlobals.CEGhost:
            alpha = 0
            if localAvatar.seeGhosts:
                alpha = 0.2
            return Sequence(self.__doToonGhostColorScale(VBase4(1, 1, 1, alpha), lerpTime, keepDefault=1),
                            Func(self.nametag3d.hide))
        return Sequence()

    def __undoCheesyEffect(self, effect, lerpTime):
        if effect == ToontownGlobals.CEBigHead:
            return self.__doHeadScale(None, lerpTime)
        elif effect == ToontownGlobals.CESmallHead:
            return self.__doHeadScale(None, lerpTime)
        if effect == ToontownGlobals.CEBigLegs:
            return self.__doLegsScale(None, lerpTime)
        elif effect == ToontownGlobals.CESmallLegs:
            return self.__doLegsScale(None, lerpTime)
        elif effect == ToontownGlobals.CEBigToon:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CESmallToon:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CEFlatPortrait:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CEFlatProfile:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CETransparent:
            return self.doToonColorScale(None, lerpTime, keepDefault=1)
        elif effect == ToontownGlobals.CENoColor:
            return self.__doToonColor(None, lerpTime)
        elif effect == ToontownGlobals.CEInvisible:
            return self.__doPartsColorScale(None, lerpTime)
        elif effect == ToontownGlobals.CEPumpkin:
            return self.__doPumpkinHeadSwitch(lerpTime, toPumpkin=False)
        elif effect == ToontownGlobals.CEBigWhite:
            return self.__doBigAndWhite(None, None, lerpTime)
        elif effect == ToontownGlobals.CESnowMan:
            return self.__doSnowManHeadSwitch(lerpTime, toSnowMan=False)
        elif effect == ToontownGlobals.CEGreenToon:
            return self.__doGreenToon(lerpTime, toGreen=False)
        elif effect == ToontownGlobals.CEWireFrame:
            return self.__doWireFrameToon(lerpTime, toWireFrame=False)
        elif effect == ToontownGlobals.CELongLegs:
            return self.__doLegsScale(None, lerpTime)
        elif effect == ToontownGlobals.CEWide:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CENoTorso:
            return self.__doNoTorsoToon(lerpTime, toNoTorso=False)
        elif effect == ToontownGlobals.CEMagicCat:
            return self.__doMagicCat(lerpTime, toMagicCat=False)
        elif effect == ToontownGlobals.CEVirtual:
            return self.__doUnVirtual()
        elif effect == ToontownGlobals.CE20Dog:
            return self.__do20Dog(lerpTime, to20Dog=False)
        elif effect == ToontownGlobals.CEGhost:
            return Sequence(Func(self.tryShowNametag), self.__doToonGhostColorScale(None, lerpTime, keepDefault=1))
        return Sequence()

    def putOnSuit(self, suitType, setDisplayName=True, displayLevel = None, rental=False, cogType=0):
        if hasattr(self, 'suit') and hasattr(self, 'suitGeom'):
            if self.suit or self.suitGeom:
                return
        if hasattr(self, 'savedCheesyEffect') and self.savedCheesyEffect == ToontownGlobals.CENoTorso:
            self.clearCheesyEffect()
        # Let's determine what kind of suit we're going to transform into
        from toontown.suit import Suit
        dept = SuitDNA.getSuitDept(suitType)
        suit = Suit.Suit(isToon=True)
        dna = SuitDNA.SuitDNA()
        # Time to generate our suit
        dna.newSuit(suitType)
        suit.setDNA(dna)
        suit.initializeDropShadow()
        suit.setPos(self.getPos())
        suit.setHpr(self.getHpr())
        # Normal, waiter, and rental disguises should hide the Cog head
        if not cogType or cogType in ToontownGlobals.PutOnSuitToonHead:
            for part in suit.getHeadParts():
                part.hide()
        # Make the suit change based on the type
        if cogType in ToontownGlobals.PutOnSuitSkelecog:
            suit.makeSkeleton()
        elif rental and not suit.isSkeleton:
            suit.makeRentalSuit(dept)
        elif cogType in ToontownGlobals.PutOnSuitWaiter:
            suit.makeWaiter()
        if cogType in ToontownGlobals.PutOnSuitVirtual:
            suit.makeVirtual()
        if cogType in ToontownGlobals.PutOnSuitSkeleRevive:
            suit.makeSkeleRevive()
        # Hide or show the Toon head depending on the type
        if suit.getBodyType() == 'a':
            suitHeadNull = suit.find('**/to_head')
        else:
            suitHeadNull = suit.find('**/joint_head')
        toonHead = self.getPart('head', '1000')
        toonGeom = self.getGeomNode()
        toonGeom.hide()
        worldScale = toonHead.getScale(render)
        self.headOrigScale = toonHead.getScale()
        headPosNode = hidden.attachNewNode('headPos')
        if cogType and cogType not in ToontownGlobals.PutOnSuitToonHead or suit.isSkeleton:
            toonHead.reparentTo(hidden)
        else:
            toonHead.reparentTo(headPosNode)
        toonHead.setPos(0, 0, 0.2)
        headPosNode.reparentTo(suitHeadNull)
        headPosNode.setScale(render, worldScale)
        # Further setup
        suitGeom = suit.getGeomNode()
        suitGeom.reparentTo(self)
        self.suit = suit
        self.suitGeom = suitGeom
        self.setHeight(suit.getHeight() * self.toonScale)
        self.nametag3d.setPos(0, 0, self.height + 1.3)
        if self.isLocal():
            self.oldForward = ToontownGlobals.ToonForwardSpeed
            self.oldReverse = ToontownGlobals.ToonReverseSpeed
            self.oldRotate = ToontownGlobals.ToonRotateSpeed
            ToontownGlobals.ToonForwardSpeed = ToontownGlobals.SuitWalkSpeed
            ToontownGlobals.ToonReverseSpeed = ToontownGlobals.SuitWalkSpeed
            ToontownGlobals.ToonRotateSpeed = ToontownGlobals.ToonRotateSlowSpeed
            if self.hasTrackAnimToSpeed():
                self.stopTrackAnimToSpeed()
                self.startTrackAnimToSpeed()
            self.chatMgr.chatInputSpeedChat.addCogMenu(suitType)
        if self.getTPose():
            self.suit.stop()
            self.suit.unloadAnims()
        else:
            self.suit.loop('neutral')
        self.setTransformationsIndex(ToontownGlobals.TransformationCog, suitType)
        self.disguiseType = cogType
        self.setFont(ToontownGlobals.getSuitFont())
        if setDisplayName:
            if hasattr(base, 'idTags') and base.idTags:
                name = self.getAvIdName()
            else:
                name = self.getName()
            level = displayLevel if displayLevel else self.cogLevels[SuitDNA.suitDepts.index(SuitDNA.getSuitDept(suitType))] + 1
            if cogType not in ToontownGlobals.PutOnSuitToonHead:
                if cogType in ToontownGlobals.PutOnSuitSkelecog:
                    suitName = TTLocalizer.Skeleton
                else:
                    suitName = DataPackManager.getLocalizedText(base.cr.dataPackMgr.getCogAppearance(suitType)[CogAppearanceIndex.NAME])
                if cogType in ToontownGlobals.PutOnSuitSkeleRevive:
                    level = '%s%s' % (level, TTLocalizer.SkeleRevivePostFix)
                name = TTLocalizer.SuitBaseNameWithLevel % {'name': suitName,
                                                            'dept': SuitDNA.getDeptFullname(dept),
                                                            'level': level}
                self.setName(name)
                self.nametag.setDisplayName(name)
                self.nametag.setNameWordwrap(9.0)
            else:
                suitName = DataPackManager.getLocalizedText(base.cr.dataPackMgr.getCogAppearance(suitType)[CogAppearanceIndex.NAME])
                name = TTLocalizer.SuitBaseNameWithLevel % {'name': name, 'dept': suitName, 'level': level}
                self.setName(name)
                self.nametag.setDisplayName(name)
                self.nametag.setNameWordwrap(9.0)
        if hasattr(self, 'hp'):
            self.suit.currHP = self.hp
            self.suit.maxHP = self.maxHp
            if self.maxHp == self.hp:
                self.suit.showCorpMedallion()
                self.suit.healthBar.hide()
            else:
                self.suit.hideCorpMedallion()
                self.suit.healthBar.show()
                self.suit.updateHealthBar()
        # For not breaking NPCs when they try to put on suits
        scale = suitGeom.getScale()
        scaleTuple = (scale.getX(), scale.getY(), scale.getZ())
        scaleEffect = self.getToonScaleEffect()
        if type(scaleEffect) == LVector3f:
            scaleEffectTuple = (scaleEffect.getX(), scaleEffect.getY(), scaleEffect.getZ())
            properScale = tuple(l * r for l, r in zip(scaleTuple, scaleEffectTuple))
            self.suitGeom.setScale(*properScale)
        else:
            self.suitGeom.setScale(scale.getX() * scaleEffect, scale.getY() * scaleEffect, scale.getZ() * scaleEffect)

    def getToonScaleEffect(self, scale=None):
        # Get the Toon's current scale
        if not scale:
            scale = self.getToonScale()

        # Adjust scale based on cheesy effect
        effect = self.cheesyEffect
        if effect == ToontownGlobals.CEBigToon or effect == ToontownGlobals.CEBigWhite:
            scale *= ToontownGlobals.BigToonScale
        elif effect == ToontownGlobals.CESmallToon:
            scale *= ToontownGlobals.SmallToonScale
        elif effect == ToontownGlobals.CELongLegs:
            scale *= ToontownGlobals.LongLegsScale
        elif effect == ToontownGlobals.CEFlatPortrait:
            scale = LVector3f(scale, 0.05 * scale, scale)
        elif effect == ToontownGlobals.CEFlatProfile:
            scale = LVector3f(0.05 * scale, scale, scale)
        elif effect == ToontownGlobals.CEWide:
            scale = LVector3f(5 * scale, scale, scale)

        return scale

    def makeWaiter(self):
        if not self.getTransformationsIndex(ToontownGlobals.TransformationCog):
            return
        self.suit.makeWaiter(self.suitGeom)

    def putOnChar(self, charType):
        Emote.globalEmote.disableAll(self)
        from toontown.char import Char
        from toontown.char import CharDNA
        char = Char.Char()
        dna = CharDNA.CharDNA()
        dna.newChar(CharGlobals.charTypes[charType])
        char.setDNA(dna)
        char.addActive()
        char.initializeDropShadow()
        char.setPos(self.getPos())
        char.setHpr(self.getHpr())
        char.startBlink()
        char.startEarTask()
        toonGeom = self.getGeomNode()
        toonGeom.hide()
        charGeom = char.getGeomNode()
        charGeom.reparentTo(self)
        self.char = char
        self.charGeom = charGeom
        self.setFont(ToontownGlobals.getToonFont())
        self.resetHeight()
        if self.getTPose():
            self.char.stop()
            self.char.unloadAnims()
        else:
            self.char.loop('neutral')
        self.charGeom.setScale(self.getToonScale())

        self.changeTransformation()

    def putOnDoodle(self, petName=None, petDNA=None):
        Emote.globalEmote.disableAll(self)
        from toontown.pets import Pet
        pet = Pet.Pet()
        if not petDNA or len(petDNA) < 9:
            petDNA = [-1, 0, 0, -1, 4, 0, 0, 5, 1, 191, -263, 4.597, 109]
        pet.setDNA(petDNA)
        pet.addActive()
        pet.startBlink()
        pet.initializeDropShadow()
        pet.setPos(self.getPos())
        pet.setHpr(self.getHpr())
        toonGeom = self.getGeomNode()
        toonGeom.hide()
        petGeom = pet.getGeomNode()
        petGeom.reparentTo(self)
        self.pet = pet
        self.petGeom = petGeom
        self.setFont(ToontownGlobals.getToonFont())
        if petName:
            self.setDisplayName(petName)
        self.resetHeight()
        if self.getTPose():
            self.pet.stop()
            self.pet.unloadAnims()
        else:
            self.pet.loop('neutral')
        self.petGeom.setScale(self.getToonScale())

        self.changeTransformation()

    def putOnGoon(self, goonType):
        Emote.globalEmote.disableAll(self)
        from toontown.suit import Goon
        goonType = SuitDNA.goonTypes[goonType]
        goon = Goon.Goon(goonType)
        goon.addActive()
        goon.doId = self.doId
        goon.initializeDropShadow()
        goon.setPos(self.getPos())
        goon.setHpr(self.getHpr())
        toonGeom = self.getGeomNode()
        toonGeom.hide()
        goonGeom = goon.getGeomNode()
        goonGeom.reparentTo(self)
        self.goon = goon
        self.goonGeom = goonGeom
        self.setFont(ToontownGlobals.getSuitFont())
        self.resetHeight()

        if self.getTPose():
            self.goon.stop()
            self.goon.unloadAnims()
        else:
            self.goon.pose('neutral', 96)
        self.goonGeom.setScale(self.getToonScale())

        self.changeTransformation()

    def putOnProp(self, propName):
        Emote.globalEmote.disableAll(self)
        self.propName = PropGlobals.getPropNameCaseInsensitive(propName)
        prop = PropGlobals.PropPool.getProp(self.propName)
        prop.setDepthTest(1)
        prop.setDepthWrite(1)
        pitch = NodePath('prop_pitch')
        scale = pitch.attachNewNode('prop_scale')
        prop.reparentTo(scale)
        bMin, bMax = pitch.getTightBounds()
        center = (bMin + bMax) / 2.0
        corner = Vec3(bMax - center)
        scale.setScale(1.0 / max(corner[0], corner[1], corner[2]))
        prop.flattenStrong()
        prop.clearTransform()
        collisions = prop.findAllMatches('**/+CollisionNode')
        if collisions:
            for coll in collisions:
                coll.stash()
        pitch.setPos(self.getPos())
        pitch.setHpr(self.getHpr())
        toonGeom = self.getGeomNode()
        toonGeom.hide()
        pitch.wrtReparentTo(self)

        shadow = Avatar.ShadowCaster.dropShadowModel.copyTo(pitch)
        shadow.setZ(0.07)
        shadow.setScale(0.4)
        shadow.setAlphaScale(0.7)

        self.prop = pitch
        self.setFont(ToontownGlobals.getToonFont())
        self.resetHeight()

        self.prop.setScale(self.getToonScale())

        self.changeTransformation()

    def putOnBoss(self, bossType):
        Emote.globalEmote.disableAll(self)
        from toontown.suit import BossCog
        from toontown.suit import SuitDNA
        boss = BossCog.BossCog()
        boss.toon = self
        dna = SuitDNA.SuitDNA()
        dna.newBossCog(SuitDNA.suitDepts[bossType])
        if base.cr.newsManager.isHolidayRunning(ToontownGlobals.APRIL_FOOLS_COSTUMES):
            holidayId = 2
        elif base.cr.newsManager.isHolidayRunning(ToontownGlobals.WINTER_DECORATIONS):
            holidayId = 1
        else:
            holidayId = 0
        boss.setDNA(dna, holidayId, tangible = 0)
        boss.addActive()
        boss.initializeDropShadow()
        boss.setPos(self.getPos())
        boss.setHpr(self.getHpr())
        toonGeom = self.getGeomNode()
        toonGeom.hide()
        bossGeom = boss.getGeomNode()
        bossGeom.reparentTo(self)
        self.boss = boss
        self.bossGeom = bossGeom
        self.setFont(ToontownGlobals.getSuitFont())
        self.resetHeight()
        self.bossGeom.setScale(0.2)
        self.bossGeom.flattenLight()
        self.bossGeom.setScale(self.getToonScale())

        self.changeTransformation()

    def putOnFish(self, fishType):
        Emote.globalEmote.disableAll(self)
        fishInfo = ToontownGlobals.TransformationFishExtra.get(fishType)
        fish = FishBase.FishBase(fishType, 0, 0)
        fishActor = fish.getActor()
        fishActor.setPos(*fishInfo[ToontownGlobals.TransformationExtraPos])
        fishActor.setZ(fishActor.getZ() + 2)
        fishActor.setH(180 + fishInfo[ToontownGlobals.TransformationExtraH])
        toonGeom = self.getGeomNode()
        toonGeom.hide()
        fishGeom = fishActor.getGeomNode()
        fishGeom.reparentTo(self)
        self.fish = fishActor
        self.fishGeom = fishGeom
        self.setFont(ToontownGlobals.getToonFont())
        self.resetHeight()

        self.fishGeom.setScale(fishInfo[ToontownGlobals.TransformationExtraScale])
        self.fishGeom.flattenLight()
        self.fishGeom.setScale(self.getToonScale())

        if self.getTPose():
            if fishType == 10:
                self.fish.pose(fishInfo[ToontownGlobals.TransformationExtraAnimation], frame=40)
            else:
                self.fish.stop()
                self.fish.unloadAnims()
        else:
            if fishType == 10:
                self.fish.pingpong(fishInfo[ToontownGlobals.TransformationExtraAnimation], fromFrame=40, toFrame=55)
            else:
                self.fish.loop(fishInfo[ToontownGlobals.TransformationExtraAnimation])

        self.changeTransformation()

    def putOnButterfly(self, butterflyType: int, r: int, g: int, b: int):
        Emote.globalEmote.disableAll(self)
        wingTypes = ('wings_1', 'wings_2', 'wings_3', 'wings_4', 'wings_5', 'wings_6')
        butterfly = Actor.Actor('phase_4/models/props/SZ_butterfly-mod.bam',
                                {'glide': 'phase_4/models/props/SZ_butterfly-glide.bam'})
        butterfly.setBlend(frameBlend=ClientSettings.SmoothAnimations.get())
        toonGeom = self.getGeomNode()
        toonGeom.hide()
        butterfly.setZ(butterfly.getZ() + 2)
        butterfly.setH(180)
        butterfly.setScale(self.getToonScale())
        butterfly.flattenLight()
        butterfly.reparentTo(self)
        butterflyGeom = butterfly.getGeomNode()
        chosenType = wingTypes[butterflyType]
        for type in wingTypes:
            wing = butterflyGeom.find(f'**/{type}')
            if type != chosenType:
                wing.removeNode()
            else:
                wing.setColor(Vec4(r, g, b, 1))
        self.butterfly = butterfly
        self.resetHeight()

        if self.getTPose():
            self.butterfly.stop()
            self.butterfly.unloadAnims()
        else:
            self.butterfly.loop('glide')

        self.changeTransformation()

    def putOnMisc(self, miscType):
        toonGeom = self.getGeomNode()
        toonGeom.hide()

        if miscType == ToontownGlobals.TransformationMiscStatue:
            misc = Actor.Actor('phase_14.5/models/char/cj-statue-mod',
                               {'neutral': 'phase_14.5/models/char/cj-statue-neutral',
                                'walk': 'phase_14.5/models/char/cj-statue-walk',
                                'run': 'phase_14.5/models/char/cj-statue-walk',
                                'jump': 'phase_14.5/models/char/cj-statue-jump',
                                'victory': 'phase_14.5/models/char/cj-statue-dance'})
        elif miscType == ToontownGlobals.TransformationMiscPanda:
            misc = Actor.Actor('phase_3/models/char/panda', {'walk': 'phase_3/models/char/panda-walk',
                                                             'run': 'phase_3/models/char/panda-walk'})
            misc.setScale(0.25)
            misc.setH(180)
            misc.flattenLight()
        elif miscType == ToontownGlobals.TransformationMiscChaser:
            misc = Actor.Actor()
            misc.loadModel('phase_14.5/models/char/toon-chaser-mod-legs', 'legs')
            misc.loadAnims(LegsAnimDict['l'], 'legs')
            for shoe in ["shoes", "boots_short", "boots_long"]:
                misc.find("**/%s" % shoe).hide()
            misc.loadModel('phase_14.5/models/char/toon-chaser-mod-torso', 'torso')
            misc.loadAnims(TorsoAnimDict['ls'], 'torso')
            misc.attach('torso', 'legs', 'joint_hips')
            misc.loadModel('phase_14.5/models/char/toon-chaser-mod-head', 'head')
            misc.attach('head', 'torso', 'def_head')
            misc.find('**/head-long').hide()
        elif miscType == ToontownGlobals.TransformationMiscCheese:
            misc = Actor.Actor('phase_14.5/models/char/suitA2-mod', {'neutral': 'phase_14.5/models/char/suitA2-neutral',
                                                                     'walk': 'phase_14.5/models/char/suitA2-walk',
                                                                     'run': 'phase_14.5/models/char/suitA2-walk'})
            misc.setH(180)
            misc.flattenLight()
        elif miscType == ToontownGlobals.TransformationMiscMickey:
            misc = Actor.Actor()
            misc.loadModel('phase_14.5/models/char/mickey-toon-legs', 'legs')
            misc.loadAnims(LegsAnimDict['s'], 'legs')
            misc.loadModel('phase_14.5/models/char/mickey-toon-torso', 'torso')
            misc.loadAnims(TorsoAnimDict['m'], 'torso')
            misc.attach('torso', 'legs', 'joint_hips')
            misc.loadModel('phase_14.5/models/char/mickey-toon-head', 'head')
            misc.attach('head', 'torso', 'def_head')
            misc.setScale(0.75)
            misc.flattenLight()

        shadow = Avatar.ShadowCaster.dropShadowModel.copyTo(misc)
        shadow.setZ(0.07)
        shadow.setScale(0.7)
        shadow.setAlphaScale(0.7)
        misc.setBlend(frameBlend=ClientSettings.SmoothAnimations.get())

        misc.reparentTo(self)

        self.misc = misc
        self.misc.flattenLight()
        self.misc.setScale(self.getToonScale())

        self.setFont(ToontownGlobals.getToonFont())
        self.resetHeight()

        if self.getTPose():
            self.misc.stop()
            self.misc.unloadAnims()
        else:
            self.misc.loop('neutral')

        self.changeTransformation()

    def putOnStreet(self, streetType):
        Emote.globalEmote.disableAll(self)
        toonGeom = self.getGeomNode()
        toonGeom.hide()

        from toontown.hood import StreetProp
        street = StreetProp.StreetProp(streetType)
        street.addActive()
        street.initializeDropShadow()
        street.setPos(self.getPos())
        street.setHpr(self.getHpr())

        streetGeom = street.getGeomNode()
        streetGeom.reparentTo(self)

        self.street = street
        self.streetGeom = streetGeom
        self.streetGeom.setH(180)
        self.streetGeom.flattenLight()
        self.streetGeom.setScale(self.getToonScale())

        # self.setFont(ToontownGlobals.getSuitFont())
        # self.resetHeight()

        if self.getTPose():
            self.street.stop()
            self.street.unloadAnims()
        else:
            self.street.loop('neutral')

        self.changeTransformation()

    def takeOffTransformation(self, override=None, effect=True):
        if not self.getTransformed() and override is None:
            return

        if override is None:
            transformationIndex = self.getActiveTransformationIndex()
        else:
            transformationIndex = override
        if transformationIndex == ToontownGlobals.TransformationToon:
            return
        elif transformationIndex == ToontownGlobals.TransformationCog:
            if hasattr(self, 'suit'):
                if not self.suit:
                    return
            else:
                return
            self.disguiseType = 0
            toonHeadNull = self.find('**/1000/**/def_head')
            if not toonHeadNull:
                toonHeadNull = self.find('**/1000/**/joint_head')
            toonHead = self.getPart('head', '1000')
            toonHead.reparentTo(toonHeadNull)
            toonHead.setScale(self.headOrigScale)
            toonHead.setPos(0, 0, 0)
            headPosNode = self.suitGeom.find('**/headPos')
            headPosNode.removeNode()
            self.suitGeom.reparentTo(self.suit)
            self.resetHeight()
            self.nametag3d.setPos(0, 0, self.height + 0.5)
            self.tryShowGeom()
            self.setTransformationsIndex(ToontownGlobals.TransformationCog, '')
            self.setFont(ToontownGlobals.getToonFont())
            self.nametag.setNameWordwrap(-1)
            if hasattr(base, 'idTags') and base.idTags:
                name = self.getAvIdName()
            else:
                name = self.getName()
            self.setDisplayName(name)
            if self.isLocal():
                ToontownGlobals.ToonForwardSpeed = self.oldForward
                ToontownGlobals.ToonReverseSpeed = self.oldReverse
                ToontownGlobals.ToonRotateSpeed = self.oldRotate
                if self.hasTrackAnimToSpeed():
                    self.stopTrackAnimToSpeed()
                    self.startTrackAnimToSpeed()
                del self.oldForward
                del self.oldReverse
                del self.oldRotate
                self.chatMgr.chatInputSpeedChat.removeCogMenu()
            self.suit.delete()
            del self.suit
            del self.suitGeom

            if hasattr(self, 'reconsiderCheesyEffect') and hasattr(self, 'savedCheesyEffect') and self.savedCheesyEffect == ToontownGlobals.CENoTorso:
                self.reconsiderCheesyEffect()

        elif transformationIndex == ToontownGlobals.TransformationClassicChar:
            Emote.globalEmote.releaseAll(self)
            self.setTransformationsIndex(ToontownGlobals.TransformationClassicChar, 0)
            self.charGeom.reparentTo(self.char)
            self.resetHeight()
            self.nametag3d.setPos(0, 0, self.height + 0.5)
            toonGeom = self.getGeomNode()
            toonGeom.show()
            self.setFont(ToontownGlobals.getToonFont())
            self.char.stopBlink()
            self.char.stopEarTask()
            self.char.removeActive()
            self.char.delete()
            del self.char
            del self.charGeom
        elif transformationIndex == ToontownGlobals.TransformationDoodle:
            Emote.globalEmote.releaseAll(self)
            self.setTransformationsIndex(ToontownGlobals.TransformationDoodle, 0)
            self.petGeom.reparentTo(self.pet)
            self.resetHeight()
            self.nametag3d.setPos(0, 0, self.height + 0.5)
            toonGeom = self.getGeomNode()
            toonGeom.show()
            self.setFont(ToontownGlobals.getToonFont())
            if hasattr(base, 'idTags') and base.idTags:
                name = self.getAvIdName()
            else:
                name = self.getName()
            self.setDisplayName(name)
            self.pet.removeActive()
            self.pet.delete()
            del self.pet
            del self.petGeom
        elif transformationIndex == ToontownGlobals.TransformationGoon:
            Emote.globalEmote.releaseAll(self)
            self.setTransformationsIndex(ToontownGlobals.TransformationGoon, 0)
            self.goonGeom.reparentTo(self.goon)
            self.resetHeight()
            self.nametag3d.setPos(0, 0, self.height + 0.5)
            toonGeom = self.getGeomNode()
            toonGeom.show()
            self.setFont(ToontownGlobals.getToonFont())
            self.goon.removeActive()
            self.goon.delete()
            del self.goon
            del self.goonGeom
        elif transformationIndex == ToontownGlobals.TransformationProp:
            Emote.globalEmote.releaseAll(self)
            self.setTransformationsIndex(ToontownGlobals.TransformationProp, '')
            self.resetHeight()
            self.nametag3d.setPos(0, 0, self.height + 0.5)
            toonGeom = self.getGeomNode()
            toonGeom.show()
            self.setFont(ToontownGlobals.getToonFont())
            self.prop.removeNode()
            del self.prop
            if self.propName:
                del self.propName
        elif transformationIndex == ToontownGlobals.TransformationBoss:
            Emote.globalEmote.releaseAll(self)
            self.setTransformationsIndex(ToontownGlobals.TransformationBoss, 0)
            self.bossGeom.reparentTo(self.boss)
            self.resetHeight()
            self.nametag3d.setPos(0, 0, self.height + 0.5)
            toonGeom = self.getGeomNode()
            toonGeom.show()
            self.setFont(ToontownGlobals.getToonFont())
            self.boss.removeActive()
            self.boss.delete()
            del self.boss
            del self.bossGeom
        elif transformationIndex == ToontownGlobals.TransformationFish:
            Emote.globalEmote.releaseAll(self)
            self.setTransformationsIndex(ToontownGlobals.TransformationFish, 0)
            self.resetHeight()
            self.nametag3d.setPos(0, 0, self.height + 0.5)
            toonGeom = self.getGeomNode()
            toonGeom.show()
            self.setFont(ToontownGlobals.getToonFont())
            self.fish.delete()
            self.fishGeom.removeNode()
            del self.fish
            del self.fishGeom
        elif transformationIndex == ToontownGlobals.TransformationButterfly:
            Emote.globalEmote.releaseAll(self)
            self.setTransformationsIndex(ToontownGlobals.TransformationButterfly, 0)
            self.resetHeight()
            self.nametag3d.setPos(0, 0, self.height + 0.5)
            toonGeom = self.getGeomNode()
            toonGeom.show()
            self.setFont(ToontownGlobals.getToonFont())
            self.butterfly.cleanup()
            self.butterfly.delete()
            self.butterfly.removeNode()
            del self.butterfly
        elif transformationIndex == ToontownGlobals.TransformationMisc:
            self.setTransformationsIndex(ToontownGlobals.TransformationMisc, 0)
            self.resetHeight()
            self.nametag3d.setPos(0, 0, self.height + 0.5)
            toonGeom = self.getGeomNode()
            toonGeom.show()
            self.setFont(ToontownGlobals.getToonFont())
            self.misc.cleanup()
            self.misc.delete()
            self.misc.removeNode()
            del self.misc
        elif transformationIndex == ToontownGlobals.TransformationStreet:
            Emote.globalEmote.releaseAll(self)
            self.setTransformationsIndex(ToontownGlobals.TransformationStreet, 0)
            self.streetGeom.reparentTo(self.street)
            self.resetHeight()
            self.nametag3d.setPos(0, 0, self.height + 0.5)
            toonGeom = self.getGeomNode()
            toonGeom.show()
            self.setFont(ToontownGlobals.getToonFont())
            self.street.removeActive()
            self.street.delete()
            del self.street
            del self.streetGeom
        else:
            return

        if effect:
            self.changeTransformation()

    def changeTransformation(self):

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            dustCloud.reparentTo(self)
            return Sequence(dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        dust.start()

        messenger.send(self.uniqueName('transformation-applied'))

    def getTransformed(self):
        transformations = self.getTransformations()
        for x in range(len(transformations)):
            transformation = transformations[x]
            if isinstance(transformation, int) and transformation > 0 and x not in (ToontownGlobals.TransformationCog, ToontownGlobals.TransformationProp):
                return True
            elif transformation != '' and x in (ToontownGlobals.TransformationCog, ToontownGlobals.TransformationProp):
                return True
        return False

    def setTransformationsIndex(self, index, state):
        self.transformations[index] = state
        self.resetHeight()
        if self.isLocal():
            self.initCameraPositions()
            self.resetCameraPosition()
            retroMode = ClientSettings.ClassicSFX.get()
            if not retroMode:
                self.updateFootstepSounds()

    def getTransformationsIndex(self, index):
        return self.transformations[index]

    def setTransformations(self, transformations):
        self.transformations = transformations

    def getTransformations(self):
        return self.transformations

    def getActiveTransformation(self):
        currentTransformation = self.getActiveTransformationIndex()

        if currentTransformation == -1:
            return self
        elif currentTransformation == ToontownGlobals.TransformationCog:
            return self.suit
        elif currentTransformation == ToontownGlobals.TransformationClassicChar:
            return self.char
        elif currentTransformation == ToontownGlobals.TransformationDoodle:
            return self.pet
        elif currentTransformation == ToontownGlobals.TransformationGoon:
            return self.goon
        elif currentTransformation == ToontownGlobals.TransformationProp:
            # Props are NodePaths so I'm just gonna apply it to the Toon instead
            return self
        elif currentTransformation == ToontownGlobals.TransformationBoss:
            return self.boss
        elif currentTransformation == ToontownGlobals.TransformationFish:
            return self.fish
        elif currentTransformation == ToontownGlobals.TransformationButterfly:
            return self.butterfly
        elif currentTransformation == ToontownGlobals.TransformationMisc:
            return self.misc
        elif currentTransformation == ToontownGlobals.TransformationStreet:
            return self.street
        else:
            return None

    def getActiveTransformationIndex(self):
        currentTransformation = -1
        activeTransformations = self.getTransformations()
        for transformation in activeTransformations:
            currentTransformation = activeTransformations.index(transformation)
            if currentTransformation in (ToontownGlobals.TransformationCog, ToontownGlobals.TransformationProp):
                if transformation != '':
                    break
                else:
                    currentTransformation = -1
            if isinstance(transformation, int) and transformation > 0:
                break
            else:
                currentTransformation = -1

        return currentTransformation

    def getActiveTransformationGeom(self):
        currentTransformation = self.getActiveTransformationIndex()

        if currentTransformation == ToontownGlobals.TransformationToon:
            return self.getGeomNode().getChild(0) if not self.isEmpty() else None
        elif currentTransformation == ToontownGlobals.TransformationCog:
            return self.suitGeom if hasattr(self, 'suitGeom') else None
        elif currentTransformation == ToontownGlobals.TransformationClassicChar:
            return self.charGeom if hasattr(self, 'charGeom') else None
        elif currentTransformation == ToontownGlobals.TransformationDoodle:
            return self.petGeom if hasattr(self, 'petGeom') else None
        elif currentTransformation == ToontownGlobals.TransformationGoon:
            return self.goonGeom if hasattr(self, 'goonGeom') else None
        elif currentTransformation == ToontownGlobals.TransformationProp:
            return self.prop if hasattr(self, 'prop') else None
        elif currentTransformation == ToontownGlobals.TransformationBoss:
            return self.bossGeom if hasattr(self, 'bossGeom') else None
        elif currentTransformation == ToontownGlobals.TransformationFish:
            return self.fishGeom if hasattr(self, 'fishGeom') else None
        elif currentTransformation == ToontownGlobals.TransformationButterfly:
            return self.butterfly if hasattr(self, 'butterfly') else None
        elif currentTransformation == ToontownGlobals.TransformationMisc:
            return self.misc if hasattr(self, 'misc') else None
        elif currentTransformation == ToontownGlobals.TransformationStreet:
            return self.streetGeom if hasattr(self, 'streetGeom') else None
        else:
            return None

    def playCalcTransformedAnim(self, animName, extraArgs = None, play=False):
        if extraArgs is None:
            extraArgs = []
        if self.getTransformed():
            self.playTransformationAnim(animName, extraArgs)
        else:
            if play:
                self.play(animName)
            else:
                self.loop(animName)

    # TODO: Refactor this function. 
    def playTransformationAnim(self, animName, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        if not animName:
            return
        if self.getTPose():
            return Sequence(Wait(1.0))

        currentTransformation = self.getActiveTransformationIndex()
        transformationIndex = self.getTransformationsIndex(currentTransformation)
        scale = self.getToonScaleEffect()

        if currentTransformation == ToontownGlobals.TransformationCog:
            if animName == 'neutral':
                self.suit.pose('neutral', int(self.getNumFrames('neutral') * self.randGen.random()))
                self.suit.loop('neutral', restart=0)
                self.suit.setPlayRate(self.suit.getPlayRate(), 'neutral')
            elif animName == 'run' or animName == 'walk':
                self.suit.loop('walk')
                self.suit.setPlayRate(self.suit.getPlayRate(), 'walk')
            elif animName == 'victory':
                self.suit.loop('victory')
                self.suit.setPlayRate(self.suit.getPlayRate(), 'victory')
            elif animName == 'jump':
                anim = 'slip-forward'
                self.playingAnim = anim
                self.suit.setPlayRate(1, anim)
                if hasattr(self, 'jump') and self.jump:
                    self.jump.finish()
                    self.jump = None
                if self.suit.getBodyType() == 'a':
                    self.jump = ActorInterval(self.suit, 'slip-forward', startFrame=55)
                elif self.suit.getBodyType() == 'b':
                    self.jump = Sequence(ActorInterval(self.suit, 'quick-jump', playRate=5, endFrame=15),
                                                       ActorInterval(self.suit, 'quick-jump', startFrame=15,
                                                                     endFrame=30),
                                                       ActorInterval(self.suit, 'quick-jump', startFrame=107))
                elif self.suit.getBodyType() == 'c':
                    self.jump = ActorInterval(self.suit, 'slip-forward', startFrame=59)
                self.jump.start()
            elif animName == 'jump-squat':
                anim = 'slip-forward'
                self.playingAnim = anim
                self.suit.setPlayRate(1, anim)
                if hasattr(self, 'jump') and self.jump:
                    self.jump.finish()
                    self.jump = None
                if self.suit.getBodyType() == 'a':
                    self.jump = ActorInterval(self.suit, 'slip-forward', startFrame=55, endFrame=63)
                elif self.suit.getBodyType() == 'b':
                    self.jump = Sequence(ActorInterval(self.suit, 'quick-jump', playRate=5, endFrame=15),
                                                     ActorInterval(self.suit, 'quick-jump', startFrame=15, endFrame=30))
                elif self.suit.getBodyType() == 'c':
                    self.jump = ActorInterval(self.suit, 'slip-forward', startFrame=59, endFrame=69)
                self.jump.start()
            elif animName == 'jump-idle':
                anim = 'slip-forward'
                self.playingAnim = anim
                self.suit.setPlayRate(1, anim)
                if self.suit.getBodyType() == 'a':
                    self.suit.pose(anim, 66)
                elif self.suit.getBodyType() == 'b':
                    self.suit.pose('quick-jump', 30)
                elif self.suit.getBodyType() == 'c':
                    self.suit.pose(anim, 69)
            elif animName == 'jump-land':
                anim = 'slip-forward'
                self.playingAnim = anim
                self.suit.setPlayRate(1, anim)
                if hasattr(self, 'jump') and self.jump:
                    self.jump.finish()
                    self.jump = None
                if self.suit.getBodyType() == 'a':
                    self.jump = ActorInterval(self.suit, 'slip-forward', startFrame=66)
                elif self.suit.getBodyType() == 'b':
                    self.jump = ActorInterval(self.suit, 'quick-jump', startFrame=107)
                elif self.suit.getBodyType() == 'c':
                    self.jump = ActorInterval(self.suit, 'slip-forward', startFrame=69)
                self.jump.start()
            elif animName == 'cringe':
                self.suit.loop('squirt-small-react')
            elif animName == 'openBook':
                self.loop('neutral')
                if not self.cogBook:
                    if self.suit.getBodyType() == 'c':
                        model = 'phone'
                    else:
                        model = 'rollodex'
                    self.cogBook = BattleProps.globalPropPool.getProp(model)
                    hand = self.suit.getLeftHand()
                    self.cogBook.reparentTo(hand)
                if self.suit.getBodyType() == 'b':
                    self.cogBook.setPos(0.12, 0.24, 0.01)
                    self.cogBook.setScale(0.91, 0.91, 0.91)
                    self.cogBook.setHpr(99.032, 5.973, -179.839)
                    growTrack = self.cogBook.scaleInterval(0.5, 0.91, startScale=0)
                else:
                    if self.suit.getBodyType() == 'c':
                        self.cogBook.setPos(-0.51, 0.83, -0.1)
                    else:
                        self.cogBook.setPos(-0.51, -0.03, -0.1)
                    self.cogBook.setScale(1.2, 1.2, 1.2)
                    self.cogBook.setHpr(89.673, 2.166, 177.786)
                    growTrack = self.cogBook.scaleInterval(0.5, 1.2, startScale=0)
                if hasattr(self, 'uniqueName'):
                    trackName = self.uniqueName('openBook')
                else:
                    trackName = 'openBook'
                if self.suit.getBodyType() == 'c':
                    track = Sequence(Parallel(ActorInterval(self.suit, 'phone', endFrame=24), growTrack),
                                          name=trackName)
                else:
                    track = Sequence(
                        Parallel(ActorInterval(self.suit, 'roll-o-dex', playRate=1.5, endFrame=36), growTrack),
                        name=trackName)
                return track
            elif animName == 'readBook':
                self.loop('neutral')
                if not self.cogBook:
                    if self.suit.getBodyType() == 'c':
                        model = 'phone'
                    else:
                        model = 'rollodex'
                    self.cogBook = BattleProps.globalPropPool.getProp(model)
                    hand = self.suit.getLeftHand()
                    self.cogBook.reparentTo(hand)
                if self.suit.getBodyType() == 'b':
                    self.cogBook.setPos(0.12, 0.24, 0.01)
                    self.cogBook.setScale(0.91, 0.91, 0.91)
                    self.cogBook.setHpr(99.032, 5.973, -179.839)
                else:
                    if self.suit.getBodyType() == 'c':
                        self.cogBook.setPos(-0.51, 0.83, -0.1)
                    else:
                        self.cogBook.setPos(-0.51, -0.03, -0.1)
                    self.cogBook.setScale(1.2, 1.2, 1.2)
                    self.cogBook.setHpr(89.673, 2.166, 177.786)
                if self.suit.getBodyType() == 'c':
                    self.suit.pingpong('phone', fromFrame=22, toFrame=38)
                else:
                    self.suit.pingpong('roll-o-dex', fromFrame=28, toFrame=50)
            elif animName == 'closeBook':
                self.loop('neutral')
                if not self.cogBook:
                    if self.suit.getBodyType() == 'c':
                        model = 'phone'
                    else:
                        model = 'rollodex'
                    self.cogBook = BattleProps.globalPropPool.getProp(model)
                    hand = self.suit.getLeftHand()
                    self.cogBook.reparentTo(hand)
                if self.suit.getBodyType() == 'b':
                    self.cogBook.setPos(0.12, 0.24, 0.01)
                    self.cogBook.setScale(0.91, 0.91, 0.91)
                    self.cogBook.setHpr(99.032, 5.973, -179.839)
                    growTrack = self.cogBook.scaleInterval(0.5, 0, startScale=0.91)
                else:
                    if self.suit.getBodyType() == 'c':
                        self.cogBook.setPos(-0.51, 0.83, -0.1)
                    else:
                        self.cogBook.setPos(-0.51, -0.03, -0.1)
                    self.cogBook.setScale(1.2, 1.2, 1.2)
                    self.cogBook.setHpr(89.673, 2.166, 177.786)
                    growTrack = self.cogBook.scaleInterval(0.5, 0, startScale=1.2)
                if hasattr(self, 'uniqueName'):
                    trackName = self.uniqueName('closeBook')
                else:
                    trackName = 'closeBook'
                if self.suit.getBodyType() == 'c':
                    track = Sequence(
                        Parallel(ActorInterval(self.suit, 'phone', startFrame=24, endFrame=0), growTrack),
                        name=trackName)
                else:
                    track = Sequence(
                        Parallel(ActorInterval(self.suit, 'roll-o-dex', startFrame=36, endFrame=0), growTrack),
                        name=trackName)
                return track
            elif animName == 'teleport':
                track = self.getSuitTeleport(0)
                return track
            elif animName == 'teleportIn':
                track = self.getSuitTeleport(1)
                return track
            elif animName == 'sit':
                self.suit.loop('sit')
            elif animName == 'fallDown':
                track = Sequence(ActorInterval(self.suit, 'slip-backward'), name='fallTrack')
                return track
            elif animName == 'died':
                self.suit.getGeomNode().stash()
                track = MovieUtil.createSuitDeathTrack(self.suit, self, render)
                if self.disguiseType in ToontownGlobals.PutOnSuitToonHead:
                    suitHeadNull = self.suit.loseActor.find('**/joint_head')
                    toonHead = self.getPart('head', '1000')
                    worldScale = toonHead.getScale(render)
                    headPosNode = hidden.attachNewNode('headPos')
                    toonHead.reparentTo(headPosNode)
                    toonHead.setPos(0, 0, 0.2)
                    headPosNode.reparentTo(suitHeadNull)
                    headPosNode.setScale(render, worldScale)
                return track
            elif animName == 'squish':
                sound, lerpTime, node, origScale = extraArgs
                track = Sequence(
                    LerpScaleInterval(node, lerpTime, VBase3(2, 2, 0.025), blendType='easeInOut'),
                    Wait(1.0), Parallel(
                        Sequence(
                            Wait(0.4),
                            LerpScaleInterval(node, lerpTime, VBase3(1.4, 1.4, 1.4), blendType='easeInOut'),
                            LerpScaleInterval(node, lerpTime / 2.0, VBase3(0.8, 0.8, 0.8), blendType='easeInOut'),
                            LerpScaleInterval(node, lerpTime / 3.0, origScale, blendType='easeInOut')
                        ),
                        ActorInterval(self.suit, 'drop-react', startFrame=30), SoundInterval(sound)
                    )
                )
                return track
            elif animName == 'present-pie':
                x, y, z, h, pie, pieName, pieType, animPie, pingpongPie = extraArgs
                if self.suit.getBodyType() != 'c':
                    track = Sequence(Func(self.suit.setPosHpr, x, y, z, h, 0, 0),
                                     Func(pie.reparentTo, self.suit.rightHand),
                                     Func(pie.setPosHpr, 0, 0, 0, 0, 180, 0),
                                     Parallel(pie.scaleInterval(1, self.pieScale, startScale=MovieUtil.PNT3_NEARZERO),
                                              ActorInterval(self.suit, 'throw-object', startFrame=0, endFrame=40),
                                              animPie),
                                     Func(self.suit.pingpong, 'throw-object', fromFrame=40, toFrame=50), pingpongPie)
                else:
                    track = Sequence(Func(self.suit.setPosHpr, x, y, z, h, 0, 0),
                                     Func(pie.reparentTo, self.suit.rightHand),
                                     Func(pie.setPosHpr, 0, 0, 0, 0, 180, 0),
                                     Parallel(pie.scaleInterval(1, self.pieScale, startScale=MovieUtil.PNT3_NEARZERO),
                                              ActorInterval(self.suit, 'throw-paper', startFrame=0, endFrame=30),
                                              animPie),
                                     Func(self.suit.pingpong, 'throw-paper', fromFrame=30, toFrame=40), pingpongPie)
                return track
            elif animName == 'toss-pie':
                x, y, z, h, power, pie, pieName, pieType, animPie = extraArgs
                if not pie or not self.suit.rightHand:
                    return Sequence()
                if self.suit.getBodyType() != 'c':
                    toss = Track(
                        (0, Sequence(Func(self.suit.setPosHpr, x, y, z, h, 0, 0),
                                     Func(pie.reparentTo, self.suit.rightHand),
                                     Func(pie.setPosHpr, 0, 0, 0, 0, 180, 0),
                                     Parallel(ActorInterval(self.suit, 'throw-object', playRate=1.5, startFrame=50),
                                              animPie),
                                     Func(self.suit.loop, 'neutral'))), (16.0 / 24.0, Func(pie.detachNode)))
                else:
                    toss = Track((0, Sequence(Func(self.suit.setPosHpr, x, y, z, h, 0, 0),
                                              Func(pie.reparentTo, self.suit.rightHand),
                                              Func(pie.setPosHpr, 0, 0, 0, 0, 180, 0),
                                              Parallel(ActorInterval(self.suit, 'throw-paper', startFrame=40), animPie),
                                              Func(self.suit.loop, 'neutral'))),
                                 (16.0 / 24.0, Func(pie.detachNode)))
                return toss
            elif animName == 'stun':
                track = extraArgs[0]
                return Parallel(ActorInterval(self.suit, animName='slip-backward'), track)
            elif animName == 'feed-pet':
                if self.suit.getBodyType() == 'c':
                    return Sequence(ActorInterval(self.suit, 'throw-paper', playRate=1.0),
                                    Func(self.animFSM.request, 'neutral'))
                else:
                    return Sequence(ActorInterval(self.suit, 'throw-paper', playRate=1.2),
                                    Func(self.animFSM.request, 'neutral'))
            elif animName == 'golf-putt':
                self.suit.pose('golf-club-swing', 50)
            elif animName == 'golf-swing':
                self.suit.actorInterval('golf-club-swing', startFrame=65, playRate=5 * self.suit.getPlayRate()).start()

        if currentTransformation == ToontownGlobals.TransformationClassicChar:
            if animName == 'neutral':
                self.char.pose('neutral', int(self.getNumFrames('neutral') * self.randGen.random()))
                self.char.loop('neutral', restart=0)
                self.char.setPlayRate(self.char.getPlayRate(), 'neutral')
            elif animName == 'run':
                self.char.loop('run')
                self.char.setPlayRate(self.char.getPlayRate(), 'run')
            elif animName == 'walk':
                self.char.loop('walk')
                self.char.setPlayRate(self.char.getPlayRate(), 'run')
            elif animName == 'teleport':
                return Sequence(
                    LerpScaleInterval(self.charGeom, 0.25, scale + scale * 0.25),
                    LerpScaleInterval(self.charGeom, 0.75, 0.01)
                )
            elif animName == 'teleportIn':
                return Sequence(
                    LerpScaleInterval(self.charGeom, 0.75, startScale=0.01, scale=scale + scale * 0.25),
                    LerpScaleInterval(self.charGeom, 0.25, scale)
                )
            elif animName == 'died':
                return Sequence(
                    LerpScaleInterval(self.charGeom, 3.0, scale * 1.5),
                    LerpScaleInterval(self.charGeom, 0.5, 0.01)
                )

        if currentTransformation == ToontownGlobals.TransformationDoodle:
            if animName == 'neutral':
                self.pet.pose('neutral', int(self.getNumFrames('neutral') * self.randGen.random()))
                self.pet.loop('neutral', restart=0)
                self.pet.setPlayRate(self.pet.getPlayRate(), 'neutral')
            elif animName == 'run':
                self.pet.loop('run')
                self.pet.setPlayRate(self.pet.getPlayRate(), 'run')
            elif animName == 'walk':
                self.pet.loop('walk')
                self.pet.setPlayRate(self.pet.getPlayRate(), 'walk')
            elif animName == 'teleport':
                hole = self.getHoleActors()[0]
                hole.setBin('shadow', 0)
                hole.setDepthTest(0)
                hole.setDepthWrite(0)
                hole.reparentTo(self)
                pos = Point3(0, -1, 0)
                hole.setPos(self, pos)
                hole.hide()

                def cleanupHole(hole):
                    hole.setPos(0, 0, 0)
                    hole.detachNode()
                    hole.clearBin()
                    hole.clearDepthTest()
                    hole.clearDepthWrite()

                track = Sequence(Parallel(SoundInterval(loader.loadSfx('phase_5/audio/sfx/teleport_disappear.ogg')),
                                          Sequence(ActorInterval(self.pet, 'toDig'),
                                                   Parallel(ActorInterval(self.pet, 'dig'), Func(hole.show),
                                                            ActorInterval(hole, 'hole',
                                                                          startFrame=81, endFrame=71)),
                                                   ActorInterval(self.pet, 'disappear'),
                                                   ActorInterval(hole, 'hole', startFrame=71,
                                                                 endFrame=81), Func(cleanupHole, hole)),
                                          Sequence(Wait(1.0), Func(self.dropShadow.hide))))
                return track
            elif animName == 'teleportIn':
                self.petGeom.setScale(scale)
                hole = self.getHoleActors()[0]
                hole.setBin('shadow', 0)
                hole.setDepthTest(0)
                hole.setDepthWrite(0)
                hole.reparentTo(self)
                pos = Point3(0, -1, 0)
                hole.setPos(self, pos)

                def cleanupHole(hole):
                    hole.setPos(0, 0, 0)
                    hole.detachNode()
                    hole.clearBin()
                    hole.clearDepthTest()
                    hole.clearDepthWrite()

                track = Sequence(Parallel(SoundInterval(loader.loadSfx('phase_5/audio/sfx/teleport_reappear.ogg')),
                                          Sequence(ActorInterval(hole, 'hole', startFrame=81, endFrame=71),
                                                   ActorInterval(self.pet, 'reappear'),
                                                   ActorInterval(hole, 'hole', startFrame=71, endFrame=81),
                                                   Func(cleanupHole, hole), Func(self.pet.loop, 'neutral')),
                                          Sequence(Func(self.dropShadow.hide), Wait(1.0),
                                                   Func(self.tryShowDropShadow), Func(self.tryShowNametag))))
                return track
            elif animName == 'died':
                track = Sequence(Func(Emote.globalEmote.disableBody, self),
                                 Parallel(ActorInterval(self.pet, 'playDead'),
                                          SoundInterval(loader.loadSfx('phase_5/audio/sfx/play_dead.ogg'))),
                                 LerpScaleInterval(self.petGeom, 0.5, (0.01, 0.01, 0.01)))
                return track
            elif animName == 'jump-idle':
                sound = loader.loadSfx('phase_5/audio/sfx/jump.ogg')
                track = Parallel()
                track.append(Sequence(ActorInterval(self.pet, 'jump', playRate=1.1), Func(self.pet.loop, 'neutral')))
                track.append(Sequence(Wait(0.36), ProjectileInterval(self.pet, startPos=self.pet.getPos(),
                                                                     endPos=self.pet.getPos(), duration=1.0,
                                                                     gravityMult=0.5)))
                track.append(SoundInterval(sound))
                track.start()

        if currentTransformation == ToontownGlobals.TransformationGoon:
            if animName == 'neutral':
                self.goon.stop()
            elif animName == 'run' or animName == 'walk':
                self.goon.loop('walk')
                self.goon.setPlayRate(self.goon.getPlayRate(), 'walk')
            elif animName == 'teleport':
                return Sequence(
                    LerpScaleInterval(self.goonGeom, 0.25, (scale * 1.25)),
                    LerpScaleInterval(self.goonGeom, 0.75, 0.01)
                )
            elif animName == 'teleportIn':
                return Sequence(
                    LerpScaleInterval(self.goonGeom, 0.75, startScale=0.01, scale=(scale * 1.25)),
                    LerpScaleInterval(self.goonGeom, 0.25, scale)
                )
            elif animName == 'died':
                return Sequence(
                    ActorInterval(self.goon, 'collapse'), Wait(0.5),
                    LerpScaleInterval(self.goonGeom, 0.5, 0.01)
                )

        if currentTransformation == ToontownGlobals.TransformationProp:
            if animName == 'teleport':
                return Sequence(
                    LerpScaleInterval(self.prop, 0.25, (scale * 1.25)),
                    LerpScaleInterval(self.prop, 0.75, 0.01)
                )
            elif animName == 'teleportIn':
                return Sequence(
                    LerpScaleInterval(self.prop, 0.75, startScale=0.01, scale=(scale * 1.25)),
                    LerpScaleInterval(self.prop, 0.25, scale)
                )
            elif animName == 'died':
                return Sequence(
                    LerpScaleInterval(self.prop, 3.0, (scale * 1.5)),
                    LerpScaleInterval(self.prop, 0.5, 0.01)
                )

        if currentTransformation == ToontownGlobals.TransformationBoss:
            if animName == 'teleport':
                return Sequence(
                    LerpScaleInterval(self.bossGeom, 0.25, (scale * 1.25)),
                    LerpScaleInterval(self.bossGeom, 0.75, 0.01)
                )
            elif animName == 'teleportIn':
                self.boss.getGeomNode().show()
                return Sequence(
                    LerpScaleInterval(self.bossGeom, 0.75, startScale=0.01, scale=(scale * 1.25)),
                    LerpScaleInterval(self.bossGeom, 0.25, scale)
                )
            elif animName == 'died':
                spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Cog_Death.ogg')
                deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
                deathSoundTrack = Sequence(Wait(0.6),
                                           SoundInterval(spinningSound, duration=1.2, startTime=1.5, volume=0.2),
                                           SoundInterval(spinningSound, duration=3.0, startTime=0.6, volume=0.8),
                                           SoundInterval(deathSound, volume=0.32))
                BattleParticles.loadParticles()
                smallGears = BattleParticles.createParticleEffect(file='gearExplosionSmall')
                singleGear = BattleParticles.createParticleEffect('GearExplosion', numParticles=1)
                smallGearExplosion = BattleParticles.createParticleEffect('GearExplosion', numParticles=10)
                bigGearExplosion = BattleParticles.createParticleEffect('BigGearExplosion', numParticles=30)
                smallGears.setDepthWrite(False)
                singleGear.setDepthWrite(False)
                smallGearExplosion.setDepthWrite(False)
                bigGearExplosion.setDepthWrite(False)
                explosionTrack = Sequence()
                explosionTrack.append(Wait(5.4))
                explosionTrack.append(MovieUtil.createKapowExplosionTrack(self, scale))
                gears1Track = Sequence(Wait(2.0),
                                       ParticleInterval(smallGears, self, worldRelative=0, duration=4.3, cleanup=True),
                                       name='gears1Track')
                gears2MTrack = Track((0.0, explosionTrack),
                                     (0.7, ParticleInterval(singleGear, self, worldRelative=0, duration=5.7,
                                                            cleanup=True)),
                                     (5.2, ParticleInterval(smallGearExplosion, self, worldRelative=0, duration=1.2,
                                                            cleanup=True)),
                                     (5.4, ParticleInterval(bigGearExplosion, self, worldRelative=0, duration=1.0,
                                                            cleanup=True)), name='gears2MTrack')
                ival = Sequence(Parallel(Sequence(ActorInterval(self.boss, 'death', playRate=1.125),
                                         Func(self.boss.getGeomNode().hide)), deathSoundTrack, gears1Track,
                                         gears2MTrack))
                if base.cr.newsManager.isHolidayRunning(ToontownGlobals.APRIL_FOOLS_COSTUMES) and \
                        self.getTransformationsIndex(ToontownGlobals.TransformationBoss) == 2:
                    ival.append(Func(self.boss.loop, 'Ff_neutral'))
                else:
                    ival.append(Func(self.boss.loop, 'Bb_neutral'))
                return ival
            # elif animName == 'jump-idle':
            #    track = self.boss.getAnim('areaAttack')
            #    track.start()

        if currentTransformation == ToontownGlobals.TransformationFish:
            if animName == 'teleport':
                return Sequence(
                    LerpScaleInterval(self.fishGeom, 0.25, (scale * 1.25)),
                    LerpScaleInterval(self.fishGeom, 0.75, (0.01, 0.01, 0.01))
                )
            elif animName == 'teleportIn':
                return Sequence(
                    LerpScaleInterval(self.fishGeom, 0.75, startScale=0.01, scale=(scale * 1.25)),
                    LerpScaleInterval(self.fishGeom, 0.25, scale)
                )
            elif animName == 'died':
                return Sequence(
                    LerpScaleInterval(self.fishGeom, 3.0, (scale * 1.5)),
                    LerpScaleInterval(self.fishGeom, 0.5, 0.01)
                )

        if currentTransformation == ToontownGlobals.TransformationButterfly:
            if animName == 'teleport':
                return Sequence(
                    LerpScaleInterval(self.butterfly, 0.25, (scale * 1.25)),
                    LerpScaleInterval(self.butterfly, 0.75, 0.01)
                )
            elif animName == 'teleportIn':
                return Sequence(
                    LerpScaleInterval(self.butterfly, 0.75, startScale=0.01, scale=(scale * 1.25)),
                    LerpScaleInterval(self.butterfly, 0.25, scale)
                )
            elif animName == 'died':
                return Sequence(
                    LerpScaleInterval(self.butterfly, 3.0, (scale * 1.5)),
                    LerpScaleInterval(self.butterfly, 0.5, 0.01)
                )

        if currentTransformation == ToontownGlobals.TransformationMisc:
            transformationIndex -= 1
            if transformationIndex == ToontownGlobals.TransformationMiscStatue:
                if animName == 'neutral':
                    self.misc.stop()
                elif animName == 'run' or animName == 'walk':
                    self.misc.loop('walk')
                    self.misc.setPlayRate(self.misc.getPlayRate(), 'walk')
                elif animName == 'teleport':
                    return Sequence(
                        LerpScaleInterval(self.misc, 0.25, (scale * 1.25)),
                        LerpScaleInterval(self.misc, 0.75, 0.01)
                    )
                elif animName == 'teleportIn':
                    return Sequence(
                        LerpScaleInterval(self.misc, 0.75, startScale=0.01, scale=(scale * 1.25)),
                        LerpScaleInterval(self.misc, 0.25, scale)
                    )
                elif animName == 'died':
                    return Sequence(
                        LerpScaleInterval(self.misc, 3.0, (scale * 1.5)),
                        LerpScaleInterval(self.misc, 0.5, 0.01)
                    )
                elif animName == 'jump-idle':
                    self.misc.loop('jump')
                elif animName == 'victory':
                    sfx = loader.loadSfx('phase_14.5/audio/sfx/cj-statue-dance.ogg')
                    base.playSfx(sfx, node=self)
                    self.misc.setPlayRate(0.6, 'victory')
                    self.misc.loop('victory')
            elif transformationIndex == ToontownGlobals.TransformationMiscPanda:
                if animName == 'neutral':
                    self.misc.stop()
                elif animName == 'run' or animName == 'walk':
                    self.misc.loop('walk')
                    self.misc.setPlayRate(self.misc.getPlayRate(), 'walk')
                elif animName == 'teleport':
                    return Sequence(
                        LerpScaleInterval(self.misc, 0.25, (scale * 1.25)),
                        LerpScaleInterval(self.misc, 0.75, 0.01)
                    )
                elif animName == 'teleportIn':
                    return Sequence(
                        LerpScaleInterval(self.misc, 0.75, startScale=0.01, scale=(scale * 1.25)),
                        LerpScaleInterval(self.misc, 0.25, scale)
                    )
                elif animName == 'died':
                    return Sequence(
                        LerpScaleInterval(self.misc, 3.0, (scale * 1.5)),
                        LerpScaleInterval(self.misc, 0.5, 0.01)
                    )
            elif transformationIndex in (ToontownGlobals.TransformationMiscChaser, ToontownGlobals.TransformationMiscMickey):
                self.misc.loop(animName)
            elif transformationIndex == ToontownGlobals.TransformationMiscCheese:
                if animName == 'neutral':
                    self.misc.pose('neutral', int(self.getNumFrames('neutral') * self.randGen.random()))
                    self.misc.loop('neutral', restart = 0)
                    self.misc.setPlayRate(self.misc.getPlayRate(), 'neutral')
                elif animName == 'run' or animName == 'walk':
                    self.misc.loop('walk')
                    self.misc.setPlayRate(self.misc.getPlayRate(), 'walk')
                elif animName == 'teleport':
                    return Sequence(
                        LerpScaleInterval(self.misc, 0.25, (scale * 1.25)),
                        LerpScaleInterval(self.misc, 0.75, 0.01)
                    )
                elif animName == 'teleportIn':
                    return Sequence(
                        LerpScaleInterval(self.misc, 0.75, startScale=0.01, scale=(scale * 1.25)),
                        LerpScaleInterval(self.misc, 0.25, scale)
                    )
                elif animName == 'died':
                    return Sequence(
                        LerpScaleInterval(self.misc, 3.0, (scale * 1.5)),
                        LerpScaleInterval(self.misc, 0.5, 0.01)
                    )

        if currentTransformation == ToontownGlobals.TransformationStreet:
            if animName == 'teleport':
                return Sequence(
                    LerpScaleInterval(self.streetGeom, 0.25, (scale * 1.25)),
                    LerpScaleInterval(self.streetGeom, 0.75, 0.01)
                )
            elif animName == 'teleportIn':
                return Sequence(
                    LerpScaleInterval(self.streetGeom, 0.75, startScale=0.01, scale=(scale * 1.25)),
                    LerpScaleInterval(self.streetGeom, 0.25, scale)
                )
            elif animName == 'died':
                return Sequence(
                    LerpScaleInterval(self.streetGeom, 3.0, (scale * 1.5)),
                    LerpScaleInterval(self.streetGeom, 0.5, 0.01)
                )
            elif animName == 'jump':
                self.street.play('jump')
            elif animName == 'jump-idle':
                self.street.play('jump')

        return Sequence(Wait(1.0))

    def stopTransformationAnim(self, animName):
        if not animName:
            return

        currentTransformation = self.getActiveTransformationIndex()

        if currentTransformation == ToontownGlobals.TransformationCog:
            if animName in ['jump' 'jump-squat', 'jump-land']:
                if hasattr(self, 'jump') and self.jump:
                    self.jump.finish()
                    self.jump = None
            elif animName in ['openBook', 'readBook', 'closeBook']:
                if self.cogBook:
                    self.cogBook.removeNode()
                    self.cogBook = None
            elif animName == 'died':
                self.suit.getGeomNode().unstash()
                self.takeOffTransformation()
        if currentTransformation == ToontownGlobals.TransformationCog:
            if animName in ['jump' 'jump-squat', 'jump-land']:
                if hasattr(self, 'jump') and self.jump:
                    self.jump.finish()
                    self.jump = None

    def isCog(self):
        # Redefining this here so NPCs can use it too
        if not self.getTransformationsIndex(ToontownGlobals.TransformationCog):
            return 0
        else:
            return 1

    def getSuitTeleport(self, moveIn, startPos=None):
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('teleportOut')
        else:
            trackName = 'teleportOut'
        if not startPos:
            pos = Point3(self.getPos())
        else:
            pos = startPos
        skyPos = Point3(pos)
        if not startPos:
            if moveIn:
                skyPos.setZ(pos.getZ() + SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)
            else:
                skyPos.setZ(pos.getZ() + SuitTimings.toSky * ToontownGlobals.SuitWalkSpeed)
        else:
            if moveIn:
                skyPos.setZ(pos[2] + SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)
            else:
                skyPos.setZ(pos[2] + SuitTimings.toSky * ToontownGlobals.SuitWalkSpeed)
        groundF = 28
        dur = self.suit.getDuration('landing')
        fr = self.suit.getFrameRate('landing')
        animTimeInAir = groundF / fr
        impactLength = dur - animTimeInAir
        timeTillLanding = SuitTimings.fromSky - impactLength
        waitTime = timeTillLanding - animTimeInAir
        prop = BattleProps.globalPropPool.getProp('propeller')
        prop.setPlayRate(1.5, 'propeller')
        if self.disguiseType != 5 and self.isCog():
            if self.suit.getBodyType() == 'a':
                head = self.find('**/to_head')
            else:
                head = self.find('**/joint_head')
        else:
            head = self.getHeadParts()[0]
        prop.reparentTo(head)
        propInSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg')
        propOutSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_out.ogg')
        propDur = prop.getDuration('propeller')
        lastSpinFrame = 8
        fr = prop.getFrameRate('propeller')
        spinTime = lastSpinFrame / fr
        openTime = (lastSpinFrame + 1) / fr
        if moveIn:
            lerpPosTrack = Sequence(self.posInterval(timeTillLanding, pos, startPos=skyPos), Wait(impactLength))
            shadowScale = self.suit.dropShadow.getScale()
            shadowTrack = Sequence(Func(self.suit.dropShadow.reparentTo, render), Func(self.suit.dropShadow.setPos,
                                                                                       pos),
                                   self.suit.dropShadow.scaleInterval(timeTillLanding, self.suit.scale,
                                                                      startScale=Vec3(0.01, 0.01, 1.0)),
                                   Func(self.suit.dropShadow.reparentTo, self.suit.getShadowJoint()),
                                   Func(self.suit.dropShadow.setPos, 0, 0, 0),
                                   Func(self.suit.dropShadow.setScale, shadowScale),
                                   Func(self.suit.initializeDropShadow))
            fadeInTrack = Sequence(Func(self.suitGeom.setTransparency, 1),
                                   self.suitGeom.colorScaleInterval(1, colorScale=VBase4(1, 1, 1, 1),
                                                                    startColorScale=VBase4(1, 1, 1, 0)),
                                   Func(self.suitGeom.clearColorScale), Func(self.suitGeom.clearTransparency))
            animTrack = Sequence(Func(self.suit.pose, 'landing', 0), Wait(waitTime),
                                 ActorInterval(self.suit, 'landing', duration=dur))

            animTrack.append(Func(self.loop, 'neutral'))
            propTrack = Parallel(SoundInterval(propInSound, duration=waitTime + dur, node=self), Sequence(
                Func(prop.loop, 'propeller', fromFrame=5, toFrame=10),
                Wait(waitTime),
                ActorInterval(prop, 'propeller', duration=propDur - openTime, startTime=openTime),
                Func(prop.cleanup), Func(prop.removeNode)))
            return Parallel(Func(self.tryShowNametag), lerpPosTrack, shadowTrack, fadeInTrack, animTrack, propTrack,
                            name=trackName)
        else:
            lerpPosTrack = Sequence(Wait(impactLength), LerpPosInterval(self, timeTillLanding, skyPos, startPos=pos))
            shadowTrack = Sequence(Func(self.suit.dropShadow.reparentTo, render), Func(self.suit.dropShadow.setPos,
                                                                                       pos),
                                   self.suit.dropShadow.scaleInterval(timeTillLanding, Vec3(0.01, 0.01, 1.0),
                                                                      startScale=self.suit.scale),
                                   Func(self.suit.dropShadow.reparentTo, self.suit.getShadowJoint()),
                                   Func(self.suit.dropShadow.setPos, 0, 0, 0))
            fadeOutTrack = Sequence(Func(self.suitGeom.setTransparency, 1),
                                    self.suitGeom.colorScaleInterval(1, colorScale=VBase4(1, 1, 1, 0),
                                                                     startColorScale=VBase4(1, 1, 1, 1)),
                                    Func(self.suitGeom.clearColorScale), Func(self.suitGeom.clearTransparency),
                                    Func(self.reparentTo, hidden))
            actInt = ActorInterval(self.suit, 'landing', loop=0, startTime=dur, endTime=0.0)
            prop.hide()
            propTrack = Parallel(SoundInterval(propOutSound, duration=waitTime + dur, node=self),
                                 Sequence(Func(prop.show),
                                          ActorInterval(prop, 'propeller', startFrame=88, endFrame=5, playRate=1.5),
                                          Func(prop.loop, 'propeller', fromFrame=5, toFrame=10),
                                          Wait(4.1),
                                          Func(prop.cleanup), Func(prop.removeNode)))
            return Parallel(ParallelEndTogether(lerpPosTrack, shadowTrack, fadeOutTrack), actInt, propTrack,
                            name=trackName)

    def setAnimalSound(self, animalSound):
        self.animalSound = animalSound

    def getAnimalSound(self):
        return self.animalSound

    def setTPose(self):
        self.tpose = not self.tpose

        self.stop()
        self.unloadAnims()
        activeTransformation = self.getActiveTransformationIndex()
        if (self.getTransformed() or self.getTPose()) and activeTransformation != ToontownGlobals.TransformationProp:
            transformationActor = self.getActiveTransformation()
            transformationIndex = self.getTransformationsIndex(ToontownGlobals.TransformationFish)
            if activeTransformation == ToontownGlobals.TransformationFish and transformationIndex == 10:
                fishInfo = ToontownGlobals.TransformationFishExtra.get(transformationIndex)
                transformationActor.pose(fishInfo[ToontownGlobals.TransformationExtraAnimation], frame=40)
            else:
                transformationActor.stop()
                transformationActor.unloadAnims()

    def getTPose(self):
        return self.tpose

    def setEyes(self, eyes):
        if self._ToonHead__eyelashOpen:
            self._ToonHead__eyelashOpen.unstash()
        if self._ToonHead__eyelashClosed:
            self._ToonHead__eyelashClosed.unstash()

        if eyes == 0:
            self.stashEyes(False)
            Sequence(Func(self.blinkEyes), Func(self.normalEyes), Func(self.startBlink)).start()
        elif eyes == 1:
            self.stashEyes(False)
            Sequence(Func(self.blinkEyes), Func(self.sadEyes), Func(self.startBlink)).start()
        elif eyes == 2:
            self.stashEyes(False)
            Sequence(Func(self.blinkEyes), Func(self.angryEyes), Func(self.startBlink)).start()
        elif eyes == 3:
            self.stashEyes(False)
            Sequence(Func(self.blinkEyes), Func(self.surprisedEyes), Func(self.stopBlink)).start()
        elif eyes == 4:
            self.stashEyes(True)
            Sequence(Func(self.blinkEyes), Func(self.cashedEyes), Func(self.stopBlink)).start()

        elif eyes == 5:
            self.stashEyes(True)
            Sequence(Func(self.blinkEyes), Func(self.crossedEyes), Func(self.stopBlink)).start()

        elif eyes == 6:
            self.stashEyes(True)
            Sequence(Func(self.blinkEyes), Func(self.dozedEyes), Func(self.stopBlink)).start()

        elif eyes == 7:
            self.stashEyes(True)
            Sequence(Func(self.blinkEyes), Func(self.glaredEyes), Func(self.stopBlink)).start()

        elif eyes == 8:
            self.stashEyes(True)
            Sequence(Func(self.blinkEyes), Func(self.squintedEyes), Func(self.stopBlink)).start()

    def getPieModel(self):
        from toontown.toonbase import ToontownBattleGlobals
        from toontown.battle import BattleProps
        if self.pieModel != None and self.__pieModelType != self.pieType:
            self.pieModel.detachNode()
            self.pieModel = None
        if self.pieModel == None:
            self.__pieModelType = self.pieType
            pieName = ToontownBattleGlobals.pieNames[self.pieType]
            self.pieModel = BattleProps.globalPropPool.getProp(pieName)
            if self.pieType == 9:
                self.pieScale = 8
            else:
                self.pieScale = self.pieModel.getScale()
        return self.pieModel

    def getPresentPieInterval(self, x, y, z, h, p, r):
        from toontown.toonbase import ToontownBattleGlobals
        from toontown.battle import BattleProps
        from toontown.battle import MovieUtil
        pie = self.getPieModel()
        pieName = ToontownBattleGlobals.pieNames[self.pieType]
        pieType = BattleProps.globalPropPool.getPropType(pieName)
        animPie = Sequence()
        pingpongPie = Sequence()
        if pieType == 'actor':
            animPie = ActorInterval(pie, pieName, startFrame=0, endFrame=31)
            pingpongPie = Func(pie.pingpong, pieName, fromFrame=32, toFrame=47)
        if self.getTransformed() or self.getTPose():
            track = self.playTransformationAnim('present-pie', [x, y, z, h, pie, pieName, pieType, animPie,
                                                                pingpongPie])
        else:
            if self.playingAnim != 'neutral':
                track = Sequence(
                        Func(pie.reparentTo, self.rightHand),
                        Func(pie.setPosHpr, 0, 0, 0, 0, 0, 0),
                        Parallel(pie.scaleInterval(1, self.pieScale, startScale=MovieUtil.PNT3_NEARZERO),
                                 ActorInterval(self, 'throw', startFrame=0, endFrame=31, partName = 'torso'), animPie),
                        Func(self.pingpong, 'throw', fromFrame=32, toFrame=47, partName = 'torso'), pingpongPie)
            else:
                track = Sequence(
                        Func(pie.reparentTo, self.rightHand),
                        Func(pie.setPosHpr, 0, 0, 0, 0, 0, 0),
                        Parallel(pie.scaleInterval(1, self.pieScale, startScale=MovieUtil.PNT3_NEARZERO),
                              ActorInterval(self, 'throw', startFrame=0, endFrame=31), animPie),
                        Func(self.pingpong, 'throw', fromFrame=32, toFrame=47), pingpongPie)
        return track

    def getTossPieInterval(self, x, y, z, h, p, r, power, beginFlyIval = Sequence()):
        from toontown.toonbase import ToontownBattleGlobals
        from toontown.battle import BattleProps
        pie = self.getPieModel()
        flyPie = pie.copyTo(NodePath('a'))
        pieName = ToontownBattleGlobals.pieNames[self.pieType]
        pieType = BattleProps.globalPropPool.getPropType(pieName)
        animPie = Sequence()
        if pieType == 'actor':
            animPie = ActorInterval(pie, pieName, startFrame=62)
        sound = loader.loadSfx('phase_3.5/audio/sfx/AA_pie_throw_only.ogg')
        t = power / 100.0
        dist = 100 - 70 * t
        time = 1 + 0.5 * t
        proj = ProjectileInterval(None, startPos=Point3(0, 0, 0), endPos=Point3(0, dist, 0), duration=time)
        relVel = proj.startVel

        def getVelocity(toon = self, relVel = relVel):
            return render.getRelativeVector(toon, relVel)

        def getAnim(toon = self):
            toon.loop(toon.playingAnim)

        if self.getTransformed() or self.getTPose():
            toss = self.playTransformationAnim('toss-pie', [x, y, z, h, power, pie, pieName, pieType, animPie])
        else:
            if self.playingAnim != 'neutral':
                toss = Track((0, Sequence(Func(pie.reparentTo, self.rightHand),
                                          Func(pie.setPosHpr, 0, 0, 0, 0, 0, 0),
                                          Parallel(ActorInterval(self, 'throw', startFrame=62, partName = 'torso'), animPie),
                                          Func(getAnim))), (.14, Func(pie.detachNode)))
            else:
                toss = Track((0, Sequence(Func(pie.reparentTo, self.rightHand),
                                          Func(pie.setPosHpr, 0, 0, 0, 0, 0, 0),
                                          Parallel(ActorInterval(self, 'throw', startFrame=62), animPie),
                                          Func(getAnim))), (.14, Func(pie.detachNode)))
        fly = Track((.12, SoundInterval(sound, node=self)),
                    (.14, Sequence(Func(flyPie.reparentTo, render),
                                           Func(flyPie.setScale, self.pieScale),
                                           Func(flyPie.setPosHpr, self, 0.52, 0.97, 2.24, 89.42, -10.56, 87.94),
                                           beginFlyIval, ProjectileInterval(flyPie, startVel=getVelocity, duration=3),
                                           Func(flyPie.detachNode))))
        return (toss, fly, flyPie)

    def getPieSplatInterval(self, x, y, z, pieCode):
        from toontown.toonbase import ToontownBattleGlobals
        from toontown.battle import BattleProps
        pieName = ToontownBattleGlobals.pieNames[self.pieType]
        splatName = f'splat-{pieName}'
        if pieName == 'lawbook' or pieName == 'pink-slip':
            splatName = 'dust'
        splat = BattleProps.globalPropPool.getProp(splatName)
        splat.setBillboardPointWorld(2)
        color = ToontownGlobals.PieCodeColors.get(pieCode)
        if color:
            splat.setColor(*color)
        vol = 1.0
        if pieName == 'lawbook' or pieName == 'pink-slip':
            sound = loader.loadSfx('phase_11/audio/sfx/LB_evidence_miss.ogg')
            vol = 0.25
        else:
            sound = loader.loadSfx('phase_4/audio/sfx/AA_wholepie_only.ogg')
        ival = Parallel(Func(splat.reparentTo, render), Func(splat.setPos, x, y, z), SoundInterval(sound, node=splat,
                                                                                                   volume=vol),
                        Sequence(ActorInterval(splat, splatName), Func(splat.detachNode)))
        return ival

    def cleanupPieModel(self):
        if self.pieModel != None:
            self.pieModel.detachNode()
            self.pieModel = None
        return

    def getFeatherModel(self):
        from toontown.toonbase import ToontownBattleGlobals
        from toontown.battle import BattleProps
        # Just in-case, cleanup the feather model.
        self.cleanupFeatherModel()

        self.featherModel = BattleProps.globalPropPool.getProp('feather')
        self.featherScale = self.featherModel.getScale()

        return self.featherModel

    def cleanupFeatherModel(self):
        if self.featherModel != None:
            self.featherModel.detachNode()
            self.featherModel = None

    def getFeatherInterval(self, featherBeginIval = None, callback = None):
        # TODO:
        # - interval isn't the most polished
        # - i don't like how weird the legs look when moving around
        if not self.featherModel:
            self.getFeatherModel()

        feather = self.featherModel
        feather2 = MovieUtil.copyProp(feather)
        feathers = [feather, feather2]
        hands = self.getRightHands()

        sfx = base.loader.loadSfx('phase_5/audio/sfx/AA_heal_tickle.ogg')

        track = Sequence()
        if featherBeginIval:
            track.append(featherBeginIval)

        tFeatherScaleUp = 0.1
        dFeatherScaleUp = 0.25
        tFeatherScaleDown = 2.75
        dFeatherScaleDown = 0.25
        featherTrack = Parallel(MovieUtil.getActorIntervals(feathers, 'feather'), 
                                Sequence(Wait(tFeatherScaleUp), 
                                         Func(MovieUtil.showProps, feathers, hands),  
                                         Func(self.pose, 'tickle', 63),
                                         Func(self.update, 0),
                                         MovieUtil.getScaleIntervals(feathers, dFeatherScaleUp, MovieUtil.PNT3_NEARZERO, self.featherScale)), 
                                Sequence(Wait(self.getDuration('tickle') - tFeatherScaleDown), 
                                         MovieUtil.getScaleIntervals(feathers, dFeatherScaleDown, None, MovieUtil.PNT3_NEARZERO))
                                )
        mtrack = Parallel(featherTrack,
                          ActorInterval(self, 'tickle', startTime = 2.0),
                          Sequence(Wait(0.25),
                                   SoundInterval(sfx, duration = 1, node = feather)),
                          )
        track.append(mtrack)

        def removeFeathers(toon = self, feathers = None):
            if feathers is None:
                feathers = feathers
            MovieUtil.removeProps(feathers)
            toon.featherModel = None

        track.append(Func(removeFeathers))

        if callback:
            track.append(Func(callback))

        return track

    def getFeedPetIval(self):
        if self.getTransformed() or self.getTPose():
            return self.playTransformationAnim('feed-pet')
        else:
            return Sequence(ActorInterval(self, 'feedPet'), Func(self.animFSM.request, 'neutral'))

    def getScratchPetIval(self):
        return Sequence(ActorInterval(self, 'pet-start'), ActorInterval(self, 'pet-loop'),
                        ActorInterval(self, 'pet-end'))

    def getCallPetIval(self):
        return ActorInterval(self, 'callPet')

    def enterGolfPuttLoop(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.loop('loop-putt')
        if self.getTransformed() or self.getTPose():
            self.playTransformationAnim('golf-putt')

    def exitGolfPuttLoop(self):
        self.stop()

    def enterGolfRotateLeft(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.loop('rotateL-putt')

    def exitGolfRotateLeft(self):
        self.stop()

    def enterGolfRotateRight(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.loop('rotateR-putt')

    def exitGolfRotateRight(self):
        self.stop()

    def enterGolfPuttSwing(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.loop('swing-putt')
        if self.getTransformed() or self.getTPose():
            self.playTransformationAnim('golf-swing', [animMultiplier])

    def exitGolfPuttSwing(self):
        self.stop()

    def enterGolfGoodPutt(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.loop('good-putt', restart=0)

    def exitGolfGoodPutt(self):
        self.stop()

    def enterGolfBadPutt(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.loop('badloop-putt', restart=0)

    def exitGolfBadPutt(self):
        self.stop()

    def enterFlattened(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        Emote.globalEmote.disableAll(self)
        sound = loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg')
        lerpTime = 0.1
        node = self.getGeomNode().getChild(0)
        self.origScale = node.getScale()
        self.track = Sequence(LerpScaleInterval(node, lerpTime, VBase3(2, 2, 0.025), blendType='easeInOut'))
        self.track.start(ts)
        self.setActiveShadow(1)

    def exitFlattened(self):
        self.playingAnim = 'neutral'
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        node = self.getGeomNode().getChild(0)
        node.setScale(self.origScale)
        Emote.globalEmote.releaseAll(self)
        return

    def enterCogThiefRunning(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = (('neutral', 1.0),
         ('run', 1.0),
         ('run', 1.0),
         ('run', -1.0),
         ('run', 1.0),
         ('run', 1.0))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        self.setActiveShadow(1)
        return

    def exitCogThiefRunning(self):
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()
        return

    def enterScientistJealous(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.loop('scientistJealous')
        if hasattr(self, 'showScientistProp'):
            self.showScientistProp()

    def exitScientistJealous(self):
        self.stop()

    def enterScientistEmcee(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.loop('scientistEmcee')

    def exitScientistEmcee(self):
        self.stop()

    def enterScientistWork(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.loop('scientistWork')

    def exitScientistWork(self):
        self.stop()

    def enterScientistLessWork(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.loop('scientistWork', fromFrame=319, toFrame=619)

    def exitScientistLessWork(self):
        self.stop()

    def enterScientistPlay(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.loop('scientistGame')
        if hasattr(self, 'scientistPlay'):
            self.scientistPlay()

    def exitScientistPlay(self):
        self.stop()

    def getDustCloud(self, delay=0.5, color=None, scale=0.4):
        dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)

        dustCloud.setBillboardAxis(2.0)
        dustCloud.setZ(3)
        dustCloud.setScale(scale)
        dustCloud.createTrack()
        sequence = Sequence(Wait(delay), Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy),
                            name='dustCloudIval')

        if color is not None and hasattr(self, 'laffMeter'):
            self.laffMeter.color = color
            sequence.append(Func(self.laffMeter.adjustFace, self.hp, self.maxHp))

        return sequence

    def getPortalOutTrack(self, autoFinishTrack = 1):
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('portalOut')
        else:
            trackName = 'portalOut'
        geom = base.cr.playGame.getPlace().loader.geom
        portal = geom.find('**/portalNode')
        if not portal:
            portal = geom.attachNewNode('dummyPortalNode')
            portal.setPos(self.getPos())
        if self.isLocal():
            camera.wrtReparentTo(render)
        actor = self.getActiveTransformation()
        seq = Sequence(
            Func(actor.loop, 'run'), Func(self.headsUp, portal),
            Parallel(
                self.__doToonGhostColorScale(VBase4(1, 1, 1, 0), 2.0, keepDefault=1),
                LerpPosInterval(self, 2.0, (portal.getX(geom), portal.getY(geom), portal.getZ(geom)))
            ),
            Func(self.nametag3d.hide)
        )
        if portal.getName() == 'dummyPortalNode':
            seq.append(Func(portal.removeNode))
        track = Parallel(seq, name=trackName, autoFinish=autoFinishTrack)
        return track

    def enterPortalOut(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        name = self.name
        if hasattr(self, 'doId'):
            name += '-' + str(self.doId)
        self.notify.debug('enterPortalOut %s' % name)
        if self.ghostMode or self.getTransformationsIndex(ToontownGlobals.TransformationCog):
            if callback:
                callback(*extraArgs)
            return
        self.playingAnim = 'portal'
        Emote.globalEmote.disableAll(self, 'enterPortalOut')
        if self.isLocal():
            autoFinishTrack = 0
        else:
            autoFinishTrack = 1
        self.track = self.getPortalOutTrack(autoFinishTrack)
        self.track.setDoneEvent(self.track.getName())
        self.acceptOnce(self.track.getName(), self.finishPortalOut, [callback, extraArgs])
        self.track.start(ts)
        self.setActiveShadow(0)

    def finishPortalOut(self, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        name = self.name
        if hasattr(self, 'doId'):
            name += '-' + str(self.doId)
        self.notify.debug('finishPortalOut %s' % name)
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if hasattr(self, 'animFSM'):
            self.animFSM.request('PortaledOut')
        if callback:
            callback(*extraArgs)
        return

    def exitPortalOut(self):
        name = self.name
        if hasattr(self, 'doId'):
            name += '-' + str(self.doId)
        self.notify.debug('exitPortalOut %s' % name)
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            self.track = None
        Emote.globalEmote.releaseAll(self, 'exitPortalOut')
        if self and not self.isEmpty():
            self.show()
        return

    def enterPortaledOut(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.setActiveShadow(0)

    def exitPortaledOut(self):
        pass

    def getPortalInTrack(self):
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('portalIn')
        else:
            trackName = 'portalIn'
        geom = base.cr.playGame.getPlace().loader.geom
        portal = geom.find('**/portalNode')
        if not portal:
            portal = geom.attachNewNode('dummyPortalNode')
            portal.setPos(self.getPos())
        if self.isLocal():
            camera.reparentTo(render)
            base.localAvatar.deactivateCamera()
            camera.setPosHpr(portal, 25, 25, 5, -10, 0, 0)
            camera.headsUp(portal)
        actor = self.getActiveTransformation()
        seq = Sequence(
            Func(actor.tryShowGeom), Func(self.tryShowNametag), Func(self.reparentTo, portal),
            Func(self.setPos, 0, 0, 0), Func(actor.loop, 'run'), Func(self.headsUp, 10, 10, 0),
            Parallel(
                self.__doToonGhostColorScale(VBase4(1, 1, 1, 1), 3.0, keepDefault=1),
                LerpPosInterval(self, 3.0, (10, 10, 0))
            ),
            Func(self.wrtReparentTo, render)
        )
        if portal.getName() == 'dummyPortalNode':
            seq.append(Func(portal.removeNode))
        return Parallel(seq, name=trackName)

    def enterPortalIn(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        if self.ghostMode or self.getTransformationsIndex(ToontownGlobals.TransformationCog):
            if callback:
                callback(*extraArgs)
            return
        self.show()
        self.playingAnim = 'portal'
        Emote.globalEmote.disableAll(self, 'enterPortalIn')
        self.getGeomNode().hide()
        self.nametag3d.hide()
        self.track = self.getPortalInTrack()
        if callback:
            self.track.setDoneEvent(self.track.getName())
            self.acceptOnce(self.track.getName(), callback, extraArgs)
        self.track.start(ts)
        self.setActiveShadow(0)

    def exitPortalIn(self):
        self.playingAnim = None
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if not self.getTransformed():
            self.tryShowGeom()
            self.tryShowNametag()
        Emote.globalEmote.releaseAll(self, 'exitPortalIn')
        return

    def enterPeriscope(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        anim = 'periscope'
        self.loop(anim)
        self.setPlayRate(animMultiplier, anim)

    def exitPeriscope(self):
        self.stop()


loadModels()
compileGlobalAnimList()
