#from pddlToGraphs import *
import collections
import bisect
from uuid import uuid1, uuid4
from pocl.Graph import isConsistentEdgeSet

import itertools
from clockdeco import clock
#from PlanElementGraph import Condition
#import PlanElementGraph
"""
	Flaws for plan element graphs
"""

class Flaw:
	def __init__(self, f, name):
		self.name = name
		self.flaw = f
		self.cndts = 0
		self.risks = 0
		self.criteria = self.cndts
		self.heuristic = float('inf')
		if name == 'opf':
			self.tiebreaker = f[1].litnumber

	def __hash__(self):
		return hash(self.flaw)
		
	def __eq__(self, other):
		return hash(self) == hash(other)

	#For comparison via bisect
	def __lt__(self, other):
		if self.criteria != other.criteria:
			return self.criteria < other.criteria
		else:
			return self.tiebreaker < other.tiebreaker


	def setCriteria(self, flaw_type):
		#if flaw_type == 'statics':
			#self.heuristic = 0
			#self.criteria = 0
		if flaw_type == 'threats':
			self.heuristic = 0.01
		if self.name == 'tclf':
			self.criteria = self.flaw[0].stepnumber
			self.tiebreaker = self.flaw[1].label.litnumber + self.flaw[1].sink.stepnumber*100
		elif flaw_type == 'unsafe':
			#self.criteria = self.risks
			self.criteria = self.heuristic
		elif flaw_type == 'reusable':
			self.criteria = self.heuristic
		elif flaw_type in {'inits', 'nonreusable'}:
			self.criteria = self.heuristic

	def calcHeuristic(self, GL, plan):
		s_need, pre = self.flaw
		antecedents = GL.cndt_dict[pre.litnumber]

		if (pre.name, pre.truth) not in FlawLib.non_static_preds:
			if plan.initial_dummy_step.stepnumber not in antecedents:
				self.heuristic = float('inf')
				return self.heuristic

		reusable_steps = [step.stepnumber for step in plan if step.root != s_need
						  and not plan.OrderingGraph.isPath(s_need, step.root)]

		for rs in reusable_steps:
			if rs in antecedents:
				self.heuristic = s_need.height * 30
				return self.heuristic

		c = self.h_add_q(GL, pre, collections.defaultdict(int))
		self.heuristic = c + s_need.height * 30
		return self.heuristic

	def h_add_q(self, GL, pre, visited):
		#additive heuristic with modification for reuse (VHPOP)

		antecedents = GL.cndt_dict[pre.litnumber]
		least = float('inf')

		#infinity otherwise
		if len(antecedents) == 0:
			#lisited[pre.litnumber] = least
			return least

		for ante in antecedents:
			# Shortcut - if one of your antecedents has no preconditions
			if len(GL[ante].Preconditions) == 0:
				visited[ante] = 1
				return 1

			if ante in visited:
				if visited[ante] < least:
					least = visited[ante]
			else:
				#in case it cycles...
				visited[ante] = float('inf')
				if len(GL.ante_dict[ante]) == 0:
					continue
				v = self.h_add_a(GL, GL[ante], visited)
				if v == float('inf'):
					pass
				visited[ante] = v
				if v == 0:
					return 0
				if v < least:
					least = v
		if least == float('inf'):
			pass
		return least

	def h_add_a(self, GL, step, visited):
		#cost of an action 'a' is 1 + h_{add}(Prec(a)) where Prec(a) is the conjunction of preconditions
		cost = 1
		for pre in step.Preconditions:
			#if pre.litnumber in visited:
				#v = lisited[pre.litnumber]
		#	else:
				#lisited[pre.litnumber] = float('inf')
			if len(GL.cndt_dict[pre.litnumber]) == 0:
				return float('inf')

			v = self.h_add_q(GL, pre, visited)
			if v == float('inf'):
				pass
				#lisited[pre.litnumber] = v

			if v == float('inf'):
				return v

			cost += v
		return cost

	def __repr__(self):
		return 'Flaw({}, h={}, criteria={}, tb={})'.format(self.flaw, self.heuristic, self.criteria, self.tiebreaker)

class TCLF(Flaw):
	def __init__(self, f, name):
		super(TCLF, self).__init__(f, name)
		self.threat = self.flaw[0]
		self.link = self.flaw[1]
		self.criteria = self.threat.stepnumber
		self.tiebreaker = self.link.label.litnumber + self.link.sink.stepnumber

	def __hash__(self):
	 	return self.threat.stepnumber*1000 + self.link.source.stepnumber + self.link.sink.stepnumber + \
			   self.link.label.litnumber

class DCF(Flaw):
	def __init__(self, f, name):
		super(DCF, self).__init__(f, name)
		self.criteria = len(f.Steps)
		self.tiebreaker = f.root.stepnumber
	def __repr__(self):
		steps = [''.join(str(step) + ', ' for step in self.flaw)]
		return 'DCF(' + ''.join(['{}'.format(step) for step in steps]) + 'criteria ={}, tb={})'.format(
			self.criteria, self.tiebreaker)

class Flawque:
	""" A deque which pretends to be a set, and keeps everything sorted, highest-value first"""

	def __init__(self, name=None):
		self._flaws = collections.deque()
		self.name = name

	def add(self, flaw):
		flaw.setCriteria(self.name)
		self.insert(flaw)
		#self._flaws.append(item)

	def update(self, iter):
		for flaw in iter:
			self.add(flaw)

	def __contains__(self, item):
		return item in self._flaws

	def __len__(self):
		return len(self._flaws)

	def removeDuplicates(self):
		self._flaws = collections.deque(set(self._flaws))

	def head(self):
		return self._flaws.popleft()

	def tail(self):
		return self._flaws.pop()

	def pop(self):
		return self._flaws.pop()

	def peek(self):
		return self._flaws[-1]

	def insert(self, flaw):
		index = bisect.bisect_left(self._flaws, flaw)
		self._flaws.rotate(-index)
		self._flaws.appendleft(flaw)
		self._flaws.rotate(index)

	def __getitem__(self, position):
		return self._flaws[position]

	def __repr__(self):
		return str(self._flaws)

