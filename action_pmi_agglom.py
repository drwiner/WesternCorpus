from spectral_clustering import get_clusters, cluster_this
from Stepify import plannify_scenes
import collections
import itertools
from uuid import uuid1
import math
from functools import partial
from hierarchicalClustering import Cluster, NamedPoint
import numpy as np
from pocl.Element import Literal, Argument, Actor, Operator
from pocl.ElementGraph import Action
from pocl.OrderingGraph import OrderingGraph, CausalLinkGraph

import pickle

def save_database(db):
	with open('plans.pkl', 'wb') as output:
		pickle.dump(db, output, protocol=pickle.HIGHEST_PROTOCOL)


class Event:
	def __init__(self, step_name, cluster_val):
		self.step_name = step_name
		self.cluster_val = cluster_val

	def __hash__(self):
		return hash(self.step_name) ^ hash(self.cluster_val)

	def __eq__(self, other):
		return self.step_name == other.step_name and self.cluster_val == other.cluster_val

	def __repr__(self):
		return '<{}, {}>'.format(self.step_name, self.cluster_val)


def agglom_pmi_clustering(clusters, k, dist_method):
	clusts = set(clusters)
	while len(clusts) > k:
		pairwise_clusters = set(itertools.product(clusts, clusts))
		arg_mins = None
		m = float("inf")
		print(len(pairwise_clusters))
		for i, (c1, c2) in enumerate(pairwise_clusters):
			print(i)
			if c1 == c2:
				continue
			value = dist_method(S1=c1, S2=c2)
			# print(value)
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

		print((len(c1), len(c2)))
	return clusts


def gonzales(X, k, dist_method):
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
			d = dist_method(a=X[j].point, b=C[phi[j]].point)
			if d > m:
				m = d
				# this is the worst center so far
				C[i] = X[j]
		for j in range(n):
			if dist_method(a=X[j].point, b=C[phi[j]].point) > dist_method(a=X[j].point, b=C[i].point):
				# update each mapping to the closest center.
				phi[j] = i
	return C, phi



def closest_centers(X, Clusters, dist_method):
	# for each x in X, assign to cluster C which is closest.
	C = [[c] for c in Clusters]
	for x in X:
		best_score = -1
		best_cluster = 0
		for i, rep in enumerate(Clusters):
			score = dist_method(a=x.point, b=rep.point)
			if score > best_score:
				best_cluster = i
				best_score = score
		C[best_cluster].append(x)
	return C


def collect_events(cluster_dict, plan_list):
	# events = []
	# links = []
	event_dict = collections.defaultdict(list)
	link_dict = collections.defaultdict(list)
	for (s_name, steps, og, clg) in plan_list:
		for step in steps:
			for i, arg in enumerate(step.Args):
				if arg.name not in cluster_dict.keys():
					continue
				event_dict[step.name].append(cluster_dict[arg.name])
				# events.append(Event(step.name, cluster_dict[arg.name]))
		for link in clg.edges:
			for i, arg in enumerate(link.source.Args):
				if arg.name is None:
					continue
				for j, arg2 in enumerate(link.sink.Args):
					if arg2.name is None:
						continue
					if arg.name in cluster_dict.keys():
						link_dict[(link.source.name, link.sink.name)].append(cluster_dict[arg.name])
					if arg2.name in cluster_dict.keys():
						link_dict[(link.source.name, link.sink.name)].append(cluster_dict[arg2.name])

			# source_events = [(link.source.name, i) for i, arg in enumerate(link.source) if arg.name != 'None']
			# sink_events = [Event(link.sink.name, cluster_dict[arg.name]) for arg in link.sink if arg.name != 'None']
			# for s in source_events:
			# 	for t in sink_events:
			# 		links.append({s,t})

	return event_dict, link_dict


