import argparse
import sys

from graphviz import Digraph


class BWIndex:
	def __init__(self, genome=None, genomefile=None):
		if genome is not None:
			self.Text = genome
		elif genomefile is not None:
			self.load_genome_from_file(genomefile)
		else:
			print("You must supply a genome file or a genome string.")
			sys.exit()
		if self.Text[-1] != '$':
			print("Genome must be terminated by $")
			sys.exit()
		self.build_tree()
		self.Solve()
		self.Count = dict()
		self.letters = {i for i in self.BWT}
		self.alphabet = [i for i in self.letters]
		self.alphabet.sort()
		self.compute_count_array()

		self.first_occurrence = dict()
		freq = dict()
		for i in self.BWT:
			freq[i] = freq.get(i, 0) + 1
		index = 0
		self.first_occurrence['$'] = 0
		for j in range(1, len(self.alphabet)):
			prev_letter = self.alphabet[j - 1]
			letter = self.alphabet[j]
			index += freq[prev_letter]
			self.first_occurrence[letter] = index

	def build_tree(self):
		self.G = {0: []}  # parent to child, int -> list
		self.H = dict()  # child to parent, int -> int
		self.node_count = 1
		self.node_start = dict()  # node start index
		self.node_end = dict()  # node end index
		self.suffix_start = dict()  # suffix start index
		for ix in range(len(self.Text)):
			# print(ix)
			self.thread_suffix(ix)

	def export_index(self, filename, suffix_array_gap=None, count_array_gap=None):
		g = open(filename, 'w')
		self.suffix_array_gap = suffix_array_gap
		self.count_gap = count_array_gap
		g.write(self.BWT + '\n')
		if suffix_array_gap is None:
			g.write(','.join(str(i) + ';' + str(s) for i, s in enumerate(self.suffixArray)) + '\n')
		else:
			g.write(','.join(str(i) + ';' + str(s) for i, s in enumerate(self.suffixArray) if s % suffix_array_gap == 0) + '\n')
		g.write(','.join(str(x) for x in sorted(self.Count.keys())) + '\n')
		for x in sorted(self.Count.keys()):
			if count_array_gap is None:
				g.write(','.join(str(self.Count[x][i]) for i in range(len(self.Count[x]))) + '\n')
			else:
				g.write(','.join(str(self.Count[x][i]) for i in range(len(self.Count[x])) if i % count_array_gap == 0) + '\n')
		g.write(','.join(str(self.first_occurrence[x]) for x in sorted(self.first_occurrence.keys())) + '\n')
		g.write(str(suffix_array_gap) + '\n')
		g.write(str(count_array_gap) + '\n')

	def Solve(self):
		S = [('', 0)]
		transform = ''
		suffixArray = []
		while S:
			node = S.pop()
			nodeIx = node[1]
			if self.G.get(nodeIx) is not None:
				if self.G[nodeIx]:
					children = [(self.Text[self.node_start[child]], child) for child in self.G[nodeIx]]
					children.sort(reverse=True)
					S += children
			else:
				transform += self.Text[self.suffix_start[nodeIx] - 1]
				suffixArray.append(self.suffix_start[nodeIx])
		self.BWT = transform
		self.suffixArray = suffixArray

	def drawGraph(self, maxLabelLength=None, outFile=None):
		D = Digraph()
		self.node_start[0] = 0
		self.node_end[0] = -1
		for i in range(self.node_count):
			label = self.Text[self.node_start[i]:self.node_end[i] + 1]
			if maxLabelLength:
				label = label[:maxLabelLength]
			D.node(str(i), label)
		for tail in self.G:
			for head in self.G[tail]:
				D.edge(str(tail), str(head))
		D.render(outFile, view=True)

	def report(self):
		print(self.G, self.H, self.node_start, self.node_end, self.suffix_start, self.BWT, self.suffixArray, self.first_occurrence, self.Count)

	def appendNode(self, parent, nodeStringStart, suffixStart):
		newNode = self.node_count
		self.G[parent] = self.G.get(parent, []) + [newNode]
		self.H[newNode] = parent
		self.node_start[newNode] = nodeStringStart
		self.node_end[newNode] = len(self.Text) - 1
		self.suffix_start[newNode] = suffixStart
		self.node_count += 1

	def splitNode(self, node, index):
		# introduce a new node whose parent is the original parent of node, make it the new parent of node
		newNode = self.node_count
		parent = self.H[node]
		self.G[newNode] = [node]
		self.G[parent].remove(node)
		self.G[parent] = self.G.get(parent, []) + [newNode]
		self.H[newNode] = parent
		self.H[node] = newNode
		self.node_start[newNode] = self.node_start[node]
		self.node_end[newNode] = index - 1
		self.node_start[node] = index
		self.node_count += 1
		return newNode

	def findMatchingChild(self, node, loc):
		for child in self.G[node]:
			if self.Text[loc] == self.Text[self.node_start[child]]:
				return child
		return -1

	def firstMismatch(self, node, ix):
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
		'''
		look for a node that matches the start of the current substring
		if none found, create a new node and set its string to the current substring and SS to the initial index
		if one is found, look for a mismatch within the string
		if a mismatch is found, split the target node and append the remainder of the substring
		if no mismatch, advance curIx by the length of the node string and iterate
		'''
		node = 0
		curIx = ix
		while True:
			nextNode = self.findMatchingChild(node, curIx)
			if nextNode == -1:
				self.appendNode(node, curIx, ix)
				break
			node = nextNode
			splitLoc = self.firstMismatch(node, curIx)
			if splitLoc == -1:
				curIx += self.node_end[node] - self.node_start[node] + 1
				continue
			newNode = self.splitNode(node, splitLoc)
			self.appendNode(newNode, splitLoc + (curIx - self.node_start[newNode]), ix)
			c = self.node_count - 1
			break

	def compute_count_array(self):
		for i in self.alphabet:
			self.Count[i] = [0] * (len(self.Text) + 1)  # check does this cause any reference issues?
		for j in range(1, len(self.BWT) + 1):
			self.Count[self.BWT[j - 1]][j] = self.Count[self.BWT[j - 1]][j - 1] + 1
			for k in self.alphabet:
				if k != self.BWT[j - 1]:
					self.Count[k][j] = self.Count[k][j - 1]
		return (self.Count)

	def FindCount(self, Pattern):
		top = 0
		bottom = len(self.BWT) - 1
		while top <= bottom:
			if len(Pattern) > 0:
				symbol = Pattern[-1]
				Pattern = Pattern[:-1]
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
	# Text = 'GGCGCCGCTAGTCACACACGCCGTA$'
	# Text = 'GGCGCCGCTAGTCACACACGCCGTA'
	# BWI = BWIndex(Text)
	# BWI = BWIndex()
	# genomefile = 'genome.txt'
	# genomefile = 'refgenome.txt'
	# BWI = BWIndex(genomefile=genomefile)
	# BWI.report()
	# BWI.drawGraph()
	# BWI.exportIndex("e_coli_index.txt", SA_gap=5, C_gap=5)
	# BWI.exportIndex("test_index_new.txt", SA_gap=5, C_gap=5)

	# start_time = time.time()
	# f = open("refgenome.txt")
	# T = f.readline().strip() + '$'
	# B = BWT(T)
	# B.buildTree()
	# B.exportIndex("ecoli_index.txt", C_gap = 5, SA_gap = 5)
	# print("Exported index in", time.time() - start_time)

	parser = argparse.ArgumentParser()
	genome_source = parser.add_mutually_exclusive_group()
	genome_source.add_argument('--genomefile', help='File containing text of genome all on one line')
	genome_source.add_argument('--genome', help='Genome in string form, terminated by $')
	parser.add_argument('--countgap', help='gap between elements of count array', type=int)
	parser.add_argument('--suffixgap', help='gap between elements of suffix array', type=int)
	parser.add_argument('indexfile', help='File to write the index to')

	args = parser.parse_args()
	if args.genome:
		BWI = BWIndex(genome=args.genome)
	elif args.genomefile:
		BWI = BWIndex(genomefile=args.genomefile)
	BWI.export_index(args.indexfile, count_array_gap=args.countgap, suffix_array_gap=args.suffixgap)
