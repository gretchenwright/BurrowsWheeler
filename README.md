# BurrowsWheeler

This code implements the Burrows-Wheeler algorithm for efficiently aligning DNA reads to a reference genome. It constructs the Burrows-Wheeler transform and the suffix array by means of a suffix tree. Optionally, it has the ability to visualize the suffix tree. 

To use it, first run BWIndex to create the FM index, which consists of the BW transform, the suffix array and an auxiliary array known as the count array. To save space, the suffix array and count arrays are stored with gaps, whose length can be specified via command line parameters.

Once the index is created, use it to align reads by calling BWMatch.

Command line options and examples for index creation:
-----------------------------------------------------

usage: BWIndex.py [-h] [--genomefile GENOMEFILE | --genome GENOME]
                  [--countgap COUNTGAP] [--suffixgap SUFFIXGAP]
                  indexfile

Create an index from a string supplied on the command line:<br/>
py BWIndex.py --genome ACGCGCTAA$ test_index.txt --countgap 5 --suffixgap 5

Create an index from a genome file:<br/>
py BWIndex.py --genomefile genome.txt test_index.txt --countgap 5 --suffixgap 5

Create an index from a genome file with gaps of 100:<br/>
py BWIndex.py --genomefile refgenome.txt --countgap 100 --suffixgap 100 e_coli_index_100.txt

Command line options and examples for pattern matching:
-------------------------------------------------------

usage: BWMatch.py [-h]
                  [--patternstring PATTERNSTRING | --patternfile PATTERNFILE]
                  [--outputfile OUTPUTFILE]
                  indexfile

Match a single string to the genome corresponding to the index file::<br/>
py BWMatch.py --patternstring GCG test_index.txt

Match the reads from an input file to the given index file, and write the result to the given output file:<br/>
py BWMatch.py --patternfile e_coli_1000.fa --outputfile e_coli_matches.txt e_coli_index.txt
