from turtle import position
import bot.cogs.engine.music_cog.exceptions as ex
import random


class Queue:
    def __init__(self):
        self._queue = []
        self.position = 0

    #                       #
    #      PROPERTIES       #
    #                       #
    @property
    def is_empty(self):
        return not self._queue

    @property
    def current_track(self):
        self.queue_statecheck()
        if self.position <= len(self._queue)-1:
            return self._queue[self.position]
        return None

    @property
    def upcoming(self):
        self.queue_statecheck()
        return self._queue[self.position+1:]

    @property
    def history(self):
        self.queue_statecheck()
        return self._queue[:self.position]

    @property
    def length(self) -> int:
        return len(self._queue)

    #                       #
    #       METHODS         #
    #                       #
    def queue_statecheck(self):
        if not self._queue:
            raise ex.QueueIsEmpty

    def add(self, *args):
        self._queue.extend(args)

    def clear(self):
        self.position = 0
        self._queue.clear()

    def get_next_track(self):
        self.queue_statecheck()

        self.position += 1
        if self.position > len(self._queue)-1:
            return None
        return self._queue[self.position]

    def shuffle(self):
        self.queue_statecheck()
        upcoming = self.upcoming
        random.shuffle(upcoming)
        self._queue = self._queue[:self.position+1]
        self._queue.extend(upcoming)
