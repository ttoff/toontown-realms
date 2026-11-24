from direct.interval.IntervalGlobal import *
from .BattleBase import *
from .BattleProps import *
from .BattleSounds import *
from toontown.toon.ToonDNA import *
from toontown.suit.SuitDNA import *
from . import MovieUtil
from . import MovieCamera
from direct.directnotify import DirectNotifyGlobal
from . import BattleParticles
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownBattleGlobals
import random
from otp.otpbase.PythonUtil import cmp_to_key
from . import MovieNPCSOS

notify = DirectNotifyGlobal.directNotify.newCategory('MovieSquirt')
hitSoundFiles = (
    'AA_squirt_flowersquirt.ogg', 
    'AA_squirt_glasswater.ogg', 
    'AA_squirt_neonwatergun.ogg', 
    'AA_squirt_seltzer.ogg', 
    'firehose_spray.ogg', 
    'AA_throw_stormcloud.ogg', 
    'AA_squirt_Geyser.ogg'
    )
missSoundFiles = (
    'AA_squirt_flowersquirt_miss.ogg', 
    'AA_squirt_glasswater_miss.ogg', 
    'AA_squirt_neonwatergun_miss.ogg', 
    'AA_squirt_seltzer_miss.ogg', 
    'firehose_spray.ogg', 
    'AA_throw_stormcloud_miss.ogg', 
    'AA_squirt_Geyser.ogg'
    )
sprayScales = [0.2,
 0.3,
 0.1,
 0.6,
 0.8,
 1.0,
 2.0]
WaterSprayColor = Point4(0.75, 0.75, 1.0, 0.8)


def doSquirts(squirts):
    if len(squirts) == 0:
        return (None, None)

    npcArrivals, npcDepartures, npcs = MovieNPCSOS.doNPCTeleports(squirts)
    suitSquirtsDict = {}
    doneUber = 0
    skip = 0
    for squirt in squirts:
        skip = 0
        if skip:
            pass
        else:
            if 1:
                target = squirt['target'][0]
                suitId = target['suit'].doId
                if suitId in suitSquirtsDict:
                    suitSquirtsDict[suitId].append(squirt)
                else:
                    suitSquirtsDict[suitId] = [squirt]

    suitSquirts = list(suitSquirtsDict.values())

    def compFunc(a, b):
        if len(a) > len(b):
            return 1
        elif len(a) < len(b):
            return -1
        return 0
    suitSquirts.sort(key=cmp_to_key(compFunc))

    delay = 0.0

    mtrack = Parallel()
    for st in suitSquirts:
        if len(st) > 0:
            ival = __doSuitSquirts(st, npcs)
            if ival:
                mtrack.append(Sequence(Wait(delay), ival))
            delay = delay + TOON_SQUIRT_SUIT_DELAY

    mtrack = Sequence(npcArrivals, mtrack, npcDepartures)
    camDuration = mtrack.getDuration()
    enterDuration = npcArrivals.getDuration()
    exitDuration = npcArrivals.getDuration()
    camTrack = MovieCamera.chooseSquirtShot(squirts, suitSquirtsDict, camDuration, enterDuration, exitDuration)
    return (mtrack, camTrack)


def __doSuitSquirts(squirts, npcs):
    uberClone = 0
    toonTracks = Parallel()
    delay = 0.0
    for target in squirts[0]['target']:
        if len(squirts) == 1 and target['hp'] > 0:
            fShowStun = 1
        else:
            fShowStun = 0

    for s in squirts:
        tracks = __doSquirt(s, delay, fShowStun, npcs, uberClone)
        if s['level'] >= ToontownBattleGlobals.UBER_GAG_LEVEL_INDEX:
            uberClone = 1
        if tracks:
            for track in tracks:
                toonTracks.append(track)

        delay = delay + TOON_SQUIRT_DELAY

    return toonTracks


def __doSquirt(squirt, delay, fShowStun, npcs, uberClone = 0):
    toon = squirt['toon']
    if 'npc' in squirt:
        toon = squirt['npc']
    squirtSequence = Sequence(Wait(delay))
    for target in squirt['target']:
        notify.debug('toon: %s squirts prop: %d at suit: %d for hp: %d' % (toon.getName(),
         squirt['level'],
         target['suit'].doId,
         target['hp']))

    if uberClone:
        ival = squirtfn_array[squirt['level']](squirt, delay, fShowStun, npcs, uberClone)
        if ival:
            squirtSequence.append(ival)
    else:
        ival = squirtfn_array[squirt['level']](squirt, delay, fShowStun, npcs)
        if ival:
            squirtSequence.append(ival)
    return [squirtSequence]


def __suitTargetPoint(suit):
    pnt = suit.getPos(render)
    pnt.setZ(pnt[2] + suit.getHeight() * 0.66)
    return Point3(pnt)


def __getSplashTrack(point, scale, delay, battle, splashHold = 0.01):

    def prepSplash(splash, point):
        if callable(point):
            point = point()
        splash.reparentTo(render)
        splash.setPos(point)
        scale = splash.getScale()
        splash.setBillboardPointWorld()
        splash.setScale(scale)

    splash = globalPropPool.getProp('splash-from-splat')
    splash.setScale(scale)
    return Sequence(
        Func(battle.movie.needRestoreRenderProp, splash), 
        Wait(delay), 
        Func(prepSplash, splash, point), 
        ActorInterval(splash, 'splash-from-splat'), 
        Wait(splashHold), 
        Func(MovieUtil.removeProp, splash), 
        Func(battle.movie.clearRenderProp, splash)
        )


