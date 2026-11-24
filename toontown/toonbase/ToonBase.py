import atexit
import datetime
import math
import os
import platform
import shutil
import sys
import tempfile
from direct.directnotify import DirectNotifyGlobal
from direct.gui import DirectGuiGlobals
from panda3d.core import *

from direct.gui.DirectGui import *
from direct.filter.FilterManager import FilterManager as DFilterManager
from direct.interval.IntervalGlobal import *
from direct.showbase.MessengerGlobal import messenger
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.toontown import *

from otp.otpbase import OTPBase, OTPLauncherGlobals, OTPGlobals
from toontown.chat.TTWhiteList import TTWhiteList
from toontown.effects.FilterManager import FilterManager
from toontown.launcher import ToontownDownloadWatcher
from toontown.thirdparty import ProfanityWordList
from toontown.thirdparty.ProfanityFilter import Profanity
from . import ClientSettings
from . import ToontownLoader, TTLocalizer, ToontownBattleGlobals, ControlManager, ToontownGlobals, HotkeySettings
from .ToontownFrameRateMeter import ToontownFrameRateMeter

#if TYPE_CHECKING:
#    from ..distributed.ToontownClientRepository import ToontownClientRepository
#    from otp.avatar.LocalAvatar import LocalAvatar
#    from ..toon.DistributedToon import DistributedToon

if sys.platform == 'win32':
    from winreg import ConnectRegistry, OpenKey, HKEY_CURRENT_USER, QueryValueEx


