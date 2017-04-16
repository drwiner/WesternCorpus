import numpy as np
from hierarchicalClustering import NamedPoint
from Lloyds import Lloyds, threeMeansCost, dotDistance, Gonzales
import collections


C3 = open('C3.txt')
x = set()
for line in C3:
	split_line = line.split()
	p = np.array([float(i) for i in split_line[1:]])
	x.add(NamedPoint(int(split_line[0]), p))

k = 4
x_ref = list(x)
x = list(x_ref)
import math
def lloyds_test(X, C, phi, k):
	# arbitrary choice
	changed = True
	while changed:
		changed = False
		for i, c in enumerate(C):
			for j, x in enumerate(X):
				closest = C[phi[j]]
				if dotDistance(x, c) < dotDistance(x, closest):
					phi[j] = i

		for i, c in enumerate(C):

			subsetsum = sum(x.point*x.point for j, x in enumerate(X) if phi[j] == i)
			avg = np.sqrt(subsetsum)
			n = NamedPoint('c' + str(i), avg)
			diff = C[i].point - avg
			for q in range(len(diff)):
				if diff[q] >= .2:
					changed = True
					C[i] = n
					break



	return C, phi

def kMedianCost(points, clusters, phi):
	c = 1/len(points)
	sig = sum(dotDistance(p, clusters[phi[i]]) for i, p in enumerate(points))
	return c*sig

# run gonzales to get clusters
clusters, phi = Gonzales(x, k)
print('after gonzales\n')
print(kMedianCost(x, clusters, phi))
for p in clusters.values():
	print(p.point)
print('\n')
import copy

# run lloyds normally, to see what we get
L_clusters, L_phi = Lloyds(x, list(clusters.values()), copy.deepcopy(phi), k)
print('\n after lloyds')
print(kMedianCost(x, L_clusters, L_phi))
for p in L_clusters:
	print(str(p.point))
print(L_clusters)

# run lloyds test to see if we can improve
L_clusters, L_phi = lloyds_test(x, L_clusters, L_phi, k)
print('\n after lloyds _ test')
print(kMedianCost(x, L_clusters, L_phi))
for p in L_clusters:
	print(p.point)
print(L_clusters)

output = open('k_median_centers.txt', 'w')
for i, p in enumerate(L_clusters):
	strings = ['%.7f' % p.point[i] for i in range(len(p.point))]
	output.write(str(i) + '\t' + '\t'.join(strings) + '\n')
import copy
# strategy:
	# run gonzales to find some good candidate centers
	# find point which is farthest from its center. find point which maps to same center which is farthest, split difference.
def splitDiff(x, C, phi, k):
	while True:
		benchmark = kMedianCost(x, C, phi)

		arg_farthest = None
		farthest = 0
		for j, p in enumerate(x):
			d = dotDistance(p, C[phi[j]])
			if d > farthest:
				farthest = d
				arg_farthest = j
		same_center = C[phi[arg_farthest]]

		arg_farthest_from_farthest = None
		farthest = 0
		for j, p in enumerate(x):
			# only care about that which is farthest.
			if C[phi[j]] == same_center:
				d = dotDistance(p, x[arg_farthest])
				if d > farthest:
					farthest = d
					arg_farthest_from_farthest = j

		# now, find the dimension which splits them the most.
		biggest_diff = 0
		arg_dim = None
		CC = copy.deepcopy(C)
		diff = x[arg_farthest_from_farthest].point - x[arg_farthest].point
		for dimension in range(5):
			if abs(diff[dimension]) > biggest_diff:
				biggest_diff = abs(diff[dimension])
				arg_dim = dimension
		d1 = x[arg_farthest_from_farthest].point[arg_dim]
		d2 = x[arg_farthest].point[arg_dim]
		d = (d1 + d2) / 2
		CC[phi[arg_farthest_from_farthest]].point[arg_dim] = d
		bb = kMedianCost(x, CC, phi)
		if benchmark < bb:
			C = CC
			benchmark = bb
		print(benchmark)

# splitDiff(x, list(clusters.values()), phi, k)

# tmc = []
# sames = 0
# d = 40
# z = range(d)
# for i in z:
# 	C_kmeans, phi_kmeans = kMeans(x, k)
# 	clusters, phi = Lloyds(x, list(C_kmeans.values()), k)
# 	if clusters == C_kmeans:
# 		sames += 1
# 	tmc_value = threeMeansCost(x, clusters, phi)
# 	tmc.append(tmc_value)
# 	# for i in range(k):
# 	# 	rel_points = [p for p in x if phi[p] == i]
# 	# 	xes = [p.point[0] for p in rel_points]
# 	# 	yes = [p.point[1] for p in rel_points]
# 	# 	plt.scatter(xes, yes, c=colours[i])
# 	# 	plt.scatter(clusters[i].point[0], clusters[i].point[1], c='y')
# 	# plt.show()
# print(tmc)
# print('same time: ' + str(sames/d))
#
# from collections import Counter
#
# TC = Counter([math.floor(t) for t in tmc])
#
# cu_dict = dict()
# cu = 0
# for i in range(max(TC.keys())):
# 	cu += TC[i]/d
# 	cu_dict.update({i: cu})
# plt.scatter(list(cu_dict.keys()), list(cu_dict.values()))
# plt.show()