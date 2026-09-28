# Although some of the code was adapted from my previous assignment, the code was still written following the three laws of test-driven development
import numpy as np
import random
import copy

class Genome:
    '''
    @staticmethod
    def get_random_gene(gene_length):
        # I simplified the code by eliminating the for-loop and the variable gene, and by calling numpy.random.rand()
        ## generate random number [0, 1), 0 is inclusive, but 1 is excluded
        ## Reference: https://numpy.org/doc/stable/reference/random/generated/numpy.random.rand.html
        return np.random.rand(gene_length)
    
    Title: CM3020 Artificial Intelligence, Week 10 Mid-term coursework
    Author: The author of this project (Anonoymous submission of assignment)
    Date: 2026
    Code version: N/A
    Availability: Submitted Assignment (Not published)
    (Week 10 Mid-term coursework of CM3020 Artificial Intelligence, 2026)

    The code in this function was adapted from the mid-term coursework in the week 10 of "CM3020 Artificial Intelligence" by the author of this project
    All the code was written and prepared by the author of this project.
    
    The code of the mid-term coursework was written with reference to the starter code of the mid-term coursework of "CM3020 Artificial Intelligence" (Yee-King, no date)
    '''
    # generate a random float
    # Input:
    # 1. gene_length: the length of gene list
    # Output: 
    ## 1. a list of random float [0, 1), 0 is inclusive, but 1 is excluded
    @staticmethod
    def get_random_gene(gene_length):
        ## generate random number [0, 1), 0 is inclusive, but 1 is excluded
        ## Reference: https://numpy.org/doc/stable/reference/random/generated/numpy.random.rand.html
        # return a random float from 0 to 1, 1 is excluded.
        return np.random.rand(gene_length)
    
    '''
    @staticmethod
        def get_gene_spec():
            gene_spec =  {
                # I added the lower and upper limit to the features below
                # I used lower and upper limit to control the features of creatures
                ## The "scale" attributes below were removed.
                ## <=0.33 cylinder; >0.33 and <=0.66 sphere; >0.66 box
                "link-shape":{"low_limit": 0, "up_limit": 1},
                # "link-length" and "link-radius" are for cylinder tag(s)
                # "link-radius" is for sphere tag(s)
                ## Default "link-length" is 2
                "link-length": {"low_limit": 0.1, "up_limit": 2},            
                ## Default "link-radius" is 1
                "link-radius": {"low_limit": 0.1, "up_limit": 1},
                # I added "link-width", "link-height", "link-depth" for box tag(s)
                "link-width": {"low_limit": 0.1, "up_limit": 2},
                "link-depth": {"low_limit": 0.1, "up_limit": 2},
                "link-height": {"low_limit": 0.1, "up_limit": 2},
                # Default "link-recurrence" is 3
                "link-recurrence": {"low_limit": 0, "up_limit": 2},
                "link-mass": {"low_limit": 0.1, "up_limit": 1},
                # I added the scale for "link-color"
                "link-color": {"low_limit": 0, "up_limit": 1},
                ## <=0.33 revolute; >0.33 and <=0.66 continous; >0.66 fixed
                ## Default: revolute
                "joint-type": {"low_limit": 0, "up_limit": 1},
                # The range of joint-parent must be 0-1, otherwise out-of-range
                "joint-parent":{"low_limit": 0, "up_limit": 1},
                ## <=0.33 100, >0.33 and <=0.66 010, >0.66 001
                "joint-axis-xyz": {"low_limit": 0, "up_limit": 1},
                # I added the following scales:
                # "joint-limit-lower"
                # "joint-limit-upper"
                # "joint-limit-effort"
                # "joint-limit-velocity"
                ## the unit(s) of "joint-limit-lower" and "joint-limit-upper" are in radian
                # Normally, the joint-limit-lower should be lower than joint-limit-upper to make them effective for revolute joints. Otherwise, the limit will lose its function
                "joint-limit-lower": {"low_limit": 0, "up_limit": np.pi * 2}, # in radian
                "joint-limit-upper": {"low_limit": np.pi * 4, "up_limit": np.pi * 10}, # in radian
                "joint-limit-effort": {"low_limit": 1, "up_limit": 10},
                "joint-limit-velocity": {"low_limit": 1, "up_limit": 10},
                "joint-origin-rpy-1":{"low_limit": 0, "up_limit": np.pi * 2},# in radian
                "joint-origin-rpy-2":{"low_limit": 0, "up_limit": np.pi * 2},# in radian
                "joint-origin-rpy-3":{"low_limit": 0, "up_limit": np.pi * 2},# in radian
                # Default of "joint-origin-xyz-1" is 0-1
                "joint-origin-xyz-1":{"low_limit": -1, "up_limit": 1},
                "joint-origin-xyz-2":{"low_limit": -1, "up_limit": 1},
                "joint-origin-xyz-3":{"low_limit": -1, "up_limit": 1},
                # I added joint-friction
                "joint-friction":{"low_limit": 1000.0, "up_limit": 5000.0},
                # <=0.33: PULSE; <=0.66: SINE; >0.66 RAMP
                "control-waveform":{"low_limit": 0, "up_limit": 1},
                "control-amp":{"low_limit": 0.25, "up_limit": 2},
                "control-freq":{"low_limit": 0.5, "up_limit": 2},
                "control-force":{"low_limit": 500, "up_limit": 10000},
                }
            ind = 0
            for key in gene_spec.keys():
                gene_spec[key]["ind"] = ind
                ind = ind + 1
            return gene_spec

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
    # generate a dict containing the range of parameters (the range of the parameters of financial indicators)
    # Input: None
    # output:
    ## 1. a dict specifying the range of the parameters
    @staticmethod
    def get_gene_spec():
        gene_spec={
            # financial indicators:

            ## simple moving average:
            ### the range of short window of simple moving average
            'ma_short':{'low_limit': 10, 'up_limit': 50},
            ### the range of long window of simple moving average
            'ma_long':{'low_limit': 80, 'up_limit': 250},
            ### the weight of simple moving average
            'ma_weight':{'low_limit': 1, 'up_limit': 9},

            ## RSI
            ### no. of days of RSI
            'rsi_period': {'low_limit': 7, 'up_limit':21},
            ### buy the shares at RSI below 'buy_rsi'
            'buy_rsi': {'low_limit': 10, 'up_limit':30},
            ### sell the shares at RSI above 'sell_rsi'
            'sell_rsi': {'low_limit': 70, 'up_limit':90},
            ### the weight of RSI
            'rsi_weight':{'low_limit': 1, 'up_limit': 9},

            # risk management rules:
            ## sell the shares when the loss is above 'stop_loss'
            'stop_loss': {'low_limit': -0.03, 'up_limit':-0.1},
            ## sell the shares when the profit is above 'take_profit'
            'take_profit': {'low_limit': 0.05, 'up_limit':2.0},

            # maximum no. of stocks in the investment portfolio
            'max_num_of_stock':{'low_limit': 1, 'up_limit': 5},

            # number of days to rebalance the portfolio to target portfolio
            'num_of_day_rebalance':{'low_limit': 20, 'up_limit':60},
            }
        return gene_spec
    
    '''
    @staticmethod
    def get_gene_dict(gene, spec):
        # initialize gdict
        gdict = {}
        for key in spec:
            ind = spec[key]["ind"]
            # I scaled the random gene in the range of lower and upper limit,
            # to generate gdict,
            # if spec[key]["up_limit"] < spec[key]["low_limit"], I will treat the upper limit as lower limit, and the lower limit as upper limit
            if spec[key]["up_limit"] >= spec[key]["low_limit"]:
                gene_range = spec[key]["up_limit"] - spec[key]["low_limit"]
                gdict[key] = gene[ind] * gene_range + spec[key]["low_limit"]
            else:
                # treating the upper limit as lower limit, and the lower limit as upper limit here
                gene_range = spec[key]["low_limit"] - spec[key]["up_limit"]            
                gdict[key] = gene[ind] * gene_range + spec[key]["up_limit"]
        return gdict

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

    # generate gdict{} (genes in the form of python dictionary) according to the spec
    # input: 
    ## 1. gene,
    ## 2. genome spec
    # output: 
    ## 1. gdict{}
    @staticmethod
    def get_gdict(gene, spec):
        # initialize gdict
        gdict = {}
        ind = 0
        for key in spec:
            # if spec[key]["up_limit"] < spec[key]["low_limit"], I will treat the upper limit as lower limit, and the lower limit as upper limit
            if spec[key]["up_limit"] >= spec[key]["low_limit"]:
                gene_range = abs(spec[key]["up_limit"] - spec[key]["low_limit"])
                gdict[key] = gene[ind] * gene_range + spec[key]["low_limit"]
            else:
                # treating the upper limit as lower limit, and the lower limit as upper limit here
                gene_range = abs(spec[key]["low_limit"] - spec[key]["up_limit"])
                gdict[key] = gene[ind] * gene_range + spec[key]["up_limit"]
            ind += 1
            if key != 'stop_loss' and key != 'take_profit':
                gdict[key] = int(np.round(gdict[key], 0))
            else:
                gdict[key] = float(gdict[key])
        return gdict

    '''
    # Single point crossover
    # I changed the logic of this function
    ## New genome was made from the first part of g1 and last part of g2 (instead of the last parts of both g1 and g2)
    # input: 
    ## 1. DNA of 2 creatures
    # output: 
    ## 1. a new dna made with g1 mixing with g2
    @staticmethod
    def crossover(g1, g2):
        # the index of the selected point should be lower than or equal to the shorter g1 and g2
        # This avoid the index out-of-range error
        if len(g1) > len(g2):
            # genereate random an integer in the range [0, len(g2)-1], both inclusive.
            x = random.randint(0, len(g2)-1)
            # if the random number equals the length -1 of g2, the whole new gene equals g1
            if x == len(g2)-1:
                return g1
        else:
            # genereate random an integer in the range [0, len(g1)-1], both inclusive.
            x = random.randint(0, len(g1)-1)
            # if the random number equals the length -1 of g1, the whole new gene equals g1
            if x == len(g1)-1:
                return g1
        # if the random number is 0, the whole new gene equals g2
        if x == 0:
            return g2
        return np.concatenate((g1[:x], g2[x:]))

    Title: CM3020 Artificial Intelligence, Week 10 Mid-term coursework
    Author: The author of this project (Anonoymous submission of assignment)
    Date: 2026
    Code version: N/A
    Availability: Submitted Assignment (Not published)
    (Week 10 Mid-term coursework of CM3020 Artificial Intelligence, 2026)

    The code in this function was adapted from the mid-term coursework in the week 10 of "CM3020 Artificial Intelligence" by the author of this project
    All the code was written and prepared by the author of this project, with reference to the starter code from the mid-term coursework of "CM3020 Artificial Intelligence" (Yee-King, no date)

    Reference:
    Yee-King, M., (no date) CM3020 Artificial Intelligence, Week 10 Mid-term coursework starter code [online] Available from: https://www.coursera.org/learn/uol-cm3020-artificial-intelligence/assignment-submission/6JASg/mid-term-coursework [8 December 2025]
    '''

    # Single point crossover
    ## New genome was made from the first part of g1 and last part of g2
    # input: 
    # 1. g1: DNA of a strategy
    # 2. g2: DNA of another strategy
    # output: 
    # 1. a new dna made with g1 mixing with g2
    @staticmethod
    def crossover(g1, g2):
        # the index of the selected point should be lower than or equal to the shorter g1 and g2
        # This avoid the index out-of-range error
        if len(g1) > len(g2):
            # genereate random an integer in the range [0, len(g2)-1], both inclusive.
            x = random.randint(0, len(g2)-1)
            # if the random number equals the length -1 of g2, the whole new gene equals g1
            if x == len(g2)-1:
                return g1
        else:
            # genereate random an integer in the range [0, len(g1)-1], both inclusive.
            x = random.randint(0, len(g1)-1)
            # if the random number equals the length -1 of g1, the whole new gene equals g1
            if x == len(g1)-1:
                return g1
        # if the random number is 0, the whole new gene equals g2
        if x == 0:
            return g2
        return np.concatenate((g1[:x], g2[x:]))

    '''
    # The amount was the value to be added to or subtracted from the existing gene(s)
    # The Modulus of 1 (mod 1) or (%1) limited the range of new gene(s) to [0, 1), 1 was excluded
    # input: 
    ## 1. DNA, 
    ## 2. the chance to mutate, 
    ## 3. the amount of the mutation
    # output:
    ## 1. DNA (same as input dna or after mutation)
    @staticmethod
    def point_mutate(genome, rate=0, amount=0.1):
        # I changed copy to deepcopy
        new_genome = copy.deepcopy(genome)
        for gene in range(len(new_genome)):
            for g in range(len(new_genome[gene])):
                if random.random() < rate:
                    # The value of genes should be from 0 to 1
                    # Newly randomly generated genes were in the range of [0, 1), 1 was excluded
                    new_genome[gene][g] = (new_genome[gene][g] + (random.random() * amount * 2 - amount)) % 1
        return new_genome

    Title: CM3020 Artificial Intelligence, Week 10 Mid-term coursework
    Author: The author of this project (Anonoymous submission of assignment)
    Date: 2026
    Code version: N/A
    Availability: Submitted Assignment (Not published)
    (Week 10 Mid-term coursework of CM3020 Artificial Intelligence, 2026)

    The code in this function was adapted from the mid-term coursework in the week 10 of "CM3020 Artificial Intelligence" by the author of this project
    All the code was written and prepared by the author of this project, with reference to the starter code from the mid-term coursework of "CM3020 Artificial Intelligence" (Yee-King, no date)

    Reference:
    Yee-King, M., (no date) CM3020 Artificial Intelligence, Week 10 Mid-term coursework starter code [online] Available from: https://www.coursera.org/learn/uol-cm3020-artificial-intelligence/assignment-submission/6JASg/mid-term-coursework [8 December 2025]
    '''
    # The amount was the value to be added to or subtracted from the existing gene(s)
    # The Modulus of 1 (mod 1) or (%1) limited the range of new gene(s) to [0, 1), 1 was excluded
    # input: 
    ## 1. DNA, 
    ## 2. the chance to mutate, 
    ## 3. the amount of the mutation
    # output:
    ## 1. DNA (same as input dna or after mutation)
    @staticmethod
    def point_mutate(genome, rate=0, amount=0.1):
        # I changed copy to deepcopy
        new_genome = copy.deepcopy(genome)
        for gene in range(len(new_genome)):
            if random.random() < rate:
                # The value of genes should be from 0 to 1
                # Newly randomly generated genes were in the range of [0, 1), 1 was excluded
                new_genome[gene] = (new_genome[gene] + (random.random() * amount * 2 - amount)) % 1
        return new_genome

