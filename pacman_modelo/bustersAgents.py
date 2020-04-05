# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
from wekaI import Weka
import inference
import busters

instancias = []
lastMoves = []
lastMoves.append(Directions.STOP)
lastLegal = []
lastLegal.append('Stop')


class NullGraphics:
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs


class BustersAgent:
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable
	self.weka = Weka()
	self.weka.start_jvm()

    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
        #for index, inf in enumerate(self.inferenceModules):
        #    if not self.firstMove and self.elapseTimeEnable:
        #        inf.elapseTime(gameState)
        #    self.firstMove = False
        #    if self.observeEnable:
        #        inf.observeState(gameState)
        #    self.ghostBeliefs[index] = inf.getBeliefDistribution()
        #self.display.updateDistributions(self.ghostBeliefs)
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
        return Directions.STOP

class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        return KeyboardAgent.getAction(self, gameState)
        
    def printLineData(self, gameState):
        if len(instancias) == 4:
            instancias.pop(0)
        #Posicion Pacman
        cadena = str(gameState.getPacmanPosition()[0])+","+str(gameState.getPacmanPosition()[1])+","
        #Acciones legales
        listaAcciones = ["North", "East", "South", "West", "Stop"]
        for i in range(len(listaAcciones)):
            if listaAcciones[i] in gameState.getLegalPacmanActions():
                cadena = cadena+str(1)+","
            else:
                cadena = cadena+str(0)+","
        #Posicion de los fantasmas
        sobran = 4-len(gameState.getGhostPositions())
        for i in range(len(gameState.getGhostPositions())):
            cadena = cadena + str(gameState.getGhostPositions()[i][0])+","+str(gameState.getGhostPositions()[i][1])+","
        if sobran>0:
            for i in range(sobran):
                cadena = cadena+str(-1)+","+str(-1)+","
        #Distancia a los fantasmas
        for i in range(len(gameState.data.ghostDistances)):
            if gameState.data.ghostDistances[i] != None:
                cadena = cadena + str(gameState.data.ghostDistances[i])+","
            else:
                cadena = cadena + str(-1)+","
        if sobran>0:
            for i in range(sobran):
                cadena = cadena + str(-1)+","
        #Distancia a la comidas
        distanciaComida = gameState.getDistanceNearestFood()
	if distanciaComida == None:
	    cadena = cadena + str(-1)+","
	else:
            cadena = cadena + str(distanciaComida)+","
        #Direccion
        cadena = cadena + gameState.data.agentStates[0].getDirection()+","
        #Scores
        cadena = cadena + str(gameState.getScore()) 
        for i in range(len(instancias)):
            instancias[i] = instancias[i]+","+str(gameState.getScore())
        instancias.append(cadena)
        if len(instancias) == 4:
            return instancias[0]+"\n"
        else:
            return ""

from distanceCalculator import Distancer
from game import Actions
from game import Directions
import random, sys

'''Random PacMan Agent'''
class RandomPAgent(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        ##print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table
        
    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move
        
class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def chooseAction(self, gameState):
        """
        First computes the most likely position of each ghost that has
        not yet been captured, then chooses an action that brings
        Pacman closer to the closest ghost (according to mazeDistance!).

        To find the mazeDistance between any two positions, use:
          self.distancer.getDistance(pos1, pos2)

        To find the successor position of a position after an action:
          successorPosition = Actions.getSuccessor(position, action)

        livingGhostPositionDistributions, defined below, is a list of
        util.Counter objects equal to the position belief
        distributions for each of the ghosts that are still alive.  It
        is defined based on (these are implementation details about
        which you need not be concerned):

          1) gameState.getLivingGhosts(), a list of booleans, one for each
             agent, indicating whether or not the agent is alive.  Note
             that pacman is always agent 0, so the ghosts are agents 1,
             onwards (just as before).

          2) self.ghostBeliefs, the list of belief distributions for each
             of the ghosts (including ghosts that are not alive).  The
             indices into this list should be 1 less than indices into the
             gameState.getLivingGhosts() list.
        """
        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]
        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = \
            [beliefs for i, beliefs in enumerate(self.ghostBeliefs)
             if livingGhosts[i+1]]
        return Directions.EAST

