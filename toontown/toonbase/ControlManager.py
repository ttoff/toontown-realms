import re
import warnings
from typing import Dict, List, Type

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject

from otp.otpbase import OTPLocalizer

from toontown.toonbase import ToontownGlobals, HotkeySettings

import string
import sys

from toontown.toonbase.HotkeySettings import HotkeySetting


class ControlManager(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('ControlManager')
    KeyStringToSetting: Dict[str, Type[HotkeySetting]] = {}

    def __init__(self):
        DirectObject.__init__(self)
        self.changing = False
        self.disableChat = 1
        self.disabledHotkeys = []
        self.activeHotkeys = []
        self.changedHotkeys = {ToontownGlobals.HotkeyMovement: [],
                               ToontownGlobals.HotkeyInteraction: [],
                               ToontownGlobals.HotkeyDebug: [],
                               ToontownGlobals.HotkeyMisc: []}
        self.disableAlphaNumericHotkeys = False
        self.reloadHotkeys(True)

        for key in HotkeySettings.getAllHotkeys():
            ControlManager.KeyStringToSetting[key.getSettingString()] = key

    def reloadHotkeys(self, realtime=False):
        self.ignoreAll()
        disableChat = 1
        activeHotkeys = []

        allKeys: List[Type[HotkeySetting]] = HotkeySettings.getAllHotkeys()

        for key in allKeys:
            boundKey = key.get()
            isAlphaNumeric: bool = self.isAlphaNumericHotkey(boundKey)
            if disableChat and isAlphaNumeric:
                disableChat = False
            activeHotkeys.append(boundKey)
            self.accept(boundKey, self.hotkeyPressed, extraArgs = [key.getPressed(), boundKey, key])
            self.accept(f'{boundKey}-up', self.hotkeyPressed, extraArgs = [key.getReleased(), boundKey, key])

            for modifier in ('control', 'alt', 'shift'):
                if not self.getKeyInUse(f'{modifier}-{boundKey}'):
                    self.accept(f'{modifier}-{boundKey}', self.hotkeyPressed, extraArgs = [key.getPressed(), boundKey, key])
                    self.accept(f'{modifier}-{boundKey}-up', self.hotkeyPressed, extraArgs = [key.getReleased(), boundKey, key])
        self.disableChat = disableChat
        self.activeHotkeys = activeHotkeys
        if hasattr(base, 'localAvatar') and hasattr(base.localAvatar, 'chatMgr') and base.localAvatar.chatMgr:
            base.localAvatar.chatMgr.setBackgroundFocus(disableChat, realtime)

    def setChanging(self, state):
        self.changing = state

    def getChanging(self):
        return self.changing

    def hotkeyPressed(self, hotkeyName, hotkey, key, event=None):
        self.notify.info(hotkeyName)
        if not self.getChanging() and key not in self.disabledHotkeys:
            if self.disableAlphaNumericHotkeys:
                if 'enter' in hotkey:
                    messenger.send('exitChat')
                    return
                elif not self.isAlphaNumericHotkey(hotkey):
                    messenger.send(hotkeyName)
                    return
                elif hotkeyName.endswith('-up'):
                    messenger.send(hotkeyName)
                    return
                else:
                    return
            messenger.send(hotkeyName)

    def getKeyName(self, category: str, hotkey: int) -> str:
        controlCategory: Dict = base.settings.getOption('keybinds', category, {})
        categoryInd = ToontownGlobals.Hotkeys.index(category)
        defaultDict = getattr(ToontownGlobals, 'Hotkey' + ToontownGlobals.Hotkeys[categoryInd].capitalize() + 'Defaults')
        return controlCategory.get(base.controlManager.parseHotkey(category, hotkey), defaultDict[hotkey])

    @staticmethod
    def getControlName(name, label=False):
        if not name:
            name = ToontownGlobals.InvalidKey
            return name

        if ToontownGlobals.Separator in name:
            name = name.replace(ToontownGlobals.Separator, ' + ')

        for key in ToontownGlobals.SpecialKeys.keys():
            if key in name:
                value = ToontownGlobals.SpecialKeys.get(key)
                if type(value) is list:
                    if not sys.platform == 'darwin':
                        # Windows/Linux
                        value = value[0]
                    else:
                        # macOS
                        value = value[1]
                name = name.replace(key, value)
                break

        name = name.title()

        if label:
            name += ' Key'
            if '+' in name:
                name += 's'

        return name

    @staticmethod
    def parseHotkeyString(baseString: str, label: bool = False, useGlyphs = False) -> str:
        pattern = r'\$\$(.*?)\$\$'

        def replace(match):
            key = match.group(1)
            keySetting: Type[HotkeySetting] = ControlManager.KeyStringToSetting.get('s' + key, None)
            if keySetting is None:
                return f'#UNKNOWN_HOTKEY_{key}'

            if useGlyphs:
                return f'\x01white\x01\5kbm_{keySetting.get().lower()}\5\x02'
            else:
                return ControlManager.getControlName(keySetting.get(), label)

        return re.sub(pattern, replace, baseString)


    def isAlphaNumericHotkey(self, hotkey):
        for prefix in ('shift', 'control', 'alt'):
            if prefix in hotkey:
                hotkey = hotkey.replace(prefix, '')
                if ToontownGlobals.Separator in hotkey:
                    hotkey = hotkey.replace(ToontownGlobals.Separator, '')
                else:
                    return False

        if len(hotkey) > 1:
            if hotkey == 'space':
                return True
            return False

        characters = string.printable
        if hotkey in characters:
            return True

        return False

    def getChatDisabled(self):
        return self.disableChat

    def addDisabledHotkey(self, category, hotkey):
        if type(hotkey) == int:
            hotkey = self.parseHotkey(category, hotkey)

        if hotkey not in self.disabledHotkeys:
            self.disabledHotkeys.append(hotkey)

    def removeDisabledHotkey(self, category, hotkey):
        if type(hotkey) == int:
            hotkey = self.parseHotkey(category, hotkey)

        if hotkey in self.disabledHotkeys:
            self.disabledHotkeys.remove(hotkey)

    def parseHotkey(self, category, hotkey):
        if type(hotkey) != int:
            return hotkey

        if type(category) != int:
            category = ToontownGlobals.Hotkeys.index(category)

        hotkeyNames = OTPLocalizer.HotkeyNames[category]
        hotkey = hotkeyNames.get(hotkey)
        hotkey = hotkey.lower().replace(' ', '-')

        return hotkey

    def getKeyInUse(self, hotkey):
        for key in self.activeHotkeys:
            if hotkey in key:
                return True
        return False
