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
		self._num_args = num_args
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
	nested_role_lists = [role_dict[m] for m in range(mode)]

	return mode, nested_role_lists

def predicate_dict():
	pred_names = get_pred_names()
	pred_dict = dict()
	for pn in pred_names:
		num, nested_role_lists = predicate_arg_mode(pn)
		pred_dict[pn] = ActionPredicate(pn, num, nested_role_lists)
	return pred_dict

if __name__ == '__main__':
	pd = predicate_dict()