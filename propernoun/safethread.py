import Queue
import sys
import threading


def _wrapper(q, fn):
    try:
        fn()
    except:
        q.put(sys.exc_info())


def run_safe_threads(*callables):
    """
    Run callables, each in a separate thread, while catching any
    exceptions and aborting the whole process.

    This blocks forever.
    """
    breakage = Queue.Queue()

    for c in callables:
        t = threading.Thread(
            target=_wrapper,
            kwargs=dict(
                q=breakage,
                fn=c,
                ),
            name=c.__doc__,
            )
        t.daemon = True
        t.start()

    # this is needed to see control-C from user; without the timeout,
    # it'll just hang
    while True:
        try:
            (exc_type_, exc_value, exc_tb) = breakage.get(True, 1.0)
        except Queue.Empty:
            pass
        else:
            raise exc_type_, exc_value, exc_tb
