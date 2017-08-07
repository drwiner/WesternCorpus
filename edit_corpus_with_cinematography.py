# from openpyxl import load_workbook
# import pickle
# from clockdeco import clock
# from copy import deepcopy
# from collections import defaultdict


from SceneDataStructs import *

def parse(fn):
	wb = load_workbook(filename=fn, data_only=True)
	# for each sheet, get the rows
	for ws in wb.worksheets:

		# ws = wb.worksheets[0]
		rows = list(ws.rows)
		header_rows = [clean(r.value) for r in rows[0]]
		header = Header(header_rows)
		Shot.header = header
		rows = [list(r) for r in rows[1:]]
		action_start, action_stop = header.fromTo('actionnumber', "conclusionstatus")

	# Scene Lib
	# global scene_lib
	scene_names = {clean(s.value) for s in list(ws.columns)[0][1:]}


	print('starting parsing')

	last_shot_num = 0
	last_action_num = 0
	for row in rows:

		row_values = [clean(r.value) for r in row]
		scene_name = row_values[0]

		action_params = dict(zip(header.namesFromTo(action_start, action_stop), row_values[action_start:action_stop]))

		if len(row_values) != len(header):
			print("ALERT, |row_values| != |header|")

		elif toNumber(row_values[header['shotnumber']]) == last_shot_num:

			# same shot,
			last_shot = scene_lib[row_values[0]][-1]

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
			shot_desc = row[header['eventdescription']].value
			new_shot = Shot(first_action, shot_desc, **dict(zip(header.names, row_values)))
			scene_lib[scene_name].append(new_shot)

			if toNumber(row_values[header['shotnumber']]) == 1 and not last_shot_num == 0:
				#new scene, reset counter
				last_shot_num = 1
			else:
				last_shot_num += 1

			last_action_num = 1


	return scene_lib

if __name__ == '__main__':
	filename = 'cinematicscoding2.xlsx'
	parse(filename)