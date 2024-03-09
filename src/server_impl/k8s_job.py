from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import List, Optional, Union
from kubernetes.client.models.v1_job import V1Job
from kubernetes.client.models.v1_cron_job import V1CronJob
import time
from swagger_server.server_impl.db_config import db
# TODO code clone
def create_kubernetes_job(job_name: str, command: List[str], image: str, schedule: Optional[str] = None) -> Union[V1Job, V1CronJob]:
    """
    Create a Kubernetes Job or CronJob to run a specific command in a Docker container.

    :param job_name: The name of the Kubernetes Job or CronJob.
    :type job_name: str
    :param command: The command to run in the container, provided as a list.
    :type command: List[str]
    :param image: The Docker image to use for the container.
    :type image: str
    :param schedule: The schedule in Cron format, used only if creating a CronJob. Defaults to None.
    :type schedule: Optional[str]
    :return: The created Kubernetes Job or CronJob object.
    :rtype: Union[V1Job, V1CronJob]
    """
     # Ensure command is a list of strings
    assert isinstance(command, List) and all(isinstance(elem, str) for elem in command), \
        "Command must be a list of strings"
    
    # Load the kubeconfig file from the default location or set up in-cluster config
    try:
        config.load_kube_config() # For local development
    except:
        config.load_incluster_config() # For use within a Kubernetes cluster

    # Define the Kubernetes API client
    api_instance = client.BatchV1Api()

    # Define the container to run
    container = client.V1Container(
        name=job_name,
        image=image,
        command=command
        ,image_pull_policy="IfNotPresent"
    )

    # Define the template for the job
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": job_name}),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container])
    )

    if schedule:
        # Define the CronJob spec
        job_spec = client.V1JobSpec(template=template)
        cronjob_spec = client.V1CronJobSpec(
            schedule=schedule,
            job_template=client.V1beta1JobTemplateSpec(spec=job_spec)
        )
        job = client.V1CronJob(
            api_version="batch/v1",
            kind="CronJob",
            metadata=client.V1ObjectMeta(name=job_name),
            spec=cronjob_spec
        )
        api_instance = client.BatchV1beta1Api()
        create_func = api_instance.create_namespaced_cron_job
    else:
        # Define the Job spec
        spec = client.V1JobSpec(template=template, backoff_limit=4)
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name=job_name),
            spec=spec
        )
        create_func = api_instance.create_namespaced_job

    # Create the Kubernetes Job
    api_response = create_func(
        body=job,
        namespace="default" 
    )
    return api_response

def remove_kubernetes_job(job_name: str, is_cronjob: Optional[bool] = False):
    """
    Delete a Kubernetes Job or CronJob.

    :param job_name: The name of the Kubernetes Job or CronJob to delete.
    :type job_name: str
    :param is_cronjob: Flag indicating whether the job to delete is a CronJob. Defaults to False.
    :type is_cronjob: Optional[bool]
    """
    try:
        config.load_kube_config()  # For local development
    except:
        config.load_incluster_config()  # For use within a Kubernetes cluster

    if is_cronjob:
        api_instance = client.BatchV1Api()
        api_response = api_instance.delete_namespaced_cron_job(
            name=job_name,
            namespace="default",
            body=client.V1DeleteOptions(
                propagation_policy='Foreground', 
            )
        )
    else:
        api_instance = client.BatchV1Api()
        api_response = api_instance.delete_namespaced_job(
            name=job_name,
            namespace="default",
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
            )
        )
    return api_response

# TODO refactor, too many calls to job_exists
def remove_job(job_name: str, is_cronjob: Optional[bool] = False) -> str:
    """
    Attempts to delete a Kubernetes Job or CronJob, checks for its existence, confirms its deletion, and removes its record from MongoDB.
    
    :param job_name: The name of the Kubernetes Job or CronJob to delete.
    :type job_name: str
    :param is_cronjob: Flag indicating whether the job to delete is a CronJob. Defaults to False.
    :type is_cronjob: Optional[bool]
    :return: A message indicating the outcome of the deletion process.
    :rtype: str
    """
    try:
        config.load_kube_config()  # For local development
    except:
        config.load_incluster_config()  # For use within a Kubernetes cluster

    def job_exists():
        try:
            if is_cronjob:
                client.BatchV1beta1Api().read_namespaced_cron_job(job_name, "default")
            else:
                client.BatchV1Api().read_namespaced_job(job_name, "default")
            return True
        except ApiException as e:
            if e.status == 404:
                return False
            raise

    # Check if job actually exists before attempting deletion
    if not job_exists():
        # Proceed to remove from MongoDB if it doesn't exist in Kubernetes
        db.jobs.delete_one({"_id": job_name})
        return f"Job {job_name} does not exist in Kubernetes. Removed record from MongoDB."

    try:
        # If job exists, attempt to delete it
        remove_kubernetes_job(job_name, is_cronjob)
    except ApiException as e:
        # If deletion fails for reasons other than the job not existing, return an error
        if not job_exists():  # Double-check if the job exists after catching the exception
            db.jobs.delete_one({"_id": job_name})
            return f"Job {job_name} removed from Kubernetes or did not exist. Removed record from MongoDB."
        else:
            return f"An error occurred while deleting the Kubernetes job: {e}"

    # Poll for job deletion confirmation, max 1 minute
    timeout = 60 
    start_time = time.time()
    while job_exists():
        if time.time() - start_time > timeout:
            return "Deletion confirmation timeout: Job may not have been deleted from Kubernetes."
        time.sleep(10) 

    # # Once confirmed that the job no longer exists, delete the job record from MongoDB
    db.jobs.delete_one({"_id": job_name})
    return f"Successfully deleted job {job_name} from Kubernetes and MongoDB."
