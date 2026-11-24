from typing import Tuple, List
from panda3d.toontown import *
from toontown.toonbase.ToontownGlobals import *
from direct.interval.IntervalGlobal import *
from .BattleBase import *
from .BattleProps import *
from toontown.suit.SuitDNA import *
from .BattleBase import *
from .BattleSounds import *
from . import MovieCamera
from direct.directnotify import DirectNotifyGlobal
from . import MovieUtil
from direct.particles import ParticleEffect
from . import BattleParticles
from toontown.effects import DustCloud, Splash
from toontown.toon import Toon
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
notify = DirectNotifyGlobal.directNotify.newCategory('MovieSuitAttacks')

def __doDamage(toon, dmg, died):
    if dmg > 0 and toon.hp != None:
        toon.takeDamage(dmg)

def __doStatus(toon, identifier: str):
    toon.showStatusText(identifier)


def __showProp(prop, parent, pos, hpr = None, scale = None):
    prop.reparentTo(parent)
    prop.setPos(pos)
    if hpr:
        prop.setHpr(hpr)
    if scale:
        prop.setScale(scale)


def __animProp(prop, propName, propType = 'actor'):
    if 'actor' == propType:
        prop.play(propName)
    elif 'model' == propType:
        pass
    else:
        notify.error('No such propType as: %s' % propType)

def __billboardProp(prop):
    scale = prop.getScale()
    prop.setBillboardPointWorld()
    prop.setScale(scale)

def __suitFacePoint(suit, zOffset = 0):
    pnt = suit.getPos()
    pnt.setZ(pnt[2] + suit.shoulderHeight + 0.3 + zOffset)
    return Point3(pnt)


def __toonFacePoint(toon, zOffset = 0, parent = render):
    pnt = toon.getPos(parent)
    pnt.setZ(pnt[2] + toon.shoulderHeight + 0.3 + zOffset)
    return Point3(pnt)


def __toonTorsoPoint(toon, zOffset = 0):
    pnt = toon.getPos()
    pnt.setZ(pnt[2] + toon.shoulderHeight - 0.2)
    return Point3(pnt)


def __toonGroundPoint(attack, toon, zOffset = 0, parent = render):
    pnt = toon.getPos(parent)
    battle = attack['battle']
    pnt.setZ(battle.getZ(parent) + zOffset)
    return Point3(pnt)


def __toonGroundMissPoint(attack, prop, toon, zOffset = 0):
    point = __toonMissPoint(prop, toon)
    battle = attack['battle']
    point.setZ(battle.getZ() + zOffset)
    return Point3(point)


def __toonMissPoint(prop, toon, yOffset = 0, parent = None):
    if parent:
        p = __toonFacePoint(toon) - prop.getPos(parent)
    else:
        p = __toonFacePoint(toon) - prop.getPos()
    v = Vec3(p)
    baseDistance = v.length()
    v.normalize()
    if parent:
        endPos = prop.getPos(parent) + v * (baseDistance + 5 + yOffset)
    else:
        endPos = prop.getPos() + v * (baseDistance + 5 + yOffset)
    return Point3(endPos)


def __toonMissBehindPoint(toon, parent = render, offset = 0):
    point = toon.getPos(parent)
    point.setY(point.getY() - 5 + offset)
    return point


def __throwBounceHitPoint(prop, toon):
    startPoint = prop.getPos()
    endPoint = __toonFacePoint(toon)
    return __throwBouncePoint(startPoint, endPoint)


def __throwBounceMissPoint(prop, toon):
    startPoint = prop.getPos()
    endPoint = __toonFacePoint(toon)
    return __throwBouncePoint(startPoint, endPoint)


def __throwBouncePoint(startPoint, endPoint):
    midPoint = startPoint + (endPoint - startPoint) / 2.0
    midPoint.setZ(0)
    return Point3(midPoint)


def doSuitAttack(attack):
    name: str = attack['identifier']
    notify.debug('building suit attack in doSuitAttack: %s' % attack['identifier'])
    # disgusting
    if name == 'ttrealms:active_state' or name == 'ttrealms:stomp':
        suitTrack = doStomp(attack)
    elif name in ('ttrealms:audit', 'ttrealms:calculate', 'ttrealms:tabulate'):
        suitTrack = doAudit(attack)
    elif name in ('ttrealms:bite', 'ttrealms:bite_group'):
        suitTrack = doBite(attack)
    elif name in ('ttrealms:bounce_check', 'ttrealms:bounce_check_group'):
        suitTrack = doBounceCheck(attack)
    elif name == 'ttrealms:blizzard':
        suitTrack = doBlizzard(attack)
    elif name in ('ttrealms:brainstorm', 'ttrealms:brainstorm_group'):
        suitTrack = doBrainStorm(attack)
    elif name == 'ttrealms:buzz_word':
        suitTrack = doBuzzWord(attack)
    elif name == 'ttrealms:canned':
        suitTrack = doCanned(attack)
    elif name in ('ttrealms:chomp', 'ttrealms:chomp_group'):
        suitTrack = doChomp(attack)
    elif name in ('ttrealms:cigar_smoke', 'ttrealms:cigar_smoke_group'):
        suitTrack = doCigarSmoke(attack)
    elif name in ('ttrealms:clip_on_tie', 'ttrealms:clip_on_tie_group'):
        suitTrack = doClipOnTie(attack)
    elif name == 'ttrealms:crunch':
        suitTrack = doCrunch(attack)
    elif name == 'ttrealms:demotion':
        suitTrack = doDemotion(attack)
    elif name == 'ttrealms:dormant_state':
        suitTrack = doDormantState(attack)
    elif name in ('ttrealms:double_talk', 'ttrealms:double_talk_group'):
        suitTrack = doDoubleTalk(attack)
    elif name in ('ttrealms:double_windsor', 'ttrealms:double_windsor_group', 'ttrealms:half_windsor', 'ttrealms:half_windsor_group'):
        suitTrack = doHalfWindsor(attack)
    elif name == 'ttrealms:downsize':
        suitTrack = doDownsize(attack)
    elif name in ('ttrealms:eviction_notice', 'ttrealms:eviction_notice_group'):
        suitTrack = doEvictionNotice(attack)
    elif name in ('ttrealms:evil_glare', 'ttrealms:evil_glare_group'):
        suitTrack = doEvilGlare(attack)
    elif name in ('ttrealms:evil_eye', 'ttrealms:evil_eye_group'):
        suitTrack = doEvilEye(attack)
    elif name == 'ttrealms:filibuster':
        suitTrack = doFilibuster(attack)
    elif name == 'ttrealms:fill_with_lead':
        suitTrack = doFillWithLead(attack)
    elif name == 'ttrealms:flex':
        suitTrack = doFlex(attack)
    elif name == 'ttrealms:finger_wag':
        suitTrack = doFingerWag(attack)
    elif name in ('ttrealms:fired', 'ttrealms:fired_group'):
        suitTrack = doFired(attack)
    elif name == 'ttrealms:five_o_clock_shadow':
        suitTrack = doDefault(attack)
    elif name == 'ttrealms:flood_the_market':
        suitTrack = doDefault(attack)
    elif name in ('ttrealms:fountain_pen', 'ttrealms:fountain_pen_group'):
        suitTrack = doFountainPen(attack)
    elif name in ('ttrealms:freeze_assets', 'ttrealms:freeze_assets_group'):
        suitTrack = doFreezeAssets(attack)
    elif name == 'ttrealms:frosty_reception':
        suitTrack = doFrostyReception(attack)
    elif name == 'ttrealms:gavel':
        suitTrack = doDefault(attack)
    elif name == 'ttrealms:glower_power':
        suitTrack = doGlowerPower(attack)
    elif name == 'ttrealms:guilt_trip':
        suitTrack = doGuiltTrip(attack)
    elif name in ('ttrealms:hang_up', 'ttrealms:hang_up_group'):
        suitTrack = doHangUp(attack)
    elif name == 'ttrealms:head_shrink':
        suitTrack = doHeadShrink(attack)
    elif name == 'ttrealms:heated_discussion':
        suitTrack = doHeatedDiscussion(attack)
    elif name == 'ttrealms:hot_air':
        suitTrack = doHotAir(attack)
    elif name == 'ttrealms:jargon':
        suitTrack = doJargon(attack)
    elif name == 'ttrealms:legalese':
        suitTrack = doLegalese(attack)
    elif name in ('ttrealms:liquidate', 'ttrealms:liquidate_group'):
        suitTrack = doLiquidate(attack)
    elif name in ('ttrealms:market_crash', 'ttrealms:market_crash_group'):
        suitTrack = doMarketCrash(attack)
    elif name == 'ttrealms:mumbo_jumbo':
        suitTrack = doMumboJumbo(attack)
    elif name == 'ttrealms:paradigm_shift':
        suitTrack = doParadigmShift(attack)
    elif name in ('ttrealms:pecking_order', 'ttrealms:pecking_order_group'):
        suitTrack = doPeckingOrder(attack)
    elif name == 'ttrealms:penny_pinch':
        suitTrack = doDefault(attack)
    elif name == 'ttrealms:pick_pocket':
        suitTrack = doPickPocket(attack)
    elif name in ('ttrealms:pink_slip', 'ttrealms:pink_slip_group'):
        suitTrack = doPinkSlip(attack)
    elif name in ('ttrealms:play_hardball', 'ttrealms:play_hardball_group'):
        suitTrack = doPlayHardball(attack)
    elif name == 'ttrealms:pound_key':
        suitTrack = doPoundKey(attack)
    elif name in ('ttrealms:power_tie', 'ttrealms:power_tie_group'):
        suitTrack = doPowerTie(attack)
    elif name == 'ttrealms:power_trip':
        suitTrack = doPowerTrip(attack)
    elif name == 'ttrealms:quake':
        suitTrack = doQuake(attack)
    elif name in ('ttrealms:razzle_dazzle', 'ttrealms:razzle_dazzle_group'):
        suitTrack = doRazzleDazzle(attack)
    elif name in ('ttrealms:red_tape', 'ttrealms:red_tape_group'):
        suitTrack = doRedTape(attack)
    elif name == 'ttrealms:re_org':
        suitTrack = doReOrg(attack)
    elif name in ('ttrealms:restraining_order', 'ttrealms:restraining_order_group'):
        suitTrack = doRestrainingOrder(attack)
    elif name == 'ttrealms:rolodex':
        suitTrack = doRolodex(attack)
    elif name in ('ttrealms:rubber_stamp', 'ttrealms:rubber_stamp_group'):
        suitTrack = doRubberStamp(attack)
    elif name in ('ttrealms:rub_out', 'ttrealms:rub_out_group'):
        suitTrack = doRubOut(attack)
    elif name == 'ttrealms:sacked':
        suitTrack = doSacked(attack)
    elif name == 'ttrealms:sand_trap':
        suitTrack = doDefault(attack)
    elif name == 'ttrealms:schmooze':
        suitTrack = doSchmooze(attack)
    elif name == 'ttrealms:shadow_toon':
        suitTrack = doShadowToon(attack)
    elif name == 'ttrealms:shake':
        suitTrack = doShake(attack)
    elif name == 'ttrealms:shred':
        suitTrack = doShred(attack)
    elif name == 'ttrealms:sneak_attack':
        suitTrack = doDefault(attack)
    elif name in ('ttrealms:snowball', 'ttrealms:snowball_group'):
        suitTrack = doSnowball(attack)
    elif name == 'ttrealms:song_and_dance':
        suitTrack = doDefault(attack)
    elif name == 'ttrealms:speed_dial':
        suitTrack = doDefault(attack)
    elif name == 'ttrealms:spin':
        suitTrack = doSpin(attack)
    elif name == 'ttrealms:synergy':
        suitTrack = doSynergy(attack)
    elif name in ('ttrealms:tee_off', 'ttrealms:tee_off_group'):
        suitTrack = doTeeOff(attack)
    elif name == 'ttrealms:throw_book':
        suitTrack = doDefault(attack)
    elif name == 'ttrealms:ticker_tape':
        suitTrack = doDefault(attack)
    elif name == 'ttrealms:tremor':
        suitTrack = doTremor(attack)
    elif name == 'ttrealms:watercooler':
        suitTrack = doWatercooler(attack)
    elif name in ('ttrealms:withdrawal', 'ttrealms:withdrawal_group'):
        suitTrack = doWithdrawal(attack)
    elif name in ('ttrealms:write_off', 'ttrealms:write_off_group'):
        suitTrack = doWriteOff(attack)
    elif name == 'ttrealms:burn':
        suitTrack = doBurn(attack)
    elif name == 'ttrealms:hail':
        suitTrack = doHail(attack)
    else:
        notify.warning('unknown attack: %s substituting Finger Wag' % name)
        suitTrack = doDefault(attack)
    camTrack = MovieCamera.chooseSuitShot(attack, suitTrack.getDuration())
    battle = attack['battle']
    target = attack['target']
    groupStatus = attack['group']
    toonHprTrack = Parallel()
    for t in target:
        toon = t['toon']
        if toon.getTransformationsIndex(0):
            neutralAnim = Func(toon.suit.loop, 'neutral')
        else:
            neutralAnim = Func(toon.loop, 'neutral')
        toonHprTrack.append(Sequence(Func(toon.headsUp, battle, MovieUtil.PNT3_ZERO), neutralAnim))

    if 'suit' in attack:
        suit = attack['suit']
        neutralIval = Func(suit.loop, 'neutral')
        suitTrack = Sequence(suitTrack, neutralIval, toonHprTrack)
        suitPos = suit.getPos(battle)
        resetPos, resetHpr = battle.getActorPosHpr(suit)
        if battle.isSuitLured(suit):
            resetTrack = getResetTrack(suit, battle)
            resetSuitTrack = Sequence(resetTrack, suitTrack)
            waitTrack = Sequence(Wait(resetTrack.getDuration()), Func(battle.unlureSuit, suit))
            resetCamTrack = Sequence(waitTrack, camTrack)
            return (resetSuitTrack, resetCamTrack)
    else:
        suitTrack = Sequence(suitTrack, toonHprTrack)
    return (suitTrack, camTrack)


def getResetTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=1e-05), Func(suit.loop, 'neutral'))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(walkTrack, moveTrack)


def __makeCancelledNodePath():
    tn = TextNode('CANCELLED')
    tn.setFont(getSuitFont())
    tn.setText(TTLocalizer.MovieSuitCancelled)
    tn.setAlign(TextNode.ACenter)
    tntop = hidden.attachNewNode('CancelledTop')
    tnpath = tntop.attachNewNode(tn)
    tnpath.setPosHpr(0, 0, 0, 0, 0, 0)
    tnpath.setScale(1)
    tnpath.setColor(0.7, 0, 0, 1)
    tnpathback = tnpath.instanceUnderNode(tntop, 'backside')
    tnpathback.setPosHpr(0, 0, 0, 180, 0, 0)
    tnpath.setScale(1)
    return tntop


def doDefault(attack):
    notify.debug('building suit attack in doDefault')
    suitName = attack['suitName']
    # TODO: eventually purge 'tbc' from here and make all cogs do finger wag if attack not specified
    #       need to update cog attributes first to allow random damage from glower power
    #       OR we implement "Flood The Market" and "Song and Dance" attacks
    if suitName == 'tbc':
        attack['identifier'] = 'ttrealms:glower_power'
        attack['animName'] = 'glower'
        return doGlowerPower(attack)
    else:
        attack['identifier'] = 'ttrealms:finger_wag'
        attack['animName'] = 'finger-wag'
        return doFingerWag(attack)


def getSuitTrack(attack, delay = 1e-06, splicedAnims = None):
    suit = attack['suit']
    battle = attack['battle']
    taunt = attack['taunt']
    targets = attack['target']
    # Get the average position of the Toon, similar to MovieUtil's getAvgSuitPos in the case this method is called on a group-target attack.
    avgToonPos = Point3(0.0, 0.0, 0.0)
    numTargets = len(targets)
    for i in range(numTargets):
        toon = targets[i]['toon']
        avgToonPos += toon.getPos(battle)

    avgToonPos /= numTargets
    targetPos = avgToonPos
    trapStorage = {}
    trapStorage['trap'] = None
    try:
        parent = attack['parent']
        track = Sequence(Wait(delay), Func(parent.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    except:
        track = Sequence(Wait(delay), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

    def reparentTrap(suit = suit, battle = battle, trapStorage = trapStorage):
        trapProp = suit.battleTrapProp
        if trapProp != None:
            trapProp.wrtReparentTo(battle)
            trapStorage['trap'] = trapProp

    track.append(Func(reparentTrap))
    track.append(Func(suit.headsUp, battle, targetPos))
    if splicedAnims:
        track.append(getSplicedAnimsTrack(splicedAnims, actor=suit))
    else:
        track.append(ActorInterval(suit, attack['animName']))
    origPos, origHpr = battle.getActorPosHpr(suit)
    track.append(Func(suit.setHpr, battle, origHpr))

    def returnTrapToSuit(suit = suit, trapStorage = trapStorage):
        trapProp = trapStorage['trap']
        if trapProp != None:
            if trapProp.getName() == 'traintrack':
                notify.debug('deliberately not parenting traintrack to suit')
            else:
                trapProp.wrtReparentTo(suit)
            suit.battleTrapProp = trapProp
        return

    track.append(Func(returnTrapToSuit))
    track.append(Func(suit.clearChat))
    return track


def getSuitAnimTrack(attack, delay = 0.0, splicedAnims = None):
    suit = attack['suit']
    taunt = attack['taunt']
    track = Sequence(Wait(delay), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    if splicedAnims:
        track.append(getSplicedAnimsTrack(splicedAnims, actor=suit))
    else:
        track.append(ActorInterval(suit, attack['animName']))
    track.append(suit.clearChat)
    return track


def getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs):
    particleEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) > 2:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(particleEffect, parent, worldRelative, duration=durationDelay, cleanup=True))


def hitAtleastOneToon(targets: List[dict]) -> bool:
    for t in targets:
        if t['hp'] > 0:
            return True

    return False


def getToonTrack(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5, flexOnEx = 0, prop = None):
    if not target:
        target = attack['target'][0]
    toon = target['toon']
    battle = attack['battle']
    animTrack = Sequence()
    if 'suit' in attack:
        suit = attack['suit']
        suitPos = suit.getPos(battle)
        animTrack.append(Func(toon.headsUp, battle, suitPos))
    dmg = target['hp']
    status = target.get('status', None)
    if dmg > 0:
        if flexOnEx == 1:
            animTrack.append(
                getToonTakeDamageTrack(toon, target['died'], dmg, status, damageDelay, damageAnimNames, splicedDamageAnims,
                                       showDamageExtraTime, battle, prop))
        else:
            animTrack.append(
                getToonTakeDamageTrack(toon, target['died'], dmg, status, damageDelay, damageAnimNames, splicedDamageAnims,
                                       showDamageExtraTime))
    else:
        animTrack.append(getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
    return animTrack


def getToonTracks(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 1e-06, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    toonTracks = Parallel()
    targets = attack['target']
    for i in range(len(targets)):
        tgt = targets[i]
        toonTracks.append(getToonTrack(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, target=tgt, showDamageExtraTime=showDamageExtraTime, showMissedExtraTime=showMissedExtraTime))

    return toonTracks


def getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime):
    toon = target['toon']
    toonTrack = Sequence()
    toonTrack.append(Wait(dodgeDelay))
    if dodgeAnimNames:
        for d in dodgeAnimNames:
            if d == 'sidestep':
                toonTrack.append(getAllyToonsDodgeParallel(target))
            elif d == 'jump' and toon.getTransformationsIndex(0):
                if toon.suit.getBodyType() == 'a':
                    toonTrack.append(ActorInterval(toon.suit, 'slip-forward', startFrame=55))
                elif toon.suit.getBodyType() == 'b':
                    toonTrack.append(Sequence(ActorInterval(toon.suit, 'quick-jump', playRate=5, endFrame=15),
                                                     ActorInterval(toon.suit, 'quick-jump', startFrame=15, endFrame=30),
                                                     ActorInterval(toon.suit, 'quick-jump', startFrame=107)))
                elif toon.suit.getBodyType() == 'c':
                    toonTrack.append(ActorInterval(toon.suit, 'slip-forward', startFrame=59))
            else:
                toonTrack.append(ActorInterval(toon, d))

    else:
        toonTrack.append(getSplicedAnimsTrack(splicedDodgeAnims, actor=toon))
    if toon.getTransformationsIndex(0):
        toonTrack.append(Func(toon.suit.loop, 'neutral'))
    else:
        toonTrack.append(Func(toon.loop, 'neutral'))
    indicatorTrack = Sequence(Wait(dodgeDelay + showMissedExtraTime), Func(MovieUtil.indicateMissed, toon))
    return Parallel(toonTrack, indicatorTrack)


def getAllyToonsDodgeParallel(target):
    toon = target['toon']
    leftToons = target['leftToons']
    rightToons = target['rightToons']
    if len(leftToons) > len(rightToons):
        PoLR = rightToons
        PoMR = leftToons
    else:
        PoLR = leftToons
        PoMR = rightToons
    upper = 1 + 4 * abs(len(leftToons) - len(rightToons))
    if random.randint(0, upper) > 0:
        toonDodgeList = PoLR
    else:
        toonDodgeList = PoMR
    if toonDodgeList is leftToons:
        sidestepAnim = 'sidestep-left'
        soundEffect = globalBattleSoundCache.getSound('AV_side_step.ogg')
    else:
        sidestepAnim = 'sidestep-right'
        soundEffect = globalBattleSoundCache.getSound('AV_jump_to_side.ogg')
    toonTracks = Parallel()
    for t in toonDodgeList:
        if t.getTransformationsIndex(0):
            toonTracks.append(Sequence(ActorInterval(t.suit, sidestepAnim), Func(t.suit.loop, 'neutral')))
        else:
            toonTracks.append(Sequence(ActorInterval(t, sidestepAnim), Func(t.loop, 'neutral')))

    if toon.getTransformationsIndex(0):
        toonTracks.append(Sequence(ActorInterval(toon.suit, sidestepAnim), Func(toon.suit.loop, 'neutral')))
    else:
        toonTracks.append(Sequence(ActorInterval(toon, sidestepAnim), Func(toon.loop, 'neutral')))
    toonTracks.append(Sequence(Wait(0.5), SoundInterval(soundEffect, node=toon)))
    return toonTracks


def getPropTrack(prop, parent, posPoints, appearDelay, remainDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, scaleDownTime = 0.5, startScale = Point3(0.01), anim = 0, propName = 'none', animDuration = 0.0, animStartTime = 0.0):
    if anim == 1:
        track = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints), LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale), ActorInterval(prop, propName, duration=animDuration, startTime=animStartTime), Wait(remainDelay), Func(MovieUtil.removeProp, prop))
    else:
        track = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints), LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale), Wait(remainDelay), LerpScaleInterval(prop, scaleDownTime, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProp, prop))
    return track


def getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, startScale = Point3(0.01), poseExtraArgs = None):
    propTrack = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints))
    if poseExtraArgs:
        propTrack.append(Func(prop.pose, *poseExtraArgs))
    propTrack.append(LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale))
    return propTrack


def getPropThrowTrack(attack, prop, hitPoints = [], missPoints = [], hitDuration = 0.5, missDuration = 0.5, hitPointNames = 'none', missPointNames = 'none', lookAt = 'none', groundPointOffSet = 0, missScaleDown = None, parent = render, target = None):
    if not target:
        target = attack['target'][0]
    toon = target['toon']
    dmg = target['hp']
    battle = attack['battle']

    def getLambdas(list, prop, toon):
        for i in range(len(list)):
            if list[i] == 'face':
                list[i] = lambda toon = toon: __toonFacePoint(toon)
            elif list[i] == 'miss':
                list[i] = lambda prop = prop, toon = toon: __toonMissPoint(prop, toon)
            elif list[i] == 'bounceHit':
                list[i] = lambda prop = prop, toon = toon: __throwBounceHitPoint(prop, toon)
            elif list[i] == 'bounceMiss':
                list[i] = lambda prop = prop, toon = toon: __throwBounceMissPoint(prop, toon)

        return list

    if hitPointNames != 'none':
        hitPoints = getLambdas(hitPointNames, prop, toon)
    if missPointNames != 'none':
        missPoints = getLambdas(missPointNames, prop, toon)
    propTrack = Sequence()
    propTrack.append(Func(battle.movie.needRestoreRenderProp, prop))
    propTrack.append(Func(prop.wrtReparentTo, parent))
    if lookAt != 'none':
        propTrack.append(Func(prop.lookAt, lookAt))
    if dmg > 0:
        for i in range(len(hitPoints)):
            pos = hitPoints[i]
            propTrack.append(LerpPosInterval(prop, hitDuration, pos=pos))

    else:
        for i in range(len(missPoints)):
            pos = missPoints[i]
            propTrack.append(LerpPosInterval(prop, missDuration, pos=pos))

        if missScaleDown:
            propTrack.append(LerpScaleInterval(prop, missScaleDown, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProp, prop))
    propTrack.append(Func(battle.movie.clearRenderProp, prop))
    return propTrack


def getThrowTrack(object, target, duration = 1.0, parent = render, gravity = -32.144):
    values = {}

    def calcOriginAndVelocity(object = object, target = target, values = values, duration = duration, parent = parent, gravity = gravity):
        if callable(target):
            target = target()
        object.wrtReparentTo(parent)
        values['origin'] = object.getPos(parent)
        origin = object.getPos(parent)
        values['velocity'] = (target[2] - origin[2] - 0.5 * gravity * duration * duration) / duration

    return Sequence(Func(calcOriginAndVelocity), LerpFunctionInterval(throwPos, fromData=0.0, toData=1.0, duration=duration, extraArgs=[object,
     duration,
     target,
     values,
     gravity]))


def throwPos(t, object, duration, target, values, gravity = -32.144):
    origin = values['origin']
    velocity = values['velocity']
    if callable(target):
        target = target()
    x = origin[0] * (1 - t) + target[0] * t
    y = origin[1] * (1 - t) + target[1] * t
    time = t * duration
    z = origin[2] + velocity * time + 0.5 * gravity * time * time
    object.setPos(x, y, z)


def getToonTakeDamageTrack(toon, died, dmg, status: str, delay, damageAnimNames = None, splicedDamageAnims = None, showDamageExtraTime = 0.01, battle=None, prop=None, hideDmg=False):
    toonTrack = Sequence()
    toonTrack.append(Wait(delay))
    if damageAnimNames:
        for d in damageAnimNames:
            if toon.getTransformationsIndex(0):
                if d == 'conked':
                    toonTrack.append(ActorInterval(toon.suit, 'squirt-small-react'))
                elif d.startswith('slip'):
                    toonTrack.append(ActorInterval(toon.suit, d))
                elif d == 'jump':
                    if toon.suit.getBodyType() == 'a':
                        toonTrack.append(ActorInterval(toon.suit, 'slip-forward', startFrame=55))
                    elif toon.suit.getBodyType() == 'b':
                        toonTrack.append(Sequence(ActorInterval(toon.suit, 'quick-jump', playRate=5, endFrame=15),
                                                  ActorInterval(toon.suit, 'quick-jump', startFrame=15, endFrame=30),
                                                  ActorInterval(toon.suit, 'quick-jump', startFrame=107)))
                    elif toon.suit.getBodyType() == 'c':
                        toonTrack.append(ActorInterval(toon.suit, 'slip-forward', startFrame=59))
                elif d == 'suitQuicksandAnim':
                    sinkPos1 = toon.getPos()
                    sinkPos2 = toon.getPos()
                    dropPos = toon.getPos()
                    landPos = toon.getPos()
                    sinkPos1.setZ(sinkPos1.getZ() - 3.1)
                    sinkPos2.setZ(sinkPos2.getZ() - 9.1)
                    dropPos.setZ(dropPos.getZ() + 15)
                    moveTrack = Sequence(Wait(0.9), LerpPosInterval(toon, 0.9, sinkPos1),
                                         LerpPosInterval(toon, 0.4, sinkPos2),
                                         Func(toon.setPos, dropPos), Func(toon.wrtReparentTo, hidden),
                                         Wait(1.1), Func(toon.wrtReparentTo, render),
                                         LerpPosInterval(toon, 0.3, landPos))
                    animTrack = Sequence(ActorInterval(toon.suit, 'flail'),
                                         ActorInterval(toon.suit, 'flail', startTime=1.1), Wait(0.7),
                                         ActorInterval(toon.suit, 'slip-forward', duration=2.1))
                    toonTrack.append(Parallel(moveTrack, animTrack))
                else:
                    toonTrack.append(ActorInterval(toon.suit, 'pie-small-react'))
            else:
                toonTrack.append(ActorInterval(toon, d))
        if hideDmg:
            indicatorTrack = Sequence(Wait(delay + showDamageExtraTime))
        else:
            indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamage, toon, dmg, died))
            if status is not None:
                indicatorTrack.append(Func(__doStatus, toon, status))
    else:
        if toon.getTransformationsIndex(0):
            splicedAnims = getSplicedAnimsTrack(splicedDamageAnims, flexex=1, actor=toon.suit)
        else:
            splicedAnims = getSplicedAnimsTrack(splicedDamageAnims, actor=toon)
        toonTrack.append(splicedAnims)
        if hideDmg:
            indicatorTrack = Sequence(Wait(delay + showDamageExtraTime))
        else:
            indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamage, toon, dmg, died))
            if status is not None:
                indicatorTrack.append(Func(__doStatus, toon, status))
    toonTrack.append(Func(toon.loop, 'neutral'))
    if died:
        toonTrack.append(Wait(5.0))
    return Parallel(toonTrack, indicatorTrack)


def getSplicedAnimsTrack(anims, flexex = 0, actor = None):
    track = Sequence()
    for nextAnim in anims:
        delay = 1e-06
        if flexex == 1:
            if nextAnim[0] == 'conked':
                nextAnim[0] = 'squirt-small-react'
            elif nextAnim[0].startswith('slip'):
                pass
            elif nextAnim[0] == 'melt':
                nextAnim[0] = 'flail'
            else:
                nextAnim[0] = 'pie-small-react'
        if len(nextAnim) >= 2:
            if nextAnim[1] > 0:
                delay = nextAnim[1]
        if len(nextAnim) <= 0:
            track.append(Wait(delay))
        elif len(nextAnim) == 1:
            track.append(ActorInterval(actor, nextAnim[0]))
        elif len(nextAnim) == 2:
            track.append(Wait(delay))
            track.append(ActorInterval(actor, nextAnim[0]))
        elif len(nextAnim) == 3:
            track.append(Wait(delay))
            track.append(ActorInterval(actor, nextAnim[0], startTime=nextAnim[2]))
        elif len(nextAnim) == 4:
            track.append(Wait(delay))
            duration = nextAnim[3]
            if duration < 0:
                startTime = nextAnim[2]
                endTime = startTime + duration
                if endTime <= 0:
                    endTime = 0.01
                track.append(ActorInterval(actor, nextAnim[0], startTime=startTime, endTime=endTime))
            else:
                track.append(ActorInterval(actor, nextAnim[0], startTime=nextAnim[2], duration=duration))
        elif len(nextAnim) == 5:
            track.append(Wait(delay))
            track.append(ActorInterval(nextAnim[4], nextAnim[0], startTime=nextAnim[2], duration=nextAnim[3]))

    return track


def getSplicedLerpAnims(animName, origDuration, newDuration, startTime = 0, fps = 30, reverse = 0):
    anims = []
    addition = 0
    numAnims = origDuration * fps
    timeInterval = newDuration / numAnims
    animInterval = origDuration / numAnims
    if reverse == 1:
        animInterval = -animInterval
    for i in range(0, int(numAnims)):
        anims.append([animName,
         timeInterval,
         startTime + addition,
         animInterval])
        addition += animInterval

    return anims


def getSoundTrack(fileName, delay = 0.01, duration = 0.0, node = None):
    soundEffect = globalBattleSoundCache.getSound(fileName)
    return Sequence(Wait(delay), SoundInterval(soundEffect, duration=duration, node=node))


def getColorTrack(battle, toon, delay, duration, color):
    '''
    Create a convenient track for coloring a Toon's entire body.
    NOTE: Only compatible with immediate color switches; currently not compatible with Cigar Smoke's lerp-ing color switch.

    Parameters:
        battle: The battle.  This is to toggle the needRestoreColor flag.
        toon: The Toon whose color will change.
        delay (float): How long before the Toon's color changes.
        duration (float): How long the color remains before being removed.
        color (Vec4): The color to change the Toon to.

    Returns:
        out (Sequence): The assembled sequence for changing the Toon's color.
    '''

    def changeColor(parts):
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            nextPart.setColorScale(color)


    def resetColor(parts):
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            nextPart.clearColorScale()

    headParts = toon.getHeadParts()
    torsoParts = toon.getTorsoParts()
    legsParts = toon.getLegsParts()
    return Sequence(
        Wait(delay),
        Func(battle.movie.needRestoreColor),
        Func(changeColor, headParts),
        Func(changeColor, torsoParts),
        Func(changeColor, legsParts),
        Wait(duration),
        Func(resetColor, headParts),
        Func(resetColor, torsoParts),
        Func(resetColor, legsParts),
        Func(battle.movie.clearRestoreColor)
    )


def doClipOnTie(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        throwDelay = 2.17
        damageDelay = 3.3
        dodgeDelay = 3.1
    elif suitType == 'b':
        throwDelay = 2.17
        damageDelay = 3.3
        dodgeDelay = 3.1
    elif suitType == 'c':
        throwDelay = 1.45
        damageDelay = 2.61
        dodgeDelay = 2.34
    suitTrack = getSuitTrack(attack)
    tiePropTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tie = globalPropPool.getProp('clip-on-tie')
        posPoints = [Point3(0.66, 0.51, 0.28), VBase3(-69.652, -17.199, 67.96)]
        tiePropTrack = Sequence(getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, MovieUtil.PNT3_ONE, scaleUpTime=0.5, poseExtraArgs=['clip-on-tie', 0]))
        if dmg > 0:
            tiePropTrack.append(ActorInterval(tie, 'clip-on-tie', duration=throwDelay, startTime=1.1))
        else:
            tiePropTrack.append(Wait(throwDelay))
        tiePropTrack.append(Func(tie.setHpr, Point3(0, -90, 0)))
        tiePropTrack.append(getPropThrowTrack(attack, tie, [__toonFacePoint(toon)], [__toonGroundPoint(attack, toon, 0.1)], hitDuration=0.4, missDuration=0.8, missScaleDown=1.2, target=t))
        tiePropTracks += (tiePropTrack,)

    toonTracks = getToonTracks(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    throwSound = getSoundTrack('SA_powertie_throw.ogg', delay=throwDelay + 1, node=suit)
    return Parallel(suitTrack, toonTracks, *tiePropTracks, throwSound)


def getPhoneTrack(suit, propDelay = 0.3):
    '''
    Create a convenient phone prop track method for use with multiple phone tracks (like Pound Key and Hang Up).

    Parameters:
        suit: The Cog that will be using the phone.
        propDelay (float): The time before the phone appears.
    
    Returns:
        out (Parallel): The created phone track with included sound track.
    '''
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    suitType = getSuitBodyType(suit.getStyleName())
    if suitType == 'a':
        phonePosPoints = [Point3(-0.23, 0.01, -0.26), VBase3(5.939, 2.763, -177.591)]
        receiverPosPoints = [Point3(-0.13, -0.07, -0.06), VBase3(-1.854, 2.434, -177.579)]
        receiverAdjustScale = Point3(0.8, 0.8, 0.8)
        pickupDelay = 0.44
        dialDuration = 3.07
        finalPhoneDelay = 0.01
        scaleUpPoint = Point3(0.75, 0.75, 0.75)
    elif suitType == 'b':
        phonePosPoints = [Point3(0.23, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]
        receiverPosPoints = [Point3(0.23, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]
        receiverAdjustScale = MovieUtil.PNT3_ONE
        pickupDelay = 0.74
        dialDuration = 3.07
        finalPhoneDelay = 0.69
        scaleUpPoint = MovieUtil.PNT3_ONE
    else:
        phonePosPoints = [Point3(0.23, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]
        receiverPosPoints = [Point3(0.23, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]
        pickupDelay = 0.74
        dialDuration = 3.14
        finalPhoneDelay = 0.62
        scaleUpPoint = MovieUtil.PNT3_ONE
    propTrack = Sequence(Wait(propDelay), Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]), Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]), LerpScaleInterval(phone, 0.5, scaleUpPoint, MovieUtil.PNT3_NEARZERO), Wait(pickupDelay), Func(receiver.wrtReparentTo, suit.getRightHand()))
    if suitType in ('a', 'b'):
        propTrack.append(LerpScaleInterval(receiver, 0.01, receiverAdjustScale))
        propTrack.append(LerpPosHprInterval(receiver, 0.0001, Point3(-0.53, 0.21, -0.54), VBase3(-99.49, -35.27, 1.84)))
    else:
        propTrack.append(LerpPosHprInterval(receiver, 0.0001, Point3(-0.45, 0.48, -0.62), VBase3(-87.47, -18.21, 7.82)))
    propTrack.append(Wait(dialDuration))
    propTrack.append(Func(receiver.wrtReparentTo, phone))
    propTrack.append(Wait(finalPhoneDelay))
    propTrack.append(LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProps, [receiver, phone]))
    return Parallel(propTrack, getSoundTrack('SA_hangup.ogg', delay=propDelay + 1.0, node=suit))


def doPoundKey(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('PoundKey')
    BattleParticles.setEffectTexture(particleEffect, 'poundsign', color=Vec4(0, 0, 0, 1))
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, 2.1, 1.55, [particleEffect, suit, 0])
    propTrack = getPhoneTrack(suit)
    toonTrack = getToonTrack(attack, 2.7, ['cringe'], 1.9, ['sidestep'])
    return Parallel(suitTrack, toonTrack, propTrack, partTrack)


def doShred(attack):
    suit = attack['suit']
    battle = attack['battle']
    paper = globalPropPool.getProp('shredder-paper')
    shredder = globalPropPool.getProp('shredder')
    particleEffect = BattleParticles.createParticleEffect('Shred')
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, 3.5, 1.9, [particleEffect, suit, 0])
    paperPosPoints = [Point3(0.59, -0.31, 0.81), VBase3(79.224, 32.576, -179.449)]
    paperPropTrack = getPropTrack(paper, suit.getRightHand(), paperPosPoints, 2.4, 1e-05, scaleUpTime=0.2, anim=1, propName='shredder-paper', animDuration=1.5, animStartTime=2.8)
    shredderPosPoints = [Point3(0, -0.12, -0.34), VBase3(-90.0, -53.77, -0.0)]
    shredderPropTrack = getPropTrack(shredder, suit.getLeftHand(), shredderPosPoints, 1, 3, scaleUpPoint=Point3(4.81, 4.81, 4.81))
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - 1.1, ['conked'], suitTrack.getDuration() - 3.1, ['sidestep'])
    soundTrack = getSoundTrack('SA_shred.ogg', delay=3.4, node=suit)
    return Parallel(suitTrack, paperPropTrack, shredderPropTrack, partTrack, toonTrack, soundTrack)