def __getSuitTrack(suit, contactDelay, tDodge, hp, hpbonus, kbbonus, anim, died, 
                   leftSuits, rightSuits, battle, toon, fShowStun, npcs=None, 
                   beforeStun = 0.5, afterStun = 1.8, geyser = 0, 
                   uberRepeat = 0, revived = 0):
    if hp > 0:
        suitTrack = Sequence()
        if kbbonus > 0 and not geyser:
            suitPos, suitHpr = battle.getActorPosHpr(suit)
            suitType = getSuitBodyType(suit.getStyleName())
            animTrack = Sequence()
            animTrack.append(ActorInterval(suit, anim, duration=0.2))
            if suitType == 'a':
                animTrack.append(ActorInterval(suit, 'slip-forward', startTime=2.43))
            elif suitType == 'b':
                animTrack.append(ActorInterval(suit, 'slip-forward', startTime=1.94))
            elif suitType == 'c':
                animTrack.append(ActorInterval(suit, 'slip-forward', startTime=2.58))
            animTrack.append(Func(battle.unlureSuit, suit))
            moveTrack = Sequence(Wait(0.2), LerpPosInterval(suit, 0.6, pos=suitPos, other=battle))
            sival = Parallel(animTrack, moveTrack)
        elif geyser:
            suitStartPos = suit.getPos()
            suitFloat = Point3(0, 0, 14)
            suitEndPos = Point3(suitStartPos[0] + suitFloat[0], suitStartPos[1] + suitFloat[1], suitStartPos[2] + suitFloat[2])
            suitType = getSuitBodyType(suit.getStyleName())
            if suitType == 'a':
                startFlailFrame = 16
                endFlailFrame = 16
            elif suitType == 'b':
                startFlailFrame = 15
                endFlailFrame = 15
            else:
                startFlailFrame = 15
                endFlailFrame = 15
            sival = Sequence(
                ActorInterval(suit, 'slip-backward', playRate=0.5, startFrame=0, endFrame=startFlailFrame - 1), 
                Func(suit.pingpong, 'slip-backward', fromFrame=startFlailFrame, toFrame=endFlailFrame), 
                Wait(0.5), 
                ActorInterval(suit, 'slip-backward', playRate=1.0, startFrame=endFlailFrame)
                )
            sUp = LerpPosInterval(suit, 1.1, suitEndPos, startPos=suitStartPos, fluid=1)
            sDown = LerpPosInterval(suit, 0.6, suitStartPos, startPos=suitEndPos, fluid=1)
        elif fShowStun == 1:
            sival = Parallel(ActorInterval(suit, anim), MovieUtil.createSuitStunInterval(suit, beforeStun, afterStun))
        else:
            sival = ActorInterval(suit, anim)
        showDamage = Func(suit.showHpText, -hp, openEnded=0, attackTrack=SQUIRT_TRACK)
        suitTrack.append(Wait(contactDelay))
        suitTrack.append(showDamage)
        suitTrack.append(Func(suit.updateHealthBar, hp))
        if not geyser:
            suitTrack.append(sival)
        elif not uberRepeat:
            geyserMotion = Sequence(sUp, Wait(0.0), sDown)
            suitLaunch = Parallel(sival, geyserMotion)
            suitTrack.append(suitLaunch)
        else:
            suitTrack.append(Wait(5.5))
        bonusTrack = Sequence(Wait(contactDelay))
        if kbbonus > 0:
            bonusTrack.append(Wait(0.75))
            bonusTrack.append(Func(suit.showHpText, -kbbonus, 2, openEnded=0, attackTrack=SQUIRT_TRACK))
            bonusTrack.append(Func(suit.updateHealthBar, kbbonus))
        if hpbonus > 0:
            bonusTrack.append(Wait(0.75))
            bonusTrack.append(Func(suit.showHpText, -hpbonus, 1, openEnded=0, attackTrack=SQUIRT_TRACK))
            bonusTrack.append(Func(suit.updateHealthBar, hpbonus))
        if died != 0:
            suitTrack.append(MovieUtil.createSuitDeathTrack(suit, toon, battle, npcs))
        else:
            suitTrack.append(Func(suit.loop, 'neutral'))
        if revived != 0:
            suitTrack.append(MovieUtil.createSuitReviveTrack(suit, battle, npcs))
        return Parallel(suitTrack, bonusTrack)
    else:
        return MovieUtil.createSuitDodgeMultitrack(tDodge, suit, leftSuits, rightSuits)


def __getSoundTrack(level, hitSuit, delay, node = None):
    if hitSuit:
        soundEffect = globalBattleSoundCache.getSound(hitSoundFiles[level])
    else:
        soundEffect = globalBattleSoundCache.getSound(missSoundFiles[level])
    soundTrack = Sequence()
    if soundEffect:
        soundTrack.append(Wait(delay))
        soundTrack.append(SoundInterval(soundEffect, node=node))
    return soundTrack


