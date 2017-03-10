import SceneDataStructs as SDS
from SceneDataStructs import readCorpus, parse
from SceneDataStructs import Scene, Shot, Action, ActionType, SceneLib
from Entities import Entity, assignRoles
from Actions import assignActionTypes, analyzeActions
# from NLP import readSentences

def readAndSaveFromScratch():
	print('reading corpus')
	rc = readCorpus()
	scene_lib = parse(rc)
	action_count = analyzeActions(scene_lib)
	assignActionTypes(scene_lib, action_count)
	assignRoles(scene_lib)
	# readSentences(scene_lib)
	SDS.save_scenes(scene_lib)

def getNounsAndVerbs(scene_lib):
	print('loading english')
	import spacy
	nlp = spacy.load('en')
	print('finished loading english')
	documents = dict()
	all_text = ''
	for name, scene in scene_lib.items():
		if name is None or name is 'None' or name in SDS.EXCLUDE_SCENES:
			continue
		documents[name] = []
		for i, shot in enumerate(scene):
			documents[name].append(shot.orig_sentence)
			all_text += '.\n' + shot.orig_sentence

	# # process the scene sentences as a whole.
	# story_text = dict()
	# for doc_name, sentences in documents.items():
	# 	story_text[doc_name] = '. '.join(sentences)
	#
	# for doc_name, para in story_text.items():
	# 	doc = nlp(para)
	# 	scene_lib[doc_name].sentences = doc
	# 	z_sents = zip(list(scene_lib[doc_name]), doc.sents)
	# 	for shot, sent in z_sents:
	# 		shot.nlp_sentence = sent

	ass = open('all_scene_sentences.txt', 'w')
	ass.write(all_text)
	ass.close()
	doc = nlp(all_text)
	nouns = []
	verbs = []
	for token in doc:
		if token.pos_ == 'NOUN':
			nouns.append(token.orth_)
		if token.pos_ == 'VERB':
			verbs.append(token.orth_)

	from collections import Counter

	ns = open('all_nouns.txt', 'w')
	nounCounter = Counter(nouns)

	for noun, count in nounCounter.most_common():
		ns.write('{}\t{}\n'.format(noun, str(count)))
	ns.close()
	vs = open('all_verbs.txt', 'w')
	verbCounter = Counter(verbs)
	for verb, count in verbCounter.most_common():
		vs.write('{}\t{}\n'.format(verb, str(count)))
	vs.close()



if __name__ == '__main__':
	# readAndSaveFromScratch()
	scene_lib = SDS.load()
	getNounsAndVerbs(scene_lib)
	# print(scene_lib)