class simpleQueueWrapper(collections.deque):
	#def __init__(self, name):
		#super(simpleQueueWrapper, self).__init__()
		#self.name = name
	def add(self, item):
		self.append(item)
	def pop(self):
		return self.popleft()
	def update(self, iter):
		for it in iter:
			self.append(it)

class FlawLib():
	non_static_preds = set()

	def __init__(self):

		#static = unchangeable (should do oldest first.)
		self.statics = Flawque('statics')

		#init = established by initial state
		self.inits = Flawque('inits')

		#decomps - decompositional ground subplans to add
		self.decomps = Flawque('decomps')

		#threat = causal link dependency undone
		self.threats = Flawque('threats')

		#unsafe = existing effect would undo sorted by number of cndts
		self.unsafe = Flawque('unsafe')

		#reusable = open conditions consistent with at least one existing effect sorted by number of cndts
		self.reusable = Flawque('reusable')

		#nonreusable = open conditions inconsistent with existing effect sorted by number of cndts
		self.nonreusable = Flawque('nonreusable')

		self.typs = [self.statics, self.inits, self.threats, self.decomps, self.unsafe, self.reusable, self.nonreusable]
		self.restricted_names = ['threats', 'decomps']

	# @property
	# def heuristic(self):
	# 	value = 0
	# 	for i, flawques in enumerate(self.typs):
	# 		if flawques.name in self.restricted_names:
	# 			continue
	# 		value += i*len(flawques)
	# 	return value

	def __len__(self):
		return sum(len(flaw_set) for flaw_set in self.typs)
	#	return len(self.threats) + len(self.unsafe) + len(self.statics) + len(self.reusable) + len(self.nonreusable)

	def __contains__(self, flaw):
		for flaw_set in self.typs:
			if flaw in flaw_set:
				return True
		return False

	@property
	def flaws(self):
		return [flaw for i, flaw_set in enumerate(self.typs) for flaw in flaw_set if flaw_set.name not in
				self.restricted_names]

	def OCs(self):
		''' Generator for open conditions'''
		for i, flaw_set in enumerate(self.typs):
			if len(flaw_set) == 0:
				continue
			if flaw_set.name in self.restricted_names:
				continue
			g = (flaw for flaw in flaw_set)
			yield(next(g))

	def next(self):
		''' Returns flaw with highest priority, and removes'''
		for flaw_set in self.typs:
			if len(flaw_set) > 0:
				return flaw_set.pop()
		return None

	#@clock
	def addCndtsAndRisks(self, GL, action):
		""" For each effect of Action, add to open-condition mapping if consistent"""

		for oc in self.OCs():
			s_need, pre = oc.flaw

			# step numbers of antecdent types
			if action.stepnumber in GL.cndt_dict[pre.litnumber]:
				oc.cndts += 1

			# step numbers of threatening steps
			elif action.stepnumber in GL.threat_dict[pre.litnumber]:
				oc.risks += 1

	#@clock
	def insert(self, GL, plan, flaw):
		''' for each effect of an existing step, check and update mapping to consistent effects'''

		if flaw.name == 'tclf':
			#if flaw not in self.threats:
			self.threats.add(flaw)
			return

		if flaw.name == 'dcf':
			self.decomps.add(flaw)
			return

		#unpack flaw
		flaw.calcHeuristic(GL, plan)
		s_need, pre = flaw.flaw

		#if pre.predicate is static
		if (pre.name, pre.truth) not in FlawLib.non_static_preds:
			self.statics.add(flaw)
			return

		#Eval number of existing candidates
		ante_nums = GL.cndt_dict[pre.litnumber]
		risk_nums = GL.threat_dict[pre.litnumber]

		for step in plan.Steps:
			#defense
			if step == s_need:
				continue
			if plan.OrderingGraph.isPath(s_need, step):
				continue
			if step.stepnumber in ante_nums:
				flaw.cndts += 1
				if step.name == 'dummy_init':
					self.inits.add(flaw)
			if step.stepnumber in risk_nums:
				flaw.risks += 1

		if flaw in self.inits:
			return

		if flaw.risks > 0:
			self.unsafe.add(flaw)
			return

		#if not static but has cndts, then reusable
		if flaw.cndts > 0:
			self.reusable.add(flaw)
			return

		#last, must be nonreusable
		if flaw.heuristic == float('inf'):
			pass
		self.nonreusable.add(flaw)

	def __repr__(self):
		#flaw_str_list = [str([flaw for flaw in flaw_set]) for flaw_set in self.typs]
		F = [('|' + ''.join([str(flaw) + '\n|' for flaw in T]) , T.name) for T in self.typs if len(T) > 0]
		#flaw_lib_string = str(['\n {}: \n {} '.format(flaws, name) + '\n' for flaws, name in F])
		return '______________________\n|FLAWLIBRARY: \n|' + ''.join(['\n|{}: \n{}'.format(name, flaws) for
																		  flaws, name in F]) + '______________________'

import unittest
class TestOrderingGraphMethods(unittest.TestCase):

	def test_flaw_counter(self):
		assert True


if __name__ ==  '__main__':
	unittest.main()