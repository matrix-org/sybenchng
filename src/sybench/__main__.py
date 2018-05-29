import sys
import click

from twisted.logger import globalLogBeginner, textFileLogObserver

from twisted.internet.task import react, LoopingCall
from twisted.internet.defer import ensureDeferred, DeferredList
from twisted.python.reflect import requireModule

@click.command()
@click.option("--method")
@click.option("--count", default=50)
@click.option("--url", default="http://localhost:8008")
@click.option("--username", default="user")
@click.option("--password", default="pass")
def run(method, count, url, username, password):

    #globalLogBeginner.beginLoggingTo([textFileLogObserver(sys.stdout)])

    async def go(reactor):

        mod = requireModule(f"sybench.methods.{method}")

        if not mod:
            raise Exception("Not a valid method!")

        work, results = await mod.create(url, username, password, {})

        workers = []

        for i in range(count):

            l = LoopingCall(work)
            workers.append(l.start(0, now=False))

        try:
            await DeferredList(workers, consumeErrors=True)
        finally:
            results()

    react(lambda x: ensureDeferred(go(x)))


if __name__ == "__main__":
    run()
