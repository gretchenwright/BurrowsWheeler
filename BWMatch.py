'''
Implement efficient algos from Pevzner & Compeau BWT chapter
Construct BWT from suffix tree
Suffix tree:all nodes are labeled with the start and end locations in T corresponding to their text string
Leaf nodes are additionally labeled with the index of where the suffix ending there originated in T
Then to find the BWT, we do a DFS where we always start by exploring the child node with the earlier character in the alphabet. And when we get to a leaf, we append T[i - 1] to the growing BWT.

Data structures:
index everything by integers: separate dictionary for each piece of data
G gives the child nodes, NS, NE give the start and end locations of the node substrings, SS gives the suffix starting indices

'''

from graphviz import Digraph
import time
import re
import argparse

class BWMatch:
	def __init__(self):
		pass

	def loadIndex(self, filename):
		f = open(filename)
		self.BWT = f.readline().strip()
		SA = f.readline().strip().split(',')
		self.suffixArray = {}
		for s in SA:
			k, v = s.split(';')
			self.suffixArray[int(k)] = int(v)
		alphabet = [x for x in f.readline().strip().split(',')]
		self.C = {}
		for a in alphabet:
			self.C[a] = [int(x) for x in f.readline().strip().split(',')]
		self.FO = {}
		FO_items = [int(x) for x in f.readline().strip().split(',')]
		for i, a in enumerate(alphabet):
			self.FO[a] = FO_items[i]
		self.SA_gap = int(f.readline().strip())
		self.C_gap = int(f.readline().strip())

	def lastToFirst(self, index):
		letter = self.BWT[index]
		return self.FO[letter] + self.reconstructCount(letter, index)

	def reconstructSuffixArray(self, index):
		count = 0
		while self.suffixArray.get(index) is None:
			index = self.lastToFirst(index)
			count += 1
		return self.suffixArray[index] + count

	def FindMatches(self, Pattern):
		top = 0
		bottom = len(self.BWT) - 1
		while top <= bottom:
			if len(Pattern) > 0:
				symbol = Pattern[-1]
				Pattern = Pattern[:-1]
				C_top = self.reconstructCount(symbol, top)
				C_bottom = self.reconstructCount(symbol, bottom + 1)
				if C_bottom - C_top > 0:
					top = self.FO[symbol] + C_top
					bottom = self.FO[symbol] + C_bottom - 1
				else:
					return []
			else:
				return [self.reconstructSuffixArray(x) for x in range(top, bottom + 1)]

	def MatchAllPatterns(self, patternfile, outputfile):
		g = open(outputfile, "w")
		with open(patternfile) as f:
			for line in f:
				line = line.strip()
				if line[0] == '>':
					readName = line
				else:
					readValue = line
					if re.search('N', readValue):
						continue
					match = B.FindMatches(readValue)
					if not match:
						revcomp = reverseComplement(readValue)
						match = B.FindMatches(revcomp)
					if match:
						g.write(readName + '\t')
						result = '\t'.join(str(m) for m in match)
						g.write(result + '\n')

	def reconstructCount(self, letter, index):
		# when C is the partial count array with gap 'gap', return the number of occurrences of letter strictly before index 'index'
		loc = index - (index % self.C_gap)
		C_loc = int(index / self.C_gap)
		count = self.C[letter][C_loc]
		while loc < index:
			if self.BWT[loc] == letter:
				count += 1 
			loc += 1
		return count

def reverseComplement(read):
	rc = {'A':'T', 'T':'A', 'C':'G', 'G':'C'}
	resp = ''
	for i in read[::-1]:
		resp += rc[i]
	return resp

if __name__ == '__main__':
	# B = BWMatch()
	# B.loadIndex("test_index_new.txt")
	# print(B.SA_gap, B.C_gap)
	# print(B.BWT, B.suffixArray, B.C, B.FO)
	# print(B.FindMatches('CCG'))
	
	
	# start_time = time.time()
	# B = BWMatch()
	# B.loadIndex("e_coli_index.txt")
	# print("Loaded index in", time.time() - start_time)
	# start_time = time.time()
 
	# print("Complete read matching in", time.time() - start_time)
	parser = argparse.ArgumentParser()
	parser.add_argument("indexfile", help="the file containing the index of the genome to which to align the pattern(s)")
	pattern_source = parser.add_mutually_exclusive_group()
	pattern_source.add_argument("--patternstring", help="a single pattern to be matched")
	pattern_source.add_argument("--patternfile", help="the name of a file containing the patterns to be matched, in fasta format")
	parser.add_argument("--outputfile", help="the file to which to write the match results")
	args = parser.parse_args()
	
	B = BWMatch()
	B.loadIndex(args.indexfile)
	if args.patternstring:
		print(B.FindMatches(args.patternstring))
	elif args.patternfile:
		B.MatchAllPatterns(args.patternfile, args.outputfile)
	else:
		print("Please supply a pattern string or a pattern file")
		sys.exit()
