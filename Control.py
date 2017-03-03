import SceneDataStructs as SDS
from SceneDataStructs import readCorpus, parse
from SceneDataStructs import Scene, Shot, Action, ActionType, SceneLib
from Entities import Entity, assignRoles
from Actions import assignActionTypes, analyzeActions

def readAndSaveFromScratch():
	rc = readCorpus()
	scene_lib = parse(rc)
	action_count = analyzeActions(scene_lib)
	assignActionTypes(scene_lib, action_count)
	assignRoles(scene_lib)
	SDS.save_scenes(scene_lib)


if __name__ == '__main__':
	readAndSaveFromScratch()
	# scene_lib = SDS.load()
	# print(scene_lib)