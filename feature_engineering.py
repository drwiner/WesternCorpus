"""
The purpose of this script is to calculate the observation features (and labels)

"""
import SceneDataStructs as SDS
from collections import defaultdict
from collections import Counter


# basic scales
CU = ['cu', 'ecu', 'mcu', 'closeup', 'extremecloseup', 'extremecu', 'mediumcu', 'cutoecu', 'tightecu', 'mcutocu', 'cutomcu', 'tightcu', 'cujohnny', 'cudoc', 'ms-cu', 'ecu/profile', 'cuprofile', 'cu/profile', 'mcudoc', 'culockettoface']
WAIST = ['waist', 'waistshot', 'waistshot(\"cowboy\")', 'waistshot-monacoexitslleavingcolonelaloneinframe', 'waistshotslightlybelowbeltline', 'waisttoms', 'wast', '3/4figurewaist', 'waist-3.25', 'waistshot/2characters', 'waiste', 'waist/widebg', '3/4figuretowaist', '3.4-waist', 'waist/reverse', '2-shot/waist']
FIGURE = ['figure', '3/4figure', '0.75', 'fullfigure', 'full', '3.25', 'full-figure', 'ful', 'fullshot', '3/4figureshot', '3/4fig', '0.75-ff', 'full-3.25', '3.25shot']
WIDE = ['wide','w', 'wideshot', 'mediumwide', 'extremewide', 'ew', 'wide/full', 'extremewideshot', 'extremewideshot3characters', 'medwide\"minimaster\"', 'extremewideshotrevealinghandinfg',
'full-wide', 'wideangle', 'medwide']
SCALES = [CU, WAIST, FIGURE, WIDE]

# different scales for foreground and background entities
CU_WIDE = ['overshoulder/extremewide', 'closeup/wide', 'extremecloseup/wide', 'wide/ovs', 'cu/widebg', 'wideovershouldertobandits','w-cuforeground', 'cu-widebackground', 'cu-wide', 'closeovershoulder/wide', 'cu-w']
CU_FIGURE = ['closeup/3.25', 'closeup/0.75bg']
CU_WAIST = ['waist/closeup']
WAIST_WIDE = ['0.75/wide', '0.75/w', 'wideshotwithjoeinnearfg', '0.75ovs/wide', 'waist/widebg', ]
FIGURE_WIDE = ['0,75/w', 'ff/w', 'full-wide', 'wide/full']
TWO_SCALES = [CU_WIDE, CU_FIGURE, CU_WAIST, WAIST_WIDE, FIGURE_WIDE]
TWO_SCALE_LABELS = [('cu','wide'), ('cu', 'figure'), ('cu', 'waist'), ('waist', 'wide'), ('figure', 'wide')]


def extract_scale(scale, zeta):
	new_scale = None
	for scale_type in SCALES:
		if scale in scale_type:
			return scale_type[0]
	if new_scale is None:
		for scale_type in TWO_SCALES:
			for j, scale in enumerate(scale_type):
				scale_tuple = TWO_SCALE_LABELS[j]
				if zeta == 1:
					# background
					return scale_tuple[1]
				else:
					return scale_tuple[0]
	return new_scale


BG = ['background', 'ackground', 'backgrooud']
FG = ['foreground', 'foeground', 'foregorund', 'forground']
ONE_WORD_POS = ['left', 'right', 'center', 'full']
POS = ['left', 'right', 'center-right', 'center-left', 'left-center', 'full', 'center', 'right-center']


def extract_zeta(pos, zeta):
	sp = pos.split('-')
	collected_parts = []
	_zeta = None
	_pos = None

	for part in sp:
		if part in ONE_WORD_POS: collected_parts.append(part)
		if part in BG: _zeta = 1
		elif part in FG: _zeta = 0

	if 'left' in collected_parts:
		if 'center' in collected_parts: _pos = 'center-left'
		elif 'full' in collected_parts: _pos = 'full'
		else: _pos = 'left'
	elif 'right' in collected_parts:
		if 'center' in collected_parts: _pos = 'center-right'
		elif 'full' in collected_parts: _pos = 'full'
		else: _pos = 'right'
	else:
		if 'full' in collected_parts: _pos = 'full'
		elif 'center' in collected_parts: _pos = 'center'
		else: raise ValueError('Should be a left-right-center position')


	if _zeta is None: _zeta = zeta
	if _pos is None: _pos = pos

	return _pos, _zeta

def extract_composition(_str):
	"""
	:param _str: a figureobjs(shotstart) string
	:return: one of (left, center-left, center, center-right, right), plus forground/background
	"""

	ents = []
	if _str is None or _str == 'None' or _str == 'none':
		return ''
	str_list = _str.split(',')
	for i in str_list:
		if i == '':
			continue
		z = i.split('(')
		new_ent = []
		for k in z:
			if k == '':
				continue
			m = k.split(')')
			for q in m:
				if q == '':
					continue
				new_ent.append(q)
		# new_ent[1]
		ents.append(new_ent)
	return ents


