# Using AWS DevOps Tools to model and provision AWS Glue workflows

Git repo to accompany the AWS DevOps Blog: [Using AWS DevOps Tools to model and provision AWS Glue workflows](https://aws.amazon.com/blogs/devops/provision-codepipeline-glue-workflows).

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

AWS CLI command to start glue workflow:
```
aws glue start-workflow-run --name Covid_19 --region <AWS_REGION>
```

## Interested in Contributing?

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the [LICENSE](/LICENSE) file.
