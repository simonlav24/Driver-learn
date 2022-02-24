import pygame
from vector import *
import json

BACK_COLOR = (24, 80, 165)
GRID_COLOR = (102, 169, 255)
TRACK_COLOR = (255, 255, 255)
SCORE_COLOR = (255, 255, 10)
ARROW = [Vector(0, 5), Vector(20, 0), Vector(0,-5)]

def drawGrid(grid_size):
	for i in range(0, win_width, grid_size):
		pygame.draw.line(win, GRID_COLOR, (i, 0), (i, win_height))
	for i in range(0, win_height, grid_size):
		pygame.draw.line(win, GRID_COLOR, (0, i), (win_width, i))

class Track:
	_t = None
	_font = None
	_win = None
	def __init__(self):
		Track._t = self
		self.name = "Track"
		self.trackLines = []
		self.scoreLines = []
		self.startPos = None
		self.startDir = None
		self.lineSelected = -1
		self.scoreSelected = -1
		self.updateInfo()
	def addLine(self, line, track=True):
		if dist(line[0], line[1]) < 3:
			return
		if track:
			self.trackLines.append(line)
			self.lineSelected = len(self.trackLines) - 1
		else:
			self.scoreLines.append(line)
			self.scoreSelected = len(self.scoreLines) - 1
		self.updateInfo()
	def save(self):
		data = {}
		data["name"] = self.name
		data['startPos'] = self.startPos
		data['startDir'] = self.startDir
		data['trackLines'] = []
		data['scoreLines'] = []
		for line in self.trackLines:
			data['trackLines'].append(line)
		for line in self.scoreLines:
			data['scoreLines'].append(line)
		with open('./tracks/Track_' + self.name + '.json', 'w') as outfile:
			json.dump(data, outfile)
		print("Saved track: " + self.name)
	def load(self, name):
		with open('./tracks/Track_' + name + '.json') as json_file:
			data = json.load(json_file)
		self.name = data["name"]
		self.startPos = data['startPos']
		self.startDir = data['startDir']
		self.trackLines = data['trackLines']
		self.scoreLines = data['scoreLines']
		self.lineSelected = len(self.trackLines) - 1
	def updateInfo(self):
		self.namesurf = Track._font.render(self.name, False, (255,255,255))
		self.linessurf = Track._font.render(str(len(self.trackLines)), False, (255,255,255))
	def blitInfo(self):
		Track._win.blit(self.namesurf, (10, 10))
		Track._win.blit(self.linessurf, (10, 25))
	def draw(self):
		for i, line in enumerate(self.trackLines):
			color = TRACK_COLOR
			if self.lineSelected == i:
				color = (255, 0, 0)
			pygame.draw.line(Track._win, color, line[0], line[1])
		for i, line in enumerate(self.scoreLines):
			color = SCORE_COLOR
			if self.scoreSelected == i:
				color = (255, 0, 0)
			pygame.draw.line(Track._win, color, line[0], line[1])
		if self.startDir and self.startPos:
			angle = tup2vec(self.startDir).getAngle()
			polygon = [rotateVector(i, angle) + self.startPos for i in ARROW]
			pygame.draw.polygon(Track._win, (0, 255, 0), polygon)

# setup

if __name__ == "__main__":
	pygame.init()

	myfont = pygame.font.SysFont('Arial', 12)
	fpsClock = pygame.time.Clock()
	fps = 60
	win_width = 1280
	win_height = 720
	win = pygame.display.set_mode((win_width,win_height))

	Track._win = win
	Track._font = myfont
	track = Track()

	backImage = None
	backImagePath = ""
	if backImagePath != "":
		backImage = pygame.image.load(backImagePath)

	modes = ["drawTracks", "editStart", "drawScoreLine"]
	mouseMode = "drawTracks"
	mouseHold = False

	run = True
	while run:
		for event in pygame.event.get():
			
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if mouseMode == "drawTracks" or mouseMode == "drawScoreLine":
					lineStart = tup2vec(pygame.mouse.get_pos())
					mouseHold = True
				if mouseMode == "editStart":
					track.startPos = pygame.mouse.get_pos()
					mouseHold = True

			if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				if mouseMode == "drawTracks" or mouseMode == "drawScoreLine":
					lineEnd = tup2vec(pygame.mouse.get_pos())
					mouseHold = False
					if mouseMode == "drawTracks":
						track.addLine((lineStart.vec2tup(), lineEnd.vec2tup()))
					else:
						track.addLine((lineStart.vec2tup(), lineEnd.vec2tup()), False)
				if mouseMode == "editStart":
					track.startDir = normalize(tup2vec(pygame.mouse.get_pos()) - tup2vec(track.startPos)).vec2tup()
					mouseHold = False

			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_DELETE:
					if mouseMode == "drawTracks":
						if track.lineSelected != -1:
							track.trackLines.pop(track.lineSelected)
							track.lineSelected -= 1
							track.updateInfo()
					elif mouseMode == "drawScoreLine":
						if track.scoreSelected != -1:
							track.scoreLines.pop(track.scoreSelected)
							track.scoreSelected -= 1
							track.updateInfo()
				if event.key == pygame.K_LEFT:
					if mouseMode == "drawTracks":
						track.lineSelected = (track.lineSelected - 1) % len(track.trackLines)
					elif mouseMode == "drawScoreLine":
						track.scoreSelected = (track.scoreSelected - 1) % len(track.scoreLines)
				if event.key == pygame.K_RIGHT:
					if mouseMode == "drawTracks":
						if len(track.trackLines) > 0:
							track.lineSelected = (track.lineSelected + 1) % len(track.trackLines)
					elif mouseMode == "drawScoreLine":
						if len(track.scoreLines) > 0:
							track.scoreSelected = (track.scoreSelected + 1) % len(track.scoreLines)
				if event.key == pygame.K_r:
					# get text from user
					track.name = input("Track name: ")
					track.updateInfo()
				if event.key == pygame.K_s:
					track.save()
				if event.key == pygame.K_l:
					track.load(input("Track name: "))
				if event.key == pygame.K_m:
					mouseMode = modes[(modes.index(mouseMode) + 1) % len(modes)]
					print("Mouse mode: " + mouseMode)
				
				
		keys = pygame.key.get_pressed()
		if keys[pygame.K_ESCAPE]:
			run = False
		
		#background:
		win.fill(BACK_COLOR)
		if backImage != None:
			win.blit(backImage, (0,0))
		drawGrid(100)

		track.blitInfo()

		if mouseHold:
			if mouseMode == "drawTracks" or mouseMode == "drawScoreLine":
				pygame.draw.line(win, TRACK_COLOR, lineStart, pygame.mouse.get_pos())
			if mouseMode == "editStart":
				angle = tup2vec(tup2vec(pygame.mouse.get_pos()) - tup2vec(track.startPos)).getAngle()
				polygon = [rotateVector(i, angle) + track.startPos for i in arrow]
				pygame.draw.polygon(win, (0, 255, 0), polygon)

		track.draw()

		pygame.display.update()
		fpsClock.tick(fps)

	pygame.quit()