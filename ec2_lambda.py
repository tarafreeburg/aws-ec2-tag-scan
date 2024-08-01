#import libraries
import boto3


#personalizable variables
topicarn = str()


#define clients + resources
sns_client = boto3.client('sns')
ec2_resource = boto3.resource('ec2', 'us-east-1')


#functions
def scan_resource():
    #definitions
    properTags = ["LockpathAppId", "LockpathAppName", "CostCenter", "BusinessUnitId", "Owner", "BackupTier", "BCPTier"]
    responses = dict()
    instances = ec2_resource.instances.all()
 
    #actual work
    for instance in instances:
        if instance.tags == {}:
            response = "No Tags Present"
        else:
            instance_tag_keys = [tag['Key'] for tag in instance.tags]
            missing_tags = [tag for tag in properTags if tag not in instance_tag_keys]
            if missing_tags:
                response = f"Improper Tagging. Missing: {', '.join(missing_tags)}"
            else:
                response = "Proper Tagging"
        responses.update({instance.instance_id: response})
    return responses


def sns_alert(msg):
    response = sns_client.publish(TopicArn=topicarn,Message=msg)
    print("Message published")
    return(response)


#lambda handler
def lambda_handler(event, context):
    account_id = context.invoked_function_arn.split(":")[4]
    responses = scan_resource()
    msgContent = str()

    for response in responses:
        if responses.get(response) != "Proper Tagging":
            msgContent += (str(f'{response}: {responses.get(response)}') + "\n")
    sns_alert(f"The following resources are mistagged within {account_id}\n\n{msgContent}")
    
    return responses