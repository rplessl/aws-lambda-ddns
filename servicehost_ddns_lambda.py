import boto3
import json
import os

class ServiceHostLambdaDDnsRoute53:
  def __init__(self, name):
    self.name = name

    self._client = None
    self._zone_id = None
    self.vpc = os.environ['VPC']

  def add_cname(self, name, target):
    self.modify_cname('UPSERT', name, target)

  def delete_cname(self, name, target):
    self.modify_cname('DELETE', name, target)

  def modify_cname(self, action, name, target):
    self.client().change_resource_record_sets(
        HostedZoneId=self.zone_id(),
        ChangeBatch={
          "Comment": "Updated by Lambda DDNS",
          "Changes": [
            {
              "Action": action,
              "ResourceRecordSet": {
                "Name": name + '.' + self.name,
                "Type": 'CNAME',
                "TTL": 60,
                "ResourceRecords": [
                  { "Value": target  },
                  ]
                }
              },
            ]
          }
        )

  def zone_id(self):
    if not self._zone_id:
      zones = self.client().list_hosted_zones()['HostedZones']
      zones = filter(lambda record: record['Name'] == self.name, zones)
      for zone in zones:
        zone_id = zone['Id'].split('/')[2]
        response = self.client().list_tags_for_resource(
          ResourceType='hostedzone',
          ResourceId=zone_id
        )
        tags = response['ResourceTagSet']['Tags']
        for tag in tags:
          if tag['Key'] == 'VPC':
            if tag['Value'] == self.vpc:
                self._zone_id = zone_id

    return self._zone_id

  def client(self):
    if not self._client:
      self._client = boto3.client('route53', region_name='eu-west-1')
    return self._client

class ServiceHostLambdaDDns:
  ZoneName = 'vpc.example.com.'

  def __init__(self, event, context):
    self.event = event
    self.context = context

    self.r53 = ServiceHostLambdaDDnsRoute53(ServiceHostLambdaDDns.ZoneName)

    if self._state() == 'running':
      ec2 = boto3.resource('ec2')

      instance = ec2.Instance(self.instance_id())

      target = instance.private_dns_name

      self.r53.add_cname('sh', target)
      self.r53.add_cname('*.sh', target)

  def _state(self):
    return self.event['detail']['state']

  def instance_id(self):
    return self.event['detail']['instance-id']

def lambda_handler(event, context):
  ServiceHostLambdaDDns(event, context)
