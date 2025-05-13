#awsinsights_for_developers

This blog is about making the AWS cloud-watch insights available for developers. It is achieved by creating a single page server less web application were developers can query the logs.  I will also discuss how our application logs in containers or VMs are pushed to AWS cloudwatch.
Why?

1. Easiness and convenience for developers
2. Restricted access to developers.
Application logs to AWS cloudwatch

Reference AWS Documentation   
      
Step 1: Create an IAM Role and attach it to the EC2 instances
             To create IAM Role, Navigate to IAM -> Roles -> Create Role -> Select AWS Service and EC2 -> Next Permissions -> Create Policy-> JSON -> provide the below json -> Review Policy -> Provide name, description -> Create Policy -> Refresh policy list to get newly create policy in role creation page -> search the policy with name and select it -> Next: Tags ->Next: Review -> Provide name and description -> Create Role
            Get the IAM policy script in this link: iampolicyscript_runcommand.json

            To attach IAM role, navigate to AWS Ec2 -> Instances -> select the instance-> Actions -> Instance settings -> Attach/Replace IAM Role -> Select IAM role and click Apply

Step 2: Install cloudwatch agent in AWS EC2
            Use AWS Run command to install the agent. For that navigate to AWS Ec2 -> Systems Manager Services -> Run Command
Provide command as AWS-ConfigureAWSPackage , AWS Ec2 instances, action as Install, Name as AmazonCloudWatchAgent, Version as latest and run


Step 3:  Create cloudwatch log group
              Navigate to AWS cloudwatch -> Logs-> Actions -> Create Log Group
              Provide log group name and click create log group button to create a new log group

Step 4: Create cloudwatch agent configuration and store it in parameter store
             Note: We are using windows instance to host our windows containers. The same config wizard can be used to create configuration file for windows and linux instances
             Login to the EC2 instance. Run 'amazon-cloudwatch-agent-config-wizard.exe'. Follow the wizard and provide the details
             At last the wizard will ask for storing the config in SSM parameter store. Provide the details to store the application in parameter store. Or copy the config.json manually and create the parameter in AWS. For that Navigate to AWS Ec2 -> Systems Manager Shared Resources -> Parameter store- > create Parameter. Provide the name, description, type as string and copy the config.json in value and click on create parameter

            Sample config.json

Step 5: Create application containers
             While create the application container share the application log folder with docker host folder

              docker run -d -v C:\API\Logs\ApiLog.log:c:\api\ApiLog.log applicationimage

Step 6: Configure cloudwatch agent
             To configure cloudwatch agent run the cloudwatch agent command with cloudwatch agent configuration json in parameter json as parameter
              Navigate to AWS Ec2 -> Systems Manager Services -> Run Command -> Provide below details and click run
              Optional Configuration Location is the parameter name of cloudwatch agent config json in the AWS parameters store




              After few minutes the logs will be available in log groups. As per our configuration json two log streams will be created in the log groups.




Step 7: Create the server less application
             The server less application is having three components,
              a) Lambda function
              b) API
              c) Web application

             AWS lambda will be the backend of the api created via AWS api gateway. It will get the logs from AWS cloudwatch insights.

             To create the AWS lambda, Navigate to Lamda -> Create function -> provide name and select the Runtime as Python 2.7 and click create function button.            
              Get the lambda code from this link
              Upload the source code and attach a IAM role with 'CloudWatchLogsFullAccess' policy.

              lambda_function.py is the lambda function. Based on the http_method the lambda function identifies the request type and provide the output accordingly. If it is a get request, it accepts a query id and pulls the logs from cloudwatch insights and return it. Whereas, for a post request, it accepts parameters such as query, start-time, end-time, log-group and it will request an insights query. The generated query id will be returned back with the response.

              To create API, navigate to API gateway -> create API -> provide name -> Click create API button. Then create a resource named 'getlogs' and create a get and post method in it. Choose the above created lambda function as the integration type for both the methods. Mapping templates are needed for both methods for mapping the incoming request from a front-end to the format that lambda accepts. 
              Provide the following json in Mapping template section in Integration Requests.
              a) Get Method
                            {
                                   "http_method": "$context.httpMethod",
                                   "queryid": "$input.params().querystring.get('queryid')",
                                   "region": "$input.params().querystring.get('region')"
                             }
              b) POST Method
                            {
                                   "http_method": "$context.httpMethod",
                                   "body" : $input.json('$') 
                             }

               Enable CORS for the resource
               To restrict the API with IP address provide the following rule in the Resource Policy.
                   {
                         "Version": "2012-10-17",
                         "Statement": [
                         {
                              "Effect": "Allow",
                              "Principal": "*",
                              "Action": "execute-api:Invoke",
                              "Resource": "<arn_of_the_api>/*",
                              "Condition": {
                                   "IpAddress": {
                                       "aws:SourceIp": [
                                            "<your_ipaddress>/32",
                                            "<your_ipaddress>/32"
                                        ]
                                    }
                               }
                           }
                           ]
                    }
              Deploy the api resource and get the url. This url should be added in the html page.
              The front end web application is a single HTML page using AngularJS. Create a S3 and upload the html in it. Get the html file from this link
               Enable static webhosting in the s3 properties tab. Get the endpoint and access the webpage in a browser.
               Restrict the webpage with IP address using the below bucket policy.
                  {
                       "Version": "2012-10-17",
                       "Statement": [
                       {
                            "Sid": "IPAllow",
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:*",
                            "Resource": "<s3_arn>/*",
                            "Condition": {
                               "IpAddress": {
                                   "aws:SourceIp": [
                                         "<your_ipaddress>/32",
                                         "<your_ipaddress>/32"
                                     ]
                                 }
                              }
                          }
                        ]
                    }



