# HotkeySettings
# Created by drewc Apr 22 2024
import os
import platform
import sys
from enum import IntEnum
from typing import List, Type

from otp.camera.CameraGlobals import CameraMode
from otp.settings.TOMLSettings import TOMLSettings
from toontown.social.SocialGlobals import ELoginPopupTypes, ETeleportRequestTypes
from toontown.toonbase.SettingsBase import SettingsCategory, FloatSetting, BoolSetting, IntegerSetting, StringSetting, EnumSetting, ListSetting, SettingBase


class HotkeySettingsMgr(TOMLSettings):
    globalSettings = None

    def __init__(self):
        TOMLSettings.__init__(self, 'hotkeys.toml')
        self.settings = []


HotkeySettingsManager = HotkeySettingsMgr()

""" Movement """


class HotkeySetting(StringSetting):

    def getPressed(self) -> str:
        return f'hotkey-{self.getSettingString()}'

    def getReleased(self) -> str:
        return f'hotkey-{self.getSettingString()}-up'


# == MOVEMENT ==
MoveForward = HotkeySetting(
    "MoveForward",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MOVEMENT,
    default = 'w'
)

MoveBackward = HotkeySetting(
    "MoveBackward",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MOVEMENT,
    default = 's'
)

MoveLeft = HotkeySetting(
    "MoveLeft",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MOVEMENT,
    default = 'a'
)

MoveRight = HotkeySetting(
    "MoveRight",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MOVEMENT,
    default = 'd'
)

Jump = HotkeySetting(
    "Jump",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MOVEMENT,
    default = 'space'
)

Action = HotkeySetting(
    "Action",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MOVEMENT,
    default = 'e'
)

FlyDescend = HotkeySetting(
    "FlyDescend",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MOVEMENT,
    default = 'control'
)

# == INTERACTION ==
ToggleBook = HotkeySetting(
    "ToggleBook",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_INTERACTION,
    default = 'b'
)

ExitActivity = HotkeySetting(
    "ExitActivity",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_INTERACTION,
    default = 'escape'
)

PeekTasks = HotkeySetting(
    "PeekTasks",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_INTERACTION,
    default = 'o'
)

PeekInventory = HotkeySetting(
    "PeekInventory",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_INTERACTION,
    default = 'i'
)

ToggleSocialMenu = HotkeySetting(
    "ToggleSocialMenu",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_INTERACTION,
    default = 'p'
)

ToggleMiniMap = HotkeySetting(
    "ToggleMiniMap",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_INTERACTION,
    default = 'm'
)

ToggleMagicMenu = HotkeySetting(
    "ToggleMagicMenu",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_INTERACTION,
    default = 'meta' if sys.platform == 'darwin' else 'insert'
)

TakeScreenshot = HotkeySetting(
    "TakeScreenshot",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_INTERACTION,
    default = 'f9'
)

Chat = HotkeySetting(
    "Chat",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_INTERACTION,
    default = 't'
)

Interact = HotkeySetting(
    "Interact",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_INTERACTION,
    default = 'f'
)

# == MISC ==
NextCameraView = HotkeySetting(
    "NextCameraView",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MISC,
    default = 'tab'
)

PreviousCameraView = HotkeySetting(
    "PreviousCameraView",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MISC,
    default = 'shift-tab'
)

ResetCameraView = HotkeySetting(
    "ResetCameraView",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MISC,
    default = 'control-tab'
)

CameraModeMenu = HotkeySetting(
    "CameraModeMenu",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MISC,
    default = 'f5'
)

ZoomIn = HotkeySetting(
    "ZoomIn",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MISC,
    default = 'page_up'
)

ZoomOut = HotkeySetting(
    "ZoomOut",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MISC,
    default = 'page_down'
)

ToggleNametagVisibility = HotkeySetting(
    "ToggleNametagVisibility",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MISC,
    default = 'f2'
)

ToggleMarginVisibility = HotkeySetting(
    "ToggleMarginVisibility",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MISC,
    default = 'f3'
)

ToggleOobeCamera = HotkeySetting(
    "ToggleOobeCamera",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MISC,
    default = 'f4'
)

PropGeneratorRotateModifier = HotkeySetting(
    "PropGeneratorRotateModifier",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MISC,
    default = 'z'
)

PropGeneratorDecreaseGridSize = HotkeySetting(
    "PropGeneratorDecreaseGridSize",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MISC,
    default = '['
)

PropGeneratorIncreaseGridSize = HotkeySetting(
    "PropGeneratorIncreaseGridSize",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MISC,
    default = ']'
)

PropGeneratorPreviousProp = HotkeySetting(
    "PropGeneratorPreviousProp",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MISC,
    default = 'mouse4'
)

PropGeneratorNextProp = HotkeySetting(
    "PropGeneratorNextProp",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_MISC,
    default = 'mouse5'
)

# == DEBUG ==
ToggleDebugOverlay = HotkeySetting(
    "ToggleDebugOverlay",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_DEBUG,
    default = 'shift-f1'
)

DebugFacility = HotkeySetting(
    "DebugFacility",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_DEBUG,
    default = 'shift-f2'
)

ToggleTaskMgrOverlay = HotkeySetting(
    "ToggleTaskMgrOverlay",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_DEBUG,
    default = 'shift-control-f1'
)

ToggleIvalOverlay = HotkeySetting(
    "ToggleIvalOverlay",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_DEBUG,
    default = 'shift-control-f2'
)

DebugSync = HotkeySetting(
    "DebugSync",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_DEBUG,
    default = 'shift-f6'
)

DebugGarbageCollector = HotkeySetting(
    "DebugGarbageCollector",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_DEBUG,
    default = 'shift-f11'
)

DebugCamera = HotkeySetting(
    "DebugCamera",
    settingsFile = HotkeySettingsManager,
    category = SettingsCategory.HOTKEY_DEBUG,
    default = 'shift-f12'
)


def getAllHotkeys() -> List[HotkeySetting]:
    keys = []
    for item in list(globals().values()):
        if isinstance(item, HotkeySetting):
            if item.settingsFile is None:
                continue
            keys.append(item)
    return keys


for hk in getAllHotkeys():
    HotkeySettingsManager.settings.append(hk)
