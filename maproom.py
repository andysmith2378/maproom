from copy import copy
from math import sqrt
from sets import Set
from datetime import timedelta, datetime
from landmarks import landmarkDict, cityDict, bridgeDict
import cPickle, heapq, pygame

class AdoptionType(type):
    classIndex             = {}
    _reduceMethodKey       = '_reduceMethod'
    _reduceArgumentsKey    = '_reduceArgs'
    _adoptionDictionaryKey = '_adoptionDictionary'
    _keyAttribute          = 'colour'

    def _adopt(cls, methodName, adoptFrom, reduceMethod, reduceArgs):
        adoptionMethod = getattr(adoptFrom, methodName)
        if callable(adoptionMethod) and not isinstance(adoptionMethod, type):
            def adoptedMethod(firstAdoptionType, secondAdoptionType):
                return getattr(adoptFrom, methodName)(reduce(reduceMethod, 
                    [getattr(firstAdoptionType, arg) for arg in reduceArgs]), 
                    reduce(reduceMethod, [getattr(secondAdoptionType, arg) for 
                    arg in reduceArgs]))
            setattr(cls, methodName, adoptedMethod)
    
    def _getAdoptDict(cls):
        if cls.__dict__.has_key(AdoptionType._adoptionDictionaryKey):
            return cls.__dict__
        return cls.__base__._getAdoptDict()
        
    def _getKeyAttrib(cls):
        if hasattr(cls, AdoptionType._keyAttribute):
            return getattr(cls, AdoptionType._keyAttribute)
        if hasattr(cls.__base__, cls._getKeyAttrib.__name__):
            return cls.__base__._getKeyAttrib()
        return None    
    
    def __init__(cls, identity, bases, dictionary):
        adoptDict = cls._getAdoptDict()
        keyAt     = cls._getKeyAttrib()
        [cls._adopt(methodName, adoptFrom, adoptDict[
            AdoptionType._reduceMethodKey], adoptDict[
            AdoptionType._reduceArgumentsKey]) for methodName, adoptFrom in 
            adoptDict[AdoptionType._adoptionDictionaryKey].items()]
        if keyAt is not None and not AdoptionType.classIndex.has_key(keyAt):
            AdoptionType.classIndex[keyAt] = cls



class Position(object):
    def __init__(self, coords):
        if isinstance(coords, str):
            if Unit.landmarks.has_key(coords):
                self.coordinates = Unit.landmarks[coords]
            else:
                print "Unknown landmark. For a list of all landmarks, type 'Unit.showLandmarks()'"
                raise ValueError
        elif isinstance(coords, tuple) or isinstance(coords, list):
            self.coordinates = coords
        else:
            print "coordinates should be the name of a landmark, a tuple or a list"
            raise TypeError
   
    

class Land(list, Position):
    __metaclass__       = AdoptionType
    _defaultEst         = 1.0
    _shownJunc          = []
    _shownLand          = []
    _reduceMethod       = float.__add__
    _reduceArgs         = ['meanCost', 'estimate']
    _adoptionDictionary = {'__eq__': float, '__lt__': float, '__le__': float,
        '__gt__': float, '__ge__': float, '__ne__': float, '__add__': float, 
        '__sub__': float, '__div__': float, '__mul__': float, '__mod__': float,
        '__floordiv__': float, '__truediv__': float, '__radd__': float, 
        '__rsub__': float, '__rdiv__': float, '__rmul__': float, '__rmod__': 
        float, '__rtruediv__': float, '__rfloordiv__': float}
        
    def __new__(cls, neighboursList=[], coords=None, defaultCost=_defaultEst):
        result          = list.__new__(cls, neighboursList)
        defaultJunction = Junction(defaultCost, result)
        if neighboursList is not []:
            [list.append(neighbour.land, defaultJunction) for neighbour in 
                neighboursList if (isinstance(neighbour.land, list)) and 
                (result not in neighbour.land)]                  
        return result        

    def __init__(self, neighboursList, coords=None, defaultCost=_defaultEst,
        elevation=None):
        list.__init__(self, neighboursList)
        Position.__init__(self, coords)
        self._defaultCost = defaultCost
        self.elevation    = elevation
        self.estimateSet  = False
        self.pathCostSet  = False
        self.treeParent   = None
        
    def junctionTo(self, land):
        return [junct for junct in self if junct.land is land][0]
        
    def __contains__(self, land):
        return land in self.neighbourhood
        
    def append(self, neighbour):
        if isinstance(neighbour, Junction):
            list.append(neighbour)
            if self not in neighbour.land.neighbourhood:
                neighbour.Land.append(self)
        elif isinstance(neighbour, list):
            defaultJunction = Junction(self._defaultCost, neighbour)
            self.append(defaultJunction)
    
    def remove(self, neighbour):
        if isinstance(neighbour, Junction):
            if list.__containts__(self, neighbour):
                list.remove(self, neighbour)
                self._leaveNeighbourhood(neighbour)
        elif neighbour in self:
            for junction in copy(self):
                if junction.Land == neighbour:
                    list.remove(self, junction)
            self._leaveNeighbourhood(neighbour)
    
    def __delitem__(self, indx):
        list.__delitem__(self, indx)
        self._leaveNeighbourhood(self[indx])

    def _leaveNeighbourhood(self, neighbourJunction):
        if self in neighbourJunction.Land.neighbourhood:
            for junction in copy(neighbourJunction.Land):
                if junction.land == self:
                    neighbourJunction.land.remove(junction)
    
    def _uniqueStrings(self):
        juncList = []
        landList = []
        for junct in self:
            if junct not in juncList and junct not in Land._shownJunc:
                Land._shownJunc.append(junct)
                juncList.append(junct)
                land = junct.land
                if land not in landList and land not in Land._shownLand:
                    juncList.append(junct)
                    landList.append(land)                   
        return juncList, landList    
    
    def _uniqueMembers(self):
        return self._uniqueStrings()[0]
        
    def _uniqueNeighbourhood(self):
        return self._uniqueStrings()[1]        
    
    def _costLine(self):
        return "  ".join(['mean cost ', str(self.meanCost)])
        
    def _estLine(self):
        return "  ".join(['estimate  ', str(self.estimate)])
    
    def _getNeighbourhood(self):
        return [neighbour.land for neighbour in self]
                           
    def _getEstimate(self):
        if self.estimateSet:
            return self._fixedEstimate
        return Land._defaultEst
    
    def _setEstimate(self, newEstimate):
        if newEstimate is not None:
            self.estimateSet    = True
            self._fixedEstimate = newEstimate

    def _getPathCost(self):
        if self.pathCostSet:
            return self._pathCost
        return None
    
    def _setPathCost(self, newPathCost):
        if newPathCost is not None:
            self.pathCostSet  = True
            self._pathCost    = newPathCost
    
    def _getMeanCost(self):
        if len(self) > 0:
            return sum(self) / len(self)
        return 0.0    

    def _getSummary(self):
        return " ".join([self.__class__.__name__, str(self.coordinates)])
    
    def __repr__(self):
        return "\n".join([self._costLine(), self._estLine()])
    
    def __str__(self):
        Land._shownJunc = []
        Land._shownLand = []
        return "\n".join([self._costLine(), self._estLine(), "  ".join(
            ['neighbours', ", ".join([Junction.__repr__(member) for member in
            self._uniqueMembers()])])])

    def queueOrder(firstLand, secondLand):
        firstTotal  = firstLand.pathcost + firstLand.estimate
        secondTotal = secondLand.pathcost + secondLand.estimate
        if firstTotal < secondTotal:
            return -1
        if firstTotal == secondTotal:
            return 0
        return 1

    queueOrder    = staticmethod(queueOrder)
    estimate      = property(_getEstimate, _setEstimate)
    pathcost      = property(_getPathCost, _setPathCost)
    neighbourhood = property(_getNeighbourhood)
    meanCost      = property(_getMeanCost)
    summary       = property(_getSummary)



class Woodland(Land):
    costFactor = 9.0 / 4.0



class Grassland(Land):
    costFactor = 9.0 / 8.0


    
class Wetland(Land):
    costFactor = 45.0 / 8.0

    
    
class Shrubland(Land):
    costFactor = 5.0 / 4.0

    
    
class Heathland(Land):
    costFactor = 9.0 / 8.0

    

class Artificial(Land):
    costFactor = 9.0 / 8.0

    
    
class Rock(Land):
    costFactor = 9.0 / 8.0



class Water(Land):
    colour             = (0, 0, 64)
    hue                = 240
    pull               = 0
    relativeSaturation = 1.0
    hueDrift           = 0.0
    costFactor         = None

    

class Unknown(Land):
    colour             = (255, 255, 255)
    hue                = 0
    pull               = 0
    relativeSaturation = 0.0
    hueDrift           = 0.0
    costFactor         = None

    
    
class BroadleafWoodland(Woodland):
    colour             = (254, 0, 0)
    hue                = 20
    pull               = 0
    relativeSaturation = 2.0
    hueDrift           = 0.0
    costFactor         = 45.0 / 16.0

        
    
class ConiferousWoodland(Woodland):
    colour             = (0, 102, 0)
    hue                = 180
    pull               = -100
    relativeSaturation = 3.0
    hueDrift           = -20.0
    costFactor         = 15.0 / 4.0

       
    
class Meadow(Grassland):
    colour             = (127, 228, 132)
    hue                = 110
    pull               = 0
    relativeSaturation = 2.0
    hueDrift           = 0.0
    costFactor         = 9.0 / 8.0


    
class Pasture(Grassland):
    colour             = (3, 254, 3)
    hue                = 100
    pull               = -2000
    relativeSaturation = 0.5
    hueDrift           = 0.0
    costFactor         = 9.0 / 8.0

       
    
class RoughGrassland(Grassland):
    colour             = (255, 170, 1)
    hue                = 70
    pull               = 2000
    relativeSaturation = 0.5
    hueDrift           = -30.0
    costFactor         = 9.0 / 8.0



class CalcareousGrassland(Grassland):
    colour             = (112, 167, 1)
    hue                = 80
    pull               = -1000
    relativeSaturation = 0.6
    hueDrift           = -10.0
    costFactor         = 9.0 / 8.0



class AcidGrassland(Grassland):
    colour             = (148, 129, 0)
    hue                = 60
    pull               = -1000
    relativeSaturation = 2.0
    hueDrift           = -20.0
    costFactor         = 9.0 / 8.0

    
    
class Marsh(Wetland):
    colour             = (255, 255, 1)
    hue                = 60
    pull               = 1000
    relativeSaturation = 0.25
    hueDrift           = 0.0
    costFactor         = 45.0 / 8.0

       
    
class Bog(Wetland):
    colour             = (0, 130, 116)
    hue                = 80
    pull               = 0
    relativeSaturation = 0.25
    hueDrift           = -20.0
    costFactor         = 45.0 / 8.0


    
class Highland(Shrubland):
    colour             = (1, 255, 255)
    hue                = 170
    pull               = 0
    relativeSaturation = 0.5
    hueDrift           = 0.0
    costFactor         = 9.0 / 8.0

        
    
class Heather(Heathland):
    colour             = (129, 27, 129)
    hue                = 290
    pull               = 2000
    relativeSaturation = 0.5
    hueDrift           = -50.0
    costFactor         = 9.0 / 8.0

    
    
class Saltwater(Water):
    colour             = (1, 0, 128)
    hue                = 240
    pull               = 0
    relativeSaturation = 1.0
    hueDrift           = 0.0
    costFactor         = None

        
    
class Freshwater(Water):
    colour             = (0, 0, 253)
    hue                = 240
    pull               = 0
    relativeSaturation = 1.0
    hueDrift           = 0.0 
    costFactor         = None

        

class River(Water):
    colour             = (0, 0, 102)   
    hue                = 240
    pull               = 0
    relativeSaturation = 1.0
    hueDrift           = 0.0
    costFactor         = None

        
    
class InlandRock(Rock):
    colour             = (208, 208, 255)
    hue                = 240
    pull               = 0
    relativeSaturation = 1.0
    hueDrift           = 0.0
    costFactor         = 9.0 / 8.0

        

class Littoral(Rock):
    colour             = (254, 255, 128)
    hue                = 60
    pull               = 0
    relativeSaturation = 2.0
    hueDrift           = 0.0
    costFactor         = 9.0 / 8.0



class Supralittoral(Rock):
    colour             = (205, 180, 0)
    hue                = 70
    pull               = -3000
    relativeSaturation = 0.125
    hueDrift           = 0.0
    costFactor         = 9.0 / 8.0



class Farmland(Artificial):
    colour             = (115, 37, 1)
    hue                = 220
    pull               = -2000
    relativeSaturation = 0.0
    hueDrift           = 0.0
    costFactor         = 9.0 / 8.0