def doFillWithLead(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    pencil = globalPropPool.getProp('pencil')
    sharpener = globalPropPool.getProp('sharpener')
    BattleParticles.loadParticles()
    sprayEffect = BattleParticles.createParticleEffect(file='fillWithLeadSpray')
    headSmotherEffect = BattleParticles.createParticleEffect(file='fillWithLeadSmother')
    torsoSmotherEffect = BattleParticles.createParticleEffect(file='fillWithLeadSmother')
    legsSmotherEffect = BattleParticles.createParticleEffect(file='fillWithLeadSmother')
    BattleParticles.setEffectTexture(sprayEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
    BattleParticles.setEffectTexture(headSmotherEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
    BattleParticles.setEffectTexture(torsoSmotherEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
    BattleParticles.setEffectTexture(legsSmotherEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, 2.5, 1.9, [sprayEffect, suit, 0])
    pencilPosPoints = [Point3(-0.29, -0.33, -0.13), VBase3(160.565, -11.653, -169.244)]
    pencilPropTrack = getPropTrack(pencil, suit.getRightHand(), pencilPosPoints, 0.7, 3.2, scaleUpTime=0.2)
    sharpenerPosPoints = [Point3(0.0, 0.0, -0.03), MovieUtil.PNT3_ZERO]
    sharpenerPropTrack = getPropTrack(sharpener, suit.getLeftHand(), sharpenerPosPoints, 1.3, 2.3, scaleUpPoint=MovieUtil.PNT3_ONE)
    damageAnims = []
    damageAnims.append(['conked',
     suitTrack.getDuration() - 1.5,
     1e-05,
     1.4])
    damageAnims.append(['conked',
     1e-05,
     0.7,
     0.7])
    damageAnims.append(['conked',
     1e-05,
     0.7,
     0.7])
    damageAnims.append(['conked', 1e-05, 1.4])
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, dodgeDelay=suitTrack.getDuration() - 3.1, dodgeAnimNames=['sidestep'], showDamageExtraTime=4.5, showMissedExtraTime=1.6)
    animal = toon.style.getAnimal()
    bodyScale = ToontownGlobals.toonBodyScales[animal]
    headEffectHeight = __toonFacePoint(toon).getZ()
    legsHeight = ToontownGlobals.legHeightDict[toon.style.legs] * bodyScale
    torsoEffectHeight = ToontownGlobals.torsoHeightDict[toon.style.torso] * bodyScale / 2 + legsHeight
    legsEffectHeight = legsHeight / 2
    effectX = headSmotherEffect.getX()
    effectY = headSmotherEffect.getY()
    headSmotherEffect.setPos(effectX, effectY - 1.5, headEffectHeight)
    torsoSmotherEffect.setPos(effectX, effectY - 1, torsoEffectHeight)
    legsSmotherEffect.setPos(effectX, effectY - 0.6, legsEffectHeight)
    partDelay = 3.5
    partIvalDelay = 0.7
    partDuration = 1.0
    headTrack = getPartTrack(headSmotherEffect, partDelay, partDuration, [headSmotherEffect, toon, 0])
    torsoTrack = getPartTrack(torsoSmotherEffect, partDelay + partIvalDelay, partDuration, [torsoSmotherEffect, toon, 0])
    legsTrack = getPartTrack(legsSmotherEffect, partDelay + partIvalDelay * 2, partDuration, [legsSmotherEffect, toon, 0])

    def colorParts(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

        return track

    def resetParts(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    if dmg > 0:
        colorTrack = Sequence()
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack.append(Wait(partDelay + 0.2))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(colorParts(headParts))
        colorTrack.append(Wait(partIvalDelay))
        colorTrack.append(colorParts(torsoParts))
        colorTrack.append(Wait(partIvalDelay))
        colorTrack.append(colorParts(legsParts))
        colorTrack.append(Wait(2.5))
        colorTrack.append(resetParts(headParts))
        colorTrack.append(resetParts(torsoParts))
        colorTrack.append(resetParts(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
        return Parallel(suitTrack, pencilPropTrack, sharpenerPropTrack, sprayTrack, headTrack, torsoTrack, legsTrack, colorTrack, toonTrack)
    else:
        return Parallel(suitTrack, pencilPropTrack, sharpenerPropTrack, sprayTrack, toonTrack)


def doFountainPen(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    pen = globalPropPool.getProp('pen')

    def getPenTip(pen = pen):
        tip = pen.find('**/joint_toSpray')
        return tip.getPos(render)

    suitTrack = getSuitTrack(attack)
    propTrack = Sequence(Wait(0.01), Func(__showProp, pen, suit.getRightHand(), MovieUtil.PNT3_ZERO), LerpScaleInterval(pen, 0.5, Point3(1.5, 1.5, 1.5)), Wait(1.05))
    sprayTracks = Parallel()
    for t in targets:
        toon = t['toon']
        hitPoint = lambda toon = toon: __toonFacePoint(toon)
        missPoint = lambda prop = pen, toon = toon: __toonMissPoint(prop, toon, 0, parent=render)
        sprayTrack = MovieUtil.getSprayTrack(battle, VBase4(0, 0, 0, 1), getPenTip, hitPoint if t['hp'] > 0 else missPoint, 0.2, 0.2, 0.2, horizScale=0.1, vertScale=0.1)
        sprayTracks.append(sprayTrack)

    propTrack.append(sprayTracks)
    propTrack += [LerpScaleInterval(pen, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProp, pen)]
    splashTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            splashTrack = Sequence()
        
            def prepSplash(splash, targetPoint):
                splash.reparentTo(render)
                splash.setPos(targetPoint)
                scale = splash.getScale()
                splash.setBillboardPointWorld()
                splash.setScale(scale)
        
            splash = globalPropPool.getProp('splash-from-splat')
            splash.setColor(0, 0, 0, 1)
            splash.setScale(0.15)
            splashTrack = Sequence(Func(battle.movie.needRestoreRenderProp, splash), Wait(1.65), Func(prepSplash, splash, __toonFacePoint(toon)), ActorInterval(splash, 'splash-from-splat'), Func(MovieUtil.removeProp, splash), Func(battle.movie.clearRenderProp, splash))
            headParts = toon.getHeadParts()
            splashTrack.append(Func(battle.movie.needRestoreColor))
            for partNum in range(0, headParts.getNumPaths()):
                nextPart = headParts.getPath(partNum)
                splashTrack.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))
        
            splashTrack.append(Func(MovieUtil.removeProp, splash))
            splashTrack.append(Wait(2.6))
            for partNum in range(0, headParts.getNumPaths()):
                nextPart = headParts.getPath(partNum)
                splashTrack.append(Func(nextPart.clearColorScale))
        
            splashTrack.append(Func(battle.movie.clearRestoreColor))
            splashTracks += (splashTrack,)

    penSpill = BattleParticles.createParticleEffect(file='penSpill')
    penSpill.setPos(getPenTip())
    penSpillTrack = getPartTrack(penSpill, 1.4, 0.7, [penSpill, pen, 0])
    toonTracks = getToonTracks(attack, 1.81, ['conked'], dodgeDelay=0.11, splicedDodgeAnims=[['duck', 0.01, 0.6]], showMissedExtraTime=1.66)
    soundTrack = getSoundTrack('SA_fountain_pen.ogg', delay=1.6, node=suit)
    return Parallel(suitTrack, toonTracks, propTrack, soundTrack, penSpillTrack, *splashTracks)


def doRubOut(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    pad = globalPropPool.getProp('pad')
    pencil = globalPropPool.getProp('pencil')
    suitTrack = getSuitTrack(attack)
    padPosPoints = [Point3(-0.66, 0.81, -0.06), VBase3(14.93, -2.29, 180.0)]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 0.5, 2.57)
    pencilPosPoints = [Point3(0.04, -0.38, -0.1), VBase3(-170.223, -3.762, -62.929)]
    pencilPropTrack = getPropTrack(pencil, suit.getRightHand(), pencilPosPoints, 0.5, 2.57)
    hideTracks = ()

    def hideParts(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setTransparency, 1))
            track.append(LerpFunctionInterval(nextPart.setAlphaScale, fromData=1, toData=0, duration=0.2))

        return track

    def showParts(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))
            track.append(Func(nextPart.clearTransparency))

        return track

    partTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        headEffect = BattleParticles.createParticleEffect('RubOut', color=toon.style.getHeadColor())
        torsoEffect = BattleParticles.createParticleEffect('RubOut', color=toon.style.getArmColor())
        legsEffect = BattleParticles.createParticleEffect('RubOut', color=toon.style.getLegColor())
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        animal = toon.style.getAnimal()
        bodyScale = ToontownGlobals.toonBodyScales[animal]
        headEffectHeight = __toonFacePoint(toon).getZ()
        legsHeight = ToontownGlobals.legHeightDict[toon.style.legs] * bodyScale
        torsoEffectHeight = ToontownGlobals.torsoHeightDict[toon.style.torso] * bodyScale / 2 + legsHeight
        legsEffectHeight = legsHeight / 2
        effectX = headEffect.getX()
        effectY = headEffect.getY()
        headEffect.setPos(effectX, effectY - 1.5, headEffectHeight)
        torsoEffect.setPos(effectX, effectY - 1, torsoEffectHeight)
        legsEffect.setPos(effectX, effectY - 0.6, legsEffectHeight)
        partDelay = 2.5
        headTrack = getPartTrack(headEffect, partDelay + 0, 0.5, [headEffect, toon, 0])
        torsoTrack = getPartTrack(torsoEffect, partDelay + 1.1, 0.5, [torsoEffect, toon, 0])
        legsTrack = getPartTrack(legsEffect, partDelay + 2.2, 0.5, [legsEffect, toon, 0])
        partTracks += (headTrack, torsoTrack, legsTrack)
        if dmg > 0:
            hideTrack = Sequence()
            hideTrack.append(Wait(2.2))
            hideTrack.append(Func(battle.movie.needRestoreColor))
            hideTrack.append(hideParts(headParts))
            hideTrack.append(Wait(0.4))
            hideTrack.append(hideParts(torsoParts))
            hideTrack.append(Wait(0.4))
            hideTrack.append(hideParts(legsParts))
            hideTrack.append(Wait(1))
            hideTrack.append(showParts(headParts))
            hideTrack.append(showParts(torsoParts))
            hideTrack.append(showParts(legsParts))
            hideTrack.append(Func(battle.movie.clearRestoreColor))
            hideTracks += (hideTrack,)

    toonTracks = getToonTracks(attack, 2.2, ['conked'], 2.0, ['jump'])
    soundTrack = getSoundTrack('SA_rubout.ogg', delay=1.7, node=suit)
    return Parallel(suitTrack, toonTracks, padPropTrack, pencilPropTrack, soundTrack, *hideTracks, *partTracks)


def doFingerWag(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('FingerWag')
    BattleParticles.setEffectTexture(particleEffect, 'blah', color=Vec4(0.55, 0, 0.55, 1))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 1.3
        damageDelay = 2.7
        dodgeDelay = 1.7
    elif suitType == 'b':
        partDelay = 1.3
        damageDelay = 2.7
        dodgeDelay = 1.8
    elif suitType == 'c':
        partDelay = 1.3
        damageDelay = 2.7
        dodgeDelay = 2.0
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, partDelay, 2, [particleEffect, suit, 0])
    suitName = attack['suitName']
    if suitName == 'mm':
        particleEffect.setPos(0.167, 1.5, 2.731)
    elif suitName == 'tw':
        particleEffect.setPos(0.167, 1.8, 5)
        particleEffect.setHpr(-90.0, -60.0, 180.0)
    elif suitName == 'pp':
        particleEffect.setPos(0.167, 1, 4.1)
    elif suitName == 'bs':
        particleEffect.setPos(0.167, 1, 5.1)
    elif suitName == 'bw':
        particleEffect.setPos(0.167, 1.9, suit.getHeight() - 1.8)
        particleEffect.setP(-110)
    toonTrack = getToonTrack(attack, damageDelay, ['slip-backward'], dodgeDelay, ['sidestep'])
    soundTrack = getSoundTrack('SA_finger_wag.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTrack, partTrack, soundTrack)


def doWriteOff(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    pad = globalPropPool.getProp('pad')
    pencil = globalPropPool.getProp('pencil')
    BattleParticles.loadParticles()
    suitTrack = getSuitTrack(attack)
    padPosPoints = [Point3(-0.25, 1.38, -0.08), VBase3(-19.078, -6.603, -171.594)]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 0.5, 2.57, Point3(1.89, 1.89, 1.89))
    pencilPosPoints = [Point3(-0.47, 1.08, 0.28), VBase3(21.045, 12.702, -176.374)]
    extraArgsForShowProp = [pencil, suit.getRightHand()]
    extraArgsForShowProp.extend(pencilPosPoints)
    pencilPropTrack = Sequence(Wait(0.5), Func(__showProp, *extraArgsForShowProp), LerpScaleInterval(pencil, 0.5, Point3(1.5, 1.5, 1.5), startScale=Point3(0.01)), Wait(2))
    partTracks = Parallel()
    for t in targets:
        toon = t['toon']
        checkmark = MovieUtil.copyProp(BattleParticles.getParticle('checkmark'))
        checkmark.setBillboardPointEye()
        missPoint = lambda checkmark = checkmark, toon = toon: __toonMissPoint(checkmark, toon)
        partTrack = Sequence(Func(battle.movie.needRestoreRenderProp, checkmark), Func(checkmark.reparentTo, render), Func(checkmark.setScale, 1.6), Func(checkmark.setPosHpr, pencil, 0, 0, 0, 0, 0, 0), Func(checkmark.setP, 0), Func(checkmark.setR, 0), getPropThrowTrack(attack, checkmark, [__toonFacePoint(toon)], [missPoint], target=t), Func(MovieUtil.removeProp, checkmark), Func(battle.movie.clearRenderProp, checkmark))
        partTracks.append(partTrack)

    pencilPropTrack.append(partTracks)
    pencilPropTrack.append(Wait(0.3))
    pencilPropTrack.append(LerpScaleInterval(pencil, 0.5, MovieUtil.PNT3_NEARZERO))
    pencilPropTrack.append(Func(MovieUtil.removeProp, pencil))
    toonTracks = getToonTracks(attack, 3.4, ['slip-forward'], 2.4, ['sidestep'])
    soundTrack = Sequence(Wait(2.3), SoundInterval(globalBattleSoundCache.getSound('SA_writeoff_pen_only.ogg'), duration=0.9, node=suit), SoundInterval(globalBattleSoundCache.getSound('SA_writeoff_ding_only.ogg'), node=suit))
    return Parallel(suitTrack, toonTracks, padPropTrack, pencilPropTrack, soundTrack)


def doRubberStamp(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = getSuitTrack(attack)
    stamp = globalPropPool.getProp('rubber-stamp')
    pad = globalPropPool.getProp('pad')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        padPosPoints = [Point3(-0.65, 0.83, -0.04), VBase3(5.625, 4.456, -165.125)]
        stampPosPoints = [Point3(-0.64, -0.17, -0.03), MovieUtil.PNT3_ZERO]
    elif suitType == 'c':
        padPosPoints = [Point3(0.19, -0.55, -0.21), VBase3(-166.76, -4.001, -1.658)]
        stampPosPoints = [Point3(-0.64, -0.08, 0.11), MovieUtil.PNT3_ZERO]
    else:
        padPosPoints = [Point3(-0.65, 0.83, -0.04), VBase3(5.625, 4.456, -165.125)]
        stampPosPoints = [Point3(-0.64, -0.17, -0.03), MovieUtil.PNT3_ZERO]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 1e-06, 3.2)
    propTrack = Sequence(Func(__showProp, stamp, suit.getRightHand(), stampPosPoints[0], stampPosPoints[1]), LerpScaleInterval(stamp, 0.5, MovieUtil.PNT3_ONE), Wait(2.6))
    cancelledTracks = Parallel()
    for t in targets:
        toon = t['toon']
        cancelled = __makeCancelledNodePath()
        missPoint = lambda cancelled = cancelled, toon = toon: __toonMissPoint(cancelled, toon)
        cancelledTrack = Sequence(Func(battle.movie.needRestoreRenderProp, cancelled), Func(cancelled.reparentTo, render), Func(cancelled.setScale, 0.6), Func(cancelled.setPosHpr, stamp, 0.81, -1.11, -0.16, 0, 0, 90), Func(cancelled.setP, 0), Func(cancelled.setR, 0), getPropThrowTrack(attack, cancelled, [__toonFacePoint(toon)], [missPoint], target=t), Func(MovieUtil.removeProp, cancelled), Func(battle.movie.clearRenderProp, cancelled))
        cancelledTracks.append(cancelledTrack)

    propTrack.append(cancelledTracks)
    propTrack.append(Wait(0.3))
    propTrack.append(LerpScaleInterval(stamp, 0.5, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProp, stamp))
    toonTracks = getToonTracks(attack, 3.4, ['conked'], 1.9, ['sidestep'])
    soundTrack = getSoundTrack('SA_rubber_stamp.ogg', delay=1.3, duration=1.1, node=suit)
    return Parallel(suitTrack, toonTracks, propTrack, padPropTrack, soundTrack)


def doRazzleDazzle(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    sign = globalPropPool.getProp('smile')
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('Smile')
    suitTrack = getSuitTrack(attack)
    signPosPoints = [Point3(0.0, -0.42, -0.04), VBase3(105.715, 73.977, 65.932)]
    signPropTrack = Sequence(Wait(0.5), Func(__showProp, sign, suit.getRightHand(), signPosPoints[0], signPosPoints[1]), LerpScaleInterval(sign, 0.5, Point3(1.39, 1.39, 1.39)), Wait(0.5))
    partTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        particleEffect = BattleParticles.createParticleEffect('Smile')
        if dmg > 0:
            hitPoint = lambda toon = toon: __toonFacePoint(toon)
        else:
            hitPoint = lambda particleEffect = particleEffect, toon = toon, suit = suit: __toonMissPoint(particleEffect, toon, parent=suit.getRightHand())
        partTrack = Sequence(Func(battle.movie.needRestoreParticleEffect, particleEffect), Func(particleEffect.start, sign), Func(particleEffect.wrtReparentTo, render), LerpPosInterval(particleEffect, 2.0, pos=hitPoint), Func(particleEffect.cleanup), Func(battle.movie.clearRestoreParticleEffect, particleEffect))
        partTracks.append(partTrack)

    signPropTrack.append(partTracks)
    signPropAnimTrack = ActorInterval(sign, 'smile', duration=4, startTime=0)
    toonTracks = getToonTracks(attack, 2.6, ['cringe'], 1.9, ['sidestep'])
    soundTrack = getSoundTrack('SA_razzle_dazzle.ogg', delay=1.6, node=suit)
    return Sequence(Parallel(suitTrack, signPropTrack, signPropAnimTrack, toonTracks, soundTrack), Func(MovieUtil.removeProp, sign))


def doSynergy(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    particleEffect = BattleParticles.createParticleEffect('Synergy')
    waterfallEffect = BattleParticles.createParticleEffect(file='synergyWaterfall')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1.0, 1.9, [particleEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
    damageAnims = [['slip-forward']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon(targets):
        fallingSoundTrack = Sequence(Wait(damageDelay + 0.5), SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, fallingSoundTrack, toonTracks)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)


def doTeeOff(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    club = globalPropPool.getProp('golf-club')
    suitTrack = getSuitTrack(attack)
    clubPosPoints = [MovieUtil.PNT3_ZERO, VBase3(63.097, 43.988, -18.435)]
    clubPropTrack = getPropTrack(club, suit.getLeftHand(), clubPosPoints, 0.5, 5.2, Point3(1.1, 1.1, 1.1))
    suitName = attack['suitName']
    if suitName == 'ym':
        ballPosPoints = [Point3(2.1, 0, 0.1)]
    elif suitName == 'tbc':
        ballPosPoints = [Point3(4.1, 0, 0.1)]
    elif suitName == 'm':
        ballPosPoints = [Point3(3.2, 0, 0.1)]
    elif suitName == 'ctn':
        ballPosPoints = [Point3(3.9, 0, 0.1)]
    elif suitName == 'rb':
        ballPosPoints = [Point3(4.2, 0, 0.1)]
    else:
        ballPosPoints = [Point3(2.1, 0, 0.1)]
    ballPropTracks = ()
    for t in targets:
        toon = t['toon']
        ball = globalPropPool.getProp('golf-ball')
        ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.7, Point3(1.5, 1.5, 1.5)), Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render), Wait(2.15))
        missPoint = lambda ball = ball, toon = toon: __toonMissPoint(ball, toon)
        ballPropTrack.append(getPropThrowTrack(attack, ball, [__toonFacePoint(toon)], [missPoint], target=t))
        ballPropTrack.append(Func(battle.movie.clearRenderProp, ball))
        ballPropTracks += (ballPropTrack,)

    dodgeDelay = suitTrack.getDuration() - 4.35
    toonTracks = getToonTracks(attack, suitTrack.getDuration() - 2.25, ['conked'], dodgeDelay, ['duck'], showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=4.1, node=suit)
    return Parallel(suitTrack, toonTracks, clubPropTrack, ballPropTrack, soundTrack)


def doBrainStorm(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    textureNames: Tuple[str, ...] = ('brainstorm-box',
     'brainstorm-env',
     'brainstorm-track')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 1.2
        damageDelay = 4.5
        dodgeDelay = 3.3
    elif suitType == 'b':
        partDelay = 1.2
        damageDelay = 4.5
        dodgeDelay = 3.3
    elif suitType == 'c':
        partDelay = 1.2
        damageDelay = 4.5
        dodgeDelay = 3.3
    suitTrack = getSuitTrack(attack, delay=0.9)
    cloudPropTracks = ()
    for t in targets:
        toon = t['toon']
        snowEffect = BattleParticles.createParticleEffect('BrainStorm')
        snowEffect2 = BattleParticles.createParticleEffect('BrainStorm')
        snowEffect3 = BattleParticles.createParticleEffect('BrainStorm')
        effectColor = Vec4(0.65, 0.79, 0.93, 0.85)
        BattleParticles.setEffectTexture(snowEffect, textureNames, color=effectColor)
        BattleParticles.setEffectTexture(snowEffect2, textureNames, color=effectColor)
        BattleParticles.setEffectTexture(snowEffect3, textureNames, color=effectColor)
        cloud = globalPropPool.getProp('stormcloud')
        initialCloudHeight = suit.height + 3
        cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
        cloudPropTrack = Sequence()
        cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
        cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.7))
        cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
        cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack.append(Wait(1.1))
        cloudPropTrack.append(LerpPosInterval(cloud, 1, pos=targetPoint))
        cloudPropTrack.append(Wait(partDelay))
        cloudPropTrack.append(Parallel(ParticleInterval(snowEffect, cloud, worldRelative=0, duration=2.2, cleanup=True), Sequence(Wait(0.5), ParticleInterval(snowEffect2, cloud, worldRelative=0, duration=1.7, cleanup=True)), Sequence(Wait(1.0), ParticleInterval(snowEffect3, cloud, worldRelative=0, duration=1.2, cleanup=True)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.5), ActorInterval(cloud, 'stormcloud', startTime=2.5, duration=0.5), ActorInterval(cloud, 'stormcloud', startTime=1, duration=1.5))))
        cloudPropTrack.append(Wait(0.4))
        cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
        cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
        cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
        cloudPropTracks += (cloudPropTrack,)

    damageAnims = [['cringe',
      0.01,
      0.4,
      0.8], ['duck', 1e-06, 1.6]]
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('SA_brainstorm.ogg', delay=2.6, node=suit)
    return Parallel(suitTrack, toonTracks, *cloudPropTracks, soundTrack)


def doBuzzWord(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffects = []
    textureNames: Tuple[str, ...] = ('buzzwords-crash',
     'buzzwords-inc',
     'buzzwords-main',
     'buzzwords-over',
     'buzzwords-syn')
    for i in range(0, 5):
        effect = BattleParticles.createParticleEffect('BuzzWord')
        BattleParticles.setEffectTexture(effect, textureNames, color=Vec4(1, 0.94, 0.02, 1) if random.random() > 0.5 else Vec4(0, 0, 0, 1))
        particleEffects.append(effect)

    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 4.0
        partDuration = 2.2
        damageDelay = 4.5
        dodgeDelay = 3.8
    elif suitType == 'b':
        partDelay = 4.0
        partDuration = 2.2
        damageDelay = 4.5
        dodgeDelay = 3.8
    elif suitType == 'c':
        partDelay = 4.0
        partDuration = 2.2
        damageDelay = 4.5
        dodgeDelay = 3.8
    suitName = suit.getStyleName()
    if suitName == 'm':
        for effect in particleEffects:
            effect.setPos(0, 2.8, suit.getHeight() - 2.5)
            effect.setHpr(0, -20, 0)

    elif suitName == 'mm':
        for effect in particleEffects:
            effect.setPos(0, 2.1, suit.getHeight() - 0.8)

    suitTrack = getSuitTrack(attack)
    particleTracks = []
    for effect in particleEffects:
        particleTracks.append(getPartTrack(effect, partDelay, partDuration, [effect, suit, 0]))

    toonTrack = getToonTrack(attack, damageDelay=damageDelay, damageAnimNames=['cringe'], splicedDodgeAnims=[['duck', dodgeDelay, 1.4]], showMissedExtraTime=dodgeDelay + 0.5)
    soundTrack = getSoundTrack('SA_buzz_word.ogg', delay=3.9, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, *particleTracks)


def doDemotion(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    BattleParticles.loadParticles()
    sprayEffect = BattleParticles.createParticleEffect('DemotionSpray')
    freezeEffect = BattleParticles.createParticleEffect('DemotionFreeze')
    unFreezeEffect = BattleParticles.createParticleEffect(file='demotionUnFreeze')
    BattleParticles.setEffectTexture(sprayEffect, 'snow-particle')
    BattleParticles.setEffectTexture(freezeEffect, 'snow-particle')
    BattleParticles.setEffectTexture(unFreezeEffect, 'snow-particle')
    facePoint = __toonFacePoint(toon)
    freezeEffect.setPos(0, 0, facePoint.getZ())
    unFreezeEffect.setPos(0, 0, facePoint.getZ())
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(sprayEffect, 0.7, 1.1, [sprayEffect, suit, 0])
    partTrack2 = getPartTrack(freezeEffect, 1.4, 2.9, [freezeEffect, toon, 0])
    partTrack3 = getPartTrack(unFreezeEffect, 6.65, 0.5, [unFreezeEffect, toon, 0])
    dodgeAnims = [['duck', 1e-06, 0.8]]
    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0,
     0.5])
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.4, 0.5, startTime=0.5))
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.3, 0.5, startTime=0.9))
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.3, 0.6, startTime=1.2))
    damageAnims.append(['cringe', 2.6, 1.5])
    toonTrack = getToonTrack(attack, damageDelay=1.0, splicedDamageAnims=damageAnims, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.6, showDamageExtraTime=1.3)
    soundTrack = getSoundTrack('SA_demotion.ogg', delay=1.2, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, soundTrack, partTrack, partTrack2, partTrack3)
    else:
        return Parallel(suitTrack, toonTrack, soundTrack, partTrack)