def doFlower(squirt, delay, fShowStun, npcs=None):
    toon = squirt['toon']
    if 'npc' in squirt:
        toon = squirt['npc']
    level = squirt['level']
    hpbonus = squirt['hpbonus']
    target = squirt['target']
    suit = target[0]['suit']
    if not hasattr(suit, 'updateHealthBar'):
        suitGeom = target[0]['suitGeom']
    else:
        suitGeom = suit
    hp = target[0]['hp']
    kbbonus = target[0]['kbbonus']
    died = target[0]['died']
    revived = target[0]['revived']
    leftSuits = target[0]['leftSuits']
    rightSuits = target[0]['rightSuits']
    battle = squirt['battle']

    button = globalPropPool.getProp('button')
    flower = globalPropPool.getProp('squirting-flower')
    flower.setScale(1.5, 1.5, 1.5)

    suitPos = suit.getPos(battle)
    origHpr = toon.getHpr(battle)
    hitSuit = hp > 0
    scale = sprayScales[level]
    flowerAppearT = 1.0
    flowerScaleT = 0.5
    sprayScale = 0.2
    sprayHold = 0.1

    tracks = Parallel()
    if toon.getTransformationsIndex(0):
        flowerAnimT = 1.5
        toon.suit.corpMedallion.hide()
        flower_jointpath0 = toon.suitGeom.find('**/joint_attachMeter')
        toonTrack = Sequence(
            Func(toon.headsUp, battle, suitPos),
            MovieUtil.getSuitButtonAnimTrack(toon.suit)
        )
        removeJointpath = Func(toon.suit.corpMedallion.show)
    else:
        flowerAnimT = 2.5
        lodnames = toon.getLODNames()
        toonlod0 = toon.getLOD(lodnames[0])
        toonlod1 = toon.getLOD(lodnames[1])

        flower_joint0 = toonlod0.find('**/def_joint_attachFlower')
        flower_joint1 = toonlod1.find('**/def_joint_attachFlower')
        flower_jointpath0 = flower_joint0.attachNewNode('attachFlower-InstanceNode')
        flower_jointpath1 = flower_jointpath0.instanceTo(flower_joint1)

        toonTrack = Sequence(
            Func(MovieUtil.showProp, button, toon.leftHand), 
            Func(toon.headsUp, battle, suitPos), 
            ActorInterval(toon, 'pushbutton'),
            Func(MovieUtil.removeProp, button), 
            Func(toon.loop, 'neutral')
            )
        removeJointpath = Parallel(
            Func(flower_jointpath0.removeNode),
            Func(flower_jointpath1.removeNode)
        )
    contactDelay = flowerAnimT + sprayScale
    
    if 'npc' not in squirt:
        toonTrack.append(Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)
    tracks.append(__getSoundTrack(level, hitSuit, flowerAnimT - 0.4, toon))
    targetPoint = lambda suit = suit: __suitTargetPoint(suit)

    def getSprayStartPos(flower = flower):
        toon.update(0)
        return flower.getPos(render)

    sprayTrack = MovieUtil.getSprayTrack(battle, WaterSprayColor,
                                        getSprayStartPos, targetPoint,
                                        sprayScale, sprayHold, sprayScale, 
                                        horizScale=scale, vertScale=scale)

    flowerTrack = Sequence(
        Wait(flowerAppearT), 
        Func(flower.reparentTo, flower_jointpath0),
        LerpScaleInterval(flower, flowerScaleT, flower.getScale(), startScale=MovieUtil.PNT3_NEARZERO), 
        Wait(flowerAnimT - flowerScaleT - flowerAppearT)
        )

    if hp <= 0:
        flowerTrack.append(Wait(0.5))
    flowerTrack.append(sprayTrack)
    flowerTrack.append(LerpScaleInterval(flower, flowerScaleT, MovieUtil.PNT3_NEARZERO))
    flowerTrack.append(removeJointpath)
    flowerTrack.append(Func(MovieUtil.removeProp, flower))
    tracks.append(flowerTrack)

    if hp > 0:
        tracks.append(__getSplashTrack(targetPoint, scale, flowerAnimT + sprayScale, battle))
    if hp > 0 or delay <= 0:
        tracks.append(__getSuitTrack(suitGeom, contactDelay, flowerAnimT, hp, 
                                     hpbonus, kbbonus, 'squirt-small-react', 
                                     died, leftSuits, rightSuits, battle, toon, 
                                     fShowStun, npcs, revived=revived))
    return tracks


def __doWaterGlass(squirt, delay, fShowStun, npcs):
    toon = squirt['toon']
    if 'npc' in squirt:
        toon = squirt['npc']
    level = squirt['level']
    hpbonus = squirt['hpbonus']
    target = squirt['target']
    suit = target[0]['suit']
    hp = target[0]['hp']
    kbbonus = target[0]['kbbonus']
    died = target[0]['died']
    revived = target[0]['revived']
    leftSuits = target[0]['leftSuits']
    rightSuits = target[0]['rightSuits']
    battle = squirt['battle']

    hitSuit = hp > 0
    scale = sprayScales[level]
    targetPoint = lambda suit = suit: __suitTargetPoint(suit)
    
    if toon.getTransformationsIndex(0):
        watercooler = globalPropPool.getProp('watercooler')
        
        if toon.suit.getBodyType() == 'a':
            watercooler.setPosHpr(-0.833, 0.158, -0.162, 304.357, -50.976, 118.441)
        elif toon.suit.getBodyType() == 'b':
            watercooler.setPosHpr(-0.741, 0.058, -0.108, 289.364, -46.478, 121.443)
        elif toon.suit.getBodyType() == 'c':
            watercooler.setPosHpr(Point3(0.48, 0.11, -0.92), VBase3(20.403, 33.158, 69.511))
        tip = watercooler.find('**/joint_toSpray')
        
        sprayT = 1.3
        sprayScale = 0.5
        tSuitDodges = max(sprayT - 0.5, 0.0)

        waterSprayAppearOnly = base.loader.loadSfx('phase_5/audio/sfx/SA_watercooler_appear_only.ogg')
        waterSprayOnly = base.loader.loadSfx('phase_5/audio/sfx/SA_watercooler_spray_only.ogg')

        def getTipPos(tip = tip):
            return tip.getPos(render)
        
        if toon.suit.getBodyType() == 'c':
            propAppearT = 1.01
            propScale = (0.8, 0.8, 0.8)
            sprayTrackDelay = 1.6
            hand = toon.suit.leftHand
            contactDelay = 2.9722
            toonTrack = Sequence(
                ActorInterval(toon.suit, 'watercooler'),
                Func(toon.suit.loop, 'neutral')
            )
            soundTrack = Sequence(
                Wait(1.1),
                SoundInterval(waterSprayAppearOnly, node=toon, duration=1.4722),
                Wait(0.4),
                SoundInterval(waterSprayOnly, node=toon, duration=2.313)
            )
        else:
            propAppearT = 0.01
            propScale = Point3(1.15, 1.15, 1.15)
            sprayTrackDelay = 1.05
            hand = toon.suit.rightHand
            contactDelay = 1.8
            toonTrack = Sequence(
                ActorInterval(toon.suit, 'pen-squirt'),
                Wait(2),
                Func(toon.suit.loop, 'neutral')
            )
            soundTrack = Sequence(
                Wait(1.6),
                SoundInterval(waterSprayOnly, node=toon, duration=2.313)
            )

        propTrack = Sequence(
            Wait(propAppearT),
            Func(MovieUtil.showProp, watercooler, hand, MovieUtil.PNT3_ZERO),
            watercooler.scaleInterval(0.5, propScale),
            Wait(sprayTrackDelay),
            MovieUtil.getSprayTrack(battle, 
                                    WaterSprayColor, 
                                    getTipPos, 
                                    targetPoint, 
                                    0.2, 
                                    0.2, 
                                    0.2, 
                                    horizScale = 0.1, 
                                    vertScale = 0.1),
            watercooler.scaleInterval(0.5, (0, 0, 0)),
            Func(MovieUtil.removeProp, watercooler)
        )
        tracks = Parallel(toonTrack, propTrack, soundTrack)
    else:
        dGlassHold = 5.0
        dGlassScale = 0.5
        sprayT = 82.0 / toon.getFrameRate('spit')
        sprayPoseFrame = 88
        sprayScale = 0.1
        sprayHold = 0.1
        contactDelay = sprayT + sprayScale
        tSuitDodges = max(sprayT - 0.5, 0.0)

        toonAnimTrack = Sequence(
            ActorInterval(toon, 'spit'),
            Func(toon.loop, 'neutral')
        )
        tracks = Parallel()
        tracks.append(toonAnimTrack)
        tracks.append(__getSoundTrack(level, hitSuit, 1.7, toon))

        glass = globalPropPool.getProp('glass')
        hands = toon.getRightHands()
        hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
        hand_jointpath1 = hand_jointpath0.instanceTo(hands[1])
        glassTrack = Sequence(
            Func(MovieUtil.showProp, glass, hand_jointpath0), 
            ActorInterval(glass, 'glass'), 
            Func(hand_jointpath1.removeNode),
            Func(hand_jointpath0.removeNode), 
            Func(MovieUtil.removeProp, glass)
            )
        tracks.append(glassTrack)
        targetPoint = lambda suit = suit: __suitTargetPoint(suit)

        def getSprayStartPos(toon = toon):
            toon.update(0)
            lod0 = toon.getLOD(toon.getLODNames()[0])
            if base.config.GetBool('want-new-anims', 1):
                if not lod0.find('**/def_head').isEmpty():
                    joint = lod0.find('**/def_head')
                else:
                    joint = lod0.find('**/joint_head')
            else:
                joint = lod0.find('**/joint_head')
            n = hidden.attachNewNode('pointInFrontOfHead')
            n.reparentTo(toon)
            n.setPos(joint.getPos(toon) + Point3(0, 0.3, -0.2))
            p = n.getPos(render)
            n.removeNode()
            del n
            return p

        sprayTrack = MovieUtil.getSprayTrack(battle, WaterSprayColor, 
                                            getSprayStartPos, targetPoint, 
                                            sprayScale, sprayHold, sprayScale, 
                                            horizScale=scale, vertScale=scale)
        tracks.append(Sequence(Wait(sprayT), sprayTrack))

    if hp > 0:
        tracks.append(__getSplashTrack(targetPoint, scale, contactDelay, battle))
    if hp > 0 or delay <= 0:
        tracks.append(__getSuitTrack(suit, contactDelay, tSuitDodges, hp, hpbonus, 
                                        kbbonus, 'squirt-small-react', died, 
                                        leftSuits, rightSuits, battle, toon, 
                                        fShowStun, npcs, revived=revived))
    return tracks


