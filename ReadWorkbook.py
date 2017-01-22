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
header = [r.value for r in rows[0]]
rows = [list(r) for r in rows[1:]]
scenes = defaultdict(list)

class Scene:
	#name, ordered list of shots, entities

	def __init__(self, name):
		self.name = name
		self.shots = []

	def addShot(self, shot):
		self.shots.append(shot)

class Shot:

	def __init__(self, *args, **kwargs):
		self.__dict__.update({key: value for key, value in kwargs})

	def addArg(self, action, arg):
		self[action].add(arg)

scene_names = {s.value for s in list(ws.columns)[0][1:]}

print('stop')
for i, row in enumerate(rows):
	row_values = [r.value for r in row]
	if len(row_values) != len(header):
		print("ALERT", i)
	else:
		scenes[row[0].value].append(dict(zip(header, row_values)))

print('stop')
#
# def readRows(self, rows):
# 	for row in rows:
