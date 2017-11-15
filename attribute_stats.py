"""
The purpose of this script is to calculate the frequency of averages for select attributes

"""
import SceneDataStructs as SDS
from collections import defaultdict

if __name__ == '__main__':
	# if no SDS to load, go to Narrative Understanding Pipeline and load it up
	scene_lib = SDS.load('WESTERN_DUEL_CORPUS_MASTER_update..pkl')

	shot_scale_dict = defaultdict(int)
	action_dict = defaultdict(int)
	action_shot_dict = defaultdict(list)
	for scene_name, scene in scene_lib.items():
		for shot in scene:

			shot_scale_dict[shot.scale] += 1
			for action in shot.actions:
				if action is None or action._type is None:
					continue

				if type(action._type) is str:
					action_name = action._type
				elif action._type.type_name == 'none' or action._type.type_name is None:
					action_name = action._type._orig_name
				else:
					action_name = action._type.type_name

				action_dict[action_name] += 1

				if str(shot.scale) not in ['','None', 'none'] and shot.scale is not None:
					action_shot_dict[action_name].append(str(shot.scale))

	with open('shot_scale_update.txt', 'w') as sst:
		sst.write('shot_name \t num_appearances\n')
		for shot_name, nums in shot_scale_dict.items():
			sst.write('{}\t{}\n'.format(str(shot_name), str(nums)))

	# with open('action_shot_dict_last_update.txt', 'w') as asd:
	# 	for action, shot_types in action_shot_dict.items():
	# 		asd.write(str(action) + '\t' + str(len(shot_types)) + '\t'.join(str(item) for item in shot_types))
	# 		asd.write('\n')
	#
	with open('action_shot_dict_update.txt', 'w') as asd:
		for action, shot_types in action_shot_dict.items():
			asd.write(str(action) + '\t ' + str(len(shot_types)) + '\t' + str([shot_types]))
			asd.write('\n')

	print('ok')