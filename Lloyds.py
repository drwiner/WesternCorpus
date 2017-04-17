import numpy as np
from hierarchicalClustering import Cluster, NamedPoint
import collections


def dotDistance(s1, s2):
	return np.sqrt(np.dot(s1.point - s2.point, s1.point - s2.point))


def Gonzales(X, k):
	n = len(X)
	# c_i = X[0]
	C = collections.defaultdict()
	C[0] = X[0]
	# C = dict({0 : X[0]})
	phi = [0 for i in range(n)]
	for i in range(1, k):
		m = 0
		C[i] = X[0]
		# find the x which is farthest from the center current mapped to x
		#  = X[0]
		for j in range(n):
			# for each x, find the one which is maximum distance from its center, save the i it occurs
			d = dotDistance(X[j], C[phi[j]])
			if d > m:
				m = d
				# this is the worst center so far
				C[i] = X[j]
		for j in range(n):
			if dotDistance(X[j], C[phi[j]]) > dotDistance(X[j], C[i]):
				# update each mapping to the closest center.
				phi[j] = i
	return C, phi

# this is Kmeans++ btw, for finding good staring centers
def kMeans(X, k):
	n = len(X)
	C = collections.defaultdict()
	phi = [0 for i in range(n)]
	C[0] = X[0]
	for i in range(1, k):
		# C[i] = X[0]
		choices = [(x, dotDistance(x, C[i-1])**2) for x in X]
		x = weightedChoice(choices)
		C[i] = x
		for j in range(n):
			if dotDistance(X[j], C[phi[j]]) > dotDistance(X[j], C[i]):
				phi[j] = i
	return C, phi

import random

def weightedChoice(choices):
	total = sum(w for c, w in choices)
	r = random.uniform(0, total)
	upto = 0
	for c, w in choices:
		if upto + w >= r:
			return c
		upto += w
	assert False, "shouldn't get here"



def threeMeansCost(x, C, phi):
	sig = sum(dotDistance(elm, C[phi[i]])**2 for i, elm in enumerate(x))
	cost_3means = np.sqrt((1/len(x)) * sig)
	return cost_3means


def readC2():
	#read C2.text
	C2 = open('C2.txt')
	x = set()
	for line in C2:
		split_line = line.split()
		p = np.array([float(i) for i in split_line[1:]])
		x.add(NamedPoint(int(split_line[0]), p))
	#
	k = 3
	x_ref = list(x)
	x = list(x_ref)
	C, phi = Gonzales(x, k)
	cost_max_3centers = max(dotDistance(elm, C[phi[i]]) for i, elm in enumerate(x))
	print('gonzales, max 3centers: ' + str(cost_max_3centers))
	print('gonzales, cost 3 means: ' + str(threeMeansCost(x, C, phi)))
	return x, C, phi



# 3 center cost max x in X d(x, phi[x])^2

# C is the centers, not clusters
# phi is the labeling/mapping
# Clusters = [Cluster(i,  for i, c in C)]


# import matplotlib.pyplot as plt

def runKmeans_hw():
	colours = ['r', 'g', 'b', 'y']


	########################
	########## K Means ++ ##
	########################
	tmc = []
	for i in range(10):
		C_kmeans, phi_kmeans = kMeans(x, k)
		if C_kmeans == C or phi_kmeans == phi:
			print('this time')
		tmc_value = threeMeansCost(x, C_kmeans, phi_kmeans)
		tmc.append(tmc_value)


def closestToPhi(C, X, closest_centers):
	phi = [0 for i in range(len(X))]
	for i, x in enumerate(X):
		phi[i] = C.index(closest_centers[x])
	return phi


