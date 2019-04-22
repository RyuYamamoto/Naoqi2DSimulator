import rospy
from naoqi_2d_simulator import *

if __name__ == '__main__':
    rospy.init_node("naoqi_2d_simulator_node")
    sim = Naoqi2DSimulator()
    sim.run_main_thread()
    rospy.spin()
