# WEC_recs_ping

Custom Python Ping Tool using ICMP
This Python script allows you to send ICMP echo requests (ping) to a target host and measure the Round-Trip Time (RTT) and packet loss. It is a simple implementation of a ping utility using raw sockets.

Features
Sends a specified number of ping requests (default: 4).
Calculates and displays the average RTT, maximum RTT, minimum RTT, and packet loss.
Works with both hostnames and IP addresses.
Handles ICMP packets and provides RTT measurement.
Displays RTT in milliseconds (ms).

Run the script using the following command:

python ping.py --target-host <hostname or IP>
Replace <hostname or IP> with the target host you want to ping.

The script will send the specified number of ping requests and display the results, including RTT statistics and packet loss.

Note
Ensure that you run the script with administrative privileges (superuser) to send ICMP echo requests, as raw sockets may require special permissions.

![image](https://github.com/SupradhaBhat/WEC_recs_ping/assets/97398229/369fee72-c97b-446b-b8b8-8f40cc49fff9)

RTT is a measure of the time it takes for an ICMP echo request packet to travel from the source to the destination and then for the corresponding echo response packet to travel back from the destination to the source. It accounts for the complete round trip of the packet.It is double the delay. RTT is the more commonly used metric in ICMP echo request-response cycles and is often used to evaluate network performance.
Packet loss is is a critical metric for assessing network reliability and quality, often measured as a percentage, reflecting the ratio of lost packets to the total sent. 
packet_loss = ((sent_pings - received_pings) / sent_pings) * 100
