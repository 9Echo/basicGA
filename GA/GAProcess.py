#----------------------------------------------------------
# Simple Genetic Algorithm
#----------------------------------------------------------
import numpy as np
import copy


class GA():
	'''Simple Genetic Algorithm'''
	def __init__(self, population, selection, crossover, mutation, fun_fitness=lambda x:np.arctan(-x)+np.pi):
		'''
		fun_fitness: fitness based on objective values. minimize the objective by default
		'''		
		# check compatibility between Individual and GA operators
		if not crossover.individual_class or not population.individual.__class__ in crossover.individual_class:
			raise ValueError('incompatible Individual class and Crossover operator')  
		if not mutation.individual_class or not population.individual.__class__ in mutation.individual_class:
			raise ValueError('incompatible Individual class and Mutation operator')

		self.population = population
		self.selection = selection
		self.crossover = crossover
		self.mutation = mutation
		self.fun_fitness = fun_fitness

	def run(self, fun_evaluation, gen=50, elitism=True):
		'''
		solve the problem based on Simple GA process
		two improved methods could be considered:
			a) elitism mechanism: keep the best individual, i.e. skip the selection, crossover, mutation operations
			b) adaptive mechenism: adaptive crossover rate, adaptive mutation megnitude. 
		'''

		# initialize population
		self.population.initialize()

		# solving process
		for n in range(1, gen+1):

			# the best individual in previous generation
			# attention: the population was evaluated when calculating the best individual
			# 			 otherwise, evaluate the population explicitly
			if elitism:
				the_best = copy.deepcopy(self.population.best(fun_evaluation, self.fun_fitness))
			else:
				self.population.evaluate(fun_evaluation, self.fun_fitness)

			# selection
			self.selection.select(self.population)

			# crossover
			self.crossover.cross(self.population)

			# mutation
			rate = 1.0 - np.random.rand()**((1.0-n/gen)**3)
			self.mutation.mutate(self.population, rate)

			# elitism mechanism: 
			# set a random individual as the best in previous generation
			if elitism:
				pos = np.random.randint(self.population.size)
				self.population.individuals[pos] = the_best

		# return the best individual
		return self.population.best(fun_evaluation, self.fun_fitness)