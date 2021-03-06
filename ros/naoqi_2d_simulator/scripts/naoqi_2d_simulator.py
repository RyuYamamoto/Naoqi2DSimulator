# -*- coding: utf-8 -*-
import rospy
from geometry_msgs.msg import Twist
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import math
import numpy as np
from numpy.random import *
from scipy.interpolate import interpolate
from socket_server import *
import threading

DT = 0.01
Kp = 3.5

class Naoqi2DSimulator:
    def __init__(self):
        self.r = 0.2
        self.vel = np.array([0,0,0])
        self.target_velocity = np.array([0,0,0])

        self.fig = plt.figure()
        self.ax = plt.axes()
 
        self._cmdvel_sub = rospy.Subscriber('/cmd_vel', Twist, self.cmdvel_callback, queue_size=1)

    def config_screen(self):
        self.ax.cla()
        self.ax.axis("equal")
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-5, 5)
        self.ax.set_xlabel("X [m]", fontsize=20)
        self.ax.set_ylabel("Y [m]", fontsize=20)

    def move_robot(self, pose):
        x, y, theta = pose

        self.draw_coordinate(pose)

        xn = x + self.r * math.cos(theta)
        yn = y + self.r * math.sin(theta)
        self.ax.plot([x, xn], [y, yn], color="black")
        c = patches.Circle(xy=(x, y), radius=self.r, fill=False, color="black")
        self.ax.add_patch(c)
    
    def draw_coordinate(self, pose):
        x, y, theta = pose
        ux = 0.3 * math.cos(theta)
        vx = 0.3 * math.sin(theta)
        self.ax.quiver(x, y, ux, vx, angles='xy',
                       scale_units='xy', alpha=0.3, width=0.003, scale=1)
        self.ax.annotate("x", xy=(x+ux, y+vx))

        uy = - 0.3 * math.sin(theta)
        vy = 0.3 * math.cos(theta)
        self.ax.quiver(x, y, uy, vy, angles='xy',
                       scale_units='xy', alpha=0.3, width=0.003, scale=1)
        self.ax.annotate("y", xy=(x + uy, y + vy))
        
    def cmdvel_callback(self, cmdvel_msg):
        self.target_velocity[0] = float(cmdvel_msg.linear.x)
        self.target_velocity[1] = float(cmdvel_msg.linear.y)
        self.target_velocity[2] = float(cmdvel_msg.angular.z)

        rospy.loginfo('cmd_vel is [{}, {}, {}]'.format(self.target_velocity[0], self.target_velocity[1], self.target_velocity[2]))

    def pid_velocity_control(self, t_v):
        return Kp * (t_v - self.vel)

    def control(self, pose, p_vel):
        x, y, theta = pose

        x = x + self.vel[0] * DT
        y = y + self.vel[1] * DT
        theta = theta + self.vel[2] * DT

        self.vel = self.vel + p_vel * DT

        return [x, y, theta]

    def run(self):
        self.server = SocketServer('127.0.0.1', 50007)
        self.display_thread = threading.Thread(target=self.run_main_thread, name='display_thread')

        self.display_thread.start()
    
    def run_main_thread(self):
        pose = np.array([0,0,0])

        while True:
            self.config_screen()
            pose = self.control(pose, self.pid_velocity_control(self.target_velocity))
            self.move_robot(pose)
            plt.pause(DT)

