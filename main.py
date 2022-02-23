import pygame
from vector import *
from neuralNetwork import *
from math import cos, sin, pi, sqrt
from random import uniform, randint, choice

# for the car:
# inputs: distances of the receptors
# output: a vector of probability for the best action. multiple actions are also ok
# actions: stir left, stir right, drive forward

# track maker, saved in json for practice.
# nice pictures, car sprites to the repository

TO_SQUARE = 1/sqrt(2)

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
			self.pos = pos
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
		
		self.brain = NeuralNetwork(5, 3)
		self.brain.add_hidden_layer(8)
		self.brain.add_hidden_layer(3)
		self.brain.randomize()
		if genes:
			self.brain.setParameters(genes)

		self.playerControl = False
		self.brainControl = True
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

		self.brain.setInput(info)
		# think:
		self.brain.calculate()
		actions = self.brain.getOutput()

		# actions check
		if self.brainControl:
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
			for line in trackLines:
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
		if debug:
			for s in self.sensors:
				pygame.draw.line(win, (0,255,0), s[0], s[1])
		
		pygame.draw.circle(win, self.color, self.pos, 10)
		pygame.draw.line(win, (255,0,0), self.pos, self.pos + self.dir * 20)
		for p in self.points:
			if p:
				pygame.draw.circle(win, (0,0,255), p, 5)
		
def sort_key(x):
	return x.score

def population():
	Car._reg.sort(reverse = True, key = sort_key)
	best1 = Car._reg[0].genes
	best2 = Car._reg[1].genes
	best3 = Car._reg[2].genes
	
	population_record.append((best1, Car._reg[0].score))
	
	# print("best genes: ", end="")
	# print(best_genes)
	
	Car._reg = []
	for i in range(population_size):
		new_genes = []
		best_choose = choice([best1, best1, best1, best2, best2, best3])
		
		# alter genes
		
		val = []
		for value in range(5):
			if randint(0,100) <= 5:
				adjust = uniform(-0.7,0.7)
			else:
				adjust = uniform(-0.1,0.1)
			new_val = best_choose[value] + adjust
			#limit: (-1,1)
			if new_val > 1:
				new_val = 1
			elif new_val < -1:
				new_val = -1
			val.append(new_val)
		new_genes = val
		Car(new_genes)

def check_population():
	global time
	list = []
	for d in Car._reg:
		list.append(d.collided)
	if all(list):
		time = cycle_time

# def pop_stats():
# 	drawtext("Generation: "+str(gen_count), (- win_width /2 + 10,win_height /2 - 10))
# 	drawtext("time: "+str(time), (- win_width /2 + 10,win_height /2 - 25))

################################################################################ Setup:
pygame.init()

myfont = pygame.font.SysFont('Arial', 12)
fpsClock = pygame.time.Clock()
fps = 60

win_width = 1280
win_height = 720
win = pygame.display.set_mode((win_width,win_height))

trackLines = []
# trackLines.append((Vector(randint(0,win_width), randint(0,win_height)), Vector(randint(0,win_width), randint(0,win_height))))

# load track
from tracks import *
startPos = tup2vec(track3_pos[0]) + Vector(win_width /2, win_height /2)

adjusted = []
for line in track3:
	adjusted.append((tup2vec(line[0]) + Vector(win_width /2, win_height /2), tup2vec(line[1]) + Vector(win_width /2, win_height /2)))
trackLines = adjusted

draw_track = False
training = True

recording = True
debug = True
self_control = True

Globals()

population_size = 100
population_record = []
cycle_time = 20000
gen_count = 1	
time = 0

if training:
	for i in range(population_size):
		Car(pos = vectorCopy(startPos))

if draw_track:
	border = []
	mouse_pressed = False

# d = Player(None, (255,0,0))
# p = Car(genes1, (0,255,0))
# p2 = Car(genes2, (0,0,255))

# c = Car()
# c.playerControl = True

################################################################################ Main Loop:
pause = False
run = True
while run:
	#pygame.time.delay(1)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.KEYDOWN:
			#key pressed once:
			if event.key == pygame.K_r:
				Car._reg[0].brain.randomize()
					
			if event.key == pygame.K_d:
				debug = not debug
			if event.key == pygame.K_p:
				pause = not pause
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
	
	for line in trackLines:
		pygame.draw.line(win, (255,255,255), line[0], line[1])

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