class Urban(Artificial):
    colour             = (0, 0, 0)
    hue                = 120
    pull               = 0
    relativeSaturation = 0.25
    hueDrift           = 0.0
    costFactor         = 9.0 / 8.0

       
    
class Suburban(Artificial):
    colour             = (128, 128, 128)
    hue                = 240
    pull               = 0
    relativeSaturation = 1.0
    hueDrift           = 0.0
    costFactor         = 9.0 / 8.0



class HeatherGrassland(Heathland, Grassland):
    colour             = (229, 141, 166)
    hue                = 340
    pull               = 0
    relativeSaturation = 0.5  
    hueDrift           = 0.0
    costFactor         = 9.0 / 8.0



class Saltmarsh(Marsh):
    colour             = (131, 124, 253)
    hue                = 210
    pull               = 0
    relativeSaturation = 10.0   
    hueDrift           = 0.0
    costFactor         = 45.0 / 8.0
    


class Junction(float):
    def __new__(cls, value, land, road=False):
        return float.__new__(cls, value)

    def __init__(self, cost, land, road=False):
        float.__init__(self, cost)
        self.land = land
        self.road = road

    def _getSummary(self):
        if isinstance(self.land, Land):
            return " --> ".join([self.land.summary, float.__repr__(self),
                bool.__str__(self.road)])
        return repr(self)
        
    def __repr__(self):
        if isinstance(self.land, Land):
            return " --> ".join([", ".join([Land.__repr__(memb) for memb in
                self.land._uniqueNeighbourhood()]), float.__repr__(self)])
        return " --> ".join([list.__repr__(self.land), float.__repr__(self)])

    def __str__(self):
        return ", ".join([float.__repr__(self), bool.__str__(self.road)])
        
    summary = property(_getSummary)



class Grid(dict):
    _neighOff = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    _maxDiff  = 200000

    def __init__(self, contents={}, width=None, height=None):
        dict.__init__(self, contents)
        self.width  = width
        self.height = height
        if (self.width or self.height) and (not self._coordsInRange()):
            raise ValueError
        self._columns = range(0, width)
        self._rows    = range(0, height)

    def _coordsInRange(self):
        for x, y in self.keys():
            if (x < 0) or (x >= self.width) or (y < 0) or (y >= self.height):
                return False
        return True
        
    def _squareSum(leftTuple, rightTuple):
        diffList = [leftComponent - rightComponent for leftComponent, 
            rightComponent in zip(leftTuple, rightTuple)]
        return sum([diff * diff for diff in diffList])        
    _squareSum = staticmethod(_squareSum)    



class RiverGrid(Grid):
    landType       = River
    _maxDiffSquare = 100
    
    def __init__(self, contents={}, width=None, height=None):
        if isinstance(contents, str):
            Grid.__init__(self, {}, width, height)
            import pygame
            insurface = pygame.image.load(contents)
            for x in self._columns:
                for y in self._rows:
                    r, g, b, alph = insurface.get_at((x, y),)
                    dff = Grid._squareSum(RiverGrid.landType.colour, (r, g, b))
                    if dff < RiverGrid._maxDiffSquare:
                        self[(x, y)] = RiverGrid.landType                    
        else:
            Grid.__init__(self, contents, width, height)



class RoadGrid(Grid):
    _maxDiffSquare = 100
    
    def __init__(self, contents={}, width=None, height=None):
        if isinstance(contents, str):
            Grid.__init__(self, {}, width, height)
            import pygame
            insurface = pygame.image.load(contents)
            for x in self._columns:
                for y in self._rows:
                    r, g, b, alph = insurface.get_at((x, y),)
                    dff = Grid._squareSum((0, 0, 0), (r, g, b))
                    if dff < RoadGrid._maxDiffSquare:
                        self[(x, y)] = True                    
        else:
            Grid.__init__(self, contents, width, height)
            

        
class VegGrid(Grid):
    _growOnTypes = [Unknown, InlandRock, Littoral, Meadow, Suburban, 
        HeatherGrassland, River, Land]

    def __init__(self, contents={}, width=None, height=None):
        if isinstance(contents, str):
            Grid.__init__(self, {}, width, height)
            import pygame
            insurface = pygame.image.load(contents)
            for x in self._columns:
                for y in self._rows:
                    r, g, b, alph = insurface.get_at((x, y),)
                    if (r, g, b) in AdoptionType.classIndex:
                        self[(x, y)] = AdoptionType.classIndex[(r, g, b)]
                    else:
                        leastDiff = Grid._maxDiff
                        for colCode, land in AdoptionType.classIndex.items():
                            square = Grid._squareSum(colCode, (r, g, b)) - land.pull
                            if square < leastDiff:
                                leastDiff = square
                                match     = land
                        self[(x, y)] = match
            self.grow()
        else:
            Grid.__init__(self, contents, width, height)            

    def grow(self, printdescription=True):
        if printdescription:
            print "\tExpanding vegetation grid"
        thisGrid = copy(self)
        openLand = 1
        while openLand > 0:
            nextGrid = VegGrid({}, self.width, self.height)
            openLand = 0
            for x in self._columns:
                for y in self._rows:
                    if thisGrid[(x, y)] in VegGrid._growOnTypes:
                        openLand += 1
                        neiCount  = {}
                        for xOff, yOff in Grid._neighOff:
                            neighX = x + xOff
                            neighY = y + yOff
                            if (neighX >= 0) and (neighX < self.width) and (
                                neighY >= 0) and (neighY < self.height):
                                neighb = thisGrid[(neighX, neighY)]
                                if neighb not in VegGrid._growOnTypes:
                                    if neighb.__name__ in neiCount:
                                        neiCount[neighb.__name__][0] += 1
                                    else:
                                        neiCount[neighb.__name__] = [1, neighb]                        
                        numPairs = neiCount.values()
                        if len(numPairs) > 0:
                            numPairs.sort(cmp=lambda x, y: int.__cmp__(y[0], x[0]))
                            nextGrid[(x, y)] = numPairs[0][1]
                        else:
                            nextGrid[(x, y)] = thisGrid[(x, y)]
                    else:
                        nextGrid[(x, y)] = thisGrid[(x, y)]
            thisGrid = copy(nextGrid)            
        for coordPair, landType in thisGrid.items():
            self[coordPair] = landType
        

class ElevGrid(Grid):
    """
    climb-time(x) = dist * ( [ 1 + |grad| ] ** 6 )
    
    approximate descend-time(x) = dist * ( 22 * (grad ** 2) + (4 * grad) + 1  )
     
    descend-time(x) = dist * ( ( grad * ( [1 + |grad| ] ** 6  ) ) + ( (1 / grad) * ((22 * (grad ** 2) ) + ( 4 * grad ) + 1) ) ) / ( x + (1 / grad) )
    
    validate back links
    validate nobody is his own neighbour
    
    
    """
    
    _maxStr    = 10
    _vegDict   = {}
    squareSize = 2500.0     # meters

    def __init__(self, contents={}, width=None, height=None, minElev=0.0, 
        maxElev=1400.00, fulLength=squareSize, ditchThreshold=6.0,
        printdescription=True):
        if isinstance(contents, str):
            import pygame
            insurface   = pygame.image.load(contents)
            imgWidth    = insurface.get_width()
            imgHeight   = insurface.get_height()
            columns     = range(0, imgWidth)
            rows        = range(0, imgHeight)
            cells       = {}
            minBright   = float(min([min([sum(insurface.get_at((x, y),)[:3]) 
                for y in rows]) for x in columns]))
            maxBright   = float(max([max([sum(insurface.get_at((x, y),)[:3]) 
                for y in rows]) for x in columns]))
            brightRange = maxBright - minBright
            elevRange   = maxElev - minElev
            for x in columns:
                for y in rows:
                    r, g, b, alph = insurface.get_at((x, y),)
                    cells[(x, y)] = (((sum([r, g, b]) - minBright) / 
                        brightRange) * elevRange) + minElev
            ElevGrid.__init__(self, cells, imgWidth, imgHeight, minElev, 
                maxElev, fulLength, ditchThreshold)
        elif isinstance(contents, list) or isinstance(contents, tuple):
            if printdescription:
                print "Building elevation grid"
            ElevGrid.__init__(self, contents[0], width, height, minElev,
                maxElev, fulLength, ditchThreshold)
            if len(contents) > 1:
                if isinstance(contents[1], str) and len(contents[1]) > 0:
                    if printdescription:
                        print "Building vegetation grid"
                    self.veg = VegGrid(contents[1], self.width, self.height)
                if len(contents) > 2:
                    if isinstance(contents[2], str) and len(contents[2]) > 0:
                        if printdescription:
                            print "Building river grid"
                        self.rivers = RiverGrid(contents[2], self.width, 
                            self.height)
                    else:
                        if printdescription:
                            print "Can't build river grid"
                    if len(contents) > 3:
                        if isinstance(contents[3], str) and len(
                            contents[3]) > 0:    
                            if printdescription:
                                print "Building road grid\n"
                            self.roads = RoadGrid(contents[3], self.width,
                                self.height)
                            for landmarkCoord in Unit.landmarks.values():
                                self.roads[landmarkCoord] = True
                        else:
                            if printdescription:
                                print "Can't build road grid\n"
        else:
            Grid.__init__(self, contents, width, height)
            self._fulLength = fulLength
            self._rivThresh = ditchThreshold

    def landDict(self, printdescription=True):
        if printdescription:
            print "Writing land dictionary\n"
        landDict     = {}
        hasVegDict   = hasattr(self, 'veg')
        hasRiverDict = hasattr(self, 'rivers')
        hasRoadDict  = hasattr(self, 'roads')
        for x in self._columns:
            for y in self._rows:
                coTup = (x, y)
                if hasRiverDict and self.rivers.has_key(coTup):
                    landDict[coTup] = RiverGrid.landType([], coTup)
                else:
                    if self[coTup] > self._rivThresh:
                        if hasVegDict:
                            landDict[coTup] = self.veg[coTup]([], coTup)
                        else:
                            landDict[coTup] = Land([], coTup)
                    else:
                        landDict[coTup] = Water([], coTup)
                landDict[coTup].elevation = self[coTup]
        for (x, y), land in landDict.items():
            coTup = (x, y)
            land.elevation = self[coTup]
            riverMe = isinstance(land, Water) or self[coTup] <= self._rivThresh
            if (hasRoadDict and self.roads.has_key(coTup)) or (not riverMe):
                for xOff, yOff in Grid._neighOff:
                    neighX = x + xOff
                    neighY = y + yOff
                    if (neighX >= 0) and (neighX < self.width) and (neighY >=
                        0) and (neighY < self.height):
                        neighCoord      = (neighX, neighY)
                        neighbourHeight = self[(neighX, neighY)]
                        if (neighbourHeight > self._rivThresh) or (hasRoadDict 
                            and self.roads.has_key(neighCoord)):
                            neighbour = landDict[neighCoord]
                            xDisp     = xOff * xOff
                            yDisp     = yOff * yOff
                            dist      = self._fulLength * sqrt(xDisp + yDisp)
                            rise      = neighbourHeight - self[coTup] 
                            grad      = rise / dist
                            if grad < 0:
                                cost = dist * ElevGrid._descentFactor(grad)
                            else:
                                cost = dist * ElevGrid._ascentFactor(grad)
                            
                            riverNeigh = (isinstance(neighbour, Water) or 
                                neighbourHeight <= self._rivThresh)
                            
                            if hasRoadDict and ((self.roads.has_key(coTup) and
                                self.roads.has_key(neighCoord)) or 
                                (self.roads.has_key(coTup) and (not riverMe)) or
                                (self.roads.has_key(neighCoord) and
                                (not riverNeigh))):
                                neighJunction = Junction(cost, neighbour, True)
                                list.append(land, neighJunction)
                            else:
                                if not riverNeigh:
                                    cost         *= neighbour.__class__.costFactor
                                    neighJunction = Junction(cost, neighbour)
                                    list.append(land, neighJunction)
        return landDict
        
    def landList(self):
        return self.landDict().values()

    def _ascentFactor(grad):
        return (1.0 + abs(grad)) ** 6
    
    def _descentFactor(grad):
        return ((grad * ((1.0 + abs(grad)) ** 6)) + ((1.0 / grad) * ((22.0 * 
            (grad ** 2)) + (4.0 * grad) + 1.0))) / (grad + (1.0 / grad))

    def __str__(self):
        size = " ".join(['wide:', str(self.width), ' high:', str(self.height)])
        return "\n".join([size, str(self.items()[:ElevGrid._maxStr])])        

    _ascentFactor  = staticmethod(_ascentFactor)
    _descentFactor = staticmethod(_descentFactor)



class IntentionDict(dict):
    def __new__(cls, mappings={}):
        result = dict.__new__(cls, mappings)                
        return result        

    def __init__(self, mappings={}):
        dict.__init__(self, mappings)
        
        
        
