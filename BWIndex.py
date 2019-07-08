import argparse
import sys


# from graphviz import Digraph


class BWIndex:
    def __init__(self, indexfile, genomefile='', genome='', countgap=100, suffixgap=100):
        if genome:
            self.Text = genome
        else:
            self.load_genome_from_file(genomefile)

        if self.Text[-1] != '$':
            print("Genome must be terminated by $")
            sys.exit()
        self.suffix_array_gap = suffixgap
        self.count_gap = countgap
        self.index_file = indexfile
        # The following attributes will be computed by self.build_tree().
        # Define here for transparency
        self.parent_to_child = {0: []}  # parent to child, int -> list
        self.child_to_parent = {}  # child to parent, int -> int
        self.node_count = 1
        self.node_start = {}  # node start index
        self.node_end = {}  # node end index
        self.suffix_start = {}  # suffix start index
        self.build_tree()
        self.BWT, self.suffixArray = self.compute_transform()
        self.Count = {}
        self.letters = {i for i in self.BWT}
        self.alphabet = [i for i in self.letters]
        self.alphabet.sort()
        self.compute_count_array()

        self.first_occurrence = {}
        freq = {}
        for i in self.BWT:
            freq[i] = freq.get(i, 0) + 1
        index = 0
        self.first_occurrence['$'] = 0
        for j in range(1, len(self.alphabet)):
            prev_letter = self.alphabet[j - 1]
            letter = self.alphabet[j]
            index += freq[prev_letter]
            self.first_occurrence[letter] = index

        self.export_index(self.index_file)

    def build_tree(self):

        for ix in range(len(self.Text)):
            self.thread_suffix(ix)

    def export_index(self, filename):
        with open(filename, 'w') as g:
            g.write(self.BWT + '\n')
            if self.suffix_array_gap is None:
                g.write(','.join(str(i) + ';' + str(s) for i, s in enumerate(self.suffixArray)) + '\n')
            else:
                g.write('{0}\n'.format(','.join(str(i) + ';' + str(s) for i, s in enumerate(self.suffixArray)
                                                if s % self.suffix_array_gap == 0)))
            g.write(','.join(str(x) for x in sorted(self.Count.keys())) + '\n')
            for x in sorted(self.Count.keys()):
                if self.count_gap is None:
                    g.write(','.join(str(self.Count[x][i]) for i in range(len(self.Count[x]))) + '\n')
                else:
                    g.write('{0}\n'.format(
                        ','.join(str(self.Count[x][i]) for i in range(len(self.Count[x])) if i % self.count_gap == 0)))
            g.write(','.join(str(self.first_occurrence[x]) for x in sorted(self.first_occurrence.keys())) + '\n')
            g.write(str(self.suffix_array_gap) + '\n')
            g.write(str(self.count_gap) + '\n')

    def compute_transform(self):
        stack = [('', 0)]
        transform = ''
        suffix_array = []
        while stack:
            node = stack.pop()
            node_index = node[1]
            if self.parent_to_child.get(node_index) is not None:
                if self.parent_to_child[node_index]:
                    children = [(self.Text[self.node_start[child]], child) for child in
                                self.parent_to_child[node_index]]
                    children.sort(reverse=True)
                    stack += children
            else:
                transform += self.Text[self.suffix_start[node_index] - 1]
                suffix_array.append(self.suffix_start[node_index])
        return transform, suffix_array

    def draw_graph(self, max_label_length=None, out_file=None):
        digraph = Digraph()
        self.node_start[0] = 0
        self.node_end[0] = -1
        for i in range(self.node_count):
            label = self.Text[self.node_start[i]:self.node_end[i] + 1]
            if max_label_length:
                label = label[:max_label_length]
            digraph.node(str(i), label)
        for tail in self.parent_to_child:
            for head in self.parent_to_child[tail]:
                digraph.edge(str(tail), str(head))
        digraph.render(out_file, view=True)

    def report(self):
        print(self.parent_to_child, self.child_to_parent, self.node_start, self.node_end, self.suffix_start, self.BWT,
              self.suffixArray, self.first_occurrence, self.Count)

    def append_node(self, parent, node_string_start, suffix_start):
        new_node = self.node_count
        self.parent_to_child[parent] = self.parent_to_child.get(parent, []) + [new_node]
        self.child_to_parent[new_node] = parent
        self.node_start[new_node] = node_string_start
        self.node_end[new_node] = len(self.Text) - 1
        self.suffix_start[new_node] = suffix_start
        self.node_count += 1

    def split_node(self, node, index):
        # introduce a new node whose parent is the original parent of node, make it the new parent of node
        new_node = self.node_count
        parent = self.child_to_parent[node]
        self.parent_to_child[new_node] = [node]
        self.parent_to_child[parent].remove(node)
        self.parent_to_child[parent] = self.parent_to_child.get(parent, []) + [new_node]
        self.child_to_parent[new_node] = parent
        self.child_to_parent[node] = new_node
        self.node_start[new_node] = self.node_start[node]
        self.node_end[new_node] = index - 1
        self.node_start[node] = index
        self.node_count += 1
        return new_node

    def find_matching_child(self, node, loc):
        for child in self.parent_to_child[node]:
            if self.Text[loc] == self.Text[self.node_start[child]]:
                return child
        return -1

    def first_mismatch(self, node, ix):
        offset = 1
        while True:
            if ix + offset >= len(self.Text):
                return self.node_start[node] + offset
            if self.node_start[node] + offset > self.node_end[node]:
                return -1
            if self.Text[self.node_start[node] + offset] != self.Text[ix + offset]:
                return self.node_start[node] + offset
            offset += 1

    def thread_suffix(self, ix):
        """
        look for a node that matches the start of the current substring
        if none found, create a new node and set its string to the current substring and SS to the initial index
        if one is found, look for a mismatch within the string
        if no mismatch, advance current_index by the length of the node string and iterate
        if a mismatch is found, split the target node and append the remainder of the substring
        """
        node = 0
        current_index = ix
        while True:
            next_node = self.find_matching_child(node, current_index)
            if next_node == -1:
                self.append_node(node, current_index, ix)
                break
            node = next_node
            split_loc = self.first_mismatch(node, current_index)
            if split_loc != -1:
                new_node = self.split_node(node, split_loc)
                self.append_node(new_node, split_loc + (current_index - self.node_start[new_node]), ix)
                break
            else:
                current_index += self.node_end[node] - self.node_start[node] + 1

    def compute_count_array(self):
        for i in self.alphabet:
            self.Count[i] = [0] * (len(self.Text) + 1)  # check does this cause any reference issues?
        for j in range(1, len(self.BWT) + 1):
            self.Count[self.BWT[j - 1]][j] = self.Count[self.BWT[j - 1]][j - 1] + 1
            for k in self.alphabet:
                if k != self.BWT[j - 1]:
                    self.Count[k][j] = self.Count[k][j - 1]
        return self.Count

    def find_count(self, pattern):
        top = 0
        bottom = len(self.BWT) - 1
        while top <= bottom:
            if len(pattern) > 0:
                symbol = pattern[-1]
                pattern = pattern[:-1]
                if self.Count[symbol][bottom + 1] - self.Count[symbol][top] > 0:
                    top = self.first_occurrence[symbol] + self.Count[symbol][top]
                    bottom = self.first_occurrence[symbol] + self.Count[symbol][bottom + 1] - 1
                else:
                    return 0
            else:
                return bottom - top + 1

    def load_genome_from_file(self, genomefile):
        lines = []
        with open(genomefile) as f:
            for line in f:
                if line != '':
                    if line[0] != '>':
                        lines.append(line.strip())
        self.Text = ''.join(lines)
        if self.Text[-1] != '$':
            self.Text = self.Text + '$'


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    genome_source = parser.add_mutually_exclusive_group()
    genome_source.add_argument('--genomefile', help='File containing text of genome all on one line')
    genome_source.add_argument('--genome', help='Genome in string form, terminated by $')
    parser.add_argument('--countgap', help='gap between elements of count array', type=int)
    parser.add_argument('--suffixgap', help='gap between elements of suffix array', type=int)
    parser.add_argument('indexfile', help='File to write the index to')

    args = parser.parse_args()
    if args.genomefile:
        BWIndex(args.indexfile, genomefile=args.genomefile, countgap=args.countgap, suffixgap=args.suffixgap, )
    else:
        BWIndex(args.indexfile, genome=args.genome, countgap=args.countgap, suffixgap=args.suffixgap, )
