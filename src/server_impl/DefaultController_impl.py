import connexion
import six
import logging
import re
from flask import current_app
from swagger_server.models.data_source import DataSource  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.indexer import Indexer  # noqa: E501
from swagger_server.models.inline_response201 import InlineResponse201  # noqa: E501
from swagger_server.models.job import Job  # noqa: E501
from swagger_server.models.job_configuration import JobConfiguration  # noqa: E501
from swagger_server.models.record import Record  # noqa: E501
from swagger_server import util
from swagger_server.models.environment_variable import EnvironmentVariable  # noqa: E501


import datetime
import uuid

from swagger_server.server_impl.rq_config import q

from swagger_server.server_impl.db_config import db
from swagger_server.server_impl.k8s_job import create_kubernetes_job, remove_job, get_job_logs
from flask import jsonify

def indexers_get():  # noqa: E501
    """List all available indexers.

     # noqa: E501


    :rtype: List[Indexer]
    """

    indexers = list(db.indexers.find({}))
    
    # Convert MongoDB ObjectId() to string for JSON serialization
    for indexer in indexers:
        indexer['_id'] = str(indexer['_id'])
    return jsonify(indexers)


def indexers_indexer_type_data_sources_data_source_id_records_get(indexer_type, data_source_id):  # noqa: E501
    """List all records for a specific data source of an indexer

     # noqa: E501

    :param indexer_type: 
    :type indexer_type: str
    :param data_source_id: 
    :type data_source_id: str

    :rtype: List[Record]
    """
    return 'do some magic!'


def indexers_indexer_type_data_sources_get(indexer_type):  # noqa: E501
    """List all data sources for a specific indexer type

     # noqa: E501

    :param indexer_type: 
    :type indexer_type: str

    :rtype: List[DataSource]
    """
    data_sources = list(db.data_sources.find({}))
    
    # Convert MongoDB ObjectId() to string for JSON serialization
    for d in data_sources:
        d['_id'] = str(d['_id'])
    return jsonify(data_sources)

def jobs_get():  # noqa: E501
    """List the jobs

     # noqa: E501


    :rtype: List[Job]
    """
    jobs_cursor = db.jobs.find({})
    jobs_list = list(jobs_cursor)
    
    # Convert MongoDB ObjectId() to string for JSON serialization
    for job in jobs_list:
        job['_id'] = str(job['_id'])
    
    # Using jsonify instead of converting to Job as defined in models, since there are extra fields set not specified in the schema
    return jsonify(jobs_list)


def jobs_job_id_delete(job_id):  # noqa: E501
    """Delete a job

     # noqa: E501

    :param job_id: 
    :type job_id: str

    :rtype: None
    """

    current_job = db.jobs.find_one({"_id": job_id})
    
    if not current_job:
        # Job not found
        error_response = Error(code=404, message="Job not found")
        return jsonify(error_response.to_dict()), 404

    if current_job.get("status") == "being removed":
        # Job is already being removed
    #     job = q.enqueue(remove_job, job_id, False)        
        return  Error(code=202, message="Job is already being removed"), 202
    else:
        # Update the job's status to "being removed"
        # TODO check if repeat
        job = q.enqueue(remove_job, job_id, False)
        db.jobs.update_one(
            {"_id": job_id},
            {"$set": {"status": "being removed"}}
        )
        return jsonify({"message": "Job deletion initiated"}), 202


def jobs_job_id_get(job_id):  # noqa: E501
    """Get a job&#x27;s details

     # noqa: E501

    :param job_id: 
    :type job_id: str

    :rtype: Job
    """
    job = db.jobs.find_one({"_id": job_id})
    
    if job:
        job['_id'] = str(job['_id'])
        return jsonify(job)
    else:
        return Error(code=404, message="Job not found"), 404


def jobs_job_id_request_logs_update_post(job_id):  # noqa: E501
    """Requests an update to the logs for a specific job without providing a request body.

     # noqa: E501

    :param job_id: The unique identifier for the job for which the log update is requested.
    :type job_id: str

    :rtype: Union[JobsJobIdRequestLogsUpdatePost200Response, Tuple[JobsJobIdRequestLogsUpdatePost200Response, int], Tuple[JobsJobIdRequestLogsUpdatePost200Response, int, Dict[str, str]]
    """
    job = db.jobs.find_one({"_id": job_id})
    
    if not job:
        return Error(code=404, message="Job not found"), 404

    try:
        # retrieve the latest logs for the job
        logs = get_job_logs(job_id)
        
        # Update the job entry in the database with the retrieved logs
        db.jobs.update_one({"_id": job_id}, {"$set": {"logs": logs}})
        
        return jsonify({"message": "Logs updated successfully", "logs": logs}), 200
    except Exception as e:
        current_app.logger.warn(f"An error occurred while updating logs:{e}")
        error_response = Error(code=500, message=f"An error occurred while updating logs")
        return jsonify(error_response.to_dict()), 500

def jobs_post(body):  # noqa: E501
    """Create a new job with a command or configuration

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: InlineResponse201
    """
    # if connexion.request.is_json:
    #     body = JobConfiguration.from_dict(connexion.request.get_json())  # noqa: E501
            
    if connexion.request.is_json:
        body = connexion.request.get_json()
        command = None

        if 'indexerConfiguration' in body:
            config = body['indexerConfiguration']

            record_option = f"r-{config['record']}" if config['record'] else ''
            command = f"kb_indexer {config['indexer']['type']} {record_option} {config['pipeline']}".strip()

            command = re.sub(' +', ' ', command)
            body.update({'generatedCommand' : command})
            logging.getLogger().info(f"Sending job with body: {body}")
        elif 'command' in body:
            command = body['command']
        
        env = None
        if 'environment_variables' in body:
            try :
                env = body['environment_variables']
            except Exception as e:
                print(e)
                return Error(code=400, message="Invalid environment_variables in request body"), 400

        if command:
            job_id = str(uuid.uuid4())
            body.update({
                "_id": job_id,
                "creationTimestamp": datetime.datetime.utcnow().isoformat(),
                "status": "initializing",
            })

            db.jobs.insert_one(body)

            docker_image = "qcdis/kb-indexer:latest"
            # TODO check if repeat
            repeat = body["repeat"] if "repeat" in body   else None
            create_kubernetes_job(job_id, command, docker_image, env, repeat)



            return InlineResponse201(job_id=job_id), 201
        
        return Error(code=400, message="Invalid request body, missing command or jobConfiguration"), 400
    else:
        return Error(code=400, message="Invalid, request body is not json "), 400

def environment_variables_get():
    """Get environment variables

     # noqa: E501


    :rtype: List[EnvironmentVariable]
    """
    return jsonify(list( db.environment_variables.find({}, {'_id': 0})))


def environment_variables_post(body):
    """Add new environment variables

     # noqa: E501

    :param body: 
    :type body: list | bytes

    :rtype: None
    """

    if connexion.request.is_json:
        body = connexion.request.get_json()
        if not isinstance(body, list): 
            raise f"Post body is no document list: {body}"
        for variable in body:
            db.environment_variables.insert_one(variable)