class ToonBase(OTPBase.OTPBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToonBase')
    notify.setDebug(True)

    def __init__(self):
        #if TYPE_CHECKING:
        #    self.cr: 'Optional[ToontownClientRepository]' = None
        #    self.localAvatar: 'Optional[Union[LocalAvatar, DistributedToon]]' = None
        self.clientSettingsManager = ClientSettings.ClientSettingsManager
        self.hotkeySettingsManager = HotkeySettings.HotkeySettingsManager

        OTPBase.OTPBase.__init__(self)
        self.controlManager = ControlManager.ControlManager()
        if self.config.GetBool('software-mode', 0):
            self.makeAllPipes()
            for pipe in self.pipeList:
                if pipe.getInterfaceName() == 'TinyPanda':
                    if self.pipe == pipe:
                        break
                    self.pipe = pipe
                    self.openMainWindow()
                    break
        # if self.pipe.getInterfaceName() != 'TinyPanda':
        #    self.setCursorAndIcon()
        if not self.isMainWindowOpen():
            try:
                launcher.setPandaErrorCode(7)
            except:
                pass

            sys.exit(1)
        self.__lastBackgroundColor = None
        self.certLocation = None
        self.filters = None
        self.disableShowbaseMouse()
        self.addCullBins()
        self.debugRunningMultiplier /= OTPGlobals.ToonSpeedFactor
        self.toonChatSounds = self.config.GetBool('toon-chat-sounds', 1)

        # Info for ppl sending logs
        di = self.pipe.getDisplayInformation()
        di.updateCpuFrequency(0)
        print('== System Information ==')
        print(f'CPU: {di.getCpuBrandString()} ({di.getCurrentCpuFrequency() * 1e-09:.03f}GHz/'
              f'{di.getMaximumCpuFrequency() * 1e-09:.03f}GHz) ')
        print(f'GPU: {self.win.gsg.getDriverRenderer()}')
        print(f'GPU Drivers: {self.win.gsg.getDriverVersion()}')

        if sys.platform == 'win32':
            if platform.machine().endswith('64'):
                programFiles = os.environ['PROGRAMFILES(x86)']
            else:
                programFiles = os.environ['PROGRAMFILES']
            self.defaultTextToSpeechPath = programFiles + '\\eSpeak\\command_line\\espeak'
        elif sys.platform == 'linux2':
            self.defaultTextToSpeechPath = '/usr/bin/espeak'
        else:
            self.defaultTextToSpeechPath = ''
        self.textToSpeechPath = self.config.GetString('text-to-speech-path', self.defaultTextToSpeechPath)
        self.globalChatWhispers = self.config.GetBool('global-chat-whispers', 1)
        self.transparentBook = self.config.GetBool('transparent-book', 0)
        self.smoothThrowing = self.config.GetBool('smooth-throwing', 1)
        self.characterLods = self.config.GetBool('character-lods', 1)
        self.antialiasing = self.config.GetInt('antialiasing', 1)
        self.chatLogOpen = self.config.GetBool('chat-log-open', 1)
        self.japanDialog = self.config.GetBool('japan-dialog', 1)
        self.placeBeforeObjects = self.config.GetBool('place-before-objects', 0)
        self.endlessQuietZone = False
        self.wantDynamicShadows = 0
        self.exitErrorCode = 0

        # Load the whitelist
        self.whiteList = TTWhiteList()

        camera.setPosHpr(0, 0, 0, 0, 0, 0)
        self.camLens.setMinFov(ToontownGlobals.DefaultCameraFov / (4. / 3.))
        self.camLens.setNearFar(ToontownGlobals.DefaultCameraNear, ToontownGlobals.DefaultCameraFar)

        # Setup stuff to put more musicManagers
        self.musicManagerList = [self.musicManager]
        self.musicManagerIsValidList = [self.musicManagerIsValid]

        for musicManager in self.musicManagerList:
            musicManager.setVolume(ClientSettings.MusicVolume.get())

        self.updateSfxMgrs()

        self.setBackgroundColor(ToontownGlobals.DefaultBackgroundColor)

        self.setupTextProperties()

        self.transitions.IrisModelName = 'phase_3/models/misc/iris'
        self.transitions.FadeModelName = 'phase_3/models/misc/fade'
        self.exitFunc = self.userExit
        if 'launcher' in __builtins__ and launcher:
            launcher.setPandaErrorCode(11)
        globalClock.setMaxDt(0.2)
        if self.config.GetBool('want-particles', 1) == 1:
            self.notify.debug('Enabling particles')
            self.enableParticles()
        self.accept(HotkeySettings.TakeScreenshot.getPressed(), self.takeScreenShot)
        if __debug__:
            self.accept(ToontownGlobals.RefreshHotkey, self.refresh)
        self.accept('panda3d-render-error', self.panda3dRenderError)
        oldLoader = self.loader
        self.loader = ToontownLoader.ToontownLoader(self)
        __builtins__['loader'] = self.loader
        oldLoader.destroy()

        self.screenshotSfx = self.loader.loadSfx('phase_4/audio/sfx/Photo_shutter.ogg', manager = 'gui')
        self.accept('PandaPaused', self.disableAllAudio)
        self.accept('PandaRestarted', self.enableAllAudio)
        self.friendMode = self.config.GetBool('switchboard-friends', 0)
        self.wantPets = self.config.GetBool('want-pets', 1)
        self.wantBingo = self.config.GetBool('want-fish-bingo', 1)
        self.wantKarts = self.config.GetBool('want-karts', 1)
        self.wantNewSpecies = self.config.GetBool('want-new-species', 0)
        self.inactivityTimeout = self.config.GetFloat('inactivity-timeout', ToontownGlobals.KeyboardTimeout)
        if self.inactivityTimeout:
            self.notify.debug('Enabling Panda timeout: %s' % self.inactivityTimeout)
            self.mouseWatcherNode.setInactivityTimeout(self.inactivityTimeout)
        self.randomMinigameAbort = self.config.GetBool('random-minigame-abort', 0)
        self.randomMinigameDisconnect = self.config.GetBool('random-minigame-disconnect', 0)
        self.randomMinigameNetworkPlugPull = self.config.GetBool('random-minigame-netplugpull', 0)
        self.autoPlayAgain = self.config.GetBool('auto-play-again', 0)
        self.skipMinigameReward = self.config.GetBool('skip-minigame-reward', 0)
        self.wantMinigameDifficulty = self.config.GetBool('want-minigame-difficulty', 0)
        self.minigameDifficulty = self.config.GetFloat('minigame-difficulty', -1.0)
        if self.minigameDifficulty == -1.0:
            del self.minigameDifficulty
        self.minigameSafezoneId = self.config.GetInt('minigame-safezone-id', -1)
        if self.minigameSafezoneId == -1:
            del self.minigameSafezoneId
        cogdoGameSafezoneId = self.config.GetInt('cogdo-game-safezone-id', -1)
        cogdoGameDifficulty = self.config.GetFloat('cogdo-game-difficulty', -1)
        if cogdoGameDifficulty != -1:
            self.cogdoGameDifficulty = cogdoGameDifficulty
        if cogdoGameSafezoneId != -1:
            self.cogdoGameSafezoneId = cogdoGameSafezoneId
        ToontownBattleGlobals.SkipMovie = self.config.GetBool('skip-battle-movies', 0)
        self.creditCardUpFront = self.config.GetInt('credit-card-up-front', -1)
        if self.creditCardUpFront == -1:
            del self.creditCardUpFront
        else:
            self.creditCardUpFront = self.creditCardUpFront != 0
        self.housingEnabled = self.config.GetBool('want-housing', 1)
        self.cannonsEnabled = self.config.GetBool('estate-cannons', 0)
        self.fireworksEnabled = self.config.GetBool('estate-fireworks', 0)
        self.dayNightEnabled = self.config.GetBool('estate-day-night', 0)
        self.cloudPlatformsEnabled = self.config.GetBool('estate-clouds', 1)
        self.movingCloudPlatforms = self.config.GetBool('want-moving-clouds', 1)
        self.greySpacing = self.config.GetBool('allow-greyspacing', 0)
        self.goonsEnabled = self.config.GetBool('estate-goon', 0)
        self.restrictTrialers = self.config.GetBool('restrict-trialers', 1)
        self.roamingTrialers = self.config.GetBool('roaming-trialers', 1)
        self.slowQuietZone = self.config.GetBool('slow-quiet-zone', 0)
        self.slowQuietZoneDelay = self.config.GetFloat('slow-quiet-zone-delay', 5)
        self.killInterestResponse = self.config.GetBool('kill-interest-response', 0)
        self.experimentalPropRendering = self.config.GetBool('experimental-prop-rendering', False)
        self.lastScreenShotTime = globalClock.getRealTime()
        self.accept(HotkeySettings.MoveForward.getPressed(), self.__walking, extraArgs = [True])
        self.accept(HotkeySettings.MoveForward.getPressed(), self.__walking, extraArgs = [False])
        self.canScreenShot = 1
        self.glitchCount = 0
        self.walking = 0
        self.oldX = max(1, self.win.getXSize())
        self.oldY = max(1, self.win.getYSize())
        self.aspectRatio = float(self.oldX) / self.oldY
        self.enableToggleHotkeys()
        self.aspect2dHidden = False
        self.setupCommonFilters()
        # Search for filters
        FilterManager.searchForFilters()

        colTex = Texture("sceneBuff_Color")
        depthTex = Texture("sceneBuff_Depth")

        fm = DFilterManager(self.win, self.cam)
        fquad = fm.renderSceneInto(depthTex, colTex)
        fquad.setShader(
            Shader.load(Shader.SLGLSL, vertex = 'phase_3/shaders/ttoff_sha_post_generic.vert', fragment = 'phase_3/shaders/ttrm_sha_post_gen.frag')
        )

        self.outlineNode = NodePath("postprocess_outline_holder")

        self.outlinePPBuffer = self.win.makeTextureBuffer("buffer0", 0, 0)
        self.outlinePPBuffer.setClearColor(LVecBase4(0.0, 0.0, 0.0, 0.0))
        self.buff1cam = self.makeCamera(self.outlinePPBuffer, lens = self.camLens)
        self.buff1cam.node().setScene(self.outlineNode)

        self.outlineDepthBuffer = Texture("DEPTH_BUF1")
        self.outlinePPBuffer.addRenderTexture(self.outlineDepthBuffer, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepth)

        self.postProcess = self.outlinePPBuffer.getTextureCard()
        self.postProcess.setTransparency(TransparencyAttrib.MAlpha)
        self.postProcess.setColor(1, 1, 1, 0)
        self.postProcess.reparentTo(render2d)
        self.postProcess.setShader(
            Shader.load(Shader.SLGLSL,
                        vertex = 'phase_3/shaders/ttoff_sha_post_generic.vert',
                        fragment = 'phase_3/shaders/ttrm_sha_post_propgen.frag')
        )
        self.postProcess.setShaderInput('scene_depth_texture', depthTex)
        self.postProcess.setShaderInput('outline_depth_texture', self.outlineDepthBuffer)


        self.profanityFilter = Profanity(ProfanityWordList.WordList)

        if 'intel' in self.win.gsg.getDriverRenderer().lower() and 'hd' in self.win.gsg.getDriverRenderer().lower():
            self.gpuWarning = OnscreenText(text = f'Your graphics unit "{self.win.gsg.getDriverRenderer()}" '
                                                  f'is not supported by Toontown Realms.\n'
                                                  'You will likely experience crashes and performance issues.\n'
                                                  'Use the HideUnsupportedHardwareWarning Magic Word to hide this message.',
                                           fg = (1.0, 1.0, 1.0, 0.2),
                                           scale = 0.05,
                                           parent = base.a2dpTopCenter,
                                           pos = (0, -0.06))
        ## removed for open source release
        #if __debug__:
        #    if os.path.exists('.git/HEAD') and os.path.exists('.git/FETCH_HEAD'):
        #        branch = open('.git/HEAD', 'r').readline().replace('ref: refs/heads/', '').strip()
        #        head = open('.git/FETCH_HEAD').read(6)
        #        self.WIP_LABEL = OnscreenText(text = f'{branch} {head} - development build', parent = base.a2dpBottomLeft,
        #                                      pos = (0.03, 0.03),
        #                                      align = TextNode.ALeft, fg = (1.0, 1.0, 1.0, 0.4), scale = 0.04)
        #        print(f"=== Development: Running REALMSGAME/SRC branch '{branch}' @ {head} ===")
        #    if os.path.exists('resources/.git/HEAD') and os.path.exists('resources/.git/FETCH_HEAD'):
        #        branch = open('resources/.git/HEAD', 'r').readline().replace('ref: refs/heads/', '').strip()
        #        head = open('resources/.git/FETCH_HEAD').read(6)
        #        print(f"=== Development: Running REALMSGAME/RESOURCES branch '{branch}' @ {head} ===")

        #loadPrcFileData('osd', 'on-screen-debug-enabled true')


    def setupTextProperties(self):
        tpm = TextPropertiesManager.getGlobalPtr()
        ToontownGlobals.setInterfaceFont(TTLocalizer.InterfaceFont)
        ToontownGlobals.setSignFont(TTLocalizer.SignFont)
        ToontownGlobals.setFancyFont(TTLocalizer.FancyFont)
        nameTagFontIndex = 0
        for _ in TTLocalizer.NametagFonts:
            ToontownGlobals.setNametagFont(nameTagFontIndex, TTLocalizer.NametagFonts[nameTagFontIndex])
            nameTagFontIndex += 1

        candidateActive = TextProperties()
        candidateActive.setTextColor(0, 0, 1, 1)
        tpm.setProperties('candidate_active', candidateActive)

        candidateInactive = TextProperties()
        candidateInactive.setTextColor(0.3, 0.3, 0.7, 1)
        tpm.setProperties('candidate_inactive', candidateInactive)

        white = TextProperties()
        white.setTextColor(1.0, 1.0, 1.0, 1.0)
        tpm.setProperties('white', white)

        whiteComedy = TextProperties()
        whiteComedy.setTextColor(1.0, 1.0, 1.0, 1.0)
        whiteComedy.setShadowColor(0.0, 0.0, 0.0, 1.0)
        whiteComedy.setFont(ToontownGlobals.getFancyFont())
        tpm.setProperties('white_comedy', whiteComedy)

        self.emojis = []
        emojis = self.loader.loadModel('phase_3/models/gui/ttrm_m_gui_chat_emojis')
        for emojiNP in emojis.getChild(0).getChildren():
            name = emojiNP.getName()
            self.emojis.append(name)
            emoji = emojiNP
            emoji.setScale(1)
            tpm.setGraphic(name, emoji)
            emoji.setZ(-0.25)

        controlIcons: NodePath = self.loader.loadModel('phase_3/models/gui/ttrm_m_gui_gen_keyboardIcons')
        for keyNP in controlIcons.getChild(0).getChildren():
            name = keyNP.getName()
            key = keyNP
            key.setScale(1.5)
            key.setColorScale(1.0, 0.8, 1.0, 1.0)
            tpm.setGraphic(f'kbm_{name}', key)
            key.setZ(-0.4)

        helpButtonGUI = self.loader.loadModel('phase_3.5/models/gui/tt_m_gui_brd_help')
        helpButton = helpButtonGUI.find('**/tt_t_gui_brd_helpUp')
        helpButton.setScale(10)
        tpm.setGraphic('tip.help', helpButton)
        helpButton.setZ(-0.25)

        bookIconModel = self.loader.loadModel('phase_3.5/models/gui/sos_textures')
        spellbookIcon = bookIconModel.find('**/spellbookIcon')
        tpm.setGraphic('shticker.spellbook', spellbookIcon)
        spellbookIcon.setZ(-0.25)

        optionsIcon = bookIconModel.find('**/switch1')
        tpm.setGraphic('shticker.options', optionsIcon)
        optionsIcon.setZ(-0.25)

        serverIcon = bookIconModel.find('**/district')
        tpm.setGraphic('shticker.server', serverIcon)
        serverIcon.setZ(-0.25)

        bookIconModel.detachNode()

        chatInputGui = self.loader.loadModel('phase_3.5/models/gui/chat_input_gui')
        speedchatPlus = chatInputGui.find('**/ChtBx_ChtBtn_UP')
        tpm.setGraphic('gui.speedchatplus', speedchatPlus)
        speedchatPlus.setZ(-0.25)

        speedchatGlobal = chatInputGui.find('**/ChtBx_GlbBtn_RLVR')
        tpm.setGraphic('gui.speedchatglobal', speedchatGlobal)
        speedchatGlobal.setZ(-0.25)

        chatInputGui.removeNode()

        propUi: NodePath = self.loader.loadModel('phase_3.5/models/gui/ttoff_m_gui_propgen')
        privacy_private = propUi.find('**/privacy_private')
        privacy_private.setZ(-0.35)
        tpm.setGraphic('gui.privacy_private', privacy_private)
        privacy_friends = propUi.find('**/privacy_friends')
        privacy_friends.setZ(-0.35)
        tpm.setGraphic('gui.privacy_friends', privacy_friends)
        privacy_public = propUi.find('**/privacy_public')
        privacy_public.setZ(-0.35)
        tpm.setGraphic('gui.privacy_public', privacy_public)
        propUi.removeNode()

        WLDisplay = TextProperties()
        WLDisplay.setSlant(0.3)
        tpm.setProperties('WLDisplay', WLDisplay)

        WLEnter = TextProperties()
        WLEnter.setTextColor(1.0, 0.0, 0.0, 1)
        tpm.setProperties('WLEnter', WLEnter)

        WLMagicWord = TextProperties()
        WLMagicWord.setTextColor(0.6, 0.0, 0.6, 1)
        tpm.setProperties('WLMagicWord', WLMagicWord)

        WLMagicWordArg = TextProperties()
        WLMagicWordArg.setTextColor(0.8, 0.4, 0.6, 1)
        tpm.setProperties('WLMagicWordArg', WLMagicWordArg)

        WLMagicWordArgDesc = TextProperties()
        WLMagicWordArgDesc.setTextScale(0.5)
        WLMagicWordArgDesc.setGlyphShift(-.4)
        tpm.setProperties('WLMagicWordArgDesc', WLMagicWordArgDesc)

        del tpm

    def setupCommonFilters(self):
        if self.filters is not None:
            return  # Tried to setup filters twice!
        from direct.filter.CommonFilters import CommonFilters
        self.filters = CommonFilters(self.win, self.cam)

    def setFrameRateMeter(self, flag):
        # This is now a no-op because we defined our own for the coloring behavior
        # The builtin 'loader' isn't defined yet so we can't use Panda's method for this
        pass

    def toggleFrameRateMeter(self, flag):
        if not self.frameRateMeter:
            self.frameRateMeter = ToontownFrameRateMeter(self)

        if not self.frameRateMeter.isLoaded:
            self.frameRateMeter.load()

        if flag:
            self.frameRateMeter.enter()
        else:
            self.frameRateMeter.exit()

    def enableToggleHotkeys(self):
        self.accept(HotkeySettings.ToggleNametagVisibility.getPressed(), self.toggleNametags)
        self.accept(HotkeySettings.ToggleMarginVisibility.getPressed(), self.toggleAspect2D)
        self.accept(HotkeySettings.ToggleOobeCamera.getPressed(), self.oobe)

    def disableToggleHotkeys(self):
        self.ignore(HotkeySettings.ToggleNametagVisibility.getPressed())
        self.ignore(HotkeySettings.ToggleMarginVisibility.getPressed())
        self.ignore(HotkeySettings.ToggleOobeCamera.getPressed())

    def openMainWindow(self, *args, **kw):
        result = OTPBase.OTPBase.openMainWindow(self, *args, **kw)
        self.setCursorAndIcon()
        return result

    def setCursorAndIcon(self):
        self.notify.info('Setting mouse cursor and window icon')
        tempdir = tempfile.mkdtemp()
        atexit.register(shutil.rmtree, tempdir)
        vfs = VirtualFileSystem.getGlobalPtr()

        searchPath = DSearchPath()
        searchPath.appendDirectory(Filename('/phase_3/models/gui'))

        for filename in ('toonmono.cur', 'icon.ico'):
            p3filename = Filename(filename)
            found = vfs.resolveFilename(p3filename, searchPath)
            if not found:
                self.notify.warning('Could not find {} on search path: {}'.format(p3filename, searchPath))
                return  # Can't do anything past this point.

            with open(os.path.join(tempdir, filename), 'wb') as f:
                f.write(vfs.readFile(p3filename, False))

        wp = WindowProperties()
        wp.setCursorFilename(Filename.fromOsSpecific(os.path.join(tempdir, 'toonmono.cur')))
        wp.setIconFilename(Filename.fromOsSpecific(os.path.join(tempdir, 'icon.ico')))
        self.win.requestProperties(wp)
        # get the cacert file (we have this here to share the same temp folder
        searchPath = DSearchPath()
        searchPath.appendDirectory(Filename('/phase_3/etc'))
        certFile = Filename('cacert.pem')
        found = vfs.resolveFilename(certFile, searchPath)
        if not found:
            self.notify.warning('Could not find {} on search path: {}'.format(p3filename, searchPath))
            return
        with open(os.path.join(tempdir, 'cacert.pem'), 'wb') as f:
            f.write(vfs.readFile(certFile, False))
        self.certLocation = os.path.join(tempdir, 'cacert.pem')

    def windowEvent(self, win):
        OTPBase.OTPBase.windowEvent(self, win)

        # Pass the new resolution to the filter manager
        FilterManager.updateInputs()

        if not self.config.GetInt('keep-aspect-ratio', 0):
            return
        x = max(1, win.getXSize())
        y = max(1, win.getYSize())
        maxX = self.pipe.getDisplayWidth()
        maxY = self.pipe.getDisplayHeight()
        cwp = win.getProperties()
        originX = 0
        originY = 0
        if cwp.hasOrigin():
            originX = cwp.getXOrigin()
            originY = cwp.getYOrigin()
            if originX > maxX:
                originX = originX - maxX
            if originY > maxY:
                originY = originY - maxY
        maxX -= originX
        maxY -= originY
        if math.fabs(x - self.oldX) > math.fabs(y - self.oldY):
            newY = x / self.aspectRatio
            newX = x
            if newY > maxY:
                newY = maxY
                newX = self.aspectRatio * maxY
        else:
            newX = self.aspectRatio * y
            newY = y
            if newX > maxX:
                newX = maxX
                newY = maxX / self.aspectRatio
        wp = WindowProperties()
        wp.setSize(newX, newY)
        self.win.requestProperties(wp)
        self.cam.node().getLens().setFilmSize(newX, newY)
        self.oldX = newX
        self.oldY = newY

    def disableShowbaseMouse(self):
        self.useDrive()
        self.disableMouse()
        if self.mouseInterface:
            self.mouseInterface.detachNode()
        if self.mouse2cam:
            self.mouse2cam.detachNode()

    def addCullBins(self):
        cullBinMgr = CullBinManager.getGlobalPtr()
        cullBinMgr.addBin('gui-popup', CullBinManager.BTUnsorted, 60)
        cullBinMgr.addBin('shadow', CullBinManager.BTFixed, 15)
        cullBinMgr.addBin('ground', CullBinManager.BTFixed, 14)

    def __walking(self, pressed):
        self.walking = pressed

    def takeScreenShot(self):
        folder = 'screenshots'
        if sys.platform == 'win32':
            directoryIndex = ClientSettings.ScreenshotDirectory.get()
            if directoryIndex == ClientSettings.EScreenshotDirectory.WINPHOTOS:
                # Retrieve the Windows Pictures Library location
                reg = ConnectRegistry(None, HKEY_CURRENT_USER)
                akey = OpenKey(reg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")

                location = QueryValueEx(akey, "My Pictures")[0]

                # Handle things like %LOCALAPPDATA% or %USERPROFILE%
                location = os.path.expandvars(location)

                folder = os.path.join(location, 'Toontown Realms')
                reg.Close()

        if not os.path.exists(folder):
            os.mkdir(folder)

        namePrefix = ConfigVariableList('screenshot-prefix').getStringValue(0)
        namePrefix = folder + '/' + launcher.logPrefix + namePrefix
        timedif = globalClock.getRealTime() - self.lastScreenShotTime
        if self.glitchCount > 10 and self.walking:
            return
        if timedif < 1.0 and self.walking:
            self.glitchCount += 1
            return

        ctext = ''
        self.screenshotStr = ''

        def doScreenshot(ctext):
            self.graphicsEngine.renderFrame()
            filenameStr = self.config.GetString('screenshot-filename', '%~p-%Y-%m-%d-%H-%M-%S-%~f.%~e')
            filenameStr = filenameStr.replace('%~p', namePrefix) \
                .replace('%~e', ToontownGlobals.ScreenshotFormats[ClientSettings.ScreenshotFormat.get().value]) \
                .replace('%~f', str(globalClock.getFrameCount()))
            filenameStr = datetime.datetime.now().strftime(filenameStr)

            self.screenshot(namePrefix = Filename.fromOsSpecific(filenameStr), defaultFilename = False, blocking = False,
                            imageComment = f"{ctext} {self.screenshotStr}")

            self.lastScreenShotTime = globalClock.getRealTime()

        if not hasattr(self, 'localAvatar'):
            doScreenshot(ctext)
            return

        coordOnScreen = self.config.GetBool('screenshot-coords', 0)
        if hasattr(self.localAvatar.controlManager.currentControls, 'stopThisFrame'):
            self.localAvatar.stopThisFrame = 1
        ctext = self.localAvatar.getAvPosStr()

        messenger.send('takingScreenshot')

        if coordOnScreen:
            coordTextLabel = DirectLabel(pos = (-0.81, 0.001, -0.87), text = ctext, text_scale = 0.05, text_fg = VBase4(1.0, 1.0, 1.0, 1.0), text_bg = (0, 0, 0, 0),
                                         text_shadow = (0, 0, 0, 1), relief = None)
            coordTextLabel.setBin('gui-popup', 0)
            strTextLabel = None
            if len(self.screenshotStr):
                strTextLabel = DirectLabel(pos = (0.0, 0.001, 0.9), text = self.screenshotStr, text_scale = 0.05, text_fg = VBase4(1.0, 1.0, 1.0, 1.0), text_bg = (0, 0, 0, 0),
                                           text_shadow = (0, 0, 0, 1), relief = None)
                strTextLabel.setBin('gui-popup', 0)

        doScreenshot(ctext)

        if coordOnScreen:
            if strTextLabel is not None:
                strTextLabel.destroy()
            coordTextLabel.destroy()
        self.playSfx(self.screenshotSfx)

    def addScreenshotString(self, str):
        if len(self.screenshotStr):
            self.screenshotStr += '\n'
        self.screenshotStr += str

    if __debug__:
        def refresh(self):
            try:
                import limeade
            except ModuleNotFoundError:
                self.notify.warning('Limeade must be installed to refresh.')
                if hasattr(self, 'localAvatar'):
                    self.localAvatar.setSystemMessage(0, 'Limeade must be installed to refresh.')
                return
            # Refresh all the modules currently imported with Limeade.
            limeade.refresh()

            # Since Limeade refreshes the language module (e.g. TTLocalizerEnglish.py) and doesn't update
            # the both the OTPLocalizer and TTLocalizer module with the changes made to it,
            # we have to do so ourselves.

            # First the OTPLocalizer...
            from otp.otpbase import OTPLocalizer
            languageModule = OTPLocalizer.getLanguageModule()
            for key, val in languageModule.__dict__.items():
                if key in OTPLocalizer.__dict__:
                    OTPLocalizer.__dict__[key] = val

            # And now the TTLocalizer...
            languageModule = TTLocalizer.getLanguageModule()
            for key, val in languageModule.__dict__.items():
                if key in TTLocalizer.__dict__:
                    TTLocalizer.__dict__[key] = val
            # We're all done!
            self.notify.info('Modules has been refreshed.')
            if hasattr(self, 'localAvatar'):
                self.localAvatar.setSystemMessage(0, 'Modules has been refreshed.')

    def initNametagGlobals(self):
        arrow = self.loader.loadModel('phase_3/models/props/arrow')
        card = self.loader.loadModel('phase_3/models/props/panel')
        if ClientSettings.ClassicChatBubbles.get():
            speech3d = ChatBalloon(self.loader.loadModel('phase_3/models/props/chatbox').node())
            thought3d = ChatBalloon(self.loader.loadModel('phase_3/models/props/chatbox_thought_cutout').node())
            exclaim3d = ChatBalloon(self.loader.loadModel('phase_3/models/props/chatbox_exclaim_cutout').node())
            speech2dNode = self.loader.loadModel('phase_3/models/props/chatbox_noarrow')
        else:
            speech3d = ChatBalloon(self.loader.loadModel('phase_3/models/gui/ttoff_m_gui_chat_bubbleGen').node())
            thought3d = ChatBalloon(self.loader.loadModel('phase_3/models/gui/ttoff_m_gui_chat_bubbleThought').node())
            exclaim3d = ChatBalloon(self.loader.loadModel('phase_3/models/gui/ttoff_m_gui_chat_bubbleExclaim').node())
            speech2dNode = self.loader.loadModel('phase_3/models/gui/ttoff_m_gui_chat_bubbleNoArrow')
        exclaim3d.setHscale(1.25)
        if ClientSettings.ClassicNametags.get():
            NametagGlobals.setRetroMode(True)
            speech2dNode.find("**/bottom").setTextureOff(1)
            speech2dNode.find("**/middle").setTextureOff(1)
            speech2dNode.find("**/top").setTextureOff(1)
        speech2d = ChatBalloon(speech2dNode.node())
        speech2dNode.removeNode()
        chatButtonGui = self.loader.loadModel('phase_3/models/gui/chat_button_gui')
        NametagGlobals.setCamera(self.cam)
        NametagGlobals.setAspect2d(self.aspect2d)
        NametagGlobals.setArrowModel(arrow)
        NametagGlobals.setNametagCard(card, VBase4(-0.5, 0.5, -0.5, 0.5))
        if self.mouseWatcherNode:
            NametagGlobals.setMouseWatcher(self.mouseWatcherNode)
        NametagGlobals.setSpeechBalloon3d(speech3d)
        NametagGlobals.setThoughtBalloon3d(thought3d)
        NametagGlobals.setExclaimBalloon3d(exclaim3d)
        NametagGlobals.setSpeechBalloon2d(speech2d)
        NametagGlobals.setThoughtBalloon2d(thought3d)
        NametagGlobals.setExclaimBalloon2d(speech2d)
        NametagGlobals.setPageButton(PGButton.SReady, chatButtonGui.find('**/Horiz_Arrow_UP'))
        NametagGlobals.setPageButton(PGButton.SDepressed, chatButtonGui.find('**/Horiz_Arrow_DN'))
        NametagGlobals.setPageButton(PGButton.SRollover, chatButtonGui.find('**/Horiz_Arrow_Rllvr'))
        NametagGlobals.setQuitButton(PGButton.SReady, chatButtonGui.find('**/CloseBtn_UP'))
        NametagGlobals.setQuitButton(PGButton.SDepressed, chatButtonGui.find('**/CloseBtn_DN'))
        NametagGlobals.setQuitButton(PGButton.SRollover, chatButtonGui.find('**/CloseBtn_Rllvr'))
        rolloverSound = DirectGuiGlobals.getDefaultRolloverSound()
        if rolloverSound:
            NametagGlobals.setRolloverSound(rolloverSound)
        clickSound = DirectGuiGlobals.getDefaultClickSound()
        if clickSound:
            NametagGlobals.setClickSound(clickSound)
        NametagGlobals.setToon(self.cam)
        self.marginManager = MarginManager()
        self.margins = self.aspect2d.attachNewNode(self.marginManager, DirectGuiGlobals.MIDGROUND_SORT_INDEX + 1)
        mm = self.marginManager
        self.leftCells = [
            mm.addGridCell(0, 1, -1.33333333333, 1.33333333333, -1.0, 1.0, self.a2dTopLeft, (0.222222, 0, -1.5)),
            mm.addGridCell(0, 2, -1.33333333333, 1.33333333333, -1.0, 1.0, self.a2dTopLeft, (0.222222, 0, -1.16667)),
            mm.addGridCell(0, 3, -1.33333333333, 1.33333333333, -1.0, 1.0, self.a2dTopLeft, (0.222222, 0, -0.833333)),
            mm.addGridCell(0, 3, -1.33333333333, 1.33333333333, -1.0, 1.0, self.a2dTopLeft, (0.222222, 0, -0.5)),
        ]
        self.bottomCells = [mm.addGridCell(0.5, 0, -1.33333333333, 1.33333333333, -1.0, 1.0, self.a2dBottomCenter, (-0.888889, 0, 0.16667)),
                            mm.addGridCell(1.5, 0, -1.33333333333, 1.33333333333, -1.0, 1.0, self.a2dBottomCenter, (-0.444444, 0, 0.16667)),
                            mm.addGridCell(2.5, 0, -1.33333333333, 1.33333333333, -1.0, 1.0, self.a2dBottomCenter, (0, 0, 0.16667)),
                            mm.addGridCell(3.5, 0, -1.33333333333, 1.33333333333, -1.0, 1.0, self.a2dBottomCenter, (0.444444, 0, 0.16667)),
                            mm.addGridCell(4.5, 0, -1.33333333333, 1.33333333333, -1.0, 1.0, self.a2dBottomCenter, (0.888889, 0, 0.16667))]
        self.rightCells = [
            mm.addGridCell(5, 1, -1.33333333333, 1.33333333333, -1.0, 1.0, self.a2dTopRight, (-0.222222, 0, -1.5)),
            mm.addGridCell(5, 2, -1.33333333333, 1.33333333333, -1.0, 1.0, self.a2dTopRight, (-0.222222, 0, -1.16667)),
            mm.addGridCell(5, 2, -1.33333333333, 1.33333333333, -1.0, 1.0, self.a2dTopRight, (-0.222222, 0, -0.833333)),
            mm.addGridCell(5, 2, -1.33333333333, 1.33333333333, -1.0, 1.0, self.a2dTopRight, (-0.222222, 0, -0.5))
        ]

    def setCellsAvailable(self, cell_list, available):
        for cell in cell_list:
            self.marginManager.setCellAvailable(cell, available)

    def cleanupDownloadWatcher(self):
        self.downloadWatcher.cleanup()
        del self.downloadWatcher

    def startShow(self, cr):
        self.cr = cr
        if self.config.GetBool('framebuffer-multisample', False):
            self.render.setAntialias(AntialiasAttrib.MAuto)
            self.render2d.setAntialias(AntialiasAttrib.MAuto)
            if self.config.GetBool('want-render2dp', True):
                self.render2dp.setAntialias(AntialiasAttrib.MAuto)
        self.graphicsEngine.renderFrame()
        if not launcher.isDownloadComplete():
            self.downloadWatcher = ToontownDownloadWatcher.ToontownDownloadWatcher(TTLocalizer.LauncherPhaseNames)
            self.acceptOnce('launcherAllPhasesComplete', self.cleanupDownloadWatcher)
        self.cr.loginFSM.request('mainMenu')

    def connectToMiniserver(self, address = '127.0.0.1'):
        """
        Connects to the selected server address

        :param address: Server Address
        :type address: str
        """
        url = URLSpec(address, 1)
        if self.config.GetBool('want-ssl', False):
            url.setScheme('s')
        if not url.hasPort():
            url.setPort(7198)
        self.notify.info(f'Connecting to {url}...')

        self.cr.loginFSM.request('connect', [[url]])

    def startServer(self):
        if self.cr.isConnected():
            # If we're already on a mini-server, disconnect from that server first.
            self.cr.sendSetAvatarIdMsg(0)
            self.cr.sendDisconnect()
        import builtins

        from otp.otpbase.OTPLocalizer import CRLoadingGameServices

        dialogClass = ToontownGlobals.getGlobalDialogClass()
        builtins.gameServicesDialog = dialogClass(message = CRLoadingGameServices, dialogName = 'loadingGameServicesDialog')
        builtins.gameServicesDialog.show()

        from toontown.server.DedicatedServer import DedicatedServer

        builtins.localServer = DedicatedServer(isLocal = True)
        builtins.localServer.start()

        def localServerReady():
            builtins.gameServicesDialog.cleanup()
            del builtins.gameServicesDialog
            self.joinLocalServer()

        self.acceptOnce('localServerReady', localServerReady)

    def joinLocalServer(self):
        gameServer = '127.0.0.1'
        bboard.post('game-server', gameServer)
        serverPort = self.config.GetInt('server-port', 7198)
        serverList = []
        for name in gameServer.split(';'):
            url = URLSpec(name, 1)
            if self.config.GetBool('want-ssl', False):
                url.setScheme('s')
            if not url.hasPort():
                url.setPort(serverPort)
            serverList.append(url)

        if len(serverList) == 1:
            failover = self.config.GetString('server-failover', '')
            serverURL = serverList[0]
            for arg in failover.split():
                try:
                    port = int(arg)
                    url = URLSpec(serverURL)
                    url.setPort(port)
                except:
                    url = URLSpec(arg, 1)

                if url != serverURL:
                    serverList.append(url)

        self.cr.loginFSM.request('connect', [serverList])

    def removeGlitchMessage(self):
        self.ignore(HotkeySettings.MoveForward.getPressed())
        self.ignore(HotkeySettings.MoveForward.getReleased())

    def exitShow(self, errorCode = None):
        self.notify.info('Exiting Toontown: errorCode = %s' % errorCode)
        if errorCode:
            launcher.setPandaErrorCode(errorCode)
        else:
            launcher.setPandaErrorCode(0)
        sys.exit(0)

    def setExitErrorCode(self, code):
        self.exitErrorCode = code
        if os.name == 'nt':
            exitCode2exitPage = {OTPLauncherGlobals.ExitEnableChat: 'chat',
                                 OTPLauncherGlobals.ExitSetParentPassword: 'setparentpassword',
                                 OTPLauncherGlobals.ExitPurchase: 'purchase'}
            if code in exitCode2exitPage:
                launcher.setRegistry('EXIT_PAGE', exitCode2exitPage[code])

    def getExitErrorCode(self):
        return self.exitErrorCode

    def userExit(self):
        try:
            self.localAvatar.d_setAnimState('TeleportOut', 1)
        except:
            pass

        if self.cr.timeManager:
            self.cr.timeManager.setDisconnectReason(ToontownGlobals.DisconnectCloseWindow)
        self.cr._userLoggingOut = False
        try:
            self.localAvatar
        except:
            pass
        else:
            messenger.send('clientLogout')
            self.cr.dumpAllSubShardObjects()

        self.cr.loginFSM.request('shutdown')
        self.notify.warning('Could not request shutdown; exiting anyway.')
        self.exitShow()

    def panda3dRenderError(self):
        launcher.setPandaErrorCode(14)
        if self.cr.timeManager:
            self.cr.timeManager.setDisconnectReason(ToontownGlobals.DisconnectGraphicsError)
        self.cr.sendDisconnect()
        sys.exit()

    def getShardPopLimits(self):
        limit = self.cr.populationLimit
        low = limit // 3
        med = low * 2
        return low, med, limit

    def playMusic(self, music, looping = 0, interrupt = 1, volume = None, time = 0.0):
        OTPBase.OTPBase.playMusic(self, music, looping, interrupt, volume, time)

    def loadFromSettings(self):
        displayMode = ClientSettings.DisplayMode.get()
        fullscreen = displayMode == 1
        undecorated = displayMode == 2
        music = ClientSettings.MusicEnabled.get()
        toonChatSounds = ClientSettings.ToonChatSounds.get()
        textToSpeech = ClientSettings.TextToSpeechEnabled.get()
        textToSpeechPath = ClientSettings.TextToSpeechPath.get()
        globalChatWhispers = ClientSettings.GlobalChatPopups.get()
        smoothThrowing = ClientSettings.SmoothThrowing.get()
        characterLods = ClientSettings.AvatarLODs.get()
        japanDialog = ClientSettings.JapanDialog.get()
        musicVol = ClientSettings.MusicVolume.get()
        sfxVol = ClientSettings.VolumeMaster.get()
        res = ClientSettings.Resolution.get()
        antialias = ClientSettings.AntiAliasing.get()
        syncVideo = ClientSettings.VerticalSync.get()
        smootherDelay = ClientSettings.SmootherDelay.get()
        posSendRate = ClientSettings.PositionSendRate.get()
        if antialias:
            loadPrcFileData('toonBase Settings Framebuffer MSAA', 'framebuffer-multisample 1')
            loadPrcFileData('toonBase Settings MSAA Level', 'multisamples %i' % antialias)
        else:
            loadPrcFileData('toonBase Settings Framebuffer MSAA', 'framebuffer-multisample 0')
        loadPrcFileData('toonBase Settings Window Res', 'win-size %s %s' % (res[0], res[1]))
        loadPrcFileData('toonBase Settings Window FullScreen', 'fullscreen %i' % fullscreen)
        loadPrcFileData('toonBase Settings Window Undecorated', 'undecorated %i' % undecorated)
        loadPrcFileData('toonBase Settings Music Active', 'audio-music-active %s' % music)
        loadPrcFileData('toonBase Settings Music Volume', 'audio-master-music-volume %s' % musicVol)
        loadPrcFileData('toonBase Settings Sfx Volume', 'audio-master-sfx-volume %s' % sfxVol)
        loadPrcFileData('toonBase Settings Toon Chat Sounds', 'toon-chat-sounds %s' % toonChatSounds)
        loadPrcFileData('toonBase Settings Text to Speech', 'text-to-speech %s' % textToSpeech)
        loadPrcFileData('toonBase Settings Text to Speech Path', 'text-to-speech-path %s' % textToSpeechPath)
        loadPrcFileData('toonBase Settings Global Chat Whispers', 'global-chat-whispers %s' % globalChatWhispers)
        loadPrcFileData('toonBase Settings Smooth Throwing', 'smooth-throwing %s' % smoothThrowing)
        loadPrcFileData('toonBase Settings Character LODs', 'character-lods %s' % characterLods)
        loadPrcFileData('toonBase Settings Antialiasing', 'antialiasing %s' % antialias)
        loadPrcFileData('toonBase Settings Japanese Dialog', 'japan-dialog %s' % japanDialog)
        loadPrcFileData('toonBase settings v-sync', 'sync-video %s' % syncVideo)
        loadPrcFileData('toonBase settings smoother lag', f'smooth-lag {smootherDelay}')
        loadPrcFileData('toonBase settings pos update rate', f'pos-update-rate {posSendRate}')
       # self.settings.loadFromSettings()

    def toggleNametags(self, override = -1):
        visible = not NametagGlobals.getMasterNametagsVisible() if override == -1 else override
        NametagGlobals.setMasterNametagsVisible(visible)
        NametagGlobals.setMasterNametagsActive(visible)

    def toggleAspect2D(self):
        if self.aspect2d.isHidden():
            self.aspect2dHidden = False
            self.aspect2d.show()
        else:
            self.aspect2dHidden = True
            self.aspect2d.hide()

    def resetTextToSpeech(self):
        ClientSettings.TextToSpeechEnabled.set(False)

        if sys.platform == 'win32':
            if platform.machine().endswith('64'):
                programFiles = os.environ['PROGRAMFILES(x86)']
            else:
                programFiles = os.environ['PROGRAMFILES']
            filePath = programFiles + '\\eSpeak\\command_line\\espeak'
        elif sys.platform == 'linux2':
            filePath = '/usr/bin/espeak'
        self.textToSpeechPath = filePath
        ClientSettings.TextToSpeechPath.set(filePath)

    def setBackgroundColor(self, r = None, g = None, b = None, a = 0.0, win = None, temporary = False):
        if not temporary:
            # get color that we can store
            if g is not None:
                color = VBase4(r, g, b, a)
            else:
                arg = r
                if isinstance(arg, VBase4):
                    color = arg
                else:
                    color = VBase4(arg[0], arg[1], arg[2], a)
            self.__lastBackgroundColor = color
        OTPBase.OTPBase.setBackgroundColor(self, r = r, g = g, b = b, a = a, win = win)

    def restoreBackgroundColor(self):
        if self.__lastBackgroundColor is not None:
            OTPBase.OTPBase.setBackgroundColor(self, r = self.__lastBackgroundColor)

    def addMusicManager(self, extraMusicManager):
        """
        Adds an additional music audio manager to `musicManagerList`, the list of
        managers managed by ToonBase.
        """
        # keep a list of music manager objects to apply settings to,
        # since there may be others in addition to the one we create here
        self.musicManagerList.append(extraMusicManager)
        newMusicManagerIsValid = extraMusicManager is not None and extraMusicManager.isValid()
        self.musicManagerIsValidList.append(newMusicManagerIsValid)
        if newMusicManagerIsValid:
            extraMusicManager.setConcurrentSoundLimit(1)
            extraMusicManager.setActive(self.musicActive)

    def SetAllMusicEnables(self, bEnabled):
        """Calls ``setActive(bEnabled)`` on all valid music managers."""
        for i in range(len(self.musicManagerList)):
            if self.musicManagerIsValidList[i]:
                self.musicManagerList[i].setActive(bEnabled)

    def enableMusic(self, bEnableMusic):
        """
        Enables or disables music managers.
        """
        # don't setActive(1) if no audiofocus
        if self.AppHasAudioFocus or (bEnableMusic == 0):
            self.SetAllMusicEnables(bEnableMusic)
        self.musicActive = bEnableMusic
        if bEnableMusic:
            # This is useful when we want to play different music
            # from what the primary manager has queued
            messenger.send("MusicEnabled")
            self.notify.debug("Enabling music")
        else:
            self.notify.debug("Disabling music")

    def disableAllAudio(self):
        """
        Disables all SFX and music managers, meant to be called when the app
        loses audio focus.
        """
        self.AppHasAudioFocus = 0
        self.SetAllSfxEnables(0)
        self.SetAllMusicEnables(0)
        self.notify.debug("Disabling audio")

    def enableAllAudio(self):
        """
        Reenables the SFX and music managers that were active at the time
        `disableAllAudio()` was called.  Meant to be called when the app regains
        audio focus.
        """
        self.AppHasAudioFocus = 1
        self.SetAllSfxEnables(self.sfxActive)
        self.SetAllMusicEnables(self.musicActive)
        self.notify.debug("Enabling audio")

    def updateSfxMgrs(self):
        self.musicManager.setVolume(ClientSettings.VolumeMaster.get() * ClientSettings.MusicVolume.get())
        self.sfxMgrMaster.setVolume(ClientSettings.VolumeMaster.get() * ClientSettings.VolumeSFX.get())
        self.sfxMgrDialog.setVolume(ClientSettings.VolumeMaster.get() * ClientSettings.VolumeDialog.get())
        self.sfxMgrBattle.setVolume(ClientSettings.VolumeMaster.get() * ClientSettings.VolumeBattle.get())
        self.sfxMgrEnvironment.setVolume(ClientSettings.VolumeMaster.get() * ClientSettings.VolumeEnvironment.get())
        self.sfxMgrStreetProps.setVolume(ClientSettings.VolumeMaster.get() * ClientSettings.VolumeStreetProps.get())
        self.sfxMgrGui.setVolume(ClientSettings.VolumeMaster.get() * ClientSettings.VolumeGui.get())

        self.musicManager.setActive(ClientSettings.MusicEnabled.get() and ClientSettings.VolumeMasterEnabled.get())
        self.sfxMgrMaster.setActive(ClientSettings.VolumeSFXEnabled.get() and ClientSettings.VolumeMasterEnabled.get())
        self.sfxMgrDialog.setActive(ClientSettings.VolumeDialogEnabled.get() and ClientSettings.VolumeMasterEnabled.get())
        self.sfxMgrBattle.setActive(ClientSettings.VolumeBattleEnabled.get() and ClientSettings.VolumeMasterEnabled.get())
        self.sfxMgrEnvironment.setActive(ClientSettings.VolumeEnvironmentEnabled.get() and ClientSettings.VolumeMasterEnabled.get())
        self.sfxMgrGui.setActive(ClientSettings.VolumeGuiEnabled.get() and ClientSettings.VolumeMasterEnabled.get())
        self.sfxMgrStreetProps.setActive(ClientSettings.VolumeStreetPropsEnabled.get() and ClientSettings.VolumeMasterEnabled.get())

    def _ShowBase__audioLoop(self, task):
        # Overload to loop all musicManagers
        for musicManager in self.musicManagerList:
            musicManager.update()
        for sfxManager in self.sfxManagerList:
            sfxManager.update()
        return task.cont