def __doWaterGun(squirt, delay, fShowStun, npcs):
    toon = squirt['toon']
    if 'npc' in squirt:
        toon = squirt['npc']
    level = squirt['level']
    hpbonus = squirt['hpbonus']
    target = squirt['target']
    suit = target[0]['suit']
    hp = target[0]['hp']
    kbbonus = target[0]['kbbonus']
    died = target[0]['died']
    revived = target[0]['revived']
    leftSuits = target[0]['leftSuits']
    rightSuits = target[0]['rightSuits']
    battle = squirt['battle']

    suitPos = suit.getPos(battle)
    origHpr = toon.getHpr(battle)
    hitSuit = hp > 0
    scale = sprayScales[level]
    tPistol = 0.0
    dPistolScale = 0.5
    sprayPoseFrame = 63
    sprayScale = 0.1
    tSuitDodges = 1.1

    pistol = globalPropPool.getProp('water-gun')
    tracks = Parallel()

    if toon.getTransformationsIndex(0):
        hand = toon.suit.rightHand
        pistol.reparentTo(hand)
        timeTillSpray = 0.5
        soundDelay = 1.0
        contactDelay = 1.2
        pistolPos = Point3(0, 0, 0)
        pistolHpr = (85, -4.44 - 180, 90)
        if toon.suit.getBodyType() == 'b':
            sprayHold = 0.2
            dPistolHold = 1
            toonTrack = Sequence(
                Func(toon.headsUp, battle, suitPos),
                ActorInterval(toon.suit, 'hold-pencil', startFrame=0, endFrame=40, playRate=1.2),
                ActorInterval(toon.suit, 'hold-pencil', startFrame=40, endFrame=0),
                Func(toon.suit.loop, 'neutral')
            )
        else:
            sprayHold = 0.3
            dPistolHold = 1.5
            toonTrack = Sequence(
                Func(toon.headsUp, battle, suitPos), 
                ActorInterval(toon.suit, 'finger-wag', playRate=0.7, endFrame=14), 
                Wait(2.0), 
                ActorInterval(toon.suit, 'finger-wag', startFrame=14, endFrame=0),
                Func(toon.suit.loop, 'neutral')
                )
    else:
        dPistolHold = 1.8
        hand = toon.rightHand
        tSpray = 48.0 / toon.getFrameRate('water-gun')
        sprayHold = 0.3
        timeTillSpray = tSpray - dPistolScale
        soundDelay = 1.8
        contactDelay = tSpray + sprayScale
        pistolPos = Point3(0.28, 0.1, 0.08)
        pistolHpr = VBase3(85.6, -4.44, 94.43)
        toonTrack = Sequence(
            Func(toon.headsUp, battle, suitPos), 
            ActorInterval(toon, 'water-gun'), 
            Func(toon.loop, 'neutral')
            )
    pistol.reparentTo(hand)
    pistol.setPosHpr(pistolPos, pistolHpr)
    if 'npc' not in squirt:
        toonTrack.append(Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)
    tracks.append(__getSoundTrack(level, hitSuit, soundDelay, toon))
    targetPoint = lambda suit = suit: __suitTargetPoint(suit)

    def getSprayStartPos(pistol = pistol, toon = toon):
        toon.update(0)
        joint = pistol.find('**/joint_nozzle')
        p = joint.getPos(render)
        return p

    pistolTrack = Sequence(
        LerpScaleInterval(pistol, dPistolScale, pistol.getScale(), startScale=MovieUtil.PNT3_NEARZERO), 
        Wait(timeTillSpray),
        MovieUtil.getSprayTrack(battle, WaterSprayColor, 
                                getSprayStartPos, targetPoint, 
                                sprayScale, sprayHold, sprayScale, 
                                horizScale=scale, vertScale=scale),
        Wait(dPistolHold),
        LerpScaleInterval(pistol, dPistolScale, MovieUtil.PNT3_NEARZERO),
        Func(MovieUtil.removeProp, pistol)
        )
    tracks.append(pistolTrack)

    if hp > 0:
        tracks.append(__getSplashTrack(targetPoint, 0.3, contactDelay, battle))
    if hp > 0 or delay <= 0:
        tracks.append(__getSuitTrack(suit, contactDelay, tSuitDodges, hp, hpbonus, 
                                     kbbonus, 'squirt-small-react', died, 
                                     leftSuits, rightSuits, battle, toon, 
                                     fShowStun, npcs, revived=revived))
    return tracks


