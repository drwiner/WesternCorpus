import SceneDataStructs as SDS
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
				if action._type not in encountered:
					actions_across_scenes[action._type] += 1
					encountered.add(action._type)

				# how many times does the actino occur
				action_count[action._type] +=1

				# how many arguments in the action
				if action._type not in action_args:
					action_args.update({action._type: len(action)})

	print(action_args)
	print('\n')
	print(actions_across_scenes)
	print('\n')
	print(action_count)
	print('\n')
	for action, count in action_count.items():
		print(action, count)

	return action_count



def readActionTypes(action_map_file):
	action_dict = dict()
	for line in action_map_file:
		line_split = line.split()
		new_type = line_split[-1].lower()
		if new_type == 'none':
			new_type = None
		action_dict[line_split[0].lower()] = SDS.ActionType(line_split[0].lower(), line_split[1].lower(), new_type)
	return action_dict

def assignActionTypes(action_count):
	print('assigning action Types')
	for sc_name, scene in scene_lib.items():
		if sc_name is None or sc_name in SDS.EXCLUDE_SCENES:
			continue
		print(sc_name)
		action_map_file = open('action_dict_mapping.txt')
		ad = readActionTypes(action_map_file)
		scene.substituteActionTypes(ad, action_count)


if __name__ == '__main__':


	scene_lib = SDS.load()
	print('here')
	print(scene_lib)

	action_count = analyzeActions()
	assignActionTypes(action_count)
