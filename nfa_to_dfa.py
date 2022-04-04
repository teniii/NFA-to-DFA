from typing import Tuple, List, TextIO
import graphviz

LAMBDA = 'lambda'
GRAPH_REPR = graphviz.Digraph()


"""
    Clasa pentru AFN

    Campuri:
        input_file
        output_file_name
        states (type = list[str])
        start_state (type = str)
        final_states (type = list[str])
        delta - multimea tranzitiilor dintr-o stare X in alta stare Y prin operatorul T
                in format [X, T, Y] (type = list[list[string]])
        alphabet - symbols for transitions (type = list)
        
        == utilitare ==

        states_to_index_dict (type = dict[str:int])
        alphabet_to_index_dict (type = dict[str:int])
        delta_table (type = dict['initial_state_id'+'operator' : list['new_states']])

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

        alphabet = lines[3].split()
        if(LAMBDA not in alphabet):
            alphabet.append(LAMBDA)

        delta = []

        for line in lines[4:]:
            line = line.split()

            curr_state = line[0]
            next_state = line[2]
            symbol = line[1]

            delta.append([curr_state, symbol, next_state])

        return (list(states), start_state, list(final_states), delta, list(alphabet))


    def __init__(self, input_file: TextIO, output_file_name:TextIO) -> None:
        self.input_file = input_file
        self.output_file_name = output_file_name

        (self.states,
        self.start_state,
        self.final_states,
        self.delta,
        self.alphabet) = self.read_input()

        # Popularea unor dictionare pentru a avea o mapare [valoare]: index
        self.states_to_index_dict = dict()
        for state_index in range(len(self.states)):
            self.states_to_index_dict[self.states[state_index]] = state_index

        self.alphabet_to_index_dict = dict()
        for operator_index in range(len(self.alphabet)):
            self.alphabet_to_index_dict[self.alphabet[operator_index]] = operator_index
        

        # Delta_table este de forma [Index stare initiala + index operator din alfabet]: [Starile noi]
        self.delta_table = dict()
        for state_index in range(len(self.states)):
            for alphabet_index in range(len(self.alphabet)):
                # Initializarea tuturor cheilor stare+operator
                self.delta_table[(state_index,alphabet_index)] = []

        for i in range(len(self.delta)):
            # Popularea
            self.delta_table[
                (self.states_to_index_dict[self.delta[i][0]],
                self.alphabet_to_index_dict[self.delta[i][1]])
            ].append(
                self.states_to_index_dict[self.delta[i][2]]
                )


    """
    Functie folosita pentru a returna lambda inchiderile (starile dupa lambda tranzitii) asociate unei stari trimise ca parametru
    """
    def get_states_after_lambda_transitions(self, state) -> List:
        # Dict care stocheaza toate starile in care se poate ajunge cu lamba tranzitii
        # Initial valorile sunt 0, iar odata ce o stare a fost verificata, este marcata cu 1
        state_verified_dict = dict()
        state_verified_dict[self.states_to_index_dict[state]] = 0

        # Coada cu starile ce mai trebuie verificate
        queue = [self.states_to_index_dict[state]]

        # Cat timp mai exista stari in coada, iteram
        while (len(queue) > 0):
        
            # Extragem prima stare din coada
            current_state = queue.pop(0)
            
            # Iteram prin lambda inchiderile starii curente
            for nfa_state in self.delta_table[
            (current_state,
            self.alphabet_to_index_dict[LAMBDA])]:
                # Daca starea nu este in dictionar, o adaugam ca neverificata si o adaugam in coada
                if nfa_state not in state_verified_dict.keys():
                    state_verified_dict[nfa_state] = 0
                    queue.append(nfa_state)

            # La finalizarea iteratiei starea curenta se considera ca fiind verificata
            state_verified_dict[current_state] = 1
        return list(state_verified_dict.keys())


    """
    Functie pentru a seta un nume nodurilor din graf
    """
    def get_DFA_state_name(self, states):

        list_for_join = [self.states[state] for state in states]

        return "{" + ",".join(list_for_join) + '}'
    

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

    """
    Functie pentru a adauga prima stare AFD in reprezentarea visuala sub forma de graf
    """
    def add_first_node_to_graph(self, state):
        # Verifiicare daca primul nod este stare finala in AFD
        if (self.is_final_DFA_state(state)):
            GRAPH_REPR.attr('node', shape='doublecircle')
        else:
            GRAPH_REPR.attr('node', shape='circle')
        GRAPH_REPR.node(self.get_DFA_state_name(state))

        # Adaugam sageata la starea de start
        GRAPH_REPR.attr('node', shape='none')
        GRAPH_REPR.node('')
        GRAPH_REPR.edge('', self.get_DFA_state_name(state))


    """
    Functie pentru conversia la AFD
    """
    def convert_to_DFA(self):
        queue = list()

        # pornim de la lambda inchiderile starii de start
        queue.append(self.get_states_after_lambda_transitions(self.start_state))
        
        # adaugarea primului nod in graf
        self.add_first_node_to_graph(queue[0])

        # lista cu toate starile AFD
        dfa_states = list()

        # prima stare este formata chiar din lambda inchiderile starii de start
        dfa_states.append(queue[0])

        while (len(queue) > 0):
            # Starea curenta AFD
            current_DFA_state = queue.pop(0)

            # Iteram prin alfabet pentru a calcula tranzitiile in AFD
            # Avem -1 pentru a exclude lambda
            for op_index in range(len(self.alphabet) - 1):

                initial_NFA_trans = set()
                for NFA_state in current_DFA_state:
                    # Adaugam toate tranzitiile starilor AFN din starea AFD curenta
                    initial_NFA_trans.update(
                        set(self.delta_table[(NFA_state,op_index)]))

                # Verificam multimea sa nu fie goala
                if (len(initial_NFA_trans) > 0):
                    # Stari AFN dupa lambda tranzitii <=> Stare AFD
                    NFA_states_after_lambda_trans = set()
                    for NFA_state in list(initial_NFA_trans):
                        # Pentru fiecare stare se populeaza multimea starilor dupa lamda tranziti
                        NFA_states_after_lambda_trans.update(set(self.get_states_after_lambda_transitions(self.states[NFA_state])))

                    # Verificam daca lista de lambda inchideri (starea AFD) nu este deja in dfa_states
                    # Se poate adauga un else pentru a face un AFD complet
                    if list(NFA_states_after_lambda_trans) not in dfa_states:
                        # Adaugam in coada noua stare AFD
                        queue.append(list(NFA_states_after_lambda_trans))
                        # Adaugam in lista de stari AFD noua stare generata
                        dfa_states.append(list(NFA_states_after_lambda_trans))

                # ======= AFISARE =======
                        # Verificam daca noua stare este finala, pentru afisare
                        if (self.is_final_DFA_state(list(NFA_states_after_lambda_trans))):
                            GRAPH_REPR.attr('node', shape='doublecircle')
                        else:
                            GRAPH_REPR.attr('node', shape='circle')
                        GRAPH_REPR.node(self.get_DFA_state_name(list(NFA_states_after_lambda_trans)))

                    # Adaugarea arcului de la starea curenta la starea urmatoare
                    GRAPH_REPR.edge(self.get_DFA_state_name(current_DFA_state),
                            self.get_DFA_state_name(list(NFA_states_after_lambda_trans)),
                            label=self.alphabet[op_index])
                # ======= |||||| =======

        # Randarea grafului
        GRAPH_REPR.render(self.output_file_name)


# Creara unei instante a clasei
nfa = NFA(open('input.txt'), 'conversion_to_DFA')

# Apelarea functiei de convertire din AFN in AFD
nfa.convert_to_DFA()