def __doSeltzerBottle(squirt, delay, fShowStun, npcs):
    toon = squirt['toon']
    if 'npc' in squirt:
        toon = squirt['npc']
    level = squirt['level']
    hpbonus = squirt['hpbonus']
    target = squirt['target']
    suit = target[0]['suit']
    hp = target[0]['hp']
    kbbonus = target[0]['kbbonus']
    died = target[0]['died']
    revived = target[0]['revived']
    leftSuits = target[0]['leftSuits']
    rightSuits = target[0]['rightSuits']
    battle = squirt['battle']

    suitPos = suit.getPos(battle)
    origHpr = toon.getHpr(battle)
    hitSuit = hp > 0
    scale = sprayScales[level]
    tBottle = 0.0
    tSpray = 53.0 / toon.getFrameRate('hold-bottle') + 0.05
    sprayScale = 0.2
    sprayHold = 0.1

    bottle = globalPropPool.getProp('bottle')
    tracks = Parallel()

    if toon.getTransformationsIndex(0):
        hand = toon.suit.leftHand
        timeTillSpray = 1.0
        soundDelay = 1.3
        contactDelay = 1.4
        tSuitDodges = 1.2
        dBottleHold = 0.6
        dBottleScale = 0.2
        sec = 0.7
        if toon.suit.getBodyType() == 'a':
            bottleScale = bottle.getScale()
            iPos = (-1.079, -0.288, -1.917)
            iHpr = (-58.413, -56.103, -34.484)
            frame = 19
        elif toon.suit.getBodyType() == 'b':
            bottleScale = (0.7, 0.7, 0.7)
            iPos = (-0.342, -0.375, -1.2)
            iHpr = (0.169, -67.468, -11.994)
            frame = 24
        elif toon.suit.getBodyType() == 'c':
            bottleScale = (0.8, 0.8, 0.8)
            iPos = (-0.433, -0.588, -1.291)
            iHpr = (10.495, -70.467, -1.499)
            frame = 24
        bottle.setPosHpr(Point3(iPos), Point3(iHpr))
        toonTrack = Sequence(
            Func(toon.headsUp, battle, suitPos), 
            ActorInterval(toon.suit, 'phone', endFrame=frame), 
            Wait(sec), 
            ActorInterval(toon.suit, 'phone', startFrame=frame, endFrame=0),
            Func(toon.suit.loop, 'neutral')
        )
    else:
        bottleScale = bottle.getScale()
        timeTillSpray = 1.7583
        soundDelay = 2.1583
        contactDelay = 2.4583
        tSuitDodges = 1.7583
        dBottleHold = 3.0
        dBottleScale = 0.5
        hand = toon.rightHand
        toonTrack = Sequence(
            Func(toon.headsUp, battle, suitPos), 
            ActorInterval(toon, 'hold-bottle'), 
            Func(toon.loop, 'neutral')
            )
    if 'npc' not in squirt:
        toonTrack.append(Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)
    tracks.append(__getSoundTrack(level, hitSuit, soundDelay, toon))
    targetPoint = lambda suit = suit: __suitTargetPoint(suit)

    def getSprayStartPos(bottle = bottle, toon = toon):
        toon.update(0)
        joint = bottle.find('**/joint_toSpray')
        n = hidden.attachNewNode('pointBehindSprayProp')
        n.reparentTo(toon)
        n.setPos(joint.getPos(toon) + Point3(0, -0.4, 0))
        p = n.getPos(render)
        n.removeNode()
        del n
        return p

    sprayTrack = MovieUtil.getSprayTrack(battle, WaterSprayColor, 
                                         getSprayStartPos, targetPoint, 
                                         sprayScale, sprayHold, sprayScale, 
                                         horizScale=scale, vertScale=scale)

    bottleTrack = Sequence(
        Func(MovieUtil.showProp, bottle, hand), 
        LerpScaleInterval(bottle, dBottleScale, bottleScale, startScale=MovieUtil.PNT3_NEARZERO), 
        Wait(timeTillSpray),
        )
    bottleTrack.append(sprayTrack)
    bottleTrack.append(Wait(dBottleHold))
    bottleTrack.append(LerpScaleInterval(bottle, dBottleScale, MovieUtil.PNT3_NEARZERO))
    bottleTrack.append(Func(MovieUtil.removeProp, bottle))
    tracks.append(bottleTrack)
    
    if hp > 0:
        tracks.append(__getSplashTrack(targetPoint, scale, contactDelay, battle))
    if (hp > 0 or delay <= 0) and suit:
        tracks.append(__getSuitTrack(suit, contactDelay, tSuitDodges, hp, hpbonus, 
                                     kbbonus, 'squirt-small-react', died, 
                                     leftSuits, rightSuits, battle, toon, 
                                     fShowStun, npcs, revived=revived))
    return tracks