class BasicAgentAA(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        #print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table

    def printInfo(self, gameState):
        print "---------------- TICK ", self.countActions, " --------------------------"
        # Dimensiones del mapa
        width, height = gameState.data.layout.width, gameState.data.layout.height
        print "Width: ", width, " Height: ", height
        # Posicion del Pacman
        print "Pacman position: ", gameState.getPacmanPosition()
        # Acciones legales de pacman en la posicion actual
        print "Legal actions: ", gameState.getLegalPacmanActions()
        # Direccion de pacman
        print "Pacman direction: ", gameState.data.agentStates[0].getDirection()
        # Numero de fantasmas
        print "Number of ghosts: ", gameState.getNumAgents() - 1
        # Fantasmas que estan vivos (el indice 0 del array que se devuelve corresponde a pacman y siempre es false)
        print "Living ghosts: ", gameState.getLivingGhosts()
        # Posicion de los fantasmas
        print "Ghosts positions: ", gameState.getGhostPositions()
        # Direciones de los fantasmas
        print "Ghosts directions: ", [gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)]
        # Distancia de manhattan a los fantasmas
        print "Ghosts distances: ", gameState.data.ghostDistances
        # Puntos de comida restantes
        print "Pac dots: ", gameState.getNumFood()
        # Distancia de manhattan a la comida mas cercada
        print "Distance nearest pac dots: ", gameState.getDistanceNearestFood()
        # Paredes del mapa
        print "Map:  \n", gameState.getWalls()
        # Puntuacion
        print "Score: ", gameState.getScore()
        
    def chooseAction(self, gameState):
        #global lastLegal
	x = []
	print(x)
        self.countActions = self.countActions + 1
        self.printInfo(gameState)
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        posicionPacman = gameState.getPacmanPosition()
	x.append(posicionPacman[0])
	x.append(posicionPacman[1])
	#Acciones legales
        listaAcciones = ["North", "East", "South", "West", "Stop"]
        for i in range(len(listaAcciones)):
            if listaAcciones[i] in gameState.getLegalPacmanActions():
                x.append('1')
            else:
                x.append('0')
        #Posicion de los fantasmas
        sobran = 4-len(gameState.getGhostPositions())
        """for i in range(len(gameState.getGhostPositions())):
	    x.append(gameState.getGhostPositions()[i][0])
	    x.append(gameState.getGhostPositions()[i][1])
        if sobran>0:
            for i in range(sobran):
	  	x.append(-1)
		x.append(-1)"""
	#Distancia a los fantasmas
        for i in range(len(gameState.data.ghostDistances)):
            if gameState.data.ghostDistances[i] != None:
		x.append(gameState.data.ghostDistances[i])
            else:
		x.append(-1)
        if sobran>0:
            for i in range(sobran):
		x.append(-1)
	#Distancia a la comidas
	distanciaComida = gameState.getDistanceNearestFood()
	if distanciaComida == None:
	    x.append(-1)
	else:
	    x.append(distanciaComida)
	#Scores
	x.append(gameState.getScore())
        """disMin = 1000
        for i in range(len(distanciaFantasmas)):
            if distanciaFantasmas[i] < disMin and distanciaFantasmas[i] != None: disMin = distanciaFantasmas[i]
        indiceMin = distanciaFantasmas.index(disMin)
        fantasmaCercano = posicionFantasmas[indiceMin]
        restaX = fantasmaCercano[0]-posicionPacman[0]
        restaY = fantasmaCercano[1]-posicionPacman[1]
        #Diagonal derecha hacia arriba
        if (restaX > 0) and (restaY > 0):             
            if (lastMoves[len(lastMoves)-1]==Directions.EAST or lastMoves[len(lastMoves)-1]==Directions.NORTH or lastMoves[len(lastMoves)-1]==Directions.STOP):
                if Directions.EAST in legal: move = Directions.EAST
                else: 
                    if Directions.NORTH in legal: move = Directions.NORTH
                    else:
                        if Directions.WEST in legal: move = Directions.WEST
                        else:
                            move = Directions.SOUTH
            if (lastMoves[len(lastMoves)-1]==Directions.WEST):
                if Directions.NORTH in legal: move = Directions.NORTH
                else: 
                    if Directions.WEST in legal: move = Directions.WEST
                    else:
                        if Directions.SOUTH in legal: move = Directions.SOUTH
                        else:
                            move = Directions.EAST
            if (lastMoves[len(lastMoves)-1]==Directions.SOUTH): 
                if Directions.EAST in lastLegal:
                    if Directions.WEST in legal: move = Directions.WEST
                    else: 
                        if Directions.SOUTH in legal: move = Directions.SOUTH
                        else:
                            if Directions.EAST in legal: move = Directions.EAST
                            else:
                                move = Directions.NORTH
                else:
                    if Directions.EAST in legal: move = Directions.EAST
                    else: 
                        if Directions.SOUTH in legal: move = Directions.SOUTH
                        else:
                            if Directions.WEST in legal: move = Directions.WEST
                            else:
                                move = Directions.NORTH
        #Diagonal derecha hacia abajo
        if (restaX > 0) and (restaY < 0):                 
            if (lastMoves[len(lastMoves)-1]==Directions.EAST or lastMoves[len(lastMoves)-1]==Directions.SOUTH or lastMoves[len(lastMoves)-1]==Directions.STOP):
                if Directions.EAST in legal: move = Directions.EAST
                else: 
                    if Directions.SOUTH in legal: move = Directions.SOUTH
                    else:
                        if Directions.WEST in legal: move = Directions.WEST
                        else:
                            move = Directions.NORTH
            if (lastMoves[len(lastMoves)-1]==Directions.WEST):
                if Directions.SOUTH in legal: move = Directions.SOUTH
                else: 
                    if Directions.WEST in legal: move = Directions.WEST
                    else:
                        if Directions.NORTH in legal: move = Directions.NORTH
                        else:
                            move = Directions.EAST
            if (lastMoves[len(lastMoves)-1]==Directions.NORTH):
                if Directions.EAST in lastLegal:
                    if Directions.WEST in legal: move = Directions.WEST
                    else: 
                        if Directions.NORTH in legal: move = Directions.NORTH
                        else:
                            if Directions.EAST in legal: move = Directions.EAST
                            else:
                                move = Directions.SOUTH
                else:
                    if Directions.EAST in legal: move = Directions.EAST
                    else:
                        if Directions.NORTH in legal: move = Directions.NORTH
                        else:
                            if Directions.WEST in legal: move = Directions.WEST
                            else:
                                move = Directions.SOUTH
        #Diagonal izquierda hacia arriba
        if (restaX < 0) and (restaY > 0):  
            if (lastMoves[len(lastMoves)-1]==Directions.WEST or lastMoves[len(lastMoves)-1]==Directions.NORTH or lastMoves[len(lastMoves)-1]==Directions.STOP):
                if Directions.WEST in legal: move = Directions.WEST
                else: 
                    if Directions.NORTH in legal: move = Directions.NORTH
                    else:
                        if Directions.EAST in legal: move = Directions.EAST
                        else:
                            move = Directions.SOUTH
            if (lastMoves[len(lastMoves)-1]==Directions.EAST):
                if Directions.NORTH in legal: move = Directions.NORTH
                else: 
                    if Directions.EAST in legal: move = Directions.EAST
                    else:
                        if Directions.SOUTH in legal: move = Directions.SOUTH
                        else:
                            move = Directions.WEST
            if (lastMoves[len(lastMoves)-1]==Directions.SOUTH):
                if Directions.WEST in lastLegal:
                    if Directions.EAST in legal: move = Directions.EAST
                    else: 
                        if Directions.SOUTH in legal: move = Directions.SOUTH
                        else:
                            if Directions.WEST in legal: move = Directions.WEST
                            else:
                                move = Directions.NORTH
                else:
                    if Directions.WEST in legal: move = Directions.WEST
                    else: 
                        if Directions.SOUTH in legal: move = Directions.SOUTH
                        else:
                            if Directions.EAST in legal: move = Directions.EAST
                            else:
                                move = Directions.NORTH
        #Diagonal izquierda hacia abajo
        if (restaX < 0) and (restaY < 0):                      
            if (lastMoves[len(lastMoves)-1]==Directions.WEST or lastMoves[len(lastMoves)-1]==Directions.SOUTH or lastMoves[len(lastMoves)-1]==Directions.STOP):
                if Directions.WEST in legal: move = Directions.WEST
                else: 
                    if Directions.SOUTH in legal: move = Directions.SOUTH
                    else:
                        if Directions.EAST in legal: move = Directions.EAST
                        else:
                            move = Directions.NORTH
            if (lastMoves[len(lastMoves)-1]==Directions.EAST):
                if Directions.SOUTH in legal: move = Directions.SOUTH
                else: 
                    if Directions.EAST in legal: move = Directions.EAST
                    else:
                        if Directions.NORTH in legal: move = Directions.NORTH
                        else:
                            move = Directions.WEST
            if (lastMoves[len(lastMoves)-1]==Directions.NORTH):
                if Directions.WEST in lastLegal:
                    if Directions.EAST in legal: move = Directions.EAST
                    else:
                        if Directions.NORTH in legal: move = Directions.NORTH
                        else:
                            if Directions.WEST in legal: move = Directions.WEST
                            else:
                                move = Directions.SOUTH
                else:
                    if Directions.WEST in legal: move = Directions.WEST
                    else:
                        if Directions.NORTH in legal: move = Directions.NORTH
                        else:
                            if Directions.EAST in legal: move = Directions.EAST
                            else:
                                move = Directions.SOUTH
        #Misma coordenada X
        if (restaX == 0):
            if (restaY > 0):
                if Directions.NORTH in legal: move = Directions.NORTH
                else: 
                    move_random = random.randint(0, 1)
                    if (move_random == 0) and Directions.EAST in legal: move = Directions.EAST
                    if (move_random == 0) and Directions.EAST not in legal and Directions.WEST in legal: move = Directions.WEST
                    if (move_random == 1) and Directions.WEST in legal: move = Directions.WEST
                    if (move_random == 1) and Directions.WEST not in legal and Directions.EAST in legal: move = Directions.EAST
                    if (Directions.EAST not in legal and Directions.WEST not in legal): move = Directions.SOUTH
            else: 
                if Directions.SOUTH in legal: move = Directions.SOUTH
                else: 
                    move_random = random.randint(0, 1)
                    if (move_random == 0) and Directions.EAST in legal: move = Directions.EAST
                    if (move_random == 0) and Directions.EAST not in legal and Directions.WEST in legal: move = Directions.WEST
                    if (move_random == 1) and Directions.WEST in legal: move = Directions.WEST
                    if (move_random == 1) and Directions.WEST not in legal and Directions.EAST in legal: move = Directions.EAST
                    if (Directions.EAST not in legal and Directions.WEST not in legal): move = Directions.NORTH
        #Misma coordenada Y
        if (restaY == 0):
            if (restaX > 0):
                if Directions.EAST in legal: move = Directions.EAST
                else:
                    move_random = random.randint(0, 1)
                    if (move_random == 0) and Directions.SOUTH in legal: move = Directions.SOUTH
                    if (move_random == 0) and Directions.SOUTH not in legal and Directions.NORTH in legal: move = Directions.NORTH
                    if (move_random == 1) and Directions.NORTH in legal: move = Directions.NORTH
                    if (move_random == 1) and Directions.NORTH not in legal and Directions.SOUTH in legal: move = Directions.SOUTH
                    if (Directions.SOUTH not in legal and Directions.NORTH not in legal): move = Directions.WEST
            else:
                if Directions.WEST in legal: move = Directions.WEST
                else:
                    move_random = random.randint(0, 1)
                    if (move_random == 0) and Directions.SOUTH in legal: move = Directions.SOUTH
                    if (move_random == 0) and Directions.SOUTH not in legal and Directions.NORTH in legal: move = Directions.NORTH
                    if (move_random == 1) and Directions.NORTH in legal: move = Directions.NORTH
                    if (move_random == 1) and Directions.NORTH not in legal and Directions.SOUTH in legal: move = Directions.SOUTH
                    if (Directions.SOUTH not in legal and Directions.NORTH not in legal): move = Directions.EAST
        lastMoves.append(move)
        lastMoves.pop(0)
        lastLegal = legal
	x = [13,11,'1','1','1','1','1',13,9,5,1,7,-2]"""
	print(x)
	a = self.weka.predict("./prueba1.model", x, "./training_tutorial1(2).arff")
        return a

    def printLineData(self, gameState):
        if len(instancias) == 4:
            instancias.pop(0)
        #Posicion Pacman
        cadena = str(gameState.getPacmanPosition()[0])+","+str(gameState.getPacmanPosition()[1])+","
        #Acciones legales
        listaAcciones = ["North", "East", "South", "West", "Stop"]
        for i in range(len(listaAcciones)):
            if listaAcciones[i] in gameState.getLegalPacmanActions():
                cadena = cadena+str(1)+","
            else:
                cadena = cadena+str(0)+","
        #Posicion de los fantasmas
        sobran = 4-len(gameState.getGhostPositions())
        for i in range(len(gameState.getGhostPositions())):
            cadena = cadena + str(gameState.getGhostPositions()[i][0])+","+str(gameState.getGhostPositions()[i][1])+","
        if sobran>0:
            for i in range(sobran):
                cadena = cadena+str(-1)+","+str(-1)+","
        #Distancia a los fantasmas
        for i in range(len(gameState.data.ghostDistances)):
            if gameState.data.ghostDistances[i] != None:
                cadena = cadena + str(gameState.data.ghostDistances[i])+","
            else:
                cadena = cadena + str(-1)+","
        if sobran>0:
            for i in range(sobran):
                cadena = cadena + str(-1)+","
        #Distancia a la comidas
	distanciaComida = gameState.getDistanceNearestFood()
	if distanciaComida == None:
	    cadena = cadena + str(-1)+","
	else:
            cadena = cadena + str(distanciaComida)+","
        #Direccion Pac-man
        cadena = cadena + gameState.data.agentStates[0].getDirection()+","
        #Scores
        cadena = cadena + str(gameState.getScore()) 
        for i in range(len(instancias)):
            instancias[i] = instancias[i]+","+str(gameState.getScore())
        instancias.append(cadena)
        if len(instancias) == 4:
            return instancias[0]+"\n"
        else:
            return ""
    

        