def doCanned(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    hips = toon.getHipsParts()
    propDelay = 0.8
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'c':
        suitDelay = 1.13
        dodgeDelay = 3.1
    else:
        suitDelay = 1.83
        dodgeDelay = 3.6
    throwDuration = 1.5
    can = globalPropPool.getProp('can')
    scale = 26
    torso = toon.style.torso
    torso = torso[0]
    if torso == 's':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 1.9975)
    elif torso == 'm':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 1.7975)
    elif torso == 'l':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 2.31)
    canHpr = VBase3(-173.47, -0.42, 162.09)
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.14, 0.15, 0.08), VBase3(-10.584, 11.945, -161.684)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, propDelay, Point3(6, 6, 6), scaleUpTime=0.5))
    propDelay = propDelay + 0.5
    throwTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 1.1)
    hitPoint.setY(hitPoint.getY() - 0.5)
    hitPoint.setZ(hitPoint.getZ() + toon.height + 1.1)
    throwTrack.append(Func(battle.movie.needRestoreRenderProp, can))
    throwTrack.append(getThrowTrack(can, hitPoint, duration=throwDuration, parent=battle))
    if dmg > 0:
        can2 = MovieUtil.copyProp(can)
        hips1 = hips.getPath(2)
        hips2 = hips.getPath(1)
        can2Point = Point3(hitPoint.getX(), hitPoint.getY() + 6.4, hitPoint.getZ())
        can2.setPos(can2Point)
        can2.setScale(scaleUpPoint)
        can2.setHpr(canHpr)
        throwTrack.append(Func(battle.movie.needRestoreHips))
        throwTrack.append(Func(can.wrtReparentTo, hips1))
        throwTrack.append(Func(can2.reparentTo, hips2))
        throwTrack.append(Wait(2.4))
        throwTrack.append(Func(MovieUtil.removeProp, can2))
        throwTrack.append(Func(battle.movie.clearRestoreHips))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(can, throwDuration, scaleUpPoint))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(can, throwDuration, canHpr))
        soundTrack = Sequence(Wait(2.6), SoundInterval(globalBattleSoundCache.getSound('SA_canned_tossup_only.ogg'), node=suit), SoundInterval(globalBattleSoundCache.getSound('SA_canned_impact_only.ogg'), node=suit))
    else:
        land = toon.getPos(battle)
        land.setZ(land.getZ() + 0.7)
        bouncePoint1 = Point3(land.getX(), land.getY() - 1.5, land.getZ() + 2.5)
        bouncePoint2 = Point3(land.getX(), land.getY() - 2.1, land.getZ() - 0.2)
        bouncePoint3 = Point3(land.getX(), land.getY() - 3.1, land.getZ() + 1.5)
        bouncePoint4 = Point3(land.getX(), land.getY() - 4.1, land.getZ() + 0.3)
        throwTrack.append(LerpPosInterval(can, 0.4, land))
        throwTrack.append(LerpPosInterval(can, 0.4, bouncePoint1))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint2))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint3))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint4))
        throwTrack.append(Wait(1.1))
        throwTrack.append(LerpScaleInterval(can, 0.3, MovieUtil.PNT3_NEARZERO))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(can, throwDuration, Point3(11, 11, 11)))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(can, throwDuration, canHpr), Wait(0.4), LerpHprInterval(can, 0.4, Point3(83.27, 19.52, -177.92)), LerpHprInterval(can, 0.3, Point3(95.24, -72.09, 88.65)), LerpHprInterval(can, 0.2, Point3(-96.34, -2.63, 179.89)))
        soundTrack = getSoundTrack('SA_canned_tossup_only.ogg', delay=2.6, node=suit)
    canTrack = Sequence(Parallel(throwTrack, scaleTrack, hprTrack), Func(MovieUtil.removeProp, can), Func(battle.movie.clearRenderProp, can))
    damageAnims = [['struggle',
      propDelay + suitDelay + throwDuration,
      0.01,
      0.7], ['slip-backward', 0.01, 0.45]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showDamageExtraTime=propDelay + suitDelay + 2.4)
    return Parallel(suitTrack, toonTrack, canTrack, soundTrack)


def doDownsize(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    damageDelay = 2.3
    sprayEffect = BattleParticles.createParticleEffect(file='downsizeSpray')
    cloudEffect = BattleParticles.createParticleEffect(file='downsizeCloud')
    toonPos = toon.getPos(toon)
    cloudPos = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.getHeight() * 0.55)
    cloudEffect.setPos(cloudPos)
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.28, [sprayEffect, suit, 0])
    cloudTrack = getPartTrack(cloudEffect, 2.1, 1.9, [cloudEffect, toon, 0])
    if dmg > 0:
        initialScale = toon.getScale()
        downScale = Vec3(0.4, 0.4, 0.4)
        shrinkTrack = Sequence(Wait(damageDelay + 0.5), Func(battle.movie.needRestoreToonScale), LerpScaleInterval(toon, 1.0, downScale * 1.1), LerpScaleInterval(toon, 0.1, downScale * 0.9), LerpScaleInterval(toon, 0.1, downScale * 1.05), LerpScaleInterval(toon, 0.1, downScale * 0.95), LerpScaleInterval(toon, 0.1, downScale), Wait(2.1), LerpScaleInterval(toon, 0.5, initialScale * 1.5), LerpScaleInterval(toon, 0.15, initialScale * 0.5), LerpScaleInterval(toon, 0.15, initialScale * 1.2), LerpScaleInterval(toon, 0.15, initialScale * 0.8), LerpScaleInterval(toon, 0.15, initialScale), Func(battle.movie.clearRestoreToonScale))
    damageAnims = []
    damageAnims.append(['juggle',
     0.01,
     0.87,
     0.5])
    damageAnims.append(['lose',
     0.01,
     2.17,
     0.93])
    damageAnims.append(['lose',
     0.01,
     3.1,
     -0.93])
    damageAnims.append(['struggle',
     0.01,
     0.8,
     1.8])
    damageAnims.append(['sidestep-right',
     0.01,
     2.97,
     1.49])
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.6, dodgeAnimNames=['sidestep'])
    if dmg > 0:
        return Parallel(suitTrack, sprayTrack, cloudTrack, shrinkTrack, toonTrack)
    else:
        return Parallel(suitTrack, sprayTrack, toonTrack)


def doPinkSlip(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    throwDelay = 3.03
    throwDuration = 0.5
    suitTrack = getSuitTrack(attack)
    propTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        paper = globalPropPool.getProp('pink-slip')
        posPoints = [Point3(0.07, -0.06, -0.18), VBase3(-172.075, -26.715, -89.131)]
        paperAppearTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.8, Point3(8, 8, 8), scaleUpTime=0.5))
        paperAppearTrack.append(Wait(1.73))
        hitPoint = __toonGroundPoint(attack, toon, 0.2, parent=battle)
        paperAppearTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
        paperAppearTrack.append(Func(paper.wrtReparentTo, battle))
        paperAppearTrack.append(LerpPosInterval(paper, throwDuration, hitPoint))
        if dmg > 0:
            paperPause = 0.01
            slidePoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ() + 4)
            landPoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ())
            paperAppearTrack.append(Wait(paperPause))
            paperAppearTrack.append(LerpPosInterval(paper, 0.2, slidePoint))
            paperAppearTrack.append(LerpPosInterval(paper, 1.1, landPoint))
            paperSpinTrack = Sequence(Wait(throwDelay), LerpHprInterval(paper, throwDuration, VBase3(300, 0, 0)), Wait(paperPause), LerpHprInterval(paper, 1.3, VBase3(-200, 100, 100)))
        else:
            slidePoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ())
            paperAppearTrack.append(LerpPosInterval(paper, 0.5, slidePoint))
            paperSpinTrack = Sequence(Wait(throwDelay), LerpHprInterval(paper, throwDuration, VBase3(300, 0, 0)), LerpHprInterval(paper, 0.5, VBase3(10, 0, 0)))
        propTrack = Sequence()
        propTrack.append(Parallel(paperAppearTrack, paperSpinTrack))
        propTrack.append(LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
        propTrack.append(Func(MovieUtil.removeProp, paper))
        propTrack.append(Func(battle.movie.clearRenderProp, paper))
        propTracks += (propTrack,)

    damageAnims = [['jump',
      0.01,
      0.3,
      0.7], ['slip-forward', 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=2.81, splicedDamageAnims=damageAnims, dodgeDelay=2.8, dodgeAnimNames=['jump'], showDamageExtraTime=0.9)
    soundTrack = getSoundTrack('SA_pink_slip.ogg', delay=2.9, duration=1.1, node=suit)
    return Parallel(suitTrack, toonTracks, *propTracks, soundTrack)


def doReOrg(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    damageDelay = 1.7
    attackDelay = 1.7
    sprayEffect = BattleParticles.createParticleEffect(file='reorgSpray')
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    if dmg > 0:
        headParts = toon.getHeadParts()
        headTracks = Parallel()
        for partNum in range(0, headParts.getNumPaths()):
            part = headParts.getPath(partNum)
            x = part.getX()
            y = part.getY()
            z = part.getZ()
            h = part.getH()
            p = part.getP()
            r = part.getR()
            headTracks.append(Sequence(Wait(attackDelay), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x - 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.04)), LerpPosInterval(part, 0.25, Point3(x, y, z + 2.2)), LerpHprInterval(part, 0.4, VBase3(360, 0, 180)), LerpPosInterval(part, 0.3, Point3(x, y, z + 3.1)), LerpPosInterval(part, 0.15, Point3(x, y, z + 0.3)), Wait(0.15), LerpHprInterval(part, 0.6, VBase3(-745, 0, 180), startHpr=VBase3(0, 0, 180)), LerpHprInterval(part, 0.8, VBase3(25, 0, 180), startHpr=VBase3(0, 0, 180)), LerpPosInterval(part, 0.15, Point3(x, y, z + 1)), LerpHprInterval(part, 0.3, VBase3(h, p, r)), Wait(0.2), LerpPosInterval(part, 0.1, Point3(x, y, z)), Wait(0.9)))

        def getChestTrack(part, attackDelay = attackDelay):
            origScale = part.getScale()
            return Sequence(Wait(attackDelay), LerpHprInterval(part, 1.1, VBase3(180, 0, 0)), Wait(1.1), LerpHprInterval(part, 1.1, part.getHpr()))

        chestTracks = Parallel()
        arms = toon.findAllMatches('**/arms')
        sleeves = toon.findAllMatches('**/sleeves')
        hands = toon.findAllMatches('**/hands')
        if not toon.getTransformed():
            for partNum in range(0, arms.getNumPaths()):
                chestTracks.append(getChestTrack(arms.getPath(partNum)))
                if len(toon.getStyle().torso) != 1:
                    chestTracks.append(getChestTrack(sleeves.getPath(partNum)))
                chestTracks.append(getChestTrack(hands.getPath(partNum)))

    damageAnims = [['neutral',
      0.01,
      0.01,
      0.5], ['juggle',
      0.01,
      0.01,
      1.48], ['think', 0.01, 2.28]]
    dodgeAnims = []
    dodgeAnims.append(['think',
     0.01,
     0,
     0.6])
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.01, dodgeAnimNames=['duck'], showDamageExtraTime=2.1, showMissedExtraTime=2.0)
    if dmg > 0:
        return Parallel(suitTrack, partTrack, toonTrack, headTracks, chestTracks)
    else:
        return Parallel(suitTrack, partTrack, toonTrack)


def doSacked(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    hips = toon.getHipsParts()
    propDelay = 0.85
    suitDelay = 1.93
    throwDuration = 0.9
    sack = globalPropPool.getProp('sandbag')
    initialScale = Point3(0.65, 1.47, 1.28)
    scaleUpPoint = Point3(1.05, 1.67, 0.98) * 4.1
    sackHpr = VBase3(-154.33, -6.33, 163.8)
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(0.51, -2.03, -0.73), VBase3(90.0, -24.98, 77.73)]
    sackAppearTrack = Sequence(getPropAppearTrack(sack, suit.getRightHand(), posPoints, propDelay, initialScale, scaleUpTime=0.2))
    propDelay = propDelay + 0.2
    sackAppearTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    if dmg > 0:
        hitPoint.setX(hitPoint.getX() + 2.1)
        hitPoint.setY(hitPoint.getY() + 0.9)
        hitPoint.setZ(hitPoint.getZ() + toon.height + 1.2)
    else:
        hitPoint.setZ(hitPoint.getZ() - 0.2)
    sackAppearTrack.append(Func(battle.movie.needRestoreRenderProp, sack))
    sackAppearTrack.append(getThrowTrack(sack, hitPoint, duration=throwDuration, parent=battle))
    if dmg > 0:
        sack2 = MovieUtil.copyProp(sack)
        hips1 = hips.getPath(2)
        hips2 = hips.getPath(1)
        sack2.hide()
        sack2.reparentTo(battle)
        sack2.setPos(Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ()))
        sack2.setScale(scaleUpPoint)
        sack2.setHpr(sackHpr)
        sackAppearTrack.append(Func(battle.movie.needRestoreHips))
        sackAppearTrack.append(Func(sack.wrtReparentTo, hips1))
        sackAppearTrack.append(Func(sack2.show))
        sackAppearTrack.append(Func(sack2.wrtReparentTo, hips2))
        sackAppearTrack.append(Wait(2.4))
        scaleTrack = Sequence(
            Wait(propDelay + suitDelay), 
            LerpScaleInterval(sack, throwDuration, scaleUpPoint), 
            Wait(1.8), 
            LerpScaleInterval(sack, 0.3, MovieUtil.PNT3_NEARZERO)
            )
        hprTrack = Sequence(
            Wait(propDelay + suitDelay), 
            LerpHprInterval(sack, throwDuration, sackHpr)
            )
        sackTrack = Sequence(
            Parallel(
                sackAppearTrack, 
                scaleTrack, 
                hprTrack
            ),
        )
    else:
        sackAppearTrack.append(Wait(1.1))
        sackAppearTrack.append(LerpScaleInterval(sack, 0.3, MovieUtil.PNT3_NEARZERO))
        sackTrack = Sequence(sackAppearTrack, Func(MovieUtil.removeProp, sack), Func(battle.movie.clearRenderProp, sack))
    damageAnims = [['struggle',
      0.01,
      0.01,
      0.7], ['slip-backward', 0.01, 0.45]]
    toonTrack = getToonTrack(attack, damageDelay=propDelay + suitDelay + throwDuration, splicedDamageAnims=damageAnims, dodgeDelay=3.0, dodgeAnimNames=['sidestep'], showDamageExtraTime=1.8, showMissedExtraTime=0.8)
    return Parallel(suitTrack, toonTrack, sackTrack)


def doGlowerPower(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = getSuitTrack(attack)
    suitName = suit.getStyleName()
    if suitName == 'hh':
        leftPosPoints = [Point3(0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
    elif suitName == 'tbc':
        leftPosPoints = [Point3(0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
    else:
        leftPosPoints = [Point3(0.4, 3.8, 3.7), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.4, 3.8, 3.7), MovieUtil.PNT3_ZERO]
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    for t in targets:
        leftKnives = []
        rightKnives = []
        for i in range(0, 3):
            leftKnives.append(globalPropPool.getProp('dagger'))
            rightKnives.append(globalPropPool.getProp('dagger'))

        for i in range(0, 3):
            knifeDelay = 0.11
            leftTrack = Sequence()
            leftTrack.append(Wait(1.1))
            leftTrack.append(Wait(i * knifeDelay))
            leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
            leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3, target=t))
            leftKnifeTracks.append(leftTrack)
            rightTrack = Sequence()
            rightTrack.append(Wait(1.1))
            rightTrack.append(Wait(i * knifeDelay))
            rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
            rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3, target=t))
            rightKnifeTracks.append(rightTrack)

    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonTracks = getToonTracks(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack, leftKnifeTracks, rightKnifeTracks)


def doHalfWindsor(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'c':
        throwDelay = 1.45
        damageDelay = 2.71
        dodgeDelay = 1.64
    else:
        throwDelay = 2.17
        damageDelay = 3.4
        dodgeDelay = 2.4
    suitTrack = getSuitTrack(attack)
    tiePropTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tie = globalPropPool.getProp('double-windsor' if attack['identifier'] in ('ttrealms:double_windsor', 'ttrealms:double_windsor_group') else 'half-windsor')
        posPoints = [Point3(0.02, 0.88, 0.48), VBase3(99, -3, -108.2)]
        tiePropTrack = getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, Point3(7, 7, 7), scaleUpTime=0.5)
        tiePropTrack.append(Wait(throwDelay))
        missPoint = __toonMissBehindPoint(toon, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)
        missPoint.setZ(missPoint.getZ() + 4)
        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.1)
        hitPoint.setY(hitPoint.getY() - 0.7)
        hitPoint.setZ(hitPoint.getZ() + 0.9)
        tiePropTrack.append(getPropThrowTrack(attack, tie, [hitPoint], [missPoint], hitDuration=0.4, missDuration=0.8, missScaleDown=0.3, parent=battle, target=t))
        tiePropTracks += (tiePropTrack,)

    damageAnims = [['conked',
      0.01,
      0.01,
      0.4], ['cringe', 0.01, 0.7]]
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, toonTracks, *tiePropTracks)


def doHeadShrink(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    damageDelay = 2.1
    dodgeDelay = 1.4
    shrinkSpray = BattleParticles.createParticleEffect(file='headShrinkSpray')
    shrinkCloud = BattleParticles.createParticleEffect(file='headShrinkCloud')
    shrinkDrop = BattleParticles.createParticleEffect(file='headShrinkDrop')
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(shrinkSpray, 0.3, 1.4, [shrinkSpray, suit, 0])
    shrinkCloud.reparentTo(battle)
    adjust = 0.4
    x = toon.getX(battle)
    y = toon.getY(battle) - adjust
    z = 8
    shrinkCloud.setPos(Point3(x, y, z))
    shrinkDrop.setPos(Point3(0, 0 - adjust, 7.5))
    off = 0.7
    cloudPoints = [Point3(x + off, y, z),
     Point3(x + off / 2, y + off / 2, z),
     Point3(x, y + off, z),
     Point3(x - off / 2, y + off / 2, z),
     Point3(x - off, y, z),
     Point3(x - off / 2, y - off / 2, z),
     Point3(x, y - off, z),
     Point3(x + off / 2, y - off / 2, z),
     Point3(x + off, y, z),
     Point3(x, y, z)]
    circleTrack = Sequence()
    for point in cloudPoints:
        circleTrack.append(LerpPosInterval(shrinkCloud, 0.14, point, other=battle))

    cloudTrack = Sequence()
    cloudTrack.append(Wait(1.42))
    cloudTrack.append(Func(battle.movie.needRestoreParticleEffect, shrinkCloud))
    cloudTrack.append(Func(shrinkCloud.start, battle))
    cloudTrack.append(circleTrack)
    cloudTrack.append(circleTrack)
    cloudTrack.append(LerpFunctionInterval(shrinkCloud.setAlphaScale, fromData=1, toData=0, duration=0.7))
    cloudTrack.append(Func(shrinkCloud.cleanup))
    cloudTrack.append(Func(battle.movie.clearRestoreParticleEffect, shrinkCloud))
    shrinkDelay = 0.8
    shrinkDuration = 1.1
    shrinkTrack = Sequence()
    if dmg > 0:
        headParts = toon.getHeadParts()
        initialScale = headParts.getPath(0).getScale()[0]
        shrinkTrack.append(Wait(damageDelay + shrinkDelay))

        def scaleHeadParallel(scale, duration, headParts = headParts):
            headTracks = Parallel()
            for partNum in range(0, headParts.getNumPaths()):
                nextPart = headParts.getPath(partNum)
                headTracks.append(LerpScaleInterval(nextPart, duration, Point3(scale, scale, scale)))

            return headTracks

        shrinkTrack.append(Func(battle.movie.needRestoreHeadScale))
        shrinkTrack.append(scaleHeadParallel(0.6, shrinkDuration))
        shrinkTrack.append(Wait(1.6))
        shrinkTrack.append(scaleHeadParallel(initialScale * 3.2, 0.4))
        shrinkTrack.append(scaleHeadParallel(initialScale * 0.7, 0.4))
        shrinkTrack.append(scaleHeadParallel(initialScale * 2.5, 0.3))
        shrinkTrack.append(scaleHeadParallel(initialScale * 0.8, 0.3))
        shrinkTrack.append(scaleHeadParallel(initialScale * 1.9, 0.2))
        shrinkTrack.append(scaleHeadParallel(initialScale * 0.85, 0.2))
        shrinkTrack.append(scaleHeadParallel(initialScale * 1.7, 0.15))
        shrinkTrack.append(scaleHeadParallel(initialScale * 0.9, 0.15))
        shrinkTrack.append(scaleHeadParallel(initialScale * 1.3, 0.1))
        shrinkTrack.append(scaleHeadParallel(initialScale, 0.1))
        shrinkTrack.append(Func(battle.movie.clearRestoreHeadScale))
        shrinkTrack.append(Wait(0.7))
    dropTrack = getPartTrack(shrinkDrop, 1.5, 2.5, [shrinkDrop, toon, 0])
    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.65,
     0.2])
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.64, 1.0, startTime=0.85))
    damageAnims.append(['cringe', 0.4, 1.49])
    damageAnims.append(['conked',
     0.01,
     3.6,
     -1.6])
    damageAnims.append(['conked',
     0.01,
     3.1,
     0.4])
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    if dmg > 0:
        shrinkSound = globalBattleSoundCache.getSound('SA_head_shrink_only.ogg')
        growSound = globalBattleSoundCache.getSound('SA_head_grow_back_only.ogg')
        soundTrack = Sequence(Wait(2.1), SoundInterval(shrinkSound, duration=2.1, node=suit), Wait(1.6), SoundInterval(growSound, node=suit))
        return Parallel(suitTrack, sprayTrack, cloudTrack, dropTrack, toonTrack, shrinkTrack, soundTrack)
    else:
        return Parallel(suitTrack, sprayTrack, cloudTrack, dropTrack, toonTrack)


