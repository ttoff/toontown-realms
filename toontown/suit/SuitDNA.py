import random
from typing import Dict

from panda3d.core import *
from direct.directnotify.DirectNotifyGlobal import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownTypes import CogAppearanceIndex
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from otp.avatar import AvatarDNA
notify = directNotify.newCategory('SuitDNA')
suitHeadTypes = ['f',
 'p',
 'ym',
 'mm',
 'ds',
 'hh',
 'cr',
 'tbc',
 'bf',
 'b',
 'dt',
 'ac',
 'bs',
 'sd',
 'le',
 'bw',
 'sc',
 'pp',
 'tw',
 'bc',
 'nc',
 'mb',
 'ls',
 'rb',
 'cc',
 'tm',
 'nd',
 'gh',
 'ms',
 'tf',
 'm',
 'mh',
 'sds',
 'head_honcho',
 'cold_heart',
 'the_racketeer',
 'hot_shot',
 'statue_telemarketer',
 'statue_bottom_feeder']
suitDepts = ['c',
 'l',
 'm',
 's']
suitDeptArgs2Dept = {
 # Bossbot
 'b': 'c',
 'bb': 'c',
 'boss': 'c',
 'bossbot': 'c',
 'corp': 'c',
 'corporate': 'c',
 # Lawbot
 'l': 'l',
 'lb': 'l',
 'law': 'l',
 'lawbot': 'l',
 'legal': 'l',
 # Cashbot
 'c': 'm',
 'cb': 'm',
 'cash': 'm',
 'cashbot': 'm',
 'money': 'm',
 # Sellbot
 's': 's',
 'sb': 's',
 'sell': 's',
 'sellbot': 's',
 'sales': 's'
}
suitDeptFullnames = {'c': TTLocalizer.Bossbot,
 'l': TTLocalizer.Lawbot,
 'm': TTLocalizer.Cashbot,
 's': TTLocalizer.Sellbot}
suitDeptFullnamesP = {'c': TTLocalizer.BossbotP,
 'l': TTLocalizer.LawbotP,
 'm': TTLocalizer.CashbotP,
 's': TTLocalizer.SellbotP}
suitsPerLevel = [1,
 1,
 1,
 1,
 1,
 1,
 1,
 1]
suitsPerDept = 8
goonTypes = ['pg', 'sg']
extraSuits = {
 'sds': 'c',
 'head_honcho': 'c',
 'cold_heart': 'l',
 'the_racketeer': 'm',
 'hot_shot': 's',
 'statue_telemarketer': 's',
 'statue_bottom_feeder': 'l'
}


def getSuitBodyType(cogType):
    return 'abc'[base.cr.dataPackMgr.getCogAppearance(cogType)[CogAppearanceIndex.BODY_TYPE]]


def getSuitDept(name):
    index = suitHeadTypes.index(name)
    if index < suitsPerDept:
        return suitDepts[0]
    elif index < suitsPerDept * 2:
        return suitDepts[1]
    elif index < suitsPerDept * 3:
        return suitDepts[2]
    elif index < suitsPerDept * 4:
        return suitDepts[3]
    elif name in extraSuits:
        return extraSuits.get(name)
    else:
        print(f'Unknown dept for suit name: {name}')
        return None
    return None


def getDeptFullname(dept):
    return suitDeptFullnames[dept]


def getDeptFullnameP(dept):
    return suitDeptFullnamesP[dept]


def getSuitDeptFullname(name):
    return suitDeptFullnames[getSuitDept(name)]


def getRandomSuitType(level, rng = random):
    return random.randint(max(level - 4, 1), min(level, 8))


def getRandomSuitByDept(dept):
    deptNumber = suitDepts.index(dept)
    return suitHeadTypes[suitsPerDept * deptNumber + random.randint(0, 7)]


class SuitDNA(AvatarDNA.AvatarDNA):

    def __init__(self, str = None, type = None, dna = None, r = None, b = None, g = None):
        if str != None:
            self.makeFromNetString(str)
        elif type != None:
            if type == 's':
                self.newSuit()
        else:
            self.type = 'u'

    def __str__(self):
        if self.type == 's':
            return 'type = %s\ndept = %s, name = %s' % ('suit',
             self.dept,
             self.name)
        elif self.type == 'b':
            return f'type = boss cog\ndept = {self.dept}'
        else:
            return 'type undefined'

    def makeNetString(self):
        dg = PyDatagram()
        dg.addFixedString(self.type, 1)
        if self.type == 's':
            dg.addString(self.name)
            dg.addFixedString(self.dept, 1)
        elif self.type == 'b':
            dg.addFixedString(self.dept, 1)
        elif self.type == 'u':
            notify.error('undefined avatar')
        else:
            notify.error(f'unknown avatar type: {self.type}')
        return dg.getMessage()

    def makeFromNetString(self, string):
        dg = PyDatagram(string)
        dgi = PyDatagramIterator(dg)
        self.type = dgi.getFixedString(1)
        if self.type == 's':
            self.name = dgi.getString()
            self.dept = dgi.getFixedString(1)
        elif self.type == 'b':
            self.dept = dgi.getFixedString(1)
        else:
            notify.error(f'unknown avatar type: {self.type}')
        return None

    def __defaultGoon(self):
        self.type = 'g'
        self.name = goonTypes[0]

    def __defaultSuit(self):
        self.type = 's'
        self.name = 'ds'
        self.dept = getSuitDept(self.name)

    def newSuit(self, name = None):
        if name is None:
            self.__defaultSuit()
        else:
            self.type = 's'
            self.name = name
            self.dept = getSuitDept(self.name)

    def newBossCog(self, dept):
        self.type = 'b'
        self.dept = dept

    def newSuitRandom(self, level = None, dept = None):
        self.type = 's'
        if level == None:
            level = random.choice(range(1, len(suitsPerLevel)))
        elif level < 0 or level > len(suitsPerLevel):
            notify.error(f'Invalid suit level: {level}')
        if dept is None:
            dept = random.choice(suitDepts)
        self.dept = dept
        index = suitDepts.index(dept)
        base = index * suitsPerDept
        offset = 0
        if level > 1:
            for i in range(1, level):
                offset = offset + suitsPerLevel[i - 1]

        bottom = base + offset
        top = bottom + suitsPerLevel[level - 1]
        self.name = suitHeadTypes[random.choice(range(bottom, top))]

    def newGoon(self, name = None):
        if type == None:
            self.__defaultGoon()
        else:
            self.type = 'g'
            if name in goonTypes:
                self.name = name
            else:
                notify.error(f'unknown goon type: {name}')

    def getType(self):
        if self.type == 's':
            type = 'suit'
        elif self.type == 'b':
            type = 'boss'
        else:
            notify.error(f'Invalid DNA type: {self.type}')
        return type
