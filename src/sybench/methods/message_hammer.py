import treq
import time

from collections import defaultdict

from uuid import uuid4

from sybench import _structures

from twisted.internet.defer import ensureDeferred


async def create(url, username, password, config):

    login = _structures.generate_login(username, password)
    token = (await login.execute(url))["access_token"]

    room_create = _structures.generate_room_create(token, uuid4().hex)
    room_id = (await room_create.execute(url))["room_id"]

    room_join = _structures.generate_room_join(token, room_id)
    await room_join.execute(url)

    c = iter(range(0, 1000))

    results = defaultdict(int)

    def post_message():
        time_before = time.time()

        def _(x):
            time_taken = round(time.time() - time_before, 2)
            results[time_taken] = results[time_taken] + 1
            return x

        r = _structures.generate_message(token, room_id, next(c), "foo")
        d = ensureDeferred(r.execute(url))
        d.addCallback(_)
        return d

    def _results():

        time_taken = 0.0
        requests = 0
        done = []

        for i in sorted(results.keys()):

            print(str(i) + " | " + str(results[i]))

            time_taken += results[i] * i
            requests += results[i]
            done.extend([i] * results[i])

        print("----")
        print("Average: " + str(round(time_taken / requests, 3)))
        print("Median: " + str(done[len(done)//2]))

    return post_message, _results
