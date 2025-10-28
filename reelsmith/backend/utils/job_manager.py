import uuid
from typing import Dict, Any

class JobManager:
    """A class to manage the state of video processing jobs."""

    def __init__(self):
        """Initializes the JobManager with an empty dictionary to store jobs."""
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def create_job(self) -> str:
        """
        Creates a new job with a unique ID and sets its initial status to 'processing'.

        Returns:
            str: The unique ID of the created job.
        """
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {"status": "processing", "error": None}
        return job_id

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Retrieves the status of a job by its ID.

        Args:
            job_id (str): The ID of the job to retrieve.

        Returns:
            Dict[str, Any]: A dictionary containing the job's status, or 'not_found' if the job does not exist.
        """
        return self.jobs.get(job_id, {"status": "not_found"})

    def update_job_status(self, job_id: str, status: str, error: str = None):
        """
        Updates the status of a job.

        Args:
            job_id (str): The ID of the job to update.
            status (str): The new status of the job ('completed' or 'failed').
            error (str, optional): A description of the error, if the job failed. Defaults to None.
        """
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = status
            if error:
                self.jobs[job_id]["error"] = error

# Create a single instance of the JobManager to be used throughout the application
job_manager = JobManager()
