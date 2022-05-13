from curses.ascii import isalpha, isupper
from math import nextafter
import re
from symtable import Symbol
from nltk.tree import *
from collections import defaultdict
from anytree import *
from numpy import ndarray
import sys

def rule_translate(rule):
    rule_parts = re.split('\s->\s',rule)
    right_part = re.split('\s',rule_parts[1])
    return (rule_parts[0],right_part)



class state:
    def __init__(self, left, right, dot, start_col):
       self.name = left
       self.right = right
       self.dot = dot
       self.start_col = start_col
       self.end_col = None
    
    def __str__(self):
        str_self = self.name + " -> "
        return self.name + " -> " + " ".join(self.right[:self.dot]) + " . " + \
                " ".join(self.right[self.dot:]) + " " + str(self.start_col.index) + " " + (str(self.end_col.index) if self.end_col else " -1 ")
    
    def dot_state(self):
        return self.right[self.dot] if self.dot < len(self.right) else None

    def done(self):
        return self.dot >= len(self.right)

    def identifier(self):
        return (self.name," ".join(self.right), self.dot,self.start_col.index)
    
    def __hash__(self):
        return hash(self.identifier())

    def __eq__(self, other) -> bool:
        return self.identifier() == other.identifier()
    
    def next(self):
        return state(self.name, self.right, self.dot+1, self.start_col)
    

class column:
    def __init__(self, index, token):
        self.index = index
        self.token = token
        self.states = []
        self.unique_state = set()
    
    def __str__(self):
        col_str = ""
        for state in self.states:
            col_str += str(state)
            col_str += "\n"
        return col_str
    
    def add(self, state):
        if state not in self.unique_state:
            # print("Adding: " + str(state))
            # print("Current states: ")
            # print(str(self))
            state.end_col = self
            self.unique_state.add(state)
            self.states.append(state)
            return True
        return False
            

class earley:
    def __init__(self, grammar):
        self.grammar = grammar
        self.columns = []
        self.completion_track = []
    
    def create_columns(self, tokens, start, first_rule):
        self.columns = [column(i,token) for i,token in enumerate(tokens)]
        for rule in first_rule:
            self.columns[0].add(state(start,rule,0,self.columns[0]))
    
    def predict(self, col, symmbol):
        for rule in self.grammar[symmbol]:
            col.add(state(symmbol,rule, 0, col))

    def scanner(self, col, state, token):
        if token == col.token:
            next_state = state.next()
            added = col.add(next_state)
            if(added):
                self.completion_track.append(next_state)
    
    def completer(self, col, state):
        previous_nodes = [s for s in state.start_col.states if s.dot_state() == state.name]
        # print("----------------------------------------------------------")
        # print("complete child: " + str(state))
        # print("parents: ")
        for node in previous_nodes:
            next_state = node.next()
            added = col.add(next_state)
            if(next_state.done() and added):
                self.completion_track.append(next_state)
                # print(str(next_state))

        # print("----------------------------------------------------------")

    def column_processing(self):
        for i, col in enumerate(self.columns):
            for state in col.states:
                if state.done():
                    self.completer(col,state)
                else:
                    symbol = state.dot_state()
                    if symbol in self.grammar:
                        self.predict(col, symbol)
                    elif(i + 1 < len(self.columns)):
                        self.scanner(self.columns[i+1], state, symbol)
        
# class node:
#     def __init__(self, name, children = []):
#         self.name = name
#         self.children = children

#     def add_child(self,child):
#         self.children.append(child)

#     def __str__(self, level=0):
#         ret = "\t"*level+repr(self.name)+"\n"
#         for child in self.children:
#             ret += child.__str__(level+1)
#         return ret

#     def __repr__(self):
#         return '<tree node ' + self.name + '>'

def is_terminal(t):
    return isupper(t[0])

def tree_build(states, tokens):
    if len(states[0]) > 0:
        root_states = []
        root_nodes = []
        solution_output = []
        working_tree = []
        solution_tree = []
        for st in states[0]:
            if st.name == "S":
                root_states.append(st)
                
        cleanup_index = 0
        for root in root_states:
            last_symbol = root.right.pop()
            for i,s in enumerate(states[0]):
                if last_symbol == s.name:
                    working_tree.append([Node('S')])
                    solution_tree.append([working_tree[-1].pop()])
                    for r in root.right:
                        working_tree[-1].append(Node(r, parent=solution_tree[-1][-1]))
                    
                    
                    solution_tree[-1].append(Node(last_symbol, parent=solution_tree[-1][-1]))
                    for sn in s.right:
                        working_tree[-1].append(Node(sn, parent=solution_tree[-1][-1]))
                    solution_output.append(['S'] + root.right + s.right)
                    cleanup_index = i

        states[0] = states[0][cleanup_index:]
        
        for count in range(len(solution_output)):
            for token_states in states:
                for i, st in enumerate(token_states):
                    non_t = None
                    t = None
                    if st.name == solution_output[count][-1]:
                        non_t = solution_output[count].pop()
                        solution_tree[count].append(working_tree[count].pop())
                        for j in st.right:
                            solution_output[count].append(j)
                            working_tree[count].append(Node(j,parent=solution_tree[count][-1]))
                            
                    if not is_terminal(solution_output[count][-1]):
                        t = solution_output[count].pop()
                        solution_tree[count].append(working_tree[count].pop())

        if len(solution_tree) == 0:
            print("Error: Could not build path and tree from inputs")
        else:
            for tree in solution_tree:
                result = [node.name for node in PreOrderIter(tree[0]) if node.is_leaf]
                if result != tokens:
                    solution_tree.remove(tree)
            
            for tree in solution_tree:
                for pre, fill, node in RenderTree(tree[0]):
                    print("%s%s" % (pre, node.name))
        

    else:
        print("Error: Could not build path and tree from inputs")



def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("python3 parser.py grammer.cfg string_parsing")
        print("Using anytree library for visualization -> pip3 install anytree")
    else:
        grammar_string = ""


        for line in open(sys.argv[1], "r"):
            if not line.startswith("#"):
                grammar_string += line
        rules = re.split('\n',grammar_string)[:-1]
        rules_dict = defaultdict(list)
        tokens = [None] + re.split("\s",sys.argv[2])
        for rule in rules:
            left_right = rule_translate(rule)
            rules_dict[left_right[0]].append(left_right[1])
        
        # create earley parser
        e1 = earley(rules_dict)
        e1.create_columns(tokens, "S", rules_dict["S"])
        e1.column_processing()

        preprocess_states = []

        # exclude dead states
        for col in e1.columns:
            col_state = []
            for st in col.states:
                if(st.done()):
                    col_state.append(st)
            col_state.reverse()
            preprocess_states.append(col_state)
        preprocess_states.reverse()

        # build and print trees
        tree_build(preprocess_states, tokens[1:])



if __name__ == '__main__':
    main()
