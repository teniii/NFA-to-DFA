from typing import Tuple, List, Dict
import graphviz
from collections import defaultdict

LAMBDA = 'lambda'

"""
    Clasa pentru AFN

    Campuri:
        input_file
        output_file
        alphabet - symbols for transitions (type = set)
        number_of_states
        states (type = list[int])
        final_states (type = list[int])
        delta - multimea tranzitiilor dintr-o stare X in alta stare Y prin tranzitia T
                in format [X, T, Y] (type = list[list[string]])
"""
class NFA:

    """
    Functie folosita pentru citirea starilor, tranzitiilor si starilor finale ale AFN
    """
    # def read_input(self) -> Tuple[int, List, str, set, Dict,list]:
    def read_input(self) -> Tuple[int, List, str, List, List, List]:
        lines = self.input_file.readlines()
        # number_of_states = int(lines[0])

        states = set(lines[0].split())
        number_of_states = len(states)

        start_state = lines[1].split()[0]

        final_states = set(lines[2].split())

        alphabet = set(lines[3].split())

        alphabet.add(LAMBDA)

        delta = []

        for line in lines[4:]:
            line = line.split()
            curr_state = line[0]

            next_state = line[2]

            symbol = line[1]

            if line[1] == LAMBDA:
                symbol = LAMBDA
                alphabet.add(symbol)
            else:			
                symbol = line[1]
                alphabet.add(symbol)

            # next_states = []
            # for state in line[2:]:
            #     next_states.append(state)

            # delta[(curr_state, symbol)] = next_states
            delta.append([curr_state, symbol, next_state])

        return (number_of_states, list(states), start_state, list(final_states), delta, list(alphabet))


    def __init__(self, input_file, output_file) -> None:
        # self.no_state = no_state
        # self.states = states
        # self.no_alphabet = no_alphabet
        # self.alphabet = alphabet
        
        # Adding epsilon alphabet to the list
        # and incrementing the alphabet count
        # self.alphabet.append('e')
        # self.no_alphabet += 1

        # ==
        self.input_file = input_file
        self.output_file = output_file
        (self.number_of_states,
        self.states,
        self.start_state,
        self.final_states,
        self.delta,
        self.alphabet) = self.read_input()
        self.alphabet_length = len(self.alphabet)

        # self.delta_length = len(self.delta.keys())
        self.delta_length = len(self.delta)

        print(f" states: {self.states}, final: {self.final_states}, delta: {self.delta}, alphabet: {self.alphabet}, delta_lenght: {self.delta_length} ")
        # == 
        
        print(f"range of self.delta_length: ", range(self.delta_length))

        # self.start = start

        self.graph = graphviz.Digraph()

        # Dictionaries to get index of states or alphabet
        self.states_dict = dict()
        for i in range(self.number_of_states):
            self.states_dict[self.states[i]] = i
        self.alphabet_dict = dict()
        for i in range(self.alphabet_length):
            self.alphabet_dict[self.alphabet[i]] = i
            
        # delta table is of the form
        # [From State + Alphabet pair] -> [Set of To States]
        self.delta_table = dict()
        for i in range(self.number_of_states):
            for j in range(self.alphabet_length):
                self.delta_table[str(i)+str(j)] = []
        for i in range(self.delta_length):
            # print(f"\n\nself.delta[{self.states[i]}][2]")
            # print(f"self.delta:", self.delta)
            # print(f".append(self.states_dict[{self.delta[self.states[i]][2]}])")
            print(f"self.delta_table[{str(self.states_dict[self.delta[i][0]])+str(self.alphabet_dict[self.delta[i][1]])}]")
            self.delta_table[str(self.states_dict[self.delta[i][0]])
                                + str(self.alphabet_dict[
                                    self.delta[i][1]])].append(
                                        self.states_dict[self.delta[i][2]])



    def get_lambda_closures(self, state):
        # Method to get Epsilon Closure of a state of NFA
        # Make a dictionary to track if the state has been visited before
        # And a array that will act as a stack to get the state to visit next
        closure = dict()
        closure[self.states_dict[state]] = 0
        closure_stack = [self.states_dict[state]]

        # While stack is not empty the loop will run
        while (len(closure_stack) > 0):
        
            # Get the top of stack that will be evaluated now
            cur = closure_stack.pop(0)
            
            # For the epsilon transition of that state,
            # if not present in closure array then add to dict and push to stack
            for x in self.delta_table[
                    str(cur)+str(self.alphabet_dict[LAMBDA])]:
                if x not in closure.keys():
                    closure[x] = 0
                    closure_stack.append(x)
            closure[cur] = 1
        return closure.keys()


    def getStateName(self, state_list):

        # Get name from set of states to display in the final DFA diagram
        list_for_join = [self.states[state] for state in state_list]

        return "[" + ",".join(list_for_join) + ']'
    

    def isFinalDFA(self, state_list):

        # Method to check if the set of state is final state in DFA
        # by checking if any of the set is a final state in NFA
        for x in state_list:
            for y in self.final_states:
                if (x == self.states_dict[y]):
                    return True
        return False



