from ReadWorkbook import SceneLib, Scene, Action, Shot
import pickle
from collections import Counter

scene_lib = None
action_count = Counter()
actions_across_scenes = Counter()
action_args = dict()
# scene_entities = ][\]

def analyzeActions():
	for name, scene in scene_lib.items():
		encountered = set()
		print(name)
		if name is 'None':
			continue
		for shot in scene:
			for action in shot.actions:
				if action is None:
					continue

				# count of actions only if in new scene (out of 30)
				if action.type not in encountered:
					actions_across_scenes[action.type] += 1
					encountered.add(action.type)

				# how many times does the actino occur
				action_count[action.type] +=1

				# how many arguments in the action
				if action.type not in action_args:
					action_args.update({action.type: len(action)})

	print(action_args)
	print('\n')
	print(actions_across_scenes)
	print('\n')
	print(action_count)
	print('\n')
	for action, count in action_count.items():
		print(action, count)

class ActionType:
	def __init__(self, type_name, quant, old_name):
		self.type_name = type_name
		self.num_appearances = quant
		self._orig_name = old_name

	def updateQuant(self, new_quant_data):
		if self.type_name in new_quant_data.keys():
			self.num_appearances = int(new_quant_data[self.type_name])

	def __repr__(self):
		return str(self.type_name)

def readActionTypes():
	action_map = open('action_dict_mapping.txt')
	action_dict = dict()
	for line in action_map:
		line_split = line.split()
		action_dict[line_split[0]] = ActionType(line_split[0], line_split[1], line_split[-1])

if __name__ == '__main__':

	def load(d='scenelib.pkl'):
		return pickle.load(open(d, 'rb'))

	scene_lib = load()
	print('here')
	print(scene_lib)

	analyzeActions()
