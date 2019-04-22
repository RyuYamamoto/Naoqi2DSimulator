import socket
import parser
import sys

if __name__ == "__main__":
    ip = '127.0.0.1'
    if(len(sys.argv)) < 4:
        print("arg is few...")
    #target = "{},{},{}".format(sys.argv[1], sys.argv[2], sys.argv[3])
    target = sys.argv[1] + "," + sys.argv[2] + "," + sys.argv[3]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 50007))
    s.send(target.encode())

