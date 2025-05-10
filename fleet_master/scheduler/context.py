from shared.utils.http import AsyncHttpClient


class SchedulerContext:
    def __init__(self):
        self.http_client = AsyncHttpClient()

scheduler_context = SchedulerContext()