def doRolodex(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    rollodex = globalPropPool.getProp('rollodex')
    particleEffect2 = BattleParticles.createParticleEffect(file='rollodexWaterfall')
    particleEffect3 = BattleParticles.createParticleEffect(file='rollodexStream')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        propPosPoints = [Point3(-0.51, -0.03, -0.1), VBase3(89.673, 2.166, 177.786)]
        propScale = Point3(1.2, 1.2, 1.2)
        partDelay = 2.6
        part2Delay = 2.8
        part3Delay = 3.2
        partDuration = 1.6
        part2Duration = 1.9
        part3Duration = 1
        damageDelay = 3.8
        dodgeDelay = 2.5
    elif suitType == 'b':
        propPosPoints = [Point3(0.12, 0.24, 0.01), VBase3(99.032, 5.973, -179.839)]
        propScale = Point3(0.91, 0.91, 0.91)
        partDelay = 2.9
        part2Delay = 3.1
        part3Delay = 3.5
        partDuration = 1.6
        part2Duration = 1.9
        part3Duration = 1
        damageDelay = 4
        dodgeDelay = 2.5
    elif suitType == 'c':
        propPosPoints = [Point3(-0.51, -0.03, -0.1), VBase3(89.673, 2.166, 177.786)]
        propScale = Point3(1.2, 1.2, 1.2)
        partDelay = 2.3
        part2Delay = 2.8
        part3Delay = 3.2
        partDuration = 1.9
        part2Duration = 1.9
        part3Duration = 1
        damageDelay = 3.5
        dodgeDelay = 2.5
    hitPoint = lambda toon = toon: __toonFacePoint(toon)
    partTrack2 = getPartTrack(particleEffect2, part2Delay, part2Duration, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, part3Delay, part3Duration, [particleEffect3, suit, 0])
    suitTrack = getSuitTrack(attack)
    propTrack = getPropTrack(rollodex, suit.getLeftHand(), propPosPoints, 1e-06, 4.7, scaleUpPoint=propScale, anim=0, propName='rollodex', animDuration=0, animStartTime=0)
    toonTrack = getToonTrack(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    soundTrack = getSoundTrack('SA_rolodex.ogg', delay=2.8, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, partTrack2, partTrack3)

def doEvilGlare(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    eye = globalPropPool.getProp('evil-glare')
    damageDelay = 2.44
    dodgeDelay = 1.64
    suitName = suit.getStyleName()
    if suitName == 'cr':
        posPoints = [Point3(-0.46, 4.85, 5.28), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'tf':
        posPoints = [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)]
    elif suitName in ['le', 'smc']:
        posPoints = [Point3(-0.64, 4.45, 5.91), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'shj':
        posPoints = [Point3(-0.7, 5.75, 7.5), VBase3(-155.0, -20.0, 0.0)]
    else:
        posPoints = [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)]
    appearDelay = 0.8
    suitHoldStart = 1.06
    suitHoldStop = 1.69
    suitHoldDuration = suitHoldStop - suitHoldStart
    eyeHoldDuration = 1.1
    moveDuration = 1.1
    suitSplicedAnims = []
    suitSplicedAnims.append(['glower',
     0.01,
     0.01,
     suitHoldStart])
    suitSplicedAnims.extend(getSplicedLerpAnims('glower', suitHoldDuration, 1.1, startTime=suitHoldStart))
    suitSplicedAnims.append(['glower', 0.01, suitHoldStop])
    suitTrack = getSuitTrack(attack, splicedAnims=suitSplicedAnims)
    eyeAppearTrack = Sequence(Wait(suitHoldStart), Func(__showProp, eye, suit, posPoints[0], posPoints[1]), LerpScaleInterval(eye, suitHoldDuration, Point3(2, 2, 2)), Wait(1.12), Func(battle.movie.needRestoreRenderProp, eye), Func(eye.wrtReparentTo, battle), Wait(moveDuration))
    eyePropTrack = Sequence(eyeAppearTrack, Func(battle.movie.clearRenderProp, eye), Func(MovieUtil.removeProp, eye))
    damageAnims = [['duck',
      0.01,
      0.01,
      1.4], ['cringe', 0.01, 0.3]]
    toonTracks = getToonTracks(attack, splicedDamageAnims=damageAnims, damageDelay=damageDelay, dodgeDelay=dodgeDelay, dodgeAnimNames=['laugh'], showDamageExtraTime=1.7, showMissedExtraTime=1.7)
    return Parallel(suitTrack, toonTracks, eyePropTrack)

def doEvilEye(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 2.44
    dodgeDelay = 1.64
    suitName = suit.getStyleName()
    if suitName == 'cr':
        posPoints = [Point3(-0.46, 4.85, 5.28), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'tf':
        posPoints = [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)]
    elif suitName in ['le', 'smc']:
        posPoints = [Point3(-0.64, 4.45, 5.91), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'shj':
        posPoints = [Point3(-0.7, 5.75, 7.5), VBase3(-155.0, -20.0, 0.0)]
    else:
        posPoints = [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)]
    appearDelay = 0.8
    suitHoldStart = 1.06
    suitHoldStop = 1.69
    suitHoldDuration = suitHoldStop - suitHoldStart
    eyeHoldDuration = 1.1
    moveDuration = 1.1
    suitSplicedAnims = []
    suitSplicedAnims.append(['glower',
     0.01,
     0.01,
     suitHoldStart])
    suitSplicedAnims.extend(getSplicedLerpAnims('glower', suitHoldDuration, 1.1, startTime=suitHoldStart))
    suitSplicedAnims.append(['glower', 0.01, suitHoldStop])
    suitTrack = getSuitTrack(attack, splicedAnims=suitSplicedAnims)
    eyePropTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        eye = globalPropPool.getProp('evil-eye')
        eyeAppearTrack = Sequence(Wait(suitHoldStart), Func(__showProp, eye, suit, posPoints[0], posPoints[1]), LerpScaleInterval(eye, suitHoldDuration, Point3(11, 11, 11)), Wait(eyeHoldDuration * 0.3), LerpHprInterval(eye, 0.02, Point3(205, 40, 0)), Wait(eyeHoldDuration * 0.7), Func(battle.movie.needRestoreRenderProp, eye), Func(eye.wrtReparentTo, battle))
        toonFace = __toonFacePoint(toon, parent=battle)
        if dmg > 0:
            lerpInterval = LerpPosInterval(eye, moveDuration, toonFace)
        else:
            lerpInterval = LerpPosInterval(eye, moveDuration, Point3(toonFace.getX(), toonFace.getY() - 5, toonFace.getZ() - 2))
        eyeMoveTrack = lerpInterval
        eyeRollTrack = LerpHprInterval(eye, moveDuration, Point3(0, 0, -180))
        eyePropTrack = Sequence(eyeAppearTrack, Parallel(eyeMoveTrack, eyeRollTrack), Func(battle.movie.clearRenderProp, eye), Func(MovieUtil.removeProp, eye))
        eyePropTracks += (eyePropTrack,)

    damageAnims = [['duck',
      0.01,
      0.01,
      1.4], ['cringe', 0.01, 0.3]]
    toonTracks = getToonTracks(attack, splicedDamageAnims=damageAnims, damageDelay=damageDelay, dodgeDelay=dodgeDelay, dodgeAnimNames=['duck'], showDamageExtraTime=1.7, showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_evil_eye.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTracks, *eyePropTracks, soundTrack)


def doPlayHardball(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitType = getSuitBodyType(attack['suitName'])
    if suitType in ('a', 'b'):
        suitDelay = 1.79
        damageDelay = 3.46
        dodgeDelay = 2.56
        soundDelay = 3.1
    elif suitType == 'c':
        suitDelay = 1.09
        damageDelay = 2.76
        dodgeDelay = 1.86
        soundDelay = 2.4
    suitTrack = getSuitTrack(attack)
    propTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        ball = globalPropPool.getProp('baseball')
        ballPosPoints = [Point3(0.04, 0.03, -0.31), VBase3(-1.152, 86.581, -76.784)]
        propTrack = Sequence(getPropAppearTrack(ball, suit.getRightHand(), ballPosPoints, 0.8, Point3(5, 5, 5), scaleUpTime=0.5))
        propTrack.append(Wait(suitDelay))
        propTrack.append(Func(battle.movie.needRestoreRenderProp, ball))
        propTrack.append(Func(ball.wrtReparentTo, battle))
        toonPos = toon.getPos(battle)
        x = toonPos.getX()
        y = toonPos.getY()
        z = toonPos.getZ()
        z = z + 0.2
        if dmg > 0:
            propTrack.append(LerpPosInterval(ball, 0.5, __toonFacePoint(toon, parent=battle)))
            propTrack.append(LerpPosInterval(ball, 0.5, Point3(x, y + 3, z)))
            propTrack.append(LerpPosInterval(ball, 0.4, Point3(x, y + 5, z + 2)))
            propTrack.append(LerpPosInterval(ball, 0.3, Point3(x, y + 6, z)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 7, z + 1)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 8, z)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 8.5, z + 0.6)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 9, z + 0.2)))
        else:
            propTrack.append(LerpPosInterval(ball, 0.5, Point3(x, y + 2, z)))
            propTrack.append(LerpPosInterval(ball, 0.4, Point3(x, y - 1, z + 2)))
            propTrack.append(LerpPosInterval(ball, 0.3, Point3(x, y - 3, z)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 4, z + 1)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 5, z)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 5.5, z + 0.6)))
            propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 6, z + 0.2)))
        propTrack.append(Wait(0.4))
        propTrack.append(LerpScaleInterval(ball, 0.3, MovieUtil.PNT3_NEARZERO))
        propTrack.append(Func(MovieUtil.removeProp, ball))
        propTrack.append(Func(battle.movie.clearRenderProp, ball))
        propTracks += (propTrack,)

    damageAnims = [['conked',
      damageDelay,
      0.01,
      0.5], ['slip-backward', 0.01, 0.7]]
    toonTracks = getToonTracks(attack, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showDamageExtraTime=3.9)
    soundTrack = getSoundTrack('SA_hardball_impact_only.ogg', delay=soundDelay - 0.3, node=suit) if hitAtleastOneToon(targets) else getSoundTrack('SA_hardball.ogg', delay=soundDelay, node=suit)
    return Parallel(suitTrack, toonTracks, *propTracks, soundTrack)


def doPowerTie(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        throwDelay = 2.17
        damageDelay = 3.3
        dodgeDelay = 3.1
    elif suitType == 'b':
        throwDelay = 2.17
        damageDelay = 3.3
        dodgeDelay = 3.1
    elif suitType == 'c':
        throwDelay = 1.45
        damageDelay = 2.61
        dodgeDelay = 2.34
    suitTrack = getSuitTrack(attack)
    tiePropTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tie = globalPropPool.getProp('power-tie')
        posPoints = [Point3(1.16, 0.24, 0.63), VBase3(171.561, 1.745, -163.443)]
        tiePropTrack = Sequence(getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, Point3(3.5, 3.5, 3.5), scaleUpTime=0.5))
        tiePropTrack.append(Wait(throwDelay))
        tiePropTrack.append(Func(tie.setBillboardPointEye))
        tiePropTrack.append(getPropThrowTrack(attack, tie, [__toonFacePoint(toon)], [__toonGroundPoint(attack, toon, 0.1)], hitDuration=0.4, missDuration=0.8, target=t))
        tiePropTracks += (tiePropTrack,)

    toonTracks = getToonTracks(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    throwSound = getSoundTrack('SA_powertie_throw.ogg', delay=throwDelay + 0.85, node=suit)
    if hitAtleastOneToon(targets):
        hitSound = getSoundTrack('SA_powertie_impact.ogg', delay=throwDelay + 1.45, node=suit)
        return Parallel(suitTrack, toonTracks, tiePropTracks, throwSound, hitSound)
    else:
        return Parallel(suitTrack, toonTracks, tiePropTracks, throwSound)


def doDoubleTalk(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    textureNames: Tuple[str, ...] = ('doubletalk-double', 'doubletalk-good')
    particleEffect = BattleParticles.createParticleEffect('DoubleTalkLeft')
    particleEffect2 = BattleParticles.createParticleEffect('DoubleTalkRight')
    BattleParticles.setEffectTexture(particleEffect, textureNames, color=Vec4(0, 1.0, 0.0, 1))
    BattleParticles.setEffectTexture(particleEffect2, textureNames, color=Vec4(0, 1.0, 0.0, 1))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 3.3
        damageDelay = 3.5
        dodgeDelay = 3.3
    elif suitType == 'b':
        partDelay = 3.3
        damageDelay = 3.5
        dodgeDelay = 3.3
    elif suitType == 'c':
        partDelay = 3.3
        damageDelay = 3.5
        dodgeDelay = 3.3
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, partDelay, 1.8, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, partDelay, 1.8, [particleEffect2, suit, 0])
    damageAnims = [['duck',
      0.01,
      0.4,
      1.05], ['cringe', 1e-06, 0.8]]
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=[['duck', 0.01, 1.4]], showMissedExtraTime=0.9, showDamageExtraTime=0.8)
    soundTrack = getSoundTrack('SA_filibuster.ogg', delay=2.5, node=suit)
    return Parallel(suitTrack, toonTracks, partTrack, partTrack2, soundTrack)


def doFreezeAssets(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.3
    elif suitType == 'b':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.3
    elif suitType == 'c':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.3
    suitTrack = getSuitTrack(attack, delay=0.9)
    cloudPropTracks = ()
    for t in targets:
        toon = t['toon']
        snowEffect = BattleParticles.createParticleEffect('FreezeAssets')
        BattleParticles.setEffectTexture(snowEffect, 'snow-particle')
        cloud = globalPropPool.getProp('stormcloud')
        initialCloudHeight = suit.height + 3
        cloudPosPoints = [Point3(0, 3, initialCloudHeight), MovieUtil.PNT3_ZERO]
        cloudPropTrack = Sequence()
        cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
        cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.7))
        cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
        cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack.append(Wait(1.1))
        cloudPropTrack.append(LerpPosInterval(cloud, 1, pos=targetPoint))
        cloudPropTrack.append(Wait(partDelay))
        cloudPropTrack.append(ParticleInterval(snowEffect, cloud, worldRelative=0, duration=2.1, cleanup=True))
        cloudPropTrack.append(Wait(0.4))
        cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
        cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
        cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
        cloudPropTracks += (cloudPropTrack,)

    damageAnims = [['cringe',
      0.01,
      0.4,
      0.8], ['duck', 0.01, 1.6]]
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.2)
    return Parallel(suitTrack, toonTracks, *cloudPropTracks)


def doHotAir(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    BattleParticles.loadParticles()
    sprayEffect = BattleParticles.createParticleEffect('HotAir')
    baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame')
    flameEffect = BattleParticles.createParticleEffect('FiredFlame')
    flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
    BattleParticles.setEffectTexture(sprayEffect, 'fire')
    BattleParticles.setEffectTexture(baseFlameEffect, 'fire')
    BattleParticles.setEffectTexture(flameEffect, 'fire')
    BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.95, 0.95, 0.0, 1))
    sprayDelay = 1.3
    flameDelay = 3.2
    flameDuration = 2.6
    flecksDelay = flameDelay + 0.8
    flecksDuration = flameDuration - 0.8
    damageDelay = 3.6
    dodgeDelay = 2.0
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, sprayDelay, 2.3, [sprayEffect, suit, 0])
    baseFlameTrack = getPartTrack(baseFlameEffect, flameDelay, flameDuration, [baseFlameEffect, toon, 0])
    flameTrack = getPartTrack(flameEffect, flameDelay, flameDuration, [flameEffect, toon, 0])
    flecksTrack = getPartTrack(flecksEffect, flecksDelay, flecksDuration, [flecksEffect, toon, 0])
    if dmg > 0:
        colorTrack = getColorTrack(battle, toon, 4.0, 3.5, Vec4(0, 0, 0, 1))
    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.7,
     0.62])
    damageAnims.append(['slip-forward',
     0.01,
     0.4,
     1.2])
    damageAnims.append(['slip-forward', 0.01, 1.0])
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=1.6, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, sprayTrack, soundTrack, baseFlameTrack, flameTrack, flecksTrack, colorTrack)
    else:
        return Parallel(suitTrack, toonTrack, sprayTrack, soundTrack)


def doPickPocket(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    bill = globalPropPool.getProp('1dollar')
    suitTrack = getSuitTrack(attack)
    billPosPoints = [Point3(-0.01, 0.45, -0.25), VBase3(136.424, -46.434, -129.712)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.6, 0.55, scaleUpPoint=Point3(1.41, 1.41, 1.41))
    toonTrack = getToonTrack(attack, 0.6, ['cringe'], 0.01, ['sidestep'])
    multiTrackList = Parallel(suitTrack, toonTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('SA_pick_pocket.ogg', delay=0.2, node=suit)
        multiTrackList.append(billPropTrack)
        multiTrackList.append(soundTrack)
    return multiTrackList


def doFilibuster(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    battle = attack['battle']
    BattleParticles.loadParticles()
    textureNames: Tuple[str, ...] = ('filibuster-cut',
     'filibuster-fiscal',
     'filibuster-impeach',
     'filibuster-inc')
    sprayEffect = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect2 = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect3 = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect4 = BattleParticles.createParticleEffect(file='filibusterSpray')
    color = Vec4(0.4, 0, 0, 1)
    BattleParticles.setEffectTexture(sprayEffect, textureNames, color=color)
    BattleParticles.setEffectTexture(sprayEffect2, textureNames, color=color)
    BattleParticles.setEffectTexture(sprayEffect3, textureNames, color=color)
    BattleParticles.setEffectTexture(sprayEffect4, textureNames, color=color)
    partDelay = 1.3
    partDuration = 1.15
    damageDelay = 2.45
    dodgeDelay = 1.7
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, partDelay, partDuration, [sprayEffect, suit, 0])
    sprayTrack2 = getPartTrack(sprayEffect2, partDelay + 0.8, partDuration, [sprayEffect2, suit, 0])
    sprayTrack3 = getPartTrack(sprayEffect3, partDelay + 1.6, partDuration, [sprayEffect3, suit, 0])
    sprayTrack4 = getPartTrack(sprayEffect4, partDelay + 2.4, partDuration, [sprayEffect4, suit, 0])
    damageAnims = []
    for i in range(0, 3):
        damageAnims.append(['cringe',
         1e-05,
         0.3,
         0.8])

    damageAnims.append(['cringe', 1e-05, 0.3])
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_filibuster.ogg', delay=1.1, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, soundTrack, sprayTrack, sprayTrack2, sprayTrack3, sprayTrack4)
    else:
        return Parallel(suitTrack, toonTrack, soundTrack, sprayTrack, sprayTrack2, sprayTrack3)


def doSchmooze(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    upperEffects = []
    lowerEffects = []
    textureNames: Tuple[str, ...] = ('schmooze-genius',
     'schmooze-instant',
     'schmooze-master',
     'schmooze-viz')
    for i in range(0, 4):
        upperEffect = BattleParticles.createParticleEffect(file='schmoozeUpperSpray')
        lowerEffect = BattleParticles.createParticleEffect(file='schmoozeLowerSpray')
        # Two particle effects simulate what looks like one particle effect, so be sure the textures, while being random, appear consistent.
        name = random.choice(textureNames)
        BattleParticles.setEffectTexture(upperEffect, name, color=Vec4(0, 0, 1, 1))
        BattleParticles.setEffectTexture(lowerEffect, name, color=Vec4(0, 0, 1, 1))
        upperEffects.append(upperEffect)
        lowerEffects.append(lowerEffect)

    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 1.3
        damageDelay = 1.8
        dodgeDelay = 1.1
    elif suitType == 'b':
        partDelay = 1.3
        damageDelay = 2.5
        dodgeDelay = 1.8
    elif suitType == 'c':
        partDelay = 1.3
        damageDelay = partDelay + 1.4
        dodgeDelay = 0.9
    suitTrack = getSuitTrack(attack)
    upperPartTracks = Parallel()
    lowerPartTracks = Parallel()
    for i in range(0, 4):
        upperPartTracks.append(getPartTrack(upperEffects[i], partDelay + i * 0.65, 0.8, [upperEffects[i], suit, 0]))
        lowerPartTracks.append(getPartTrack(lowerEffects[i], partDelay + i * 0.65 + 0.7, 1.0, [lowerEffects[i], suit, 0]))

    damageAnims = []
    for i in range(0, 3):
        damageAnims.append(['conked',
         0.01,
         0.3,
         0.71])

    damageAnims.append(['conked', 0.01, 0.3])
    dodgeAnims = []
    dodgeAnims.append(['duck',
     0.01,
     0.2,
     2.7])
    dodgeAnims.append(['duck',
     0.01,
     1.22,
     1.28])
    dodgeAnims.append(['duck', 0.01, 3.16])
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.9, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTrack, upperPartTracks, lowerPartTracks)


def doQuake(attack):
    suit = attack['suit']
    suitTrack = getSuitAnimTrack(attack)
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01], ['jump', 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=1.8, splicedDamageAnims=damageAnims, dodgeDelay=1.1, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTracks)


def doShake(attack):
    suit = attack['suit']
    suitTrack = getSuitAnimTrack(attack)
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=1.1, splicedDamageAnims=damageAnims, dodgeDelay=0.7, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTracks)


def doTremor(attack):
    suit = attack['suit']
    suitTrack = getSuitAnimTrack(attack)
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=1.1, splicedDamageAnims=damageAnims, dodgeDelay=0.7, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    soundTrack = getSoundTrack('SA_tremor.ogg', delay=0.9, node=suit)
    return Parallel(suitTrack, soundTrack, toonTracks)


def doHangUp(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = getSuitTrack(attack)
    propTrack = getPhoneTrack(suit)
    toonTracks = getToonTracks(attack, 5.5, ['slip-backward'], 4.7, ['jump'])
    return Parallel(suitTrack, toonTracks, propTrack)


def doRedTape(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = getSuitTrack(attack)
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        tapePosPoints = [Point3(-0.24, 0.09, -0.38), VBase3(-1.152, 86.581, -76.784)]
    else:
        tapePosPoints = [Point3(0.24, 0.09, -0.38), VBase3(-1.152, 86.581, -76.784)]
    tapeScaleUpPoint = Point3(0.9, 0.9, 0.24)
    propTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tape = globalPropPool.getProp('redtape')
        tubes = []
        for i in range(0, 3):
            tubes.append(globalPropPool.getProp('redtape-tube'))

        propTrack = Sequence(getPropAppearTrack(tape, suit.getRightHand(), tapePosPoints, 0.8, tapeScaleUpPoint, scaleUpTime=0.5))
        propTrack.append(Wait(1.73))
        hitPoint = lambda toon = toon: __toonTorsoPoint(toon)
        propTrack.append(getPropThrowTrack(attack, tape, [hitPoint], [__toonGroundPoint(attack, toon, 0.7)], target=t))
        hips = toon.getHipsParts()
        animal = toon.style.getAnimal()
        scale = ToontownGlobals.toonBodyScales[animal]
        legs = toon.style.legs
        torso = toon.style.torso
        torso = torso[0]
        animal = animal[0]
        tubeHeight = -0.8
        if torso == 's':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 0.7975)
        elif torso == 'm':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 0.7975)
        elif torso == 'l':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 1.11)
        if animal in ('h', 'd'):
            tubeHeight = -0.87
            scaleUpPoint = Point3(scale * 1.69, scale * 1.69, scale * 0.67)
        tubePosPoints = [Point3(0, 0, tubeHeight), MovieUtil.PNT3_ZERO]
        tubeTracks = Parallel()
        tubeTracks.append(Func(battle.movie.needRestoreHips))
        for partNum in range(0, hips.getNumPaths()):
            nextPart = hips.getPath(partNum)
            tubeTracks.append(getPropTrack(tubes[partNum], nextPart, tubePosPoints, 3.25, 3.17, scaleUpPoint=scaleUpPoint))
        
        tubeTracks.append(Func(battle.movie.clearRestoreHips))
        propTracks += (propTrack,)
        if dmg > 0:
            propTracks += (tubeTracks,)

    toonTracks = getToonTracks(attack, 3.4, ['struggle'], 2.8, ['jump'])
    soundTrack = getSoundTrack('SA_red_tape.ogg', delay=2.9, node=suit)
    return Parallel(suitTrack, toonTracks, *propTracks, soundTrack)


