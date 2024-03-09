import connexion
import six

from swagger_server.server_impl.DefaultController_impl import DefaultController_impl

from swagger_server.models.data_source import DataSource  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.indexer import Indexer  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.inline_response201 import InlineResponse201  # noqa: E501
from swagger_server.models.job import Job  # noqa: E501
from swagger_server.models.job_configuration import JobConfiguration  # noqa: E501
from swagger_server.models.record import Record  # noqa: E501
from swagger_server import util


def indexers_get():  # noqa: E501
    """List all available indexers.

     # noqa: E501


    :rtype: List[Indexer]
    """
    return DefaultController_impl.indexers_get()


def indexers_indexer_type_data_sources_data_source_id_records_get(indexer_type, data_source_id):  # noqa: E501
    """List all records for a specific data source of an indexer

     # noqa: E501

    :param indexer_type: 
    :type indexer_type: str
    :param data_source_id: 
    :type data_source_id: str

    :rtype: List[Record]
    """
    return DefaultController_impl.indexers_indexer_type_data_sources_data_source_id_records_get(indexer_type, data_source_id)


def indexers_indexer_type_data_sources_get(indexer_type):  # noqa: E501
    """List all data sources for a specific indexer type

     # noqa: E501

    :param indexer_type: 
    :type indexer_type: str

    :rtype: List[DataSource]
    """
    return DefaultController_impl.indexers_indexer_type_data_sources_get(indexer_type)


def jobs_get():  # noqa: E501
    """List the jobs

     # noqa: E501


    :rtype: List[Job]
    """
    return DefaultController_impl.jobs_get()


def jobs_job_id_delete(job_id):  # noqa: E501
    """Delete a job

     # noqa: E501

    :param job_id: 
    :type job_id: str

    :rtype: None
    """
    return DefaultController_impl.jobs_job_id_delete(job_id)


def jobs_job_id_get(job_id):  # noqa: E501
    """Get a job&#x27;s details

     # noqa: E501

    :param job_id: 
    :type job_id: str

    :rtype: Job
    """
    return DefaultController_impl.jobs_job_id_get(job_id)


def jobs_job_id_request_logs_update_post(job_id):  # noqa: E501
    """Requests an update to the logs for a specific job without providing a request body.

     # noqa: E501

    :param job_id: The unique identifier for the job for which the log update is requested.
    :type job_id: str

    :rtype: InlineResponse200
    """
    return DefaultController_impl.jobs_job_id_request_logs_update_post(job_id)


def jobs_post(body):  # noqa: E501
    """Create a new job with a command or configuration

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: InlineResponse201
    """
    if connexion.request.is_json:
        body = JobConfiguration.from_dict(connexion.request.get_json())  # noqa: E501
    return DefaultController_impl.jobs_post(body)
