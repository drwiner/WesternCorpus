import numpy as np
from itertools import product
from clockdeco import clock
import math
# import collections

# NamedPoint = collections.namedtuple('NamedPoint', ['id', 'point'])

class NamedPoint:
	def __init__(self, int_id, point):
		self.int_id = int_id
		self.point = point

	def __hash__(self):
		return hash(self.int_id)

	def __repr__(self):
		return 'named_point: ' + str(self.int_id)

	def __add__(self, other):
		return self.point + other.point


class Cluster:
	def __init__(self, int_id, points):
		self.int_id = int_id
		self.points = list(points)

	def absorb(self, cluster):
		self.points.extend(cluster.points)

	def __hash__(self):
		return hash(self.int_id)

	def __len__(self):
		return len(self.points)

	def __getitem__(self, pos):
		return self.points[pos]

	def __repr__(self):
		n = 'cluster: ' + str(self.int_id) + ' --- '
		return n + ' '.join(str(p) for p in self.points)


def dotDistance(s1, s2):
	return math.sqrt(np.dot(s1.point - s2.point, s1.point - s2.point))
def nopointDist(a1, a2):
	return math.sqrt(np.dot(a1 - a2, a1 - a2))

# @clock
def singleLink(S1, S2):
	# S1 and S2 are clusters, possibly with just 1 entity
	# each entity has a point
	S_prod = set(product(S1, S2))
	return min(dotDistance(s1,s2) for s1,s2 in S_prod)

# @clock
def completeLink(S1, S2):
	S_prod = set(product(S1, S2))
	return max(dotDistance(s1,s2) for s1, s2 in S_prod)

# @clock
def meanLink(S1, S2):
	a1 = (1/len(S1))*sum(s.point for s in S1)
	a2 = (1/len(S2))*sum(s.point for s in S2)
	return nopointDist(a1, a2)

points = set()

def initialLoading(text_name):
	# initial loading
	C1 = open('C1.txt')
	# points = set()
	for line in C1:
		split_line = line.split()
		p = np.array([float(i) for i in split_line[1:]])
		points.add(NamedPoint(int(split_line[0]), p))


singleLink_clusters = set()
completeLink_clusters = set()
meanLink_clusters = set()

def initClusters():
	# initialization:
	for point in points:
		p = [point]
		singleLink_clusters.add(Cluster(point.int_id, p))
		completeLink_clusters.add(Cluster(point.int_id, p))
		meanLink_clusters.add(Cluster(point.int_id, p))

@clock
def h_clustering(clusters, k, dist_method):
	clusts = set(clusters)
	while len(clusts) > k:
		pairwise_clusters = set(product(clusts, clusts))
		arg_mins = None
		m = float("inf")
		for c1, c2 in pairwise_clusters:
			if c1 == c2:
				continue
			value = dist_method(c1, c2)
			if value < m:
				m = value
				arg_mins = (c1, c2)
		if arg_mins is None:
			print('wtf')
		c1, c2 = arg_mins
		if len(c1) < len(c2):
			c2.absorb(c1)
			clusts = clusts - {c1}
		else:
			c1.absorb(c2)
			clusts = clusts - {c2}
	return clusts


# def output(k):
# 	k = 4
# 	sl_clusts = h_clustering(singleLink_clusters, k, singleLink)
# 	print('Shortest Link:\n')
# 	for clust in sl_clusts:
# 		print(clust)
# 		for point in clust:
# 			print(point.int_id,point.point)
# 	print('\n')
# 	print('Complete Link:\n')
# 	cl_clusts = h_clustering(completeLink_clusters, k, completeLink)
# 	for clust in cl_clusts:
# 		print(clust)
# 		for point in clust:
# 			print(point.int_id, point.point)
# 	print('\n')
# 	print('Mean Link:\n')
# 	ml_clusts = h_clustering(meanLink_clusters, k, meanLink)
# 	for clust in ml_clusts:
# 		print(clust)
# 		for point in clust:
# 			print(point.int_id, point.point)
# 	print('\n')
#
# 	import matplotlib.pyplot as plt
#
# 	colours = ['r', 'g', 'y', 'b']
# 	s1 = list(sl_clusts)
#
# 	for i in range(k):
# 		x = [p.point[0] for p in s1[i]]
# 		y = [p.point[1] for p in s1[i]]
# 		plt.scatter(x, y, c=colours[i])
#
# 	plt.show()
#
# 	s1 = list(cl_clusts)
#
# 	for i in range(k):
# 		x = [p.point[0] for p in s1[i]]
# 		y = [p.point[1] for p in s1[i]]
# 		plt.scatter(x, y, c=colours[i])
#
# 	plt.show()
#
# 	s1 = list(ml_clusts)
#
# 	for i in range(k):
# 		x = [p.point[0] for p in s1[i]]
# 		y = [p.point[1] for p in s1[i]]
# 		plt.scatter(x, y, c=colours[i])
#
# 	plt.show()

# initialLoading(45)
# initClusters()
# output(4)