class OldDate(datetime):
    def __init__(self, *positionalArguments, **keywordArguments):
        datetime.__init__(self, *positionalArguments, **keywordArguments)
        
    def __add__(self, delta):
        dateTimeResult = datetime.__add__(self, delta)
        return OldDate(dateTimeResult.year, dateTimeResult.month,
            dateTimeResult.day, dateTimeResult.hour, dateTimeResult.minute,
            dateTimeResult.second, dateTimeResult.microsecond)
        
    def strftime(self, formatString):
        cyclesBefore = int((1900 - self.year) / 400) + 1
        echoYear     = self.year + cyclesBefore * 400
        futureEcho   = datetime(echoYear, self.month, self.day, self.hour,
            self.minute, self.second, self.microsecond)
        echoResult   = datetime.strftime(futureEcho, formatString)
        return echoResult.replace(str(futureEcho.year), str(self.year))



class Unit(Position):
    roster               = {}
    landmarks            = landmarkDict
    cities               = cityDict
    bridges              = bridgeDict
    daylightHours        = range(8, 18)
    defaultBaseSpeed     = 250           # flat-road-meters every six minutes
    defaultBaseIntercept = 78000000      # meters squared
    defaultInterceptDict = {"Woodland": 28000000, 
        "BroadleafWoodland": 28000000, 
        "ConiferousWoodland": 28000000}  # meters squared
    defaultBaseSight     = 410000000     # meters squared
    defaultSightDict     = {"Woodland": 0, "BroadleafWoodland": 0, 
        "ConiferousWoodland": 0}         # meters squared
    tileWidth            = 2500          # meters
    resolutionDay        = 3             # Thursday
    resolutionHour       = 8             # 8AM
    resolutionMinute     = 0
    time                 = None
    daySpan              = timedelta(1)
    minuteSpan           = timedelta(0, 0, 0, 0, 1)
    hourSpan             = timedelta(0, 0, 0, 0, 0, 1)
    weekSpan             = timedelta(0, 0, 0, 0, 0, 0, 1)
    timestep             = minuteSpan * 6
    encHeight            = 900
    encWidth             = 900
    encZoom              = 100
    encBox               = encZoom
    encSuffix            = "encounter.bmp"   
    counterDigits        = 3
    messengerSuffix      = "-messenger"
    sideNames            = {1: ("osric", (255, 111, 107)),
        2: ("shoujing", (107, 111, 255)), 3: ("others", (107, 255, 107))}

    def __init__(self, side=None, coords=None, identity=None,
        baseIntercept=defaultBaseIntercept, interceptDict=defaultInterceptDict,
        intentionDict=IntentionDict(), currentOrder=None, progressList=None,
        printdescription=True):
        Position.__init__(self, coords)
        if printdescription:
            print "initialising Unit:", identity
        self.setup(side, coords, identity, baseIntercept, interceptDict,
            intentionDict, currentOrder, progressList)
        if not isinstance(self, Messenger):
            messengerKnows = copy(intentionDict)
            messengerKnows.update({identity: (self.coordinates, self.order,
                self.progress, copy(Unit.time))})
            self.messenger = Messenger(self.side, coords, "".join([identity,
                Unit.messengerSuffix]), self, messengerKnows)

    def setup(self, side=None, coords=None, identity=None,
        baseIntercept=defaultBaseIntercept, interceptDict=defaultInterceptDict,
        intentionDict=IntentionDict(), currentOrder=None, progressList=None):
        if isinstance(side, int):
            if Unit.sideNames.has_key(side):
                self.side = side
            else:
                print "Unknown side. For a list of all sides, type 'Unit.showSides()'"            
        else:
            print "side should be an integer"
            raise TypeError
        self.intentionDict = copy(intentionDict)
        self._curOrder     = copy(currentOrder)
        self.progress      = copy(progressList)
        self.baseSpeed     = self.__class__.defaultBaseSpeed
        self.baseIntercept = baseIntercept
        self.baseSight     = self.__class__.defaultBaseSight
        self.sightDict     = self.__class__.defaultSightDict
        self.interceptDict = interceptDict
        self.lastMovement  = copy(Unit.time)
        self.disposition   = Order.proceed
        self.engaged       = False
        if isinstance(identity, str):
            if Unit.roster.has_key(identity):
                counter  = 2
                baseName = identity
                while Unit.roster.has_key(identity):
                    counterString = str(counter)
                    counterString = "".join(["0" * (Unit.counterDigits - len(counterString)),
                        counterString])
                    identity      = "_".join([baseName, counterString])
            self.identity         = identity
            Unit.roster[identity] = self
        else:
            print "identity should be a string"
            raise TypeError

    def addIntention(self, identity, coord, order, prg, timestamp):
        if self.identity != identity:
            if self.intentionDict.has_key(identity):
                existingIntention = self.intentionDict[identity]
                if existingIntention[3] < timestamp:
                    self.intentionDict[identity] = (copy(coord), copy(order),
                        copy(prg), copy(timestamp))
            else:
                self.intentionDict[identity] = (copy(coord), copy(order),
                    copy(prg), copy(timestamp))

    def updateIntentions(self, intentionDict):
        [self.addIntention(identity, coord, order, progress, timestamp) for
            identity, (coord, order, progress, timestamp) in
            intentionDict.items()]

    def advance(self, grains):
        legInd        = self.progress[0]
        nextLegIndex  = legInd + 1
        tileInd       = self.progress[1]
        nextTileIndex = tileInd + 1
        progInd       = self.progress[2]
        curDest       = self._curOrder[legInd]
        if curDest.target != self.coordinates:
            currentLeg = curDest.path
            if len(currentLeg) == 0:
                pathExists = curDest.findPath(self.coordinates)
                if not pathExists:
                    print "Path finding has failed. No path found between", self.coordinates, "and", curDest.target
                    return False
            currentLeg = curDest.path                    
            orderTile  = currentLeg[tileInd]
            numTiles   = len(currentLeg)
            numLegs    = len(self._curOrder)
            assert self.coordinates == orderTile.coordinates  
            if nextTileIndex >= numTiles:
                if nextLegIndex >= numLegs:
                    return False
                nextDest = self._curOrder[nextLegIndex]
                nextLeg  = nextDest.path
                if (len(nextLeg) == 0) and (nextDest.target !=
                    self.coordinates):
                    nextDest.findPath(self.coordinates)
                nextLeg  = nextDest.path
                nextTile = nextLeg[1]
            else:
                nextTile = currentLeg[nextTileIndex]         
            grainTarget = orderTile.junctionTo(nextTile)     
            progInd    += grains
            while progInd >= grainTarget:
                self.lastMovement = copy(Unit.time)
                progInd -= grainTarget
                if nextTileIndex >= numTiles:  
                    legInd += 1
                    if legInd < numLegs:
                        tileInd       = 1
                        nextTileIndex = 2
                    else:
                        break
                else:
                    tileInd += 1    
                curDest = self._curOrder[legInd]
                curLeg  = curDest.path
                if (len(curLeg) == 0) and (curDest.target !=
                    orderTile.coordinates):
                    curDest.findPath(orderTile.coordinates)
                curLeg           = curDest.path
                self.coordinates = curDest.path[tileInd].coordinates
                nextTileIndex    = tileInd + 1
            if legInd < numLegs:    
                self.progress = [legInd, tileInd, progInd]
            else:
                self.progress = None
        return self.progress

    def _setOrder(self, newOrder):
        if isinstance(newOrder, Order):
            newOrder = newOrder.destinationSequence
        elif (newOrder is not None) and (((not isinstance(newOrder, list)) and (not
            isinstance(newOrder, tuple))) or (not isinstance(newOrder[0],
                Destination))):
            print "new order should be a list or tuple of Destinations"
            raise TypeError
        if self._curOrder is not None:
            oldFirstDest = self._curOrder[0].target
        else:
            oldFirstDest = None
        self._curOrder = newOrder
        if (oldFirstDest is None) or (newOrder is None) or (self.progress is
            None) or (oldFirstDest != newOrder[0].target):
            self.progress = [0, 0, 0.0]
        else:
            self.progress = [0, 0, self.progress[2]]
        if not isinstance(self, Messenger) and not isinstance(self, Commander):
            self.messenger.intentionDict[self.identity] = (copy(
            self.coordinates), copy(newOrder), copy(self.progress), 
            copy(Unit.time))
            if self.messenger.goingToUnit:
                self.messenger.order = [Destination(self.coordinates)]
                if self.coordinates != self.messenger.coordinates:
                    self.messenger.order[0].findPath(
                        self.messenger.coordinates)
        
    def _getOrder(self):
        return self._curOrder

    def __del__(self):       
        if Unit.roster.has_key(self.identity):
            del Unit.roster[self.identity]
        if hasattr(self, 'messenger') and isinstance(self.messenger, Messenger):
            if self.messenger.commander.subordinates.has_key(self.identity):
                del self.messenger.commander.subordinates[self.identity]
            del self.messenger
            
    def __str__(self):
        return " at ".join([self.identity, str(self.coordinates)])
    
    def friendlyContact(self, friendlyUnit):
        self.updateIntentions(friendlyUnit.intentionDict)
        if isinstance(friendlyUnit, Messenger):
            return False
        return self.sight(friendlyUnit, friendlyUnit.order,
            friendlyUnit.progress)
        
    def sight(self, sightedUnit, order=None, progress=None):
        if isinstance(sightedUnit, Messenger):
            return False
        if self.side == sightedUnit.side:
            self.addIntention(sightedUnit.identity, 
                sightedUnit.coordinates, sightedUnit.order,
                sightedUnit.progress, copy(Unit.time))
        else:
            if not isinstance(self, Messenger):
                self.addIntention(sightedUnit.identity, 
                    sightedUnit.coordinates, order, progress, copy(Unit.time))
                if not self.engaged:
                    if self.order is None:
                        existingTargetCoord = None
                    else:
                        existingTargetCoord = self.order[-1].path[-1].coordinates
                    findNewPath = False
                    if self.disposition == Order.halt:
                        if self.coordinates != existingTargetCoord:
                            self.order  = [Destination(self.coordinates)]
                            findNewPath = True
                    elif self.disposition == Order.attack:
                        if sightedUnit.coordinates != existingTargetCoord:
                            self.order  = [Destination(sightedUnit.coordinates)]
                            findNewPath = True
                    elif self.disposition == Order.withdraw:
                        meX, meY   = self.coordinates
                        heX, heY   = sightedUnit.coordinates
                        dirX, dirY = meX - heX, meY - heY
                        for withdrawSquares in Order.withdrawDistances:
                            scaleX, scaleY = Destination.scale(dirX, dirY,
                                withdrawSquares)
                            coord = (meX + int(scaleX + 0.5), meY + int(scaleY + 0.5))
                            if not isinstance(Destination.landDict[coord], Water):
                                if coord != existingTargetCoord:
                                    self.order  = [Destination(coord)]
                                    findNewPath = True
                                break
                    if findNewPath:
                        if self.order[0].target != self.coordinates:
                            self.order[0].findPath(self.coordinates)
        if isinstance(self, Commander):
            directKnowledge                = copy(self.intentionDict)
            directKnowledge[self.identity] = (self.coordinates, self.order,
                self.progress, copy(Unit.time))
            aideDeCamp                     = Adjutant(self.side, 
                'aide-de-camp', directKnowledge)
            result                         = aideDeCamp.deliverReport(self)
            del aideDeCamp
            return result
        return False
    
    def showUnits():
        for unit in Unit.roster.values():
            print unit
    
    def showLandmarks():
        for key, value in Unit.landmarks.items():
            print key, " at", value
            
    def showSides():
        for key, (sidename, rgb) in Unit.sideNames.items():
            print key, ":", sidename, "(colour =", rgb, ")"            
    
    def retreat(identity, targetdestination, retreatspeed=4800.0):
        if isinstance(identity, str):
            if Unit.roster.has_key(identity):
                retreatingUnit = Unit.roster[identity]
                if isinstance(targetdestination, str):
                    if Unit.landmarks.has_key(targetdestination):
                        coord             = Unit.landmarks[targetdestination]
                        targetdestination = Destination(coord)
                    else:
                        print "Unknown landmark. For a list of all landmarks, type 'Unit.showLandmarks()'"
                elif isinstance(targetdestination, tuple) or isinstance(targetdestination, list):
                    targetdestination = Destination(targetdestination)
                elif not isinstance(targetdestination, Destination):
                    print "second argument should be a string, coordinate tuple, coordinate list or Destination"
                    raise TypeError
                retreatingUnit.order       = [targetdestination]
                retreatingUnit.disposition = Order.withdraw
                retreatingUnit.order[0].findPath(retreatingUnit.coordinates)
                retreatingUnit.advance(retreatspeed)
            else:
                print "Unknown unit. For a list of all units, type 'Unit.showUnits()'"
        elif isinstance(identity, Unit):
            Unit.retreat(identity.identity, targetdestination, retreatspeed)
        else:
            print "first argument should be a string or Unit"
            raise TypeError

    def release(identity):
        if isinstance(identity, str):
            if Unit.roster.has_key(identity):
                releasedUnit = Unit.roster[identity]
                if releasedUnit.engaged:
                    releasedUnit.engaged = False
                else:
                    print "Unit already released"
            else:
                print "Unknown unit. For a list of all units, type 'Unit.showUnits()'"
        elif isinstance(identity, Unit):
            Unit.release(identity.identity)
        else:
            print "first argument should be a string or Unit"
            raise TypeError                
    
    def setTime(year=1331, month=2, day=21, hour=6):
        Unit.time = OldDate(year, month, day, hour)
        
    def addWeeks(numWeeks=1):
        Unit.time += numWeeks * Unit.weekSpan
        
    def addDays(numDays=1):
        Unit.time += numDays * Unit.daySpan
        
    def addHours(numHours=1):
        Unit.time += numHours * Unit.hourSpan
        
    def addMinutes(numMinutes=1):
        Unit.time += numMinutes * Unit.minuteSpan
        
    def addTimestep():
        Unit.time += Unit.timestep
    
    def nextEvent():
        eventFlag = False
        while not eventFlag:
            eventFlag, eventList = Unit.tick()
        return copy(Unit.time), eventList
    
    def showNext():
        reportTypes = {}
        while len(reportTypes) < 2:
            result = Unit.nextEvent()
            print result[0]
            for eventDescription in result[1]:
                print eventDescription
                if not reportTypes.has_key(eventDescription):
                    reportTypes[eventDescription] = True
            print    
    
    def tick():
        Unit.addTimestep()
        eventList = []
        if Unit.time.hour in Unit.daylightHours:
            if (Unit.time.weekday() == Unit.resolutionDay) and (Unit.time.hour
                == Unit.resolutionHour) and (Unit.time.minute ==
                Unit.resolutionMinute):
                eventFlag = True
                eventList = ["Weekly resolution"]
            else:
                eventFlag = False
            for identity, unitObject in Unit.roster.items():
                if unitObject.engaged:
                    eventFlag = True
                if unitObject.order is not None:
                    unitObject.advance(unitObject.baseSpeed)
            unitList = Unit.roster.values()
            for first in unitList:
                firstCoord     = first.coordinates
                firstMessenger = isinstance(first, Messenger)
                firstID        = first.identity
                if not firstMessenger:                
                    firstTile    = Destination.landDict[firstCoord]
                    firstTerrain = firstTile.__class__.__name__
                    if first.interceptDict.has_key(firstTerrain):
                        firstInter = first.interceptDict[firstTerrain]
                    else:
                        firstInter = first.baseIntercept
                    if first.sightDict.has_key(firstTerrain):
                        firstSight = first.sightDict[firstTerrain]
                    else:
                        firstSight = first.baseSight                    
                    firstX = first.coordinates[0]
                    firstY = first.coordinates[1]
                for second in unitList:
                    if first is second:
                        continue
                    secondCoord = second.coordinates
                    if firstMessenger:
                        if (firstCoord == secondCoord) and (first.side ==
                            second.side):
                            contactResult = first.friendlyContact(second)
                            if contactResult:
                                eventFlag = True
                                eventList.append(" ".join(["new report for",
                                    Unit.sideNames[first.side][0]]))
                    elif not isinstance(second, Messenger):
                        secondID      = second.identity
                        secondTile    = Destination.landDict[secondCoord]
                        secondTerrain = secondTile.__class__.__name__
                        if second.interceptDict.has_key(secondTerrain):
                            secondInter = second.interceptDict[secondTerrain]
                        else:
                            secondInter = second.baseIntercept
                        interSquare = max(firstInter, secondInter)
                        xDisp       = Unit.tileWidth * (firstX -
                            second.coordinates[0])
                        yDisp       = Unit.tileWidth * (firstY -
                            second.coordinates[1])
                        squareDist  = xDisp * xDisp + yDisp * yDisp
                        if squareDist < interSquare:
                            first.sight(second)
                            if first.side == second.side:
                                first.friendlyContact(second)
                            else: 
                                result         = Messenger.savePerfectMap(first)
                                first.order    = None
                                second.order   = None
                                first.engaged  = True
                                second.engaged = True
                                eventFlag      = eventFlag or result
                                if result:
                                    eventList.append("new situation map for GM")
                                    Messenger.savePerfectMap(first,
                                        Unit.encWidth, Unit.encHeight,
                                        Unit.encZoom, Unit.encBox, 
                                        Unit.encSuffix, False)        
                        else:
                            if second.sightDict.has_key(secondTerrain):
                                secondSight = second.sightDict[secondTerrain]
                            else:
                                secondSight = second.baseSight
                            sightSquare = min(firstSight, secondSight)
                            if squareDist < sightSquare:
                                commanderResult = first.sight(second)
                                if (isinstance(first, Commander) and 
                                    commanderResult):
                                    eventFlag = True
                                    eventList.append(" ".join([
                                        "new report for",
                                        Unit.sideNames[first.side][0]]))
            return eventFlag, eventList
        return False, eventList
        
    def start():
        eg2 = ElevGrid(("uktopo.tga", "veg2.tga", "river.tga", "roads2.tga"),)
        Unit.setTime()
        Destination.setLandDict(eg2.landDict())
        churlsA           = Churls(1, "Brigand's Eden", "Churls A")
        churlsB           = Churls(1, "Bat Cave", "Churls B")
        churlsC           = Churls(1, "Greater Kimbrough", "Churls C")
        churlsD           = Churls(1, "Puddle Hill", "Churls D")
        churlsE           = Churls(1, "Gooseneck Ridge", "Churls E")
        churlsF           = Churls(1, "Sour Biscuit", "Churls F")
        huscarlsA         = Huscarls(1, "Shankly Mallet", "Huscarls A")
        huscarlsB         = Huscarls(1, "Hickingbotham", "Huscarls B")
        huscarlsC         = Huscarls(1, "Witenagemot of Sussex", "Huscarls C")
        kentishRoyalGuard = KentishRoyalGuard(1, "Freyja's Hof", "Kentish Royal Guard")
        knightsEcstatic   = KnightsEcstatic(1, "Tick Hollow", "Knights Ecstatic")
        skirmishersA      = Skirmishers(1, "Tingle Heath", "Skirmishers A")
        skirmishersB      = Skirmishers(1, "Burnside", "Skirmishers B")
        thanesA           = Thanes(1, "Jodhpurs-on-the-Wakely", "Thanes A")
        thanesB           = Thanes(1, "Wallowleigh", "Thanes B")
        thanesC           = Thanes(1, "Cheesequake Mill", "Thanes C")
        honeyEaters1      = HoneyEaters(2, "Fahey-on-Kubrick", "Honey Eaters 1")
        honeyEaters2      = HoneyEaters(2, "Ullr's Cross", "Honey Eaters 2")
        kingsGuard        = KingsGuard(2, "Rohan-on-Sykes", "King's Guard")
        mercianGuard1     = MercianGuard(2, "Ox Sock", "Mercian Guard 1")
        mercianGuard2     = MercianGuard(2, "Sykesford Forum", "Mercian Guard 2")
        mercianGuard3     = MercianGuard(2, "Gingham-on-Kinski", "Mercian Guard 3")
        mercianGuard4     = MercianGuard(2, "Crayton", "Mercian Guard 4")
        mercianGuard5     = MercianGuard(2, "Damp Wellan", "Mercian Guard 5")
        mercianGuard6     = MercianGuard(2, "Zig Zag Ridge", "Mercian Guard 6")
        Messenger.savePerfectMap(mercianGuard3, 1400, 2100, 15, 15, "initialpositions.bmp", False, showMessengers=False)
    
    def reinforce():        
        kingsThanes1   = Thanes(2, "Ashby-on-Humidor", "King's Thanes 1")
        kingsThanes2   = Thanes(2, "Damp Wellan", "King's Thanes 2")
        lightCavalry1  = LightCavalry(2, "Fahey-on-Kubrick", "Light Cavalry 1")
        lightCavalry2  = LightCavalry(2, "Surly", "Light Cavalry 2")
        normanCavalry1 = NormanCavalry(2, "Damp Wellan", "Norman Cavalry 2")
        normanCavalry2 = NormanCavalry(2, "Surly", "Norman Cavalry 2")
        raiders1       = Raiders(2, "Thunor's Pillar", "Raiders 1")
        raiders2       = Raiders(2, "Ashby-on-Humidor", "Raiders 2")
        warParty1      = WarParty(2, "Ashby-on-Humidor", "War Party 1")
        warParty2      = WarParty(2, "Thunor's Pillar", "War Party 2")
        warParty3      = WarParty(2, "Fahey-on-Kubrick", "War Party 3")
        warParty4      = WarParty(2, "Surly", "War Party 4")

    def legacy():
        john = Commander(2, "Rohan-on-Sykes", "John")
        john.absorb("King's Guard")
        john.command("Mercian Guard 2")
        john.command("Honey Eaters 1")
        john.command("Mercian Guard 1")
        john.command("Mercian Guard 3")
        john.giveOrder(john, "Freyja's Hof", Order.attack)
        john.giveOrder("Mercian Guard 2", "Rohan-on-Sykes", Order.proceed)
        john.giveOrder("Honey Eaters 1", "Ox Sock", Order.proceed)
        
        bradey = CommandDetail(2, "Crayton", "Bradey")
        bradey.command("Mercian Guard 4")
        bradey.command("Mercian Guard 5")
        bradey.command("Honey Eaters 2")
        bradey.command("Mercian Guard 6")
        bradey.giveOrder("Mercian Guard 4", Destination("Ullr's Cross", Offset((0, -30),)), Order.proceed)
        bradey.giveOrder("Mercian Guard 5", "Ullr's Cross", Order.proceed)
        
        avi = Commander(1, "Brigand's Eden", "Avi")
        avi.absorb("Churls A")
        avi.command("Thanes B")
        avi.command("Huscarls B")
        avi.giveOrder(avi, "Jodhpurs-on-the-Wakely", Order.proceed)
        avi.giveOrder("Thanes B", Destination("Hickingbotham", Offset((0, 6),)), Order.proceed)
        
        rohan = Commander(1, "Freyja's Hof", "Rohan")
        rohan.absorb("Kentish Royal Guard")
        rohan.command("Skirmishers B")
        rohan.command("Huscarls C")
        rohan.giveOrder("Skirmishers B", "London", Order.halt)
        rohan.giveOrder("Huscarls C", "Burnside", Order.proceed)
        rohan.giveOrder(rohan, "Burnside", Order.proceed)
        
        kym = Commander(1, "Bat Cave", "Kym")
        kym.absorb("Churls B")
        kym.command("Churls C")
        kym.command("Churls D")
        kym.command("Thanes C")
        kym.command("Skirmishers A")
        kym.giveOrder(kym, Destination("Crayton", Offset((-25, 0),)), Order.proceed)
        kym.giveOrder("Churls C", Destination("Crayton", Offset((-25, 0),)), Order.proceed)
        kym.giveOrder("Churls D", Destination("Crayton", Offset((0, 25),)), Order.proceed)
        kym.giveOrder("Thanes C", Destination("Crayton", Offset((0, 25),)), Order.proceed)
        kym.giveOrder("Skirmishers A", Destination("Waksberg", Offset((-50, -50),)), Order.proceed)
        
        tom = CommandDetail(1, "Shankly Mallet", "Tom")
        tom.command("Huscarls A")
        tom.command("Churls F")
        tom.command("Churls E")
        tom.command("Knights Ecstatic")
        tom.giveOrder("Huscarls A", "Greater Kimbrough", Order.proceed)
        tom.giveOrder("Churls F", "Sour Biscuit", Order.proceed)
        tom.giveOrder("Churls E", "Betws-y-Moel", Order.proceed)
        tom.giveOrder("Knights Ecstatic", "Caerperlewygol", Order.proceed)
        
        chris = Commander(3, "Dwfrbwlch", "Chris")
        oak   = WelshPilgrims(3, "Dwfrbwlch", "Oak")
        hawthorn = WelshPilgrims(3, "Dwfrbwlch", "Hawthorn")
        willow = WelshPilgrims(3, "Dwfrbwlch", "Willow")
        hazel = WelshPilgrims(3, "Dwfrbwlch", "Hazel")
        welshKnightsEcstatic = WelshKnightsEcstatic(3, "Dwfrbwlch", "Welsh Knights Ecstatic")
        chris.absorb("Welsh Knights Ecstatic")
        chris.command("Oak")
        chris.command("Hawthorn")
        chris.command("Willow")
        chris.command("Hazel")
        
        return john, bradey, avi, rohan, kym, tom, chris
        
        

    order         = property(_getOrder, _setOrder)
    showUnits     = staticmethod(showUnits)
    showLandmarks = staticmethod(showLandmarks)
    showSides     = staticmethod(showSides)
    retreat       = staticmethod(retreat)
    release       = staticmethod(release)
    nextEvent     = staticmethod(nextEvent)
    showNext      = staticmethod(showNext)
    tick          = staticmethod(tick)
    start         = staticmethod(start)
    reinforce     = staticmethod(reinforce)
    legacy        = staticmethod(legacy)
    setTime       = staticmethod(setTime)
    addWeeks      = staticmethod(addWeeks)
    addDays       = staticmethod(addDays)
    addHours      = staticmethod(addHours)
    addMinutes    = staticmethod(addMinutes)
    addTimestep   = staticmethod(addTimestep)
    
    
        
