## Read western duel corpus workbook
# Read headers
# skip blank rows
# save and load data with pickle

from openpyxl import load_workbook
from collections import defaultdict

def clean(s):
	if not isinstance(s, str):
		return s
	return ''.join(s.split()).lower()

wb = load_workbook(filename='Western_duel_corpus.xlsx', data_only=True)
#first worksheet
ws = wb.worksheets[0]
rows = list(ws.rows)
header_rows = [clean(r.value) for r in rows[0]]
rows = [list(r) for r in rows[1:]]



class Header:
	def __init__(self, row_0):
		self._header = row_0

	def __len__(self):
		return len(self._header)

	def __getitem__(self, name):
		return self._header.index(name)

	@property
	def names(self):
		return self._header

	def fromTo(self, _from, _to):
		return (self[_from], self[_to]+1)

	def namesFromTo(self, _from, _to):
		return self._header[_from:_to]

	def __repr__(self):
		return self._header.__repr__()

header = Header(header_rows)
action_start, action_stop = header.fromTo('actionnumber', "conclusionstatus")

class Scene:
	#name, ordered list of shots, entities

	def __init__(self, name):
		self._shots = []

	def __len__(self):
		return len(self._shots)

	def __getitem__(self, item):
		return self._shots[item]

	def append(self, item):
		self._shots.append(item)

	def __getattribute__(self, name):

		if name is 'shot' and not self.shots:
			print('no shot')
			return -1
		else:
			return object.__getattribute__(self, name)

	def addShot(self, shot):
		self.shots.append(shot)

	def __repr__(self):
		shots = [''.join('str([shot for shot in self])
		return 'Scene: ' + ''.join(shot for shot in shots)


class Action:

	def __init__(self, **kwargs):
		self.type = kwargs['actionpredicates']
		self._args = [kwargs['arguments']]
		self.concluded = kwargs['conclusionstatus']

	def appendArg(self, arg):
		self._args.append(arg)

	def __len__(self):
		return len(self._args)

	def __getitem__(self, item):
		return self._args[item]

	def __repr__(self):
		args = str([arg for arg in self])
		return '{}'.format(self.type) + args


#store by scene name

class Shot:

	def __init__(self, first_action, **kwargs):
		#self.__dict__.update(kwargs)
		self.shot_values = kwargs
		self.actions = [first_action]

	def update(self, row_values):
		#thus far, only update is to add argument to action
		arg = row_values[header['arguments']]
		self.actions[-1].appendArg(arg)

	def __repr__(self):
		actions = [' '.join('\t' + str(i) + ': ' + str(action) for action in self.actions)]
		return 'Shots: \n' + ''.join(['{}'.format(action) for action in actions])


class SceneLib:
	def __init__(self, names):
		self._scenes = defaultdict(Scene)
		for name in scene_names:
			self._scenes[name] = Scene(name)

	def __len__(self):
		return len(self._scenes)

	def __getitem__(self, item):
		return self._scenes[item]

	def __repr__(self):
		scenes = [''.join('\n' + str(key) + ' : ' + str(value) for key,value in self)]
		return 'All Scenes: ' + '\n' + ''.join(['{}'.format(scene) for scene in scenes])


#Scene Lib
scene_names = {clean(s.value) for s in list(ws.columns)[0][1:]}
scenes = SceneLib(scene_names)

print('starting parsing')

last_shot_num = 0
last_action_num = 0
for row in rows:

	row_values = [clean(r.value) for r in row]
	scene_name = row_values[0]

	action_params = dict(zip(header.namesFromTo(action_start, action_stop), row_values[action_start:action_stop]))

	if len(row_values) != len(header):
		print("ALERT, |row_values| != |header|")

	elif row_values[header['shotnumber']] == last_shot_num:

		# same shot,
		last_shot = scenes[row_values[0]].shots[-1]

		action_num = row_values[header['actionnumber']]
		if action_num != last_action_num:
			# new action
			last_shot.actions.append(Action(**action_params))
			last_action_num += 1

		else:
			# new action argument
			last_shot.update(row_values)
	else:
		# new shot, first action
		first_action = Action(**action_params)
		new_shot = Shot(first_action, **dict(zip(header.names, row_values)))
		scenes[scene_name].append(new_shot)

		if row_values[header['shotnumber']] == 1 and not last_shot_num == 0:
			#new scene, reset counter
			last_shot_num = 1
		else:
			last_shot_num += 1

		last_action_num = 1



print('stop')
#
# def readRows(self, rows):
# 	for row in rows:
