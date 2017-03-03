import spacy
nlp = spacy.load('en')
import SceneDataStructs as SDS

def readSentences(scene_lib):
	documents = dict()
	print('Loading sentences from scenes')

	for name, scene in scene_lib.items():
		if name is None or name is 'None' or name in SDS.EXCLUDE_SCENES:
			continue
		documents[name] = []
		for i, shot in enumerate(scene):
			documents[name].append(shot.orig_sentence)

	# process the scene sentences as a whole.
	story_text = dict()
	for doc_name, sentences  in documents.items():
		story_text[doc_name] = '. '.join(sentences)
		# print(story_text[doc_name])

	for doc_name, para in story_text.items():
		doc = nlp(para)
		for proc in nlp.pipeline:
			proc(doc)
		scene_lib[doc_name].sentences = doc
		z_sents = zip(list(scene_lib[doc_name]), doc.sents)
		for shot, sent in z_sents:
			shot.nlp_sentence = sent



def processScene(scene_text):
	# extract important lexical information
	# extract by sentence
	# NER
	# coreference resolution
	return None

if __name__ == '__main__':
	from SceneDataStructs import Scene, SceneLib, Shot, Action, ActionType
	from Entities import Entity

	scene_lib = SDS.load()
	readSentences(scene_lib)
	print('check it here')