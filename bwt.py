'''
Implement efficient algos from Pevzner & Compeau BWT chapter
Construct BWT from suffix tree
Suffix tree:all nodes are labeled with the start and end locations in T corresponding to their text string
Leaf nodes are additionally labeled with the index of where the suffix ending there originated in T
Then to find the BWT, we do a DFS where we always start by exploring the child node with the earlier character in the alphabet. And when we get to a leaf, we append T[i - 1] to the growing BWT.
GAME PLAN: 2 implementations

1. index everything by integers: separate dictionary for each piece of data
G gives the child nodes, NS, NE give the start and end locations of the node substrings, SS gives the suffix starting indices

2. Node is a class with attributes for: child nodes (a list), node substring start and end; suffix start
'''

from graphviz import Digraph
import time
from BetterBWMatch import BetterBWMatch
import re

class BWT:
	def __init__(self, T):
		self.T = T
		self.G = {0: []} # parent to child, int -> list
		self.H = dict() # child to parent, int -> int
		self.nodeCount = 1
		self.NS = dict() # node start index
		self.NE = dict() # node end index
		self.SS = dict() # suffix start index
		for ix in range(len(T)):
			self.threadSuffix(ix)
	def Solve(self):
		S = [('', 0)]
		transform = ''
		suffixArray = []
		while S:
			node = S.pop()
			nodeIx = node[1]
			if self.G.get(nodeIx) is not None:
				if self.G[nodeIx] != []:
					children = [(self.T[self.NS[child]], child) for child in self.G[nodeIx]] 
					children.sort(reverse=True)
					S += children
			else:
				transform += self.T[self.SS[nodeIx] - 1]
				suffixArray.append(self.SS[nodeIx])
		return transform, suffixArray
	def drawGraph(self, maxLabelLength = None, outFile = None):
		D = Digraph()
		self.NS[0] = 0
		self.NE[0] = -1
		for i in range(self.nodeCount):
			label = T[self.NS[i]:self.NE[i] + 1]
			if maxLabelLength:
				label = label[:maxLabelLength]
			D.node(str(i), label)
		for tail in self.G:
			for head in self.G[tail]:
				D.edge(str(tail), str(head))
		D.render(outFile, view = True)
		
	def report(self):
		print(self.G, self.H, self.NS, self.NE, self.SS)
	def appendNode(self, parent, nodeStringStart, suffixStart):
		newNode = self.nodeCount
		self.G[parent] = self.G.get(parent, []) + [newNode]
		self.H[newNode] = parent
		self.NS[newNode] = nodeStringStart
		self.NE[newNode] = len(self.T) - 1
		self.SS[newNode] = suffixStart
		self.nodeCount += 1
	def splitNode(self, node, index):
		# introduce a new node whose parent is the original parent of node, make it the new parent of node
		newNode = self.nodeCount
		parent = self.H[node]
		self.G[newNode] = [node]
		self.G[parent].remove(node)
		self.G[parent] = self.G.get(parent, []) + [newNode]
		self.H[newNode] = parent
		self.H[node] = newNode
		self.NS[newNode] = self.NS[node]
		self.NE[newNode] = index - 1
		self.NS[node] = index
		self.nodeCount += 1
		return newNode
	def findMatchingChild(self, node, loc):
		for child in self.G[node]:
			if self.T[loc] == self.T[self.NS[child]]: 
				return child
		return -1
	def firstMismatch(self, node, ix): 
		offset = 1
		while True:
			if ix + offset >= len(self.T):
				return self.NS[node] + offset
			if self.NS[node] + offset > self.NE[node]:
				return -1
			if self.T[self.NS[node] + offset] != self.T[ix + offset]:
				return self.NS[node] + offset
			offset += 1
	def threadSuffix(self, ix):
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
				curIx += self.NE[node] - self.NS[node] + 1
				continue
			newNode = self.splitNode(node, splitLoc)
			self.appendNode(newNode, splitLoc + (curIx - self.NS[newNode]), ix)
			c = self.nodeCount - 1
			break
			
def exportIndex(T, filename):
	g = open(filename, 'w')
	B = BWT(T)
	transform, suffixArray = B.Solve()
	M = BetterBWMatch(T, transform)
	C = M.computeCountArray()
	FO = M.FirstOccurrence
	g.write(','.join(str(x) for x in suffixArray) + '\n')
	g.write(','.join(str(x) for x in sorted(C.keys())) + '\n')
	for x in sorted(C.keys()):
		g.write(','.join(str(y) for y in C[x]) + '\n')
	g.write(','.join(str(FO[x]) for x in sorted(FO.keys())) + '\n')
	
def loadIndex(filename):
	f = open(filename)
	suffixArray = [int(x) for x in f.readline().strip().split(',')]
	alphabet = [x for x in f.readline().strip().split(',')]
	C = {}
	for a in alphabet:
		C[a] = [int(x) for x in f.readline().strip().split(',')]
	FO = {}
	FO_items = [int(x) for x in f.readline().strip().split(',')]
	for i, a in enumerate(alphabet):
		FO[a] = FO_items[i]
	return suffixArray, C, FO
	
def reverseComplement(read):
	rc = {'A':'T', 'T':'A', 'C':'G', 'G':'C'}
	resp = ''
	for i in read[::-1]:
		resp += rc[i]
	return resp
	
def FindMatches(suffixArray, C, FO, Pattern):
	top = 0
	bottom = len(suffixArray) - 1
	while top <= bottom:
		# print(top, bottom)
		if len(Pattern) > 0:
			symbol = Pattern[-1]
			Pattern = Pattern[:-1]
			if C[symbol][bottom + 1] - C[symbol][top] > 0:
				top = FO[symbol] + C[symbol][top]
				bottom = FO[symbol] + C[symbol][bottom + 1] - 1
			else:
				return []
		else:
			# return [a[1] for a in self.SA[top:bottom + 1]]
			# return [a[1] for a in suffixArray[top - 1:bottom]]
			return suffixArray[top:bottom + 1]
	
if __name__ == '__main__':
	# f = open("refgenome.txt")
	# T = f.readline().strip() + '$'
	# exportIndex(T, "ecoli_index.txt")
	
	# T = 'panamabananas$'
	# # exportIndex(T, "pb_index.txt")
	start_time = time.time()
	suffixArray, C, FO = loadIndex("ecoli_index.txt")
	g = open("ecoli_matches.txt", "w")
	with open('e_coli_1000.fa') as f:
		for line in f:
			line = line.strip()
			if line[0] == '>':
				readName = line
			else:
				readValue = line
				if re.search('N', readValue):
					continue
				match = FindMatches(suffixArray, C, FO, readValue)
				if not match:
					revcomp = reverseComplement(readValue)
					match = FindMatches(suffixArray, C, FO, revcomp)
				if match:
					g.write(readName + '\t')
					result = '\t'.join(str(m) for m in match)
					g.write(result + '\n') 
			
	
	
	
	# print("Loaded index after", time.time() - start_time)
	# start_time = time.time()
	# pattern = 'AGGTGATGGTATGCGCACCTTACGTGGGATCTCGGCGAAATTCTTTGCCGCGCTGGCCCGCGCCAATATC'
	# print(FindMatches(suffixArray, C, FO, pattern))
	# print("Completed matching after", time.time() - start_time)
		
	# B.drawGraph()
	