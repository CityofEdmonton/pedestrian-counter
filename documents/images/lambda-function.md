# How to migrate AWS Lambda Functions between AWS accounts
1. Export Lambda Function through AWS Console > Lamda Function > Actions > Export function as pedestrian-counter-lambda-microservice.yaml
2. Install AWS CLI
3. Sign in AWS CLI with credential

`aws configure`

4. Deploy the exported function YAML file:

`sam deploy --template-file ./pedestrian-counter-lambda-microservice.yaml  --stack-name mystack --capabilities CAPABILITY_IAM`
