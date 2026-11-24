from direct.fsm.FSM import FSM
from direct.interval.LerpInterval import LerpFunctionInterval
from panda3d.core import WindowProperties, MouseButton

from toontown.toonbase import ClientSettings

import sys


class CameraBase(FSM):

    def __init__(self, avatar):
        FSM.__init__(self, 'CameraBase')
        self._mouseActive = False
        self._inputEnabled = False
        self._mouseDelta = (0, 0)
        self._lastMousePos = (0, 0)
        self._mouseOrigin = (0, 0)
        self._isPageUp = 0
        self._isPageDown = 0
        self.avatar = avatar
        self.request('Inactive')

    def enterActive(self):
        self._inputEnabled = True
        self.accept('mouse3', self.startMouseControl)

        # If we are already holding down rmb when initializing, we can use that
        if base.mouseWatcherNode.isButtonDown(MouseButton.three()):
            self.startMouseControl()

    def exitActive(self):
        pass

    def enterInactive(self):
        self._inputEnabled = False
        self.stopMouseControl()
        self.ignore('mouse3')
        self.ignore('mouse3-up')

    def exitInactive(self):
        pass

    def startMouseControl(self):
        if self.getCurrentOrNextState() != 'Active':
            return
        if hasattr(base, 'oobeMode') and base.oobeMode:
            return
        self.ignore('mouse3')
        self.accept('mouse3-up', self.stopMouseControl)

        self._mouseActive = True

        mouseData = base.win.getPointer(0)
        # Save the cursor origin so we can set it back when we are done controllign
        self._mouseOrigin = int(mouseData.getX()), int(mouseData.getY())
        if sys.platform != 'win32':
            self._lastMousePos = int(mouseData.getX()), int(mouseData.getY())
        else:
            base.win.movePointer(0, base.win.getXSize() // 2, base.win.getYSize() // 2)
            self._lastMousePos = base.win.getXSize() // 2, base.win.getYSize() // 2

        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)
        base.graphicsEngine.openWindows()
        self._startMouseControl()

    def stopMouseControl(self):
        self.ignore('mouse3-up')
        self.ignore('mouse3')
        self.accept('mouse3', self.startMouseControl)

        if hasattr(base, 'oobeMode') and base.oobeMode:
            return

        if self._mouseActive:
            self._mouseActive = False
            self._stopMouseControl()

            base.win.movePointer(0, *self._mouseOrigin)
            props = WindowProperties()
            props.setCursorHidden(False)
            base.win.requestProperties(props)
            base.graphicsEngine.openWindows()

    def _startMouseControl(self):
        if self._mouseActive:
            # set thje mouse mode to relative
            props = WindowProperties()
            props.setMouseMode(WindowProperties.MRelative)
            base.win.requestProperties(props)
            self._startReadingMouse()
            self._startMouseUpdateTasks()

    def _stopMouseControl(self):
        props = WindowProperties()
        props.setMouseMode(WindowProperties.MAbsolute)
        base.win.requestProperties(props)
        self._stopReadingMouse()
        self._stopMouseUpdateTasks()

    def _startReadingMouse(self):
        self.addTask(self._mouseReadTask, 'mouseRead', sort = 47)

    def _stopReadingMouse(self):
        self.removeTask('mouseRead')

    def _startMouseUpdateTasks(self):
        """ start all the tasks needed """
        self.addTask(self._mouseUpdateTask, 'mouseUpdates', sort = 48)

    def _stopMouseUpdateTasks(self):
        self.removeTask('mouseUpdates')

    def _mouseReadTask(self, task):
        # Don't run this if we are in OOBE, or there's no cursor in the window
        if hasattr(base, 'oobeMode') and base.oobeMode:
            self._mouseDelta = (0, 0)
            return task.cont
        elif not base.mouseWatcherNode.hasMouse():
            self._mouseDelta = (0, 0)
            return task.cont

        # We have a mouse and aren't in oobe mode? Lets continue
        winSize = base.win.getXSize(), base.win.getYSize()
        mouseData = base.win.getPointer(0)
        # distance between current frame and last frame mouse positions
        self._mouseDelta = mouseData.getX() - self._lastMousePos[0], mouseData.getY() - self._lastMousePos[1]
        if sys.platform == 'win32':
            base.win.movePointer(0, winSize[0] // 2, winSize[1] // 2)
        mouseData = base.win.getPointer(0)
        # save this frame as the 'last' frame
        self._lastMousePos = mouseData.getX(), mouseData.getY()
        return task.cont

    def _mouseUpdateTask(self, task):
        """ Overwritten by subclasses """
        return task.cont

    def changePreset(self, direction: int):
        """ Overwritten by subclasses """
        pass

    def pageUp(self):
        """ Overwritten by subclasses """
        pass

    def pageDown(self):
        """ Overwritten by subclasses """
        pass

    def lerpCameraFov(self, fov: float, time: float, blendType: str = 'noBlend'):
        if hasattr(self, 'camLerpInterval'):
            self.camLerpInterval.finish()

        oldFov = base.camLens.getMinFov()
        if abs(fov - oldFov) > 0.1:

            def setCamFov(fov):
                base.camLens.setMinFov(fov)

            self.camLerpInterval = LerpFunctionInterval(setCamFov, fromData=oldFov, toData=fov, duration=time,
                                                        blendType = blendType, name='cam-fov-lerp')
            self.camLerpInterval.start()

    def attachCamera(self):
        """ Some cam modes (like orbital) will attach to other nodes, not avatar, some will tho
        this can be overridden by classes that need to attach to other nodes """
        camera.reparentTo(self.avatar)
        base.localAvatar.setCameraFov(ClientSettings.CameraFOV.get())

    @property
    def mouseActive(self) -> bool:
        return self._mouseActive
