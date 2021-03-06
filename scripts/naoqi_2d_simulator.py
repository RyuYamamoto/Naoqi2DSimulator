# -*- coding: utf-8 -*-
import sys
import os
import argparse
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
    def __init__(self, ip, port):
        self.r = 0.2
        self.vel = np.array([0,0,0])

        self.robot_pos_x_list = []
        self.robot_pos_y_list = []

        self.fig = plt.figure()
        self.ax = plt.axes()

        self.server = SocketServer(ip, port)
        self.server_thread = threading.Thread(target=self.server.update, name="server_thread")
        self.server_thread.start()

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
        self.draw_trajectory(pose)

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

    def draw_trajectory(self, robot_pos):
        x, y, _ = robot_pos
        self.robot_pos_x_list.append(x)
        self.robot_pos_y_list.append(y)
        self.ax.scatter(self.robot_pos_x_list,
                        self.robot_pos_y_list, s=1, color="blue", label="trajectory")
        self.ax.legend()
        
    def set_velocity(self, vel):
        self.vel = vel

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
        pose = np.array([0,0,0])
        self.set_velocity(np.array([0,0,0]))
        target_velocity = np.array([0.0,0,0])

        while True:
            self.config_screen()
            get_target_velocity = self.server.get_target_value()
            if get_target_velocity is not None:
                target_velocity = get_target_velocity
            pose = self.control(pose, self.pid_velocity_control(target_velocity))
            self.move_robot(pose)
            plt.pause(DT)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='2d simulator for naoqi service.')

    parser.add_argument('--ip', help='server ip address', default='127.0.0.1')
    parser.add_argument('--port', help='server port number', type=int, default=9559)

    args = parser.parse_args()

    sim = Naoqi2DSimulator(args.ip, args.port)
    sim.run()
