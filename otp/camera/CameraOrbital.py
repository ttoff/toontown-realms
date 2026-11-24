import math
from typing import Callable, Final

from direct.showbase.InputStateGlobal import inputState
from direct.showbase.PythonUtil import lerp, bound
from direct.task import Task
from panda3d.core import Vec3, CollisionTraverser, CollisionSegment, CollisionNode, BitMask32, CollisionHandlerQueue, \
    CollisionSphere, CollisionHandlerPusher, Point3, deg2Rad, CollisionEntry, NodePath

from otp.camera.CameraBase import CameraBase
from otp.camera.CameraGlobals import *
from otp.otpbase import OTPGlobals
from toontown.sandbox.DistributedPropGenerator import DistributedPropGenerator
from toontown.toonbase import ClientSettings, HotkeySettings

TURN_SMOOTHING: Final[float] = .8
SMOOTH_TURN_RATE: Final[float] = 15

class CameraOrbital(CameraBase):
    CameraOffset = Vec3(0, -9, 0)

    def __init__(self, avatar):
        self.__initializedCollisions = False
        super().__init__(avatar)
        # Optimization: Don't keep calculating collisions if the camera hasnt moved at all
        self.__lastPosWrtRender: Vec3 | None = None
        self.__lastHprWrtRender: Vec3 | None = None
        self.__cameraAttachPoint: NodePath = base.render.attachNewNode('__orbitAttachPoint')
        self.__lerpActive: bool = False

        self.__targetPitch: float | None = None

        self.__zoom: float = -9
        self.__targetZoom: float | None = None

        self.__presetIndex: int = 0

        self.__presetPositions: list[tuple[float, float]] = [
            (0, -9),
            (-40, -25),
            (-10, -25),
            (-18, -12),
        ]

    def enterActive(self):
        super().enterActive()
        self.removeAllTasks()
        if not self.__initializedCollisions:
            self.__initializeCollisions()
            self.avatar.cTrav.addCollider(self.__ccSphereNodePath, self.__camPusher)

        self.__recalcCameraSphere()
        self.attachCamera()
        self.__acceptHotkeys()

        self.addTask(self._realignCamera, 'realignCamera')

        self.addTask(self.__doCollisionCheck, 'collisionCheck', sort = 49)

    def enterInactive(self):
        self.removeAllTasks()
        self.__ignoreHotkeys()

        if self.__initializedCollisions:
            self.avatar.cTrav.removeCollider(self.__ccSphereNodePath)
            self.__deleteCollisions()
        super().enterInactive()


    def attachCamera(self):
        self.__cameraAttachPoint.setPos(0, 0, self.avatar.getHeight())
        self.__cameraAttachPoint.setH(self.avatar.getH() % 360)
        base.camera.reparentTo(self.__cameraAttachPoint)

        base.camera.setPosHpr(CameraOrbital.CameraOffset.x, self.__getScaledDistance(CameraOrbital.CameraOffset.y), 0,
                              0, 0, 0)

        base.localAvatar.setCameraFov(ClientSettings.CameraFOV.get())

    def _mouseUpdateTask(self, task):
        """ this task happens every frame the user is holding the mouse down """
        if hasattr(base, 'oobeMode') and base.oobeMode:
            return task.cont

        isMoving = self.isAvatarMoving() or base.localAvatar.isPresentingPie or DistributedPropGenerator.editorOpen
        if self._mouseDelta[0] or self._mouseDelta[1]:
            dx, dy = self._mouseDelta

            sensitivity = ClientSettings.CameraSensitivity.get() / 4
            self.__cameraAttachPoint.setH(self.__cameraAttachPoint, -dx * sensitivity)
            pitch = bound(self.__cameraAttachPoint.getP() + -dy * sensitivity, ORBIT_MIN_PITCH, ORBIT_MAX_PITCH)
            self.__cameraAttachPoint.setP(pitch)
            self.__cameraAttachPoint.setR(render, 0)
        return task.cont

    def __handleObstruction(self, node: CollisionEntry):
        """ handle an object in the way """
        if not node.hasSurfacePoint():
            return
        collisionPoint = node.getSurfacePoint(self.__cameraAttachPoint)

        base.camera.setPos(collisionPoint + node.getSurfaceNormal(self.__ccLineNodePath))

        # maybe???? makes the camera alwys looka t the toon but it can look weird
        # base.camera.lookAt(self.__cameraAttachPoint)
        # base.camera.setR(render, 0)

    def startMouseControl(self):
        super().startMouseControl()
        self.avatar.controlManager.get('walk').setCameraLocked(True)
        # self.avatar.controlManager.get('swim').setCameraLocked(True)

        self.__lerpActive = False

        self.removeTask('realignCamera')

    def stopMouseControl(self):
        super().stopMouseControl()
        if (mover := self.avatar.controlManager.get('walk')) is not None:
            mover.setCameraLocked(False)
        # if (swimMover := self.avatar.controlManager.get('swim')) is not None:
        #    swimMover.setCameraLocked(False)
        self.removeTask('realignCamera')

        self.addTask(self._realignCamera, 'realignCamera')

    def _realignCamera(self, task: Task.Task) -> int:
        if self._mouseActive:
            return task.cont
        if self.avatar.isEmpty():
            return task.done
        curr: float = self.__cameraAttachPoint.getH(base.render)
        target: float = self.avatar.getH(base.render) % 360
        if self.isAvatarMoving():
            self.__lerpActive = True
        if abs(curr - target) < .2:
            self.__lerpActive = False

        if __debug__:
            onScreenDebug.add('camOrbit lerpingH', f'{curr=} / {target=}')
        if not self.__lerpActive:
            return task.cont

        angleDiff = target - curr
        if angleDiff > 180:
            angleDiff -= 360
        elif angleDiff < -180:
            angleDiff += 360

        lerpRatio = 1 - pow(TURN_SMOOTHING, base.clock.getDt() * SMOOTH_TURN_RATE)
        result: float = curr + (angleDiff * lerpRatio)

        # Normalize the result to be between 0 and 360
        result %= 360
        self.__cameraAttachPoint.setH(result)
        return task.cont

    def realignCameraPitch(self, task: Task.Task) -> Callable[[], bool] | int | Callable[[], bool]:
        if self._mouseActive:
            self.__targetPitch = None
            self.__targetZoom = None
            return task.done

        lerpRatio: float = 1 - pow(TURN_SMOOTHING, base.clock.getDt() * SMOOTH_TURN_RATE)
        pitchDone: bool = True
        zoomDone: bool = True

        if self.__targetPitch is not None:
            curr = self.__cameraAttachPoint.getP()
            if __debug__:
                onScreenDebug.add('camOrbit reqPitch', f'{self.__targetPitch=} / {curr=}')
            diff = self.__targetPitch - curr
            if abs(diff) < .1:
                self.__cameraAttachPoint.setP(self.__targetPitch)
                self.__targetPitch = None
            else:
                self.__cameraAttachPoint.setP(curr + diff * lerpRatio)
                pitchDone = False

        if self.__targetZoom is not None:
            if __debug__:
                onScreenDebug.add('camOrbit reqPitch', f'{self.__targetPitch=} / {self.__zoom=}')
            diff = self.__targetZoom - self.__zoom
            if abs(diff) < .1:
                self.__zoom = self.__targetZoom
                self.__targetZoom = None
            else:
                self.__zoom += diff * lerpRatio
                zoomDone = False
            CameraOrbital.CameraOffset.setY(self.__zoom)

        return task.done if pitchDone and zoomDone else task.cont

    def setPitchAndZoom(self, pitch: float, zoom: float | None = None):
        if self._mouseActive:
            self.stopMouseControl()
        self.__targetPitch = pitch
        if zoom is not None:
            self.__targetZoom = zoom
        self.removeTask('requestedPitch')
        self.addTask(self.realignCameraPitch, 'requestedPitch')

    def __acceptHotkeys(self):
        self.accept('wheel_up', self.__handleWheelUp)
        self.accept(HotkeySettings.ZoomIn.getPressed(), self.__handleWheelUp)
        self.accept('wheel_down', self.__handleWheelDown)
        self.accept(HotkeySettings.ZoomOut.getPressed(), self.__handleWheelDown)
        self.accept(HotkeySettings.NextCameraView.getPressed(), self.__handleNextPreset)
        self.accept(HotkeySettings.PreviousCameraView.getPressed(), self.__handlePreviousPreset)
        self.accept(HotkeySettings.ResetCameraView.getPressed(), self.__resetToPreset)

    def __handleNextPreset(self):
        if self.__presetIndex+1 >= len(self.__presetPositions):
            self.__presetIndex = 0
        else:
            self.__presetIndex+=1
        self.setToPreset(*self.__presetPositions[self.__presetIndex])
        return

    def __handlePreviousPreset(self):
        if self.__presetIndex-1 <=0:
            self.__presetIndex = len(self.__presetPositions) - 1
        else:
            self.__presetIndex-=1
        self.setToPreset(*self.__presetPositions[self.__presetIndex])

    def __resetToPreset(self):
        self.setToPreset(*self.__presetPositions[self.__presetIndex])

    def setToPreset(self, pitch: float, zoom: float | None = None):
        self.removeTask('realignCamera')
        self.__lerpActive = True
        self.addTask(self._realignCamera, 'realignCamera')
        self.setPitchAndZoom(pitch, zoom)
        if __debug__:
            onScreenDebug.add('camOrbit preset', f'{pitch=} / {zoom=}')

    def __ignoreHotkeys(self):
        self.ignore('wheel_up')
        self.ignore('wheel_down')
        self.ignore(HotkeySettings.ZoomIn.getPressed())
        self.ignore(HotkeySettings.ZoomOut.getPressed())

    def __handleWheelUp(self):
        self.__adjustZoom(1)

    def __handleWheelDown(self):
        self.__adjustZoom(-1)

    def __adjustZoom(self, offset: float):
        """ Adjust the zoom level """
        y = CameraOrbital.CameraOffset.y
        y = bound(y + offset, ORBIT_MIN_ZOOM, ORBIT_MAX_ZOOM)
        CameraOrbital.CameraOffset.setY(y)
        self.__zoom = y
        self.__setZoom(self.__zoom)

    def __setZoom(self, zoom: float):
        z = lerp(self.avatar.getHeight(), self.avatar.getHeight(), (-14 - zoom) / -12)
        self.__cameraAttachPoint.setZ(self.avatar, z)

    def __doCollisionCheck(self, task: Task.Task) -> int:
        """ Check if the camera is obstructed and handle it """
        if hasattr(base, 'oobeMode') and base.oobeMode:
            return task.cont
        self.__recalcCameraSphere()
        self.__cameraAttachPoint.setPos(self.avatar, Vec3(0, 0, lerp(self.avatar.getHeight(), self.avatar.getHeight(), (-14 - self.__zoom) / -12)))

        if __debug__:
            onScreenDebug.add('camOrbit zoom', self.__zoom)
        base.camera.setPos(CameraOrbital.CameraOffset.x, self.__getScaledDistance(CameraOrbital.CameraOffset.y), 0)
        base.camera.setHpr(Vec3(0))
        if self.__lastPosWrtRender == base.camera.getPos(base.render) and self.__lastHprWrtRender == base.camera.getHpr(base.render):
            return task.cont
        self.__ccLine.setPointA(Vec3(0, 0, self.avatar.getHeight()))
        self.__ccLine.setPointB(base.camera.getPos(self.avatar))

        self.__ccTrav.traverse(base.render)

        if self.__camCollisionQueue.getNumEntries() > 0:
            self.__camCollisionQueue.sortEntries()
            self.__handleObstruction(self.__camCollisionQueue.getEntry(0))

        self.__lastPosWrtRender, self.__lastHprWrtRender = base.camera.getPos(base.render), base.camera.getHpr(base.render)
        return task.cont

    @staticmethod
    def isAvatarMoving() -> bool:
        if inputState.isSet('forward') or inputState.isSet('reverse') or inputState.isSet(
                'turnRight') or inputState.isSet('turnLeft') or inputState.isSet('slideLeft') or inputState.isSet(
            'slideRight'):
            return True
        else:
            return False

    def __initializeCollisions(self):
        self.__initializedCollisions = True

        # setup camera collision traverser
        # we need this because normal collisions get handled just before
        # rendering. using the normal collision mechanisms would introduce
        # one frame of lag in the smart camera, allowing the camera to pop
        # through walls momentarily.
        self.__ccTrav = CollisionTraverser('CameraOrbital.ccTrav')

        # Set up the camera obstruction test line segment
        # This is a line segment from the visibility point to the ideal
        # camera location
        self.__ccLine = CollisionSegment(0.0, 0.0, 0.0, 0, -20, 0.0)
        self.__ccLineNode = CollisionNode('CameraOrbital.ccLineNode')
        self.__ccLineNode.addSolid(self.__ccLine)
        self.__ccLineNodePath = self.avatar.attachNewNode(self.__ccLineNode)
        # self.__ccLineNodePath.show()
        self.__ccLineNode.setFromCollideMask(OTPGlobals.CameraBitmask |
                                             OTPGlobals.CameraTransparentBitmask |
                                             OTPGlobals.FloorBitmask)
        self.__ccLineNode.setIntoCollideMask(BitMask32.allOff())

        self.__camCollisionQueue = CollisionHandlerQueue()

        self.__ccTrav.addCollider(self.__ccLineNodePath, self.__camCollisionQueue)

        # sphere to keep it away from walls
        # sphere radius n shit will be calculated later based on fov n stuff
        self.__ccSphere = CollisionSphere(0, 0, 0, 1)
        self.__ccSphereNode = CollisionNode('CameraOrbital.ccSphereNode')
        self.__ccSphereNode.addSolid(self.__ccSphere)
        self.__ccSphereNodePath = base.camera.attachNewNode(self.__ccSphereNode)
        # self.__ccSphereNodePath.show()
        self.__ccSphereNode.setFromCollideMask(OTPGlobals.CameraBitmask |
                                               OTPGlobals.CameraTransparentBitmask |
                                               OTPGlobals.FloorBitmask)
        self.__ccSphereNode.setIntoCollideMask(BitMask32.allOff())

        self.__camPusher = CollisionHandlerPusher()
        self.__camPusher.addCollider(self.__ccSphereNodePath, base.camera)
        self.__camPusher.addCollider(self.__ccLineNodePath, base.camera)
        self.__ccTrav.addCollider(self.__ccSphereNodePath, self.__camCollisionQueue)

        self.__camPusher.setCenter(self.avatar)

        self.__ccPusherTrav = CollisionTraverser("CameraOrbital.ccPusherTrav")
        ##self.__ccPusherTrav.showCollisions(render)

    def __deleteCollisions(self):
        self.__initializedCollisions = False
        del self.__ccTrav
        del self.__ccLine

        del self.__ccLineNode
        self.__ccLineNodePath.removeNode()
        del self.__ccLineNodePath
        del self.__camCollisionQueue

        del self.__ccSphere
        del self.__ccSphereNode
        self.__ccSphereNodePath.removeNode()
        del self.__ccSphereNodePath

        del self.__camPusher
        del self.__ccPusherTrav

    def __recalcCameraSphere(self):
        """ this will adjust the smart camera for new FOV/near plane settings"""
        # get the near-plane params
        nearPlaneDist = base.camLens.getNear()
        hFov = base.camLens.getHfov()
        vFov = base.camLens.getVfov()

        hOff = nearPlaneDist * math.tan(deg2Rad(hFov / 2.))
        vOff = nearPlaneDist * math.tan(deg2Rad(vFov / 2.))

        # average the points together to get the sphere center
        camPnts = [Point3(hOff, nearPlaneDist, vOff),
                   Point3(-hOff, nearPlaneDist, vOff),
                   Point3(hOff, nearPlaneDist, -vOff),
                   Point3(-hOff, nearPlaneDist, -vOff),
                   Point3(0.0, 0.0, 0.0)]

        avgPnt = Point3(0.0, 0.0, 0.0)
        for camPnt in camPnts:
            avgPnt += camPnt
        avgPnt /= len(camPnts)

        # calculate a minimum bounding sphere
        sphereRadius = 0.0
        for camPnt in camPnts:
            dist = Vec3(camPnt - avgPnt).length()
            if dist > sphereRadius:
                sphereRadius = dist

        # set the new sphere params
        avgPnt = Point3(avgPnt)
        self.__ccSphereNodePath.setPos(avgPnt)
        self.__ccSphere.setRadius(sphereRadius)

    def __getScaledDistance(self, distance: float) -> float:
        camHeight = self.avatar.getClampedAvatarHeight()
        heightScaleFactor = camHeight * 1./3.
        return distance * heightScaleFactor
