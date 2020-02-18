# How to migrate AWS Lambda Functions between AWS accounts
1. Sign in with the source AWS account
2. Export the Lambda Function SAM file through AWS Console > Lamda Function > Actions > Export function as pedestrian-counter-lambda-microservice.yaml
3. Sign in with the destination AWS account
4. Create a new Lambda Function and API Gateway with REST API and Open with API key)
5. Get the role arn through https://console.aws.amazon.com/iam/home?region=us-west-2#/roles 

`arn:aws:iam::XXXX:role/service-role/pedestrian-counter-role-XXXX`
6. Edit the YAML file to replace the new role arn (e.g. `arn:aws:iam::XXXX:role/service-role/pedestrian-counter-role-XXXX`)

7. Deploy the SAM file:
- Install AWS CLI
- Sign in AWS CLI with the destination AWS account keys:

`aws configure`

- Deploy the exported function YAML file:

`sam deploy --template-file ./pedestrian-counter-lambda-microservice.yaml  --stack-name pedestrian-counter --capabilities CAPABILITY_IAM`
