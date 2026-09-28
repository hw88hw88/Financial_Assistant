import strategy
import numpy as np

class Population:
    '''
    # I added the default value to input arguments
    # input:
    ## 1. pop size
    ## 2. gene count
    def __init__(self, pop_size=10, gene_count=3):
        self.creatures = [creature.Creature(
                          gene_count=gene_count) 
                          for i in range(pop_size)]
    
    Title: CM3020 Artificial Intelligence, Week 10 Mid-term coursework
    Author: The author of this project (Anonoymous submission of assignment)
    Date: 2026
    Code version: N/A
    Availability: Submitted Assignment (Not published)
    (Week 10 Mid-term coursework of CM3020 Artificial Intelligence, 2026)

    The code in this function was adapted from the mid-term coursework in the week 10 of "CM3020 Artificial Intelligence" by the author of this project
    All the code was written and prepared by the author of this project.
    
    The code of the mid-term coursework was written with reference to the starter code from the mid-term coursework of "CM3020 Artificial Intelligence" (Yee-King, no date)

    Reference:
    Yee-King, M., (no date) CM3020 Artificial Intelligence, Week 10 Mid-term coursework starter code [online] Available from: https://www.coursera.org/learn/uol-cm3020-artificial-intelligence/assignment-submission/6JASg/mid-term-coursework [8 December 2025]
    '''
    # input:
    # 1. start_up_cash: start up capital
    # 2. pop size: population size
    # 3. st: strategy instance (optional)
    def __init__(
            self, 
            start_up_cash, 
            pop_size=10, 
            st=None
        ):
        if st is not None:
            self.strategies = [strategy.Strategy(start_up_cash) for i in range(pop_size - 1)]
            self.strategies.append(st)
        else:
            self.strategies = [strategy.Strategy(start_up_cash) for i in range(pop_size)]

    '''
    # generate fitmap and return it
    # input: 
    ## 1. a list of rewards
    # output: 
    ## 1. a fitmap
    @staticmethod
    def get_fitness_map(reward):
        # I changed the variable name. It stores the fitmap
        fitmap = []
        # a list to store the value of each fit
        fits = [r for r in reward]
        
        total = 0
        for f in fits:
            if f is not None:
                total += f
            fitmap.append(total)
        return fitmap

    Title: CM3020 Artificial Intelligence, Week 10 Mid-term coursework
    Author: The author of this project (Anonoymous submission of assignment)
    Date: 2026
    Code version: N/A
    Availability: Submitted Assignment (Not published)
    (Week 10 Mid-term coursework of CM3020 Artificial Intelligence, 2026)

    The code in this function was adapted from the mid-term coursework in the week 10 of "CM3020 Artificial Intelligence" by the author of this project
    All the code was written and prepared by the author of this project.
    
    The code of the mid-term coursework was written with reference to the starter code from the mid-term coursework of "CM3020 Artificial Intelligence" (Yee-King, no date)

    Reference:
    Yee-King, M., (no date) CM3020 Artificial Intelligence, Week 10 Mid-term coursework starter code [online] Available from: https://www.coursera.org/learn/uol-cm3020-artificial-intelligence/assignment-submission/6JASg/mid-term-coursework [8 December 2025]
    '''

    # generate fitmap and return it
    # input: 
    ## 1. a list of rewards
    # output: 
    ## 1. a fitmap
    @staticmethod
    def get_fitness_map(reward):
        fitmap = []
        # a list to store the value of each fit
        fits = [r for r in reward]
        
        total = 0
        for f in fits:
            if f is not None:
                total += f
            fitmap.append(total)
        return fitmap

    '''
    # implement selection of creatures for breeding according to fitmap
        # input: 
        ## 1. fitmap
        # output:
        ## 1. the selected value in the fitmap
        @staticmethod
        def select_parent(fitmap):
            # I changed the variable names and added more explanation
            # genereate random float in the range [0, 1), 0 is inclusive, 1 is excluded.
            # Reference: https://numpy.org/doc/stable/reference/random/generated/numpy.random.rand.html
            picked_num = np.random.rand() # [0,1)
            picked_num = picked_num * fitmap[-1]
            for f in range(len(fitmap)):
                # the condition is <, instead of <=, because any zero in fitmap should not be selected.
                # For example, if the fitmap = [0, 0, 1], and the random number is 0, 0 <= 0 will be true, and the first zero in fitmap will be selected, and this is not correct. The next element higher than 0 should be selected instead. 
                # The creatures with 0 fitness should not have any chance to breed, but the 1 should have a chance to breed.
                if picked_num < fitmap[f]:
                    return f
            # in very rare cases, if no parent can be selected
            # return 0 instead of nothing to avoid error(s)
            return 0

    Title: CM3020 Artificial Intelligence, Week 10 Mid-term coursework
    Author: The author of this project (Anonoymous submission of assignment)
    Date: 2026
    Code version: N/A
    Availability: Submitted Assignment (Not published)
    (Week 10 Mid-term coursework of CM3020 Artificial Intelligence, 2026)

    The code in this function was adapted from the mid-term coursework in the week 10 of "CM3020 Artificial Intelligence" by the author of this project
    All the code was written and prepared by the author of this project.
    
    The code of the mid-term coursework was written with reference to the starter code from the mid-term coursework of "CM3020 Artificial Intelligence" (Yee-King, no date)

    Reference:
    Yee-King, M., (no date) CM3020 Artificial Intelligence, Week 10 Mid-term coursework starter code [online] Available from: https://www.coursera.org/learn/uol-cm3020-artificial-intelligence/assignment-submission/6JASg/mid-term-coursework [8 December 2025]
    '''

    # implement selection of strategies for breeding according to fitmap
    # input: 
    ## 1. fitmap
    # output:
    ## 1. the selected value in the fitmap
    @staticmethod
    def select_parent(fitmap):
        # genereate random float in the range [0, 1), 0 is inclusive, 1 is excluded.
        # Reference: https://numpy.org/doc/stable/reference/random/generated/numpy.random.rand.html
        picked_num = np.random.rand() # [0,1)
        picked_num = picked_num * fitmap[-1]
        for f in range(len(fitmap)):
            # the condition is <, instead of <=, because any zero in fitmap should not be selected.
            # For example, if the fitmap = [0, 0, 1], and the random number is 0, 0 <= 0 will be true, and the first zero in fitmap will be selected, but this is incorrect. The next element higher than 0 should be selected instead. 
            # The creatures with 0 fitness should not have any chance to breed.
            if picked_num < fitmap[f]:
                return f
        # in very rare cases, if no parent can be selected
        # return 0 instead of nothing to avoid error(s)
        return 0
