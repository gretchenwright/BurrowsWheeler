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
from BetterBWMatch import BetterBWMatch
import re

class BWT:
	def __init__(self, T):
		self.T = T
	def buildTree(self):
		self.G = {0: []} # parent to child, int -> list
		self.H = dict() # child to parent, int -> int
		self.nodeCount = 1
		self.NS = dict() # node start index
		self.NE = dict() # node end index
		self.SS = dict() # suffix start index
		for ix in range(len(T)):
			self.threadSuffix(ix)
			
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
		
			
	def exportIndex(self, filename, SA_gap = None, C_gap = None):
		g = open(filename, 'w')
		self.Solve()
		M = BetterBWMatch(self.T, self.BWT)
		self.C = M.computeCountArray()
		self.FO = M.FirstOccurrence
		self.SA_gap = SA_gap
		self.C_gap = C_gap
		g.write(self.BWT + '\n')
		g.write(','.join(str(i) + ';' + str(s) for i, s in enumerate(self.suffixArray) if s % SA_gap == 0) + '\n')
		g.write(','.join(str(x) for x in sorted(self.C.keys())) + '\n')
		for x in sorted(self.C.keys()):
			g.write(','.join(str(self.C[x][i]) for i in range(len(self.C[x])) if i % C_gap == 0) + '\n')
		g.write(','.join(str(self.FO[x]) for x in sorted(self.FO.keys())) + '\n')
		g.write(str(SA_gap) + '\n')
		g.write(str(C_gap) + '\n')
	
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
		self.BWT =  transform 
		self.suffixArray = suffixArray
		
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
	# start_time = time.time()
	# f = open("refgenome.txt")
	# T = f.readline().strip() + '$'
	# B = BWT(T)
	# B.buildTree()
	# B.exportIndex("ecoli_index.txt", C_gap = 5, SA_gap = 5)
	# print("Exported index in", time.time() - start_time)
	
	# T = 'abracadabra$'
	
	# B = BWT(T)
	# B.buildTree()
	# B.exportIndex("magic_index_gap.txt", C_gap = 5, SA_gap = 5)
	
	# B = BWT(T)
	# B.loadIndex("magic_index_gap.txt")
	# print(B.SA_gap, B.C_gap)
	# print(B.BWT, B.suffixArray, B.C, B.FO)
	# print(B.FindMatches('abra'))
	
	# C_recon = {}
	# C_gap = 5
	# for k in B.C.keys():
	# # for k in  ['$']:
		# C_recon[k] = []
		# for i in range(len(B.BWT)):
			# C_recon[k].append(reconstructCount(B.BWT, B.suffixArray, B.C, B.FO, k, i, C_gap))
	# f = open("C_recon.txt", "w")
	# for x in sorted(C_recon.keys()):
	# # for x in ['$']:
		# f.write(','.join(str(C_recon[x][i]) for i in range(len(C_recon[x]))) + '\n')
	# # print(BWT, suffixArray, C, FO)
	
	start_time = time.time()
	T = 'dummy' # remove need for this later
	B = BWT(T)
	B.loadIndex("ecoli_index.txt")
	print("Loaded index in", time.time() - start_time)
		
		
	start_time = time.time()
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
				match = B.FindMatches(readValue)
				if not match:
					revcomp = reverseComplement(readValue)
					match = B.FindMatches(revcomp)
				if match:
					g.write(readName + '\t')
					result = '\t'.join(str(m) for m in match)
					g.write(result + '\n') 
	print("Complete read matching in", time.time() - start_time)

			
	
	
	
	# print("Loaded index after", time.time() - start_time)
	# start_time = time.time()
	# pattern = 'AGGTGATGGTATGCGCACCTTACGTGGGATCTCGGCGAAATTCTTTGCCGCGCTGGCCCGCGCCAATATC'
	# print(FindMatches(suffixArray, C, FO, pattern))
	# print("Completed matching after", time.time() - start_time)
		
	# B.drawGraph()
	