def collect_kgram_events(scene_lib_file_name, cluster_d):
	k16_grams = []
	k8_grams = []

	k16 = collections.deque(maxlen=16)
	k8 = collections.deque(maxlen=8)
	# k4_grams = set()
	with open(scene_lib_file_name) as scene_lib_file:

		# k4 = collections.Queue(maxsize=4)
		for i, line in enumerate(scene_lib_file):
			sp = line.split()

			if sp[2].strip() == 'None':
				continue
			step_name = sp[2].strip()
			clusts = [cluster_d[arg] for j, arg in enumerate(sp[3:-2]) if arg in cluster_d.keys()]
			for c in clusts:
				# e = Event(sp[2].strip(), c)
				k16.append((step_name, c))
				k8.append((step_name, c))
				if len(k16) == 16:
					k16_grams.append(list(k16))
				if len(k8) == 8:
					k8_grams.append(list(k8))
	return k16_grams, k8_grams


def prob(event_d, e, cluster):
	# the probability that event e via value cluster is
	denom = 0
	for k, val_list in event_d.items():
		denom += len(val_list)
	numer = len([1 for i in event_d[e] if i == cluster])
	return numer / denom


def all_count(event_d):
	sumo = 0
	for e1, e2 in itertools.product(event_d.keys(), event_d.keys()):
		if e1 == e2:
			continue
		sumo += jointcount(event_d, e1, e2)

	return sumo


def all_count_links(link_d):
	sumo = 0
	for (s, t), vals in link_d.items():
		sumo += len(vals)
	return sumo

def jointcount(event_d, a, b):
	# the number of times a and b have same value
	sumo = 0
	for ca in event_d[a]:
		for cb in event_d[b]:
			if ca == cb:
				sumo += 1
	return sumo

def jointcountlinks(link_d, a, b):

	return len(link_d[(a,b)] + link_d[(b,a)])

def jointprob(event_d, a, b, val):
	denom = all_count(event_d)
	numer = count(event_d, a, b, val)
	return numer / denom


def prob_e_in_link(link_d, a):
	sumo = 0
	for (s, t), vals in link_d.items():
		if s==a or t==a:
			sumo+= len(vals)
	return sumo / all_count_links(link_d)


def count(event_d, a, b, val):
	# number of time a and b have value
	sumo = 0
	for ca in event_d[a]:
		for cb in event_d[b]:
			if ca == val and cb == val:
				sumo += 1
	return sumo

def pmi_val(event_d, a, b, val):
	if val not in event_d[a] or val not in event_d[b]:
		return 0
	denom = prob(event_d, a, val) * prob(event_d, b, val)
	if denom == 0:
		return 0
	return math.log2(jointprob(event_d, a, b, val) / denom)


def pmi(event_d, a, b):
	if a.cluster_val != b.cluster_val:
		return 0
	return pmi_val(event_d, a.step_name, b.step_name, a.cluster_val)



def avg_pmi_val(event_d, cluster):
	sumo = 0
	for e1, e2 in itertools.product(cluster, cluster):
		if e1 == e2:
			continue
		if e1.cluster_val != e2.cluster_val:
			continue
		sumo += pmi_val(e1.step_name, e2.step_name, e1.cluster_val)
	return sumo / len(cluster)


def member_pmi_fit(event_d, e, cluster):
	sumo = 0
	for event in cluster:
		if event.cluster_val != e.cluster_val:
			continue
		sumo += pmi_dist(e.event_name, event.event_name, event.cluster_val)
	return sumo / len(cluster)


# def singleLink(event_d, S1, S2):
# 	S_prod = list(itertools.product(S1.points, S2.points))
# 	# for ((e1, v1), (e2, v2) in S_prod:
# 	# 	print(v1)
# 	mino = float("inf")
# 	for e1, e2, in S_prod:
# 		if e1.cluster_val != e2.cluster_val:
# 			continue
# 		s = pmi_val(event_d=event_d, a=e1.step_name, b=e2.step_name, val=e1.cluster_val)
# 		if s < mino:
# 			mino = s
# 	return mino


def singleLink(event_d, S1, S2):
	S_prod = list(itertools.product(S1.points, S2.points))
	mino = float("inf")
	for e1, e2, in S_prod:
		s = pmi_dist_2(event_d=event_d, a=e1, b=e2)
		if s < mino:
			mino = s
	return mino





# @clock
def completeLink(event_d, S1, S2):
	S_prod = set(itertools.product(S1, S2))
	return max(pmi_val(event_d, e1, e2, v1) for (e1, v1), (e2, v2) in S_prod if v1 == v2)

