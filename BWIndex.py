# Code Challenge: Implement BetterBWMatching.
     # Input: A string BWT(Text) followed by a collection of strings Patterns.
     # Output: A list of integers, where the i-th integer corresponds to the number of substring matches of the i-th member of Patterns
     # in Text.
	 
from Util import GetFirstRealLine

class BetterBWMatch():
	def __init__(self, Text, BWText):
		self.Text = Text
		self.LastColumn = BWText
		self.Count = dict()
		# alphabet = ['$', 'A', 'C', 'G', 'T']
		# old way may cause problems if the input uses a different alphabet, so make more robust:
		self.letters = {i for i in self.LastColumn}
		self.alphabet = [i for i in self.letters]
		self.alphabet.sort()
		self.computeCountArray()

		self.FirstOccurrence = dict()
		freq = dict()
		for i in self.LastColumn:
			freq[i] = freq.get(i, 0) + 1
		index = 0
		self.FirstOccurrence['$'] = 0
		for j in range(1, len(self.alphabet)):
			prevLetter = self.alphabet[j - 1]
			letter = self.alphabet[j]
			index += freq[prevLetter]
			self.FirstOccurrence[letter] = index
		# print(self.FirstOccurrence)
	def computeCountArray(self):
		for i in self.alphabet: 
			self.Count[i] = [0] * (len(self.Text) + 1)# check does this cause any reference issues?
		for j in range(1, len(self.LastColumn) + 1):
			self.Count[self.LastColumn[j - 1]][j] = self.Count[self.LastColumn[j - 1]][j - 1] + 1
			for k in self.alphabet:
				if k != self.LastColumn[j - 1]:
					self.Count[k][j] = self.Count[k][j - 1]
		return(self.Count)
	
	def FindCount(self, Pattern):
		top = 0
		bottom = len(self.LastColumn) - 1
		while top <= bottom:
			if len(Pattern) > 0:
				symbol = Pattern[-1]
				Pattern = Pattern[:-1]
				if self.Count[symbol][bottom + 1] - self.Count[symbol][top] > 0:
					top = self.FirstOccurrence[symbol] + self.Count[symbol][top]
					bottom = self.FirstOccurrence[symbol] + self.Count[symbol][bottom + 1] - 1
				else:
					return 0
			else:
				return bottom - top + 1	 
	 
if __name__ == '__main__':
	Text = 'GGCGCCGC$TAGTCACACACGCCGTA'
	Patterns = 'ACC CCG CAG'.split()
	# f = open('rosalind_ba9m.txt')
	# Text = GetFirstRealLine(f).strip()
	# Patterns = f.readline().strip().split()
	BW = BetterBWMatch(Text)
	counts = []
	# for Pattern in Patterns:
		# counts.append(BW.FindCount(Pattern))
	# g = open("out.txt", "w")
	# g.write(' '.join([str(a) for a in counts]))
	print(' '.join([str(a) for a in counts]))
	
#out.txt accepted