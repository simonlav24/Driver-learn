import pygame
import colorsys
from tvector import *
from math import cos, sin, pi, sqrt
from pygame import gfxdraw
from random import uniform, randint, choice
pygame.init()
pygame.font.init()
myfont = pygame.font.SysFont('Arial', 12)

win_width = 1280
win_height = 720
win = pygame.display.set_mode((win_width,win_height))

draw_track = False
training = False

recording = True
debug = False
self_control = True

# bg = pygame.image.load("track_4.png")

import tracks
border = tracks.track1
start_pos = tracks.track1_pos

# good saved genes:
genes1 = [0.26005145221093984, -0.46601971779192686, -0.1119722092901568, -0.1369977259929777, 0.9274343300980304]
genes2 = [0.2422152058502862, -0.7829403230638791, -0.10585584612393753, -0.07190077346825725, 1]
genes3 = [0.22749146386512578, -0.8060641629162983, 0.038982132718937516, -0.15032539728738215, 0.9886474646607389]

def param(pos):
	res = (pos[0] + win_width / 2, - pos[1] + win_height / 2)
	return (int(res[0]), int(res[1]))

def iparam(pos):
    res = (pos[0] - win_width / 2,- pos[1] + win_height / 2)
    return res
	
def smap(value,a,b,c,d,constrained=False):
	res = (value - a)/(b - a) * (d - c) + c
	if constrained:
		if res > d:
			return d
		if res < c:
			return c
		return res
	else:
		return res

def drawcircle(pos,rad,color):
	pygame.gfxdraw.filled_circle(win, param(pos)[0], param(pos)[1], rad, color)
	pygame.gfxdraw.aacircle(win, param(pos)[0], param(pos)[1], rad, color)

def drawline(start_pos, end_pos, color, width=1):
	pygame.draw.line(win, color, param(start_pos), param(end_pos), width)

def drawpoly(dots, color):
	dots2 = [param(i) for i in dots]
	pygame.gfxdraw.filled_polygon(win, dots2, color)
	pygame.gfxdraw.aapolygon(win, dots2, color)

def drawtext(text, pos, color=(0,0,0)):
	color_str = myfont.render(text, False, color)
	win.blit(color_str, param(pos))
	
def hsv2rgb(h,s,v):
	h/=100
	s/=100
	v/=100
	return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

def show_color_mouse():
	# string = str(iparam(pygame.mouse.get_pos()))
	string = str(d.p_drive.output) +" "+ str(d.p_right.output) +" "+ str(d.p_left.output)
	string_out = myfont.render(string, False, (255, 0, 0))
	win.blit(string_out, (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]+25))

def intersection_point(line1, line2):
	x1, y1, x2, y2 = line1[0][0], line1[0][1], line1[1][0], line1[1][1]
	x3, y3, x4, y4 = line2[0][0], line2[0][1], line2[1][0], line2[1][1]
	
	den = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
	if den == 0:
		return None
	t = ((x1 - x3)*(y3 - y4) - (y1 - y3)*(x3 - x4)) / den
	u = -((x1 - x2)*(y1 - y3) - (y1 - y2)*(x1 - x3)) / den
	point = (x1 + t*(x2 - x1), y1 + t*(y2 - y1))
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

