from collections import defaultdict
from collections import Counter
import os
from os.path import isfile, join

ROLES = 'duel-location duel-weapon dueler observer thug amigo bartender'.split()
PERSON_ROLES = 'dueler observer thug amigo bartender'.split()
LOC_ROLES = ['duel-location']
WEAPON_ROLES = ['duel-weapon']

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
					AssertionError(sp)
					continue
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

def entArgMat(scene_lib):
	entity_arg_matrix = defaultdict(int)
	entities = set()

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
					col = str(action._type) + str(i)
					entity_arg_matrix[(arg.name, col)] += 1
					entities.add(arg.name)
	return entities, entity_arg_matrix


def write_entArgMatrix_toFile(entities, entity_arg_matrix, columns):
	with open('entity_arg_matrix.txt', 'w') as emt:
		emt.write('\t' + '\t'.join(c for c in columns) + '\n')
		for ent in entities:
			emt.write(ent + '\t')
			for c in columns:
				emt.write(str(entity_arg_matrix[(ent, c)]) + '\t')
			emt.write('\n')


def loadColNames(pd):
	cols = []
	for p_name, apred in pd.items():
		for i in range(apred._num_args):
			cols.append(p_name + str(i))
	return cols

def entMat(scene_lib):
	# one entMat per scene
	entity_matrices = {sc_name: defaultdict(set) for sc_name, scene in scene_lib.items() if sc_name not in SDS.EXCLUDE_SCENES}

	for sc_name, scene in scene_lib.items():
		if sc_name in SDS.EXCLUDE_SCENES:
			continue
		sc_entity_matrix = entity_matrices[sc_name]
		for shot in scene:
			for action in shot.actions:
				if action._type is None or str(action._type).lower() == 'none':
					continue
				for i, a in enumerate(action):
					for j, b in enumerate(action):
						if i == j:
							continue
						sc_entity_matrix[(a.name, b.name)].add(str(action._type))
	return entity_matrices


def write_entMatrix_toFile(scene_lib, ent_mats):
	for scene_name, ent_mat in ent_mats.items():
		scene = scene_lib[scene_name]
		with open('ent_mats//{}'.format(scene_name) + '.txt', 'w') as ems:
			ems.write('\t' + '\t'.join(ent.name for ent in scene.entities) + '\n')
			for ent in scene.entities:
				ems.write(ent.name + '\t')
				for e in scene.entities:
					preds = ent_mat[(ent.name, e.name)]
					if len(preds) > 0:
						ems.write('{}\t'.format(preds))
					else:
						ems.write('{}\t'.format('-'))
				ems.write('\n')


def entityGrid(scene_lib):
	entity_grids = {sc_name: defaultdict(int) for sc_name, scene in scene_lib.items() if
	                sc_name not in SDS.EXCLUDE_SCENES}

	# e_grid = {(s, e) for s in shots for e in ents}
	for sc_name, scene in scene_lib.items():
		if sc_name in SDS.EXCLUDE_SCENES:
			continue
		entity_grid = entity_grids[sc_name]
		for i, shot in enumerate(scene):
			for ent in shot.entities:
				entity_grid[(i, ent.name)] = 1.0
			for ent in shot.foreground:
				entity_grid[(i, ent[0])] += 1.0 + (1.0/len(shot.foreground))
	return entity_grids

def write_entGrid_toFile(scene_lib, ent_grids):
	for scene_name, egrid in ent_grids.items():
		if scene_name in SDS.EXCLUDE_SCENES:
			continue
		scene = scene_lib[scene_name]
		scene_ents = scene.entities
		with open('ent_grids//{}'.format(scene_name) + '.txt', 'w') as egs:
			egs.write('\t' + '\t'.join(e.name for e in scene_ents) + '\n')
			for i, shot in enumerate(scene):
				egs.write(str(i) + '\t')
				for ent in scene_ents:
					egs.write(str(egrid[(i, ent.name)]) + '\t')
				egs.write('\n')


if __name__ == '__main__':
	import SceneDataStructs as SDS

	do_ent_arg  = False
	do_ent      = False
	do_ent_grid = False

	# load scenes from memory
	scene_lib = SDS.load()

	# make dictionary of action predicates
	pd = predicate_dict()

	if do_ent_arg:
		# make col names for entity arg matrix (type1arg0, type1arg1,...,) x (e1, e2,..., ek)
		cols = loadColNames(pd)
		# make entity arg matrix and write to file
		ents, ea_mat = entArgMat(scene_lib)
		write_entArgMatrix_toFile(ents, ea_mat, cols)

	if do_ent:
		# now make entity matrix, rows and columns are ents. each value is the set of action-predicates shared.
		emats = entMat(scene_lib)
		write_entMatrix_toFile(scene_lib, emats)

	if do_ent_grid:
		egrids = entityGrid(scene_lib)
		write_entGrid_toFile(scene_lib, egrids)