def __doFireHose(squirt, delay, fShowStun, npcs):
    toon = squirt['toon']
    if 'npc' in squirt:
        toon = squirt['npc']
    level = squirt['level']
    hpbonus = squirt['hpbonus']
    target = squirt['target']
    suit = target[0]['suit']
    hp = target[0]['hp']
    kbbonus = target[0]['kbbonus']
    died = target[0]['died']
    revived = target[0]['revived']
    leftSuits = target[0]['leftSuits']
    rightSuits = target[0]['rightSuits']
    battle = squirt['battle']

    suitPos = suit.getPos(battle)
    origHpr = toon.getHpr(battle)
    hitSuit = hp > 0

    targetPoint = lambda suit = suit: __suitTargetPoint(suit)
    # pen-squirt works for now. I'll probably make a proper fire hose animation
    if toon.getTransformationsIndex(0):
        pen = globalPropPool.getProp('pen')
        tip = pen.find('**/joint_toSpray')
        ink = BattleParticles.createParticleEffect(file='penSpill')
        ink.setPos(tip.getPos(render))
        
        sprayT = 1.3
        sprayScale = 0.5
        splashDelay = 1.8
        splashHold = 0.01
        contactDelay = 1.8
        tSuitDodges = 1.4

        def getTipPos(tip = tip):
            return tip.getPos(render)
        
        inkTrack = Sequence(
            Wait(1.4),
            ParticleInterval(ink, pen, worldRelative=0, duration=0.7, cleanup=True)
        )
        toonTrack = Sequence(
            ActorInterval(toon.suit, 'pen-squirt'),
            Wait(2),
            Func(toon.suit.loop, 'neutral')
        )
        propTrack = Sequence(
            Wait(0.01),
            Func(MovieUtil.showProp, pen, toon.suit.rightHand, MovieUtil.PNT3_ZERO),
            pen.scaleInterval(0.5, (1.5, 1.5, 1.5)),
            Wait(1.05),
            MovieUtil.getSprayTrack(battle, 
                                    VBase4(0, 0, 0, 1), 
                                    getTipPos, 
                                    targetPoint, 
                                    0.2, 
                                    0.2, 
                                    0.2, 
                                    horizScale = 0.1, 
                                    vertScale = 0.1),
            pen.scaleInterval(0.5, (0, 0, 0)),
            Func(MovieUtil.removeProp, pen)
        )

        sfx = loader.loadSfx('phase_5/audio/sfx/SA_fountain_pen.ogg')
        soundTrack = Sequence(
            Wait(1.6),
            SoundInterval(sfx, node=toon)
        )
        tracks = Parallel(toonTrack, propTrack, soundTrack, inkTrack)
    else:
        tracks = Parallel()
        
        tAppearDelay = 0.7
        dHoseHold = 0.7
        tSprayDelay = 2.8
        tSpray = 0.2
        sprayScale = 0.1
        sprayHold = 1.8
        contactDelay = 2.9
        tSuitDodges = 2.1
        propScale = 1
        splashDelay = 2.7
        splashHold = 1.5

        hose = globalPropPool.getProp('firehose')
        hydrant = globalPropPool.getProp('hydrant')
        hose.reparentTo(hydrant)
        hose.pose('firehose', 2)

        hydrantNode = toon.attachNewNode('hydrantNode')
        hydrantScale = hydrantNode.attachNewNode('hydrantScale')
        hydrant.reparentTo(hydrantScale)
        hydrantNode.clearTransform(toon.getGeomNode().getChild(0))

        toonTrack = Sequence(
            Wait(tAppearDelay), 
            Func(toon.headsUp, battle, suitPos), 
            ActorInterval(toon, 'firehose'),
            Func(toon.loop, 'neutral')
            )
        if 'npc' not in squirt:
            toonTrack.append(Func(toon.setHpr, battle, origHpr))
        tracks.append(toonTrack)
        tracks.append(__getSoundTrack(level, hitSuit, tSprayDelay, toon))

        toon.pose('firehose', 30)
        toon.update(0)
        torso = toon.getPart('torso', '1000')
        if toon.style.torso[0] == 'm':
            hydrant.setPos(torso, 0, 0, -1.85)
        else:
            hydrant.setPos(torso, 0, 0, -1.45)
        hydrant.setPos(0, 0, hydrant.getZ())
        base = hydrant.find('**/base')
        base.setColor(1, 1, 1, 0.5)
        base.setPos(toon, 0, 0, 0)
        toon.loop('neutral')

        def getSprayStartPos(hose = hose, toon = toon, targetPoint = targetPoint):
            toon.update(0)
            if hose.isEmpty() == 1:
                if callable(targetPoint):
                    return targetPoint()
                else:
                    return targetPoint
            joint = hose.find('**/joint_water_stream')
            n = hidden.attachNewNode('pointBehindSprayProp')
            n.reparentTo(toon)
            n.setPos(joint.getPos(toon) + Point3(0, -0.55, 0))
            p = n.getPos(render)
            n.removeNode()
            del n
            return p

        sprayTrack = Sequence()
        sprayTrack.append(Wait(tSprayDelay))
        sprayTrack.append(MovieUtil.getSprayTrack(battle, WaterSprayColor, 
                                                getSprayStartPos, targetPoint,
                                                sprayScale, sprayHold, 
                                                sprayScale, horizScale=0.3, 
                                                vertScale=0.3))
        tracks.append(sprayTrack)
        hydrantNode.detachNode()

        propTrack = Sequence(
            Func(battle.movie.needRestoreRenderProp, hydrantNode), 
            Func(hydrantNode.reparentTo, toon), 
            LerpScaleInterval(hydrantScale, tAppearDelay * 0.5, Point3(propScale, propScale, 1.4), startScale=Point3(propScale, propScale, 0.01)), 
            LerpScaleInterval(hydrantScale, tAppearDelay * 0.3, Point3(propScale, propScale, 0.8), startScale=Point3(propScale, propScale, 1.4)), 
            LerpScaleInterval(hydrantScale, tAppearDelay * 0.1, Point3(propScale, propScale, 1.25), startScale=Point3(propScale, propScale, 0.8)), 
            LerpScaleInterval(hydrantScale, tAppearDelay * 0.1, Point3(propScale, propScale, propScale), startScale=Point3(propScale, propScale, 1.25)), 
            ActorInterval(hose, 'firehose', duration=5.1, startTime=0), 
            Wait(dHoseHold - 0.2), 
            LerpScaleInterval(hydrantScale, 0.2, Point3(1, 1, 0.01), startScale=Point3(1, 1, 1)), 
            Func(MovieUtil.removeProps, [hydrantNode, hose]), 
            Func(battle.movie.clearRenderProp, hydrantNode)
            )
        tracks.append(propTrack)

    if hp > 0:
        tracks.append(__getSplashTrack(targetPoint, 0.4, splashDelay, battle, splashHold=splashHold))
    if hp > 0 or delay <= 0:
        tracks.append(__getSuitTrack(suit, contactDelay, tSuitDodges, hp, hpbonus, 
                                     kbbonus, 'squirt-small-react', died, 
                                     leftSuits, rightSuits, battle, toon, 
                                     fShowStun, npcs, revived=revived))
    return tracks


