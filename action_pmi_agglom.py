from spectral_clustering import get_cluster


class Event:
	def __init__(self, sc_name, shot_num, action_num, action_type, arg_name):
		self.sc_name = sc_name
		self.shot_num = shot_num
		self.action_num = action_num
		self.action_type = action_type
		self.arg_name = arg_name


def collect_events(scene_lib):
	events = []
	for sc_name, scene in scene_lib.items():
		if sc_name in SDS.EXCLUDE_SCENES:
			continue

		for j, shot in enumerate(scene):
			for k, action in enumerate(shot.actions):
				if action._type is None or str(action._type).lower() == 'none':
					continue

				action_pred = pd[str(action._type)]
				m = action_pred._num_args

				for i, arg in enumerate(action):
					if i + 1 >= m:
						break
					if arg is None or str(arg).lower() == 'none' is None or arg.name.lower() == 'none':
						continue
					events.append(Event(sc_name, j, k, str(action._type), arg.name))
	return events


def pmi():
	pass

if __name__ == '__main__':
	import SceneDataStructs as SDS
	scene_lib = SDS.load()
	events = collect_events(scene_lib)