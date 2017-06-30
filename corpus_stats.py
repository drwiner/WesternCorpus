
def in_millis(datetime_item):
	return datetime_item.second*1000 + datetime_item.microsecond / 1000


total_shots = 0
total_ents = 0
total_obs = 0
total_shot_duration = 0
total_scene_duration = 0

for name, scene in scene_lib.items():
	if name is None or name is 'None':
		continue
	print(name)
	print('num shots: {}'.format(len(scene)))
	num_actions = 0
	# scene_duration = in_millis(scene[-1].shotend)
	scene_duration = 0
	for shot in scene:
		scene_duration += in_millis(shot.shotlength)
		num_actions += len(shot.actions)
	print('num actions: {}'.format(num_actions))
	print(len(scene.entities))
	total_ents += len(scene.entities)
	total_obs += num_actions
	total_shots += len(scene)
	total_shot_duration += scene_duration
	print(scene_duration)
	total_scene_duration += scene_duration
	print('\n')

print('\n')
print('avg entities: {}'.format(total_ents / 30))
print('avg obs: {}'.format(total_obs / 30))
print('avg shots: {}'.format(total_shots / 30))
print('avg shot duration: {}'.format(total_shot_duration/total_shots))
print('avg scene duration: {}'.format(total_scene_duration/30))
