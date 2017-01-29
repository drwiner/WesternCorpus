from ReadWorkbook import SceneLib, Scene, Action, Shot
import pickle
def load(d='scenelib.pkl'):
	return pickle.load(open(d, 'rb'))

scene_lib = load()

documents = dict()

for name, scene in scene_lib.items():
	if name is None or name is 'None':
		continue
	documents[name] = []
	for shot in scene:
		documents[name].append(shot.sentence)

print('ok')