# =======

# Making an object of Digraph to visualize NFA diagram
nfa = NFA(open('input.txt'), open('output.txt', 'w'))

dfa_vGraf = graphviz.Digraph()


# Finding epsilon closure beforehand so to not recalculate each time
epsilon_closure = dict()
for x in nfa.states:
	epsilon_closure[x] = list(nfa.get_lambda_closures(x))

# First state of DFA will be epsilon closure of start state of NFA
# This list will act as stack to maintain till when to evaluate the states
dfa_stack = list()
dfa_stack.append(epsilon_closure[nfa.start_state])

# Check if start state is the final state in DFA
if (nfa.isFinalDFA(dfa_stack[0])):
	dfa_vGraf.attr('node', shape='doublecircle')
else:
	dfa_vGraf.attr('node', shape='circle')
dfa_vGraf.node(nfa.getStateName(dfa_stack[0]))

# Adding start state arrow to start state in DFA
dfa_vGraf.attr('node', shape='none')
dfa_vGraf.node('')
dfa_vGraf.edge('', nfa.getStateName(dfa_stack[0]))

# List to store the states of DFA
dfa_states = list()
dfa_states.append(epsilon_closure[nfa.start_state])

# Loop will run till this stack is not empty
while (len(dfa_stack) > 0):
	# Getting top of the stack for current evaluation
	cur_state = dfa_stack.pop(0)

	# Traversing through all the alphabet for evaluating transitions in DFA
	for al in range((nfa.alphabet_length) - 1):
		# Set to see if the epsilon closure of the set is empty or not
		from_closure = set()
		for x in cur_state:
			# Performing Union update and adding all the new states in set
			from_closure.update(
				set(nfa.delta_table[str(x)+str(al)]))

		# Check if epsilon closure of the new set is not empty
		if (len(from_closure) > 0):
			# Set for the To state set in DFA
			to_state = set()
			for x in list(from_closure):
				to_state.update(set(epsilon_closure[nfa.states[x]]))

			# Check if the to state already exists in DFA and if not then add it
			if list(to_state) not in dfa_states:
				dfa_stack.append(list(to_state))
				dfa_states.append(list(to_state))

				# Check if this set contains final state of NFA
				# to get if this set will be final state in DFA
				if (nfa.isFinalDFA(list(to_state))):
					dfa_vGraf.attr('node', shape='doublecircle')
				else:
					dfa_vGraf.attr('node', shape='circle')
				dfa_vGraf.node(nfa.getStateName(list(to_state)))

			# Adding edge between from state and to state
			dfa_vGraf.edge(nfa.getStateName(cur_state),
					nfa.getStateName(list(to_state)),
					label=nfa.alphabet[al])

# Makes a pdf with name dfa.pdf and views the pdf
dfa_vGraf.render('dfa', view = True)