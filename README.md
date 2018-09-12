# aws-lambda-ddns
DDNS Service using Lambda and private DNS Zone in VPC

## functionality
1. create a service host (sh.example.com) using EC2 instance and internal DHCP IP and internal CNAMEs
2. every reboot of this host the lambda function will be called by a SNS fan-in

## architecture diagram

## credits
Initial Code was developed by nine.ch
