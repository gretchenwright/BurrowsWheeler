"""
Implement efficient algos from Pevzner & Compeau BWT chapter
Construct BWT from suffix tree
Suffix tree:all nodes are labeled with the start and end locations in T corresponding to their text string
Leaf nodes are additionally labeled with the index of where the suffix ending there originated in T
Then to find the BWT, we do a DFS where we always start by exploring the child node with the earlier character
in the alphabet. And when we get to a leaf, we append T[i - 1] to the growing BWT.

Data structures:
index everything by integers: separate dictionary for each piece of data
G gives the child nodes, NS, NE give the start and end locations of the node substrings, SS gives the suffix starting
indices

"""

import argparse
import re
import sys


class BWMatch:
    def __init__(self, filename):
        with open(filename) as f:
            self.BWT = f.readline().strip()
            suffix_array_list = f.readline().strip().split(',')
            self.suffix_array = {}
            for s in suffix_array_list:
                k, v = s.split(';')
                self.suffix_array[int(k)] = int(v)
            alphabet = [x for x in f.readline().strip().split(',')]
            self.C = {}
            for a in alphabet:
                self.C[a] = [int(x) for x in f.readline().strip().split(',')]
            self.first_occurrence = {}
            first_occurrence_list = [int(x) for x in f.readline().strip().split(',')]
            for i, a in enumerate(alphabet):
                self.first_occurrence[a] = first_occurrence_list[i]
            self.suffix_array_gap = int(f.readline().strip())
            self.count_gap = int(f.readline().strip())

    def last_to_first(self, index):
        letter = self.BWT[index]
        return self.first_occurrence[letter] + self.reconstruct_count(letter, index)

    def reconstruct_suffix_array(self, index):
        count = 0
        while self.suffix_array.get(index) is None:
            index = self.last_to_first(index)
            count += 1
        return self.suffix_array[index] + count

    def find_matches(self, pattern):
        top = 0
        bottom = len(self.BWT) - 1
        while top <= bottom:
            if len(pattern) > 0:
                symbol = pattern[-1]
                pattern = pattern[:-1]
                count_top = self.reconstruct_count(symbol, top)
                count_bottom = self.reconstruct_count(symbol, bottom + 1)
                if count_bottom - count_top > 0:
                    top = self.first_occurrence[symbol] + count_top
                    bottom = self.first_occurrence[symbol] + count_bottom - 1
                else:
                    return []
            else:
                return [self.reconstruct_suffix_array(x) for x in range(top, bottom + 1)]

    def match_all_patterns(self, patternfile, outputfile):
        with open(patternfile) as f, open(outputfile, "w") as g:
            while True:
                read_name = f.readline().strip()
                if read_name == '':
                    break
                assert(read_name.startswith('>'))
                read_value = f.readline().strip()
                assert(not(read_value.startswith('>')))
                if re.search('N', read_value):
                    continue
                match = self.find_matches(read_value)
                if not match:
                    revcomp = reverse_complement(read_value)
                    match = self.find_matches(revcomp)
                if match:
                    g.write(read_name + '\t')
                    result = '\t'.join(str(m) for m in match)
                    g.write(result + '\n')

    def reconstruct_count(self, letter, index):
        # when C is the partial count array with gap 'gap', return the number of occurrences of letter strictly
        # before index 'index'
        loc = index - (index % self.count_gap)
        count_loc = int(index / self.count_gap)
        count = self.C[letter][count_loc]
        while loc < index:
            if self.BWT[loc] == letter:
                count += 1
            loc += 1
        return count
        
def parse_command_line_arguments(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument("indexfile",
                        help="the file containing the index of the genome to which to align the pattern(s)")
    pattern_source = parser.add_mutually_exclusive_group()
    pattern_source.add_argument("--patternstring", help="a single pattern to be matched")
    pattern_source.add_argument("--patternfile",
                                help="the name of a file containing the patterns to be matched, in fasta format")
    parser.add_argument("--outputfile", help="the file to which to write the match results")
    return parser.parse_args()


def reverse_complement(read):
    rc = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    resp = ''
    for i in read[::-1]:
        resp += rc[i]
    return resp


if __name__ == '__main__':

    args = parse_command_line_arguments(sys.argv)

    B = BWMatch(args.indexfile)
    if args.patternstring:
        print(B.find_matches(args.patternstring))
    elif args.patternfile:
        B.match_all_patterns(args.patternfile, args.outputfile)
    else:
        print("Please supply a pattern string or a pattern file")