class Driver:
	_reg = []
	def __init__(self, genes =[], color = None):
		self._reg.append(self)
		# self.pos = (-165 + randint(0,10),290 + randint(0,10))
		self.pos = start_pos[0]
		self.ipos = (self.pos[0], self.pos[1])
		self.vel = (0,0)
		self.dir = start_pos[1]
		self.acc = (0,0)
		
		if color:
			self.color = color
		else:
			self.color = hsv2rgb(randint(0,100), 100,100)
		
		self.actions = {"left":False, "right":False}
		self.collided = False
		self.score = 0
		
		#genes:
		if genes == []:
			self.genes = [uniform(-1,1) for i in range(5)]
		else:
			self.genes = genes
		
		self.p_turn = Perseptron(5, self.genes)
	def step(self):
		if not self.collided:
			# sense:
			info = self.sense()
			# persept
			self.p_turn.inputs = info
			self.p_turn.func()
			# actions check
			if self.p_turn.output >= 0.1:
				self.actions["right"] = True
			if self.p_turn.output <= -0.1:
				self.actions["left"] = True
		
		# actions act
		self.acc = am2vec(self.dir, 0.005)
		if self.actions["right"]:
			self.dir -= 0.01
		if self.actions["left"]:
			self.dir += 0.01
		# reset actions
		self.actions["right"], self.actions["left"] = False, False
		#dynamics:
		if not self.collided:
			self.vel = vec_add(self.vel, self.acc)
			friction = 0.99
			self.vel = vec_mult_scalar(self.vel, friction)
			limit(self.vel, 0.05)
			self.score += 1
			self.pos = vec_add(self.pos, self.vel)
		self.acc = (0,0)
	def dist_self(self, vec):
		return vec_dist(self.pos, vec)
	
	def sense(self):
		#update and check sensors:
		self.sensors = [(self.pos, vec_add(self.pos, am2vec(self.dir, 200))), \
						(self.pos, vec_add(self.pos, am2vec(self.dir - pi/2, 200))),\
						(self.pos, vec_add(self.pos, am2vec(self.dir + pi/2, 200))),\
						(self.pos, vec_add(self.pos, am2vec(self.dir - pi/4, 200))),\
						(self.pos, vec_add(self.pos, am2vec(self.dir + pi/4, 200)))]
		self.points = [None]*len(self.sensors)
		
		for s in range(len(self.sensors)):
			p_points = []
			for l in border:
				point = intersection_point(self.sensors[s], l)
				if point:
					p_points.append(point)
			if len(p_points) > 0:
				self.points[s] = min(p_points ,key=self.dist_self)
				
		#create info:
		info = [-1]*len(self.sensors)
		for i in range(len(self.sensors)):
			if self.points[i]:
				dist = vec_dist(self.pos, self.points[i])
				if dist <= 1:
					#COLLIDED
					self.collided = True
				info[i] = smap(dist, 0, 200, 1, 0)   #1-means close, 0-means disatnt
			else:
				info[i] = 0
		return info
	
	def actions_check(self):
		#actions_check:
		force_left, force_right = 0, 0
		for p in range(len(self.sensors)):
			if self.points[p]:
				#calculate distance
				dist = vec_dist(self.pos, self.points[p])
				# print(1/dist)
				
				if p == 0:#front
					pass
				elif p == 1:#right
					self.actions["left"] = True
					# force_left += smap(1/dist, 0.01, 0.3, 0, 1,True)
					force_left += 1/dist
				elif p == 2:#left
					self.actions["right"] = True
					# force_right += smap(1/dist, 0.01, 0.3, 0, 1,True)
					force_right += 1/dist
				elif p == 3:#front_right
					self.actions["left"] = True
					# force_left += smap(1/dist, 0.01, 0.3, 0, 1,True)
					force_left += 1/dist
				elif p == 4:#front_left
					self.actions["right"] = True
					# force_right += smap(1/dist, 0.01, 0.3, 0, 1,True)
					force_right += 1/dist
		# force_right = min(force_right, 0.01)
		# force_left = min(force_left, 0.01)
		#actions act:
		if not self_control or not self.index == 0:
			if self.actions["drive"]:
				self.acc = am2vec(self.dir, 0.005)
			if self.actions["right"]:
				self.dir -= force_right
			if self.actions["left"]:
				self.dir += force_left
		#reset actions:
		self.actions["right"], self.actions["left"] = False, False
		
	def draw(self):
		if debug:
			for s in self.sensors:
				drawline(s[0], s[1], (0,255,0), 1)
		
			for p in self.points:
				if p:
					drawcircle(p, 5, (0,0,255))
		
		dir_vec = am2vec(self.dir, 8)
		orthogonal = (dir_vec[1], -dir_vec[0])
		p1 = vec_add(self.pos, orthogonal)
		p2 = vec_sub(self.pos, orthogonal)
		p3 = vec_add(self.pos, setmag(dir_vec, 30))
		drawpoly([p1,p2,p3], self.color)
		# drawtext(str(self.score), self.pos)
		# drawtext(str(self.timer2), vec_add(self.pos, (0,-10)))
		
class Player(Driver):
	def step(self):
		#keys:
		if pygame.key.get_pressed()[pygame.K_RIGHT]:
			self.dir += -0.01
		if pygame.key.get_pressed()[pygame.K_LEFT]:
			self.dir += 0.01
		if pygame.key.get_pressed()[pygame.K_UP]:
			self.acc = am2vec(self.dir, 0.005)#regular is 0.005
		if pygame.key.get_pressed()[pygame.K_DOWN]:
			pass
			
		self.sense()

		#dynamics:
		self.vel = vec_add(self.vel, self.acc)
		friction = 0.99
		self.vel = vec_mult_scalar(self.vel, friction)
		limit(self.vel, 0.05)
		self.pos = vec_add(self.pos, self.vel)
		self.acc = (0,0)
		
