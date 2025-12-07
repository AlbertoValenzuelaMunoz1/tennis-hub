from locust import HttpUser, TaskSet, between, task

from core.environment.host import get_host_for_locust_testing


class FakenodoBehavior(TaskSet):
    """
    Simulates a user interacting with the Fakenodo API.

    The typical flow is:
    1. Create a deposition.
    2. Interact with the created deposition (get, upload, publish).
    3. Delete the deposition.
    """

    deposition_id = None

    def on_start(self):
        """
        Called when a simulated user starts.
        It creates a new deposition to get a valid ID for other tasks.
        """
        self.create_deposition()

    def on_stop(self):
        """
        Called when a simulated user stops.
        It cleans up by deleting the deposition if it exists.
        """
        if self.deposition_id:
            self.client.delete(
                f"/fakenodo/{self.deposition_id}", name="/fakenodo/[id] (delete)"
            )
            self.deposition_id = None

    def create_deposition(self):
        """Creates a deposition and saves its ID."""
        with self.client.post("/fakenodo", name="/fakenodo (create)", catch_response=True) as response:
            if response.status_code == 201:
                try:
                    self.deposition_id = response.json().get("id")
                except ValueError:
                    response.failure("Response is not valid JSON")

    @task(5)
    def get_and_publish_deposition(self):
        """A sequence of tasks for a specific deposition."""
        if not self.deposition_id:
            self.create_deposition()
            return

        self.client.get(f"/fakenodo/{self.deposition_id}", name="/fakenodo/[id] (get)")
        self.client.post(f"/fakenodo/{self.deposition_id}/files", name="/fakenodo/[id]/files (upload)")
        self.client.post(f"/fakenodo/{self.deposition_id}/actions/publish", name="/fakenodo/[id]/actions/publish")

    @task(1)
    def list_depositions(self):
        """Task to get the list of all depositions."""
        self.client.get("/fakenodo", name="/fakenodo (list)")


class FakenodoUser(HttpUser):
    """User class that will execute the FakenodoBehavior tasks."""

    tasks = [FakenodoBehavior]
    wait_time = between(1, 5)
    host = get_host_for_locust_testing()