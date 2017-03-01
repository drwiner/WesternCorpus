from ReadWorkbook import SceneLib, Scene, Action, Shot
import pickle
def load(d='scenelib.pkl'):
	return pickle.load(open(d, 'rb'))
#empty for default scene_lib name
print('loading scene library')
scene_lib = load()
print(scene_lib)

print('writing entities:')

for sc_name, scene in scene_lib.items():
	if sc_name is None:
		continue
	print(sc_name)
	scene_entity_file = open('entity_folder/scene' + sc_name + '_entities.txt', 'w')
	for entity in scene.entities:
		scene_entity_file.write(entity)
		scene_entity_file.write('\n')