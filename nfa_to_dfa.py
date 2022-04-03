from typing import Tuple, List, TextIO
import graphviz

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
    Functie folosita pentru citirea datelor asociate AFN-ului, din fisierul de input:
        starile
        starea initiala
        starile finale
        alfabetul
        tranzitiile
    """
    def read_input(self) -> Tuple[int, List, str, List, List, List]:
        lines = self.input_file.readlines()

        states = set(lines[0].split())

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

            delta.append([curr_state, symbol, next_state])

        return (list(states), start_state, list(final_states), delta, list(alphabet))


    def __init__(self, input_file: TextIO, output_file:TextIO) -> None:
        self.input_file = input_file
        self.output_file = output_file

        (self.states,
        self.start_state,
        self.final_states,
        self.delta,
        self.alphabet) = self.read_input()

        self.graph = graphviz.Digraph()

        # popularea unor dictionare pentru a avea o mapare [valoare]: index
        self.states_to_index_dict = dict()
        for state_index in range(len(self.states)):
            self.states_to_index_dict[self.states[state_index]] = state_index

        self.alphabet_to_index_dict = dict()
        for operator_index in range(len(self.alphabet)):
            self.alphabet_to_index_dict[self.alphabet[operator_index]] = operator_index
            
        # delta_table este de forma [Index stare initiala + index operator din alfabet]: [Starile noi]
        self.delta_table = dict()
        for state_index in range(len(self.states)):
            for alphabet_index in range(len(self.alphabet)):
                # initializarea tuturor cheilor stare+operator
                self.delta_table[str(state_index)+','+str(alphabet_index)] = []

        for i in range(len(self.delta)):
            # popularea
            self.delta_table[
                str(self.states_to_index_dict[self.delta[i][0]])+','+
                str(self.alphabet_to_index_dict[self.delta[i][1]])
            ].append(
                self.states_to_index_dict[self.delta[i][2]]
                )


    """
    Functie folosita pentru a returna starile dupa lambda tranzitii asociate unei stari trimise ca parametru
    """
    def get_states_after_lambda_transitions(self, state):
        # dict care stocheaza toate starile in care se poate ajunge cu lamba tranzitii
        # initial valorile sunt 0, iar odata ce o stare a fost verificata, este marcata cu 1
        state_verified_dict = dict()
        state_verified_dict[self.states_to_index_dict[state]] = 0

        # coada cu starile ce mai trebuie verificate
        queue = [self.states_to_index_dict[state]]

        # Cat timp mai exista stari in coada, iteram
        while (len(queue) > 0):
        
            # Extragem prima stare din coada
            current_state = queue.pop(0)
            
            # For the epsilon transition of that state,
            # if not present in closure array then add to dict and push to stack
            for x in self.delta_table[
            str(current_state)+','+
            str(self.alphabet_to_index_dict[LAMBDA])]:
                if x not in state_verified_dict.keys():
                    state_verified_dict[x] = 0
                    queue.append(x)
            state_verified_dict[current_state] = 1
        return state_verified_dict.keys()


    """
    Functie pentru a seta un nume nodurilor din graf
    """
    def get_DFA_state_name(self, states):

        list_for_join = [self.states[state] for state in states]

        return "[" + ",".join(list_for_join) + ']'
    
    """
    Functie pentru a verifica daca o stare din AFD este finala
    """
    def is_final_DFA_state(self, states):

        # Verificam daca lista de stari include o stare finala din AFN
        for x in states:
            for y in self.final_states:
                if (x == self.states_to_index_dict[y]):
                    return True
        return False


# Making an object of Digraph to visualize NFA diagram
nfa = NFA(open('input.txt'), open('output.txt', 'w'))

dfa_vGraf = graphviz.Digraph()


# Finding epsilon closure beforehand so to not recalculate each time
epsilon_closure = dict()
for x in nfa.states:
	epsilon_closure[x] = list(nfa.get_states_after_lambda_transitions(x))

# First state of DFA will be epsilon closure of start state of NFA
# This list will act as stack to maintain till when to evaluate the states
dfa_stack = list()
dfa_stack.append(epsilon_closure[nfa.start_state])

# Check if start state is the final state in DFA
if (nfa.is_final_DFA_state(dfa_stack[0])):
	dfa_vGraf.attr('node', shape='doublecircle')
else:
	dfa_vGraf.attr('node', shape='circle')
dfa_vGraf.node(nfa.get_DFA_state_name(dfa_stack[0]))

# Adding start state arrow to start state in DFA
dfa_vGraf.attr('node', shape='none')
dfa_vGraf.node('')
dfa_vGraf.edge('', nfa.get_DFA_state_name(dfa_stack[0]))

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
				set(nfa.delta_table[str(x)+','+str(al)]))

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
				if (nfa.is_final_DFA_state(list(to_state))):
					dfa_vGraf.attr('node', shape='doublecircle')
				else:
					dfa_vGraf.attr('node', shape='circle')
				dfa_vGraf.node(nfa.get_DFA_state_name(list(to_state)))

			# Adding edge between from state and to state
			dfa_vGraf.edge(nfa.get_DFA_state_name(cur_state),
					nfa.get_DFA_state_name(list(to_state)),
					label=nfa.alphabet[al])

# Makes a pdf with name dfa.pdf and views the pdf
dfa_vGraf.render('dfa', view = True)