class Messenger(Unit):
    pygame.font.init()
    
    defaultBaseSpeed  = 2500        # flat-road-meters every six minutes
    backgroundColour  = (0, 0, 51)
    roadColour        = (215, 191, 187)
    landmarkColour    = (0, 48, 94)
    minSaturation     = 0.1
    minColourValue    = 0.2
    colourValueRange  = 1.0 - minColourValue
    saturationCoeffs  = [0.958, 0.338, -1.181]
    mapFont           = pygame.font.SysFont('garamond', 24, bold=1, italic=0)
    unitFont          = pygame.font.SysFont('garamond', 12, bold=1, italic=0)
    landmarkFont      = pygame.font.SysFont('garamond', 24, bold=1, italic=0)
    bridgeFont        = pygame.font.SysFont('garamond', 12, bold=0, italic=1)
    perfectDirectory  = "gm"
    perfCaptionPrefix = "GM"
    sitMapSuffix      = ".bmp"
    sitOutHeight      = 836
    sitOutWidth       = 672
    sitBorder         = 12
    sitUnitBorder     = 2
    sitRatio          = 2
    sitZoom           = 16
    sitDotRadius      = 12
    sitBridgeRadius   = 5
    sitDotDiam        = sitDotRadius * 2
    sitMaxWidth       = int(sitOutWidth / 2)
    sitMaxHeight      = int(sitOutHeight / 2)
    sitHalfWidth      = int(sitMaxWidth / sitZoom)
    sitHalfHeight     = int(sitMaxHeight / sitZoom)
    sitBoxSize        = sitZoom
    sitUnitBoxSize    = sitBoxSize - (2 * sitUnitBorder)
    captionDateForm   = "%A, %d %B %I:%M%p"
    filenameDateForm  = "%Y-%m-%d-%H-%M"
    lastPerfect       = Set()

    def __init__(self, side=None, coords=None, identity=None, unit=None,
        intentionDict=IntentionDict(), commander=None, message=None):
        Unit.__init__(self, side, coords, identity, 0, {}, intentionDict)
        self.message     = message
        self.unit        = unit
        self._commander  = commander
        self.goingToUnit = False
        self.report      = {}
        self.baseSpeed   = Messenger.defaultBaseSpeed
        if unit is not None:
            assert unit.side == self.side
            self.updateIntentions(unit.intentionDict)
            self.sight(unit, unit.order, unit.progress)
        if commander is not None:
            assert commander.side == self.side
            self.clearDestination()
            self.findDestination()

    def advance(self, grains):
        Unit.advance(self, grains)
        if ((len(self.order) < 1) or (len(self.order[0].path) < 1) or
            (self.coordinates == self.order[0].path[-1].coordinates)):
            if self.goingToUnit:
                self.order = [Destination(self.unit.coordinates)]
            else:
                self.order = [Destination(self.commander.coordinates)]
            if self.order[0].target != self.coordinates:
                self.order[0].findPath(self.coordinates)    

    def friendlyContact(self, friendlyUnit):
        result = False
        self.updateIntentions(friendlyUnit.intentionDict)
        self.sight(friendlyUnit, friendlyUnit.order, friendlyUnit.progress)
        newTarget = False
        if (friendlyUnit is self.commander) and (not self.goingToUnit):
            result           = self.deliverReport(friendlyUnit)
            self.goingToUnit = True
            newTarget        = True
            self.order       = [Destination(self.unit.coordinates)]
        elif (friendlyUnit is self.unit) and self.goingToUnit:
            if self.message is not None:
                self.deliverMessage(friendlyUnit)
                self.message = None
            self.goingToUnit = False
            newTarget        = True
            self.order       = [Destination(self.commander.coordinates)]
        if newTarget and (self.order[0].target != self.coordinates):
            self.order[0].findPath(self.coordinates)
        return result

    def deliverMessage(self, friendlyUnit):
        if self.message.disposition is not None:
            friendlyUnit.disposition = self.message.disposition
        if isinstance(self.message, Addendum):
            newPart = self.message.destinationSequence
            friendlyUnit.order += newPart
        else:
            if isinstance(self.message, Order):
                friendlyUnit.order = self.message.destinationSequence
        
    def deliverReport(self, receiver, printdescription=False):
        self.report = copy(self.intentionDict)
        if (receiver is self.commander) and (self.commander.outBox.has_key(
            self.unit.identity) and (self.commander.outBox[self.unit.identity]
            is not None)):
            if printdescription:
                print "collecting order for", self.unit.identity, "from outbox"
            newOrder = self.commander.outBox[self.unit.identity]
            self.message = self.commander.outBox[self.unit.identity]
            self.commander.outBox[self.unit.identity] = None
            del self.commander.outBox[self.unit.identity]
        return self.saveSituationMap(receiver)

    def saveSituationMap(self, receiver):
        if (not hasattr(self, 'unit')) or (self.unit is None):
            coord     = copy(receiver.coordinates)
            order     = None
            progress  = None
            timestamp = copy(Unit.time)
            unitID    = receiver.identity
            unitCoord = coord
        else:
            unitID                            = self.unit.identity
            coord, order, progress, timestamp = self.report[unitID]
            unitCoord                         = self.unit.coordinates
        fileID      = Messenger.makeFilename(unitID)
        fileSub     = Messenger.makeFilename(receiver.identity)
        fileDirect  = Messenger.makeFilename(Unit.sideNames[receiver.side][0])
        sitMapFname = "\\".join([fileDirect, "".join(["-".join([fileSub,
            fileID, timestamp.strftime(Messenger.filenameDateForm)]),
            Messenger.sitMapSuffix])])
        captionText = " at ".join([unitID,
            timestamp.strftime(Messenger.captionDateForm)])
        highestPeak = max([land.elevation for land in
            Destination.landDict.values()])    
        sitMap      = pygame.Surface((Messenger.sitOutWidth,
            Messenger.sitOutHeight), 0, 24)
        xMin        = max(0, (unitCoord[0] -
            Messenger.sitHalfWidth))
        xMax        = min(Messenger.sitMaxWidth, (unitCoord[0] +
            Messenger.sitHalfWidth) + 1)
        yMin        = max(0, (unitCoord[1] -
            Messenger.sitHalfHeight))
        yMax        = min(Messenger.sitMaxHeight, (unitCoord[1] +
            Messenger.sitHalfHeight) + 1)  
        wideRange   = range(xMin, xMax)
        highRange   = range(yMin, yMax)
        for x in wideRange:
            for y in highRange:
                leftX      = (x - xMin) * Messenger.sitZoom
                leftY      = (y - yMin) * Messenger.sitZoom
                outCorners = (leftX, leftY, Messenger.sitBoxSize,
                    Messenger.sitBoxSize)
                land       = Destination.landDict[(x, y)]
                if land.elevation == 0:
                    boxColour = Messenger.backgroundColour
                else:
                    roadJunctCount = 0
                    roadFlag       = False
                    for junct in land:
                        if junct.road:
                            roadJunctCount += 1
                        if (roadJunctCount > 5) or ((roadJunctCount >
                            0) and isinstance(land, Water)):
                            boxColour = Messenger.roadColour
                            roadFlag  = True
                            break                  
                    if not roadFlag:
                        relativeElevation = land.elevation / highestPeak
                        colourValue       = (Messenger.minColourValue +
                            relativeElevation * Messenger.colourValueRange)
                        baseSaturation    = (Messenger.saturationCoeffs[0] + 
                            Messenger.saturationCoeffs[1] * colourValue +
                            Messenger.saturationCoeffs[2] * colourValue *
                            colourValue)
                        if hasattr(land, 'relativeSaturation'):
                            baseSaturation *= land.relativeSaturation
                        colourSaturation = max(Messenger.minSaturation,
                            min(1.0, baseSaturation))           
                        chroma = colourValue * colourSaturation
                        if hasattr(land, 'hueDrift'):
                            huePrime = ((land.hue + relativeElevation
                                * land.hueDrift) % 360.0) / 60.0
                        else:
                            huePrime = (land.hue % 360.0) / 60.0
                        xTerm = chroma * (1.0 - abs((huePrime % 2.0) - 1.0))
                        if huePrime < 1.0:
                            colourBase = (chroma, xTerm, 0.0)
                        else:
                            if huePrime < 2.0:
                                colourBase = (xTerm, chroma, 0.0)
                            else:
                                if huePrime < 3.0:
                                    colourBase = (0.0, chroma, xTerm)
                                else:
                                    if huePrime < 4.0:
                                        colourBase = (0.0, xTerm, chroma)
                                    else:
                                        if huePrime < 5.0:
                                            colourBase = (xTerm, 0.0, chroma)
                                        else:
                                            colourBase = (chroma, 0.0, xTerm)
                        chromaGap = colourValue - chroma
                        boxColour = (int(255.0 * (colourBase[0] + chromaGap)),
                            int(255.0 * (colourBase[1] + chromaGap)),
                            int(255.0 * (colourBase[2] + chromaGap)))             
                pygame.draw.rect(sitMap, boxColour, outCorners)   
        collisionDict = {}
        for landmarkName, (x, y) in Unit.landmarks.items():
            if (x > xMin) and (x < xMax) and (y > yMin) and (y < yMax):
                collisionDict[(x, y)] = 1
                centreX = int((0.5 + x - xMin) * Messenger.sitZoom)
                centreY = int((0.5 + y - yMin) * Messenger.sitZoom)
                markText = "".join(["     ", landmarkName])
                if Unit.bridges.has_key(landmarkName):
                    lableFont = Messenger.bridgeFont
                    dotRadius = Messenger.sitBridgeRadius                
                else:
                    lableFont = Messenger.landmarkFont
                    dotRadius = Messenger.sitDotRadius
                textSurface = lableFont.render(markText, True,
                    (0, 0, 0), (255, 255, 255))
                sitMap.blit(textSurface, (centreX - dotRadius - 1,
                    centreY - dotRadius - 1)) 
                pygame.draw.circle(sitMap, Messenger.landmarkColour, (centreX,
                    centreY), dotRadius)
        stateDescription = Set()
        for identity, ((x, y), order, prg, tm) in self.intentionDict.items():
            if (x > xMin) and (x < xMax) and (y > yMin) and (y < yMax):
                stateDescription.add((identity, (x, y)),)
                sighting    = Unit.roster[identity]
                side        = sighting.side
                leftX       = (x - xMin) * Messenger.sitZoom
                leftY       = (y - yMin) * Messenger.sitZoom
                outCorners  = (leftX + Messenger.sitUnitBorder,
                    leftY + Messenger.sitUnitBorder, Messenger.sitUnitBoxSize,
                    Messenger.sitUnitBoxSize)
                boxColour   = Unit.sideNames[side][1]
                topLine     = "".join(["     ", identity, " at ",
                    tm.strftime(Messenger.captionDateForm)])
                terrain     = Destination.landDict[(x, y)]
                terrainType = terrain.__class__.__name__
                elevation   = terrain.elevation
                bottomLine  = "".join(["      in ", terrainType, " ",
                    str(int(elevation)), "m above sea level"])               
                topX, topY  = Messenger.unitFont.size(topLine)
                btmX, btmY  = Messenger.unitFont.size(bottomLine)
                widest      = max(topX, btmX)
                tallest     = max(topY, btmY)
                lineHeight  = Messenger.unitFont.get_linesize()
                textSurface = pygame.Surface((widest, tallest + lineHeight),
                    0, 32)
                if collisionDict.has_key((x, y),) and (collisionDict[(x,
                    y)] > 3):
                    topSurf = Messenger.unitFont.render(topLine, True,
                        (0, 0, 0))
                    btmSurf = Messenger.unitFont.render(bottomLine, True,
                        (0, 0, 0))                
                else:
                    textSurface.fill((255, 255, 255),)
                    topSurf = Messenger.unitFont.render(topLine, True,
                        (0, 0, 0), (255, 255, 255))
                    btmSurf = Messenger.unitFont.render(bottomLine, True,
                        (0, 0, 0), (255, 255, 255))
                textSurface.blit(topSurf, (0, 0))
                textSurface.blit(btmSurf, (0, lineHeight))
                if collisionDict.has_key((x, y),):
                    overlaps               = collisionDict[(x, y)]
                    angle                  = -90 * overlaps
                    textSurface            = pygame.transform.rotate(textSurface, angle)
                    collisionDict[(x, y)] += 1
                else:
                    collisionDict[(x, y)] = 1
                    angle                 = 0
                textHeight    = textSurface.get_height()
                quarterHeight = textHeight / 4
                if angle == 0:    
                    sitMap.blit(textSurface, (leftX, leftY - quarterHeight))
                else:
                    angle = angle % 360
                    if angle >= 270:
                        textX = 0
                        textY = 0
                    elif angle >= 180:
                        textX = textSurface.get_width()
                        textY = 0
                    elif angle >= 90:
                        textX = textSurface.get_width()
                        textY = textHeight
                    else:
                        textX = 0
                        textY = textHeight
                    sitMap.blit(textSurface, (leftX - textX, leftY + textY))
                pygame.draw.rect(sitMap, boxColour, outCorners)
                pygame.draw.rect(sitMap, (0, 0, 0), outCorners, 1)
        if stateDescription == receiver.lastSight:
            return False
        receiver.lastSight = stateDescription
        pygame.draw.rect(sitMap, (0, 0, 0), (0, 0, Messenger.sitOutWidth,
            Messenger.sitOutHeight), Messenger.sitBorder)    
        textSurface = Messenger.mapFont.render(captionText, True, (0, 0, 0),
            (255, 255, 255))
        sitMap.blit(textSurface, (Messenger.sitBorder, Messenger.sitBorder))
        pygame.image.save(sitMap, sitMapFname.lower())
        return True
    
    def _getCommander(self):
        return self._commander
        
    def _setCommander(self, newCom):
        if isinstance(newCom, Commander):
            if newCom.side == self.side:
                self._commander = newCom
                self.intentionDict[newCom.identity] = (copy(newCom.coordinates),
                    copy(newCom.order), copy(newCom.progress), copy(Unit.time))
                self.order = [Destination(self.commander.coordinates)]
                if self.commander.coordinates != self.coordinates:
                    self.order[0].findPath(self.coordinates)
            else:
                print "commander and messenger should belong to the same side."
                print "commander belongs to", Unit.sideNames[newCom.side][0]
                print "messenger belongs to", Unit.sideNames[self.side][0]
                raise ValueError
        elif isinstance(newCom, str):
            if Unit.roster.has_key(newCom):
                self._setCommander(Unit.roster[newCom])
            else:
                print "Unknown unit. For a list of all units, type 'Unit.showUnits()'"
        else:
            print "first argument should be a Commander or string"
            raise TypeError
    
    def makeFilename(fullName):
        return fullName.replace(' ', '-').lower().strip()
    
    def savePerfectMap(subject, width=sitOutWidth, height=sitOutHeight,
        zoom=sitZoom, boxSize=sitBoxSize, suffix=sitMapSuffix,
        testForDouble=True, showMessengers=True):
        sitMaxWidth  = int(width / 2)
        sitMaxHeight = int(height / 2)
        halfWidth    = int(sitMaxWidth / zoom)
        halfHeight   = int(sitMaxHeight / zoom)   
        coord        = subject.coordinates
        sitMapFname  = "\\".join([Messenger.perfectDirectory,
            "".join([Messenger.makeFilename(subject.identity), "-",
            Unit.time.strftime(Messenger.filenameDateForm),
            suffix])])
        captionText  = "  ".join([Messenger.perfCaptionPrefix,
            Unit.time.strftime(Messenger.captionDateForm)])        
        highestPeak  = max([land.elevation for land in
            Destination.landDict.values()])               
        sitMap       = pygame.Surface((width,
            height), 0, 24)        
        xMin         = max(0, (subject.coordinates[0] -
            halfWidth))
        xMax         = min(sitMaxWidth, (subject.coordinates[0] +
            halfWidth) + 1)
        yMin         = max(0, (subject.coordinates[1] -
            halfHeight))
        yMax         = min(sitMaxHeight, (subject.coordinates[1] +
            halfHeight) + 1)  
        wideRange    = range(xMin, xMax)
        highRange    = range(yMin, yMax)
        for x in wideRange:
            for y in highRange:
                leftX      = (x - xMin) * zoom
                leftY      = (y - yMin) * zoom
                outCorners = (leftX, leftY, boxSize,
                    boxSize)
                land       = Destination.landDict[(x, y)]
                if land.elevation == 0:
                    boxColour = Messenger.backgroundColour
                else:
                    roadFlag       = False
                    roadJunctCount = 0
                    for junct in land:
                        if junct.road:
                            roadJunctCount += 1
                        if (roadJunctCount > 5) or ((roadJunctCount > 0) and isinstance(land, Water)):
                            boxColour = Messenger.roadColour
                            roadFlag  = True
                            break                
                    if not roadFlag:
                        relativeElevation = land.elevation / highestPeak
                        colourValue       = (Messenger.minColourValue +
                            relativeElevation * Messenger.colourValueRange)
                        baseSaturation    = (Messenger.saturationCoeffs[0] + 
                            Messenger.saturationCoeffs[1] * colourValue +
                            Messenger.saturationCoeffs[2] * colourValue *
                            colourValue)
                        if hasattr(land, 'relativeSaturation'):
                            baseSaturation *= land.relativeSaturation
                        colourSaturation = max(Messenger.minSaturation,
                            min(1.0, baseSaturation))           
                        chroma = colourValue * colourSaturation
                        if hasattr(land, 'hueDrift'):
                            huePrime = ((land.hue + relativeElevation
                                * land.hueDrift) % 360.0) / 60.0
                        else:
                            huePrime = (land.hue % 360.0) / 60.0
                        xTerm = chroma * (1.0 - abs((huePrime % 2.0) - 1.0))
                        if huePrime < 1.0:
                            colourBase = (chroma, xTerm, 0.0)
                        else:
                            if huePrime < 2.0:
                                colourBase = (xTerm, chroma, 0.0)
                            else:
                                if huePrime < 3.0:
                                    colourBase = (0.0, chroma, xTerm)
                                else:
                                    if huePrime < 4.0:
                                        colourBase = (0.0, xTerm, chroma)
                                    else:
                                        if huePrime < 5.0:
                                            colourBase = (xTerm, 0.0, chroma)
                                        else:
                                            colourBase = (chroma, 0.0, xTerm)
                        chromaGap = colourValue - chroma
                        boxColour = (int(255.0 * (colourBase[0] + chromaGap)),
                            int(255.0 * (colourBase[1] + chromaGap)),
                            int(255.0 * (colourBase[2] + chromaGap)))             
                pygame.draw.rect(sitMap, boxColour, outCorners)   
        collisionDict = {}
        for landmarkName, (x, y) in Unit.landmarks.items():
            if (x > xMin) and (x < xMax) and (y > yMin) and (y < yMax):
                collisionDict[(x, y)] = 1
                centreX = int((0.5 + x - xMin) * zoom)
                centreY = int((0.5 + y - yMin) * zoom)
                markText = "".join(["     ", landmarkName])
                if Unit.bridges.has_key(landmarkName):
                    lableFont = Messenger.bridgeFont
                    dotRadius = Messenger.sitBridgeRadius                
                else:
                    lableFont = Messenger.landmarkFont
                    dotRadius = Messenger.sitDotRadius                
                textSurface = lableFont.render(markText, True,
                    (0, 0, 0), (255, 255, 255))
                sitMap.blit(textSurface, (centreX - dotRadius - 1,
                    centreY - dotRadius - 1)) 
                pygame.draw.circle(sitMap, Messenger.landmarkColour, (centreX,
                    centreY), dotRadius)
        stateDescription = Set()
        for identity, unitObj in Unit.roster.items():
            if (not showMessengers) and isinstance(unitObj, Messenger):
                continue
            x, y = unitObj.coordinates
            if (x > xMin) and (x < xMax) and (y > yMin) and (y < yMax):
                if not isinstance(unitObj, Messenger):
                    stateDescription.add((identity, (x, y)),)
                side       = unitObj.side
                leftX      = (x - xMin) * zoom
                leftY      = (y - yMin) * zoom
                outCorners = (leftX + Messenger.sitUnitBorder,
                    leftY + Messenger.sitUnitBorder, Messenger.sitUnitBoxSize,
                    Messenger.sitUnitBoxSize)
                boxColour = Unit.sideNames[side][1]
                if isinstance(unitObj, Messenger):
                    unitText = "".join(["     ", identity.join(["(", ")"])])
                    textSurface = Messenger.unitFont.render(unitText, True,
                        (0, 0, 0), (255, 255, 255))                    
                else:
                    lastMove = unitObj.lastMovement.strftime(
                        Messenger.captionDateForm)
                    topLine  = "".join(["     ", identity,
                        " stationary since ", lastMove])
                    terrain     = Destination.landDict[(x, y)]
                    terrainType = terrain.__class__.__name__
                    elevation   = terrain.elevation
                    bottomLine  = "".join(["      in ", terrainType, " ",
                        str(int(elevation)), "m above sea level"])
                    topX, topY  = Messenger.unitFont.size(topLine)
                    btmX, btmY  = Messenger.unitFont.size(bottomLine)
                    widest      = max(topX, btmX)
                    tallest     = max(topY, btmY)
                    lineHeight  = Messenger.unitFont.get_linesize()
                    textSurface = pygame.Surface((widest,
                        tallest + lineHeight), 0, 32)
                    if collisionDict.has_key((x, y),) and (collisionDict[(x,
                        y)] > 3):
                        topSurf = Messenger.unitFont.render(topLine, True,
                            (0, 0, 0))
                        btmSurf = Messenger.unitFont.render(bottomLine, True,
                            (0, 0, 0))                
                    else:
                        textSurface.fill((255, 255, 255),)
                        topSurf = Messenger.unitFont.render(topLine, True,
                            (0, 0, 0), (255, 255, 255))
                        btmSurf = Messenger.unitFont.render(bottomLine, True,
                            (0, 0, 0), (255, 255, 255))
                    textSurface.blit(topSurf, (0, 0))
                    textSurface.blit(btmSurf, (0, lineHeight))
                if collisionDict.has_key((x, y),):
                    overlaps               = collisionDict[(x, y)]
                    angle                  = -90 * overlaps
                    textSurface            = pygame.transform.rotate(textSurface, angle)
                    collisionDict[(x, y)] += 1
                else:
                    collisionDict[(x, y)] = 1
                    angle                 = 0
                textHeight    = textSurface.get_height()
                quarterHeight = textHeight / 4                
                if angle == 0:
                    if isinstance(unitObj, Messenger):
                        sitMap.blit(textSurface, (leftX, leftY))
                    else:
                        sitMap.blit(textSurface, (leftX,
                            leftY - quarterHeight))
                else:
                    angle = angle % 360
                    if angle >= 270:
                        textX = 0
                        textY = 0
                    elif angle >= 180:
                        textX = textSurface.get_width()
                        textY = 0
                    elif angle >= 90:
                        textX = textSurface.get_width()
                        textY = textHeight
                    else:
                        textX = 0
                        textY = textHeight
                    sitMap.blit(textSurface, (leftX - textX, leftY + textY))
                pygame.draw.rect(sitMap, boxColour, outCorners)
                pygame.draw.rect(sitMap, (0, 0, 0), outCorners, 1)                    
        if (Messenger.lastPerfect == stateDescription) and testForDouble:
            return False
        if testForDouble:
            Messenger.lastPerfect = stateDescription
        pygame.draw.rect(sitMap, (0, 0, 0), (0, 0, width,
            height), Messenger.sitBorder)    
        textSurface = Messenger.mapFont.render(captionText, True, 
            (0, 0, 0), (255, 255, 255))
        sitMap.blit(textSurface, (Messenger.sitBorder, Messenger.sitBorder))
        pygame.image.save(sitMap, sitMapFname.lower())
        return True
    
    commander      = property(_getCommander, _setCommander)
    makeFilename   = staticmethod(makeFilename)
    savePerfectMap = staticmethod(savePerfectMap)



