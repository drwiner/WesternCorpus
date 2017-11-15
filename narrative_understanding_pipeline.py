import SceneDataStructs as SDS
from SceneDataStructs import readCorpus, parse
from SceneDataStructs import Scene, Shot, Action, ActionType, SceneLib
from Entities import Entity, assignRoles
from Actions import assignActionTypes, analyzeActions, temporalizeActions
from plot_induction import induce_plots
from Stepify import plannify
# from NLP import readSentences


def readAndSaveFromScratch(text_name=None):
	print('reading corpus')
	if text_name is not None:
		rc = readCorpus(text_name)
	else:
		rc = readCorpus()
		# text_name = 'overwritable_corpus.txt'
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
	plannify(scene_lib)
	# induce_plots('scene_lib_file')
	# readSentences(scene_lib)  - no nlp today
	return scene_lib

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


from datetime import date, datetime, time
import json
def json_serial(obj):
	if isinstance(obj, (time, datetime, date)):
		serial = obj.isoformat()
		return serial

	try:
		return obj.asDict()
	except ValueError(str(obj)):
		# if isinstance(obj, (datetime, datetime.time)):
		# 	serial = obj.isof
		raise TypeError("Type %s is not serializable" % type(obj))

def write_to_json(scene_lib):

	# from bson import json_util

	# prep scene_lib for json
	if type(scene_lib) is dict:
		scene_lib_as_dict = {key: value.asDict() for key, value in scene_lib.items()}
	else:
		scene_lib_as_dict = scene_lib.asDict()
	with open('western_duel_film_corpus.json', 'w') as fp:
		fp.write(json.dumps(scene_lib_as_dict, indent=4, default=json_serial))




if __name__ == '__main__':
	old_file_name = 'Western_duel_corpus_edited.xlsx'
	master_file_name = 'WESTERN_DUEL_CORPUS_MASTER_update.xlsx'
	# master_file_name = 'WESTERN_DUEL_CORPUS_MASTER_last_update.xlsx'
	rc = readCorpus(file_name=master_file_name)
	parse(rc)
	#
	# # start pipeline
	scene_lib = readAndSaveFromScratch(text_name=master_file_name)
	#
	SDS.save_scenes(scene_lib, master_file_name[0:-4] + '.pkl')
	RELOAD = 0
	if RELOAD:
		scene_lib = SDS.load('WESTERN_DUEL_CORPUS_MASTERt_update..pkl')
		# SDS.save_scenes(scene_lib, 'scenelib.pkl')
		write_to_json(scene_lib)
	# print('inspect')
	# byactiontype_dic(scene_lib)
