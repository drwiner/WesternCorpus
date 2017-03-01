from ReadWorkbook import SceneLib, Scene, Action, Shot
import pickle
def load(d='scenelib.pkl'):
	return pickle.load(open(d, 'rb'))
#empty for default scene_lib name
scene_lib = load()
print('here')
print(scene_lib)



### Action Library ###
#from collections import defaultdict
from collections import Counter

action_count = Counter()
actions_across_scenes = Counter()
action_args = dict()
# scene_entities = ][\]

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
