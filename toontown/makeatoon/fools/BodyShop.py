"""BodyShop module: contains the BodyShop class"""

from panda3d.core import Vec3

from toontown.datapack.DataPackManager import DataPackManager
from toontown.suit import SuitDNA
from direct.fsm import StateData
from direct.gui.DirectGui import *
from toontown.makeatoon.MakeAToonGlobals import *
from toontown.toonbase import TTLocalizer, ToontownGlobals
from direct.directnotify import DirectNotifyGlobal
from toontown.makeatoon import ShuffleButton
from toontown.toonbase.ToontownTypes import CogAppearanceIndex

speciesFrameHalfButtonScale = Vec3(halfButtonScale) * 1.5
speciesFrameHalfButtonHoverScale = Vec3(halfButtonHoverScale) * 1.5
speciesFrameHalfButtonInvertScale = Vec3(halfButtonInvertScale) * 1.5
speciesFrameHalfButtonInvertHoverScale = Vec3(halfButtonInvertHoverScale) * 1.5


class BodyShop(StateData.StateData):
    """
    BodyShop class: contains methods for changing the Avatar's
    suit type via user input
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('BodyShop')

    def __init__(self, doneEvent):
        """
        Set-up the body shop interface to change body parts on the
        given toon
        """
        StateData.StateData.__init__(self, doneEvent)
        self.toon = None
        self.typeChoice = 0

    def enter(self, toon):
        # turn off any user control
        base.disableMouse()

        # load up the given toon
        self.toon = toon
        self.dna = self.toon.getStyle()

        self.typeStart = SuitDNA.suitHeadTypes.index(self.dna.name)
        self.typeChoice = self.typeStart

        self.__swapType(0)

        choicePool = [SuitDNA.suitHeadTypes]
        self.shuffleButton.setChoicePool(choicePool)
        self.accept(self.shuffleFetchMsg, self.changeBody)

        # set up the "last" button
        self.acceptOnce('last', self.__handleBackward)
        # set up the "next" button
        self.accept('next', self.__handleForward)
        self.acceptOnce('MAT-newToonCreated', self.shuffleButton.cleanHistory)

    def showButtons(self):
        self.parentFrame.show()

    def hideButtons(self):
        self.parentFrame.hide()

    def exit(self):
        """
        Remove events and restore display
        """
        try:
            del self.toon
        except AttributeError:
            self.notify.warning('BodyShop: toon not found')

        self.hideButtons()
        self.ignore('last')
        self.ignore('next')
        self.ignore('enter')
        self.ignore(self.shuffleFetchMsg)

    def load(self):
        self.gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        shuffleFrame = self.gui.find('**/tt_t_gui_mat_shuffleFrame')
        shuffleArrowUp = self.gui.find('**/tt_t_gui_mat_shuffleArrowUp')
        shuffleArrowDown = self.gui.find('**/tt_t_gui_mat_shuffleArrowDown')
        shuffleArrowRollover = self.gui.find('**/tt_t_gui_mat_shuffleArrowUp')
        shuffleArrowDisabled = self.gui.find('**/tt_t_gui_mat_shuffleArrowDisabled')
        self.parentFrame = DirectFrame(relief=DGG.RAISED, parent=base.a2dTopRight, pos=(-0.353333, 0, -0.584), frameColor=(1, 0, 0, 0))
        self.speciesFrame = DirectFrame(parent=self.parentFrame, image=shuffleFrame, image_scale=speciesFrameHalfButtonInvertScale, relief=None, pos=(-0.15, 0, -0.073), hpr=(0, 0, 0), scale=1.3, frameColor=(1, 1, 1, 1), text=TTLocalizer.BodyShopSpeciesFools, text_font=ToontownGlobals.getSuitFont(), text_wordwrap=6, text_scale=0.0625, text_pos=(-0.001, 0.015), text_fg=(1, 1, 1, 1))
        self.speciesLButton = DirectButton(parent=self.speciesFrame, relief=None, image=(shuffleArrowUp,
         shuffleArrowDown,
         shuffleArrowRollover,
         shuffleArrowDisabled), image_scale=speciesFrameHalfButtonScale, image1_scale=speciesFrameHalfButtonHoverScale, image2_scale=speciesFrameHalfButtonHoverScale, pos=(-0.3, 0, 0), command=self.__swapType, extraArgs=[-1])
        self.speciesRButton = DirectButton(parent=self.speciesFrame, relief=None, image=(shuffleArrowUp,
         shuffleArrowDown,
         shuffleArrowRollover,
         shuffleArrowDisabled), image_scale=speciesFrameHalfButtonInvertScale, image1_scale=speciesFrameHalfButtonInvertHoverScale, image2_scale=speciesFrameHalfButtonInvertHoverScale, pos=(0.3, 0, 0), command=self.__swapType, extraArgs=[1])
        self.parentFrame.hide()
        self.shuffleFetchMsg = 'BodyShopShuffle'
        self.shuffleButton = ShuffleButton.ShuffleButton(self, self.shuffleFetchMsg)
        self.shuffleButton.shuffleBtn['text_font'] = ToontownGlobals.getSuitFont()
        self.shuffleButton.shuffleBtn['text_scale'] = TTLocalizer.SBshuffleBtn * 0.8
        return

    def unload(self):
        self.gui.removeNode()
        del self.gui
        self.parentFrame.destroy()
        self.speciesFrame.destroy()
        self.speciesLButton.destroy()
        self.speciesRButton.destroy()
        del self.parentFrame
        del self.speciesFrame
        del self.speciesLButton
        del self.speciesRButton
        self.shuffleButton.unload()
        self.ignore('MAT-newToonCreated')

    # event handlers

    def __swapType(self, offset):
        length = len(SuitDNA.suitHeadTypes)
        self.typeChoice = (self.typeChoice + offset) % length
        self.__updateScrollButtons(self.typeChoice, length, self.typeStart, self.speciesLButton, self.speciesRButton)
        suitType = SuitDNA.suitHeadTypes[self.typeChoice]
        self.__changeTypeName(suitType)
        # Change suit type
        self.dna.name = suitType
        # And finally, change the department
        self.dna.dept = SuitDNA.getSuitDept(suitType)
        self.toon.setDNA(self.dna)
        # tell MAT to move update the camera height
        messenger.send('mat-toon-updated')

    def __updateScrollButtons(self, choice, length, start, lButton, rButton):
        # ghost the pickers if at the end of the 'wheel'
        if choice == (start - 1) % length:
            rButton['state'] = DGG.DISABLED
        elif choice != (start - 1) % length:
            rButton['state'] = DGG.NORMAL
        if choice == start % length:
            lButton['state'] = DGG.DISABLED
        elif choice != start % length:
            lButton['state'] = DGG.NORMAL

        # RAU guard code against both buttons getting disabled, unable to reproduce, but
        # screen shot shows it can happen,  bug 15281
        if lButton['state'] == DGG.DISABLED and rButton['state'] == DGG.DISABLED:
            self.notify.info('Both buttons got disabled! Doing fallback code. choice%d, length=%d, start=%d, lButton=%s, rButton=%s' % (choice,
             length,
             start,
             lButton,
             rButton))
            if choice == start % length:
                lButton['state'] = DGG.DISABLED
                rButton['state'] = DGG.NORMAL
            elif choice == (start - 1) % length:
                lButton['state'] = DGG.NORMAL
                rButton['state'] = DGG.DISABLED
            else:
                lButton['state'] = DGG.NORMAL
                rButton['state'] = DGG.NORMAL

    def __handleForward(self):
        self.doneStatus = 'next'
        messenger.send(self.doneEvent)

    def __handleBackward(self):
        self.doneStatus = 'last'
        messenger.send(self.doneEvent)

    def changeBody(self):
        newChoice = self.shuffleButton.getCurrChoice()
        newSuitType = newChoice[0]
        newSuitTypeIndex = SuitDNA.suitHeadTypes.index(newSuitType)
        oldSuitType = self.toon.style.name
        oldSuitTypeIndex = SuitDNA.suitHeadTypes.index(oldSuitType)
        self.__swapType(newSuitTypeIndex - oldSuitTypeIndex)

    def getCurrToonSetting(self):
        return [self.toon.style.name]

    def __changeTypeName(self, suitType):
        try:
            self.speciesFrame['text'] = DataPackManager.getLocalizedText(base.cr.dataPackMgr.getCogAppearance(suitType)[CogAppearanceIndex.NAME])
        except IndexError:
            self.notify.error('Invalid suitType %s' % suitType)
