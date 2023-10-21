import os
import argparse
import socket
import struct
import select
import time

ICMP_ECHO_REQUEST = 8  # ICMP type number for echo request
TIME_OUT = 2
NUMBER_OF_PINGS = 4

universal = 0  # Add this variable to keep track of the sum of RTTs
maxi = 0
minimum = 100000000000
sent_pings = 0
received_pings = 0


class Pinger(object):
    # Send a ping to some host using an ICMP echo request
    def __init__(self, target_host, count=NUMBER_OF_PINGS, timeout=TIME_OUT):
        # Initialize values of target_host, count, and timeout
        self.target_host = target_host
        self.count = count
        self.timeout = timeout

    # ... (Rest of your code remains the same)

    def chksum(self, input_string):
        sum = 0 
        max_count = (len(input_string)/2)*2 #Length of our checksum string
        count = 0
        while count < max_count: #loop through checksum string

            val = input_string[count + 1]*256 + input_string[count]        

            sum = sum + val
            sum = sum & 0xffffffff 
            count = count + 2
     
        if max_count<len(input_string): #If our source string is larger than our max string length...
            sum = sum + ord(input_string[len(input_string) - 1])
            sum = sum & 0xffffffff 
     
        sum = (sum >> 16)  +  (sum & 0xffff)
        sum = sum + (sum >> 16)
        answer = ~sum
        answer = answer & 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer
 
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
     
     
    def send_ping(self, sock,  ID):
        """
        Here we create a dummy ICMP packet and attaching it to the IP header. 
        """
        target_addr  =  socket.gethostbyname(self.target_host) # set address variable to target address.
     
        my_checksum = 0 #Create a dummy checksum with value zero.
     
        # Create a dummy header with a zero checksum.
        header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
        bytes_In_double = struct.calcsize("d")
        data = (192 - bytes_In_double) * "Q"
        data = struct.pack("d", time.time()) + bytes(data.encode())
     
        # Get the checksum on the data and the dummy header.
        my_checksum = self.chksum(header + data)
        header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1)
        
        #add the data from above to the header to create a complete packet
        packet = header + data
        #send the packet to the target address
        sock.sendto(packet, (target_addr, 1))
     
     
    def ping_once(self):
        """
        Returns the delay (in seconds) or none on timeout.
        """
        icmp = socket.getprotobyname("icmp")
        try:
        #add the ipv4 socket (same as we did in our first project, SOCK_RAW(to bypass some of the TCP/IP handling by your OS) and the ICMP packet
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        except socket.error as e:
            if e.errno == 1:
                # print a messege if not run by superuser/admin, so operation is not permitted
                e.msg +=  "Not permitted. User is not superuser/admin."
                raise socket.error(e.msg)
        except Exception as e:
            #print the errror messege    
            print ("Exception: %s" %(e.msg))
    
        my_ID = os.getpid() & 0xFFFF
        
        #Call the definition from send.ping above and send to the socket you created above
        self.send_ping(sock , my_ID)
        delay = self.receive_response(sock, my_ID, self.timeout)
        sock.close()
        return delay

    def ping(self):
        """
        It iterates for the specified number of pings (default: 4), sending pings and printing the results.
        """
        global universal  # Access the global variable
        global maxi
        global minimum
        global sent_pings
        global received_pings

        for i in range(self.count):
            print("Ping to %s..." % self.target_host, )
            try:
                sent_pings += 1
                delay = self.ping_once()
                if delay is not None:
                    received_pings += 1
            except socket.gaierror as e:
                print("Ping failed. (socket error: '%s')" % e[1])
                break

            if delay == None:
                print("Ping failed. (timeout within %s sec.)" % self.timeout)
            else:
                delay = delay * 1000
                print("Delay is : %0.4f ms" % delay)
                print("RTT is : %0.4f ms" % (delay * 2))

                universal += delay  # Add the delay to the sum
                maxi=max(maxi,delay)
                minimum=min(minimum,delay)

        if self.count > 0:
            average_rtt = universal / self.count  # Calculate the average RTT
            print(f"The average RTT is : {average_rtt}")
        if sent_pings > 0:
            packet_loss = ((sent_pings - received_pings) / sent_pings) * 100
            print(f"Packet Loss: {packet_loss:.2f}%")
        if self.count > 0:
            maxi=max(maxi,delay)
            print(f"The maximum RTT is : {maxi*2}")
        if self.count > 0:
            minimum=min(minimum,delay)
            print(f"The minimum RTT is : {minimum*2}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Custom python ping command using ICMP sockets')
    parser.add_argument('--target-host', action="store", dest="target_host", required=True)
    given_args = parser.parse_args()
    target_host = given_args.target_host
    pinger = Pinger(target_host=target_host)
    pinger.ping()
