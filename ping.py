import os 
import argparse 
import socket
import struct
import select
import time

ICMP_ECHO_REQUEST = 8 #ICMP type number for echo request
TIME_OUT = 2
NUMBER_OF_PINGS = 4 

class Pinger(object):
    #Send a ping to some host using an ICMP echo request
    def __init__(self, target_host, count=NUMBER_OF_PINGS, timeout=TIME_OUT):
	#Initilize values of target_host, count, and timeout
        self.target_host = target_host
        self.count = count
        self.timeout = timeout
 
    def receive_response(self, sock, ID, time_out):
        """
        This is to create a socket on our side so we can receive the replies from the destination host.
        Also we should not wait more than a specified time called “TIMEOUT”.
        """
        time_left = time_out
        while True:
            start_time = time.time() #Start time is the time at which ping was sent
            readable = select.select([sock], [], [], time_left) 
            time_spent = (time.time() - start_time) #Time spent waiting for response.
            if readable[0] == []: #Timeout occurs if readable is 0 
                return
     
            time_received = time.time() #Time we recieved our response
            recv_packet, addr = sock.recvfrom(1024) 
            icmp_header = recv_packet[20:28] 
            #bbHHh is a format string and lets us know the expected format and layout of data when unpacking.
            #In this case, we have: signed char, signed char, unsigned short, unsigned short, and short
            #data types.
            type, code, checksum, packet_ID, sequence = struct.unpack(
                "bbHHh", icmp_header
            )
            if packet_ID == ID:
                bytes_In_double = struct.calcsize("d")
                time_sent = struct.unpack("d", recv_packet[28:28 + bytes_In_double])[0]
                return time_received - time_sent
     
            time_left = time_left - time_spent
            if time_left <= 0:
                return
            
    #ping_once - function to ping once
    #receive_response - function to get the delay and inturn the RTT
     
     
    def ping(self):
        """
        It iterates for the specified number of pings (default: 4), sending pings and printing the results.
        """
        for i in range(self.count):
            print ("Ping to %s..." % self.target_host,)
            try:
                delay  =  self.ping_once()
            except socket.gaierror as e:
                print ("Ping failed. (socket error: '%s')" % e[1])
                break
     
            if delay  ==  None:
                print ("Ping failed. (timeout within %ssec.)" % self.timeout)
            else:
                delay  =  delay * 1000
                print ("Delay is : %0.4fms" % delay)
                print ("RTT is : %0.4fms" % (delay*2))

 
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Custom python ping command using ICMP sockets')
    parser.add_argument('--target-host', action="store", dest="target_host", required=True)
    given_args = parser.parse_args()  
    target_host = given_args.target_host
    pinger = Pinger(target_host=target_host)
    pinger.ping()
