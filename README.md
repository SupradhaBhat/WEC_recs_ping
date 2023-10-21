# WEC_recs_ping
This is the python implementation of the PING command using ICMP sockets

running instructions : python script_name.py --target-host host_name.com
Example:               python ping.py --target-host www.google.com

![image](https://github.com/SupradhaBhat/WEC_recs_ping/assets/97398229/369fee72-c97b-446b-b8b8-8f40cc49fff9)

RTT is a measure of the time it takes for an ICMP echo request packet to travel from the source to the destination and then for the corresponding echo response packet to travel back from the destination to the source. It accounts for the complete round trip of the packet.It is double the delay. RTT is the more commonly used metric in ICMP echo request-response cycles and is often used to evaluate network performance.
Packet loss is is a critical metric for assessing network reliability and quality, often measured as a percentage, reflecting the ratio of lost packets to the total sent. 
packet_loss = ((sent_pings - received_pings) / sent_pings) * 100
