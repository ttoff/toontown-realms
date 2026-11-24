import math
from typing import Optional

from direct.showbase.InputStateGlobal import inputState
from direct.showbase.PythonUtil import lerp
from panda3d.core import Vec3, CollisionTraverser, CollisionSegment, CollisionNode, BitMask32, CollisionHandlerQueue, \
    CollisionSphere, CollisionHandlerPusher, Point3, deg2Rad, CollisionEntry, NodePath, LVector3, Vec3F

from otp.camera.CameraBase import CameraBase
from otp.camera.CameraGlobals import *
from otp.otpbase.PythonUtil import bound
from toontown.toonbase import ClientSettings, HotkeySettings


class CameraEditor(CameraBase):
    CameraOffset: Vec3F = Vec3(0, -40, -45)

    def __init__(self, avatar):
        self.__initializedCollisions = False
        super().__init__(avatar)
        self.__lastPosWrtRender: Optional[Vec3F] = None
        self.__lastHprWrtRender: Optional[Vec3F] = None
        self.__cameraAttachPoint: NodePath = base.render.attachNewNode('__editorOrbitAttachPoint')
        self.__zoom: float = -40

    def enterActive(self):
        super().enterActive()
        self.attachCamera()
        self.__acceptHotkeys()
        self.addTask(self.__doCamUpdate, 'camUpdate', sort = 49)
        if (mover := self.avatar.controlManager.get('walk')) is not None:
            mover.setCameraLocked(True)

    def enterInactive(self):
        self.removeTask('camUpdate')
        self.__ignoreHotkeys()
        super().enterInactive()
        if (mover := self.avatar.controlManager.get('walk')) is not None:
            mover.setCameraLocked(False)

    def attachCamera(self):
        self.__cameraAttachPoint.setPos(0, 0, self.avatar.getHeight())
        self.__cameraAttachPoint.setP(CameraEditor.CameraOffset.z)
        base.camera.reparentTo(self.__cameraAttachPoint)
        base.localAvatar.setCameraFov(60)

        base.camera.setPosHpr(CameraEditor.CameraOffset.y, self.__getScaledDistance(CameraEditor.CameraOffset.y), 0,
                              0, 0, 0)

    def _mouseUpdateTask(self, task):
        """ this task happens every frame the user is holding the mouse down """
        if hasattr(base, 'oobeMode') and base.oobeMode:
            return task.cont

        if self._mouseDelta[0] or self._mouseDelta[1]:
            dx, dy = self._mouseDelta

            sensitivity = ClientSettings.CameraSensitivity.get() / 4
            self.__cameraAttachPoint.setH(self.__cameraAttachPoint, -dx * sensitivity)
            pitch = bound(self.__cameraAttachPoint.getP() + -dy * sensitivity, EDITOR_MIN_PITCH, EDITOR_MAX_PITCH)
            self.__cameraAttachPoint.setP(pitch)
            self.__cameraAttachPoint.setR(render, 0)

        return task.cont

    def startMouseControl(self):
        super().startMouseControl()

    def stopMouseControl(self):
        super().stopMouseControl()

    def __acceptHotkeys(self) -> None:
        self.accept('wheel_up', self.__handleWheelUp)
        self.accept(HotkeySettings.ZoomIn.getPressed(), self.__handleWheelUp)
        self.accept('wheel_down', self.__handleWheelDown)
        self.accept(HotkeySettings.ZoomOut.getPressed(), self.__handleWheelDown)

    def __ignoreHotkeys(self) -> None:
        self.ignore('wheel_up')
        self.ignore('wheel_down')
        self.ignore(HotkeySettings.ZoomIn.getPressed())
        self.ignore(HotkeySettings.ZoomOut.getPressed())

    def __handleWheelUp(self) -> None:
        self.__adjustZoom(1)

    def __handleWheelDown(self) -> None:
        self.__adjustZoom(-1)

    def __adjustZoom(self, offset: float):
        """ Adjust the zoom level """
        y = CameraEditor.CameraOffset.y
        y = bound(y + offset, EDITOR_MIN_ZOOM, EDITOR_MAX_ZOOM)
        CameraEditor.CameraOffset.setY(y)
        self.__zoom = y
        self.__setZoom(self.__zoom)

    def __setZoom(self, zoom: float):
        z = lerp(self.avatar.getHeight(), self.avatar.getHeight(), (-14 - zoom) / -12)
        self.__cameraAttachPoint.setZ(self.avatar, z)

    def __doCamUpdate(self, task):
        """ update camera """
        if hasattr(base, 'oobeMode') and base.oobeMode:
           return task.cont
        self.__cameraAttachPoint.setPos(self.avatar, Vec3(0, 0, lerp(self.avatar.getHeight(), self.avatar.getHeight(), (-14 - self.__zoom) / -12)))

        if self.__lastPosWrtRender == base.camera.getPos(base.render) and self.__lastHprWrtRender == base.camera.getHpr(base.render):
            return task.cont
        base.camera.setPos(CameraEditor.CameraOffset.x, self.__getScaledDistance(CameraEditor.CameraOffset.y), 0)
        base.camera.setHpr(Vec3(0))

        self.__lastPosWrtRender, self.__lastPosWrtRender = base.camera.getPos(render), base.camera.getHpr(render)

        return task.cont

    @staticmethod
    def isAvatarMoving() -> bool:
        if inputState.isSet('forward') or inputState.isSet('reverse') or inputState.isSet(
                'turnRight') or inputState.isSet('turnLeft') or inputState.isSet('slideLeft') or inputState.isSet(
                'slideRight'):
            return True
        else:
            return False

    def __getScaledDistance(self, distance: float) -> float:
        camHeight = self.avatar.getClampedAvatarHeight()
        heightScaleFactor = camHeight * 0.3333333333
        return distance * heightScaleFactor