def Lloyds(X, C, phi, k):
	# arbitrary choice
	changed = True
	while changed:
		changed = False
		for i, c in enumerate(C):
			for j, x in enumerate(X):
				closest = C[phi[j]]
				if dotDistance(x, C[c]) < dotDistance(x, closest):
					phi[j] = i

		for i, c in enumerate(C):

			subset = [x.point for j, x in enumerate(X) if phi[j] == i]

			s = sum(subset)
			avg = s / len(subset)

			n = NamedPoint('c' + str(i), avg)
			diff = C[i].point - avg
			for q in range(len(diff)):
				if diff[q] > 0:
					changed = True
					C[i] = n
					break

		# print('new round')
	return C, phi


# def run_Lloyds_hw(x, gC, gPhi):
# 	# problem a
# 	k = 3
# 	Clusters = x[0:k]
# 	Clusters, closest_centers_map = Lloyds(x, Clusters, [0 for i in range(len(x))], k)
# 	# phi = closestToPhi(Clusters, x, closest_centers_map)
# 	print('dude')
#
# 	colours = ['r', 'g', 'b', 'y']
# 	s1 = list(Clusters)
# 	print('you are looking at lloyds {1,2,3}')
# 	for i in range(k):
# 		rel_points = [p for j, p in enumerate(x) if closest_centers_map[j] == i]
# 		xes = [p.point[0] for p in rel_points]
# 		yes = [p.point[1] for p in rel_points]
# 		plt.scatter(xes, yes, c=colours[i])
# 		plt.scatter(Clusters[i].point[0], Clusters[i].point[1], c='y')
#
# 	plt.show()
#
# 	for p in Clusters:
# 		print(p.point)
# 	lloyds_a_3means = threeMeansCost(x, Clusters, closest_centers_map)
# 	print(lloyds_a_3means)
#
# 	#C is the gonzales output before
# 	Clusters, closest_centers_map = Lloyds(x, list(gC.values()), gPhi, k)
# 	colours = ['r', 'g', 'b', 'y']
# 	s1 = list(Clusters)
# 	for i in range(k):
# 		rel_points = [p for j, p in enumerate(x) if closest_centers_map[j] == i]
# 		xes = [p.point[0] for p in rel_points]
# 		yes = [p.point[1] for p in rel_points]
# 		plt.scatter(xes, yes, c=colours[i])
# 		plt.scatter(Clusters[i].point[0], Clusters[i].point[1], c='y')
# 	#
# 	plt.show()
# 	#
# 	for p in Clusters:
# 		print(p.point)
# 	lloyds_a_3means = threeMeansCost(x, Clusters, closest_centers_map)
# 	print(lloyds_a_3means)
#
# 	tmc = []
# 	sames = 0
# 	d = 40
# 	z = range(d)
# 	allclusters = list()
# 	for i in z:
# 		C_kmeans, phi_kmeans = kMeans(x, k)
# 		clusters, phi = Lloyds(x, list(C_kmeans.values()), phi_kmeans, k)
# 		if clusters in allclusters:
# 			sames += 1
# 		else:
# 			allclusters.append(clusters)
# 		tmc_value = threeMeansCost(x, clusters, phi)
# 		tmc.append(tmc_value)
# 		# for i in range(k):
# 		# 	rel_points = [p for p in x if phi[p] == i]
# 		# 	xes = [p.point[0] for p in rel_points]
# 		# 	yes = [p.point[1] for p in rel_points]
# 		# 	plt.scatter(xes, yes, c=colours[i])
# 		# 	plt.scatter(clusters[i].point[0], clusters[i].point[1], c='y')
# 		# plt.show()
# 	print(tmc)
# 	print('same time: ' + str(sames/d))
# 	#
# 	from collections import Counter
#
# 	TC = Counter([math.floor(t) for t in tmc])
#
# 	cu_dict = dict()
# 	cu = 0
# 	for i in range(max(TC.keys())):
# 		cu += TC[i]/d
# 		cu_dict.update({i: cu})
# 	plt.scatter(list(cu_dict.keys()), list(cu_dict.values()))
# 	plt.show()

# x, C, phi = readC2()
# run_Lloyds_hw(x, C, phi)

if __name__ == '__main__':
	pass