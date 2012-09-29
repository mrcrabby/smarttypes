
from optparse import OptionParser
import math

"""
given 2 points (one good and one bad) 
show how our objective function ranks 
various spots between good and bad points
"""


if __name__ == '__main__':

	parser = OptionParser()
	parser.add_option("-g", "--good", action="store", type="int", dest="good")
	parser.add_option("-b", "--bad", action="store", type="int", dest="bad")
	options, args = parser.parse_args()

	scores = []
	for x in range(20):
		good_dist = max(abs(options.good - x), 2)
		bad_dist = max(abs(options.bad - x), 2)
		score = float(math.log(good_dist)) / float(bad_dist)
		values = (score, x, good_dist, bad_dist)
		scores.append(values)

	for x in sorted(scores):
		print "Score: %s, Point: %s, Good dist: %s, Bad dist: %s" % x










