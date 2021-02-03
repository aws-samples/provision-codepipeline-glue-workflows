import sys
import boto3  # type: ignore
import logging
import json
from awsglue.utils import getResolvedOptions  # type: ignore


# Setup Logging
def setup_logger(log_level):
    log_msg_format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    log_datetime_format = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(format=log_msg_format, datefmt=log_datetime_format)
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    return logger


# Read params from commandline
args = getResolvedOptions(sys.argv, ['WORKFLOW_NAME', 'WORKFLOW_RUN_ID', 'LOG_LEVEL'])

workflow_name = args['WORKFLOW_NAME']
workflow_run_id = args['WORKFLOW_RUN_ID']
log_level = args['LOG_LEVEL']

# Logging
logger = setup_logger(log_level)

logger.info(f"workflowName [{workflow_name}]")
logger.info(f"runId [{workflow_run_id}]")

# Initiate Events client
events = boto3.client('events')

detail = json.dumps({'workflowName': workflow_name, 'runId': workflow_run_id, 'state': 'ENDED'})

# Submit event to PutEvents API
response = events.put_events(
    Entries=[
        {
            'Detail': detail,
            'DetailType': 'Glue Workflow State Change',
            'Source': 'finance.cur.kpi.pipeline'
        }
    ]
)
response_string = json.dumps(response)
logger.info(f"Response from PutEvents API [{response_string}]")
logger.info("emit_event_workflow_run_id.py: Job completed successfully ...")
