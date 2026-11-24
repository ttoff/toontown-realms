import math

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui import DirectGuiGlobals
from direct.gui.DirectGui import *

from panda3d.core import *

from otp.otpgui import OTPGUIUtils
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.toontowngui import TTDialog, HelpButton

from .DistributedMicroGame import DistributedMicroGame
from ..instancedgames.InstancedGamesGUI import ToonPortrait
from ..toontowngui.AnimatedButton import AnimatedButton
from ..toontowngui.ToontownScrolledGridFrame import ToontownScrolledGridFrame

CategoryToTitle = {
    ToontownGlobals.BossPartyCategoryMinigames: TTLocalizer.BossPartyCategoryMinigames,
    ToontownGlobals.BossPartyCategorySellbot: TTLocalizer.ACogVP,
    ToontownGlobals.BossPartyCategoryCashbot: TTLocalizer.ACogCFO,
    ToontownGlobals.BossPartyCategoryLawbot: TTLocalizer.ACogCJ,
    ToontownGlobals.BossPartyCategoryBossbot: TTLocalizer.ACogCEO
}

GameToIconPath = {
    ToontownGlobals.BossPartySellbotBoss: 'VP_NORMAL',
    ToontownGlobals.BossPartySellbotBossStormSellbot: 'VP_NORMAL',
    ToontownGlobals.BossPartySellbotBossHardcore: 'VP_HARDCORE',
    ToontownGlobals.BossPartySellbotBossArena: 'VP_ARENA',
    ToontownGlobals.BossPartySellbotBossWinter: 'VP_WINTER',

    ToontownGlobals.BossPartyCashbotBoss: 'CFO_NORMAL',
    ToontownGlobals.BossPartyCashbotBossHardcore: 'CFO_HARDCORE',

    ToontownGlobals.BossPartyLawbotBoss: 'CJ_NORMAL',
    ToontownGlobals.BossPartyLawbotBossHardcore: 'CJ_HARDCORE',
    ToontownGlobals.BossPartyLawbotBossArena: 'CJ_ARENA',

    ToontownGlobals.BossPartyBossbotBoss: 'CEO_NORMAL',
    ToontownGlobals.BossPartyBossbotBossHardcore: 'CEO_HARDCORE',

    #ToontownGlobals.BossPartyPropHunt: 'MG_PROPHUNT'
}

# TODO: CLEANUP
#   - Move these constant variables below up to above here

# TODO:
#   - handle case where a toon dies through a toon-down unite while in the interface.

