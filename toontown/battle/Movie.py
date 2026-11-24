from typing import List, Dict, Any
from toontown.toonbase.ToontownBattleGlobals import *
from .BattleBase import *
from direct.interval.IntervalGlobal import *
from direct.showbase import DirectObject
from . import MovieFire
from . import MovieSOS
from . import MovieNPCSOS
from . import MoviePetSOS
from . import MovieHeal
from . import MovieTrap
from . import MovieLure
from . import MovieSound
from . import MovieThrow
from . import MovieSquirt
from . import MovieDrop
from . import MovieSuitAttacks
from . import MovieToonVictory
from .PlayByPlayText import PlayByPlayText
from . import BattleParticles
from toontown.distributed import DelayDelete
from . import BattleExperience
from direct.directnotify import DirectNotifyGlobal
from . import RewardPanel
import random
from . import MovieUtil
from toontown.toon import Toon
from toontown.toonbase import ToontownGlobals
from toontown.toontowngui import TTDialog
import copy
from toontown.toonbase import TTLocalizer
from toontown.toon import NPCToons
from panda3d.toontown import *
from otp.otpbase.PythonUtil import cmp_to_key
camPos = Point3(14, 0, 10)
camHpr = Vec3(89, -30, 0)
randomBattleTimestamp = base.config.GetBool('random-battle-timestamp', 0)

