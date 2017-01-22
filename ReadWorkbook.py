## Read western duel corpus workbook
# Read headers
# skip blank rows
# save and load data with pickle

from openpyxl import load_workbook

wb = load_workbook(filename='Western_duel_corpus.xlsx')
#first worksheet
ws = wb.worksheets[0]
rows = list(ws.rows)
header = [r.value for r in rows[0]]

class Scene:
	#name, ordered list of shots, entities
	def __init__(self, name):
		self.name = name

class Shot:
	def __init__(self, *args, **kwargs):
		self.params = {key: value for key, value in kwargs}

	def addArg(self, action, arg):
		self.params[action].add(arg)