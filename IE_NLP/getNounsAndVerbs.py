import SceneDataStructs as SDS
# from SceneDataStructs import readCorpus, parse
# from SceneDataStructs import Scene, Shot, Action, ActionType, SceneLib

scene_lib = SDS.load()

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


def suftab(wrd):
	return wrd + '\t'

output = open('duelcorpus.parse', 'w')
sents = []
for span in doc.sents:
	sents.append([doc[i] for i in range(span.start, span.end)])


for sent in sents:
	for i, token in enumerate(sent):
		parsed_line = suftab(str(i+1)) + suftab(token.orth_) + suftab('_') + suftab(token.pos_) + suftab(token.pos_)
		parsed_line += suftab('_') + suftab(str(sent.index(token.head)+1)) + suftab(token.dep_) + '_\t_\n'
		output.write(parsed_line)
	output.write('\n')