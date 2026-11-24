from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *

from panda3d.toontown import CFSpeech, CFTimeout

from otp.avatar import Emote

from panda3d.core import *

from toontown.battle import MovieSuitAttacks, MovieThrow, MovieSquirt, MovieUtil, PlayByPlayText
from toontown.episodes import DistributedEpisodeZone, EpisodeLocalizer
from toontown.episodes import EpisodeConfig
from toontown.shtiker import DisguisePage
from toontown.suit import Suit
from toontown.suit import SuitDNA
from ..toonbase.ToontownTypes import CogAppearanceIndex
from toontown.toonbase import TTLocalizer, ToontownGlobals, ToontownTimer, ToontownBattleGlobals
from toontown.town import TownBattleToonPanel, TownBattleCogPanel

import random


class CogBathroomBattle(NodePath):

    def __init__(self):
        NodePath.__init__(self, hidden.attachNewNode('CogBathroomBattle'))
        from toontown.battle import Movie
        self.movie = Movie.Movie(self)

    def getActorPosHpr(self, suit):
        return Point3(0, 0, 0), VBase3(suit.getH(), 0, 0)


class EP02DistributedCogBathroom(DistributedEpisodeZone.DistributedEpisodeZone):

    def __init__(self, cr):
        DistributedEpisodeZone.DistributedEpisodeZone.__init__(self, cr)
        self.episodeZoneId = EpisodeConfig.EP02_HIGH_RISE_BATHROOM

    def disable(self):
        DistributedEpisodeZone.DistributedEpisodeZone.disable(self)

        render.clearFog()

        self.fog = None

        self.cogHp = None
        
        self.body = None

        # The AI has cleaned up the NPC so we don't have to
        # do it here
        if hasattr(self, 'npc'):
            del self.npc

    def setNpcId(self, npcId):
        episodeStatus = base.cr.episodeManager.getEpisodeStatus(self.episodeZoneId)
        if episodeStatus == 0:
            self.npcId = npcId
            self.npc = self.cr.doId2do[npcId]
            self.npc.setupToonNodes()

    def generateGeom(self):
        self.geom = loader.loadModel('phase_14/models/modules/cog-bathroom')
        self.geom.reparentTo(render)
        self.geom.find('**/urinal1').setPosHpr(2, -1, 12, 0, 16, 16)

        self.fog = Fog("fog")
        self.fog.setColor(0, 0, 0)
        self.fog.setExpDensity(0.01)
        render.setFog(self.fog)

        self.doors = loader.loadModel('phase_14/models/props/bathroom-doors')
        self.doors.find('**/L_door').setY(4.10)
        self.doors.find('**/R_door').setY(-4.10)
        self.doors.setPosHpr(35.666, 22.974, 0.0, 47.6, 0.0, 0.0)
        self.doors.reparentTo(self.geom)

        collNode = CollisionNode('door_collision')
        collNode.addSolid(CollisionBox(0, 0.7, 4, 2))
        self.doors.attachNewNode(collNode)

    def acceptInteractions(self):
        leftDoor = self.doors.find('**/L_door')
        rightDoor = self.doors.find('**/R_door')

        self.acceptOnce('enterdoor_collision', self.handleDoorOpen, extraArgs=[leftDoor, rightDoor])

        collNode = CollisionNode('stall_collision')
        collNode.addSolid(CollisionSphere(-9.857, -36.127, 1.116, 2))
        self.geom.attachNewNode(collNode)

        self.acceptOnce('enterstall_collision', self.handleStall)

    def finishBattle(self):
        base.cr.episodeManager.setEpisodeStatus(EpisodeConfig.EP02_HIGH_RISE_BATHROOM, 1)
        self.sendUpdate('cleanupNpc', [])
        self.playChat(self.toon, wait=4.0, postClear=True)

    def handleDoorOpen(self, leftDoor, rightDoor, collEntry):
        self.toon.b_setAnimState('neutral')
        self.toon.wrtReparentTo(self.doors)

        doorSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_door_open.ogg')

        # Sometimes the play rate is -1 so let's make it look good
        self.toon.suit.setPlayRate(1, 'walk')

        seq = Parallel(Sequence(Func(base.camera.wrtReparentTo, render), Func(self.toon.disableAvatarControls),
                                Func(self.toon.deactivateCamera), Func(self.toon.collisionsOff),
                                Parallel(Sequence(Func(self.toon.suit.loop, 'walk'),
                                                  self.toon.posHprInterval(0.5, (-7.0, 0.0, 0.0), (-90.0, 0.0, 0.0)),
                                                  Func(self.toon.suit.loop, 'neutral')),
                                         base.camera.posHprInterval(1.7, (11.097, 6.6870, 9.9445), (-57.0, -10.0, 0.0),
                                                                    blendType='easeInOut')),
                                Parallel(Sequence(Func(self.toon.suit.loop, 'walk'),
                                                  self.toon.posInterval(2.0, (10.5, 0.0, 0.0)),
                                                  Func(self.toon.wrtReparentTo, render)),
                                         Sequence(Wait(3.5), Func(base.transitions.fadeOut), Wait(1),
                                                  Func(self.toon.attachCamera), Func(self.toon.initializeSmartCamera),
                                                  Func(self.toon.activateCamera), Func(self.toon.show),
                                                  Func(self.teleportToZone, self.zoneConnections[0])))),
                       Sequence(Wait(1.7), Func(base.playSfx, doorSfx, volume=1),
                                Parallel(Sequence(LerpHprInterval(leftDoor, 1, (80, 0, 0), (0, 0, 0),
                                                                  blendType='easeInOut'),
                                                  LerpHprInterval(leftDoor, 1.5, (-60, 0, 0), blendType='easeInOut'),
                                                  LerpHprInterval(leftDoor, 1.5, (30, 0, 0), blendType='easeInOut'),
                                                  LerpHprInterval(leftDoor, 1.5, (0, 0, 0), blendType='easeInOut')),
                                         Sequence(LerpHprInterval(rightDoor, 1, (-80, 0, 0), (0, 0, 0),
                                                                  blendType='easeInOut'),
                                                  LerpHprInterval(rightDoor, 1.5, (60, 0, 0), blendType='easeInOut'),
                                                  LerpHprInterval(rightDoor, 1.5, (-30, 0, 0), blendType='easeInOut'),
                                                  LerpHprInterval(rightDoor, 1.5, (0, 0, 0), blendType='easeInOut')))))
        seq.start()

    def handleStall(self, collEntry):
        waterSfx = base.loader.loadSfx('phase_8/audio/sfx/SZ_DG_fountain_loop.ogg')
        dialogue = EpisodeLocalizer.ShortChangeBathroomDialogue
        seq = Sequence(Func(base.transitions.irisOut, 1.0), Wait(2.0),
                       Func(base.playSfx, waterSfx, volume=0.5), Wait(waterSfx.length()),
                       Func(self.toon.setPosHpr, 34.045, -1.995, 0.025, 270, 0, 0), Func(base.transitions.irisIn, 2.0),
                       Wait(2.0), self.getChatSequence(self.toon, dialogue[4]),
                       Func(self.playChat, self.toon, wait=3.0, postClear=True))
        seq.start()

    def playBattleMusic(self):
        place = base.cr.playGame.getPlace()
        if place:
            place.loader.music.stop()
        base.playMusic(self.battleMusic, looping = 1)

    def cleanupBattleMusic(self):
        if hasattr(self, 'battleMusic'):
            self.battleMusic.stop()
            del self.battleMusic

    def generateMovie(self):
        base.cr.episodeManager.setEpisodeStatus(EpisodeConfig.EP02_HIGH_RISE_HALLWAY, 1)
        episodeStatus = base.cr.episodeManager.getEpisodeStatus(self.episodeZoneId)
        if episodeStatus == 0:
            leftDoor = self.doors.find('**/L_door')
            rightDoor = self.doors.find('**/R_door')

            self.npc.hp = 5
            self.npc.maxHp = 32
            self.npc.loop('neutral')
            self.npc.setPosHpr(-10.76, -17.10, 0.0, 292.0, 0.0, 0.0)

            suitHeight = self.toon.suit.getHeight()
            height = suitHeight * 0.66

            self.battleMusic = base.loader.loadMusic('phase_9/audio/bgm/encntr_suit_winning.ogg')
            doorSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_door_open.ogg')

            dialogue = EpisodeLocalizer.ShortChangeBathroomDialogue
            self.movie = Sequence(Func(self.lockToon), Func(self.toon.setPosHpr, 41.954, 28.833, 0.0, 135., 0.0, 0.0),
                                  Func(self.toon.suit.loop, 'walk'), Func(aspect2d.hide),
                                  Func(base.camera.setPosHpr, 14.929, 13.126, 4.4499, -70.0, 0.0, 0.0),
                                  Parallel(Sequence(Wait(1.0), Func(base.playSfx, doorSfx, volume=1),
                                                    LerpHprInterval(leftDoor, 1, (-80, 0, 0), (0, 0, 0),
                                                                    blendType='easeInOut'),
                                                    LerpHprInterval(leftDoor, 1.5, (60, 0, 0), blendType='easeInOut'),
                                                    LerpHprInterval(leftDoor, 1.5, (-30, 0, 0), blendType='easeInOut'),
                                                    LerpHprInterval(leftDoor, 1.5, (0, 0, 0), blendType='easeInOut')),
                                           Sequence(Wait(1.0), LerpHprInterval(rightDoor, 1, (80, 0, 0), (0, 0, 0),
                                                                               blendType='easeInOut'),
                                                    LerpHprInterval(rightDoor, 1.5, (-60, 0, 0), blendType='easeInOut'),
                                                    LerpHprInterval(rightDoor, 1.5, (30, 0, 0), blendType='easeInOut'),
                                                    LerpHprInterval(rightDoor, 1.5, (0, 0, 0), blendType='easeInOut')),
                                           Sequence(LerpPosInterval(self.toon, 2.0, pos=(32.762, 19.641, 0.0)),
                                                    Func(self.toon.suit.loop, 'neutral'), Wait(1.0),
                                                    self.getChatSequence(self.toon, dialogue[0]))),
                                  Func(base.camera.setPosHpr, 16.584, -5.383, 3.7503, 111.0, -1.2, 0.0),
                                  Parallel(LerpPosHprInterval(base.camera, 1.0, pos=(-2.094, -13.16, 3.7503),
                                                              hpr=(112.0, -2.7, 0.0)),
                                           self.getChatSequence(self.npc, dialogue[1], chatFlags=CFSpeech | CFTimeout),
                                           Func(Emote.globalEmote.doEmote, self.npc, 19)),
                                  Wait(2.0), Func(base.camera.wrtReparentTo, self.toon), self.getChatSequence(self.npc),
                                  Func(base.camLens.setMinFov, ToontownBattleGlobals.BattleCamFaceOffFov / (4. / 3.)),
                                  Func(base.camera.setPos, random.choice((-5, 5)), 16, random.choice((height, 1, 11))),
                                  Func(base.camera.lookAt, self.toon, Point3(0, 0, suitHeight)),
                                  Func(self.playBattleMusic),
                                  self.getChatSequence(self.toon, dialogue[2], preClear=True),
                                  Func(aspect2d.show), Wait(5.0),
                                  Func(self.toon.setPosHpr, 25.481, 16.850, 0.057, 131.2, 0, 0),
                                  Func(self.npc.setPosHpr, 0.2350, -7.88, 0.0, -45.0, 0, 0),
                                  Func(base.camLens.setMinFov, ToontownGlobals.DefaultCameraFov / (4. / 3.)),
                                  Func(base.camera.wrtReparentTo, render),
                                  Func(base.camera.setPosHpr, 27, 30, 4.5, 150, 0, 0),
                                  self.getChatSequence(self.toon), Func(self.generateBattle))
        elif episodeStatus == 1:
            self.movie = Sequence(Func(self.toon.setPosHpr, 22.762, 13.641, 0.0, 131.2, 0.0, 0.0),
                                  Func(self.acceptInteractions))

    def generateBattle(self):
        self.toon.suit.battleTrapProp = None
        self.cogHp = 6
        self.playByPlayText = PlayByPlayText.PlayByPlayText(fg=(0.5, 0.5, 0.5, 1.0))
        self.playByPlayText.hide()
        self.enterBattleSelect()

    def enterBattleSelect(self):
        self.battleTimer = ToontownTimer.ToontownTimer()
        self.battleTimer.posInTopRightCorner()
        self.battleTimer.countdown(ToontownGlobals.ShortWorkBathroomBattleDuration, self.timerCallback)

        self.cogPanel = TownBattleCogPanel.TownBattleCogPanel(0)
        self.cogPanel.setCogMeter(self.toon.suit, level=1)
        self.cogPanel.updateCogMeter()
        self.cogPanel.setZ(-0.75)
        self.cogPanel.show()

        self.toonPanel = TownBattleToonPanel.TownBattleToonPanel(1)
        self.toonPanel.setLaffMeter(self.npc, hp=self.npc.hp, maxHp=self.npc.maxHp)
        self.toonPanel.setZ(0.75)
        self.toonPanel.show()

        battleGui = loader.loadModel('phase_3.5/models/gui/suit_detail_panel')
        self.attackPanel = DirectFrame(parent=aspect2d, frameColor=(.9, .9, .9, 1), frameSize=(-1, 1, -1, 1),
                                  pos=(-0.520, 0.0, -0.110), scale=.09, geom=battleGui, geom_scale=(2.2, 1, 2.2))
        self.infoPanel = DirectFrame(parent=aspect2d, frameColor=(.9, .9, .9, 1), frameSize=(-1, 1, -1, 1),
                                     pos=(-0.041, 5.8291, 0.1599), hpr=(0, 0, 90), scale=.09, geom=battleGui,
                                     geom_scale=(1.3, 0.5, 1.1), text='Choose An Attack', text_font=ToontownGlobals.getSuitFont(),
                                     text_scale=0.4, text_pos=(0, 0.5))
        self.infoPanel['text_hpr'] = (0, 0, -90)
        self.attackLabel = DirectLabel(parent=aspect2d, relief=None, pos=(-0.198, 5.8291, 0.1099), scale=.09,
                                       text='', text_font=ToontownGlobals.getSuitFont(), text_align=TextNode.ALeft,
                                       text_scale=0.3, text_pos=(0, 0.5))
        battleGui.removeNode()

        self.attackButtons = []
        self.attackSpins = []
        attackInfo = ToontownGlobals.ShortWorkBathroomBattleAttackInfo
        for attack in attackInfo:
            prop = loader.loadModel('phase_%s/models/props/%s' % (attack[0], attack[1]))
            prop.setPosHpr(*attack[6])
            attackButton = self.makeFrameModel(prop, self.attackPanel, attackInfo.index(attack))
            attackButton.bind(DGG.ENTER, self.selectAttack, extraArgs=[attackInfo.index(attack)])
            attackButton.bind(DGG.EXIT, self.selectAttack, extraArgs=[-1])
            self.attackButtons.append(attackButton)

    def exitBattleSelect(self):
        self.battleTimer.destroy()
        del self.battleTimer
        self.cogPanel.cleanup()
        del self.cogPanel
        self.toonPanel.cleanup()
        del self.toonPanel

        for ival in self.attackSpins:
            ival.finish()
            del ival

        for button in self.attackButtons:
            button.destroy()
            del button

        self.attackPanel.destroy()
        del self.attackPanel
        self.infoPanel.destroy()
        del self.infoPanel
        self.attackLabel.destroy()
        del self.attackLabel

    def selectAttack(self, index, collEntry=None):
        if index == -1:
            self.infoPanel['text'] = EpisodeLocalizer.ShortWorkBathroomBattleChooseAttack
            self.attackLabel['text'] = ''

            for ival in self.attackSpins:
                ival.finish()
                del ival
            return

        attackInfo = ToontownGlobals.ShortWorkBathroomBattleAttackInfo[index]
        self.infoPanel['text'] = attackInfo[2]

        accuracy = attackInfo[4]
        if accuracy <= 50:
            accStr = TTLocalizer.BattleGlobalAvTrackAccLow
        elif accuracy <= 75:
            accStr = TTLocalizer.BattleGlobalAvTrackAccMedium
        elif accuracy >= 95:
            accStr = TTLocalizer.BattleGlobalAvTrackAccHigh
        else:
            accStr = TTLocalizer.BattleGlobalAvTrackAccPerfect

        if attackInfo[5]:
            affectStr = TTLocalizer.InventoryAffectsAllToons
        else:
            affectStr = TTLocalizer.InventoryAffectsOneToon
        self.attackLabel['text'] = EpisodeLocalizer.ShortWorkBathroomBattleAttackLbl.format(accStr, attackInfo[3], affectStr)

        for seq in self.attackSpins:
            seq.finish()
            del seq

        self.attackSpins = []
        for x in range(4):
            geom = self.attackButtons[index]['geom' + str(x) + '_geom'].find('rotate')
            seq = LerpHprInterval(geom, 10, VBase3(geom.getH() - 360, 0, 0))
            self.attackSpins.append(seq)
            seq.loop()

    def makeFrame(self, parent, geom, index):
        framePos = [3, 1, -1, -3]
        frame = DirectButton(parent=parent, geom=geom, frameSize=(-1.0, 1.0, -1.0, 1.0),
                             pos=(0, 0, framePos[index]), relief=None, command=self.advanceRound, extraArgs=[index])
        return frame

    def makeFrameModel(self, model, parent, index):
        model.setDepthTest(1)
        model.setDepthWrite(1)
        pitch = aspect2d.attachNewNode('pitch')
        rotate = pitch.attachNewNode('rotate')
        scale = rotate.attachNewNode('scale')
        model.reparentTo(scale)
        bMin, bMax = model.getTightBounds()
        center = (bMin + bMax) / 2.0
        model.setPos(-center[0], -center[1], -center[2])
        pitch.setP(20)
        bMin, bMax = pitch.getTightBounds()
        center = (bMin + bMax) / 2.0
        corner = Vec3(bMax - center)
        scale.setScale(1.0 / max(corner[0], corner[1], corner[2]))
        pitch.setY(2)
        frame = self.makeFrame(parent, pitch, index)
        pitch.removeNode()
        return frame

    def timerCallback(self):
        self.advanceRound(-1)

    def advanceRound(self, attackIndex):
        self.exitBattleSelect()
        cogIval, cogDamage = self.getCogAttack(attackIndex)
        toonIval, toonDamage = self.getToonAttack()

        self.cogHp -= toonDamage
        toonHp = self.npc.hp - cogDamage

        battleIval = Sequence(toonIval)

        if self.cogHp > 0:
            if toonHp <= 0:
                battleIval.append(Parallel(cogIval, Sequence(Wait(cogIval.getDuration() - 6.0),
                                                             Func(self.npc.setAnimState, 'Died'))))
                battleIval.append(Func(self.npc.removeActive))
            else:
                battleIval.append(cogIval)
            battleIval.append(Func(self.toon.suit.loop, 'neutral'))
            if toonHp <= 0:
                battleIval.append(Func(self.endBattle, True))
            else:
                battleIval.append(Wait(0.5))
                battleIval.append(Func(self.enterBattleSelect))
        else:
            battleIval.append(Func(self.endBattle, False))

        battleIval.start()

    def endBattle(self, success):
        if success:

            def incrementCogbucks(bar):
                bar['value'] = 40
                bar['text'] = TTLocalizer.RewardPanelMeritAlert
                bar['barColor'] = (DisguisePage.DeptColors[2][0], DisguisePage.DeptColors[2][1],
                                   DisguisePage.DeptColors[2][2], 1)

            gscale = (TTLocalizer.RPdirectFrame[0], TTLocalizer.RPdirectFrame[1], TTLocalizer.RPdirectFrame[2] * 1.1)
            rewardPanel = DirectFrame(parent=aspect2d, relief=None, geom=DGG.getDefaultDialogGeom(),
                                      geom_color=ToontownGlobals.GlobalDialogColor, geom_pos=Point3(0, 0, -.05),
                                      geom_scale=gscale, pos=(0.35, 0, 0))
            cogbucksBar = DirectWaitBar(parent=rewardPanel, relief=DGG.SUNKEN, frameSize=(-1, 1, -0.15, 0.15),
                                        borderWidth=(0.02, 0.02), scale=0.35,
                                        frameColor=(DisguisePage.DeptColors[2][0] * 0.7,
                                                    DisguisePage.DeptColors[2][1] * 0.7,
                                                    DisguisePage.DeptColors[2][2] * 0.7, 1),
                                        barColor=(DisguisePage.DeptColors[2][0] * 0.8,
                                                  DisguisePage.DeptColors[2][1] * 0.8,
                                                  DisguisePage.DeptColors[2][2] * 0.8, 1),
                                        text= EpisodeLocalizer.ShortWorkBathroomBattleDefaultCogbuckAmt + TTLocalizer.RewardPanelMeritBarLabels[2],
                                        text_scale=TTLocalizer.RPmeritBarLabels, text_fg=(0, 0, 0, 1),
                                        text_align=TextNode.ALeft, text_pos=(-0.96, -0.0525), pos=(0, 0, -0.375), range=40,
                                        value=38)
            levelLabel = DirectLabel(parent=rewardPanel, relief=None, text= EpisodeLocalizer.ShortWorkBathroomBattleLevelLbl, text_scale=0.1, pos=(0, 0, 0.225))

            body = rewardPanel.attachNewNode('body')
            self.body = Suit.Suit()
            dna = SuitDNA.SuitDNA()
            dna.newSuit(self.toon.suit.style.name)
            self.body.setDNA(dna)
            self.body.update()
            self.body.reparentTo(rewardPanel)
            self.body.setH(180)
            self.body.getGeomNode().setScale(0.085)
            self.body.setZ((-.38, -0.3, -0.3)[self.body.appearance[CogAppearanceIndex.BODY_TYPE]])
            self.body.setDepthTest(1)
            self.body.setDepthWrite(1)
            self.body.pose('neutral', 30)

            icons = loader.loadModel('phase_3/models/gui/cog_icons')
            deptIcon = icons.find('**/MoneyIcon').copyTo(rewardPanel)
            icons.removeNode()
            deptIcon.setPos(0, 0, -0.125)
            deptIcon.setScale(0.33)
            deptIcon.hide()
            dialogue = EpisodeLocalizer.ShortChangeBathroomDialogue
            successIval = Sequence(Func(self.toon.suit.loop, 'victory'), Wait(2.0),
                                   Func(incrementCogbucks, cogbucksBar), Wait(3.0), Func(cogbucksBar.destroy),
                                   Func(self.body.removeNode), Func(deptIcon.show),
                                   Func(levelLabel.setText, TTLocalizer.RewardPanelMeritAlert), Wait(4.0),
                                   Func(deptIcon.removeNode), Func(levelLabel.destroy), Func(rewardPanel.destroy),
                                   Func(self.toon.suit.loop, 'neutral'), Func(self.toon.setPos, 22.762, 13.641, 0.0),
                                   Func(self.cleanupBattleMusic), Func(self.playZoneMusic), Func(self.toon.attachCamera),
                                   Func(self.toon.enableAvatarControls), Func(self.toon.initializeSmartCamera),
                                   Func(self.toon.activateCamera),
                                   Func(self.toon.collisionsOn), Wait(1.0),
                                   self.getChatSequence(self.toon, dialogue[3], preClear=True),
                                   Func(self.acceptInteractions), Func(self.finishBattle))
        else:

            def removeDeathSuit(suit, deathSuit):
                if not deathSuit.isEmpty():
                    deathSuit.detachNode()
                    suit.cleanupLoseActor()

            self.generateStory()
            self.story.hide()
            self.story.setPos(-0.8, 0, -0.5)

            deathSuit = self.toon.suit.getLoseActor()
            ival = Sequence(Func(deathSuit.setPos, self.toon.getPos()), Func(deathSuit.setHpr, self.toon.getHpr()),
                            Func(self.toon.hide), Func(deathSuit.wrtReparentTo, render),
                            ActorInterval(deathSuit, 'lose', duration=MovieUtil.SUIT_LOSE_DURATION),
                            Func(removeDeathSuit, self.toon.suit, deathSuit))
            spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Cog_Death.ogg')
            deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
            deathSoundTrack = Sequence(Wait(0.8), SoundInterval(spinningSound, duration=1.2, startTime=1.5, volume=0.2,
                                                                node=deathSuit),
                                       SoundInterval(spinningSound, duration=3.0, startTime=0.6, volume=0.8,
                                                     node=deathSuit),
                                       SoundInterval(deathSound, volume=0.32, node=deathSuit))
            deathIval = Parallel(ival, deathSoundTrack)
            successIval = Sequence(deathIval, Wait(1.0), Func(self.npc.loop, 'victory'),
                                   Func(self.enterText, self.story),
                                   Func(self.speakText, self.story, EpisodeLocalizer.ShortWorkDefeatCard[0]),
                                   Wait(9.0), Func(self.speakText, self.story, EpisodeLocalizer.ShortWorkDefeatCard[1]),
                                   Wait(4.5), Func(self.leaveText, self.story), Wait(1.5),
                                   Func(base.transitions.irisOut, 2.0), Wait(3.0), Func(self.releaseToon),
                                   # We gotta manually cleanup the NPC here to prevent a crash
                                   Func(self.sendUpdate, 'cleanupNpc', []),
                                   Func(self.cleanupBattleMusic),
                                   Func(self.endEpisode))
        if self.playByPlayText != None:
            self.playByPlayText.cleanup()
        self.playByPlayText = None
        successIval.start()

    def getCogAttack(self, attackIndex):
        if attackIndex == -1:
            return Sequence(), 0

        attackInfo = ToontownGlobals.ShortWorkBathroomBattleAttackInfo[attackIndex]

        if config.GetBool('bathroom-battle-instakill', False):
            # Force NPC instakill
            damage = self.npc.hp
        else:
            if config.GetBool('bathroom-battle-perfect-accuracy', False):
                # Force perfect accuracy
                damage = attackInfo[3]
            else:
                accuracy = attackInfo[4]

                if random.random() < accuracy / 100:
                    damage = attackInfo[3]
                else:
                    damage = 0
        seq = Sequence()
        seq.append(self.getChatSequence(self.toon))     # always clear chat beforehand
        seq.append(Parallel(
            self.getCogAttackIval(attackIndex, damage),
            self.getChatSequence(self.toon, wait=3.0, postClear=True)   # clear chat after a bit
        ))
        return seq, damage

    def getCogAttackIval(self, attackIndex, damage):
        battle = CogBathroomBattle()
        battle.setPos(self.toon.getX(), self.toon.getY(), self.toon.getZ())
        target = {'toon': self.npc,
                  'hp': damage,
                  'died': self.npc.hp - damage <= 0,
                  'leftToons': [],
                  'rightToons': []}
        attack = {'suit': self.toon.suit,
                  'parent': self.toon,
                  'suitName': 'sc',
                  'battle': battle,
                  'target': [target],
                  'name': ToontownGlobals.ShortWorkBathroomBattleAttackInfo[attackIndex][2],
                  'animName': ToontownGlobals.ShortWorkBathroomBattleAttackInfo[attackIndex][7],
                  'taunt': None}

        if attackIndex == 0:
            return MovieSuitAttacks.doWatercooler(attack)
        elif attackIndex == 1:
            return MovieSuitAttacks.doBounceCheck(attack)
        elif attackIndex == 2:
            return MovieSuitAttacks.doPickPocket(attack)
        elif attackIndex == 3:
            return MovieSuitAttacks.doClipOnTie(attack)

    def getToonAttack(self):
        if config.GetBool('bathroom-battle-toon-always-pass', False):
            attackIndex = 2
        else:
            rng = random.random()
            if rng <= 0.35:
                attackIndex = 0
            elif rng <= 0.7:
                attackIndex = 1
            else:
                attackIndex = 2

        attackInfo = ToontownGlobals.ShortWorkBathroomBattleToonAttackInfo[attackIndex]
        accuracy = attackInfo[1]

        if random.random() < accuracy / 100:
            damage = attackInfo[0]
        else:
            damage = 0
        seq = self.getToonAttackIval(attackIndex, damage)
        return seq, damage

    def getToonAttackIval(self, attackIndex, damage):
        battle = CogBathroomBattle()
        battle.setPos(self.toon.getX(), self.toon.getY(), self.toon.getZ())
        target = {'suit': self.toon,
                  'suitGeom': self.toon.suit,
                  'hp': damage,
                  'kbbonus': 0,
                  'died': 0,
                  'revived': 0,
                  'leftSuits': [],
                  'rightSuits': []}
        attack = {'toon': self.npc,
                  'hpbonus': 0,
                  'target': target,
                  'sidestep': 0,
                  'level': 0,
                  'battle': battle}

        if attackIndex == 0:
            toonTracks = Parallel()
            tracks = MovieThrow.throwPie(attack, 0, 0)
            for track in tracks:
                toonTracks.append(track)
            displayName = TTLocalizer.BattleGlobalAvPropStrings[4][0] + '!'
            pbpTrack = self.playByPlayText.getShowInterval(displayName, 3.5)
            toonTracks.append(pbpTrack)
            return toonTracks
        elif attackIndex == 1:
            displayName = TTLocalizer.BattleGlobalAvPropStrings[5][0] + '!'
            pbpTrack = self.playByPlayText.getShowInterval(displayName, 3.5)
            flowerTrack = MovieSquirt.doFlower(attack, 0, 0)
            return Parallel(pbpTrack, flowerTrack)
        elif attackIndex == 2:
            return Sequence()
