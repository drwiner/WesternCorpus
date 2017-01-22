## Read western duel corpus workbook
# Read headers
# skip blank rows
# save and load data with pickle

from openpyxl import load_workbook
from collections import defaultdict

wb = load_workbook(filename='Western_duel_corpus.xlsx', data_only=True)
#first worksheet
ws = wb.worksheets[0]
rows = list(ws.rows)
header_rows = [r.value for r in rows[0]]
rows = [list(r) for r in rows[1:]]

class Header:
	def __init__(self, row_0):
		self._header = row_0

	def __len__(self):
		return len(self._header)

	def __getitem__(self, name):
		return self._header.index()

header = Header(header_rows)

class Scene:
	#name, ordered list of shots, entities

	def __init__(self, name):
		self.name = name
		self.shots = []

	def __getattribute__(self, name):

		if name is 'shot' and not self.shots:
			print('no shot')
			return -1
		else:
			return object.__getattribute__(self, name)

	def addShot(self, shot):
		self.shots.append(shot)

scenes = defaultdict(Scene)

class Shot:

	def __init__(self, *args, **kwargs):
		self.__dict__.update({key: value for key, value in kwargs})
		self.actions = []

	def addArg(self, action, arg):
		self[action].add(arg)

	def update(self, row_values):
		#thus far, only update is to add argument to action
		arg = row_values[header['Arguments']]
		self.addArg(self.actions[-1], )

scene_names = {s.value for s in list(ws.columns)[0][1:]}

print('stop')
last_shot_num = 0
for i, row in enumerate(rows)
	row_values = [r.value for r in row]
	if len(row_values) != len(header):
		print("ALERT", i)
	elif row_values[header['shot number']] == last_shot_num:
		#same shot, then load argument
		last_shot = scenes[row[0].value].shots[-1]\
		last_shot.update(row_values)
	else:
		#new shot
		new_shot = Shot(dict(zip(header, row_values)))
		scenes[row[0].value].append(new_shot)
		last_shot_num +=1

print('stop')
#
# def readRows(self, rows):
# 	for row in rows:
