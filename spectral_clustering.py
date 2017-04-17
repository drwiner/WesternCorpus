# Spectral Clustering algorithm
# Written by David Winer 2017 - 04 - 15


# we'll need a matrix, an ndarray
import numpy as np
from numpy import linalg as LA

from collections import defaultdict
from collections import Counter
import os
from os.path import isfile, join
import math
from hierarchicalClustering import NamedPoint, Cluster
from Lloyds import Gonzales, Lloyds, threeMeansCost, closestToPhi


class ActionPredicate:
	def __init__(self, name, num_args, nested_role_list):
		self._name = name
		self._num_args = num_args[0][0]
		self._appearances = num_args[0][1]
		self.role_dict = dict()
		for i, role_list in enumerate(nested_role_list):
			self.role_dict[i] = set(role_list)


def get_pred_names():
	path = 'action_types'
	files = [f for f in os.listdir(path) if isfile(join(path, f))]
	return files


def predicate_arg_mode(pred_name):
	role_dict = defaultdict(list)
	with open('action_types//' + pred_name) as atp:
		num_arg_counter = []
		for line in atp:
			args = line.split()[1:]
			num_arg_counter.append(len(args))
			for i, arg in enumerate(args):
				sp = arg.split('_')
				if len(sp) != 2:
					raise AssertionError(sp)
				role = sp[1].lower()
				if role == 'none':
					continue
				role_dict[i].append(role)

	tc = Counter(num_arg_counter)
	mode = tc.most_common(1)
	nested_role_lists = [role_dict[m] for m in range(mode[0][0])]

	return mode, nested_role_lists


def predicate_dict():
	pred_names = get_pred_names()
	pred_dict = dict()
	for pn in pred_names:
		num, nested_role_lists = predicate_arg_mode(pn)
		pred_dict[pn] = ActionPredicate(pn, num, nested_role_lists)
	return pred_dict


def entity_by_arg(pd, scene_lib):
	import SceneDataStructs as SDS
	# one entMat per scene
	entity_dict = defaultdict(list)
	arg_positions = []

	for sc_name, scene in scene_lib.items():
		if sc_name in SDS.EXCLUDE_SCENES:
			continue

		for shot in scene:
			for action in shot.actions:
				if action._type is None or str(action._type).lower() == 'none':
					continue

				action_pred = pd[str(action._type)]
				m = action_pred._num_args

				for i, arg in enumerate(action):
					if i + 1 >= m:
						break
					if arg is None or str(arg).lower() == 'none' is None or arg.name.lower() == 'none':
						continue
					arg_pos = (str(action._type), str(i))
					entity_dict[arg.name].append(arg_pos)
					if arg_pos not in arg_positions:
						arg_positions.append(arg_pos)
	return entity_dict, arg_positions


def entity_arg_matrix(ent_list, entity_dict, arg_positions):
	# returns unnormalized laplacian entity matrix
	num_ents = len(entity_dict.keys())
	mat = [[0 for i in range(num_ents)] for j in range(num_ents)]
	for i, a in enumerate(ent_list):
		type_pos_tuples = entity_dict[a]
		for j, b in enumerate(ent_list):
			for t_pos_tuple in entity_dict[b]:
				if t_pos_tuple in type_pos_tuples:
					mat[i][j] += 1
	return mat


def degree_diag(mat):
	# construct D, defined by the weight of the edge between each
	return [sum(mat[i]) for i in range(len(mat))]


def unnormalized_laplacian(mat):
	D = np.diag(degree_diag(mat))
	W = np.array(mat)
	return D - W


def normalized_laplacian(mat):
	d = np.array([v**-.5 if v != 0. else 0 for v in degree_diag(mat)])
	D = np.diag(d)
	I = np.identity(len(mat))
	W = np.array(mat)
	return I - np.dot(D, np.dot(W,D))

def column(matrix, i):
	return [row[i] for row in matrix]


# import matplotlib.pyplot as plt
def spectral_clustering(mat, k, normalized=False):
	# mat should be a nested list
	if normalized:
		L = normalized_laplacian(mat)
	else:
		L = unnormalized_laplacian(mat)
	w, v = LA.eig(L)
	# w are weights (lambdas, eigenvalues)
	# v are eigen vectors
	index_scale = [1. / np.sqrt(w[i]) for i in range(k)]
	# V_k is scaled and the first k

	V_k = np.array([v[:, i]*index_scale[i] for i in range(k)])
	first_k = V_k.T
	x = []
	z = 0
	# should be number of rows is number of entities
	for row in first_k:
		x.append(NamedPoint(z, np.array(row)))
		z += 1



	# cluster points in Y into k clusters
	clusters, phi = Gonzales(x, k)
	clusters, phi = Lloyds(x, clusters, phi, k)
	tmc = threeMeansCost(x, clusters, phi)
	# print(tmc)


	# for i in range(k):
	# 	for j in range(len(phi)):
	# 		if phi[j] == i:
	# 			p = list(x[j].point.real)
	# 			x_0 = p[1]
	# 			y_0 = p[2]
	# 			with open('points.txt', 'a') as point_file:
	# 				point_file.write('{}\t{}\t{}\n'.format(str(i), str(x_0), str(y_0)))

	return clusters, phi, tmc


