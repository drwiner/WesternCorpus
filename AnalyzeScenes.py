from ReadWorkbook import SceneLib, Scene, Action, Shot
import pickle
def load(d='scenelib.pkl'):
	return pickle.load(open(d, 'rb'))
#empty for default scene_lib name
scene_lib = load()
print('here')
print(scene_lib)

