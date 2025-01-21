#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import NavSatFix

class publishGPS(object):

	def __init__(self):
		rospy.loginfo("Initialising GPS publishing")
		self.lastMsg=None
		self.gps_pub=rospy.Publisher('/gps_new', NavSatFix, queue_size=1)
		rospy.sleep(8)
		rospy.loginfo("initialised")

	def do_work(self):
		gpsmsg=NavSatFix()
		gpsmsg.header.stamp = rospy.Time.now()
		gpsmsg.header.frame_id = "gps"
		rospy.loginfo('test')
		gpsmsg.latitude=47.01
		gpsmsg.longitude=10.01
		self.gps_pub.publish(gpsmsg)

	def run(self):
		r=rospy.Rate(1)
		while not rospy.is_shutdown():
			self.do_work()
			r.sleep()

if __name__=='__main__':
	rospy.init_node('pubgps')
	obj=publishGPS()
	obj.run()