class BossPartyManager(DistributedMicroGame):
    notify = directNotify.newCategory('BossPartyManager')
    defaultTransitions = {'Off': ['Planning', 'Start'],
                          'Planning': ['Off', 'Start'],
                          'Start': ['Done', 'Off'],
                          'Done': ['Off']
                          }
    neverDisable = 1
    bossCogs = {ToontownGlobals.BossPartySellbotBoss: TTLocalizer.ACogVP,
                ToontownGlobals.BossPartyCashbotBoss: TTLocalizer.ACogCFO,
                ToontownGlobals.BossPartyLawbotBoss: TTLocalizer.ACogCJ,
                ToontownGlobals.BossPartyBossbotBoss: TTLocalizer.ACogCEO
                }
    bossCogSubcategories = {ToontownGlobals.BossPartySellbotBossHardcore: TTLocalizer.BossPartyHardcore,
                            ToontownGlobals.BossPartySellbotBossStormSellbot: TTLocalizer.BossPartyStormSellbot,
                            ToontownGlobals.BossPartySellbotBossWinter: TTLocalizer.BossPartyWinter,
                            ToontownGlobals.BossPartySellbotBossArena: TTLocalizer.BossPartySellbotArena,
                            ToontownGlobals.BossPartyCashbotBossHardcore: TTLocalizer.BossPartyHardcore,
                            ToontownGlobals.BossPartyLawbotBossHardcore: TTLocalizer.BossPartyHardcore,
                            ToontownGlobals.BossPartyLawbotBossArena: TTLocalizer.BossPartyLawbotArena,
                            ToontownGlobals.BossPartyBossbotBossHardcore: TTLocalizer.BossPartyHardcore
                            }
    bossPartyNoPromoCheck = (
        ToontownGlobals.BossPartySellbotBossStormSellbot, ToontownGlobals.BossPartySellbotBossArena,
        ToontownGlobals.BossPartyLawbotBossArena, ToontownGlobals.BossPartyPropHunt)
    bossPartyComingSoon = ()

    bossPartyModeToName = {
        ToontownGlobals.BossPartyPropHunt: TTLocalizer.BossPartyPropHunt,

        ToontownGlobals.BossPartySellbotBoss: TTLocalizer.BossPartySellbot,
        ToontownGlobals.BossPartySellbotBossHardcore: TTLocalizer.BossPartyHardcoreSellbot,
        ToontownGlobals.BossPartySellbotBossStormSellbot: TTLocalizer.BossPartyStormSellbot,
        ToontownGlobals.BossPartySellbotBossWinter: TTLocalizer.BossPartyWinter,
        ToontownGlobals.BossPartySellbotBossArena: TTLocalizer.BossPartySellbotArena,

        ToontownGlobals.BossPartyCashbotBoss: TTLocalizer.BossPartyCashbot,
        ToontownGlobals.BossPartyCashbotBossHardcore: TTLocalizer.BossPartyHardcoreCashbot,

        ToontownGlobals.BossPartyLawbotBoss: TTLocalizer.BossPartyLawbot,
        ToontownGlobals.BossPartyLawbotBossHardcore: TTLocalizer.BossPartyHardcoreLawbot,
        ToontownGlobals.BossPartyLawbotBossArena: TTLocalizer.BossPartyLawbotArena,

        ToontownGlobals.BossPartyBossbotBoss: TTLocalizer.BossPartyBossbot,
        ToontownGlobals.BossPartyBossbotBossHardcore: TTLocalizer.BossPartyHardcoreBossbot
    }

    BG_RATIO = OTPGUIUtils.getImageScale(1193, 646)
    LEFT_X = -0.4085 * BG_RATIO[0]
    RIGHT_X = 0.092 * BG_RATIO[0]

    USE_NEW_UI = True

    PartyMenuGUI = loader.loadModel('phase_3.5/models/gui/ttoff_m_gui_mgmn_bossParty')  # type: NodePath

    DISABLE_MINIGAMES_FOR_BETA = True

    if DISABLE_MINIGAMES_FOR_BETA:
        ActiveCategory = ToontownGlobals.BossPartyCategorySellbot
    else:
        ActiveCategory = ToontownGlobals.BossPartyCategoryMinigames

    def __init__(self, cr):
        DistributedMicroGame.__init__(self, cr)
        base.cr.bossPartyManager = self

        if BossPartyManager.USE_NEW_UI:
            self.plannerFrame = DirectFrame(
                    parent = aspect2dp,
                    relief = None,
                    image = self.PartyMenuGUI.find('**/partymenubg'),
                    image_scale = self.BG_RATIO,
                    scale = 1.4
            )
            self.plannerFrame.hide()

            self.plannerCategoryTitle = OnscreenText(
                    parent = self.plannerFrame,
                    text = '$plannerCategoryTitle',
                    align = TextNode.ACenter,
                    pos = (BossPartyManager.RIGHT_X, 0.45),
                    scale = 0.035
            )

            self.categoryButtons = {}

            def makeCategoryButton(data, num, *args):  # type: (dict, int, []) -> DirectButton
                category = list(ToontownGlobals.BossPartyCategories.keys())[num]
                images = {
                    ToontownGlobals.BossPartyCategoryMinigames: "MINIGAMES",
                    ToontownGlobals.BossPartyCategorySellbot: "VP_NORMAL",
                    ToontownGlobals.BossPartyCategoryCashbot: "CFO_NORMAL",
                    ToontownGlobals.BossPartyCategoryLawbot: "CJ_NORMAL",
                    ToontownGlobals.BossPartyCategoryBossbot: "CEO_NORMAL"
                }
                btn = AnimatedButton(
                        scale = 0.20,
                        image = self.PartyMenuGUI.find(f'**/{images[category]}'),
                        image3_color = (1.0, 1.0, 1.0, 0.5),
                        command = self.setCategory,
                        extraArgs = [category]
                )
                self.categoryButtons[category] = btn
                return btn

            gui = loader.loadModel('phase_3/models/gui/ttoff_m_gui_opts_buttons')  # type: NodePath
            self.plannerCategories = DirectScrolledList(
                    parent = self.plannerFrame,
                    relief = None,
                    forceHeight = 0.21,
                    numItemsVisible = 4,
                    # stupid hack bc it only accepts strings otherwise it has a stroke
                    items = ['x' for i in range(5)],
                    itemFrame_scale = 1,
                    itemFrame_pos = (0, 0, 0.314),
                    itemFrame_frameSize = (-.4, .4, -.4, .4),
                    pos = (BossPartyManager.LEFT_X, 0, 0),
                    itemFrame_relief = None,
                    itemMakeFunction = makeCategoryButton,
                    incButton_image = (
                        gui.find('**/arrow_l_normal'),
                        gui.find('**/arrow_l_click'),
                        gui.find('**/arrow_l_hover'),
                        gui.find('**/arrow_l_disabled')
                    ),
                    incButton_relief = None,
                    incButton_pressEffect = False,
                    incButton_pos = (0.0, 0.0, -.45),
                    incButton_scale = (0.05, 1, 0.1),
                    incButton_hpr = (0, 0, -90),
                    decButton_image = (
                        gui.find('**/arrow_r_normal'),
                        gui.find('**/arrow_r_click'),
                        gui.find('**/arrow_r_hover'),
                        gui.find('**/arrow_r_disabled')
                    ),
                    decButton_relief = None,
                    decButton_pressEffect = False,
                    decButton_pos = (0.0, 0.0, 0.45),
                    decButton_scale = (0.05, 1, 0.1),
                    decButton_hpr = (0, 0, -90),

            )

            self.plannerGameButtons = {}

            self.plannerGameBanner = OnscreenGeom(
                    parent = self.plannerFrame,
                    geom = BossPartyManager.PartyMenuGUI.find('**/UNKNOWN_BANNER'),
                    scale = (0.6, 1.0, 0.3),
                    pos = (BossPartyManager.RIGHT_X, 0, 0.1)
            )

            self.plannerGameTitle = OnscreenText(
                    parent = self.plannerFrame,
                    text = '$plannerGameTitle',
                    align = TextNode.ACenter,
                    pos = (BossPartyManager.RIGHT_X, -0.15),
                    scale = 0.065
            )

            self.plannerGameDescription = OnscreenText(
                    parent = self.plannerFrame,
                    text = '$plannerGameDescription',
                    align = TextNode.ACenter,
                    wordwrap = 50,
                    pos = (BossPartyManager.RIGHT_X, -0.2),
                    scale = 0.035
            )

            self.plannerGamePlayers = OnscreenText(
                    parent = self.plannerFrame,
                    text = '$plannerGamePlayers',
                    align = TextNode.ACenter,
                    pos = (BossPartyManager.RIGHT_X, -0.08),
                    scale = 0.02,
                    fg = (0.3, 0.3, 0.3, 0.8)
            )

            self.plannerCreateButton = AnimatedButton(
                    parent = self.plannerFrame,
                    image = (gui.find('**/button_green_up'),
                             gui.find('**/button_green_down'),
                             gui.find('**/button_green_rollover')),
                    image_scale = (.4, 1, .11),
                    text = TTLocalizer.BossPartyPlanningCreate,
                    text_scale = 0.055,
                    text_pos = (0.0, -0.015),
                    scale = 0.6,
                    pos = (BossPartyManager.RIGHT_X, 0, -0.42),
                    command = self.createLobby
            )

            self.plannerCloseButton = AnimatedButton(
                    parent = self.plannerFrame,
                    image = (
                        gui.find('**/close_button_normal'),
                        gui.find('**/close_button_click'),
                        gui.find('**/close_button_hover')),
                    scale = 0.08,
                    pos = (0.84, 0, 0.42),
                    command = self.closePlanner
            )

            self.setCategory(BossPartyManager.ActiveCategory)

        # Make the prompt interface
        self._prompt = DirectFrame(parent = aspect2d, relief = None,
                                   image = BossPartyManager.PartyMenuGUI.find('**/partymenulobbybg'),
                                   pos = (0.0, 0.0, 0.05), image_scale = OTPGUIUtils.getImageScale(978, 655, 1.4),
                                   image_pos = (0, 0, -0.05),
                                   image_color = ToontownGlobals.GlobalDialogColor,
                                   borderWidth = (0.01, 0.01), scale = 0.8)
        self._prompt.setBin('gui-popup', 0)
        self._prompt.hide()
        self._label = DirectLabel(parent = self._prompt, relief = None, pos = (0.0, 0.0, 0.55),
                                  text = TTLocalizer.ACogVP, text_scale = 0.1)
        self._label.hide()
        self._labelSubcategory = DirectLabel(parent = self._prompt, relief = None, pos = (0.0, 0.0, 0.25),
                                             text = TTLocalizer.BossPartyNormal, text_scale = 0.06)
        self._labelSubcategory.hide()
        self._notice = DirectLabel(parent = self._prompt, relief = None, pos = (0.0, 0.0, -0.4),
                                   text = TTLocalizer.BossPartyWait, text_scale = 0.06)
        count = TTLocalizer.BossPartyToonCount.format(0, 8)
        self._count = DirectLabel(parent = self._prompt, relief = None, pos = (0.0, 0.0, -0.5),
                                  text = count, text_scale = 0.06)
        self._toonsInParty: list[ToonPortrait] = []

        settingsScrollbarModel: NodePath = loader.loadModel('phase_3.5/models/gui/ttoff_m_gui_sbk_generic')
        self._toonsInPartyGrid = ToontownScrolledGridFrame(
                parent = self._prompt,
                relief = DirectGuiGlobals.RIDGE,
                borderWidth = (0.01, 0.01),
                frameColor = (0.95, 0.85, 0.65, .5),
                height = 0.4,
                width = 0.6,
                useItemBoundsForPadding = False,
                itemPadding = 0.2,
                itemsPerRow = 5,
                itemMargin = (-0.26, -0.25),
                pos = (0, 0, .12),
                scrollAmount = 1,
                manageScrollBars = False,
                verticalScroll_frameColor = (0, 0, 0, 0),
                verticalScroll_manageButtons = False,
                verticalScroll_thumb_geom = (
                    settingsScrollbarModel.find('**/scrollbar_normal'),
                    settingsScrollbarModel.find('**/scrollbar_press'),
                    settingsScrollbarModel.find('**/scrollbar_hover')),
                verticalScroll_thumb_geom_scale = OTPGUIUtils.getImageScale(151, 399, 0.125),
                verticalScroll_thumb_relief = None,
                verticalScroll_resizeThumb = False,
                verticalScroll_decButton_relief = None,
                verticalScroll_incButton_relief = None
        )
        settingsScrollbarModel.removeNode()
        model = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        bookModel = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
        okImageList = (model.find('**/ChtBx_OKBtn_UP'), model.find('**/ChtBx_OKBtn_DN'),
                       model.find('**/ChtBx_OKBtn_Rllvr'))
        cancelImageList = (model.find('**/CloseBtn_UP'), model.find('**/CloseBtn_DN'),
                           model.find('**/CloseBtn_Rllvr'))
        self._leave = DirectButton(parent = self._prompt, relief = None, image = (guiButton.find('**/QuitBtn_UP'),
                                                                                  guiButton.find('**/QuitBtn_DN'),
                                                                                  guiButton.find('**/QuitBtn_RLVR')),
                                   image_scale = (1.3, 1.1, 1.1), pos = (0.0, 0.0, -0.625),
                                   text = TTLocalizer.BossPartyLeaveButton, text_scale = TTLocalizer.MPsafeZoneButton,
                                   text_pos = (0, -0.02), textMayChange = 1, command = self.leave)
        self._leave.hide()
        self._ready = DirectButton(parent = self._prompt, relief = None, image = (guiButton.find('**/QuitBtn_UP'),
                                                                                  guiButton.find('**/QuitBtn_DN'),
                                                                                  guiButton.find('**/QuitBtn_RLVR')),
                                   image_scale = (1.3, 1.1, 1.1), image3_color = Vec4(0.5, 0.5, 0.5, 1),
                                   pos = (0.3, 0.0, -0.625),
                                   text = TTLocalizer.BossPartyGoNow, text_scale = TTLocalizer.MPsafeZoneButton,
                                   text_pos = (0, -0.02), textMayChange = 1, command = self.goNow)
        self._ready.hide()
        self._bossFrame = DirectFrame(parent = self._prompt, relief = None, pos = (0.0, 0.0, .2))
        model.removeNode()
        guiButton.removeNode()
        bookModel.removeNode()

        # Disband dialog
        self._dialog = None

        self._bossCog = ToontownGlobals.BossPartyPropHunt
        self._hoster = 0

    def getBossCog(self):
        return self._bossCog

    def setBossCog(self, bossCog):
        self._bossCog = bossCog

    def getHoster(self):
        return self._hoster

    def setHoster(self, hoster):
        self._hoster = hoster

    def setupRules(self, flag):
        pass

    def setCategory(self, category):
        #if category == ToontownGlobals.BossPartyCategoryMinigames:
        #    base.localAvatar.setSystemMessage(0, 'This feature is not available in this beta.')
        #    return

        for cat, button in self.categoryButtons.items():
            if cat == category:
                button['state'] = DirectGuiGlobals.DISABLED
            else:
                button['state'] = DirectGuiGlobals.NORMAL

        self.plannerCategoryTitle['text'] = CategoryToTitle.get(category, 'whoops')

        for btn in self.plannerGameButtons:
            self.plannerGameButtons[btn].destroy()

        self.plannerGameButtons = {}

        BossPartyManager.ActiveCategory = category
        
        numGames = len(ToontownGlobals.BossPartyCategories[category])
        start = BossPartyManager.RIGHT_X - (0.10 * (numGames - 1))

        for i, game in enumerate(ToontownGlobals.BossPartyCategories[category]):
            btn = AnimatedButton(
                    parent = self.plannerFrame,
                    scale = 0.18,
                    image = self.PartyMenuGUI.find(f'**/{GameToIconPath.get(game, "UNKNOWN")}'),
                    image3_color = (1.0, 1.0, 1.0, 0.5),
                    pos = (start + (0.20 * i), 0, 0.35),
                    command = self.setGame,
                    extraArgs = [game]
            )
            self.plannerGameButtons[game] = btn
            if i == 0:
                self.setGame(game)

        OTPGUIUtils.Animations.staggeredPopUp(list(self.plannerGameButtons.values()))

    def setGame(self, game):
        #if game == ToontownGlobals.BossPartySellbotBossArena:
        #    base.localAvatar.setSystemMessage(0, 'This feature is not available in this beta.')
        #    return
        # Somehow the game we select isnt in theactive category, lets switch to the right catgeory
        if game not in ToontownGlobals.BossPartyCategories[BossPartyManager.ActiveCategory]:
            for category, modes in ToontownGlobals.BossPartyCategories.items():
                if game in modes:
                    self.setCategory(category)
                    self.setGame(game)
                    return

        for mode, button in self.plannerGameButtons.items():
            if mode == game:
                button['state'] = DirectGuiGlobals.DISABLED
            else:
                button['state'] = DirectGuiGlobals.NORMAL

        self._bossCog = game

        self.plannerGameBanner['geom'] = BossPartyManager.PartyMenuGUI.find(
                f'**/{GameToIconPath.get(game, "UNKNOWN")}_BANNER')

        self.plannerGameTitle['text'] = self.bossPartyModeToName[self._bossCog]

        self.plannerGameDescription['text'] = TTLocalizer.BossPartyId2Description.get(self._bossCog,
                                                                                      '$plannerGameDescription')
        self.plannerGamePlayers['text'] = TTLocalizer.BossPartyPlanningLimit.format(self.getLimit())

    def enterPlanning(self):
        if BossPartyManager.USE_NEW_UI:
            self.plannerFrame.show()
            OTPGUIUtils.Animations.popup(self.plannerFrame, 1.4).start()

            self.setCategory(BossPartyManager.ActiveCategory)

        base.transitions.fadeScreen(0.5)

        if base.localAvatar.firstPerson:
            base.localAvatar.exitFirstPerson(0)

        self.accept('toon-caged', self.closePlanner)

    def exitPlanning(self):
        if BossPartyManager.USE_NEW_UI:
            self.plannerFrame.hide()

        self.ignore('toon-caged')

    def createLobby(self):
        self.hideAll()
        self.setState('Off')
        base.transitions.noTransitions()
        base.localAvatar.setLocked(False, ToontownGlobals.LockedStateMessengerExemption)
        self.sendUpdate('createBossParty', [self._bossCog])

    def closePlanner(self):
        self.hideAll()
        self.setState('Off')
        base.transitions.noTransitions()
        base.localAvatar.setLocked(False, ToontownGlobals.LockedStateMessengerExemption)

    def enterOff(self):
        # This state is transitioned to when the host leaves the game
        # so we need to cleanup the timer
        DistributedMicroGame.enterOff(self)
        if self._timer and not self._timer.isEmpty():
            self._timer.hide()
            self._timer.reset()

    def enterStart(self):
        DistributedMicroGame.enterStart(self)

        bossLabel = self.bossPartyModeToName[self._bossCog]
        subcategoryLabel = self.bossCogSubcategories.get(self._bossCog, TTLocalizer.BossPartyNormal)
        magicWordPrefix = base.cr.magicWordManager.getMagicWordPrefix()

        # If we are the hoster, don't change the display message or show buttons since we're already subscribed
        hoster = self.isHoster()
        if hoster:
            self._leave.setText(TTLocalizer.BossPartyDisbandButton)
            self._leave.setPos(-0.3, 0.0, -0.625)
            self._leave.show()
            self._ready.show()
        else:
            self._leave.setText(TTLocalizer.BossPartyLeaveButton)
            self._leave.setPos(0.0, 0.0, -0.625)
            self._leave.hide()
            self._ready.hide()

        self.generatePoster(bossLabel)

        # TODO: remove dynamic zone checks from boss parties
        # probably need to make sure we handle cases where a toon is forced to teleport out
        # and handle a case where you could start a party while in the vp transition scene, and then it goes into the second round while the party is still up
        if ZoneUtil.isDynamicZone(base.localAvatar.zoneId):
            self._timer.hide()
            body = TTLocalizer.NotificationBodyPartyFailDynamic.format(bossLabel)
            icon = self.PartyMenuGUI.find(f'**/{GameToIconPath.get(self._bossCog, "UNKNOWN")}').copyTo(hidden)
            base.localAvatar.sendNotification(
                title = TTLocalizer.NotificationTitlePartyFail,
                body = TTLocalizer.NotificationBodyPartyFailDynamic.format(bossLabel),
                icon = icon,
                id = "party_invite_failed"
            )
            return

        if hoster:
            place = base.cr.playGame.getPlace()
            if (place and place.fsm.getCurrentState().getName() != 'walk'):
                self._timer.hide()
                self.sendUpdate('requestLeave')
                return

        category = self.getBossPartyCategory(self._bossCog)
        if category != ToontownGlobals.BossPartyCategoryMinigames:
            # Make sure the Toon also has their promotion
            if not self.hasPromotion(base.localAvatar, self._bossCog):
                self._timer.hide()
                icon = self.PartyMenuGUI.find(f'**/{GameToIconPath.get(self._bossCog, "UNKNOWN")}').copyTo(hidden)
                base.localAvatar.sendNotification(
                    title = TTLocalizer.NotificationTitlePartyFail,
                    body = TTLocalizer.NotificationBodyPartyFail.format(bossLabel),
                    icon = icon,
                    id = "party_invite_failed"
                )
                return

        # Show the interface for the hoster
        if hoster:
            self._prompt.show()
            base.transitions.fadeScreen(0.5)
        else:
            self._timer.hide()
            icon = self.PartyMenuGUI.find(f'**/{GameToIconPath.get(self._bossCog, "UNKNOWN")}').copyTo(hidden)
            base.localAvatar.sendNotification(
                title = TTLocalizer.NotificationTitleParty,
                body = TTLocalizer.NotificationBodyParty.format(bossLabel),
                icon = icon,
                id = "party_invite",
                allowDuplicateIds = False,
                dismissButton2Text = TTLocalizer.NotificationDeny,
                dismissButton2Action = self.deny,
                button2Text = TTLocalizer.NotificationPartyJoin,
                button2Action = self.confirm
            )
        self.sendUpdate('gotInvite')

    def isHoster(self):
        hoster = base.localAvatar.getDoId() == self.getHoster()
        return hoster

    def confirm(self):
        # Show the prompt
        self._leave.show()
        self._timer.show()
        self._prompt.show()
        base.transitions.fadeScreen(0.5)

        # Tell the player to please wait
        self._notice.setText(TTLocalizer.BossPartyWait)

        # Send an update to the server requesting to join the party
        self.sendUpdate('joinParty')

    def deny(self):
        # Hide the interface if they deny
        self.hideAll()
        self._timer.hide()
        base.transitions.noTransitions()

        # Send an update to the server denying the request
        self.sendUpdate('denyParty')

    def leave(self):
        # Only allow an exit prompt if the interface is currently active, otherwise just cleanup without question
        if self.isActive():
            if self.isHoster():
                prompt = TTLocalizer.BossPartyDisbandPrompt
            else:
                prompt = TTLocalizer.BossPartyLeavePrompt

            self._dialog = TTDialog.TTDialog(style = TTDialog.TwoChoice, text = prompt,
                                             command = self.requestLeave)
            self._dialog.show()
            self._prompt.hide()
        else:
            self.hideAll()
            self.setState('Off')
            base.transitions.noTransitions()
            base.localAvatar.setLocked(False, ToontownGlobals.LockedStateMessengerExemption)

    def requestLeave(self, state):
        if self._dialog:
            self._dialog.destroy()
            self._dialog = None

        if state == 1:
            self.hideAll()
            self._timer.hide()
            self.sendUpdate('requestLeave')
        else:
            self._prompt.show()
            base.transitions.fadeScreen(0.5)

    def disbandParty(self, hosterAvId):
        # Clear up any previous dialogs, for example if someone was already in the process of leaving
        if self._dialog:
            self._dialog.destroy()
            self._dialog = None

        if base.localAvatar.getDoId() != hosterAvId:
            self.hideAll()
            self._dialog = TTDialog.TTDialog(style = TTDialog.Acknowledge, text = TTLocalizer.BossPartyDisband,
                                             command = self.__confirmDisbandParty)
            self._dialog.show()
        else:
            self._prompt.hide()
            base.transitions.noTransitions()

    def __confirmDisbandParty(self, state):
        if self._dialog:
            self._dialog.destroy()
            self._dialog = None

    def goNow(self):
        if self.isActive():
            if self.isHoster():
                self.sendUpdate('goNow')
        else:
            self.hideAll()
            self.setState('Off')
            base.transitions.noTransitions()
            base.localAvatar.setLocked(False, ToontownGlobals.LockedStateMessengerExemption)
            self.sendUpdate('createBossParty', [self._bossCog])

    def startParty(self, zoneId):
        # Hide the interface
        self.hideAll()
        base.transitions.noTransitions()

        # Teleport the Toons to the boss party
        place = self.cr.playGame.getPlace()
        hoods = {
            ToontownGlobals.BossPartyCategoryMinigames: ToontownGlobals.ToontownSkies,
            ToontownGlobals.BossPartyCategorySellbot: ToontownGlobals.SellbotHQ,
            ToontownGlobals.BossPartyCategoryCashbot: ToontownGlobals.CashbotHQ,
            ToontownGlobals.BossPartyCategoryLawbot: ToontownGlobals.LawbotHQ,
            ToontownGlobals.BossPartyCategoryBossbot: ToontownGlobals.BossbotHQ
                 }

        if place:
            category = self.getBossPartyCategory(self._bossCog)
            hoodId = hoods[category]
            # Imagine a world where we had case switches. yayyyyyyyy pyp being outdated!!!!!!!!!!
            if self._bossCog == ToontownGlobals.BossPartyPropHunt:
                place.requestLeave({'loader': 'safeZoneLoader',
                                    'where': 'propHuntGame',
                                    'how': 'teleportIn',
                                    'hoodId': hoodId,
                                    'zoneId': zoneId,
                                    'avId': -1
                                    })
            else:
                place.requestLeave({'loader': ZoneUtil.getBranchLoaderName(hoodId),
                                    'where': 'cogHQBossBattle',
                                    'how': 'placeIn',
                                    'hoodId': hoodId,
                                    'zoneId': zoneId,
                                    'avId': -1
                                    })
        else:
            self.notify.warning("startParty: Couldn't find playGame.getPlace(), zoneId: %s" % zoneId)

    def partyFull(self):
        # Hide the interface if they neither confirmed nor denied
        self.hideAll()

        # Tell them the party is full
        self._dialog = TTDialog.TTDialog(style = TTDialog.Acknowledge, text = TTLocalizer.BossPartyFull,
                                         command = self.__confirmPartyFull)
        self._dialog.show()

    def __confirmPartyFull(self, state):
        if self._dialog:
            self._dialog.destroy()
            self._dialog = None

    def updateToons(self, toons, state):

        self._toonsInPartyGrid.clearItems()

        __portraits = []
        for av in toons:
            portrait = ToonPortrait(avatar = (av[1], av[2], av[3]), team = 3)
            __portraits.append(portrait)
        self._toonsInPartyGrid.addItems(*__portraits)

        # Update the amount of Toons in the party
        count = len(toons)
        limit = self.getLimit()
        self._count.setText(TTLocalizer.BossPartyToonCount.format(count, limit))

        if count >= limit and self._notice['text'] != TTLocalizer.BossPartyWait:
            self.partyFull()
            return

        # If all Toons have responded, set the status to ready
        if state:
            if self.isHoster():
                self._notice.setText(TTLocalizer.BossPartyReady)
            else:
                self._notice.setText(TTLocalizer.BossPartyWaiting)
        elif self._notice['text'] != TTLocalizer.BossPartyWait:
            self._notice.setText(TTLocalizer.BossPartyWait)

    def getLimit(self):
        limit = ToontownGlobals.BossPartyPlayerLimits.get(self._bossCog)
        return limit

    def generatePoster(self, label = None):
        # Clear out the Boss poster from the last party
        bossIcon = self._bossFrame.find('**/BossIcon')
        if bossIcon:
            bossIcon.removeNode()

        # Create the label if we don't have it
        if not label:
            label = self.bossPartyModeToName[self._bossCog]

        # Change the label for the Boss we're going to
        self._label.setText(label)
        self._label.show()

        # Generate a poster for the Boss we're going to
        bossIcon = self._bossFrame.attachNewNode('BossIcon')
        bossPaths = {
            ToontownGlobals.BossPartySellbotBoss: 'VP_NORMAL',
            ToontownGlobals.BossPartySellbotBossStormSellbot: 'VP_NORMAL',
            ToontownGlobals.BossPartySellbotBossHardcore: 'VP_HARDCORE',
            ToontownGlobals.BossPartySellbotBossArena: 'VP_ARENA',
            ToontownGlobals.BossPartySellbotBossWinter: 'VP_WINTER',

            ToontownGlobals.BossPartyCashbotBoss: 'CFO_NORMAL',
            ToontownGlobals.BossPartyCashbotBossHardcore: 'CFO_HARDCORE',

            ToontownGlobals.BossPartyLawbotBoss: 'CJ_NORMAL',
            ToontownGlobals.BossPartyLawbotBossHardcore: 'CJ_HARDCORE',
            ToontownGlobals.BossPartyLawbotBossArena: 'CJ_ARENA',

            ToontownGlobals.BossPartyBossbotBoss: 'CEO_NORMAL',
            ToontownGlobals.BossPartyBossbotBossHardcore: 'CEO_HARDCORE',

            ToontownGlobals.BossPartyPropHunt: 'VP_WINTER'

        }
        bookModel = loader.loadModel('phase_3.5/models/gui/ttoff_m_gui_mgmn_bossParty')
        lIconGeom = bookModel.find('**/' + bossPaths[self._bossCog])
        lIconGeom.setScale(0.3)
        lIconGeom.reparentTo(bossIcon)
        bossIcon.setPos(-.86, 0, .26)
        bookModel.removeNode()

        # If our Boss Party is coming soon, disable the creation button
        if self._bossCog in self.bossPartyComingSoon:
            self._ready.setText(TTLocalizer.BossPartyPlanningComingSoon)
            self._ready['state'] = DGG.DISABLED
        else:
            if not self.isHoster() and not self.isActive():
                self._ready.setText(TTLocalizer.BossPartyPlanningCreate)
            else:
                # Change the text back to "Go Now" if we're pending invites
                self._ready.setText(TTLocalizer.BossPartyGoNow)
            self._ready['state'] = DGG.NORMAL

        # Generate a new help button
        if hasattr(self, '_helpButton') and self._helpButton:
            self._helpButton.destroy()

        description = TTLocalizer.BossPartyId2Description.get(self._bossCog)
        self._helpButton = HelpButton.HelpButton(parent = self._prompt, contents = description,
                                                 pos = (-0.8, 0.0, -0.625), scale = 0.55, image_scale = 1.5)

    def updateBossCog(self):
        # Generate a new poster
        self.generatePoster()

    def toggleBoss(self, modifier):
        # All possible Boss Party categories
        bossPartyCategories = self.getBossPartyCategories()

        # Get the index of our current category
        category = self.getBossPartyCategory(self._bossCog)
        index = bossPartyCategories.index(category)

        # Get our new Boss index
        boss = index + modifier

        # Determine the highest possible Boss index
        cap = len(bossPartyCategories) - 1

        # Wrap forwards and backwards if necessary
        if boss < 0:
            boss = cap
        elif boss > cap:
            boss = 0

        # Set our new Boss index
        self._bossCog = bossPartyCategories[boss]

        # If we're already active, send this info to the server
        if self.isActive():
            self.sendUpdate('toggleBoss', [self._bossCog])
        else:
            # Generate a new Boss poster
            bossLabel = self.bossPartyModeToName[self._bossCog]
            self.generatePoster(bossLabel)

            # Update the notice text depending on our Boss
            self._notice.setText(TTLocalizer.BossPartyPlanningNotice.format(bossLabel[4:]))

            # Update the limit depending on our Boss
            limit = self.getLimit()
            self._count.setText(TTLocalizer.BossPartyPlanningLimit.format(limit))

    def __setToPropHuntTemp(self):
        self._bossCog = ToontownGlobals.BossPartyPropHunt
        self.sendUpdate('toggleBoss', [self._bossCog])

        # Generate a new Boss poster
        bossLabel = self.bossPartyModeToName[self._bossCog]
        self.generatePoster(bossLabel)

        # Update the notice text depending on our Boss
        self._notice.setText(TTLocalizer.BossPartyPlanningNotice.format(bossLabel[4:]))

        # Update the limit depending on our Boss
        limit = self.getLimit()
        self._count.setText(TTLocalizer.BossPartyPlanningLimit.format(limit))

    def toggleBossSubcategory(self, modifier):
        bossPartyCategory = self.getBossPartyCategory(self._bossCog)

        bossPartySubcategories = [bossPartyCategory]
        subcategories = ToontownGlobals.BossPartyDict.get(bossPartyCategory)
        for subcategory in subcategories:
            bossPartySubcategories.append(subcategory)

        index = bossPartySubcategories.index(self._bossCog)

        boss = index + modifier

        cap = len(bossPartySubcategories) - 1

        if boss < 0:
            boss = cap
        elif boss > cap:
            boss = 0

        self._bossCog = bossPartySubcategories[boss]

        if self.isActive():
            self.sendUpdate('toggleBoss', [self._bossCog])
        else:
            # Generate a new Boss poster
            category = self.getBossPartyCategory(self._bossCog)
            bossLabel = self.bossCogs[category]
            self.generatePoster(bossLabel)

            # Update the notice text depending on our Boss
            self._notice.setText(TTLocalizer.BossPartyPlanningNotice.format(bossLabel[4:]))

            # Update the limit depending on our Boss
            limit = self.getLimit()
            self._count.setText(TTLocalizer.BossPartyPlanningLimit.format(limit))

    def hideAll(self):
        self._toonsInPartyGrid.clearItems()
        self._prompt.hide()
        self._label.hide()
        self._labelSubcategory.hide()
        self._leave.hide()
        self._ready.hide()
        if self._dialog:
            self._dialog.hide()

    def getBossPartyCategories(self):
        categories = list(ToontownGlobals.BossPartyCategories.keys())
        return categories

    def getBossPartyCategory(self, index):
        for category, modes in ToontownGlobals.BossPartyCategories.items():
            if index in modes:
                return category

    def hasPromotion(self, av, index):
        # Sometimes we don't want a promotion for the
        # just for fun stuff; example: LawbotArena
        if index in self.bossPartyNoPromoCheck:
            return True
        category = self.getBossPartyCategory(index)
        return av.readyForPromotion(ToontownGlobals.BossPartyPromotionInfo[category])
