import pygame
from vector import *
from neuralNetwork import *
from trackMaker import Track
from math import cos, sin, pi, sqrt
from random import uniform, randint, choice

# for the car:
# inputs: distances of the receptors
# output: a vector of probability for the best action. multiple actions are also ok
# actions: stir left, stir right, drive forward

# track maker, saved in json for practice.
# nice pictures, car sprites to the repository

TO_SQUARE = 1/sqrt(2)

pygame.init()

myfont = pygame.font.SysFont('Arial', 12)
fpsClock = pygame.time.Clock()
fps = 60
win_width = 1280
win_height = 720
win = pygame.display.set_mode((win_width,win_height))

def intersection_point(line1, line2):
	x1, y1, x2, y2 = line1[0][0], line1[0][1], line1[1][0], line1[1][1]
	x3, y3, x4, y4 = line2[0][0], line2[0][1], line2[1][0], line2[1][1]
	
	den = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
	if den == 0:
		return None
	t = ((x1 - x3)*(y3 - y4) - (y1 - y3)*(x3 - x4)) / den
	u = -((x1 - x2)*(y1 - y3) - (y1 - y2)*(x1 - x3)) / den
	point = Vector(x1 + t*(x2 - x1), y1 + t*(y2 - y1))
	if u >= 0 and u <= 1 and t >= 0 and t <= 1:
		return point
	return None

def is_intersecting(line1, line2):
	x1, y1, x2, y2 = line1[0][0], line1[0][1], line1[1][0], line1[1][1]
	x3, y3, x4, y4 = line2[0][0], line2[0][1], line2[1][0], line2[1][1]
	
	den = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
	if den == 0:
		return False
	t = ((x1 - x3)*(y3 - y4) - (y1 - y3)*(x3 - x4)) / den
	u = -((x1 - x2)*(y1 - y3) - (y1 - y2)*(x1 - x3)) / den
	if u >= 0 and u <= 1 and t >= 0 and t <= 1:
		return True
	return False

class Globals:
	_g = None
	def __init__(self):
		Globals._g = self
		self.friction = 0.95

class Car:
	_reg = []
	def __init__(self, pos=None, genes = None, color = None):
		self._reg.append(self)
		self.pos = Vector(win_width/2, win_height/2)
		if pos:
			self.pos = vectorCopy(pos)
		self.vel = Vector()
		self.acc = Vector()
		
		self.dir = Vector(1, 0)

		if color:
			self.color = color
		else:
			self.color = (randint(0,255), randint(0,255), randint(0,255))
		
		self.actions = {"left":False, "right":False, "forward":False}
		self.collided = False
		self.score = 0
		
		self.dna = NeuralNetwork(5, 3)
		self.dna.add_hidden_layer(8)
		self.dna.add_hidden_layer(3)
		self.dna.randomize()
		if genes:
			self.dna.setParameters(genes)

		self.playerControl = False
		self.dnaControl = True
		self.points = []

	def step(self):
		if self.collided:
			return

		# sense:
		info = self.sense()
		# if any of the info is zero (wall), then the car is stuck
		if any([inf < 0.05 for inf in info]):
			self.collided = True
			return

		self.dna.setInput(info)
		# think:
		self.dna.calculate()
		actions = self.dna.getOutput()

		# actions check
		if self.dnaControl:
			if actions[0] > 0.5:
				self.dir.rotate(0.05)
			if actions[1] > 0.5:
				self.dir.rotate(-0.05)
			if actions[2] > 0.5:
				self.acc = self.dir * 0.3

		if self.playerControl:
			if pygame.key.get_pressed()[pygame.K_RIGHT]:
				self.dir.rotate(0.05)
			if pygame.key.get_pressed()[pygame.K_LEFT]:
				self.dir.rotate(-0.05)
			if pygame.key.get_pressed()[pygame.K_UP]:
				self.acc = self.dir * 0.3

		# physics:
		self.vel += self.acc
		self.vel *= Globals._g.friction # limit vel(?)
		self.pos += self.vel
		self.acc *= 0.0
		
		# scoring
		self.score += 1
	
	def sense(self):
		# check sensors and return number (0,1) for each sensor.
		# 0 means close, 1 means far or none
		length = 200
		dirNormal = self.dir.normal()
		self.sensors = [(self.pos, self.pos + dirNormal * length),
						(self.pos, self.pos + dirNormal * -length),
						(self.pos, self.pos + self.dir * length),
						(self.pos, self.pos + self.dir * length * TO_SQUARE + dirNormal * length * TO_SQUARE),
						(self.pos, self.pos + self.dir * length * TO_SQUARE - dirNormal * length * TO_SQUARE)]

		self.points = [None for i in range(len(self.sensors))]
		weights = [1.0 for i in range(5)]
		
		for i, sensor in enumerate(self.sensors):
			intersections = []
			for line in Track._t.trackLines:
				point = intersection_point(sensor, line)
				if point:
					# calculate t
					# t = (point - self.pos).getMag() / length
					# self.points[i] = point
					# weights[i] = t
					intersections.append(point)
			if len(intersections) > 0:
				# pick the closest to the car and use that
				closest = intersections[0]
				for point in intersections:
					if distus(point, self.pos) < distus(closest, self.pos):
						closest = point

				self.points[i] = closest
				weights[i] = (closest - self.pos).getMag() / length
				
			
		return weights

	def draw(self):
		pygame.draw.circle(win, self.color, self.pos, 10)
		pygame.draw.line(win, (255,0,0), self.pos, self.pos + self.dir * 20)
		if debug and not self.collided:
			for s in self.sensors:
				pygame.draw.line(win, (0,255,0), s[0], s[1])
			for p in self.points:
				if p:
					pygame.draw.circle(win, (0,0,255), p, 5)	