class Adjutant(Messenger):
    def __init__(self, side=None, identity=None,
        intentionDict=IntentionDict()):
        self.intentionDict = intentionDict
        self.report        = {}
        self.side          = side
        self.identity      = identity

    def __del__(self):
        pass

    def advance(self, grains):
        pass    

    def friendlyContact(self, friendlyUnit):
        pass

    def deliverMessage(self, friendlyUnit):
        pass
        
    def deliverReport(self, receiver):
        self.report = copy(self.intentionDict)
        self.saveSituationMap(receiver)

    def _getCommander(self):
        return None
        
    def _setCommander(self, newCom):
        pass



class Order(object):
    halt              = 'halt'
    withdraw          = 'withdraw'
    proceed           = 'proceed'
    attack            = 'attack'
    minWithdraw       = 3600         # meters
    maxWithdraw       = 23600        # meters
    withdrawDistances = [float(dist) / ElevGrid.squareSize for dist in
        range(minWithdraw, maxWithdraw, int(ElevGrid.squareSize + 1.0))]

    def __init__(self, unit=None, destinationSequence=None, disposition=None):
        self.unit                = unit
        self.destinationSequence = destinationSequence
        self.disposition         = disposition
        
    def __eq__(self, otherOrder):
        if isinstance(otherOrder, Order):
            if (self.unit != otherOrder.unit) or (self.disposition !=
                otherOrder.disposition):
                return False
            for ind, dest in enumerate(self.destinationSequence):
                otherDest = otherUnit.destinationSequence[ind]
                if dest != otherDest:
                    return False
            return True
        return False
        
    def __ne__(self, otherOrder):
        return not Order.__eq__(self, otherOrder)
        


