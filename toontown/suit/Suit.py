from direct.actor import Actor
from direct.gui import DirectGuiGlobals
from direct.gui.DirectWaitBar import DirectWaitBar
from direct.interval.IntervalGlobal import *
from direct.task.Task import Task

from otp.avatar import Avatar
from otp.avatar.ShadowCaster import globalDropShadowGrayLevel
from otp.otpbase import OTPGlobals
from panda3d.core import *
from panda3d.toontown import *

from toontown.battle import BattleParticles
from toontown.battle import BattleProps
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals, ClientSettings
from toontown.toonbase import TTLocalizer

from . import SuitDNA
from . import SuitTimings

from ..datapack.DataPackManager import DataPackManager
from ..toonbase.ToontownTypes import TCogAppearance_D, CogAppearanceIndex

aSize = 6.06
SuitDialogArray = []
SkelSuitDialogArray = []

AllSuits = (('walk', 'walk'), ('run', 'walk'), ('neutral', 'neutral'), ('griddy', 'griddy'))
AllSuitsMinigame = (('victory', 'victory'),
 ('flail', 'flailing'),
 ('tug-o-war', 'tug-o-war'),
 ('slip-backward', 'slip-backward'),
 ('slip-forward', 'slip-forward'))
AllSuitsTutorialBattle = (('lose', 'lose'), ('pie-small-react', 'pie-small'), ('squirt-small-react', 'squirt-small'))
AllSuitsBattle = (('drop-react', 'anvil-drop'),
 ('flatten', 'drop'),
 ('sidestep-left', 'sidestep-left'),
 ('sidestep-right', 'sidestep-right'),
 ('squirt-large-react', 'squirt-large'),
 ('landing', 'landing'),
 ('reach', 'walknreach'),
 ('rake-react', 'rake'),
 ('hypnotized', 'hypnotize'),
 ('lured', 'lured'),
 ('soak', 'soak'))
SuitsCEOBattle = (('sit', 'sit'),
 ('sit-eat-in', 'sit-eat-in'),
 ('sit-eat-loop', 'sit-eat-loop'),
 ('sit-eat-out', 'sit-eat-out'),
 ('sit-angry', 'sit-angry'),
 ('sit-hungry-left', 'leftsit-hungry'),
 ('sit-hungry-right', 'rightsit-hungry'),
 ('tray-walk', 'tray-walk'),
 ('tray-neutral', 'tray-neutral'),
 ('sit-lose', 'sit-lose'))
ModelDict = {'a': ('/models/char/suitA-', 4),
    'b': ('/models/char/suitB-', 4),
    'c': ('/models/char/suitC-', 3.5)}
SuitBattleAnims = {
    'all': (
            ('magic1', 'magic1', 5),
            ('magic2', 'magic2', 5),
            ('pickpocket', 'pickpocket', 5),
            ('speak', 'speak', 5),
            ('finger-wag', 'finger-wag', 5),
            ('effort', 'effort', 5),
            ('throw-paper', 'throw-paper', 5),
            ('pen-squirt', 'fountain-pen', 5),
            ('phone', 'phone', 5)
        ),
    'a': (
            ('throw-object', 'throw-object', 5),
            ('roll-o-dex', 'roll-o-dex', 5),
            ('glower', 'glower', 5),
            ('magic3', 'magic3', 5),
            ('golf-club-swing', 'golf-club-swing', 5),
            ('rubber-stamp', 'rubber-stamp', 5),
            ('smile', 'smile', 5),
            ('cigar-smoke', 'cigar-smoke', 8),
            ('song-and-dance', 'song-and-dance', 8),
            ('active-state', 'active-state', 5),
            ('heated-discussion', 'heated-discussion', 5)
        ),
    'b': (
            ('throw-object', 'throw-object', 5),
            ('roll-o-dex', 'roll-o-dex', 5),
            ('pencil-sharpener', 'pencil-sharpener', 5),
            ('hold-eraser', 'hold-eraser', 5),
            ('hold-pencil', 'hold-pencil', 5),
            ('magic3', 'magic3', 5),
            ('stomp', 'stomp', 5),
            ('quick-jump', 'jump', 5)
        ),
    'c': (
            ('shredder', 'shredder', 3.5),
            ('glower', 'glower', 5),
            ('rubber-stamp', 'rubber-stamp', 5),
            ('watercooler', 'watercooler', 5)
        )
}

ParticleRefCount = 0
ParticleThreshold = 5
ParticleList = []


def loadTutorialSuit():
    loader.loadModel('phase_3.5/models/char/suitC-mod').node()
    loadDialog()


def loadSuits():
    loadSuitModelsAndAnims(flag=1)
    loadDialog()


def unloadSuits():
    loadSuitModelsAndAnims(flag=0)
    unloadDialog()


def loadSuitModelsAndAnims(flag = 0):
    for key in list(ModelDict.keys()):
        model, phase = ModelDict[key]
        headModel, headPhase = ModelDict[key]

        if flag:
            loader.loadModel(f'phase_3.5{model}mod').node()
            loader.loadModel(f'phase_{headPhase}{headModel}heads').node()
        else:
            loader.unloadModel(f'phase_3.5{model}mod')
            loader.unloadModel(f'phase_{headPhase}{headModel}heads')