def doParadigmShift(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.95
    dodgeDelay = 0.95
    sprayEffect = BattleParticles.createParticleEffect('ShiftSpray')
    suitName = suit.getStyleName()
    sprayEffect.setPos(Point3(-5.2, 4.6, 2.7))
    suitTrack = getSuitAnimTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    liftTracks = Parallel()
    toonRiseTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            liftEffect = BattleParticles.createParticleEffect('ShiftLift')
            liftEffect.setPos(toon.getPos(battle))
            liftEffect.setZ(liftEffect.getZ() - 1.3)
            liftTracks.append(getPartTrack(liftEffect, 1.1, 4.1, [liftEffect, battle, 0]))
            shadow = toon.dropShadow
            fakeShadow = MovieUtil.copyProp(shadow)
            x = toon.getX()
            y = toon.getY()
            z = toon.getZ()
            height = 3
            groundPoint = Point3(x, y, z)
            risePoint = Point3(x, y, z + height)
            shakeRight = Point3(x, y + 0.7, z + height)
            shakeLeft = Point3(x, y - 0.7, z + height)
            shakeTrack = Sequence()
            shakeTrack.append(Wait(damageDelay + 0.25))
            shakeTrack.append(Func(shadow.hide))
            shakeTrack.append(LerpPosInterval(toon, 1.1, risePoint))
            for i in range(0, 17):
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeLeft))
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeRight))

            shakeTrack.append(LerpPosInterval(toon, 0.1, risePoint))
            shakeTrack.append(LerpPosInterval(toon, 0.1, groundPoint))
            shakeTrack.append(Func(shadow.show))
            shadowTrack = Sequence()
            shadowTrack.append(Func(battle.movie.needRestoreRenderProp, fakeShadow))
            shadowTrack.append(Wait(damageDelay + 0.25))
            shadowTrack.append(Func(fakeShadow.hide))
            shadowTrack.append(Func(fakeShadow.setScale, 0.27))
            shadowTrack.append(Func(fakeShadow.reparentTo, toon))
            shadowTrack.append(Func(fakeShadow.setPos, MovieUtil.PNT3_ZERO))
            shadowTrack.append(Func(fakeShadow.wrtReparentTo, battle))
            shadowTrack.append(Func(fakeShadow.show))
            shadowTrack.append(LerpScaleInterval(fakeShadow, 0.4, Point3(0.17, 0.17, 0.17)))
            shadowTrack.append(Wait(1.81))
            shadowTrack.append(LerpScaleInterval(fakeShadow, 0.1, Point3(0.27, 0.27, 0.27)))
            shadowTrack.append(Func(MovieUtil.removeProp, fakeShadow))
            shadowTrack.append(Func(battle.movie.clearRenderProp, fakeShadow))
            toonRiseTracks.append(Parallel(shakeTrack, shadowTrack))

    damageAnims = []
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.9, startTime=2.06))
    damageAnims.append(['slip-backward', 0.01, 0.5])
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.0, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=2.7)
    if hitAtleastOneToon(targets):
        soundTrack = getSoundTrack('SA_paradigm_shift.ogg', delay=2.1, node=suit)
        return Parallel(suitTrack, sprayTrack, soundTrack, liftTracks, toonTracks, toonRiseTracks)
    else:
        return Parallel(suitTrack, sprayTrack, liftTracks, toonTracks, toonRiseTracks)


def doPowerTrip(attack):
    suit = attack['suit']
    battle = attack['battle']
    centerColor = Vec4(0.1, 0.1, 0.1, 0.4)
    edgeColor = Vec4(0.4, 0.1, 0.9, 0.7)
    powerBar1 = BattleParticles.createParticleEffect(file='powertrip')
    powerBar2 = BattleParticles.createParticleEffect(file='powertrip2')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-60, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(60, 0, 0)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitName = suit.getStyleName()
    if suitName == 'mh':
        waterfallEffect.setPos(0, 4, 3.6)
    suitTrack = getSuitAnimTrack(attack)

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(1.0), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 1.3, [waterfallEffect, suit, 0])
    toonTracks = getToonTracks(attack, 1.8, ['slip-forward'], 1.29, ['jump'])
    return Parallel(suitTrack, partTrack1, partTrack2, waterfallTrack, toonTracks)


def getThrowEndPoint(suit, toon, battle, whichBounce):
    pnt = toon.getPos(toon)
    if whichBounce == 'one':
        pnt.setY(pnt[1] + 8)
    elif whichBounce == 'two':
        pnt.setY(pnt[1] + 5)
    elif whichBounce == 'threeHit':
        pnt.setZ(pnt[2] + toon.shoulderHeight + 0.3)
    elif whichBounce == 'threeMiss':
        pass
    elif whichBounce == 'four':
        pnt.setY(pnt[1] - 5)
    return Point3(pnt)


def doBounceCheck(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    checkPosPoints = [MovieUtil.PNT3_ZERO, VBase3(95.247, 79.025, 88.849)]
    suitType = getSuitBodyType(attack['suitName'])
    if suitType in ('a', 'b'):
        throwDelay = 2.5
        dodgeDelay = 4.3
        damageDelay = 5.1
    elif suitType == 'c':
        throwDelay = 1.8
        dodgeDelay = 3.6
        damageDelay = 4.4
    suitTrack = getSuitTrack(attack)
    checkPropTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        check = globalPropPool.getProp('bounced-check')
        bounce1Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'one')
        bounce2Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'two')
        hit3Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'threeHit')
        miss3Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'threeMiss')
        bounce4Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'four')
        checkPropTrack = Sequence(getPropAppearTrack(check, suit.getRightHand(), checkPosPoints, 1e-05, Point3(8.5, 8.5, 8.5), startScale=MovieUtil.PNT3_ONE))
        checkPropTrack.append(Wait(throwDelay))
        checkPropTrack.append(Func(check.wrtReparentTo, toon))
        checkPropTrack.append(Func(check.setHpr, Point3(0, -90, 0)))
        checkPropTrack.append(getThrowTrack(check, bounce1Point, duration=0.5, parent=toon))
        checkPropTrack.append(getThrowTrack(check, bounce2Point, duration=0.9, parent=toon))
        if dmg > 0:
            checkPropTrack.append(getThrowTrack(check, hit3Point, duration=0.7, parent=toon))
        else:
            checkPropTrack.append(getThrowTrack(check, miss3Point, duration=0.7, parent=toon))
            checkPropTrack.append(getThrowTrack(check, bounce4Point, duration=0.7, parent=toon))
            checkPropTrack.append(LerpScaleInterval(check, 0.3, MovieUtil.PNT3_NEARZERO))
        checkPropTrack.append(Func(MovieUtil.removeProp, check))
        checkPropTracks += (checkPropTrack,)

    toonTracks = getToonTracks(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    soundTracks = Sequence(getSoundTrack('SA_pink_slip.ogg', delay=throwDelay + 0.5, duration=0.6, node=suit), getSoundTrack('SA_pink_slip.ogg', delay=0.4, duration=0.6, node=suit))
    return Parallel(suitTrack, *checkPropTracks, toonTracks, soundTracks)


def doWatercooler(attack):
    suit = attack['suit']
    battle = attack['battle']
    # TODO: Have a more sophisticated system for multiple targets on a single-target attack.
    targets = attack['target']
    watercooler = globalPropPool.getProp('watercooler')

    def getCoolerSpout(watercooler = watercooler):
        spout = watercooler.find('**/joint_toSpray')
        return spout.getPos(render)

    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(0.48, 0.11, -0.92), VBase3(20.403, 33.158, 69.511)]
    propTrack = Sequence(Wait(1.01), Func(__showProp, watercooler, suit.getLeftHand(), posPoints[0], posPoints[1]), LerpScaleInterval(watercooler, 0.5, Point3(1.15, 1.15, 1.15)), Wait(1.6))
    sprayTracks = Parallel()
    for t in targets:
        toon = t['toon']
        hitPoint = lambda toon = toon: __toonFacePoint(toon)
        missPoint = lambda prop = watercooler, toon = toon: __toonMissPoint(prop, toon, 0, parent=render)
        sprayTrack = MovieUtil.getSprayTrack(battle, Point4(0.75, 0.75, 1.0, 0.8), getCoolerSpout, hitPoint if t['hp'] > 0 else missPoint, 0.2, 0.2, 0.2, horizScale=0.3, vertScale=0.3)
        sprayTracks.append(sprayTrack)

    propTrack.append(sprayTracks)
    propTrack += [Wait(0.01), LerpScaleInterval(watercooler, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProp, watercooler)]
    splashTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        splashTrack = Sequence()
        if dmg > 0:
        
            def prepSplash(splash, targetPoint):
                splash.reparentTo(render)
                splash.setPos(targetPoint)
                scale = splash.getScale()
                splash.setBillboardPointWorld()
                splash.setScale(scale)
        
            splash = globalPropPool.getProp('splash-from-splat')
            splash.setColor(0.75, 0.75, 1, 0.8)
            splash.setScale(0.3)
            splashTrack = Sequence(Func(battle.movie.needRestoreRenderProp, splash), Wait(3.2), Func(prepSplash, splash, __toonFacePoint(toon)), ActorInterval(splash, 'splash-from-splat'), Func(MovieUtil.removeProp, splash), Func(battle.movie.clearRenderProp, splash))
            splashTracks += (splashTrack,)

    toonTracks = getToonTracks(attack, suitTrack.getDuration() - 1.5, ['cringe'], 2.4, ['sidestep'])
    soundTrack = Sequence(Wait(1.1), SoundInterval(globalBattleSoundCache.getSound('SA_watercooler_appear_only.ogg'), node=suit, duration=1.4722), Wait(0.4), SoundInterval(globalBattleSoundCache.getSound('SA_watercooler_spray_only.ogg'), node=suit, duration=2.313))
    return Parallel(suitTrack, toonTracks, propTrack, soundTrack, *splashTracks)


def doFired(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    suitTrack = getSuitTrack(attack)
    partTracks = ()
    colorTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame')
        flameEffect = BattleParticles.createParticleEffect('FiredFlame')
        flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(baseFlameEffect, 'fire')
        BattleParticles.setEffectTexture(flameEffect, 'fire')
        BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.8, 0.8, 0.8, 1))
        baseFlameSmall = BattleParticles.createParticleEffect(file='firedBaseFlame')
        flameSmall = BattleParticles.createParticleEffect('FiredFlame')
        flecksSmall = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(baseFlameSmall, 'fire')
        BattleParticles.setEffectTexture(flameSmall, 'fire')
        BattleParticles.setEffectTexture(flecksSmall, 'roll-o-dex', color=Vec4(0.8, 0.8, 0.8, 1))
        baseFlameSmall.setScale(0.7)
        flameSmall.setScale(0.7)
        flecksSmall.setScale(0.7)
        baseFlameTrack = getPartTrack(baseFlameEffect, 1.0, 1.9, [baseFlameEffect, toon, 0])
        flameTrack = getPartTrack(flameEffect, 1.0, 1.9, [flameEffect, toon, 0])
        flecksTrack = getPartTrack(flecksEffect, 1.8, 1.1, [flecksEffect, toon, 0])
        baseFlameSmallTrack = getPartTrack(baseFlameSmall, 1.0, 1.9, [baseFlameSmall, toon, 0])
        flameSmallTrack = getPartTrack(flameSmall, 1.0, 1.9, [flameSmall, toon, 0])
        flecksSmallTrack = getPartTrack(flecksSmall, 1.8, 1.1, [flecksSmall, toon, 0])
        if dmg > 0:
            colorTrack = getColorTrack(battle, toon, 2.0, 3.5, Vec4(0, 0, 0, 1))
            partTracks += (baseFlameTrack, flameTrack, flecksTrack)
            colorTracks += (colorTrack,)
        else:
            partTracks += (baseFlameSmallTrack, flameSmallTrack, flecksSmallTrack)

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.7,
     0.62])
    damageAnims.append(['slip-forward',
     1e-05,
     0.4,
     1.2])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.8, startTime=1.2))
    toonTracks = getToonTracks(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=0.3, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=1.0, node=suit)
    return Parallel(suitTrack, *partTracks, toonTracks, *colorTracks, soundTrack)


def doAudit(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    calculator = globalPropPool.getProp('calculator')
    BattleParticles.loadParticles()
    textureNames: Tuple[str, ...] = ('audit-div',
     'audit-five',
     'audit-four',
     'audit-minus',
     'audit-mult',
     'audit-one',
     'audit-plus',
     'audit-six',
     'audit-three',
     'audit-two')
    particleEffect = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect, textureNames, color=Vec4(0, 0, 0, 1))
    particleEffect2 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect2, textureNames, color=Vec4(0, 0, 0, 1))
    particleEffect3 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect3, textureNames, color=Vec4(0, 0, 0, 1))
    particleEffect4 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect4, textureNames, color=Vec4(0, 0, 0, 1))
    particleEffect5 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect5, textureNames, color=Vec4(0, 0, 0, 1))
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, 2.1, 1.9, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, 2.2, 2.0, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, 2.3, 2.1, [particleEffect3, suit, 0])
    partTrack4 = getPartTrack(particleEffect4, 2.4, 2.2, [particleEffect4, suit, 0])
    partTrack5 = getPartTrack(particleEffect5, 2.5, 2.3, [particleEffect5, suit, 0])
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        calcPosPoints = [Point3(-0.15, 0.37, 0.03), VBase3(1.352, -6.518, -6.045)]
        calcDuration = 0.76
        scaleUpPoint = Point3(1.1, 1.85, 1.81)
    else:
        calcPosPoints = [Point3(0.35, 0.52, 0.03), VBase3(1.352, -6.518, -6.045)]
        calcDuration = 1.87
        scaleUpPoint = Point3(1.0, 1.37, 1.31)
    calcPropTrack = getPropTrack(calculator, suit.getLeftHand(), calcPosPoints, 1e-06, calcDuration, scaleUpPoint=scaleUpPoint, anim=1, propName='calculator', animStartTime=0.5, animDuration=3.4)
    if attack['identifier'] in ('ttrealms:calculate', 'ttrealms:tabulate'):
        # Preserve the dodge attributes from the Calculate and Tabulate attacks.
        # I'd like to not have this so that the Toon ducks regardless of attack because I plan to eventually give these attacks the option to hit all Toons, but I'm not sure how the Toontown Realms team would feel about that.
        dodgeDelay = 1.8
        dodgeAnims = ['sidestep']
        showMissedExtraTime = 0.5
    else:
        dodgeDelay = 0.9
        dodgeAnims = ['duck']
        showMissedExtraTime = 2.2
    toonTrack = getToonTrack(attack, 3.2, ['conked'], dodgeDelay, dodgeAnims, showMissedExtraTime=showMissedExtraTime)
    soundTrack = getSoundTrack('SA_audit.ogg', delay=1.9, node=suit)
    return Parallel(suitTrack, toonTrack, calcPropTrack, soundTrack, partTrack, partTrack2, partTrack3, partTrack4, partTrack5)


def doCrunch(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    throwDuration = 3.03
    suitTrack = getSuitTrack(attack)
    BattleParticles.loadParticles()
    textureNames: Tuple[str, ...] = ('audit-five',
     'audit-four',
     'audit-one',
     'audit-six',
     'audit-three',
     'audit-two')
    numberSpill1 = BattleParticles.createParticleEffect(file='numberSpill')
    numberSpill2 = BattleParticles.createParticleEffect(file='numberSpill')
    BattleParticles.setEffectTexture(numberSpill1, textureNames)
    BattleParticles.setEffectTexture(numberSpill2, textureNames)
    numberSpillTrack1 = getPartTrack(numberSpill1, 1.1, 2.2, [numberSpill1, suit, 0])
    numberSpillTrack2 = getPartTrack(numberSpill2, 1.5, 1.0, [numberSpill2, suit, 0])
    numberSprayTracks = Parallel()
    numOfNumbers = random.randint(5, 9)
    for i in range(0, numOfNumbers - 1):
        nextSpray = BattleParticles.createParticleEffect(file='numberSpray')
        BattleParticles.setEffectTexture(nextSpray, textureNames)
        nextStartTime = random.random() * 0.6 + throwDuration
        nextDuration = random.random() * 0.4 + 1.4
        nextSprayTrack = getPartTrack(nextSpray, nextStartTime, nextDuration, [nextSpray, suit, 0])
        numberSprayTracks.append(nextSprayTrack)

    numberTracks = Parallel()
    for i in range(0, numOfNumbers):
        next = MovieUtil.copyProp(BattleParticles.getParticle(random.choice(textureNames)))
        next.reparentTo(suit.getRightHand())
        next.setScale(0.01, 0.01, 0.01)
        next.setColor(Vec4(0.0, 0.0, 0.0, 1.0))
        next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
        next.setHpr(VBase3(-1.15, 86.58, -76.78))
        numberTrack = Sequence(Wait(0.9), LerpScaleInterval(next, 0.6, MovieUtil.PNT3_ONE), Wait(1.7), Func(MovieUtil.removeProp, next))
        numberTracks.append(numberTrack)

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.14,
     0.28])
    damageAnims.append(['cringe',
     0.01,
     0.16,
     0.3])
    damageAnims.append(['cringe',
     0.01,
     0.13,
     0.22])
    damageAnims.append(['slip-forward', 0.01, 0.6])
    toonTrack = getToonTrack(attack, damageDelay=4.7, splicedDamageAnims=damageAnims, dodgeDelay=3.6, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, toonTrack, numberSpillTrack1, numberSpillTrack2, numberTracks, numberSprayTracks)


def doLiquidate(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.45
    elif suitType == 'b':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.45
    elif suitType == 'c':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.45
    suitTrack = getSuitTrack(attack, delay=0.9)
    cloudPropTracks = ()
    puddleTracks = ()
    for t in targets:
        dmg = t['hp']
        toon = t['toon']
        rainEffect = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect2 = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect3 = BattleParticles.createParticleEffect(file='liquidate')
        cloud = globalPropPool.getProp('stormcloud')
        initialCloudHeight = suit.height + 3
        cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
        cloudPropTrack = Sequence()
        cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
        cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.7))
        cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
        cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack.append(Wait(1.1))
        cloudPropTrack.append(LerpPosInterval(cloud, 1, pos=targetPoint))
        cloudPropTrack.append(Wait(partDelay))
        cloudPropTrack.append(Parallel(Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=2.1, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
        cloudPropTrack.append(Wait(0.4))
        cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
        cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
        cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
        cloudPropTracks += (cloudPropTrack,)
        if dmg > 0:
            puddle = globalPropPool.getProp('quicksand')
            puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
            puddle.setHpr(Point3(120, 0, 0))
            puddle.setScale(0.01)
            puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Wait(damageDelay - 0.7), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
            puddleTracks += (puddleTrack,)

    toonTracks = Parallel() # Unique toonTracks to account for a Cog disguise.  Previous iteration had flexOnEx and prop parameters, which I'm not going to worry about for now because both arguments are eventually unused in getToonTakeDamageTrack.
    for i in range(len(targets)):
        tgt = targets[i]
        toon = tgt['toon']
        if not toon.getTransformationsIndex(0):
            damageAnims = [['melt'], ['jump', 1.5, 0.4]]
            toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], target=tgt)
        else:
            toonTrack = getToonTrack(attack, 3.5, ['suitQuicksandAnim'], 2.45, ['sidestep'], target=tgt)
        toonTracks.append(toonTrack)

    soundTrack = getSoundTrack('SA_liquidate.ogg', delay=2.0, node=suit)
    return Parallel(suitTrack, toonTracks, *cloudPropTracks, soundTrack, *puddleTracks)


def doMarketCrash(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitDelay = 1.32
    propDelay = 0.6
    throwDuration = 1.5
    suitTrack = getSuitTrack(attack)
    propTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        paper = globalPropPool.getProp('newspaper')
        posPoints = [Point3(-0.07, 0.17, -0.13), Point3(-169.69, -36.03, -39.289)]
        paperIvals = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(3, 3, 3), scaleUpTime=0.5))
        paperIvals.append(Wait(suitDelay))
        hitPoint = toon.getPos(battle)
        hitPoint.setX(hitPoint.getX() + 1.5)
        hitPoint.setY(hitPoint.getY() + 1.5)
        if dmg > 0:
            hitPoint.setZ(hitPoint.getZ() + 1.1)
    
        movePoint = Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ() + 0.2)
        paperIvals.append(Func(battle.movie.needRestoreRenderProp, paper))
        paperIvals.append(Func(paper.wrtReparentTo, battle))
        paperIvals.extend(getThrowTrack(paper, hitPoint, duration = throwDuration, parent = battle))
        paperIvals.append(Wait(0.6))
        paperIvals.append(LerpPosInterval(paper, 0.4, movePoint))
        spinTrack = Sequence(
            Wait(propDelay + suitDelay + 0.2),
            LerpHprInterval(paper, throwDuration, Point3(180, 0, 180)))
        sizeTrack = Sequence(
            Wait(propDelay + suitDelay + 0.2),
            LerpScaleInterval(paper, throwDuration, Point3(6, 6, 6)),
            Wait(0.949),
            LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
        propTrack = Sequence(
            Parallel(
                paperIvals,
                spinTrack,
                sizeTrack),
            Func(MovieUtil.removeProp, paper),
            Func(battle.movie.clearRenderProp, paper))
        propTracks += (propTrack,)

    damageAnims = []
    damageAnims.append([
        'cringe',
        0.01,
        0.21,
        0.08])
    damageAnims.append([
        'slip-forward',
        0.01,
        0.6,
        0.85])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.95, startTime = 1.2))
    damageAnims.append([
        'slip-forward',
        0.01,
        1.51])
    toonTracks = getToonTracks(attack, damageDelay=3.8, splicedDamageAnims=damageAnims, dodgeDelay=2.4, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    return Parallel(suitTrack, toonTracks, *propTracks)



def doBite(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    propDelay = 0.8
    propScaleUpTime = 0.5
    suitDelay = 1.73
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.4
    suitTrack = getSuitTrack(attack)
    propTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        teeth = globalPropPool.getProp('teeth')
        posPoints = [Point3(-0.05, 0.41, -0.54), VBase3(4.465, -3.563, 51.479)]
        teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(3, 3, 3), scaleUpTime=propScaleUpTime))
        teethAppearTrack.append(Wait(suitDelay))
        teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
        teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
        if dmg > 0:
            x = toon.getX(battle)
            y = toon.getY(battle)
            z = toon.getZ(battle)
            toonHeight = z + toon.getHeight()
            flyPoint = Point3(x, y + 2.7, toonHeight * 0.8)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5)))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 0.2, toonHeight * 0.9)))
            teethAppearTrack.append(Wait(0.4))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(teeth, throwDuration, Point3(8, 8, 8)), Wait(0.9), LerpScaleInterval(teeth, 0.2, Point3(14, 14, 14)), Wait(1.2), LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO))
            hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2), LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.6), LerpHprInterval(teeth, 0.1, Point3(180, -75, 0), startHpr=Point3(180, -35, 0)))
            animTrack = Sequence(
                Wait(throwDelay), 
                ActorInterval(teeth, 'teeth', duration=throwDuration), 
                ActorInterval(teeth, 'teeth', duration=0.3), 
                Func(teeth.pose, 'teeth', 1), 
                Wait(0.7), 
                ActorInterval(teeth, 'teeth', duration=0.1),
                ActorInterval(teeth, 'teeth', duration=0.1),
                ActorInterval(teeth, 'teeth', duration=0.1),
                ActorInterval(teeth, 'teeth', duration=0.1),
                ActorInterval(teeth, 'teeth', duration=0.1),
                ActorInterval(teeth, 'teeth', duration=0.1),
                ActorInterval(teeth, 'teeth', duration=0.1))
            propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack), Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
        else:
            flyPoint = __toonFacePoint(toon, parent=battle)
            flyPoint.setY(flyPoint.getY() - 7.1)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(Func(MovieUtil.removeProp, teeth))
            teethAppearTrack.append(Func(battle.movie.clearRenderProp, teeth))
            propTrack = teethAppearTrack
        propTracks += (propTrack,)

    damageAnims = [['cringe',
      0.01,
      0.7,
      1.2], ['conked',
      0.01,
      0.2,
      2.1], ['conked', 0.01, 3.2]]
    dodgeAnims = [['cringe',
      0.01,
      0.7,
      0.2], ['duck', 0.01, 1.6]]
    toonTracks = getToonTracks(attack, damageDelay=3.2, splicedDamageAnims=damageAnims, dodgeDelay=2.9, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=2.4)
    return Parallel(suitTrack, toonTracks, *propTracks)


