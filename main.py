import base64
import json
from google.cloud import scheduler_v1, firestore

from act.ACT import ACT
from act.persistence.persistence import Persistence
from act.persistence.persistence_type import PersistenceType


def act(event, context):
    print("event: ", event)
    print("context: ", context)

    if 'data' in event:
        # setup_path = base64.b64decode(event['data']).decode('utf-8')
        path, name = Persistence.get_path_and_name_from_data(event)
        print("path: ",path)
        print("name: ",name)
        ACT.serialized_run(persistence_type=PersistenceType.GOOGLE_FIRESTORE,
                           setup_path=path,
                           setup_name=name,
                           scheduler=None,
                           running_in_cloud=True)


def update_job(data, context):
    """ Triggered by a change to a Firestore document
    Args:
        data (dict): The event payload.
        context (google.cloud.functions.Context): Metadata for the event.
        https://cloud.google.com/functions/docs/calling/cloud-firestore#functions_firebase_firestore-python
    """
    trigger_resource = context.resource
    doc_ref = firestore.Client().document(trigger_resource)
    trade_setup = doc_ref.get().to_dict()
    print(trade_setup)
    act_cloud_scheduler = trade_setup.get('act_cloud_scheduler')
    print(act_cloud_scheduler)
    topic = act_cloud_scheduler.get('topic')
    print(topic)
    cron_config = act_cloud_scheduler.get('cron')
    print(cron_config)
    project = '/projects/example5-237118'
    parent = project+'/locations/europe-west1'
    complete_topic_name = project+'/topics/'+topic
    print(complete_topic_name    )
    print('Function triggered by change to: %s' % trigger_resource)
    #
    # print('\nOld value: ')
    # print(json.dumps(data["oldValue"]))
    #
    # print('\nNew value: ')
    # print(json.dumps(data["value"]))
    #
    # if data["oldValue"].get("job") is None:
    # current_folder = os.path.dirname(os.path.abspath(__file__))
    # abs_auth_path = os.path.join(current_folder, 'auth.json')
    # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = abs_auth_path
    job = {
        "pubsub_target": {
            "topic_name": "projects/example5-237118/topics/"+topic,
            "data": bytes(trigger_resource, 'utf-8')
        },
        "schedule": cron_config # "* * * * *"
    }
    print("job: "+str(job))
    # see https://googleapis.github.io/google-cloud-python/latest/scheduler/gapic/v1/api.html
    response = scheduler_v1.CloudSchedulerClient().create_job(parent, job)
    print("name")
    print(response.name)
    job_name = response.name[response.name.rindex('/')+1:]
    print(job_name)
    print(response)
    doc_ref.collection('jobs').document(job_name).set({'content': str(response)})

    #return 'finished'