class Commander(Unit):
    def __init__(self, side=None, coords=None, identity=None,
        baseIntercept=Unit.defaultBaseIntercept,
        interceptDict=Unit.defaultInterceptDict, intentionDict=IntentionDict(),
        currentOrder=None, progressList=None):
        Position.__init__(self, coords)
        self.setup(side, coords, identity.upper(), baseIntercept,
            interceptDict, intentionDict, currentOrder, progressList)
        self.lastSight    = Set()
        self.outBox       = {}
        self.subordinates = {}

    def command(self, targetUnit):
        if isinstance(targetUnit, Unit):
            targetUnit.messenger.commander         = self
            self.subordinates[targetUnit.identity] = targetUnit
        elif isinstance(targetUnit, str):
            if Unit.roster.has_key(targetUnit):
                self.command(Unit.roster[targetUnit])
            else:
                print "Unknown unit. For a list of all units, ",
                print "type 'Unit.showUnits()'"
        else:
            print "first argument should be a Unit or string"
            raise TypeError

    def absorb(self, targetUnit):
        if isinstance(targetUnit, Unit):
            del Unit.roster[self.identity]
            self.coordinates = targetUnit.coordinates
            self.identity    = " commanding ".join([self.identity,
                targetUnit.identity])
            self.baseSpeed   = targetUnit.baseSpeed
            del Unit.roster[targetUnit.identity]
            del Unit.roster[targetUnit.messenger.identity]
            del targetUnit.messenger
            del targetUnit
            Unit.roster[self.identity] = self
            messengerKnows = copy(self.intentionDict)
            messengerKnows.update({self.identity: (self.coordinates, self.order,
                self.progress, copy(Unit.time))})
            self.messenger = Messenger(self.side, self.coordinates, "".join([self.identity,
                Unit.messengerSuffix]), self, messengerKnows)            
            self.command(self)
        elif isinstance(targetUnit, str):
            if Unit.roster.has_key(targetUnit):
                self.absorb(Unit.roster[targetUnit])
            else:
                print "Unknown unit. For a list of all units, ",
                print "type 'Unit.showUnits()'"
        else:
            print "first argument should be a Unit or string"
            raise TypeError

    def giveOrder(self, targetUnit, destSeq, disposition=Order.proceed,
        isAddendum=False, printdescription=True):
        if isinstance(targetUnit, str):
            if Unit.roster.has_key(targetUnit):
                targetUnit = Unit.roster[targetUnit]
            else:
                print "Unknown unit. For a list of all units, ",
                print "type 'Unit.showUnits()'"
                return False
        elif not isinstance(targetUnit, Unit):
            print "first argument should be a string or Unit"
            raise TypeError
        if targetUnit.side == self.side:
            if isinstance(destSeq, Destination):
                destSeq = [destSeq]
            elif isinstance(destSeq, str):
                if Unit.landmarks.has_key(destSeq):
                    destSeq = [Destination(destSeq)]
                else:
                    print "Unknown landmark. For a list of all landmarks,",
                    print "type 'Unit.showLandmarks()'"
                    return False
            elif hasattr(destSeq, '__len__'):
                if len(destSeq) == 2:
                    destSeq = [Destination(destSeq)]
                elif len(destSeq) == 1:
                    if isinstance(destSeq[0], str):
                        if Unit.landmarks.has_key(destSeq[0]):
                            destSeq = [Destination(destSeq[0])]
                        else:
                            print "Unknown landmark. For a list of all",
                            print "landmarks, type 'Unit.showLandmarks()'"
                            return False
                    elif hasattr(destSeq[0], '__len__'):
                        if len(destSeq[0]) == 2:
                            destSeq = [Destination(destSeq[0])]
                        else:
                            print "second argument should be a string,",
                            print "a sequence of strings, a Destination,",
                            print "a sequence of Destinations,",
                            print "a coordinate tuple,",
                            print "a sequence of coordinate tuples,",
                            print "a coordinate list or a sequence of",
                            print "coordinate lists"
                            raise TypeError
            else:
                print "second argument should be a string,",
                print "a sequence of strings, a Destination,",
                print "a sequence of Destinations,",
                print "a coordinate tuple,",
                print "a sequence of coordinate tuples,",
                print "a coordinate list or a sequence of",
                print "coordinate lists"
                raise TypeError            
            if (targetUnit.order is not None):
                if disposition == targetUnit.disposition:
                    duplicateFlag = True
                    for ind, newDest in enumerate(destSeq):
                        existingDest = targetUnit.order[ind]
                        if existingDest != newDest:
                            duplicateFlag = False
                            break
                    if duplicateFlag:
                        return False
            targetCoord    = targetUnit.coordinates
            messengerCoord = targetUnit.messenger.coordinates
            if isAddendum:
                newOrder = Addendum(targetUnit, destSeq, disposition)
            else:
                newOrder = Order(targetUnit, destSeq, disposition)
            if messengerCoord == self.coordinates:
                targetUnit.messenger.message = newOrder
                if printdescription:
                    print "handing new order to messenger"
            else:
                self.outBox[targetUnit.identity] = newOrder
                if printdescription:
                    print "adding new order to outbox"
            return True
        print "Commander belongs to", Unit.sideNames[self.side][0]
        print targetUnit.identity, "belongs to", Unit.sideNames[targetUnit.side][0]
        print "Commander cannot give orders to enemy units"
        return False