def doChomp(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    propDelay = 0.8
    propScaleUpTime = 0.5
    suitDelay = 1.73
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.4
    suitTrack = getSuitTrack(attack)
    propTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        teeth = globalPropPool.getProp('teeth')
        posPoints = [Point3(-0.05, 0.41, -0.54), VBase3(4.465, -3.563, 51.479)]
        teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(3, 3, 3), scaleUpTime=propScaleUpTime))
        teethAppearTrack.append(Wait(suitDelay))
        teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
        teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
        if dmg > 0:
            x = toon.getX(battle)
            y = toon.getY(battle)
            z = toon.getZ(battle)
            toonHeight = z + toon.getHeight()
            flyPoint = Point3(x, y + 2.7, toonHeight * 0.7)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5)))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y, toonHeight + 3)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 1.2, toonHeight * 0.7)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 0.7, toonHeight * 0.4)))
            teethAppearTrack.append(Wait(0.4))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(teeth, throwDuration, Point3(6, 6, 6)), Wait(0.9), LerpScaleInterval(teeth, 0.2, Point3(10, 10, 10)), Wait(1.2), LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO))
            hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2), LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.6), LerpHprInterval(teeth, 0.1, Point3(0, -35, 0), startHpr=Point3(180, -35, 0)))
            animTrack = Sequence(
                Wait(throwDelay), 
                ActorInterval(teeth, 'teeth', duration=throwDuration), 
                ActorInterval(teeth, 'teeth', duration=0.3), 
                Func(teeth.pose, 'teeth', 1), 
                Wait(0.7), 
                ActorInterval(teeth, 'teeth', duration=0.1),
                ActorInterval(teeth, 'teeth', duration=0.1),
                ActorInterval(teeth, 'teeth', duration=0.1),
                ActorInterval(teeth, 'teeth', duration=0.1),
                ActorInterval(teeth, 'teeth', duration=0.1),
                ActorInterval(teeth, 'teeth', duration=0.1),
                ActorInterval(teeth, 'teeth', duration=0.1))
            propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack), Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
        else:
            x = toon.getX(battle)
            y = toon.getY(battle)
            z = toon.getZ(battle)
            z = z + 0.2
            flyPoint = Point3(x, y - 2.1, z)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.5, y - 2.5, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 1.0, y - 3.0, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 1.3, y - 3.6, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.9, y - 3.1, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.3, y - 2.6, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.1, y - 2.2, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.4, y - 1.9, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.7, y - 2.1, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.8, y - 2.3, z)))
            teethAppearTrack.append(LerpScaleInterval(teeth, 0.6, MovieUtil.PNT3_NEARZERO))
            hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.5), LerpHprInterval(teeth, 0.4, Point3(80, 0, 0), startHpr=Point3(180, 0, 0)), LerpHprInterval(teeth, 0.8, Point3(-10, 0, 0), startHpr=Point3(80, 0, 0)))
            animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=3.6))
            propTrack = Sequence(Parallel(teethAppearTrack, hprTrack, animTrack), Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
        propTracks += (propTrack,)

    damageAnims = [['cringe',
      0.01,
      0.7,
      1.2],
     ['spit',
      0.01,
      2.95,
      1.47],
     ['spit',
      0.01,
      4.42,
      0.07],
     ['spit',
      0.08,
      4.49,
      -0.07],
     ['spit',
      0.08,
      4.42,
      0.07],
     ['spit',
      0.08,
      4.49,
      -0.07],
     ['spit',
      0.08,
      4.42,
      0.07],
     ['spit',
      0.08,
      4.49,
      -0.07],
     ['spit', 0.01, 4.42]]
    dodgeAnims = [['jump', 0.01, 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=3.2, splicedDamageAnims=damageAnims, dodgeDelay=2.75, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=1.4)
    return Parallel(suitTrack, toonTracks, *propTracks)


def doCigarSmoke(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    cigar = globalPropPool.getProp('cigar')
    suitTrack = getSuitTrack(attack)
    suitCigar = suit.find('**/suit_cigar')
    if not suitCigar.isEmpty():
        propTrack = Sequence(
            LerpScaleInterval(suitCigar, 0.5, MovieUtil.PNT3_NEARZERO),
            Func(suitCigar.stash),
            Func(__showProp, cigar, suit.getRightHand(), (-0.34, -0.49, -0.24), (180.00, 0.00, 180.00)),
            LerpScaleInterval(cigar, 0.5, Point3(8.0)),
            Wait(4.0),
            Wait(0.01),
            LerpScaleInterval(cigar, 0.5, MovieUtil.PNT3_NEARZERO),
            Func(MovieUtil.removeProp, cigar),
            Func(suitCigar.unstash),
            LerpScaleInterval(suitCigar, 0.5, Point3(8.0)))
    else:
        propTrack = Sequence(
            Wait(0.5),
            Func(__showProp, cigar, suit.getRightHand(), (-0.34, -0.49, -0.24), (180.00, 0.00, 180.00)),
            LerpScaleInterval(cigar, 0.5, Point3(8.0)),
            Wait(4.5),
            Wait(0.01),
            LerpScaleInterval(cigar, 0.5, MovieUtil.PNT3_NEARZERO),
            Func(MovieUtil.removeProp, cigar))
    baseFlameTracks = ()

    def changeColor(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(nextPart.colorScaleInterval(0.1, Vec4(0.5, 0.5, 0.5, 1)))

        return track

    def resetColor(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    colorTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        baseFlameEffect = BattleParticles.createParticleEffect(file='cigar')
        baseFlameSmall = BattleParticles.createParticleEffect(file='cigar')
        baseFlameSmall.setScale(0.7)
        baseFlameTrack = getPartTrack(baseFlameEffect, 3.8, 1.9, [baseFlameEffect, toon, 0])
        baseFlameSmallTrack = getPartTrack(baseFlameSmall, 3.8, 1.9, [baseFlameSmall, toon, 0])
        if dmg > 0:
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
            colorTrack = Sequence()
            colorTrack.append(Wait(4.4))
            colorTrack.append(Func(battle.movie.needRestoreColor))
            colorTrack.append(changeColor(headParts))
            colorTrack.append(changeColor(torsoParts))
            colorTrack.append(changeColor(legsParts))
            colorTrack.append(Wait(3.5))
            colorTrack.append(resetColor(headParts))
            colorTrack.append(resetColor(torsoParts))
            colorTrack.append(resetColor(legsParts))
            colorTrack.append(Func(battle.movie.clearRestoreColor))
            baseFlameTracks += (baseFlameTrack,)
            colorTracks += (colorTrack,)
        else:
            baseFlameTracks += (baseFlameSmallTrack,)

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.7,
     0.62])
    damageAnims.append(['slip-forward',
     1e-05,
     0.4,
     1.2])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.8, startTime=4.2))
    toonTracks = getToonTracks(attack, damageDelay=4.8, splicedDamageAnims=damageAnims, dodgeDelay=3.9, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_filibuster.ogg', delay=4.0, node=suit)
    return Parallel(suitTrack, propTrack, *baseFlameTracks, toonTracks, *colorTracks, soundTrack)


def doEvictionNotice(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = getSuitTrack(attack)
    propTracks = ()
    for t in targets:
        toon = t['toon']
        paper = globalPropPool.getProp('shredder-paper')
        posPoints = [Point3(-0.04, 0.15, -1.38), VBase3(10.584, -11.945, 18.316)]
        propTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.8, MovieUtil.PNT3_ONE, scaleUpTime=0.5))
        propTrack.append(Wait(1.73))
        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.4)
        missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)
        propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], parent=battle, target=t))

    toonTracks = getToonTracks(attack, 3.4, ['conked'], 2.8, ['jump'])
    return Parallel(suitTrack, toonTracks, *propTracks)


def doWithdrawal(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('Withdrawal')
    BattleParticles.setEffectTexture(particleEffect, 'snow-particle')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1e-05, suitTrack.getDuration() + 1.2, [particleEffect, suit, 0])
    toonTracks = getToonTracks(attack, damageDelay=1.2, damageAnimNames=['cringe'], dodgeDelay=0.2, splicedDodgeAnims=[['duck', 1e-05, 0.8]], showMissedExtraTime=0.8)
    colorTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            colorTrack = getColorTrack(battle, toon, 1.6, 2.9, Vec4(0, 0, 0, 1))
            colorTracks += (colorTrack,)

    soundTrack = getSoundTrack('SA_withdrawl.ogg', delay=1.4, node=suit)
    return Parallel(suitTrack, partTrack, toonTracks, soundTrack, *colorTracks)


def doJargon(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect(file='jargonSpray')
    particleEffect2 = BattleParticles.createParticleEffect(file='jargonSpray')
    particleEffect3 = BattleParticles.createParticleEffect(file='jargonSpray')
    particleEffect4 = BattleParticles.createParticleEffect(file='jargonSpray')
    BattleParticles.setEffectTexture(particleEffect, 'jargon-brow', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect2, 'jargon-deep', color=Vec4(0, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect3, 'jargon-hoop', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect4, 'jargon-ipo', color=Vec4(0, 0, 0, 1))
    damageDelay = 2.2
    dodgeDelay = 1.5
    partDelay = 1.1
    partInterval = 1.2
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, partDelay + partInterval * 0, 2, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, partDelay + partInterval * 1, 2, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, partDelay + partInterval * 2, 2, [particleEffect3, suit, 0])
    partTrack4 = getPartTrack(particleEffect4, partDelay + partInterval * 3, 1.0, [particleEffect4, suit, 0])
    damageAnims = []
    damageAnims.append(['conked',
     0.0001,
     0,
     0.4])
    damageAnims.append(['conked',
     0.0001,
     2.7,
     0.85])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.09])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.09])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.66])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.09])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.09])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.86])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.14])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.14])
    damageAnims.append(['conked', 0.0001, 0.4])
    dodgeAnims = [['duck', 0.0001, 1.2], ['duck', 0.0001, 1.3]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.6, showDamageExtraTime=0.7)
    soundTrack = getSoundTrack('SA_jargon.ogg', delay=2.1, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, partTrack, partTrack2, partTrack3, partTrack4)


def doMumboJumbo(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    BattleParticles.loadParticles()
    textureNames: Tuple[str, ...] = ('mumbojumbo-boiler',
     'mumbojumbo-creative',
     'mumbojumbo-deben',
     'mumbojumbo-high',
     'mumbojumbo-iron')
    particleEffect = BattleParticles.createParticleEffect(file='mumboJumboSpray')
    particleEffect2 = BattleParticles.createParticleEffect(file='mumboJumboSpray')
    particleEffect3 = BattleParticles.createParticleEffect(file='mumboJumboSmother')
    particleEffect4 = BattleParticles.createParticleEffect(file='mumboJumboSmother')
    particleEffect5 = BattleParticles.createParticleEffect(file='mumboJumboSmother')
    BattleParticles.setEffectTexture(particleEffect, textureNames, color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect2, textureNames, color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect3, textureNames, color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect4, textureNames, color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect5, textureNames, color=Vec4(1, 0, 0, 1))
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, 2.5, 2, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, 2.5, 2, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, 3.3, 1.7, [particleEffect3, toon, 0])
    partTrack4 = getPartTrack(particleEffect4, 3.3, 1.7, [particleEffect4, toon, 0])
    partTrack5 = getPartTrack(particleEffect5, 3.3, 1.7, [particleEffect5, toon, 0])
    toonTrack = getToonTrack(attack, 3.2, ['cringe'], 2.2, ['sidestep'])
    soundTrack = getSoundTrack('SA_mumbo_jumbo.ogg', delay=2.5, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, soundTrack, partTrack, partTrack2, partTrack3, partTrack4, partTrack5)
    else:
        return Parallel(suitTrack, toonTrack, soundTrack, partTrack, partTrack2)


def doGuiltTrip(attack):
    suit = attack['suit']
    battle = attack['battle']
    centerColor = Vec4(1.0, 0.2, 0.2, 0.9)
    edgeColor = Vec4(0.9, 0.9, 0.9, 0.4)
    powerBar1 = BattleParticles.createParticleEffect(file='guiltTrip')
    powerBar2 = BattleParticles.createParticleEffect(file='guiltTrip')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-90, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(90, 0, 0)
    powerBar1.setScale(5)
    powerBar2.setScale(5)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitTrack = getSuitAnimTrack(attack)

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(0.7), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 0.6, [waterfallEffect, suit, 0])
    toonTracks = getToonTracks(attack, 1.5, ['slip-forward'], 0.86, ['jump'])
    soundTrack = getSoundTrack('SA_guilt_trip.ogg', delay=1.1, node=suit)
    return Parallel(suitTrack, partTrack1, partTrack2, soundTrack, waterfallTrack, toonTracks)


def doRestrainingOrder(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = getSuitTrack(attack)
    propTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        paper = globalPropPool.getProp('shredder-paper')
        posPoints = [Point3(-0.04, 0.15, -1.38), VBase3(10.584, -11.945, 18.316)]
        propTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.8, MovieUtil.PNT3_ONE, scaleUpTime=0.5))
        propTrack.append(Wait(1.73))
        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.4)
        missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)
        propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], parent=battle, target=t))
        propTracks += (propTrack,)
        if dmg > 0:
            restraintCloud = BattleParticles.createParticleEffect(file='restrainingOrderCloud')
            restraintCloud.setPos(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ())
            cloudTrack = getPartTrack(restraintCloud, 3.5, 0.2, [restraintCloud, battle, 0])
            propTracks += (cloudTrack,)

    damageAnims = [['conked',
      0.01,
      0.3,
      0.2], ['struggle', 0.01, 0.2]]
    toonTracks = getToonTracks(attack, damageDelay=3.4, splicedDamageAnims=damageAnims, dodgeDelay=2.8, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, toonTracks, *propTracks)


def doSpin(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    damageDelay = 1.7
    sprayEffect = BattleParticles.createParticleEffect(file='spinSpray')
    spinEffect1 = BattleParticles.createParticleEffect(file='spinEffect')
    spinEffect2 = BattleParticles.createParticleEffect(file='spinEffect')
    spinEffect3 = BattleParticles.createParticleEffect(file='spinEffect')
    spinEffect1.reparentTo(toon)
    spinEffect2.reparentTo(toon)
    spinEffect3.reparentTo(toon)
    height1 = toon.getHeight() * (random.random() * 0.2 + 0.7)
    height2 = toon.getHeight() * (random.random() * 0.2 + 0.4)
    height3 = toon.getHeight() * (random.random() * 0.2 + 0.1)
    spinEffect1.setPos(0.8, -0.7, height1)
    spinEffect1.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect1.setHpr(spinEffect1, 0, 50, 0)
    spinEffect2.setPos(0.8, -0.7, height2)
    spinEffect2.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect2.setHpr(spinEffect2, 0, 50, 0)
    spinEffect3.setPos(0.8, -0.7, height3)
    spinEffect3.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect3.setHpr(spinEffect3, 0, 50, 0)
    spinEffect1.wrtReparentTo(battle)
    spinEffect2.wrtReparentTo(battle)
    spinEffect3.wrtReparentTo(battle)
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    spinTrack1 = getPartTrack(spinEffect1, 2.1, 3.9, [spinEffect1, battle, 0])
    spinTrack2 = getPartTrack(spinEffect2, 2.1, 3.9, [spinEffect2, battle, 0])
    spinTrack3 = getPartTrack(spinEffect3, 2.1, 3.9, [spinEffect3, battle, 0])
    damageAnims = []
    damageAnims.append(['duck',
     0.01,
     0.01,
     1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['sidestep'], showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    if dmg > 0:
        toonSpinTrack = Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5))
        return Parallel(suitTrack, sprayTrack, toonTrack, toonSpinTrack, spinTrack1, spinTrack2, spinTrack3)
    else:
        return Parallel(suitTrack, sprayTrack, toonTrack)


def doLegalese(attack):
    suit = attack['suit']
    BattleParticles.loadParticles()
    textureNames: Tuple[str, ...] = ('legalese-hc',
     'legalese-qpq',
     'legalese-vd')
    sprayEffect1 = BattleParticles.createParticleEffect(file='legaleseSpray')
    sprayEffect2 = BattleParticles.createParticleEffect(file='legaleseSpray')
    sprayEffect3 = BattleParticles.createParticleEffect(file='legaleseSpray')
    color = Vec4(0.4, 0, 0, 1)
    BattleParticles.setEffectTexture(sprayEffect1, textureNames, color=color)
    BattleParticles.setEffectTexture(sprayEffect2, textureNames, color=color)
    BattleParticles.setEffectTexture(sprayEffect3, textureNames, color=color)
    partDelay = 1.3
    partDuration = 1.15
    damageDelay = 1.9
    dodgeDelay = 1.1
    suitTrack = getSuitTrack(attack)
    sprayTrack1 = getPartTrack(sprayEffect1, partDelay, partDuration, [sprayEffect1, suit, 0])
    sprayTrack2 = getPartTrack(sprayEffect2, partDelay + 0.8, partDuration, [sprayEffect2, suit, 0])
    sprayTrack3 = getPartTrack(sprayEffect3, partDelay + 1.6, partDuration, [sprayEffect3, suit, 0])
    damageAnims = []
    damageAnims.append(['cringe',
     1e-05,
     0.3,
     0.8])
    damageAnims.append(['cringe',
     1e-05,
     0.3,
     0.8])
    damageAnims.append(['cringe', 1e-05, 0.3])
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=0.8)
    return Parallel(suitTrack, toonTrack, sprayTrack1, sprayTrack2, sprayTrack3)