class Movie(DirectObject.DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('Movie')

    def __init__(self, battle):
        self.battle = battle
        self.track = None
        self.rewardPanel = None
        self.rewardCallback = None
        self.playByPlayText: PlayByPlayText = PlayByPlayText()
        self.playByPlayText.hide()
        self.playByPlayDescText: PlayByPlayText = PlayByPlayText(scale = 0.3, pos = (0, -0.55), fg = (1.0, 0.5, 0, 1))
        self.playByPlayDescText.hide()
        self.renderProps = []
        self.hasBeenReset = 0
        self.reset()
        self.rewardHasBeenReset = 0
        self.resetReward()

    def cleanup(self):
        self.reset()
        self.resetReward()
        self.battle = None
        if self.playByPlayText != None:
            self.playByPlayText.cleanup()
        self.playByPlayText = None
        if self.playByPlayDescText != None:
            self.playByPlayDescText.cleanup()
        self.playByPlayDescText = None
        if self.rewardPanel != None:
            self.rewardPanel.cleanup()
        self.rewardPanel = None
        self.rewardCallback = None

    def needRestoreColor(self):
        self.restoreColor = 1

    def clearRestoreColor(self):
        self.restoreColor = 0

    def needRestoreHips(self):
        self.restoreHips = 1

    def clearRestoreHips(self):
        self.restoreHips = 0

    def needRestoreHeadScale(self):
        self.restoreHeadScale = 1

    def clearRestoreHeadScale(self):
        self.restoreHeadScale = 0

    def needRestoreToonScale(self):
        self.restoreToonScale = 1

    def clearRestoreToonScale(self):
        self.restoreToonScale = 0

    def needRestoreParticleEffect(self, effect):
        self.specialParticleEffects.append(effect)

    def clearRestoreParticleEffect(self, effect):
        if self.specialParticleEffects.count(effect) > 0:
            self.specialParticleEffects.remove(effect)

    def needRestoreRenderProp(self, prop):
        self.renderProps.append(prop)

    def clearRenderProp(self, prop):
        if self.renderProps.count(prop) > 0:
            self.renderProps.remove(prop)

    def restore(self):
        return
        for toon in self.battle.activeToons:
            toon.loop('neutral')
            origPos, origHpr = self.battle.getActorPosHpr(toon)
            toon.setPosHpr(self.battle, origPos, origHpr)
            hands = toon.getRightHands()[:]
            hands += toon.getLeftHands()
            for hand in hands:
                props = hand.getChildren()
                for prop in props:
                    if prop.getName() != 'book':
                        MovieUtil.removeProp(prop)

            if self.restoreColor == 1:
                headParts = toon.getHeadParts()
                torsoParts = toon.getTorsoParts()
                legsParts = toon.getLegsParts()
                partsList = [headParts, torsoParts, legsParts]
                for parts in partsList:
                    for partNum in range(0, parts.getNumPaths()):
                        nextPart = parts.getPath(partNum)
                        nextPart.clearColorScale()
                        nextPart.clearTransparency()

            if self.restoreHips == 1:
                parts = toon.getHipsParts()
                for partNum in range(0, parts.getNumPaths()):
                    nextPart = parts.getPath(partNum)
                    props = nextPart.getChildren()
                    for prop in props:
                        if prop.getName() == 'redtape-tube.egg':
                            MovieUtil.removeProp(prop)

            if self.restoreHeadScale == 1:
                headScale = ToontownGlobals.toonHeadScales[toon.style.getAnimal()]
                for lod in toon.getLODNames():
                    toon.getPart('head', lod).setScale(headScale)

            if self.restoreToonScale == 1:
                toon.setScale(1)
            headParts = toon.getHeadParts()
            for partNum in range(0, headParts.getNumPaths()):
                part = headParts.getPath(partNum)
                part.setHpr(0, 0, 0)
                part.setPos(0, 0, 0)

            arms = toon.findAllMatches('**/arms')
            sleeves = toon.findAllMatches('**/sleeves')
            hands = toon.findAllMatches('**/hands')
            for partNum in range(0, arms.getNumPaths()):
                armPart = arms.getPath(partNum)
                sleevePart = sleeves.getPath(partNum)
                handsPart = hands.getPath(partNum)
                armPart.setHpr(0, 0, 0)
                sleevePart.setHpr(0, 0, 0)
                handsPart.setHpr(0, 0, 0)

        for suit in self.battle.activeSuits:
            if suit._Actor__animControlDict != None:
                suit.loop('neutral')
                suit.battleTrapIsFresh = 0
                origPos, origHpr = self.battle.getActorPosHpr(suit)
                suit.setPosHpr(self.battle, origPos, origHpr)
                hands = [suit.getRightHand(), suit.getLeftHand()]
                for hand in hands:
                    props = hand.getChildren()
                    for prop in props:
                        MovieUtil.removeProp(prop)

        for effect in self.specialParticleEffects:
            if effect != None:
                effect.cleanup()

        self.specialParticleEffects = []
        for prop in self.renderProps:
            MovieUtil.removeProp(prop)

        self.renderProps = []
        return

    def _deleteTrack(self):
        if self.track:
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        return

    def reset(self, finish = 0):
        if self.hasBeenReset == 1:
            return
        self.hasBeenReset = 1
        self.stop()
        self._deleteTrack()
        if finish == 1:
            self.restore()
        self.attackDicts = []
        self.restoreColor = 0
        self.restoreHips = 0
        self.restoreHeadScale = 0
        self.restoreToonScale = 0
        self.specialParticleEffects = []
        for prop in self.renderProps:
            MovieUtil.removeProp(prop)

        self.renderProps = []

    def resetReward(self, finish = 0):
        if self.rewardHasBeenReset == 1:
            return
        self.rewardHasBeenReset = 1
        self.stop()
        self._deleteTrack()
        if finish == 1:
            self.restore()
        self.toonRewardDicts = []
        if self.rewardPanel != None:
            self.rewardPanel.destroy()
        self.rewardPanel = None
        return

    def play(self, ts, callback):
        self.hasBeenReset = 0
        ptrack = Sequence()
        camtrack = Sequence()
        if random.random() > 0.5:
            MovieUtil.shotDirection = 'left'
        else:
            MovieUtil.shotDirection = 'right'
        for s in self.battle.activeSuits:
            s.battleTrapIsFresh = 0

        attacks, cam = self.__doAttacks()
        if attacks:
            ptrack.append(attacks)
            camtrack.append(cam)
        ptrack.append(Func(callback))
        self._deleteTrack()
        self.track = Sequence(ptrack, name='movie-track-%d' % self.battle.doId)
        if self.battle.localToonPendingOrActive():
            self.track = Parallel(self.track, Sequence(camtrack), name='movie-track-with-cam-%d' % self.battle.doId)
        if randomBattleTimestamp == 1:
            randNum = random.randint(0, 99)
            dur = self.track.getDuration()
            ts = float(randNum) / 100.0 * dur
        self.track.delayDeletes = []
        for suit in self.battle.suits:
            self.track.delayDeletes.append(DelayDelete.DelayDelete(suit, 'Movie.play'))

        for toon in self.battle.toons:
            self.track.delayDeletes.append(DelayDelete.DelayDelete(toon, 'Movie.play'))

        self.track.start(ts, playRate = self.battle.getRoundSpeed())

    def finish(self):
        self.track.finish()

    def playReward(self, ts, name, callback, noSkip = False):
        self.rewardHasBeenReset = 0
        ptrack = Sequence()
        camtrack = Sequence()
        self.rewardPanel = RewardPanel.RewardPanel(name)
        self.rewardPanel.hide()
        victory, camVictory, skipper = MovieToonVictory.doToonVictory(self.battle.localToonActive(), self.battle.activeToons, self.toonRewardIds, self.toonRewardDicts, self.deathList, self.rewardPanel, 1, self.uberList, self.helpfulToonsList, noSkip=noSkip)
        if victory:
            skipper.setIvals((ptrack, camtrack), ptrack.getDuration())
            ptrack.append(victory)
            camtrack.append(camVictory)
        ptrack.append(Func(callback))
        self._deleteTrack()
        self.track = Sequence(ptrack, name='movie-reward-track-%d' % self.battle.doId)
        if self.battle.localToonActive():
            self.track = Parallel(Func(self.battle.adjustWeather), self.track, camtrack, name='movie-reward-track-with-cam-%d' % self.battle.doId)
        self.track.delayDeletes = []
        for t in self.battle.activeToons:
            self.track.delayDeletes.append(DelayDelete.DelayDelete(t, 'Movie.playReward'))

        skipper.setIvals((self.track,), 0.0)
        skipper.setBattle(self.battle)
        self.track.start(ts)

    def playTutorialReward(self, ts, tutorialNPC, name, callback):
        self.rewardHasBeenReset = 0
        self.rewardPanel = RewardPanel.RewardPanel(name)
        self.rewardCallback = callback
        self.questList = self.rewardPanel.getQuestIntervalList(base.localAvatar, [[0,
         1,
         1,
         0]], [base.localAvatar], base.localAvatar.quests[0], [], [base.localAvatar.getDoId()])
        camera.setPosHpr(0, 8, base.localAvatar.getHeight() * 0.66, 179, 15, 0)
        self.playTutorialReward_1(tutorialNPC)

    def playTutorialReward_1(self, tutorialNPC):
        self.tutRewardDialog_1 = TTDialog.TTDialog(
                                         text = TTLocalizer.MovieTutorialReward1,
                                         command = self.playTutorialReward_2,
                                         extraArgs = [tutorialNPC],
                                         style = TTDialog.Acknowledge,
                                         fadeScreen = None,
                                         pos = (0.65, 0, 0.5),
                                         scale = 0.8
                                        )
        self.tutRewardDialog_1.hide()
        self._deleteTrack()
        self.track = Sequence(name='tutorial-reward-1')
        self.track.append(Func(self.rewardPanel.initGagFrame, base.localAvatar, [0,
         0,
         0,
         0,
         0,
         0,
         0], [0,
         0,
         0,
         0], noSkip=True))
        _, _, trackIval = self.rewardPanel.getTrackIntervalList(
                                           base.localAvatar, 
                                           [0, 0, 0, 0, 0, 0, 0], 
                                           [0, 0, 0, 0, 1, 1, 0], 
                                           0)
        self.track.append(trackIval)
        self.track.append(Func(self.tutRewardDialog_1.show))
        self.track.start()

    def playTutorialReward_2(self, value, tutorialNPC):
        self.tutRewardDialog_1.cleanup()
        from toontown.toon import Toon
        from toontown.toon import ToonDNA

        def doneChat1(page, elapsed = 0):
            self.track2.start()

        def doneChat2(elapsed):
            self.track2.pause()
            self.track3.start()

        def uniqueName(hook):
            return 'TutorialNPC-' + hook

        self.tutorialNPC = Toon.Toon()
        dna = ToonDNA.ToonDNA(tutorialNPC[1])
        self.tutorialNPC.setDNA(dna)
        self.tutorialNPC.setName(tutorialNPC[0])
        self.tutorialNPC.setPlayerType(NametagGroup.CCNonPlayer)
        self.tutorialNPC.setHat(*tutorialNPC[2])
        self.tutorialNPC.setBackpack(*tutorialNPC[3])
        self.tutorialNPC.setGlasses(*tutorialNPC[4])
        self.tutorialNPC.setShoes(*tutorialNPC[5])
        self.tutorialNPC.uniqueName = uniqueName
        if base.japanDialog:
            self.tomDialogue03 = base.loader.loadSfx('phase_3.5/audio/dial/CC_tom_movie_tutorial_reward01.ogg')
            self.tomDialogue04 = base.loader.loadSfx('phase_3.5/audio/dial/CC_tom_movie_tutorial_reward02.ogg')
            self.tomDialogue05 = base.loader.loadSfx('phase_3.5/audio/dial/CC_tom_movie_tutorial_reward03.ogg')
            self.musicVolume = base.config.GetFloat('tutorial-music-volume', 0.5)
        else:
            self.tomDialogue03 = None
            self.tomDialogue04 = None
            self.tomDialogue05 = None
            self.musicVolume = 0.9
        music = base.cr.playGame.place.loader.battleMusic
        if self.questList:
            self.track1 = Sequence(Wait(1.0), Func(self.rewardPanel.initQuestFrame, base.localAvatar, copy.deepcopy(base.localAvatar.quests)), Wait(1.0), Sequence(*self.questList), Wait(1.0), Func(self.rewardPanel.hide), Func(camera.setPosHpr, render, 34, 19.88, 3.48, -90, -2.36, 0), Func(base.localAvatar.animFSM.request, 'neutral'), Func(base.localAvatar.setPosHpr, 40.31, 22.0, -0.47, 150.0, 360.0, 0.0), Wait(0.5), Func(self.tutorialNPC.reparentTo, render), Func(self.tutorialNPC.show), Func(self.tutorialNPC.setPosHpr, 40.29, 17.9, -0.47, 11.31, 0.0, 0.07), Func(self.tutorialNPC.animFSM.request, 'TeleportIn'), Wait(1.517), Func(self.tutorialNPC.animFSM.request, 'neutral'), Func(self.acceptOnce, self.tutorialNPC.uniqueName('doneChatPage'), doneChat1), Func(self.tutorialNPC.addActive), Func(music.setVolume, self.musicVolume), Func(self.tutorialNPC.setLocalPageChat, TTLocalizer.MovieTutorialReward2, 0, None, [self.tomDialogue03]), name='tutorial-reward-3a')
            self.track2 = Sequence(Func(self.acceptOnce, self.tutorialNPC.uniqueName('doneChatPage'), doneChat2), Func(self.tutorialNPC.setLocalPageChat, TTLocalizer.MovieTutorialReward3, 1, None, [self.tomDialogue04]), Func(self.tutorialNPC.setPlayRate, 1.5, 'right-hand-start'), Func(self.tutorialNPC.play, 'right-hand-start'), Wait(self.tutorialNPC.getDuration('right-hand-start') / 1.5), Func(self.tutorialNPC.loop, 'right-hand'), name='tutorial-reward-3b')
            self.track3 = Parallel(Sequence(Func(self.tutorialNPC.setPlayRate, -1.8, 'right-hand-start'), Func(self.tutorialNPC.play, 'right-hand-start'), Wait(self.tutorialNPC.getDuration('right-hand-start') / 1.8), Func(self.tutorialNPC.animFSM.request, 'neutral'), name='tutorial-reward-3ca'), Sequence(Wait(0.5), Func(self.tutorialNPC.setChatAbsolute, TTLocalizer.MovieTutorialReward4, CFSpeech | CFTimeout, self.tomDialogue05), Wait(1.0), Func(self.tutorialNPC.animFSM.request, 'TeleportOut'), Wait(self.tutorialNPC.getDuration('teleport')), Wait(1.0), Func(self.playTutorialReward_3, 0), name='tutorial-reward-3cb'), name='tutorial-reward-3c')
            self.track1.start()
        else:
            self.playTutorialReward_3(0)

    def playTutorialReward_3(self, value):
        base.localAvatar.setH(270)
        self.tutorialNPC.removeActive()
        self.tutorialNPC.delete()
        self.questList = None
        self.rewardCallback()

    def stop(self):
        if self.track:
            self.track.finish()
            self._deleteTrack()
        if hasattr(self, 'track1'):
            self.track1.finish()
            self.track1 = None
        if hasattr(self, 'track2'):
            self.track2.finish()
            self.track2 = None
        if hasattr(self, 'track3'):
            self.track3.finish()
            self.track3 = None
        if self.rewardPanel:
            self.rewardPanel.hide()
        if self.playByPlayText:
            self.playByPlayText.hide()
        if self.playByPlayDescText:
            self.playByPlayDescText.hide()

    def doToonAttacks(self, attacks, track: Sequence, camTrack: Sequence):
        atkTrack = attacks[0]['track']
        if atkTrack == FIRE:
            ival, camIval = MovieFire.doFires(attacks)
        elif atkTrack == SOS:
            ival, camIval = MovieSOS.doSOSs(attacks)
        elif atkTrack in (NPCSOS, NPC_TOONS_HIT, NPC_COGS_MISS, NPC_RESTOCK_GAGS):
            ival, camIval = MovieNPCSOS.doNPCSOSs(attacks)
        elif atkTrack == PETSOS:
            ival, camIval = MoviePetSOS.doPetSOSs(attacks)
        elif atkTrack == HEAL:
            hasHealBonus = self.battle.getInteractivePropTrackBonus() == HEAL
            ival, camIval = MovieHeal.doHeals(attacks, hasHealBonus)
        elif atkTrack == TRAP:
            sortedTraps = []
            for attack in attacks:
                if 'npcId' not in attack:
                    sortedTraps.append(attack)
            for attacks in attacks:
                if 'npcId' in attack:
                    sortedTraps.append(attack)
            ival, camIval = MovieTrap.doTraps(sortedTraps)
        elif atkTrack == LURE:
            ival, camIval = MovieLure.doLures(attacks)
        elif atkTrack == SOUND:
            ival, camIval = MovieSound.doSounds(attacks)
        elif atkTrack == THROW:
            ival, camIval = MovieThrow.doThrows(attacks)
        elif atkTrack == SQUIRT:
            ival, camIval = MovieSquirt.doSquirts(attacks)
        elif atkTrack == DROP:
            ival, camIval = MovieDrop.doDrops(attacks)

        if ival:
            track.append(ival)
            camTrack.append(camIval)

    def __doAttacks(self):
        track: Sequence = Sequence(name = 'battle-attacks')
        camTrack: Sequence = Sequence(name = 'battle-attack-cam')
        isLocalToonSad: bool = False
        toonAttacks = []
        for i, atk in enumerate(self.attackDicts):
            if 'toon' in atk:
                # if this track is not the last track being queued up or it is the last toon attack
                # we are gonna perform the previous attacks
                lastAttack = i == len(self.attackDicts) - 1
                if (toonAttacks and toonAttacks[0]['track'] != atk['track']) or (toonAttacks and lastAttack):
                    self.doToonAttacks(toonAttacks, track, camTrack)
                    toonAttacks = []
                if lastAttack:
                    self.doToonAttacks([atk], track, camTrack)
                else:
                    toonAttacks.append(atk)
            else:
                # there is also a case where a cog attack is being played and there are no more toon attacks to process
                # but we haven't processed the rest of the toon attacks
                # rather than peeking ahead of the dict, we are just gonna handle that here
                if toonAttacks:
                    self.doToonAttacks(toonAttacks, track, camTrack)
                    toonAttacks = []
                ival, camIval = MovieSuitAttacks.doSuitAttack(atk)
                if ival:
                    track.append(ival)
                    camTrack.append(camIval)
                targetField = atk.get('target')
                if targetField is None:
                    continue
                for target in targetField:
                    if target['died'] and target['toon'].doId == base.localAvatar.doId:
                        isLocalToonSad = True
                if isLocalToonSad:
                    break

        if len(track) == 0:
            return (None, None)
        return (track, camTrack)

    def genRewardDicts(self, toonExp, deathList, uberList, helpfulToonsList):
        self.deathList = deathList
        self.helpfulToonsList = helpfulToonsList
        self.toonRewardDicts = BattleExperience.genRewardDicts(toonExp)
        self.toonRewardIds = [exp[0] for exp in toonExp]
        self.uberList = uberList

    def handleSuitAttackDict(self, toons: List[int], atk, adict: Dict[str, Any]):
        targetGone: bool = False
        hps = atk[ATK_HP_COL]
        if adict['group'] == 'group':
            targets = []
            for t in toons:
                if t != -1:
                    target = self.battle.findToon(t)
                    if target == None:
                        continue
                    targetIndex = toons.index(t)
                    tdict = {}
                    tdict['toon'] = target
                    tdict['hp'] = hps[targetIndex]
                    for status in atk[ATK_STATUS_COL]:
                        if target.doId == status[0]:
                            tdict['status'] = status[1]
                            break
                    self.notify.debug('DAMAGE: toon: %d hit for hp: %d' % (target.doId, hps[targetIndex]))
                    toonDied = atk[ATK_TGT_DIED_COL] & 1 << targetIndex
                    tdict['died'] = toonDied
                    targets.append(tdict)

            if len(targets) > 0:
                adict['target'] = targets
            else:
                targetGone = True
        elif adict['group'] == 'single':
            targetIndex = atk[ATK_TGT_COL]
            targetId = toons[targetIndex]
            target = self.battle.findToon(targetId)
            if target == None:
                targetGone = True
            else:
                tdict = {}
                tdict['toon'] = target
                tdict['hp'] = hps[targetIndex]
                if atk[ATK_STATUS_COL]:
                    tdict['status'] = atk[ATK_STATUS_COL][0][1]
                self.notify.debug('DAMAGE: toon: %d hit for hp: %d' % (target.doId, hps[targetIndex]))
                toonDied = atk[ATK_TGT_DIED_COL] & 1 << targetIndex
                tdict['died'] = toonDied
                toonIndex = self.battle.activeToons.index(target)
                rightToons = []
                for ti in range(0, toonIndex):
                    rightToons.append(self.battle.activeToons[ti])

                lenToons = len(self.battle.activeToons)
                leftToons = []
                if lenToons > toonIndex + 1:
                    for ti in range(toonIndex + 1, lenToons):
                        leftToons.append(self.battle.activeToons[ti])

                tdict['leftToons'] = leftToons
                tdict['rightToons'] = rightToons
                adict['target'] = [tdict]
        else:
            self.notify.warning('got attack not group or single!')
        if not targetGone:
            self.attackDicts.append(adict)
        else:
            self.notify.warning('handleSuitAttackDict(): target gone!')

    def genAttackDicts(self, toons: List[int], suits: List[int], battleAttacks):
        if self.track and self.track.isPlaying():
            self.notify.warning('genAttackDicts() - track is playing!')
        for atk in battleAttacks:
            if atk[ATK_AVTYPE_COL] == AVTYPE_TOON:
                targetGone: bool = False
                track = int(atk[ATK_TRACK_COL])
                if track != NO_ATTACK:
                    adict = {}
                    toonIndex = atk[ATK_ID_COL]
                    toonId = toons[toonIndex]
                    toon = self.battle.findToon(toonId)
                    if toon == None:
                        continue
                    level = atk[ATK_LVL_COL]
                    adict['toon'] = toon
                    adict['track'] = track
                    adict['level'] = level
                    hps = atk[ATK_HP_COL]
                    kbbonuses = atk[ATK_KBBONUS_COL]
                    if track == NPCSOS:
                        adict['npcId'] = atk[ATK_TGT_COL]
                        toonId = atk[ATK_TGT_COL]
                        track, npc_level, npc_hp = NPCToons.getNPCTrackLevelHp(adict['npcId'])
                        if track == None:
                            track = NPCSOS
                        adict['track'] = track
                        adict['level'] = npc_level
                    elif track == PETSOS:
                        petId = atk[ATK_TGT_COL]
                        adict['toonId'] = toonId
                        adict['petId'] = petId
                    if track == SOS:
                        targetId = atk[ATK_TGT_COL]
                        if targetId == base.localAvatar.doId:
                            target = base.localAvatar
                            adict['targetType'] = 'callee'
                        elif toon == base.localAvatar:
                            target = base.cr.identifyAvatar(targetId)
                            adict['targetType'] = 'caller'
                        else:
                            target = None
                            adict['targetType'] = 'observer'
                        adict['target'] = target
                    elif track == NPCSOS or track == NPC_COGS_MISS or track == NPC_TOONS_HIT or track == NPC_RESTOCK_GAGS or track == PETSOS:
                        toonHandles = []
                        for t in toons:
                            if t != -1:
                                target = self.battle.findToon(t)
                                if target == None:
                                    continue
                                if track == NPC_TOONS_HIT and t == toonId:
                                    continue
                                toonHandles.append(target)

                        adict['toons'] = toonHandles
                        suitHandles = []
                        for s in suits:
                            if s != -1:
                                target = self.battle.findSuit(s)
                                if target == None:
                                    continue
                                suitHandles.append(target)

                        adict['suits'] = suitHandles
                        if track == PETSOS:
                            targets = []
                            for t in toons:
                                if t != -1:
                                    target = self.battle.findToon(t)
                                    if target == None:
                                        continue
                                    tdict = {}
                                    tdict['toon'] = target
                                    tdict['hp'] = hps[toons.index(t)]
                                    self.notify.debug('PETSOS: toon: %d healed for hp: %d' % (target.doId, hps[toons.index(t)]))
                                    targets.append(tdict)

                            if len(targets) > 0:
                                adict['target'] = targets
                    elif track == HEAL:
                        if levelAffectsGroup(HEAL, level):
                            targets = []
                            for t in toons:
                                if t == toonId and not base.cr.selfToonUp:
                                    continue
                                if t != -1:
                                    target = self.battle.findToon(t)
                                    if target == None:
                                        continue
                                    tdict = {}
                                    tdict['toon'] = target
                                    tdict['hp'] = hps[toons.index(t)]
                                    self.notify.debug('HEAL: toon: %d healed for hp: %d' % (target.doId, hps[toons.index(t)]))
                                    targets.append(tdict)

                            if len(targets) > 0:
                                adict['target'] = targets
                            else:
                                targetGone = True
                        else:
                            targetIndex = atk[ATK_TGT_COL]
                            if targetIndex < 0:
                                targetGone = True
                            else:
                                targetId = toons[targetIndex]
                                target = self.battle.findToon(targetId)
                                if target != None:
                                    tdict = {}
                                    tdict['toon'] = target
                                    tdict['hp'] = hps[targetIndex]
                                    adict['target'] = tdict
                                else:
                                    targetGone = True
                    elif attackAffectsGroup(track, level, atk[ATK_TRACK_COL]):
                        targets = []
                        for s in suits:
                            if s != -1:
                                target = self.battle.findSuit(s)
                                if atk[ATK_TRACK_COL] == NPCSOS:
                                    if track == LURE and self.battle.isSuitLured(target) == 1:
                                        continue
                                    elif track == TRAP and (self.battle.isSuitLured(target) == 1 or target.battleTrap != NO_TRAP):
                                        continue
                                targetIndex = suits.index(s)
                                sdict = {}
                                sdict['suit'] = target
                                sdict['hp'] = hps[targetIndex]
                                if atk[ATK_TRACK_COL] == NPCSOS and track == DROP and hps[targetIndex] == 0:
                                    continue
                                sdict['kbbonus'] = kbbonuses[targetIndex]
                                sdict['died'] = atk[ATK_TGT_DIED_COL] & 1 << targetIndex
                                sdict['revived'] = atk[ATK_TGT_REVIVE_COL] & 1 << targetIndex
                                sdict['leftSuits'] = []
                                sdict['rightSuits'] = []
                                targets.append(sdict)

                        adict['target'] = targets
                    else:
                        targetIndex = atk[ATK_TGT_COL]
                        if targetIndex < 0:
                            targetGone = True
                        else:
                            targetId = suits[targetIndex]
                            target = self.battle.findSuit(targetId)
                            sdict = {}
                            sdict['suit'] = target
                            if self.battle.activeSuits.count(target) == 0:
                                targetGone = True
                                suitIndex = 0
                            else:
                                suitIndex = self.battle.activeSuits.index(target)
                            leftSuits = []
                            for si in range(0, suitIndex):
                                asuit = self.battle.activeSuits[si]
                                if self.battle.isSuitLured(asuit) == 0:
                                    leftSuits.append(asuit)

                            lenSuits = len(self.battle.activeSuits)
                            rightSuits = []
                            if lenSuits > suitIndex + 1:
                                for si in range(suitIndex + 1, lenSuits):
                                    asuit = self.battle.activeSuits[si]
                                    if self.battle.isSuitLured(asuit) == 0:
                                        rightSuits.append(asuit)

                            sdict['leftSuits'] = leftSuits
                            sdict['rightSuits'] = rightSuits
                            sdict['hp'] = hps[targetIndex]
                            sdict['kbbonus'] = kbbonuses[targetIndex]
                            sdict['died'] = atk[ATK_TGT_DIED_COL] & 1 << targetIndex
                            sdict['revived'] = atk[ATK_TGT_REVIVE_COL] & 1 << targetIndex
                            if track in (DROP, SQUIRT, TRAP):
                                adict['target'] = [sdict]
                            else:
                                adict['target'] = sdict
                    adict['hpbonus'] = atk[ATK_HPBONUS_COL]
                    adict['sidestep'] = atk[ATK_ACCBONUS_COL]
                    if 'npcId' in adict:
                        adict['sidestep'] = 0
                    adict['battle'] = self.battle
                    adict['playByPlayText'] = self.playByPlayText
                    if not targetGone:
                        self.attackDicts.append(adict)
                    else:
                        self.notify.warning('genAttackAttacks(): toon - target gone!')
            elif atk[ATK_AVTYPE_COL] == AVTYPE_SUIT:
                identifier = atk[ATK_TRACK_COL]
                suitIndex = atk[ATK_ID_COL]
                suitId = suits[suitIndex]
                suit = self.battle.findSuit(suitId)
                if suit == None:
                    self.notify.error('suit: %d not in battle!' % suitId)
                adict = {}
                adict['suitName'] = suit.getStyleName()
                adict['identifier'] = identifier
                adict['group'] = base.cr.dataPackMgr.getCogAttackTargetType(identifier)
                adict['animName'] = base.cr.dataPackMgr.getCogAttackAnimName(identifier)
                adict['suit'] = suit
                adict['battle'] = self.battle
                adict['playByPlayText'] = self.playByPlayText
                adict['playByPlayDescText'] = self.playByPlayDescText
                adict['taunt'] = atk[ATK_TAUNT_COL]
                self.handleSuitAttackDict(toons, atk, adict)
            else:
                identifier = atk[ATK_TRACK_COL]
                adict = {}
                adict['identifier'] = identifier
                adict['group'] = base.cr.dataPackMgr.getCogAttackTargetType(identifier)
                adict['battle'] = self.battle
                adict['playByPlayText'] = self.playByPlayText
                adict['playByPlayDescText'] = self.playByPlayDescText
                self.handleSuitAttackDict(toons, atk, adict)
