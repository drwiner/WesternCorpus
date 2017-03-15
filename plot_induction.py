
# def induce_intervals(scene_lib):
# 	for n, scene in scene_lib.items():
# 		scene_actions = [action for action in shot.actions for shot in scene]
# 		for action in scene_actions:
# 			# find earliest appearance of

import math
from collections import defaultdict

class ActionObs:
	def __init__(self, name, args, unique_id):
		self._name = name
		self._args = args
		self._id = unique_id
		self.starts = 'phi'
		self.finishes = 'psi'
		self.observed_at = []
		self.shot_nums = []
		# this will be transformed into a plan step?
		self.preconditions = []
		self.effects = []
		self.consenters = []

	def __eq__(self, other):
		if self._id == other._id:
			return True
		return False

	def __hash__(self):
		return hash(self._name) ^ hash(self._id)

	def __repr__(self):
		return self._name + '\tid={}\t'.format(str(self._id)) + '\t'.join(arg for arg in self._args)

def parseActionInstances(obs_shot_zip):

	action_instances = []
	timestep = 0
	_id = 0
	open_action_instances = dict()

	for obs, shot_num in obs_shot_zip:
		action = tuple(obs[0:-2])
		starts = int(obs[-2])
		finishes = int(obs[-1])
		if starts:
			aobs = ActionObs(action[0], action[1:], _id)
			action_instances.append(aobs)
			_id += 1
			aobs.starts = timestep
			if finishes:
				aobs.finishes = timestep
			else:
				open_action_instances[action] = aobs
		elif finishes:
			if action in open_action_instances.keys():
				aobs = open_action_instances[action]
				aobs.finishes = timestep
				del open_action_instances[action]
			else:
				# first time we see it, it finishes
				aobs = ActionObs(action[0], action[1:], _id)
				aobs.finishes = timestep
				_id += 1
				action_instances.append(aobs)
		else:
			# continues
			if action in open_action_instances.keys():
				aobs = open_action_instances[action]
				aobs.observed_at.append(timestep)
			else:
				aobs = ActionObs(action[0], action[1:], _id)
				action_instances.append(aobs)
				_id += 1
				aobs.observed_at.append(timestep)
				open_action_instances[action] = aobs
		timestep += 1
		aobs.shot_nums.append(shot_num)

	for ai in open_action_instances.values():
		ai.finishes = timestep
	return action_instances

def arg_intersect(arg_list_1, arg_list_2):
	for a1 in arg_list_1:
		for a2 in arg_list_2:
			if a1 == a2:
				return True
	return False

def max_o_same_arg(a, action_instances):
	if a.observed_at:
		first_seen = a.observed_at[0]
	else:
		first_seen = a.finishes
	max_seen = -1

	for obs in action_instances:
		if not arg_intersect(a._args, obs._args):
			continue

		if obs.finishes == 'psi':
			if len(obs.observed_at) == 0:
				latest = obs.starts
			else:
				latest = obs.observed_at[-1]
		else:
			latest = obs.finishes

		if max_seen < latest < first_seen:
			max_seen = latest

	if max_seen == -1:
		return first_seen
	return max_seen

def min_o_same_arg(a, action_instances):
	if a.observed_at:
		last_seen = a.observed_at[-1]
	else:
		last_seen = a.starts
	min_seen = float('inf')

	for obs in action_instances:
		if not arg_intersect(a._args, obs._args):
			continue

		if obs.starts == 'phi':
			if len(obs.observed_at) == 0:
				earliest = obs.finishes
			else:
				earliest = obs.observed_at[0]

		else:
			earliest = obs.starts

		if min_seen > earliest > last_seen:
			min_seen = earliest

	if min_seen == float('inf'):
		return last_seen
	return min_seen

def find_interval_span(a, action_instances):

	if a.starts == 'phi':
		a.starts = max_o_same_arg(a, action_instances) + 1
	if a.finishes == 'psi':
		a.finishes = min_o_same_arg(a, action_instances) - 1

def induce_intervals(shot_dict):

	scene_obs_list = []
	shot_nums = []
	for i in range(len(shot_dict.keys())):
		# each obs is a list of more line parameters
		action_list = shot_dict[str(i)]
		scene_obs_list.extend(action_list)
		shot_nums.extend([i for j in range(len(action_list))])

	obs_shot_zip = zip(scene_obs_list, shot_nums)

	action_instances = parseActionInstances(obs_shot_zip)
	for ai in action_instances:
		find_interval_span(ai, action_instances)

	return action_instances


def get_last_timestep(end_dict):
	return sorted(list(end_dict.keys()))[-1]

def write_ais(sc_name, ais):
	start_dict = {ai.starts: ai for ai in ais}
	end_dict = {ai.finishes: ai for ai in ais}

	with open('plot_inductions//' + sc_name, 'w') as pisc:
		for i in range(int(get_last_timestep(end_dict))):

			if i in start_dict.keys():
				pisc.write(str(start_dict[i]) + '\tstarts\t' + '\t'.join(str(sn) for sn in start_dict[i].shot_nums) + '\n')

			if i in end_dict.keys():
				pisc.write(str(end_dict[i]) + '\tends\t' + '\t'.join(str(sn) for sn in end_dict[i].shot_nums) + '\n')



def induce_plots(scene_lib_file_name):
	scene_dict = defaultdict(list)

	with open(scene_lib_file_name) as scene_lib_file:
		for line in scene_lib_file:
			sp = line.split()
			if sp[-1] not in {'0', '1'}:
				continue
			scene_dict[sp[0]].append(sp[1:])

	ai_scene_dict = dict()
	for sc_name, scene_list in scene_dict.items():
		shot_dict = defaultdict(list)
		for elm in scene_list:
			shot_dict[elm[0]].append(elm[1:])
		ais = induce_intervals(shot_dict)
		# use these for orderings
		ai_scene_dict[sc_name] = ais
	return ai_scene_dict


if __name__ == '__main__':
	act_inst_dict = induce_plots('scene_lib_file')
	for sc, act_instances in act_inst_dict.items():
		write_ais(sc, act_instances)