def extract_labeled_features(scene_lib):
	none_town = {'None', 'none', None}
	# gOAL: create tuple (entity, action, starts, finishes, shot_num, scale, fore/back, horizon_pos)

	labeled_observations_per_scene = dict()
	for scene_name, scene in scene_lib.items():
		labeled_observations_per_scene[scene_name] = []
		for shot_num, shot in enumerate(scene):

			if shot.scale in none_town:
				continue

			current_scale = str(shot.scale)


			fground_dict = {str(ent[0]): str(ent[1]) for ent in shot.foreground if len(ent)>1}
			bground_dict = {str(ent[0]): str(ent[1]) for ent in shot.background if len(ent)>1}


			# shot_scale_dict[shot.scale] += 1
			for action in shot.actions:
				if action in none_town or action._type in none_town:
					continue

				if type(action._type) is str:
					action_name = action._type

				elif action._type.type_name in none_town or action._type.type_name in none_town:
					action_name = action._type._orig_name
				else:
					action_name = action._type.type_name

				if action_name in none_town or str(action_name) in none_town:
					continue

				# check for each argument if any of them are in the shot.
				arg_2_pos = dict()
				for arg in action._args:
					if str(arg) in fground_dict.keys():
						pos = (0, fground_dict[str(arg)])
					elif str(arg) in bground_dict.keys():
						pos = (1, bground_dict[str(arg)])
					else:
						pos = (None, None)
					arg_2_pos[str(arg)] = pos

				# create observation for each entity
				for arg, pos in arg_2_pos.items():
					labeled_observation = (
					arg, action_name, action.starts, action.finishes, scene_name, shot_num, current_scale, pos[0],
					pos[1])
					labeled_observations_per_scene[scene_name].append(labeled_observation)

	return labeled_observations_per_scene


def extract_and_print_original_observations(scene_lib, file_name):
	labeled_features = extract_labeled_features(scene_lib)

	with open(file_name, 'w') as asd:
		for scene_name, observation_list in labeled_features.items():
			for obs in observation_list:
				asd.write(str(obs))
				asd.write('\n')
		asd.write('\n')


def clean_observations(obs_file):
	cleaned_list = []
	with open(obs_file, 'r') as asb:
		for line in asb:
			if line == '\n':
				continue

			feat = eval(line)
			if feat[-1] is None:
				continue
			if feat[-2] is None:
				continue

			zeta = feat[-2]
			pos = feat[-1]
			scale = feat[-3]

			# first, make sure zeta is accurate
			(new_pos, new_zeta) = extract_zeta(pos, zeta)
			new_scale = extract_scale(scale, zeta)
			# new scale commandeered
			cleaned_list.append((feat[0], feat[1], feat[2], feat[3], feat[4], feat[5], new_scale, new_zeta, new_pos))


	with open('observation_features_cleaned.txt', 'w') as asd:
		for obs in cleaned_list:
			asd.write(str(obs))
			asd.write('\n')


def get_most_frequent_actions(obs_file):
	actions = []

	with open(obs_file, 'r') as asb:
		for line in asb:
			if line == '\n':
				continue
			feat = eval(line)
			actions.append(feat[1])

	c_a = Counter(actions)
	x_list = c_a.most_common(39)
	acts = [x[0] for x in x_list]
	return acts


def clean_actions(obs_file):
	top_acts = get_most_frequent_actions(obs_file)

	new_obs = []
	with open(obs_file, 'r') as asd:
		for line in asd:
			if line =='\n':
				continue
			feat = eval(line)
			if feat[1] in ['firegun', 'aimgun', 'getshot']:
				if feat[1] == 'firegun':
					new_line = str(
						(feat[0], 'fire-gun', feat[2], feat[3], feat[4], feat[5], feat[6], feat[7], feat[8])) + '\n'
				elif feat[1] == 'aimgun':
					new_line = str(
						(feat[0], 'aim-gun', feat[2], feat[3], feat[4], feat[5], feat[6], feat[7], feat[8])) + '\n'
				else:
					new_line = str(
						(feat[0], 'get-shot', feat[2], feat[3], feat[4], feat[5], feat[6], feat[7], feat[8])) + '\n'
			elif feat[1] not in top_acts:
				continue
			else:
				new_line = line

			# fix some minor problems with actions; if number of items on feature changes, need more clever strategy

			new_obs.append(new_line)

	with open('observation_features_cleaned_action-pruned.txt', 'w') as asb:
		for obs in new_obs:
			asb.write(obs)

def eval_feats(obs_file):
	actions = []
	scales = []
	comps = []
	with open(obs_file, 'r') as asb:
		for line in asb:
			if line == '\n':
				continue
			feat = eval(line)

			actions.append(feat[1])
			scales.append(feat[6])
			comps.append(feat[-1])

	c_a = Counter(actions)
	c_s = Counter(scales)
	c_c = Counter(comps)
	print('stop')

if __name__ == '__main__':
	# if no SDS to load, go to Narrative Understanding Pipeline and load it up
	scene_lib = SDS.load('WESTERN_DUEL_CORPUS_MASTER_update..pkl')

	obs_file = 'observation_features.txt'
	obs_file_cleaned = 'observation_features_cleaned.txt'
	obs_file_cleaned_pruned = 'observation_features_cleaned_action-pruned.txt'

	# extract_and_print_original_observations(scene_lib, obs_file)
	clean_actions(obs_file_cleaned)
	eval_feats(obs_file_cleaned_pruned)

	# clean_observations(obs_file)
	# clean_actions(obs_file_cleaned)


	print('end')