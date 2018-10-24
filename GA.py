import numpy as np
import math

class Individual():
	'''individual of population'''
	def __init__(self, dim, lbound, ubound):
		'''dimension of individual'''
		self._dim = dim
		self._lbound = lbound
		self._ubound = ubound
		self._chrom = np.empty((dim,))

	def initialize(self):
		'''initialize random values in [lbound, ubound]'''
		seeds = np.random.random(self._dim)		
		self._chrom = self.lbound + (self.ubound-self.lbound)*seeds

	@property
	def dimension(self):
		return self._dim

	@property
	def lbound(self):
		return self._lbound

	@property
	def ubound(self):
		return self._ubound

	@property
	def chrom(self):
		return self._chrom

	@chrom.setter
	def chrom(self, chrom):
		assert self.dimension == chrom.shape[0]
		assert (chrom>=self._lbound).all() and (chrom<=self._ubound).all()
		self._chrom = chrom	

	def mutate(self, positions, alpha):
		'''
		positions: mutating gene positions, list
		alpha: mutatation magnitude
		'''
		for pos in positions:
			if np.random.rand() < 0.5:
				self._chrom[pos] -= (self._chrom[pos]-self._lbound[pos])*alpha
			else:
				self._chrom[pos] += (self._ubound[pos]-self._chrom[pos])*alpha
	

class Population():
	'''collection of individuals'''
	def __init__(self, fun_evaluation, size=50):
		self._fun_evaluation = fun_evaluation
		self._size = size
		self._individuals = None
		self._evaluation = None

	def initialize(self, dim, lbound, ubound):
		'''initialization for next generation'''
		self._individuals = [Individual(dim, lbound, ubound) for i in range(self._size)]
		for individual in self._individuals:
			individual.initialize()	

	@property
	def individuals(self):
		return self._individuals	

	@property
	def evaluation(self):
		if self._evaluation is None:
			self._evaluation = np.array([self._fun_evaluation(I.chrom) for I in self._individuals])
		return self._evaluation

	@property
	def fitness(self):
		'''
		we're trying to minimize the evaluation value,
		so the fitness is defined as: sum(abs(V))-Vi
		'''
		fitness = np.sum(np.abs(self.evaluation)) - self.evaluation
		return fitness/np.sum(fitness)

	@property
	def best(self):
		pos = np.argmin(self.evaluation)
		return self._individuals[pos], self.evaluation[pos]

	def convergent(self, tol=1e-6):
		'''max deviation of all individuals'''
		max_eval, min_eval = np.max(self.evaluation), np.min(self.evaluation)
		return max_eval-min_eval <= tol
	

	@staticmethod
	def cross_individuals(individual_a, individual_b, alpha=0.5):
		'''
		generate two child individuals based on parent individuals:
		new values are calculated at random positions
		alpha: linear ratio to cross two parent valus
		'''
		# random positions to be crossed
		pos = np.random.rand(individual_a.dimension) <= 0.5

		# cross value
		new_value_a = individual_a.chrom*pos*alpha + individual_b.chrom*pos*(1-alpha)
		new_value_b = individual_a.chrom*pos*(1-alpha) + individual_b.chrom*pos*alpha

		# return new individuals
		new_individual_a = Individual(individual_a.dimension, individual_a.lbound, individual_a.ubound)
		new_individual_b = Individual(individual_b.dimension, individual_b.lbound, individual_b.ubound)

		new_individual_a.chrom = new_value_a
		new_individual_b.chrom = new_value_b

		return new_individual_a, new_individual_b

	def select(self):
		'''select individuals by Roulette'''
		probabilities = np.cumsum(self.fitness)
		selected_individuals = [self._individuals[np.sum(np.random.rand()>=probabilities)] for i in range(self._size)]
		self._individuals = selected_individuals
		self._evaluation = None # reset evaluation

	def crossover(self, rate, alpha):
		'''crossover operation'''
		new_individuals = []		
		random_population = np.random.permutation(self._individuals) # random order
		for individual_a, individual_b in zip(self._individuals, random_population):
			if np.random.rand() <= rate:
				child_individuals = self.cross_individuals(individual_a, individual_b, alpha)
				new_individuals.extend(child_individuals)
			else:
				new_individuals.append(individual_a)
				new_individuals.append(individual_b)

		self._individuals = np.random.choice(new_individuals, self._size, replace=False).tolist()
		self._evaluation = None # reset evaluation

	def mutate(self, num, rate, alpha):
		'''
		mutation operation:
		num: count of mutating gene
		rate: propability of mutation
		alpha: mutating magnitude
		'''
		self._evaluation = None # reset evaluation
		for individual in self._individuals:
			if np.random.rand() <= rate:
				pos = np.random.choice(individual.dimension, num, replace=False)
				individual.mutate(pos, alpha)


class GA():
	'''collection of individuals'''
	def __init__(self, fun_evaluation, dimention, **kw):
		'''
		dimention : dimension of individual
		fun_evaluation: evaluation function
		'''
		self._fun_evaluation = fun_evaluation

		# default parameters
		self._param = {
			'var_dim': dimention,
			'lbound': [-1e9] * dimention,
			'ubound': [1e9] * dimention,
			'size'	: 200,
			'max_generation': 10,
			'crossover_rate': 0.9,
			'mutation_rate'	: 0.08,
			'crossover_alpha': 0.75
		}
		self._param.update(kw)		

		# initialize population
		lbound = np.array(self._param['lbound'])
		ubound = np.array(self._param['ubound'])
		self._population = Population(fun_evaluation, self._param['size'])
		self._population.initialize(dimention, lbound, ubound)


	def solve(self):

		for current_gen in range(1, self._param['max_generation']+1):
			# GA operations
			rate = 1.0 - np.random.rand()**(1.0-current_gen/self._param['max_generation'])
			self._population.select()
			self._population.crossover(self._param['crossover_rate'], self._param['crossover_alpha'])
			self._population.mutate(np.random.randint(self._param['var_dim'])+1, self._param['mutation_rate'], rate)

			# evaluation
			# individual, val = self._population.best
			# print('----------Generation {0}----------'.format(current_gen))
			# print('Best individual: {0}'.format(individual.chrom))
			# print('Output: {0}'.format(val))

			if self._population.convergent():
				break

		# results
		individual, val = self._population.best
		print('Current generation: {0}'.format(current_gen))
		print('Best individual: {0}'.format(individual.chrom))
		print('Output: {0}'.format(val))

		return individual, val



if __name__ == '__main__':

	# schaffer function
	# sol: x=[0,0], min=0
	schaffer = lambda x: 0.5 + (math.sin((x[0]**2+x[1]**2)**0.5)**2-0.5) / (1.0+0.001*(x[0]**2+x[1]**2))**2

	kw = {
		'lbound': [-10, -10],
		'ubound': [10, 10],
		'size'	: 200,
		'max_generation': 20,
		'crossover_rate': 0.9,
		'mutation_rate'	: 0.1,
		'crossover_alpha': 0.25
	}
	g = GA(schaffer, 2, **kw)
	g.solve()