def sort_key(x):
	return x.score

class Population:
	def __init__(self, size):
		self.generation = -1
		self.populationSize = size
		self.mutationRate = 0.05
		self.matingPool = []
	def createMatingPool(self):
		"""probabilistic method"""

		# calculate total fitness
		totalFitness = 0
		for car in Car._reg:
			totalFitness += car.score
		
		# normalize score
		for car in Car._reg:
			car.score /= totalFitness
		
		# create mating pool
		self.matingPool = []
		for car in Car._reg:
			for i in range(int(car.score * 100)):
				self.matingPool.append(car)
		
	def createNextGeneration(self):
		# create new generation
		self.generation += 1
		newGen = []
		for i, car in enumerate(Car._reg):
			car1 = self.matingPool[randint(0, len(self.matingPool)-1)]
			car2 = self.matingPool[randint(0, len(self.matingPool)-1)]
			# crossover
			# create a new car with genes from both parents and add to newGen
			newGenes = crossOver(car1.dna.getParameters(), car2.dna.getParameters())
			newCar = Car(genes=newGenes)
			newGen.append(newCar)
		
		# mutate
		for car in newGen:
			car.dna.mutate(self.mutationRate)
		
		# replace old generation
		Car._reg = newGen
	
	def createFirstGeneration(self, track):
		# create first generation
		self.generation += 1
		newGen = []
		for i in range(self.populationSize):
			newGen.append(Car(pos = track.startPos))
		
		# replace old generation
		Car._reg = newGen

################################################################################ Setup:

if __name__ == "__main__":

	Track._font = myfont
	Track._win = win
	track = Track()
	track.load("1")

	training = True

	debug = True

	Globals()

	population = Population(100)

	if training:
		population.createFirstGeneration(track)

	################################################################################ Main Loop:
	pause = False
	run = True
	while run:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_r:
					Car._reg[0].dna.randomize()
						
				if event.key == pygame.K_d:
					debug = not debug
				if event.key == pygame.K_p:
					print(Car._reg[0].dna.getParameters())
				if event.key == pygame.K_c:
					self_control = not self_control
				# if event.key == pygame.K_s:
					# for p in Perseptron._reg:
						# p.randomize()
		keys = pygame.key.get_pressed()
		if keys[pygame.K_ESCAPE]:
			run = False
		
		if pause:
			continue

		#background:
		win.fill((100,100,100))

		for d in Car._reg:
			d.step()
		for d in Car._reg:
			d.draw()
		
		track.draw()

		# if training:
		# 	time += 1
		# 	pop_stats()
		# 	check_population()
		
		# 	if time == cycle_time:
		# 		population()
		# 		gen_count += 1
		# 		time = 0
			
		pygame.display.update()
		fpsClock.tick(fps)

	pygame.quit()






