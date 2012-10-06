
from optparse import OptionParser
import numpy as np

"""
given 3 cartesian points (good, bad, me) prove that we can:

  + id the best goal point
    - equals goal_to_good_dist
	- on the same line as good and bad
	- (goal to bad distance) > (good to bad distance)

  + id my movement (some step towards our goal point)

"""

if __name__ == '__main__':

	goal_to_good_dist = 0.25
	good = np.array((1.2, 1.1))
	bad = np.array((-4.4, -3.7))
	me = np.array((7.4, -3.3))

	good_to_bad_diff = good - bad 
	good_to_bad_dist = np.linalg.norm(good_to_bad_diff)
	good_to_bad_x_ratio = good_to_bad_diff[0] / good_to_bad_dist 
	good_to_bad_y_ratio = good_to_bad_diff[1] / good_to_bad_dist 

	goal_to_bad_dist = good_to_bad_dist + goal_to_good_dist
	goal_to_bad_x_dist = goal_to_bad_dist * good_to_bad_x_ratio
	goal_to_bad_y_dist = goal_to_bad_dist * good_to_bad_y_ratio
	goal_x = good[0] + (goal_to_bad_x_dist - good_to_bad_diff[0])
	goal_y = good[1] + (goal_to_bad_y_dist - good_to_bad_diff[1])
	goal = np.array((goal_x, goal_y))

	assert np.linalg.norm(goal-bad) == goal_to_bad_dist, \
		"""
This thing doest work.
 - np.linalg.norm(goal-bad): %s
 - goal_to_bad_dist: %s
 - good: %s
 - bad: %s
 - goal: %s
 - good_to_bad_x_ratio: %s
 - good_to_bad_y_ratio: %s
		""" % (np.linalg.norm(goal-bad), goal_to_bad_dist, 
			good, bad, goal, good_to_bad_x_ratio, good_to_bad_y_ratio)


	new_x = (goal[0] + me[0]) * 0.25
	new_y = (goal[1] + me[1]) * 0.25
	new_spot = np.array((new_x, new_y))
	print "bad: %s" % bad
	print "good: %s" % good
	print "goal: %s" % goal
	print "me: %s" % me
	print "new_spot: %s" % new_spot