def loadDialog():
    global SuitDialogArray
    if len(SuitDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        if ClientSettings.ClassicSFX.get():
            SuitDialogFiles = ['COG_VO_grunt',
                               'COG_VO_murmur',
                               'COG_VO_statement',
                               'COG_VO_question_retro',
                               'COG_VO_grunt']
        else:
            SuitDialogFiles = ['COG_VO_grunt',
                               'COG_VO_murmur',
                               'COG_VO_statement',
                               'COG_VO_question',
                               'COG_VO_grunt']
        for dialog in SuitDialogFiles:
            SuitDialogArray.append(loader.loadSfx(f'{loadPath}{dialog}.ogg', manager = 'dialog'))


def loadSkelDialog():
    global SkelSuitDialogArray
    if len(SkelSuitDialogArray) > 0:
        return
    else:
        grunt = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_grunt.ogg', manager = 'dialog')
        murmur = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_murmur.ogg', manager = 'dialog')
        statement = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_statement.ogg', manager = 'dialog')
        question = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_question.ogg', manager = 'dialog')
        SkelSuitDialogArray = [grunt,
         murmur,
         statement,
         question,
         grunt]


def unloadDialog():
    global SuitDialogArray
    SuitDialogArray = []


def unloadSkelDialog():
    global SkelSuitDialogArray
    SkelSuitDialogArray = []


class Suit(Avatar.Avatar):
    healthColors = (Vec4(0, 1, 0, 1),
     Vec4(1, 1, 0, 1),
     Vec4(1, 0.5, 0, 1),
     Vec4(1, 0, 0, 1),
     Vec4(0.3, 0.3, 0.3, 1),
     Vec4(0.3, 1, 1, 1))
    healthGlowColors = (Vec4(0.25, 1, 0.25, 0.5),
     Vec4(1, 1, 0.25, 0.5),
     Vec4(1, 0.5, 0.25, 0.5),
     Vec4(1, 0.25, 0.25, 0.5),
     Vec4(0.3, 0.3, 0.3, 0),
     Vec4(0.3, 1, 1, 0.5))
    medallionColors = {'c': Vec4(0.863, 0.776, 0.769, 1.0),
     's': Vec4(0.843, 0.745, 0.745, 1.0),
     'l': Vec4(0.749, 0.776, 0.824, 1.0),
     'm': Vec4(0.749, 0.769, 0.749, 1.0)}
    # This is here to fix crashes in the Short Work episode
    HpTextEnabled = 1
    ghostMode = 0
    HpTextGenerator = TextNode('HpTextGenerator')

    def __init__(self, isToon = False):
        try:
            self.Suit_initialized
            return
        except:
            self.Suit_initialized = 1

        Avatar.Avatar.__init__(self)
        self.setFont(ToontownGlobals.getSuitFont())
        self.setPlayerType(NametagGroup.CCSuit)
        self.setPickable(1)
        self.battleDetectName = None
        self.leftHand = None
        self.rightHand = None
        self.shadowJoint = None
        self.nametagJoint = None
        self.headParts = []
        self.healthBar = None
        self.healthCondition = 0
        self.corpMedallion = None
        self.isToon = isToon
        self.isSkeleton = 0
        self.isVirtual = 0
        self.isWaiter = 0
        self.isRental = 0
        self.isSkeleRevive = 0
        self.particleEffect = None
        self.prop = None
        self.propInSound = None
        self.propOutSound = None
        self.hpText = None
        self.hpTextSeq = None
        self.sillySurgeText = False
        self.interactivePropTrackBonus = -1

        self.appearance: TCogAppearance_D = None

    def delete(self):
        try:
            self.Suit_deleted
        except:
            self.Suit_deleted = 1
            if self.leftHand:
                self.leftHand.removeNode()
                self.leftHand = None
            if self.rightHand:
                self.rightHand.removeNode()
                self.rightHand = None
            if self.shadowJoint:
                self.shadowJoint.removeNode()
                self.shadowJoint = None
            if self.nametagJoint:
                self.nametagJoint.removeNode()
                self.nametagJoint = None
            for part in self.headParts:
                part.removeNode()
            self.cleanupParticleEffect()

            self.headParts = []
            self.removeHealthBar()
            Avatar.Avatar.delete(self)

    def setHeight(self, height):
        Avatar.Avatar.setHeight(self, height)
        self.nametag3d.setPos(0, 0, height + 1.0)

    def getRadius(self):
        return 2

    def setDNAString(self, dnaString):
        self.dna = SuitDNA.SuitDNA()
        self.dna.makeFromNetString(dnaString)
        self.setDNA(self.dna)

    def setDNA(self, dna):
        self.appearance: TCogAppearance_D = base.cr.dataPackMgr.getCogAppearance(dna.name)
        if self.style:
            self.removePart('modelRoot')
            self.style = dna
            self.generateSuit()
            self.loop('neutral')
        else:
            self.style = dna
            self.generateSuit()

        self.initializeDropShadow()
        self.initializeNametag3d()

    def initializeDropShadow(self, hasGeomNode = True):
        if self.appearance[CogAppearanceIndex.SCALE] >= 0.6:
            Avatar.Avatar.initializeDropShadow(self, hasGeomNode)
        else:
            dropShadow = Avatar.ShadowCaster.dropShadowModel.copyTo(self)
            dropShadow.setScale(0.4)
            dropShadow.flattenMedium()
            dropShadow.setBillboardAxis(2)
            dropShadow.setColor(0.0, 0.0, 0.0, globalDropShadowGrayLevel, 1)
            self.dropShadow = dropShadow
            if self.getShadowJoint():
                dropShadow.reparentTo(self.getShadowJoint())
            else:
                self.dropShadow.hide()

    def generateSuit(self):
        dna = self.style
        self.headParts = []
        self.headColor = None
        self.headTexture = None
        self.loseActor = None
        self.isSkeleton = 0

        headModels, bodyType, scale, height, torsoTex, \
            legTex, armTex, wristTex, shoeTex, name, nameS, \
            nameP, handTex, handColor, colorScale, skeletonColorScale, \
            virtualColorScale, medallionColor, isSkeleton, isVirtual, \
            voiceGrunt, voiceMurmur, voiceStatement, voiceQuestion, \
            skeletonGrunt, skeletonMurmur, skeletonStatement, skeletonQuestion, quoteSets = self.appearance

        self.scale = scale
        self.handColor = VBase4(*handColor)

        self.generateBody()

        self.setHeight(height)

        self.getGeomNode().setScale(self.scale)
        self.getGeomNode().setColorScale(VBase4(*colorScale))
        self.generateHealthBar()
        self.generateCorporateMedallion()
        self.setBlend(frameBlend=ClientSettings.SmoothAnimations.get())
        self.setLODAnimation(750, 20, 0.4)

        if isSkeleton:
            self.makeSkeleton()
        if isVirtual:
            self.makeVirtual()

        self.generateHeads()
        self.setName(DataPackManager.getLocalizedText(name))

    def getBodyType(self):
        return 'abc'[self.appearance[CogAppearanceIndex.BODY_TYPE]]

    def generateBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.getBodyType()]
        self.loadModel(f'phase_3.5{filePrefix}mod')
        self.loadAnims(animDict)
        self.setSuitClothes()

    def generateAnimDict(self):
        _body = self.getBodyType()
        animDict = {}
        filePrefix, bodyPhase = ModelDict[_body]
        for anim in AllSuits:
            animDict[anim[0]] = f'phase_{bodyPhase}{filePrefix}{anim[1]}'

        for anim in AllSuitsMinigame:
            animDict[anim[0]] = f'phase_4{filePrefix}{anim[1]}'

        for anim in AllSuitsTutorialBattle:
            filePrefix, bodyPhase = ModelDict[_body]
            animDict[anim[0]] = f'phase_{bodyPhase}{filePrefix}{anim[1]}'

        for anim in AllSuitsBattle:
            animDict[anim[0]] = f'phase_5{filePrefix}{anim[1]}'

        if _body == 'a':
            animDict['neutral'] = 'phase_4/models/char/suitA-neutral'
            for anim in SuitsCEOBattle:
                animDict[anim[0]] = f'phase_12/models/char/suitA-{anim[1]}'

        elif _body == 'b':
            animDict['neutral'] = 'phase_4/models/char/suitB-neutral'
            for anim in SuitsCEOBattle:
                animDict[anim[0]] = f'phase_12/models/char/suitB-{anim[1]}'

        elif _body == 'c':
            animDict['neutral'] = 'phase_3.5/models/char/suitC-neutral'
            for anim in SuitsCEOBattle:
                animDict[anim[0]] = f'phase_12/models/char/suitC-{anim[1]}'

        try:
            animList = tuple(list(SuitBattleAnims['all']) + list(SuitBattleAnims[_body]))
        except KeyError:
            animList = ()

        for anim in animList:
            phase = f'phase_{anim[2]}'
            animDict[anim[0]] = f'{phase}{filePrefix}{anim[1]}'

        return animDict

    def initializeBodyCollisions(self, collIdStr):
        Avatar.Avatar.initializeBodyCollisions(self, collIdStr)
        if not self.ghostMode:
            self.collNode.setCollideMask(self.collNode.getIntoCollideMask() | ToontownGlobals.PieBitmask)

    def setSuitClothes(self, modelRoot = None, deathSuit: bool = False):
        if not modelRoot:
            modelRoot = self

        torsoTex = DataPackManager.getTexture(self.appearance[CogAppearanceIndex.TORSO_TEX])
        legTex = DataPackManager.getTexture(self.appearance[CogAppearanceIndex.LEG_TEX])
        armTex = DataPackManager.getTexture(self.appearance[CogAppearanceIndex.ARM_TEX])

        wristTexPath = self.appearance[CogAppearanceIndex.WRIST_TEX]
        if wristTexPath != '':
            wristTex = DataPackManager.getTexture(wristTexPath)
        shoeTexPath = self.appearance[CogAppearanceIndex.SHOE_TEX]
        if shoeTexPath != '':
            shoeTex = DataPackManager.getTexture(self.appearance[CogAppearanceIndex.SHOE_TEX])
        handTexPath = self.appearance[CogAppearanceIndex.HAND_TEX]
        if handTexPath != '':
            handTex = DataPackManager.getTexture(self.appearance[CogAppearanceIndex.HAND_TEX])

        torsoTex.setMinfilter(Texture.FTLinearMipmapLinear)
        legTex.setMinfilter(Texture.FTLinearMipmapLinear)
        armTex.setMinfilter(Texture.FTLinearMipmapLinear)
        modelRoot.find('**/torso').setTexture(torsoTex, 1)
        modelRoot.find('**/arms').setTexture(armTex, 1)
        modelRoot.find('**/legs').setTexture(legTex, 1)
        if handTexPath != '':
            handTex.setMinfilter(Texture.FTLinearMipmapLinear)
            modelRoot.find('**/hands').setTexture(handTex, 1)
        modelRoot.find('**/hands').setColor(self.appearance[CogAppearanceIndex.HAND_COLOR])
        if wristTexPath != '':
            wristTex.setMinfilter(Texture.FTLinearMipmapLinear)
            if self.appearance[CogAppearanceIndex.BODY_TYPE] == 2:
                if deathSuit:
                    modelRoot.find('**/sleeve').setTexture(wristTex, 1)
                else:
                    modelRoot.find('**/').setTexture(wristTex, 1)
            else:
                modelRoot.find('**/sleeves').setTexture(wristTex, 1)
        if shoeTexPath != '':
            shoeTex.setMinfilter(Texture.FTLinearMipmapLinear)
            modelRoot.find('**/shoes').setTexture(shoeTex, 1)
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')

    def generateHeads(self):
        for head in self.appearance[CogAppearanceIndex.HEAD]:
            path, node, texture, pos, hpr, scale, colorScale, removeNodes = head

            if node == '':
                node = None

            _headModel = DataPackManager.getModelNode(path, node)
            if self.appearance[CogAppearanceIndex.BODY_TYPE] == 0:
                headPart = self.instance(_headModel, 'modelRoot', 'to_head')
            else:
                headPart = self.instance(_headModel, 'modelRoot', 'joint_head')
            if texture != '':
                headTex = DataPackManager.getTexture(texture)
                headTex.setMinfilter(Texture.FTLinearMipmapLinear)
                headPart.setTexture(headTex, 1)

            for node in removeNodes:
                _np = headPart.find(f'**/{node}')
                if not _np.isEmpty():
                    _np.removeNode()

            headPart.setPosHprScale(*pos, *hpr, *scale)
            headPart.setColorScale(colorScale)

            self.headParts.append(headPart)

            _headModel.removeNode()

    def generateCorporateTie(self, modelPath = None):
        if not modelPath:
            modelPath = self
        dept = self.style.dept
        tie = modelPath.find('**/tie')
        if tie.isEmpty():
            self.notify.warning('Skelecog has no tie model!')
            return
        if dept == 'c':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_boss.png')
        elif dept == 's':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_sales.png')
        elif dept == 'l':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_legal.png')
        elif dept == 'm':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_money.png')
        tieTex.setMinfilter(Texture.FTLinearMipmapLinear)
        tieTex.setMagfilter(Texture.FTLinear)
        tie.setTexture(tieTex, 1)

    def generateCorporateMedallion(self):
        if hasattr(self, 'doId') and self.zoneId is not None and ZoneUtil.isBetaPlaygroundZone(self.zoneId):
            pass
        else:
            chestNull = self.find('**/joint_attachMeter')
            # Remove a corporate medallion if it exists
            if chestNull.getNumChildren() >= 2:
                medallion = chestNull.getChild(1)
                if medallion and not medallion.isEmpty():
                    medallion.removeNode()
            self.corpMedallion = self.getCorporateMedallionIcon().copyTo(chestNull)
            self.corpMedallion.setPosHprScale(0.02, 0.05, 0.04, 180.0, 0.0, 0.0, 0.51, 0.51, 0.51)
            if self.appearance[CogAppearanceIndex.MEDALLION_COLOR] == (-1, -1, -1, -1):
                self.corpMedallion.setColor(self.medallionColors[self.style.dept])
            else:
                self.corpMedallion.setColor(Vec4(self.appearance[CogAppearanceIndex.MEDALLION_COLOR]))

    def getCorporateMedallionIcon(self):
        icons = loader.loadModel('phase_3/models/gui/cog_icons')
        dept = self.style.dept
        iconDict = {
            'c': 'Corp',
            's': 'Sales',
            'l': 'Legal',
            'm': 'Money'
        }
        if dept in iconDict:
            icon = icons.find(f'**/{iconDict.get(dept)}Icon')
        else:
            self.notify.error(f'getCorporateMedallionIcon(): Invalid suit dept {dept}')
        icons.removeNode()
        return icon

    def showCorpMedallion(self):
        if self.corpMedallion and not self.corpMedallion.isEmpty():
            self.corpMedallion.show()

    def hideCorpMedallion(self):
        if self.corpMedallion and not self.corpMedallion.isEmpty():
            self.corpMedallion.hide()

    def generateHealthBar(self):
        self.removeHealthBar()

        def generateRegularHealthBar():
            model = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
            button = model.find('**/minnieCircle')
            button.setScale(3.0)
            button.setH(180.0)
            if hasattr(self, 'doId') and self.currHP > self.maxHP:
                condition = 5
            else:
                condition = 0
            button.setColor(self.healthColors[condition])
            chestNull = self.find('**/joint_attachMeter')
            button.reparentTo(chestNull)
            self.healthBar = button
            glow = BattleProps.globalPropPool.getProp('glow')
            glow.reparentTo(self.healthBar)
            glow.setScale(0.28)
            glow.setPos(-0.005, 0.01, 0.015)
            glow.setColor(self.healthGlowColors[condition])
            button.flattenLight()
            self.healthBarGlow = glow
            self.healthCondition = condition

        if hasattr(self, 'doId'):
            if self.zoneId is not None and ZoneUtil.isBetaPlaygroundZone(self.zoneId):
                self.healthBar = DirectWaitBar(parent=self.nametag.getNameIcon(), relief=DirectGuiGlobals.FLAT,
                                               barColor=(0.1537, 0.0078, 0, 1), barRelief=DirectGuiGlobals.RAISED,
                                               pos=(0, 0, 2), frameSize=(-2, 2, -0.24, 0.24))
            else:
                generateRegularHealthBar()
        else:
            generateRegularHealthBar()
            self.healthCondition = 0
        self.healthBar.hide()

    def reseatHealthBarForSkele(self):
        if not isinstance(self.healthBar, DirectWaitBar):
            self.healthBar.setPos(0.0, 0.1, 0.0)

    def updateHealthBar(self, dmg = 0, subtractHp = True):
        if subtractHp:
            if dmg > self.currHP:
                dmg = self.currHP
            self.currHP -= dmg
        health = float(self.currHP) / float(self.maxHP)
        if health > 1:
            condition = 5
        elif health > 0.95:
            condition = 0
        elif health > 0.7:
            condition = 1
        elif health > 0.3:
            condition = 2
        elif health > 0.05:
            condition = 3
        elif health > 0.0:
            condition = 4
        else:
            condition = 6
        if not isinstance(self.healthBar, DirectWaitBar):
            if self.healthCondition != condition:
                if condition == 4:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 6:
                    if self.healthCondition == 4:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.healthBar.setColor(self.healthColors[condition], 1)
                    self.healthBarGlow.setColor(self.healthGlowColors[condition], 1)
                    if self.isVirtual:
                        self.setVirtualHealthColor(condition)
                    taskMgr.remove(self.uniqueName('blink-task'))
        else:
            self.healthBar.update(self.currHP)
        self.healthCondition = condition

    def uniqueName(self, name):
        return f'{name}-{id(self)}'

    def setVirtualHealthColor(self, condition: int):
        if self.appearance[CogAppearanceIndex.VIRTUAL_COLOR_SCALE] != (-1, -1, -1, -1):
            return
        actorNode = self.find('**/__Actor_modelRoot')
        if actorNode.isEmpty():
            return
        actorCollection = actorNode.findAllMatches('*')
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag'):
                thing.setColorScale(self.healthColors[condition])

        self.healthBar.setDepthWrite(False)
        self.healthBarGlow.setDepthWrite(False)

    def __blinkRed(self, task):
        self.healthBar.setColor(self.healthColors[3], 1)
        self.healthBarGlow.setColor(self.healthGlowColors[3], 1)
        if self.isVirtual:
            self.setVirtualHealthColor(3)
        if self.healthCondition == 6:
            self.healthBar.setScale(1.17)
        return Task.done

    def __blinkGray(self, task):
        if not self.healthBar:
            return
        self.healthBar.setColor(self.healthColors[4], 1)
        self.healthBarGlow.setColor(self.healthGlowColors[4], 1)
        if self.isVirtual:
            self.setVirtualHealthColor(4)
        if self.healthCondition == 6:
            self.healthBar.setScale(1.0)
        return Task.done

    def removeHealthBar(self):
        if self.healthBar:
            if isinstance(self.healthBar, DirectWaitBar):
                self.healthBar.destroy()
            else:
                self.healthBar.removeNode()
            self.healthBar = None
        if self.healthCondition == 4 or self.healthCondition == 6:
            taskMgr.remove(self.uniqueName('blink-task'))
        self.healthCondition = 0

    def getLoseActor(self):
        if self.loseActor is None:
            if self.isSkeleton:
                body = self.getBodyType()
                loseModel = f'phase_5/models/char/cog{body.upper()}_robot-lose-mod'
                filePrefix, phase = ModelDict[body]
                loseAnim = f'phase_{phase}{filePrefix}lose'
                self.loseActor = Actor.Actor(loseModel, {'lose': loseAnim})
                self.generateCorporateTie(self.loseActor)
                self.loseActor.getGeomNode().setColorScale(VBase4(self.appearance[CogAppearanceIndex.SKELETON_COLOR_SCALE]))
            else:
                filePrefix, phase = ModelDict[self.getBodyType()]
                loseModel = f'phase_{phase}{filePrefix}lose-mod'
                loseAnim = f'phase_{phase}{filePrefix}lose'
                self.loseActor = Actor.Actor(loseModel, {'lose': loseAnim})
                self.loseActor.getGeomNode().setColorScale(VBase4(self.appearance[CogAppearanceIndex.NORMAL_COLOR_SCALE]))
                loseNeck = self.loseActor.find('**/joint_head')
                for part in self.headParts:
                    part.instanceTo(loseNeck)

                if self.isWaiter:
                    self.makeWaiter(self.loseActor)
                elif self.isRental:
                    self.makeRentalSuit(self.style.dept, self.loseActor)
                else:
                    self.setSuitClothes(self.loseActor, True)

        if self.isVirtual:
            actorNode = self.loseActor.find('**/__Actor_modelRoot')
            actorCollection = actorNode.findAllMatches('*')
            for thingIndex in range(0, actorCollection.getNumPaths()):
                thing = actorCollection[thingIndex]
                if thing.getName() not in ('joint_attachMeter', 'joint_nameTag'):
                    thing.setColorScale(1.0, 0.0, 0.0, 1.0)
                    thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                    thing.setDepthWrite(False)
                    thing.setBin('fixed', 1)
            self.loseActor.find('**/joint_shadow').hide()

        self.loseActor.setScale(self.scale)
        self.loseActor.setPos(self.getPos())
        self.loseActor.setHpr(self.getHpr())

        shadowJoint = self.loseActor.find('**/joint_shadow')
        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(shadowJoint)

        self.loseActor.setBlend(frameBlend=ClientSettings.SmoothAnimations.get())
        self.setLODAnimation(750, 20, 0.4)
        return self.loseActor

    def cleanupLoseActor(self):
        self.notify.debug('cleanupLoseActor()')
        if self.loseActor != None:
            self.notify.debug('cleanupLoseActor() - got one')
            self.loseActor.delete()
        self.loseActor = None

    def makeSkeleton(self):
        model = f'phase_5/models/char/cog{"ABC"[self.appearance[CogAppearanceIndex.BODY_TYPE]]}_robot-zero'
        anims = self.generateAnimDict()
        anim = self.getCurrentAnim()
        self.removePart('modelRoot')
        self.loadModel(model)
        self.loadAnims(anims)
        self.getGeomNode().setScale(self.scale * 1.0173)
        self.generateHealthBar()
        self.generateCorporateMedallion()
        self.generateCorporateTie()
        self.setHeight(self.height)
        parts = self.findAllMatches('**/pPlane*')
        for partNum in range(0, parts.getNumPaths()):
            bb = parts.getPath(partNum)
            bb.setTwoSided(1)
        self.setName(TTLocalizer.Skeleton)
        if hasattr(self, 'dna') and self.dna:
            nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': self._name,
                                                            'dept': self.getStyleDept(),
                                                            'level': self.getActualLevel()}
            self.setDisplayName(nameInfo)
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagNull = self.find('**/joint_nameTag')
        self.loop(anim)
        self.isSkeleton = 1
        self.getGeomNode().setColorScale(VBase4(self.appearance[CogAppearanceIndex.SKELETON_COLOR_SCALE]))
        self.setBlend(frameBlend=ClientSettings.SmoothAnimations.get())
        self.setLODAnimation(750, 20, 0.4)

    def makeVirtual(self):
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag'):
                if self.appearance[CogAppearanceIndex.VIRTUAL_COLOR_SCALE] != (-1, -1, -1, -1):
                    thing.setColorScale(VBase4(self.appearance[CogAppearanceIndex.VIRTUAL_COLOR_SCALE]))
                else:
                    thing.setColorScale(self.healthColors[0])
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)
        self.healthBar.setDepthWrite(False)
        self.healthBarGlow.setDepthWrite(False)
        self.find('**/joint_shadow').hide()
        self.isVirtual = True

    def getVirtual(self):
        return self.isVirtual

    def makeWaiter(self, modelRoot = None):
        if not modelRoot:
            modelRoot = self.getGeomNode()
        torso = modelRoot.find('**/torso')
        if torso.isEmpty():
            return
        arms = modelRoot.find('**/arms')
        legs = modelRoot.find('**/legs')
        hands = modelRoot.find('**/hands')
        self.isWaiter = 1
        dept = self.style.dept
        torsoTex = loader.loadTexture(f'phase_3.5/maps/waiter_{dept}_blazer.png')
        torsoTex.setMinfilter(Texture.FTLinearMipmapLinear)
        torsoTex.setMagfilter(Texture.FTLinear)
        legTex = loader.loadTexture('phase_3.5/maps/waiter_leg.png')
        legTex.setMinfilter(Texture.FTLinearMipmapLinear)
        legTex.setMagfilter(Texture.FTLinear)
        armTex = loader.loadTexture('phase_3.5/maps/waiter_sleeve.png')
        armTex.setMinfilter(Texture.FTLinearMipmapLinear)
        armTex.setMagfilter(Texture.FTLinear)
        torso.setTexture(torsoTex, 1)
        arms.setTexture(armTex, 1)
        legs.setTexture(legTex, 1)
        hands.setColor(self.handColor)

    def makeRentalSuit(self, suitType, modelRoot = None):
        if not modelRoot:
            modelRoot = self.getGeomNode()
        dept = ToontownGlobals.Dept2Dept.get(suitType).lower()
        if dept:
            torsoTex = loader.loadTexture(f'phase_3.5/maps/tt_t_ene_{dept}Rental_blazer.png')
            legTex = loader.loadTexture(f'phase_3.5/maps/tt_t_ene_{dept}Rental_leg.png')
            armTex = loader.loadTexture(f'phase_3.5/maps/tt_t_ene_{dept}Rental_sleeve.png')
            handTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_Rental_hand.png')
        else:
            self.notify.warning(f'No rental suit for cog type {suitType}')
            return
        self.isRental = 1
        modelRoot.find('**/torso').setTexture(torsoTex, 1)
        modelRoot.find('**/arms').setTexture(armTex, 1)
        modelRoot.find('**/legs').setTexture(legTex, 1)
        modelRoot.find('**/hands').setTexture(handTex, 1)

    def makeSkeleRevive(self):
        self.isSkeleRevive = 1

    def getHeadParts(self):
        return self.headParts

    def getRightHand(self):
        return self.rightHand

    def getLeftHand(self):
        return self.leftHand

    def getShadowJoint(self):
        return self.shadowJoint

    def getNametagJoints(self):
        return []

    def getDialogueArray(self):
        if self.isSkeleton:
            loadSkelDialog()
            return SkelSuitDialogArray
        else:
            return SuitDialogArray

    def getTTSDarwinVoice(self):
        return ToontownGlobals.DefaultVoiceSuit

    def getStyleDept(self):
        if hasattr(self, 'dna') and self.dna:
            return SuitDNA.getDeptFullname(self.dna.dept)
        else:
            self.notify.error('called getStyleDept() before dna was set!')
            return 'unknown'

    def getActualLevel(self):
        if hasattr(self, 'dna'):
            if hasattr(self, 'level'):
                return self.level + 1
            return 1
        else:
            self.notify.warning('called getActualLevel with no DNA, returning 1 for level')
            return 1

    def getStyleName(self):
        if hasattr(self, 'dna') and self.dna:
            return self.dna.name
        else:
            self.notify.error('called getStyleName() before dna was set!')
            return 'unknown'

    def attachPropeller(self):
        if self.prop is None:
            self.prop = BattleProps.globalPropPool.getProp('propeller')
        if self.propInSound is None:
            self.propInSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg')
        if self.propOutSound is None:
            self.propOutSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_out.ogg')
        if self.appearance[CogAppearanceIndex.BODY_TYPE] == 0:
            head = self.find('**/to_head')
        else:
            head = self.find('**/joint_head')
        self.prop.reparentTo(head)

    def detachPropeller(self):
        if self.prop:
            self.prop.cleanup()
            self.prop.removeNode()
            self.prop = None
        if self.propInSound:
            self.propInSound = None
        if self.propOutSound:
            self.propOutSound = None

    def beginSupaFlyMove(self, pos, moveIn, trackName, detachPropeller=True):
        def detachFunc():
            if detachPropeller:
                self.detachPropeller()

        skyPos = Point3(pos)
        if moveIn:
            skyPos.setZ(pos.getZ() + SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)
        else:
            skyPos.setZ(pos.getZ() + SuitTimings.toSky * ToontownGlobals.SuitWalkSpeed)
        groundF = 28
        dur = self.getDuration('landing')
        fr = self.getFrameRate('landing')
        animTimeInAir = groundF / fr
        impactLength = dur - animTimeInAir
        timeTillLanding = SuitTimings.fromSky - impactLength
        waitTime = timeTillLanding - animTimeInAir
        if self.prop is None:
            self.prop = BattleProps.globalPropPool.getProp('propeller')
            self.prop.setPlayRate(1.5, 'propeller')
        propDur = self.prop.getDuration('propeller')
        lastSpinFrame = 8
        fr = self.prop.getFrameRate('propeller')
        spinTime = lastSpinFrame / fr
        openTime = (lastSpinFrame + 1) / fr
        if moveIn:
            shadowScale = self.dropShadow.getScale()

            lerpPosTrack = Sequence(
                self.posInterval(timeTillLanding, pos, startPos=skyPos), 
                Wait(impactLength)
                )

            shadowTrack = Sequence(
                Func(self.dropShadow.reparentTo, render), 
                Func(self.dropShadow.setPos, pos), 
                self.dropShadow.scaleInterval(timeTillLanding, 
                                              self.scale, 
                                              startScale=Vec3(0.01, 0.01, 1.0)), 
                Func(self.dropShadow.reparentTo, self.getShadowJoint()), 
                Func(self.dropShadow.setPos, 0, 0, 0), 
                Func(self.dropShadow.setScale, shadowScale)
                )

            fadeInTrack = Sequence(
                Func(self.setTransparency, 1), 
                self.colorScaleInterval(1, 
                                        colorScale=VBase4(1, 1, 1, 1), 
                                        startColorScale=VBase4(1, 1, 1, 0)), 
                Func(self.clearColorScale), 
                Func(self.clearTransparency)
                )

            animTrack = Sequence(
                Func(self.pose, 'landing', 0), 
                Wait(waitTime), 
                ActorInterval(self, 'landing', duration=dur), 
                Func(self.loop, 'walk')
                )
            self.attachPropeller()

            propTrack = Parallel(
                SoundInterval(self.propInSound, 
                              duration=waitTime + dur, 
                              node=self), 
                Sequence(
                    Func(self.prop.loop, 'propeller', fromFrame=5, toFrame=10),
                    Wait(waitTime),
                    ActorInterval(self.prop, 
                                  'propeller', 
                                  duration=propDur - openTime, 
                                  startTime=openTime), 
                    Func(detachFunc)
                    )
                )
            return Parallel(lerpPosTrack, 
                            shadowTrack, 
                            fadeInTrack, 
                            animTrack, 
                            propTrack, 
                            name=trackName
                            )
        else:
            lerpPosTrack = Sequence(
                Wait(impactLength), 
                LerpPosInterval(self, timeTillLanding, skyPos, startPos=pos)
                )

            shadowTrack = Sequence(
                Func(self.dropShadow.reparentTo, render), 
                Func(self.dropShadow.setPos, pos), 
                self.dropShadow.scaleInterval(timeTillLanding, 
                                              Vec3(0.01, 0.01, 1.0), 
                                              startScale=self.scale), 
                Func(self.dropShadow.reparentTo, self.getShadowJoint()), 
                Func(self.dropShadow.setPos, 0, 0, 0)
                )

            fadeOutTrack = Sequence(
                Func(self.setTransparency, 1), 
                self.colorScaleInterval(1, 
                                        colorScale=VBase4(1, 1, 1, 0), 
                                        startColorScale=VBase4(1, 1, 1, 1)), 
                Func(self.clearColorScale), 
                Func(self.clearTransparency), 
                Func(self.reparentTo, hidden)
                )
            actInt = ActorInterval(self, 'landing', loop=0, startTime=dur, endTime=0.0)
            self.attachPropeller()
            self.prop.hide()
            propTrack = Parallel(
                SoundInterval(self.propOutSound, 
                              duration=waitTime + dur, 
                              node=self), 
                Sequence(
                    Func(self.prop.show), 
                    ActorInterval(self.prop, 
                                  'propeller', 
                                  startFrame=88, 
                                  endFrame=5,
                                  playRate=1.5),
                    Func(self.prop.loop, 'propeller', fromFrame=5, toFrame=10),
                    Wait(4.1),
                    Func(detachFunc)
                    )
                )
            return Parallel(
                ParallelEndTogether(
                    lerpPosTrack, 
                    shadowTrack, 
                    fadeOutTrack
                    ), 
                actInt, 
                propTrack, 
                name=trackName
                )

    def enableBattleDetect(self, name, handler, *args):
        if self.collTube:
            self.battleDetectName = name
            self.collNode = CollisionNode(self.battleDetectName)
            self.collNode.addSolid(self.collTube)
            self.collNodePath = self.attachNewNode(self.collNode)
            self.collNode.setCollideMask(ToontownGlobals.WallBitmask)
            self.accept(f'enter{self.battleDetectName}', handler, extraArgs=[args])
        return Task.done

    def disableBattleDetect(self):
        if self.battleDetectName:
            self.ignore(f'enter{self.battleDetectName}')
            self.battleDetectName = None
        if hasattr(self, 'collNodePath'):
            if self.collNodePath:
                self.collNodePath.removeNode()
                self.collNodePath = None

    def showHpText(self, number, bonus = 0, scale = 1, attackTrack = -1):
        if number != 0:
            if self.hpText:
                self.hideHpText()
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            if number < 0:
                self.HpTextGenerator.setText(str(number))
                if base.cr.newsManager.isHolidayRunning(ToontownGlobals.SILLY_SURGE_HOLIDAY):
                    self.sillySurgeText = True
                    absNum = abs(number)
                    if 0 < absNum <= 10:
                        self.HpTextGenerator.setText(f'{number}\n{TTLocalizer.SillySurgeTerms[1]}')
                    elif 10 < absNum <= 20:
                        self.HpTextGenerator.setText(f'{number}\n{TTLocalizer.SillySurgeTerms[2]}')
                    elif 20 < absNum <= 30:
                        self.HpTextGenerator.setText(f'{number}\n{TTLocalizer.SillySurgeTerms[3]}')
                    elif 30 < absNum <= 40:
                        self.HpTextGenerator.setText(f'{number}\n{TTLocalizer.SillySurgeTerms[4]}')
                    elif 40 < absNum <= 50:
                        self.HpTextGenerator.setText(f'{number}\n{TTLocalizer.SillySurgeTerms[5]}')
                    elif 50 < absNum <= 60:
                        self.HpTextGenerator.setText(f'{number}\n{TTLocalizer.SillySurgeTerms[6]}')
                    elif 60 < absNum <= 70:
                        self.HpTextGenerator.setText(f'{number}\n{TTLocalizer.SillySurgeTerms[7]}')
                    elif 70 < absNum <= 80:
                        self.HpTextGenerator.setText(f'{number}\n{TTLocalizer.SillySurgeTerms[8]}')
                    elif 80 < absNum <= 90:
                        self.HpTextGenerator.setText(f'{number}\n{TTLocalizer.SillySurgeTerms[9]}')
                    elif 90 < absNum <= 100:
                        self.HpTextGenerator.setText(f'{number}\n{TTLocalizer.SillySurgeTerms[10]}')
                    elif 100 < absNum <= 110:
                        self.HpTextGenerator.setText(f'{number}\n{TTLocalizer.SillySurgeTerms[11]}')
                    else:
                        self.HpTextGenerator.setText(f'{number}\n{TTLocalizer.SillySurgeTerms[12]}')
                if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                    self.sillySurgeText = True
                    if attackTrack in TTLocalizer.InteractivePropTrackBonusTerms:
                        self.HpTextGenerator.setText(f'{number}\n{TTLocalizer.InteractivePropTrackBonusTerms[attackTrack]}')
            else:
                self.HpTextGenerator.setText(f'+{number}')
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            if bonus == 1:
                r = 1.0
                g = 1.0
                b = 0
                a = 1
            elif bonus == 2:
                r = 1.0
                g = 0.5
                b = 0
                a = 1
            elif number < 0:
                r = 0.9
                g = 0
                b = 0
                a = 1
                if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                    r = 0
                    g = 0
                    b = 1
                    a = 1
            else:
                r = 0
                g = 0.9
                b = 0
                a = 1
            self.HpTextGenerator.setTextColor(r, g, b, a)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)
            if self.sillySurgeText:
                self.nametag3d.setDepthTest(0)
                self.nametag3d.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextSeq = Sequence(
                    self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType = 'easeOut'),
                    Wait(0.85),
                    self.hpText.colorScaleInterval(0.1, Vec4(r, g, b, 0)),
                    Func(self.hideHpText))
            self.hpTextSeq.start()

    def hideHpText(self):
        if self.hpText:
            self.hpText.removeNode()
            self.hpText = None
            if self.hpTextSeq:
                self.hpTextSeq.finish()
                self.hpTextSeq = None

        if self.sillySurgeText:
            self.nametag3d.clearDepthTest()
            self.nametag3d.clearBin()
            self.sillySurgeText = False

    def cleanupParticleEffect(self):
        if self.particleEffect:
            global ParticleRefCount
            if self.particleEffect.isEnabled():
                ParticleRefCount -= 1
            global ParticleList
            if self.particleEffect in ParticleList:
                ParticleList.remove(self.particleEffect)
            self.particleEffect.cleanup()
            if ParticleRefCount and ParticleRefCount < ParticleThreshold:
                try:
                    particle = ParticleList[-1]
                    if not particle.isEnabled():
                        particle.enable()
                        ParticleRefCount += 1
                except IndexError:
                    pass
