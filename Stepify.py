from pocl.pddlToGraphs import parseDomAndProb
from pocl.Element import Literal, Argument, Actor, Operator
from pocl.ElementGraph import Action
from pocl.OrderingGraph import OrderingGraph, CausalLinkGraph
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

def make_step(ai, cop, scene_ent_dict):
	obs_args = tuple(scene_ent_dict[arg] for arg in ai._args)
	if len(obs_args) != len(cop.Args):
		if len(obs_args) > len(cop.Args):
			for i, arg in enumerate(cop.Args):
				cop.replaceArg(arg, scene_ent_dict[ai._args[i]])
		else:
			for i, arg in enumerate(ai._args):
				cop.replaceArg(cop.Args[i], scene_ent_dict[arg])

	else:
		cop.replaceArgs(obs_args)

def stepify(op_dict, scene, plot):
	scene_steps = []
	obs_to_step_dict = dict()

	scene_ent_dict = {ent.name+'_'+str(ent.role): Argument(name=ent.name, arg_name=ent.name) for ent in scene.entities}

	# for each action instance (each is an action obs),
	for ai in plot:
		# cehck if name is in operator names
		if ai._name not in op_dict.keys():
			if ai._name == 'none':
				continue
			print('{} not an operator name'.format(ai._name))
			continue
		cop = op_dict[ai._name].deepcopy(True)
		make_step(ai, cop, scene_ent_dict)
		scene_steps.append(cop)
		obs_to_step_dict[cop.ID] = ai

	return scene_steps, obs_to_step_dict


def order_steps(plan, obs_step_dict, ais):
	og = OrderingGraph()
	start_dict = {ai: ai.starts for ai in ais}
	end_dict = {ai: ai.finishes for ai in ais}

	for step in plan:
		ai_step = obs_step_dict[step.ID]
		og.elements.add(step)
		for ordered_step in list(og.elements):
			ai_ord = obs_step_dict[ordered_step.ID]
			if end_dict[ai_step] <= start_dict[ai_ord]:
				og.addOrdering(step, ordered_step)
			if end_dict[ai_ord] <= start_dict[ai_step]:
				og.addOrdering(ordered_step, step)


	return og


def link_steps(og):
	clg = CausalLinkGraph()
	for edge in og.edges:
		effs = edge.source.Effects
		pres = edge.sink.Preconditions
		for eff in effs:
			if None in eff.Args:
				continue
			for pre in pres:
				if None in pre.Args:
					continue
				if eff == pre:
					clg.addEdge(edge.source, edge.sink, eff)

	return clg


def scene_to_plan(op_dict, scene, ais):
	plan, ai_step_map = stepify(op_dict, scene, ais)
	# plan is a list of Steps
	og = order_steps(plan, ai_step_map, ais)
	# now, for each edge in og, see if there is a causal link.
	clg = link_steps(og)
	return plan, og, clg

import copy
def topoSort(ordering_graph):
	L =[]
	# ogr = copy.deepcopy(ordering_graph)
	ogr = OrderingGraph()
	init_dummy = Action(name='init_dummy')
	ogr.elements.add(init_dummy)
	for elm in list(ordering_graph.elements):
		ogr.addOrdering(init_dummy, elm)
	S = {init_dummy}

	#L = list(graph.Steps)
	while len(S) > 0:
		n = S.pop()
		if n not in L:
			L.append(n)
		for m_edge in ogr.getIncidentEdges(n):
			ogr.edges.remove(m_edge)
			#if the sink has no other ordering sources, add it to the visited
			if len({edge for edge in ogr.getParents(m_edge.sink)}) == 0:
				S.add(m_edge.sink)
	return L


def plannify_scenes(scene_lib, domain='western.pddl', problem='generic_western_problem.pddl', scene_file='scene_lib_file'):
	operators, dops, objects, object_types, ia, ga = parseDomAndProb(domain, problem)
	op_dict = {op.name: op for op in operators}
	plot_ais_dict = induce_plots(scene_file)
	plans = []
	for sc_name, scene in scene_lib.items():
		if sc_name in SDS.EXCLUDE_SCENES:
			continue
		p, og, clg = scene_to_plan(op_dict, scene, plot_ais_dict[sc_name])
		# print(sc_name)
		steps_in_list = topoSort(og)
		plans.append((steps_in_list, og, clg))
	return plans


def plannify(scene_lib, domain='western.pddl', problem='generic_western_problem.pddl', scene_file='scene_lib_file'):
	operators, dops, objects, object_types, ia, ga = parseDomAndProb(domain, problem)
	op_dict = {op.name: op for op in operators}
	plot_ais_dict = induce_plots(scene_file)
	for sc_name, scene in scene_lib.items():
		if sc_name in SDS.EXCLUDE_SCENES:
			continue
		p, og, clg = scene_to_plan(op_dict, scene, plot_ais_dict[sc_name])
		print(sc_name)
		steps_in_list = topoSort(og)

		with open('scene_plans//' + sc_name + '.txt', 'w') as sps:
			sps.write('orderings:\n')
			for edge in og.edges:
				sps.write(str(edge.source) + ' < ' + str(edge.sink) + '\n')
			sps.write('\n')
			sps.write('potential causal-links:\n')
			for edge in clg.edges:
				sps.write(str(edge) + '\n')
			sps.write('\n')
			for i, step in enumerate(steps_in_list):
				# skip
				if i == 0:
					continue
				sps.write('{}\t{}\n'.format(str(i), str(step)))
	print('here')


if __name__ == '__main__':
	plannify(SDS.load())

	# now, we would somehow check if our scene_plans_dict has any merit.
	# put in topological order and output to scene files