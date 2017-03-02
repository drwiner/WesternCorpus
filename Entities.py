from ReadWorkbook import SceneLib, Scene, Action, Shot
import pickle

EXCLUDE_SCENES = ['tg']

def load(d='scenelib.pkl'):
	return pickle.load(open(d, 'rb'))


print('loading scene library')
scene_lib = load()
print(scene_lib)

entity_path = 'entity_folder/'

# a class for an entity object
class Entity:
	def __init__(self, entity_name, types=None, role=None):
		self.name = entity_name
		self.types =types
		self.role = role

	def __hash__(self):
		return hash(str(self.name) + str(self.role))

	def __str__(self):
		return str(self.name) + ' ' + str(self.role)

	def __repr__(self):
		return str(self.name) + ' ' + str(self.role)

def generateEntities():
	print('writing entities:')
	for sc_name, scene in scene_lib.items():
		if sc_name is None:
			continue
		print(sc_name)
		scene_entity_file = open(entity_path + 'scene' + sc_name + '_entities.txt', 'w')
		for entity in scene.entities:
			scene_entity_file.write(entity)
			scene_entity_file.write('\n')

def readEntityRoles(scene_file):
	role_dict = dict()
	subs = False
	for line in scene_file:
		split_line = line.split()
		if not subs:
			if len(split_line) > 1:
				role_dict[split_line[0]] = Entity(split_line[0], roles=split_line[-1])
			else:
				role_dict[split_line[0]] = Entity(split_line[0])
			if split_line[-1] != '_':
				subs = True
				continue
		if subs:
			role_dict[split_line[0]] = set(split_line[2:])
	return role_dict


def assignRoles():
	print('assigning entities to roles')
	for sc_name, scene in scene_lib.items():
		if sc_name is None or sc_name in EXCLUDE_SCENES:
			continue
		print(sc_name)
		scene_entity_file = open(entity_path + 'scene' + sc_name + '_entities.txt')
		rd = readEntityRoles(scene_entity_file)
		scene.substituteEntities(rd)

if __name__ == '__main__':
	assignRoles()