class CommandDetail(Commander):
    defaultBaseSpeed = 200           # flat-road-meters every six minutes

    def __init__(self, side=None, coords=None, identity=None,
        baseIntercept=Unit.defaultBaseIntercept,
        interceptDict=Unit.defaultInterceptDict, intentionDict=IntentionDict(),
        currentOrder=None, progressList=None):
        Commander.__init__(self, side, coords, identity, baseIntercept,
            interceptDict, intentionDict, currentOrder, progressList)
        messengerKnows = copy(self.intentionDict)
        messengerKnows.update({self.identity: (self.coordinates, self.order,
            self.progress, copy(Unit.time))})
        self.messenger = Messenger(self.side, self.coordinates, "".join([self.identity,
            Unit.messengerSuffix]), self, messengerKnows)            
        self.command(self)



class Huscarls(Unit):
    defaultBaseSpeed = 250           # flat-road-meters every six minutes



class KentishRoyalGuard(Unit):
    defaultBaseSpeed = 200           # flat-road-meters every six minutes
    
    
    
class KnightsEcstatic(Unit):
    defaultBaseSpeed = 250           # flat-road-meters every six minutes
    
    
    
class Skirmishers(Unit):
    defaultBaseSpeed = 300           # flat-road-meters every six minutes



class Churls(Unit):
    defaultBaseSpeed = 250           # flat-road-meters every six minutes



class Thanes(Unit):
    defaultBaseSpeed = 250           # flat-road-meters every six minutes
    
    
    
class BretonColonialGuard(Unit):
    defaultBaseSpeed = 200           # flat-road-meters every six minutes
    
    
    
class CumbrianKnights(Unit):
    defaultBaseSpeed = 450           # flat-road-meters every six minutes



class Raiders(Unit):
    defaultBaseSpeed = 350           # flat-road-meters every six minutes



class HoneyEaters(Unit):
    defaultBaseSpeed = 250           # flat-road-meters every six minutes
    
    
    
class KingsGuard(Unit):
    defaultBaseSpeed = 200           # flat-road-meters every six minutes
    
    
    
class MercianGuard(Unit):
    defaultBaseSpeed = 200           # flat-road-meters every six minutes



class NormanCavalry(Unit):
    defaultBaseSpeed = 450           # flat-road-meters every six minutes



class WarParty(Unit):
    defaultBaseSpeed = 300           # flat-road-meters every six minutes
    
    
    
class LightCavalry(Unit):
    defaultBaseSpeed = 500           # flat-road-meters every six minutes



class WelshKnightsEcstatic(Unit):
    defaultBaseSpeed = 400           # flat-road-meters every six minutes



class WelshPilgrims(Unit):
    defaultBaseSpeed = 300           # flat-road-meters every six minutes



class CornishLozenge(Unit):
    defaultBaseSpeed = 300           # flat-road-meters every six minutes



class NorthumbrianManiple(Unit):
    defaultBaseSpeed = 200           # flat-road-meters every six minutes



class Mercenaries(Unit):
    defaultBaseSpeed = 200           # flat-road-meters every six minutes



class PressGang(Unit):
    defaultBaseSpeed = 250           # flat-road-meters every six minutes
    


class Addendum(Order):
    pass



