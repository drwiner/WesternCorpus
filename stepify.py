from pocl.pddlToGraphs import parseDomAndProb
from pocl.Element import Literal, Argument, Actor, Operator
from plot_induction import induce_plots, ActionObs
import SceneDataStructs as SDS
# from pocl.pddlToGraphs import parseDomAndProb

# for each scene, create problem file

# ALGORITHM
"""
	for each scene, create empty plan 'pi'
	for each entity in scene, make element and store.
	for each action-instance in plot_induction, Stepify(action-instance) (makes it a step in plan)
		keep dictionary of action-instances to steps
		add new-step to plan, and for each existing step in plan, determine if ordering between step and new-step
		for each existing step in plan, determine if causal link possible, add ALL possible causal links, no flaws
"""


# Operators, DOperators, objects, GC.object_types, init, goal
# print('check these out')


def stepify(op_dict, scene_lib):
	plot_dict = induce_plots('scene_lib_file')
	# plot_dict = {scene_name: action_instances}

	for sc_name, scene in scene_lib.items():
		plot = plot_dict[sc_name]
		scene_ent_dict = {ent.name: Argument(name=ent.name, arg_name=ent.name) for ent in scene.entities}
		# for each action instance (each is an action obs),
		for ai in plot:
			# cehck if name is in operator names
			if ai._name not in op_dict.keys():
				print('{} not an operator name'.format(ai._name))
				continue
			cop = op_dict[ai._name].deepcopy()
			obs_args = tuple(scene_ent_dict[arg.name] for arg in ai._args)
			if len(obs_args) != len(cop.Args):
				if len(obs_args) > len(cop.Args):
					for i, arg in enumerate(cop.Args):
						cop.replace(arg, ai._args[i])
				else:
					for i, arg in enumerate(ai._args):
						cop.replaceArg(cop.Args[i], arg)

			else:
				obs_args = tuple(scene_ent_dict[arg.name] for arg in ai._args)
				cop.replaceArgs(obs_args)



if __name__ == '__main__':
	operators, dops, objects, object_types, ia, ga = parseDomAndProb('western.pddl', 'generic_western_problem.pddl')
	op_dict = {op.name:op for op in operators}
	scene_lib = SDS.load()
	stepify(op_dict, scene_lib)


		# need list of action_instances

"""
FlawLib.non_static_preds = preprocessDomain(operators)
	obtypes = obTypesDict(object_types)

	Argument.object_types = obtypes
	planner = PlanSpacePlanner(operators, objects, initAction, goalAction)
	#planner.story_GL = GLib(operators, story_objs, obtypes, initAction, goalAction)

	results = planner.POCL(1)

	for result in results:
		totOrdering = topoSort(result)
		print('\n\n\n')
		for step in topoSort(result):
			print(Action.subgraph(result, step))
			"""