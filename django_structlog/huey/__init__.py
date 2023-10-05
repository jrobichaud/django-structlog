from huey import Huey as OriginalHuey
from huey.storage import RedisStorage


class Huey(OriginalHuey):
    def enqueue(self, task):
        # TODO: See https://github.com/coleifer/huey/pull/771
        if not self._immediate:
            self._emit("enqueue", task)
        return super().enqueue(task)


class RedisHuey(Huey):
    storage_class = RedisStorage