class Perseptron:
	_reg = []
	def __init__(self, amount, weights=[]):
		self._reg.append(self)
		self.inputs = [0]*amount
		if weights == []:
			self.weights = [uniform(-1,1) for i in range(amount)]
		else:
			self.weights = weights
		self.output = None
	def func(self):
		sum = 0
		for i in range(len(self.inputs)):
			sum += self.inputs[i] * self.weights[i]
		self.output = sum
	def randomize(self):
		self.weights = [uniform(-1,1) for i in self.inputs]

def sort_key(x):
	return x.score

def population():
	Driver._reg.sort(reverse = True, key = sort_key)
	best1 = Driver._reg[0].genes
	best2 = Driver._reg[1].genes
	best3 = Driver._reg[2].genes
	
	population_record.append((best1, Driver._reg[0].score))
	
	# print("best genes: ", end="")
	# print(best_genes)
	
	Driver._reg = []
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
		Driver(new_genes)

def check_population():
	global time
	list = []
	for d in Driver._reg:
		list.append(d.collided)
	if all(list):
		time = cycle_time

def pop_stats():
	drawtext("Generation: "+str(gen_count), (- win_width /2 + 10,win_height /2 - 10))
	drawtext("time: "+str(time), (- win_width /2 + 10,win_height /2 - 25))
	
################################################################################ Setup:
population_size = 20
population_record = []
cycle_time = 20000
gen_count = 1	
time = 0

if training:
	for i in range(population_size):
		Driver()

if draw_track:
	border = []
	mouse_pressed = False

# d = Player(None, (255,0,0))
p = Driver(genes1, (0,255,0))
p2 = Driver(genes2, (0,0,255))


################################################################################ Main Loop:
pause = False
run = True
while run:
	#pygame.time.delay(1)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if draw_track:
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				mouse_pos = pygame.mouse.get_pos()
				p1 = iparam(mouse_pos)
				mouse_pressed = True
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
				if len(border) > 0:
					border.pop()
			if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				mouse_pos = pygame.mouse.get_pos()
				p2 = iparam(mouse_pos)
				mouse_pressed = False
				new_line = (p1,p2)
				border.append(new_line)
		if event.type == pygame.KEYDOWN:
			#key pressed once:
			if event.key == pygame.K_r:
				for d in Driver._reg:
					d.pos = (0,0)
			if event.key == pygame.K_d:
				debug = not debug
			if event.key == pygame.K_k:
				# KILL SPINNERS:
				for d in Driver._reg:
					if not d.collided:
						d.score = 0
						d.collided = True

			if event.key == pygame.K_p:
				pause = not pause
			if event.key == pygame.K_c:
				self_control = not self_control
			if event.key == pygame.K_s:
				for p in Perseptron._reg:
					p.randomize()
	keys = pygame.key.get_pressed()
	if keys[pygame.K_ESCAPE]:
		run = False
	
	if pause:
		continue

	#background:
	win.fill((255,255,255))
	# win.blit(bg, (0,0))
	# show_color_mouse()
	
	#step:
	if draw_track:
		if mouse_pressed:
			drawline(p1, iparam(pygame.mouse.get_pos()), (255,255,0), 1)
	
	for b in border:
		drawline(b[0], b[1], (0,60,200), 1)

	
	for d in Driver._reg:
		d.step()
	for d in Driver._reg:
		d.draw()
	
	if training:
		time += 1
		pop_stats()
		check_population()
	
		if time == cycle_time:
			population()
			gen_count += 1
			time = 0
		
	pygame.display.update()

# writings
if draw_track:
	f = open("driver_output", 'w')
	for b in border:\
	f.write(str(b) + "\n")
	f.close()
if training:
	if recording:
		f = open("driver_record", 'w')
		for i in range(len(population_record)):
			f.write("Generation: " + str(i+1) + " best score: " + str(population_record[i][1]) + "\n" )
			f.write("best genes:\n")
			f.write(str(population_record[i][0]) + "\n")
		f.close()

pygame.quit()