import itertools


def muc_scoring(K, R):
	# first, for each pair of entities in each key cluster, see if that pair together in response
	numer = 0
	denom = 0
	for clust in K:
		denom += len(clust)-1
		numer += len(clust)
		partitions = []
		for i, j in itertools.product(clust, clust):
			if i == j:
				continue
			for r in R:
				if i not in r and j not in r:
					continue
				if i in r and j not in r:
					exists = 0
					for p in partitions:
						if i in p:
							exists = 1
							break
					if not exists:
						partitions.append({i})
					continue
				if j in r and i not in r:
					exists = 0
					for p in partitions:
						if j in p:
							exists = 1
							break
					if not exists:
						partitions.append({j})
					continue
				# i and j in r
				exists = 0
				for p in partitions:
					if i in p:
						p.add(j)
						exists = 1
					if j in p:
						p.add(i)
						exists = 1
				if not exists:
					partitions.append({i, j})

		# for each pair of partitions which includes a common member, those members must be in same R and can be joined

		p_set = {tuple(sorted(p)) for p in partitions}
		numer -= len(p_set)
	return numer / denom


def b_cubed_scoring(entities, K, R):
	numer = 0
	for k in K:
		for ent in k:
			for r in R:
				if ent in r:
					numer += len(set(r) & set(k))/len(k)
	return numer / len(entities)


def collect_ent_role_keys(scene_lib):
	ent_roles = defaultdict(set)
	for sc_name, scene in scene_lib.items():
		if sc_name in SDS.EXCLUDE_SCENES:
			continue
		for shot in scene:
			for action in shot.actions:
				if action._type is None or str(action._type).lower() == 'none':
					continue

				action_pred = pd[str(action._type)]
				m = action_pred._num_args

				for i, arg in enumerate(action):
					if i + 1 >= m:
						break
					if arg is None or str(arg).lower() == 'none' is None or arg.name.lower() == 'none':
						continue
					ent_roles[arg.role].add(arg.name)
	return ent_roles


def cluster_this(items, mat, k):

	clusters, phi, cost = spectral_clustering(mat, k, normalized=True)
	m = []
	for i in range(k):
		c = []
		for j in range(len(phi)):
			if phi[j] == i:
				c.append(items[j])
		m.append(c)

		print('cluster: ')
		for z in c:
			print(z)
	return m


def get_clusters(k, scene_lib):
	import SceneDataStructs as SDS

	# load scenes from memory
	# scene_lib = SDS.load()

	# make dictionary of action predicates
	pd = predicate_dict()

	# exact entities and corresponding arg positions
	ent_dict, arg_pos_list = entity_by_arg(pd, scene_lib)

	# an E by E matrix whose values are the number of types entites share arg position in action class
	ents = list(ent_dict.keys())
	ent_arg_mat = entity_arg_matrix(ents, ent_dict, arg_pos_list)

	clusters, phi, cost = spectral_clustering(ent_arg_mat, k, normalized=True)
	ent_map = []
	for i in range(k):
		ent_clust = []
		for j in range(len(phi)):
			if phi[j] == i:
				ent_clust.append(ents[j])
		ent_map.append(ent_clust)
		# print('cluster: ')
		# print(ent_clust)
	return ent_map, pd


if __name__ == '__main__':
	import SceneDataStructs as SDS

	# load scenes from memory
	scene_lib = SDS.load()

	# make dictionary of action predicates
	pd = predicate_dict()

	# exact entities and corresponding arg positions
	ent_dict, arg_pos_list = entity_by_arg(pd, scene_lib)

	# an E by E matrix whose values are the number of types entites share arg position in action class
	ents = list(ent_dict.keys())
	ent_arg_mat = entity_arg_matrix(ents, ent_dict, arg_pos_list)

	for k in [4,5,6,7]:
		print(k)
		clusters, phi, cost = spectral_clustering(ent_arg_mat, k, normalized=True)
		ent_map = []
		for i in range(k):
			ent_clust = []
			for j in range(len(phi)):
				if phi[j] == i:
					ent_clust.append(ents[j])
			ent_map.append(ent_clust)
			print('cluster: ')
			print(ent_clust)

		# read in key chains
		ent_role_dict = collect_ent_role_keys(scene_lib)
		K = [values for key, values in ent_role_dict.items()]

		# score
		muc_recall = muc_scoring(K, ent_map)
		print('muc_recall: \t{}'.format(muc_recall))
		muc_precision = muc_scoring(ent_map, K)
		print('muc_precision: \t{}'.format(muc_precision))

		b_recall = b_cubed_scoring(ents, K, ent_map)
		print('b_cubed recall: \t{}'.format(b_recall))
		b_precision = b_cubed_scoring(ents, ent_map, K)
		print('b_cubed precision: \t{}'.format(b_precision))
