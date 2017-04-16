import SceneDataStructs as SDS

scene_lib = SDS.load()
print('loading english')
import spacy
nlp = spacy.load('en')
print('finished loading english')


with open('IE_sent_key.txt', 'w') as ss:
	for name, scene in scene_lib.items():
		if name is None or name is 'None' or name in SDS.EXCLUDE_SCENES:
			continue
		for i, shot in enumerate(scene):
			# action_list =
			ss.write('{} -#- {}\n'.format(shot.orig_sentence, ' '.join(str(action._type) for action in shot.actions)))