# # @clock
# def meanLink(S1, S2):
# 	a1 = (1/len(S1))*sum(s.point for s in S1)
# 	a2 = (1/len(S2))*sum(s.point for s in S2)
# 	return nopointDist(a1, a2)
#
# def nopointDist(a1, a2):
# 	return math.sqrt(np.dot(a1 - a2, a1 - a2))


def pmi_dist(event_d, a, b):
	# a and b are step names
	vals = set(event_d[a]) | set(event_d[b])
	sumo = 0
	for val in vals:
		sumo += pmi_val(event_d, a, b, val)
	return sumo


def pmi_dist_2(event_d, a, b):
	# a and b are step names
	vals = set(event_d[a]) | set(event_d[b])
	sumo = 0
	for val in vals:
		sumo += pmi_val(event_d, a, b, val)
	return sumo


def cpmi(event_d, link_d, a, b):
	event_pmi = pmi_dist2(event_d, a, b)
	numer = jointcountlinks(link_d, a, b) / all_count_links(link_d)
	denom = prob_e_in_link(link_d, a) * prob_e_in_link(link_d, b)
	print(numer/denom)
	return event_pmi + numer/denom


def event_matrix(points, d_method):
	num_events = len(points)
	mat = [[0 for i in range(num_events)] for j in range(num_events)]

	for i, e1 in enumerate(points):
		for j, e2 in enumerate(points):

			if e1 == e2:
				continue

			mat[i][j] = d_method(a=e1.point, b=e2.point)

	return mat


if __name__ == '__main__':
	import SceneDataStructs as SDS
	print('loading scene')
	scene_lib = SDS.load()

	k = 5

	print('getting clusters')
	entity_cluster_map, pd = get_clusters(k, scene_lib)

	print('collecting events')
	ent_clusters_dict = {c: i for i, cluster in enumerate(entity_cluster_map) for c in cluster}

	# events = collect_events(pd, scene_lib)

	print('constructing plans')
	# plans are of the form (scene_name, step_list, ordering graph, causal link graph)
	# plans = plannify_scenes(scene_lib)
	with open('plans.pkl', 'rb') as db:
		plans = pickle.load(db)

	# keys are (step.name, arg.pos), and value is a list of observations of cluster nums in [k]
	print('collecting events')
	event_d, link_d = collect_events(ent_clusters_dict, plans)
	event_types = list(event_d.keys())

	# these are nested lists of the form [[(step.name, arg.pos)]] whose internal lists are k-grams
	# k16g, k8g = collect_kgram_events('scene_lib_file', ent_clusters_dict)

	# dist_method = partial(pmi_val, event_d=event_d)
	# first, create clusters for each action-type by cluster_val in len(entity_cluster_map)
	# initial_cluster_items = itertools.product(event_types, [i for i in range(len(entity_cluster_map))])

	# points = [NamedPoint(i, Event(p, j)) for i, (p, j) in enumerate(initial_cluster_items)]

	# d_method = partial(pmi, event_d=event_d)
	print('constructing event matrix')
	# event_mat = event_matrix(points, d_method)
	# with open('event_matrix.pkl', 'rb') as db:
	# 	event_mat = pickle.load(db)


	print('spectral clustering actions')
	# m = cluster_this(points, event_mat, 24)

	# these grams are sets with elements of the form (step_name, position)
	# 1) Construct a dictionary k16_dict
	# k16g, k8g = collect_kgram_events('scene_lib_file', ent_clusters_dict)


	# d_method = partial(pmi, event_d=event_d)
	# print('finding initial centers')
	# cluster_dict, phi = gonzales(points, 8, d_method)
	# print(cluster_dict)
	# clusters = list(cluster_dict.values())
	# print('clustering remaining points')
	# full_clusters = closest_centers(points, clusters, d_method)
	# h_clusters = [Cluster(i, Event(p, j)) for i, (p, j) in enumerate(initial_cluster_items)]
	# event_types
	h_clusters = [Cluster(i, e) for i, e in enumerate(event_types)]
	final_clusts = agglom_pmi_clustering(h_clusters, 8, partial(singleLink, event_d=event_d, link_d))

	for clust in final_clusts:
		print('cluster:')
		for c in clust:
			print(c)
		print('\n')

	print('check')
	# for each event,