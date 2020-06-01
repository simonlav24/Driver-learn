from math import sqrt, cos, sin, pi, atan2
from random import uniform
def vec_add(vec1, vec2):
	return (vec1[0] + vec2[0], vec1[1] + vec2[1])

def vec_sub(vec1, vec2):
	return (vec1[0] - vec2[0], vec1[1] - vec2[1])

def normalize(vec):
	norm = sqrt(vec[0]**2 + vec[1]**2)
	if norm == 0:
		return vec
	return (vec[0] / norm, vec[1] / norm)

def vec_mult_scalar(vec, scalar):
	return (vec[0] * scalar, vec[1] * scalar)

def setmag(vec, mag):
	vec = normalize(vec)
	return vec_mult_scalar(vec, mag)
	
def am2vec(angle, mag):
	return (mag * cos(angle), mag * sin(angle))
	
def vec2am(vec):
	angle = atan2(vec[0], vec[1])
	mag = sqrt(vec[0]**2 + vec[1]**2)
	return (angle, mag)
	
def limit(vec, value):
	norm = sqrt(vec[0]**2 + vec[1]**2)
	if norm >= value:
		return setmag(vec, value)
	return vec
	
def vec_dist(vec1, vec2):
	return sqrt((vec1[0] - vec2[0])**2 + (vec1[1] - vec2[1])**2)
	
def random_unit():
	angle = uniform(0, 2*pi)
	return am2vec(angle, 1)