def doPeckingOrder(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toon = targets[0]['toon']
    dmg = targets[0]['hp']
    throwDuration = 3.03
    throwDelay = 3.2
    suitTrack = getSuitTrack(attack)
    numBirds = random.randint(4, 7)
    birdTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        numBirds = random.randint(4, 7)
        propDelay = 1.5
        for i in range(0, numBirds):
            next = globalPropPool.getProp('bird')
            next.setScale(0.01)
            next.reparentTo(suit.getRightHand())
            next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
            if dmg > 0:
                hitPoint = Point3(random.random() * 5 - 2.5, random.random() * 2 - 1 - 6, random.random() * 3 - 1.5 + toon.getHeight() - 0.9)
            else:
                hitPoint = Point3(random.random() * 2 - 1, random.random() * 4 - 2 - 15, random.random() * 4 - 2 + 2.2)
            birdTrack = Sequence(Wait(throwDelay), Func(battle.movie.needRestoreRenderProp, next), Func(next.wrtReparentTo, battle), Func(next.setHpr, Point3(90, 20, 0)), LerpPosInterval(next, 1.1, hitPoint))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(next, 0.15, Point3(9, 9, 9)))
            birdTracks.append(Sequence(Parallel(birdTrack, scaleTrack), Func(MovieUtil.removeProp, next)))

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.14,
     0.21])
    damageAnims.append(['cringe',
     0.01,
     0.14,
     0.13])
    damageAnims.append(['cringe', 0.01, 0.43])
    toonTracks = getToonTracks(attack, damageDelay=4.2, splicedDamageAnims=damageAnims, dodgeDelay=2.8, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    return Parallel(suitTrack, toonTracks, birdTracks)


def doShadowToon(attack):
    suit = attack['suit']
    toon = attack['target'][0]['toon']
    hp = attack['target'][0]['hp']
    battle = attack['battle']
    taunt = attack['taunt']
    oldPos = suit.getPos(battle)
    oldHpr = suit.getHpr(battle)
    toonPos = toon.getPos(battle)
    newPos = oldPos + Point3(0, 5, 0)
    tPieLeavesHand = 2.7
    tPieHitsSuit = 3.0
    tSuitDodges = 2.45
    ratioMissToHit = 1.5

    def __getSoundTrack(hitToon, tPieLeavesHand, node=None):
        throwSound = globalBattleSoundCache.getSound('AA_pie_throw_only.ogg')
        throwTrack = Sequence(Wait(2.6), SoundInterval(throwSound, node=node))
        if hitToon:
            hitSound = globalBattleSoundCache.getSound('AA_wholepie_only.ogg')
            hitTrack = Sequence(Wait(tPieLeavesHand), SoundInterval(hitSound, node=node))
            return Parallel(throwTrack, hitTrack)
        return throwTrack

    def __propPreflight(props, suit, toon, battle):
        prop = props[0]
        toon.update(0)
        prop.wrtReparentTo(battle)
        props[1].reparentTo(hidden)
        for ci in range(prop.getNumChildren()):
            prop.getChild(ci).setHpr(0, -90, 0)

        targetPnt = MovieUtil.avatarFacePoint(suit, other=battle)
        prop.lookAt(targetPnt)

    def __suitMissPoint(suit, other=render):
        pnt = suit.getPos(other)
        pnt.setZ(pnt[2] + suit.getHeight() * 1.3)
        return pnt

    def __piePreMiss(missDict, pie, suitPoint, other=render):
        ratioMissToHit = 1.5
        missDict['pie'] = pie
        missDict['startScale'] = pie.getScale()
        missDict['startPos'] = pie.getPos(other)
        v = Vec3(suitPoint - missDict['startPos'])
        endPos = missDict['startPos'] + v * ratioMissToHit
        missDict['endPos'] = endPos

    def __pieMissLerpCallback(t, missDict):
        tPieShrink = 0.7
        pie = missDict['pie']
        newPos = missDict['startPos'] * (1.0 - t) + missDict['endPos'] * t
        if t < tPieShrink:
            tScale = 0.0001
        else:
            tScale = (t - tPieShrink) / (1.0 - tPieShrink)
        newScale = missDict['startScale'] * max(1.0 - tScale, 0.01)
        pie.setPos(newPos)
        pie.setScale(newScale)

    def createEvilToon(toon=toon, oldPos=oldPos):
        evilToon = Toon.Toon()
        style = toon.style.clone()
        evilToon.setDNA(style)
        evilToon.hat = toon.getHat()
        evilToon.glasses = toon.getGlasses()
        evilToon.backpack = toon.getBackpack()
        evilToon.shoes = toon.getShoes()
        evilToon.generateToonAccessories()
        evilToon.setColorScale(0, 0, 0, 1)
        evilToon.setPos(battle, oldPos)
        evilToon.setHpr(battle, oldHpr)
        return evilToon

    evilToon = createEvilToon()
    evilToon.loop('neutral')

    def getDustCloudIval(evilToon=evilToon, oldPos=oldPos):
        dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
        dustCloud.setBillboardAxis(2.0)
        dustCloud.setZ(3)
        dustCloud.setScale(0.4)
        dustCloud.createTrack()
        dustCloud.setColorScale(0.2, 0.2, 0.2, 1)
        return Sequence(Func(dustCloud.reparentTo, render), Func(dustCloud.setPos, battle, oldPos + (0, 0, evilToon.getHeight())), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

    suitTrack = Sequence(Parallel(LerpPosInterval(suit, duration=1.0, pos=newPos, other=battle), ActorInterval(suit, 'walk', loop=1, playRate=-1, duration=1.0)), Parallel(Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), ActorInterval(suit, 'magic2'), Func(suit.loop, 'neutral')), Sequence(Wait(1.35), Func(getDustCloudIval().start), Wait(0.5), Func(evilToon.addActive), Func(evilToon.reparentTo, render), Wait(3.0), Func(suit.clearChat))))
    pieName = 'creampie'
    pie = globalPropPool.getProp(pieName)
    pieType = globalPropPool.getPropType(pieName)
    pie2 = MovieUtil.copyProp(pie)
    pies = [pie, pie2]
    for p in pies:
        p.setColorScale(0, 0, 0, 1)

    hands = evilToon.getRightHands()
    splatName = 'splat-' + pieName
    splat = globalPropPool.getProp(splatName)
    splatType = globalPropPool.getPropType(splatName)
    splat.setColorScale(0, 0, 0, 1)
    evilToonTrack = Sequence()
    toonFace = Func(evilToon.headsUp, battle, toonPos)
    evilToonTrack.append(toonFace)
    evilToonTrack.append(ActorInterval(evilToon, 'throw'))
    evilToonTrack.append(Func(evilToon.loop, 'neutral'))
    evilToonTrack.append(Func(getDustCloudIval().start))
    evilToonTrack.append(Wait(0.5))
    evilToonTrack.append(Func(evilToon.reparentTo, hidden))
    evilToonTrack.append(Sequence(Func(evilToon.removeActive), Func(evilToon.cleanup), Func(evilToon.removeNode)))
    hitToon = hp > 0
    pieShow = Func(MovieUtil.showProps, pies, hands)
    pieAnim = Func(__animProp, pies, pieName, pieType)
    pieScale1 = LerpScaleInterval(pie, 1.0, pie.getScale(), startScale=MovieUtil.PNT3_NEARZERO)
    pieScale2 = LerpScaleInterval(pie2, 1.0, pie2.getScale(), startScale=MovieUtil.PNT3_NEARZERO)
    pieScale = Parallel(pieScale1, pieScale2)
    piePreflight = Func(__propPreflight, pies, toon, evilToon, battle)
    pieTrack = Sequence(pieShow, pieAnim, pieScale, Func(battle.movie.needRestoreRenderProp, pies[0]), Wait(tPieLeavesHand - 1.0), piePreflight)
    soundTrack = __getSoundTrack(hitToon, tPieLeavesHand, evilToon)
    if hitToon:
        pieFly = LerpPosInterval(pie, tPieHitsSuit - tPieLeavesHand, pos=MovieUtil.avatarFacePoint(toon, other=battle), other=battle)
        pieHide = Func(MovieUtil.removeProps, pies)
        splatShow = Func(__showProp, splat, toon, Point3(0, 0, toon.getHeight()))
        splatBillboard = Func(__billboardProp, splat)
        splatAnim = ActorInterval(splat, splatName)
        splatHide = Func(MovieUtil.removeProp, splat)
        pieTrack.append(pieFly)
        pieTrack.append(pieHide)
        pieTrack.append(Func(battle.movie.clearRenderProp, pies[0]))
        pieTrack.append(splatShow)
        pieTrack.append(splatBillboard)
        pieTrack.append(splatAnim)
        pieTrack.append(splatHide)
    else:
        missDict = {}
        suitPoint = __suitMissPoint(toon, other=battle)
        piePreMiss = Func(__piePreMiss, missDict, pie, suitPoint, battle)
        pieMiss = LerpFunctionInterval(__pieMissLerpCallback, extraArgs=[missDict], duration=(tPieHitsSuit - tPieLeavesHand) * ratioMissToHit)
        pieHide = Func(MovieUtil.removeProps, pies)
        pieTrack.append(piePreMiss)
        pieTrack.append(pieMiss)
        pieTrack.append(pieHide)
        pieTrack.append(Func(battle.movie.clearRenderProp, pies[0]))
    moveUp = Sequence(Parallel(LerpPosInterval(suit, duration=1.0, pos=oldPos, other=battle), ActorInterval(suit, 'walk', loop=1, duration=1.0)), Func(suit.loop, 'neutral'))
    if toon.getTransformationsIndex(ToontownGlobals.TransformationCog):
        # TODO: fix this and make the disguise react properly. doesn't work atm
        toonTrack = getToonTrack(attack, tPieHitsSuit, ['cringe'], tSuitDodges, ['sidestep'])
    else:
        toonTrack = getToonTrack(attack, tPieHitsSuit, ['slip-backward'], tSuitDodges, ['sidestep'])
    return Sequence(suitTrack, Parallel(evilToonTrack, pieTrack, soundTrack, toonTrack), moveUp)


def doFlex(attack):
    suit = attack['suit']
    suitTrack = getSuitAnimTrack(attack)
    targets = attack['target']
    missedOneToon = False
    for t in targets:
        if t['hp'] <= 0:
            missedOneToon = True

    damageAnims = [['cringe']]
    dodgeAnims = [['shrug']]
    suitsfx = globalBattleSoundCache.getSound('SA_watercooler_appear_only.ogg')
    toonTracks = getToonTracks(attack, damageDelay=1.8, splicedDamageAnims=damageAnims, dodgeDelay=1.1, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.8, showDamageExtraTime=1.1)
    throwSound = Sequence(Wait(0.6), SoundInterval(suitsfx, node=suit, duration=0.4))
    toonsfx = base.loader.loadSfx('phase_3.5/audio/sfx/avatar_emotion_shrug.ogg')
    missSound = Sequence(Wait(1.1), SoundInterval(toonsfx, node=suit))
    hitSound = getSoundTrack('SA_powertie_impact.ogg', delay=1.8, node=suit)
    if hitAtleastOneToon(targets):
        if missedOneToon:
            return Parallel(suitTrack, toonTracks, throwSound, hitSound, missSound)
        else:
            return Parallel(suitTrack, toonTracks, throwSound, hitSound)
    else:
        return Parallel(suitTrack, toonTracks, throwSound, missSound)


def doBurn(attack):
    battle = attack['battle']
    targets = attack['target']
    flameTracks = Parallel()
    
    for target in targets:
        toon = target['toon']
    
        BattleParticles.loadParticles()
        baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame')
        flameEffect = BattleParticles.createParticleEffect('FiredFlame')
        flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(baseFlameEffect, 'fire')
        BattleParticles.setEffectTexture(flameEffect, 'fire')
        BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.8, 0.8, 0.8, 1))
        baseFlameSmall = BattleParticles.createParticleEffect(file='firedBaseFlame')
        flameSmall = BattleParticles.createParticleEffect('FiredFlame')
        flecksSmall = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(baseFlameSmall, 'fire')
        BattleParticles.setEffectTexture(flameSmall, 'fire')
        BattleParticles.setEffectTexture(flecksSmall, 'roll-o-dex', color=Vec4(0.8, 0.8, 0.8, 1))
        baseFlameSmall.setScale(0.7)
        flameSmall.setScale(0.7)
        flecksSmall.setScale(0.7)

        baseFlameTrack = getPartTrack(baseFlameEffect, 1.0, 1.9, [baseFlameEffect, toon, 0])
        flameTrack = getPartTrack(flameEffect, 1.0, 1.9, [flameEffect, toon, 0])
        flecksTrack = getPartTrack(flecksEffect, 1.8, 1.1, [flecksEffect, toon, 0])
        
        flameTracks.append(baseFlameTrack)
        flameTracks.append(flameTrack)
        flameTracks.append(flecksTrack)
        
        colorTrack = getColorTrack(battle, toon, 2.0, 3.5, Vec4(0, 0, 0, 1))
        
        flameTracks.append(colorTrack)

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.7,
     0.62])
    damageAnims.append(['slip-forward',
     1e-05,
     0.4,
     1.2])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.8, startTime=1.2))

    toonTracks = getToonTracks(attack, damageDelay=1.5, splicedDamageAnims=damageAnims)
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=1.0)    
 
    return Parallel(flameTracks, toonTracks, soundTrack)


def doHail(attack):
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    hailTracks = Parallel()
    for target in targets:
        toon = target['toon']
        freezeEffect = BattleParticles.createParticleEffect('DemotionFreeze')
        unFreezeEffect = BattleParticles.createParticleEffect(file='demotionUnFreeze')
        BattleParticles.setEffectTexture(freezeEffect, 'snow-particle')
        BattleParticles.setEffectTexture(unFreezeEffect, 'snow-particle')
        facePoint = __toonFacePoint(toon)
        freezeEffect.setPos(0, 0, facePoint.getZ())
        unFreezeEffect.setPos(0, 0, facePoint.getZ())
        partTrack1 = getPartTrack(freezeEffect, 1.4, 2.9, [freezeEffect, toon, 0])
        partTrack2 = getPartTrack(unFreezeEffect, 6.65, 0.5, [unFreezeEffect, toon, 0])
        hailTracks.append(partTrack1)
        hailTracks.append(partTrack2)

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0,
     0.5])
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.4, 0.5, startTime=0.5))
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.3, 0.5, startTime=0.9))
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.3, 0.6, startTime=1.2))
    damageAnims.append(['cringe', 2.6, 1.5])

    toonTracks = getToonTracks(attack, damageDelay = 1.0, splicedDamageAnims = damageAnims)
    soundTrack = getSoundTrack('SA_demotion.ogg', delay=1.2)

    return Parallel(hailTracks, toonTracks, soundTrack)


def doSnowball(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitType = getSuitBodyType(attack['suitName'])
    if suitType in ('a', 'b'):
        suitDelay = 1.79
        damageDelay = 3.46
        dodgeDelay = 2.56
        soundDelay = 3.1
    elif suitType == 'c':
        suitDelay = 1.09
        damageDelay = 2.76
        dodgeDelay = 1.86
        soundDelay = 2.4
    suitTrack = getSuitTrack(attack)
    propTracks = ()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        ball = globalPropPool.getProp('snowball')
        ballPosPoints = [Point3(0.04, 0.03, -0.31), VBase3(-1.152, 86.581, -76.784)]
        propTrack = Sequence(getPropAppearTrack(ball, suit.getRightHand(), ballPosPoints, 0.8, Point3(1, 1, 1), scaleUpTime=0.5))
        propTrack.append(Wait(suitDelay))
        propTrack.append(Func(battle.movie.needRestoreRenderProp, ball))
        propTrack.append(Func(ball.wrtReparentTo, battle))
        toonPos = toon.getPos(battle)
        x = toonPos.getX()
        y = toonPos.getY()
        z = toonPos.getZ()
        splat = globalPropPool.getProp('splat-snowball')
        if dmg > 0:
            splat = globalPropPool.getProp('splat-snowball')
            propTrack.append(LerpPosInterval(ball, 0.5, __toonFacePoint(toon, parent=battle)))
            propTrack.append(Func(MovieUtil.removeProp, ball))
            propTrack.append(Func(battle.movie.clearRenderProp, ball))
            propTrack.append(Func(__showProp, splat, toon, Point3(0, 0, toon.getHeight())))
            propTrack.append(Func(__billboardProp, splat))
            propTrack.append(ActorInterval(splat, 'splat-snowball'))
            propTrack.append(Func(MovieUtil.removeProp, splat))
        else:
            propTrack.append(LerpPosInterval(ball, 0.4, Point3(x, y - 3, z)))
            propTrack.append(Func(MovieUtil.removeProp, ball))
            propTrack.append(Func(battle.movie.clearRenderProp, ball))
            propTrack.append(Func(__showProp, splat, battle, Point3(x, y - 3, z + 0.2)))
            propTrack.append(Func(__billboardProp, splat))
            propTrack.append(ActorInterval(splat, 'splat-snowball'))
            propTrack.append(Func(MovieUtil.removeProp, splat))        
        propTrack.append(Wait(0.4))
        propTracks += (propTrack,)

    damageAnims = [['conked',
      damageDelay,
      0.01,
      0.5], ['slip-backward', 0.01, 0.7]]
    toonTracks = getToonTracks(attack, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showDamageExtraTime=3.9)
    soundTrack = getSoundTrack('SA_hardball_impact_only.ogg', delay=soundDelay - 0.3, node=suit) if hitAtleastOneToon(targets) else getSoundTrack('SA_hardball.ogg', delay=soundDelay, node=suit)
    return Parallel(suitTrack, toonTracks, *propTracks, soundTrack)


def doBlizzard(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    particleEffect = BattleParticles.createParticleEffect('Blizzard')
    waterfallEffect = BattleParticles.createParticleEffect(file='blizzardWaterfall')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1.0, 1.9, [particleEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
    damageAnims = [['slip-forward']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon(targets):
        fallingSoundTrack = Sequence(Wait(damageDelay + 0.5), SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, fallingSoundTrack, toonTracks)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)


def doHeatedDiscussion(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    for part in suit.getHeadParts(): #TODO: fix particles for skelecogs
        headPart = part

    BattleParticles.loadParticles()

    # Volcano Particles
    hotShotHeadEffect = BattleParticles.createParticleEffect('HotShotHead')
    hotShotHeadEffect.setZ(1.7)

    splash = Splash.Splash(headPart, wantParticles = 0, wantRipples = 0)
    splash.setColorScale(1.0, 0.2, 0.0, 1.0)
    splash.setScale(5)
    splash.setZ(1.5)

    dustCloud = DustCloud.DustCloud(fBillboard=0)
    dustCloud.setBillboardAxis(2.0)
    dustCloud.setZ(8)
    dustCloud.setScale(0.5)
    dustCloud.createTrack()

    if len(target) >= 3:
        volcanoScale = (3, 2, 2)
    else:
        volcanoScale = (1, 2, 2)
    volcanoEffect = BattleParticles.createParticleEffect('Volcano')
    volcanoEffect.setScale(volcanoScale)
    volcanoEffect.setZ(1.7)

    smokeEffect = BattleParticles.loadParticleFile('tt_p_efx_rocketLaunchSmoke')
    smokeEffect.setScale(5)
    smokeEffect.setZ(9)
    smokeEffect.setR(180)

    lavaTrack = Parallel()
    for t in target:
        toon = t['toon']
        lavaWaterfall = BattleParticles.createParticleEffect('LavaWaterfall')
        lavaWaterfall.setPosHpr(0, 9, 12, 180, 90, 0)
        lavaTrack.append(getPartTrack(lavaWaterfall, 4, 3, [lavaWaterfall, toon, 0]))

    volcanoTrack = Parallel(
        getPartTrack(hotShotHeadEffect, 0, 2, [hotShotHeadEffect, headPart, 0]),
        getPartTrack(volcanoEffect, 3, 4, [volcanoEffect, headPart, 0]),
        getPartTrack(smokeEffect, 3, 4, [smokeEffect, headPart, 0]),
        lavaTrack,
        Sequence(
            Wait(2), 
            Func(dustCloud.reparentTo, headPart), 
            dustCloud.track, 
            Func(dustCloud.detachNode)
        ),
        Sequence(
            Wait(2),
            Func(splash.play),
            Wait(3),
            Func(splash.destroy)
        ),
        Sequence(
            Wait(6.5),
            Parallel(
                volcanoEffect.colorScaleInterval(0.5, (1, 1, 1, 0), blendType='easeInOut'),
                smokeEffect.colorScaleInterval(0.5, (1, 1, 1, 0), blendType='easeInOut'),
                lavaWaterfall.colorScaleInterval(0.5, (1, 1, 1, 0), blendType = 'easeInOut')
            )
        )
    )

    # Toon Burn Particles
    baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame')
    flameEffect = BattleParticles.createParticleEffect('FiredFlame')
    flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
    BattleParticles.setEffectTexture(baseFlameEffect, 'fire')
    BattleParticles.setEffectTexture(flameEffect, 'fire')
    BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.8, 0.8, 0.8, 1))
    baseFlameSmall = BattleParticles.createParticleEffect(file='firedBaseFlame')
    flameSmall = BattleParticles.createParticleEffect('FiredFlame')
    flecksSmall = BattleParticles.createParticleEffect('SpriteFiredFlecks')
    BattleParticles.setEffectTexture(baseFlameSmall, 'fire')
    BattleParticles.setEffectTexture(flameSmall, 'fire')
    BattleParticles.setEffectTexture(flecksSmall, 'roll-o-dex', color=Vec4(0.8, 0.8, 0.8, 1))
    baseFlameSmall.setScale(0.7)
    flameSmall.setScale(0.7)
    flecksSmall.setScale(0.7)
    suitTrack = Sequence(
        getSuitAnimTrack(attack, delay = 0.5),
        Func(suit.loop, 'neutral', 0)
    )

    def changeColor(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

        return track

    def resetColor(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    colorTrack = Sequence()
    colorTrack.append(Wait(5.3))
    colorChangeTrack = Parallel()
    colorResetTrack = Parallel()
    baseFlameTrack = Parallel()
    flameTrack = Parallel()
    flecksTrack = Parallel()
    for t in target:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
            colorChangeTrack.append(Func(battle.movie.needRestoreColor))
            colorChangeTrack.append(changeColor(headParts))
            colorChangeTrack.append(changeColor(torsoParts))
            colorChangeTrack.append(changeColor(legsParts))
            baseFlameTrack.append(getPartTrack(baseFlameEffect, 5.3, 1.9, [baseFlameEffect, toon, 0]))
            flameTrack.append(getPartTrack(flameEffect, 5.3, 1.9, [flameEffect, toon, 0]))
            flecksTrack.append(getPartTrack(flecksEffect, 5.3, 1.1, [flecksEffect, toon, 0]))
        else:
            baseFlameTrack.append(getPartTrack(baseFlameSmall, 5, 1.9, [baseFlameSmall, toon, 0]))
            flameTrack.append(getPartTrack(flameSmall, 5.3, 1.9, [flameSmall, toon, 0]))
            flecksTrack.append(getPartTrack(flecksSmall, 5.3, 1.1, [flecksSmall, toon, 0]))

    colorTrack.append(colorChangeTrack)
    colorTrack.append(Wait(3.5))
    for t in target:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
            colorResetTrack.append(resetColor(headParts))
            colorResetTrack.append(resetColor(torsoParts))
            colorResetTrack.append(resetColor(legsParts))
            colorResetTrack.append(Func(battle.movie.needRestoreColor))
    colorTrack.append(colorResetTrack)
    colorTrack.append(Func(battle.movie.clearRestoreColor))

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.7,
     0.62])
    damageAnims.append(['slip-forward',
     1e-05,
     0.4,
     1.2])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.8, startTime=1.2))
    dodgeAnims = []
    dodgeAnims.append(['sidestep-right',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('sidestep-right', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['sidestep-right', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=5.3, splicedDamageAnims=damageAnims, dodgeDelay=4.5, splicedDodgeAnims = dodgeAnims)
    soundTrack = getSoundTrack('ttrm_s_ene_atk_heatedDiscussion.ogg', delay=0.0, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, baseFlameTrack, flameTrack, flecksTrack, toonTracks, colorTrack, volcanoTrack, soundTrack)
    else:
        return Parallel(suitTrack, baseFlameTrack, flameTrack, flecksTrack, toonTracks, volcanoTrack, soundTrack)


def doFrostyReception(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    BattleParticles.loadParticles()
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.3
    elif suitType == 'b':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.3
    elif suitType == 'c':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.3
    suitTrack = getSuitAnimTrack(attack, delay=0.9)
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), MovieUtil.PNT3_ZERO]
    cloudTrack = Parallel()
    for t in target:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            snowEffect = BattleParticles.createParticleEffect('FreezeAssets')
            BattleParticles.setEffectTexture(snowEffect, 'snow-particle')
            toonCloud = MovieUtil.copyProp(cloud)
            cloudPropTrack = Sequence()
            cloudPropTrack.append(Func(toonCloud.pose, 'stormcloud', 0))
            cloudPropTrack.append(getPropAppearTrack(toonCloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.7))
            cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, toonCloud))
            cloudPropTrack.append(Func(toonCloud.wrtReparentTo, render))
            targetPoint = __toonFacePoint(toon)
            targetPoint.setZ(targetPoint[2] + 3)
            cloudPropTrack.append(Wait(1.1))
            cloudPropTrack.append(LerpPosInterval(toonCloud, 1, pos=targetPoint))
            cloudPropTrack.append(Wait(partDelay))
            cloudPropTrack.append(ParticleInterval(snowEffect, toonCloud, worldRelative=0, duration=2.1, cleanup=True))
            cloudPropTrack.append(Wait(0.4))
            cloudPropTrack.append(LerpScaleInterval(toonCloud, 0.5, MovieUtil.PNT3_NEARZERO))
            cloudPropTrack.append(Func(MovieUtil.removeProp, toonCloud))
            cloudPropTrack.append(Func(battle.movie.clearRenderProp, toonCloud))
            cloudTrack.append(cloudPropTrack)
    cloudTrack.append(Func(MovieUtil.removeProp, cloud))
    damageAnims = [['cringe',
      0.01,
      0.4,
      0.8], ['duck', 0.01, 1.6]]
    toonTrack = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.2)
    return Parallel(suitTrack, toonTrack, cloudTrack)


def doStomp(attack):
    suit = attack['suit']
    toonAnimNames = ['slip-forward']
    animDelay = 0.35
    suitTrack = getSuitAnimTrack(attack)
    toonTracks = getToonTracks(attack, 
                               damageDelay=animDelay, 
                               damageAnimNames=toonAnimNames, 
                               dodgeDelay=animDelay, 
                               dodgeAnimNames=toonAnimNames,
                               showDamageExtraTime = 0, 
                               showMissedExtraTime = 0)
    soundTrack = getSoundTrack('ttrm_s_ene_atk_activeState.ogg', delay=animDelay, node=suit)
    track = Sequence(
        Parallel(suitTrack, soundTrack, toonTracks),
        Wait(1)
    )
    return track


def doDormantState(attack):
    suit = attack['suit']
    toonAnimNames = ['neutral']
    animDelay = 0
    suitTrack = getSuitAnimTrack(attack)
    toonTracks = getToonTracks(attack, 
                               damageDelay=animDelay, 
                               damageAnimNames=toonAnimNames, 
                               dodgeDelay=animDelay, 
                               dodgeAnimNames=toonAnimNames,
                               showDamageExtraTime = 0, 
                               showMissedExtraTime = 0)
    soundTrack = getSoundTrack('SA_withdrawl.ogg', delay=0, node=suit)
    return Parallel(suitTrack, soundTrack, toonTracks)