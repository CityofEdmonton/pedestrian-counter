## How to migrate AWS Lambda Functions between AWS accounts
### Export the Lambda Function deployment package .zip file
1. Sign in with the source AWS account
1. Enter Lambda Function Admin UI: Services > Lambda Function
1. Export the Lambda Function deployment package zip file: Services > Lamda Function > Actions > Export function > Download deployment package

### Import the Lambda Function deployment package .zip file
1. Sign in with the destination AWS account
1. Enter Lambda Function Admin UI: Services > Lambda Function
1. Create a Lambda Function: Create function
1. Create API Gateway with REST API and Open with API key): Lambda > Functions > pedestrain-counter > Desinger > Add trigger > API Gateway
1. Upload Function package zip file: Lambda > Functions > pedestrain-counter > Function code > Code entry type > Upload a .zip file
