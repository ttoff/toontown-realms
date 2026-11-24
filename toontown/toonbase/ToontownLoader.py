import json
from typing import Optional, Tuple, Union, List

from panda3d.core import *
from panda3d.toontown import *
from direct.directnotify.DirectNotifyGlobal import *
from direct.showbase import Loader
from direct.stdpy import file
from toontown.toontowngui import ToontownLoadingScreen
from toontown.toontowngui import ToontownOfflineLoadingScreen
from toontown.toonbase import TTLocalizer, ClientSettings
from toontown.toonbase import ToontownGlobals


class ToontownLoader(Loader.Loader):
    TickPeriod = 0.2

    def __init__(self, base):
        Loader.Loader.__init__(self, base)
        self.inBulkBlock = None
        self.blockName = None
        if not ClientSettings.ClassicLoadingScreen.get():
            self.loadingScreen = ToontownOfflineLoadingScreen.ToontownOfflineLoadingScreen()
        else:
            self.loadingScreen = ToontownLoadingScreen.ToontownLoadingScreen()
        return

    def destroy(self):
        self.loadingScreen.destroy()
        del self.loadingScreen
        Loader.Loader.destroy(self)

    def beginBulkLoad(self, name, label, range, gui, tipCategory, zoneId = None):
        self._loadStartT = globalClock.getRealTime()
        Loader.Loader.notify.info("starting bulk load of block '%s'" % name)
        if self.inBulkBlock:
            Loader.Loader.notify.warning("Tried to start a block ('%s'), but am already in a block ('%s')" % (name, self.blockName))
            return None
        self.inBulkBlock = 1
        self._lastTickT = globalClock.getRealTime()
        self.blockName = name

        # Expand general tips
        if tipCategory == TTLocalizer.TIP_GENERAL:
            tipCategory = [TTLocalizer.TIP_GENERAL, TTLocalizer.TIP_OFFLINE_MODE]

            # Determine the gamemode
            try:
                if localServer:
                    gamemode = ToontownGlobals.ModeOffline
            except:
                gamemode = ToontownGlobals.ModeServer

            if gamemode == ToontownGlobals.ModeServer:
                tipCategory.append(TTLocalizer.TIP_MINISERVER_MODE)

            # Legit mode
            if hasattr(base.cr, 'legitMode') and base.cr.legitMode:
                tipCategory.append(TTLocalizer.TIP_LEGIT)
            else:
                tipCategory.append(TTLocalizer.TIP_CHEATS)

            # Holidays
            holiday = self.loadingScreen.getActiveHoliday()
            if holiday == ToontownGlobals.HolidayAprilFools:
                tipCategory.append(TTLocalizer.TIP_APRIL_FOOLS)
            # elif holiday == ToontownGlobals.HolidayHalloween:
            # tipCategory.append(TTLocalizer.TIP_HALLOWEEN)
            elif holiday == ToontownGlobals.HolidayWinter:
                tipCategory.append(TTLocalizer.TIP_WINTER)

        self.loadingScreen.begin(range, label, gui, tipCategory, zoneId)
        return None

    def endBulkLoad(self, name):
        if not self.inBulkBlock:
            Loader.Loader.notify.warning("Tried to end a block ('%s'), but not in one" % name)
            return None
        if name != self.blockName:
            Loader.Loader.notify.warning("Tried to end a block ('%s'), other then the current one ('%s')" % (name, self.blockName))
            return None
        self.inBulkBlock = None
        expectedCount, loadedCount = self.loadingScreen.end(name)
        now = globalClock.getRealTime()
        Loader.Loader.notify.info("At end of block '%s', expected %s, loaded %s, duration=%s" % (self.blockName,
                                                                                                 expectedCount,
                                                                                                 loadedCount,
                                                                                                 now - self._loadStartT))
        return

    def abortBulkLoad(self):
        if self.inBulkBlock:
            Loader.Loader.notify.info("Aborting block ('%s')" % self.blockName)
            self.inBulkBlock = None
            self.loadingScreen.abort()
        return

    def tick(self):
        if self.inBulkBlock:
            now = globalClock.getRealTime()
            if now - self._lastTickT > self.TickPeriod:
                self._lastTickT += self.TickPeriod
                try:
                    base.cr.considerHeartbeat()
                except:
                    pass
                self.loadingScreen.tick()
            else:
                self.loadingScreen.tick(False)

    def loadModel(self, *args, **kw):
        ret = Loader.Loader.loadModel(self, *args, **kw)
        self.tick()
        return ret

    def loadFont(self, *args, **kw):
        ret = Loader.Loader.loadFont(self, *args, **kw)
        self.tick()
        return ret

    def loadTexture(self, texturePath: str, alphaPath: Optional[str] = None, okMissing: bool = False, readMipmaps: bool = False,
                    minfilter: Optional[SamplerState] = None, magfilter: Optional[SamplerState] = None, anisotropicDegree: Optional[int] = None,
                    loaderOptions: Optional[LoaderOptions] = None, multiview: Optional[bool] = None) -> Texture:

        ret = Loader.Loader.loadTexture(self, texturePath, alphaPath, readMipmaps, okMissing,
                                        minfilter, magfilter, anisotropicDegree, loaderOptions, multiview)
        self.tick()
        if alphaPath:
            self.tick()
        return ret

    def loadSfx(self, soundPath: str, manager: Optional[Union[str, AudioManager]] = 'master', positional: bool = False) -> AudioSound:
        if ClientSettings.MickeyModeEasterEgg.get():
            soundPath = 'phase_3/audio/dial/mickey.ogg'
        if isinstance(manager, str):
            manager = {
                'master': base.sfxMgrMaster,
                'dialog': base.sfxMgrDialog,
                'environment': base.sfxMgrEnvironment,
                'battle': base.sfxMgrBattle,
                'streetprops': base.sfxMgrStreetProps,
                'gui': base.sfxMgrGui
            }[manager]
        ret = Loader.Loader.loadSound(self, manager, soundPath, positional)
        self.tick()
        return ret

    def loadMusic(self, soundPath: Union[str, Tuple[str, ...]]) -> Union[AudioSound, List[AudioSound]]:
        if isinstance(soundPath, tuple):
            ret: List[AudioSound] = []
            for sound in soundPath:
                snd: AudioSound = self.loadMusic(sound)
                ret.append(snd)
            return ret

        ret: AudioSound = Loader.Loader.loadMusic(self, soundPath)

        # Check if there's extra info for this song
        # Currently this is only used to set loop points for audio
        _jsonPath = soundPath.replace('.ogg', '.json')
        if __debug__:
            # dev needs to point to the resource folder.
            _jsonPath = 'resources/'+_jsonPath

        if file.exists(_jsonPath):
            with file.open(_jsonPath, 'r') as _jsonFile:
                _jsonData = json.loads(_jsonFile.read())
                if 'loop_start' in _jsonData:
                    loopStart: float = _jsonData.get('loop_start')
                    if isinstance(loopStart, (int, float)):
                        ret.setLoopStart(loopStart)
                        self.notify.info(f'Setting loop start for {soundPath} to {loopStart}')
                    else:
                        self.notify.warning(f"Error getting loop start for {soundPath}. loop_start type was not a number. was {type(loopStart)}")
        else:
            self.notify.debug(f'No json file for {soundPath} ({_jsonPath})')

        self.tick()
        return ret

    def loadDNAFileAI(self, dnaStore, dnaFile):
        ret = loadDNAFileAI(dnaStore, dnaFile, CSDefault)
        self.tick()
        return ret

    def loadDNAFile(self, dnaStore, dnaFile):
        ret = loadDNAFile(dnaStore, dnaFile, CSDefault, 0)
        self.tick()
        return ret