def __doStormCloud(squirt, delay, fShowStun, npcs):
    toon = squirt['toon']
    if 'npc' in squirt:
        toon = squirt['npc']
    level = squirt['level']
    hpbonus = squirt['hpbonus']
    tracks = Parallel()

    if toon.getTransformationsIndex(0):
        animTrack = MovieUtil.getSuitButtonAnimTrack(toon.suit)
        contactDelay = 1.8
        tSuitDodges = 0.7
        firstSoundDelay = 1.2
        secondSoundDelay = 3.5
        cloudScaleDur = 1.35
        rainDelay = 0
        effectDelay = 0
    else:
        animTrack = MovieUtil.getToonButtonAnimTrack(toon)
        contactDelay = 2.9
        tSuitDodges = 1.8
        firstSoundDelay = 2.3
        secondSoundDelay = 4.6
        cloudScaleDur = 1.5
        rainDelay = 1
        effectDelay = 0.3

    battle = squirt['battle']
    origHpr = toon.getHpr(battle)
    suitPos = MovieUtil.calcAvgSuitPos(squirt)

    toonTrack = Sequence( 
        Func(toon.headsUp, battle, suitPos),
        animTrack
    ) 
    if 'npc' not in squirt:
        toonTrack.append(Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)

    for target in squirt['target']:
        suit = target['suit']
        hp = target['hp']
        kbbonus = target['kbbonus']
        died = target['died']
        revived = target['revived']
        leftSuits = target['leftSuits']
        rightSuits = target['rightSuits']
        suitPos = suit.getPos(battle)
        hitSuit = hp > 0
        scale = sprayScales[level]
        tracks.append(__getSoundTrack(level, hitSuit, firstSoundDelay, toon))
        tracks.append(__getSoundTrack(level, hitSuit, secondSoundDelay, toon))
        delayTime = random.random()
        cloud = globalPropPool.getProp('stormcloud')
        cloud2 = MovieUtil.copyProp(cloud)
        BattleParticles.loadParticles()
        trickleEffect = BattleParticles.createParticleEffect(file='trickleLiquidate')
        rainEffect = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect2 = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect3 = BattleParticles.createParticleEffect(file='liquidate')
        cloudHeight = suit.height + 3
        cloudPosPoint = Point3(0, 0, cloudHeight)
        scaleUpPoint = Point3(3, 3, 3)
        rainEffects = [rainEffect, rainEffect2, rainEffect3]
        if hp > 0:
            cloudHold = 4.7
        else:
            cloudHold = 1.7
        
        def getCloudTrack(cloud, suit, cloudPosPoint, scaleUpPoint, rainEffects, 
                          rainDelay, effectDelay, cloudHold, useEffect, 
                          battle = battle, trickleEffect = trickleEffect):
            track = Sequence(
                Func(MovieUtil.showProp, cloud, suit, cloudPosPoint), 
                Func(cloud.pose, 'stormcloud', 0), 
                LerpScaleInterval(cloud, cloudScaleDur, scaleUpPoint, startScale=MovieUtil.PNT3_NEARZERO), 
                Wait(rainDelay)
                )
        
            if useEffect == 1:
                ptrack = Parallel()
                delay = trickleDuration = cloudHold * 0.25
                trickleTrack = Sequence(
                    Func(battle.movie.needRestoreParticleEffect, trickleEffect), 
                    ParticleInterval(trickleEffect, cloud, worldRelative=0, duration=trickleDuration, cleanup=True), 
                    Func(battle.movie.clearRestoreParticleEffect, trickleEffect)
                    )
                track.append(trickleTrack)
                for i in range(0, 3):
                    dur = cloudHold - 2 * trickleDuration
                    ptrack.append(
                        Sequence(
                            Func(battle.movie.needRestoreParticleEffect, rainEffects[i]), 
                            Wait(delay), 
                            ParticleInterval(rainEffects[i], cloud, worldRelative=0, duration=dur, cleanup=True), 
                            Func(battle.movie.clearRestoreParticleEffect, rainEffects[i])
                        )
                    )
                    delay += effectDelay
        
                ptrack.append(
                    Sequence(
                        Wait(3 * effectDelay), 
                        ActorInterval(cloud, 'stormcloud', startTime=1, duration=cloudHold)
                    )
                )
                track.append(ptrack)
            else:
                track.append(ActorInterval(cloud, 'stormcloud', startTime=1, duration=cloudHold))
            track.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
            track.append(Func(MovieUtil.removeProp, cloud))
            return track
        
        tracks.append(
            Sequence(
                Wait(delayTime),
                getCloudTrack(cloud, suit, cloudPosPoint, scaleUpPoint, 
                              rainEffects, rainDelay, effectDelay,
                              cloudHold, useEffect=1)
            )
        )
        tracks.append(
            Sequence(
                Wait(delayTime),
                getCloudTrack(cloud2, suit, cloudPosPoint, scaleUpPoint, 
                              rainEffects, rainDelay, effectDelay,
                              cloudHold, useEffect=0)
            )
        )
        if hp > 0 or delay <= 0:
            tracks.append(
                Sequence(
                    Wait(delayTime),
                    __getSuitTrack(suit, contactDelay, tSuitDodges, hp, hpbonus, 
                                   kbbonus, 'soak', died, leftSuits, rightSuits,
                                   battle, toon, fShowStun, npcs, beforeStun=2.6,
                                   afterStun=2.3, revived=revived)
                )
            )
        
        if hp > 0:
            changeSuitColor = Sequence(
                Wait(contactDelay - 0.5 + delayTime),
                LerpColorScaleInterval(suit, 3.5, (0.4, 0.55, 0.8, 1), blendType='easeInOut'),
                LerpColorScaleInterval(suit, 3, (1, 1, 1, 1), blendType='easeInOut')
            )
            tracks.append(changeSuitColor)

    return tracks


