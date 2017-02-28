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


story_text = dict()
for doc_name, sentences  in documents.items():
	story_text[doc_name] = '. '.join(sentences)
	print(story_text[doc_name])

print('ok')

import spacy

def processScene(scene_text):
	# extract important lexical information
	# extract by sentence
	# NER
	# coreference resolution
	return None


nlp = spacy.load('en')
for doc_name, para in story_text.items():
	doc = nlp(para)
	for proc in nlp.pipeline:
		proc(doc)

	lexical_items = processScene(doc)

print('ok')



# read in entity types.