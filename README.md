## Using AWS DevOps Tools to model and provision AWS Glue workflows

[Using AWS DevOps Tools to model and provision AWS Glue workflows](https://aws.amazon.com/blogs/devops/provision-codepipeline-glue-workflows).

This post provides a step-by-step guide on how to model and provision AWS Glue workflows utilizing a DevOps principle known as infrastructure as code (IaC) that emphasizes the use of templates, source control, and automation. The cloud resources in this solution are defined within AWS CloudFormation templates and provisioned with automation features provided by AWS CodePipeline and AWS CodeBuild. These AWS DevOps tools are flexible, interchangeable, and well suited for automating the deployment of AWS Glue workflows into different environments such as dev, test, and production, which typically reside in separate AWS accounts and Regions.

AWS Glue workflows allow you to manage dependencies between multiple components that interoperate within an end-to-end ETL data pipeline by grouping together a set of related jobs, crawlers, and triggers into one logical run unit. Many customers using AWS Glue workflows start by defining the pipeline using the AWS Management Console and then move on to monitoring and troubleshooting using either the console, AWS APIs, or the AWS Command Line Interface (AWS CLI).

## Architecture Diagram
![Alt text](images/blog.png?raw=true "Architecture Diagram")

## Deploy solution from codepipeline stack

AWS CLI command to deploy codepipeline stack:
```
aws cloudformation deploy \
--stack-name codepipeline-covid19 \
--template-file cloudformation/codepipeline-stack.yml \
--capabilities CAPABILITY_NAMED_IAM \
--no-fail-on-empty-changeset \
--region <AWS_REGION>
```

Command to zip source code:
```
zip -r source.zip . -x images/\* *.history* *.git* *.DS_Store*
```

AWS CLI command to upload source code:
```
aws s3 cp source.zip s3://covid19-codepipeline-source-<AWS_ACCOUNT_ID>-<AWS_REGION>
```
**Note**: Uploading the source code will initiate an execution of the pipeline named: DeployPipelineForGlueWorkflow-codepipeline-covid19

## Deploy solution from your machine without codepipeline

AWS CLI command to deploy glue workflow stack:
```
aws cloudformation deploy \
--stack-name glue-covid19 \
--template-file cloudformation/glue-workflow-stack.yml \
--capabilities CAPABILITY_NAMED_IAM \
--no-fail-on-empty-changeset \
--region <AWS_REGION>
```

AWS CLI command to copy python scripts to bucket/glue-scripts:
```
aws s3 cp src s3://covid19-dataset-<AWS_ACCOUNT_ID>-<AWS_REGION>/glue-scripts/ --recursive
```

## Running the workflow

The workflow runs automatically at 8:00 AM UTC. To start the workflow manually, you can use either the AWS CLI or the AWS Glue console.

AWS CLI command to start glue workflow:
```
aws glue start-workflow-run --name Covid_19 --region <AWS_REGION>
```

To start the workflow on the AWS Glue console, on the Workflows page, select your workflow and choose Run on the Actions menu.
![Alt text](images/workflow_run_console.png?raw=true "Glue console run workflow")


The following screenshot shows a visual representation of the workflow as a graph with your run details.
![Alt text](images/workflow_visualiztion_and_details.png?raw=true "AWS Glue console displaying details of successful workflow run")

## Interested in Contributing?

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the [LICENSE](/LICENSE) file.