def __doGeyser(squirt, delay, fShowStun, npcs, uberClone = 0):
    toon = squirt['toon']
    if 'npc' in squirt:
        toon = squirt['npc']
    level = squirt['level']
    hpbonus = squirt['hpbonus']
    tracks = Parallel()

    contactDelay = 2.9
    tSuitDodges = 1.8

    battle = squirt['battle']
    origHpr = toon.getHpr(battle)
    suitPos = MovieUtil.calcAvgSuitPos(squirt)

    if toon.getTransformationsIndex(0):
        animTrack = MovieUtil.getSuitButtonAnimTrack(toon.suit)
    else:
        animTrack = MovieUtil.getToonButtonAnimTrack(toon)
    toonTrack = Sequence(
        Func(toon.headsUp, battle, suitPos),
        animTrack 
        )

    if 'npc' not in squirt:
        toonTrack.append(Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)

    for target in squirt['target']:
        suit = target['suit']
        hp = target['hp']
        kbbonus = target['kbbonus']
        died = target['died']
        revived = target['revived']
        leftSuits = target['leftSuits']
        rightSuits = target['rightSuits']
        suitPos = suit.getPos(battle)
        hitSuit = hp > 0
        scale = sprayScales[level]
        soundTrack = __getSoundTrack(level, hitSuit, 1.8, toon)
        delayTime = random.random()
        tracks.append(Wait(delayTime))
        tracks.append(soundTrack)
        cloud = globalPropPool.getProp('geyser')
        cloud2 = MovieUtil.copyProp(cloud)
        BattleParticles.loadParticles()
        geyserHeight = battle.getH()
        geyserPosPoint = Point3(0, 0, geyserHeight)
        scaleUpPoint = Point3(1.8, 1.8, 1.8)
        rainEffects = []
        rainDelay = 2.5
        effectDelay = 0.3
        if hp > 0:
            geyserHold = 1.5
        else:
            geyserHold = 0.5

        def getGeyserTrack(geyser, suit, geyserPosPoint, scaleUpPoint, 
                           rainEffects, rainDelay, effectDelay, geyserHold, 
                           useEffect, battle = battle):
            geyserMound = MovieUtil.copyProp(geyser)
            geyserRemoveM = geyserMound.findAllMatches('**/Splash*')
            geyserRemoveM.addPathsFrom(geyserMound.findAllMatches('**/spout'))
            for i in range(geyserRemoveM.getNumPaths()):
                geyserRemoveM[i].removeNode()

            geyserWater = MovieUtil.copyProp(geyser)
            geyserRemoveW = geyserWater.findAllMatches('**/hole')
            geyserRemoveW.addPathsFrom(geyserWater.findAllMatches('**/shadow'))
            for i in range(geyserRemoveW.getNumPaths()):
                geyserRemoveW[i].removeNode()

            track = Sequence(
                Wait(rainDelay), 
                Func(MovieUtil.showProp, geyserMound, battle, suit.getPos(battle)), 
                Func(MovieUtil.showProp, geyserWater, battle, suit.getPos(battle)), 
                LerpScaleInterval(geyserWater, 1.0, scaleUpPoint, startScale=MovieUtil.PNT3_NEARZERO), 
                Wait(geyserHold * 0.5), 
                LerpScaleInterval(geyserWater, 0.5, MovieUtil.PNT3_NEARZERO, startScale=scaleUpPoint)
                )
            track.append(LerpScaleInterval(geyserMound, 0.5, MovieUtil.PNT3_NEARZERO))
            track.append(Func(MovieUtil.removeProp, geyserMound))
            track.append(Func(MovieUtil.removeProp, geyserWater))
            track.append(Func(MovieUtil.removeProp, geyser))
            return track

        if not uberClone:
            tracks.append(
                Sequence(
                    Wait(delayTime), 
                    getGeyserTrack(cloud, suit, geyserPosPoint, scaleUpPoint, 
                                   rainEffects, rainDelay, effectDelay, 
                                   geyserHold, useEffect=1)
                )
            )
        if hp > 0 or delay <= 0:
            tracks.append(
                Sequence(
                    Wait(delayTime), 
                    __getSuitTrack(suit, contactDelay, tSuitDodges, hp, hpbonus, 
                                   kbbonus, 'soak', died, leftSuits, rightSuits, 
                                   battle, toon, fShowStun, npcs, beforeStun=2.6, 
                                   afterStun=2.3, geyser=1, uberRepeat=uberClone, 
                                   revived=revived)
                )
            )

    return tracks

squirtfn_array = (doFlower,
 __doWaterGlass,
 __doWaterGun,
 __doSeltzerBottle,
 __doFireHose,
 __doStormCloud,
 __doGeyser)
