import SceneDataStructs as SDS
from SceneDataStructs import readCorpus, parse
from SceneDataStructs import Scene, Shot, Action, ActionType, SceneLib
from Entities import Entity, assignRoles
from Actions import assignActionTypes, analyzeActions, temporalizeActions
from plot_induction import induce_plots
# from NLP import readSentences


def readAndSaveFromScratch():
	print('reading corpus')
	rc = readCorpus()
	scene_lib = parse(rc)

	""" PIPELINE
		analyzeActions(scene_lib) -get count of actions
		assignActionTypes(scene_lib, action_count) - use action-mapping dictionary to swap predicates
		assignRoles(scene_lib) - use coded entity files in entity folder to label roles
		temporalizeActions(scene_lib) - extract starts/stops
		byactiontype_dic(scene_lib) - make action-types files
	"""
	action_count = analyzeActions(scene_lib)
	assignActionTypes(scene_lib, action_count)
	assignRoles(scene_lib)
	temporalizeActions(scene_lib)
	byactiontype_dic(scene_lib)
	write_to_file(scene_lib)
	# induce_plots('scene_lib_file')
	# readSentences(scene_lib)  - no nlp today
	SDS.save_scenes(scene_lib)

import collections
def byactiontype_dic(scene_lib):
	action_instance_dict = collections.defaultdict(list)
	for s_name, scene in scene_lib.items():
		if s_name in SDS.EXCLUDE_SCENES:
			continue
		for shot in scene:
			for action in shot.actions:
				action_instance_dict[action._type.type_name].append(action)
	for action_type, instance in action_instance_dict.items():
		with open('action_types\\' + str(action_type), 'w') as atfile:
			for inst in instance:
				atfile.write('{}\t'.format(str(inst._type)) + '\t'.join(str(arg) for arg in inst) + '\n')

def write_to_file(scene_lib):
	scene_lib_file = open('scene_lib_file', 'w')
	for scene_name, scene in scene_lib.items():
		if scene_name in SDS.EXCLUDE_SCENES:
			continue
		for i, shot in enumerate(scene):
			for action in shot.actions:
				scene_lib_file.write('{}\t{}\t{}\t'.format(scene_name, str(i), str(action._type)) + '\t'.join(
					str(arg) for arg in action._args) + '\t{}\t{}\n'.format(str(action.starts), str(action.finishes)))
	scene_lib_file.close()

if __name__ == '__main__':
	readAndSaveFromScratch()
	# scene_lib = SDS.load()
	# print('inspect')
	# byactiontype_dic(scene_lib)
