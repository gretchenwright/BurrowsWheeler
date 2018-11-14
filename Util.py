import winsound

def GetFirstRealLine(f):
	s = f.readline().strip()
	if s.replace(':', '') == 'Input':
		s = f.readline().strip()
	return s
	
def BeepWhenDone():
	duration = 1000  # millisecond
	freq = 440  # Hz
	winsound.Beep(freq, duration)
	
def LoadMass():
	massTable = dict()
	f = open("integer_mass_table.txt")
	for line in f:
		x, y = line.strip().split()
		massTable[x] = int(y)
	return massTable
	
def HamDist(a, b):
	if len(a) != len(b):
		print("Error: strings must be the same length.")
		return
	count = 0
	for i in range(0, len(a)):
		if a[i] != b[i]:
			count += 1
	return count
	
# # example of timing
# import time 
# start_time = time.time()
# # your code
# elapsed_time = time.time() - start_time