class Destination(object):
    _minimumRowOffset = 0.0000001
    junctionMeanCost  = 0.0
    landDict          = {}
    pathLookup        = {}
    lookupFilename    = "paths.txt"
    
    def __init__(self, landmark=None, offset=None):
        self.path = []
        if isinstance(landmark, str):
            if Unit.landmarks.has_key(landmark):
                self.landmark = Unit.landmarks[landmark]
            else:
                print "Unknown landmark. For a list of all landmarks, type 'Unit.showLandmarks()'"
        else:
            self.landmark = landmark
        self.offset = offset
        if offset is None:
            self.target = self.landmark
        else:
            self._findTarget()
    
    def __eq__(self, otherDest):
        if isinstance(otherDest, Destination):
            if hasattr(self, 'target'):
                if hasattr(otherDest, 'target'):
                    return self.target == otherDest.target
                return False
            return not hasattr(otherDest, 'target')
        return False
        
    def __ne__(self, otherDest):
        return not Destination.__eq__(self, otherDest)
    
    def _findTarget(self):
        landX, landY = self.landmark
        offX, offY   = self.offset.coordinates
        wayX, wayY   = landX + int(offX), landY + int(offY)
        wayTile     = Destination.landDict[(wayX, wayY)]
        if isinstance(wayTile, Water) or wayTile.__class__.costFactor is None:
            self.target = landX, landY
        else:
            self.target = wayX, wayY
        if self.offset.toIn or self.offset.toNextTo:
            directionTuple = {True: -1, False: 1}
            xDirection     = directionTuple[offX < 0.0]
            yDirection     = directionTuple[offY < 0.0]
            rowLine        = yDirection / 2.0
            columnLine     = xDirection / 2.0
            coord          = self.target
            newTile        = None
            blocked        = False
            while (self.offset.landClass is not newTile.__class__):
                oldTile = Destination.landDict[coord]
                self.target = coord
                if abs(offX) < Destination._minimumRowOffset:
                    columnIntercept = 0.0
                else:
                    gradient        = float(offY) / offX
                    columnIntercept = gradient * columnLine
                if abs(columnIntercept) > abs(rowLine):
                    rowLine += yDirection
                    coord    = self.target[0], self.target[1] + yDirection
                else:
                    columnLine += xDirection
                    coord       = self.target[0] + xDirection, self.target[1]
                newTile = Destination.landDict[coord]
                if isinstance(newTile, Water):
                    blocked = True
                    for junct in oldTile:
                        if junct.land == newTile and junct.road:
                            blocked = False
                            break
                    if blocked:
                        break
            if self.offset.toIn and not blocked:
                self.target = coord
        
    def _reconstructPath(self, originCoord, useLookup=True):
        currentCoord = self.target
        treeParent   = Destination.landDict[currentCoord]
        self.path    = [treeParent]
        while currentCoord != originCoord:
            currentLand = treeParent
            treeParent  = currentLand.treeParent
            self.path.append(treeParent)
            currentCoord = treeParent.coordinates
        self.path.reverse()
        if useLookup:
            lookupKey                         = (originCoord, self.target)
            Destination.pathLookup[lookupKey] = [land.coordinates for land in self.path]

    def findPath(self, originCoord, printdescription=False, useLookup=True):
        if useLookup:
            lookupKey = (originCoord, self.target)
            if Destination.pathLookup.has_key(lookupKey):
                if Destination.pathLookup[lookupKey]:
                    if printdescription:
                        print "lookup table has path from", originCoord, "to", self.target
                    self.path = [Destination.landDict[coord] for coord in Destination.pathLookup[lookupKey]]
                    return True
                elif Destination.pathLookup[lookupKey] is False:
                    return False
        if originCoord == self.target:
            if useLookup:
                lookupKey                         = (originCoord, self.target)
                Destination.pathLookup[lookupKey] = False            
            return False
        if printdescription:
            print "finding path from", originCoord, "to", self.target
        for land in Destination.landDict.values():
            land.estimateSet = False
            land.pathCostSet = False
        targetLand = Destination.landDict[self.target]
        if isinstance(targetLand, Water):
            if len(targetLand.neighbourhood) == 0:
                if useLookup:
                    lookupKey                         = (originCoord, self.target)
                    Destination.pathLookup[lookupKey] = False            
                return False                
        originLand          = Destination.landDict[originCoord]        
        visitedCoords       = {}
        landQueue           = []
        originLand.pathcost = 0.0
        originLand.estimate = 0.0            
        heapq.heapify(landQueue)    
        heapq.heappush(landQueue, originLand)
        while len(landQueue) > 0:
            currentLand  = heapq.heappop(landQueue)
            currentCoord = currentLand.coordinates
            if not visitedCoords.has_key(currentCoord):
                if currentLand == targetLand:
                    self._reconstructPath(originCoord, useLookup)
                    return True
                for treeJunct in currentLand:
                    treeChild  = treeJunct.land
                    childCoord = treeChild.coordinates
                    if ((treeChild not in landQueue) and
                        (not visitedCoords.has_key(childCoord))):
                        treeChild.pathcost   = currentLand.pathcost + treeJunct
                        treeChild.treeParent = currentLand
                        if not treeChild.estimateSet:
                            xDisp              = childCoord[0] - self.target[0]
                            yDisp              = childCoord[1] - self.target[1]
                            distance           = sqrt(xDisp * xDisp +
                                yDisp * yDisp)
                            treeChild.estimate = (distance * 
                                Destination.junctionMeanCost)                                         
                        heapq.heappush(landQueue, treeChild)
                        landQueue.sort(Land.queueOrder)                        
                    visitedCoords[currentCoord] = True
        if useLookup:
            lookupKey                         = (originCoord, self.target)
            Destination.pathLookup[lookupKey] = False 
        return False

    def setLandDict(lands):
        if isinstance(lands, ElevGrid):
            Destination._setLandDict(lands.landDict())
        elif isinstance(lands, dict):
            Destination.landDict = lands
        elif (isinstance(lands, tuple) or isinstance(lands, list) or
            isinstance(lands, str)):
            Destination._setLandDict(ElevGrid(lands).landDict())
        totalCost     = 0.0
        junctionCount = 0
        for land in Destination.landDict.values():
            totalCost     += sum(land)
            junctionCount += len(land)
        Destination.junctionMeanCost = totalCost / float(junctionCount)
        Destination.loadPathLookup()

    def loadPathLookup(filename=lookupFilename, printdescription=True):
        if printdescription:
            print "Loading lookup table for Destination.findPath()"
        try:
            lookupFile = open(filename, "rb")
            Destination.pathLookup = cPickle.load(lookupFile)
            lookupFile.close()            
        except IOError:
            if printdescription:
                print "\tNone found"

    def savePathLookup(filename=lookupFilename):
        lookupFile = open(filename, "wb")
        cPickle.dump(Destination.pathLookup, lookupFile, cPickle.HIGHEST_PROTOCOL)
        lookupFile.close()

    def scale(x, y, length):
        if y != 0.0:
            c                = abs(x / y)
            lengthSquare     = length * length
            cSquare          = c * c
            newX             = cmp(length, 0.0) * cmp(x, 0.0) * sqrt((
                lengthSquare * cSquare) / (cSquare + 1.0))
            newXSquare       = newX * newX
            squareDifference = lengthSquare - newXSquare
            if squareDifference > 0.0:
                newY = cmp(length, 0.0) * cmp(y, 0.0) * sqrt(squareDifference)
                return (newX, newY)
            return (newX, 0.0)
        if x != 0.0:
            return (cmp(x, 0.0) * length, 0.0)
        return (0.0, 0.0)    
    
    loadPathLookup = staticmethod(loadPathLookup)
    savePathLookup = staticmethod(savePathLookup)
    setLandDict    = staticmethod(setLandDict)
    scale          = staticmethod(scale)
    


class Offset(Position):
    kmPerCell = 2.5
    
    def __init__(self, (x, y), landClass=None, toIn=False, toNextTo=False):
        Position.__init__(self, (x / Offset.kmPerCell, y / Offset.kmPerCell))
        self.toIn      = toIn
        self.toNextTo  = toNextTo
        self.landClass = landClass



if __name__ == "__main__":
    Unit.start()
    Unit.showUnits()
    
    if False:
        
        eg2 = ElevGrid(("uktopo.tga", "veg2.tga", "river.tga", "roads2.tga"),)
        Unit.setTime()
        Destination.setLandDict(eg2.landDict())
        offs = Offset((5.0, -2.5),)
        dest = Destination((220, 260), offs)
        dest2 = Destination((222, 259),)
        hq = Commander(1, (225, 280), "hq")
        mordor = Commander(2, (215, 205), "mordor")
        knight = Unit(1, (228, 300), "Galahad")
        knight.messenger.commander = hq
        knight.order = [dest]
        knight.disposition = Order.withdraw
        churl = Unit(2, (225, 225), "Churl")
        churl.messenger.commander = mordor
        churl.order = [dest2]
        churl.disposition = Order.attack
        justOnce = True
        for i in range(0, 500):
            result = Unit.nextEvent()
            print result[0]
            for eventDescription in result[1]:
                print eventDescription
            print
            for key, value in Unit.roster.items():
                if value.order is None:
                    goingTo = "destination not set"
                else:
                    goingTo = " " .join(["going to", str(value.order[0].target)])
                print key, " -> ", value, goingTo
            #    for poritionKey, portion in value.intentionDict.items():
            #        print "\t", poritionKey, " : ", portion
            #    print
            print "\n--------------------------------------------\n"
            if Unit.time.day == 22 and justOnce:
                hq.giveOrder('Galahad', 'Allergen-by-the-Sea', Order.proceed)
                justOnce = False
    
    if False:
    
        OUT_FILE = "testing.bmp"
        OUT_FILE_PREFIX = "testing"
        OUT_FILE_SUFFIX = ".bmp"
        #pNeighbours = [Junction(5.0, []), Junction(1.0, [])]
        #qNeighbours = [Junction(8.0, []),]
        #p = Land(pNeighbours)
        #q = Land(qNeighbours)
        #print p > p
        #print p > q
        #print q > p
        #print q > q
        #eg1 = ElevGrid({(1, 2): 2, (3, 4): 4}, 7, 5)
        #print
        #print eg1
        eg2 = ElevGrid(("uktopo.tga", "veg2.tga", "river.tga", "roads2.tga"),)
        #eg2 = ElevGrid(("uktopo.tga", "veg2.tga", "", "roads.tga"),)
        #print
        #print eg2
        #fullList = eg2.landList()
        fullDict = eg2.landDict()

        Destination.setLandDict(fullDict)
        #offs = Offset((2, -1), BroadleafWoodland, True)
        offs = Offset((2, -1),)
        dest = Destination((220, 260), offs)
        #dest.findPath((228, 300),)
        dest2 = Destination((210, 310),)
        #dest2.findPath((222, 259),)
        #print "dest target:", dest.target
        #for n, landTile in enumerate(dest.path):
        #    print "dest", n, landTile.summary
        #print
        #print "dest2 target:", dest2.target
        #for n, landTile in enumerate(dest2.path):
        #    print "dest2", n, landTile.summary
        #print

        knight = Unit((228, 300), "Galahad")
        knight.order = [dest, dest2]
        advanceResult = knight.advance(500)
        while advanceResult:
            print advanceResult, knight.coordinates
            advanceResult = knight.advance(500)

        pathcoords = [landTile.coordinates for landTile in dest.path] + [landTile.coordinates for landTile in dest2.path]

        fullList = fullDict.values()
        highestPeak = max([land.elevation for land in fullList])    
        import pygame
        BACKGROUND_COLOUR = (0, 0, 51)
        MIN_SATURATION = 0.1
        SATURATION_COEFFS = [0.958, 0.338, -1.181]
        MIN_COLOUR_VALUE = 0.2
        screen = pygame.display.set_mode((336, 418),)

        """
        for kindOfLand in AdoptionType.classIndex.values():
            outFilename = "".join([OUT_FILE_PREFIX, kindOfLand.__name__.lower(), OUT_FILE_SUFFIX])
            print outFilename
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, 336, 418))
            for land in fullList:
                if land.__class__ is kindOfLand:
                    x, y = land.coordinates     
                    if land.elevation == 0:
                        alternColour = BACKGROUND_COLOUR
                    else:
                        colourValueRange = 1.0 - MIN_COLOUR_VALUE
                        relativeElevation = land.elevation / highestPeak
                        colourValue = MIN_COLOUR_VALUE + relativeElevation * colourValueRange
                        baseSaturation = ( SATURATION_COEFFS[0] 
                                         + SATURATION_COEFFS[1] * colourValue 
                                         + SATURATION_COEFFS[2] * colourValue * colourValue )
                        if hasattr(land, 'relativeSaturation'):
                            baseSaturation *= land.relativeSaturation
                        colourSaturation = max(MIN_SATURATION, min(1.0, baseSaturation))           
                        chroma = colourValue * colourSaturation
                        if hasattr(land, 'hueDrift'):
                            huePrime = ((land.hue + relativeElevation * land.hueDrift) % 360.0) / 60.0
                        else:
                            huePrime = (land.hue % 360.0) / 60.0
                        xTerm = chroma * (1.0 - abs((huePrime % 2.0) - 1.0))
                        if huePrime < 1.0:
                            colourBase = (chroma, xTerm, 0.0)
                        else:
                            if huePrime < 2.0:
                                colourBase = (xTerm, chroma, 0.0)
                            else:
                                if huePrime < 3.0:
                                    colourBase = (0.0, chroma, xTerm)
                                else:
                                    if huePrime < 4.0:
                                        colourBase = (0.0, xTerm, chroma)
                                    else:
                                        if huePrime < 5.0:
                                            colourBase = (xTerm, 0.0, chroma)
                                        else:
                                            colourBase = (chroma, 0.0, xTerm)
                        chromaGap = colourValue - chroma
                        alternColour = (255.0 * (colourBase[0] + chromaGap), 
                                        255.0 * (colourBase[1] + chromaGap), 
                                        255.0 * (colourBase[2] + chromaGap))
                    screen.set_at((x, y), alternColour)  
            pygame.display.flip()    
            pygame.image.save(screen, outFilename)
        """
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, 336, 418))
        for land in fullList:
            x, y = land.coordinates
            if (x, y) in pathcoords:
                alternColour = (255, 223, 223)
            elif land.elevation == 0:
                alternColour = BACKGROUND_COLOUR
            else:
                colourValueRange = 1.0 - MIN_COLOUR_VALUE
                relativeElevation = land.elevation / highestPeak
                colourValue = MIN_COLOUR_VALUE + relativeElevation * colourValueRange
                baseSaturation = ( SATURATION_COEFFS[0] 
                                 + SATURATION_COEFFS[1] * colourValue 
                                 + SATURATION_COEFFS[2] * colourValue * colourValue )
                if hasattr(land, 'relativeSaturation'):
                    baseSaturation *= land.relativeSaturation
                colourSaturation = max(MIN_SATURATION, min(1.0, baseSaturation))           
                chroma = colourValue * colourSaturation
                if hasattr(land, 'hueDrift'):
                    huePrime = ((land.hue + relativeElevation * land.hueDrift) % 360.0) / 60.0
                else:
                    huePrime = (land.hue % 360.0) / 60.0
                xTerm = chroma * (1.0 - abs((huePrime % 2.0) - 1.0))
                if huePrime < 1.0:
                    colourBase = (chroma, xTerm, 0.0)
                else:
                    if huePrime < 2.0:
                        colourBase = (xTerm, chroma, 0.0)
                    else:
                        if huePrime < 3.0:
                            colourBase = (0.0, chroma, xTerm)
                        else:
                            if huePrime < 4.0:
                                colourBase = (0.0, xTerm, chroma)
                            else:
                                if huePrime < 5.0:
                                    colourBase = (xTerm, 0.0, chroma)
                                else:
                                    colourBase = (chroma, 0.0, xTerm)
                chromaGap = colourValue - chroma
                alternColour = (255.0 * (colourBase[0] + chromaGap), 
                                255.0 * (colourBase[1] + chromaGap), 
                                255.0 * (colourBase[2] + chromaGap))
            screen.set_at((x, y), alternColour)  
        for land in fullList:
            x, y = land.coordinates
            for junct in land:
                if junct.road and ((x, y) not in pathcoords):
                    screen.set_at((x, y), (255, 0, 0))
                    break

        pygame.display.flip()    
        pygame.image.save(screen, OUT_FILE)        
