
def in_millis(datetime_item):
	return datetime_item.second*1000 + datetime_item.microsecond / 1000


if __name__ == '__main__':
	# load the scene lib
	import SceneDataStructs as SDS

	scene_lib = SDS.load()

	total_shots = 0
	total_ents = 0
	total_obs = 0
	total_shot_duration = 0
	total_scene_duration = 0

	with open('stats_output.txt', 'w') as sot:
		for name, scene in scene_lib.items():
			if name is None or name is 'None':
				continue
			sot.write(name + '\t')
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
			sot.write(str(scene_duration/1000) + '\t')
			sot.write(str(len(scene)) + '\t')
			sot.write(str(num_actions) + '\t')
			sot.write(str(len(scene.entities)))
			sot.write('\n')

	print('\n')
	print('avg entities: {}'.format(total_ents / 30))
	print('avg obs: {}'.format(total_obs / 30))
	print('avg shots: {}'.format(total_shots / 30))
	print('avg shot duration: {}'.format(total_shot_duration/total_shots))
	print('avg scene duration: {}'.format(total_scene_duration/30))

