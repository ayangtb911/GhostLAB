import threading
import time


semaphore = threading.Semaphore(2)


def worker(worker_id):

    with semaphore:

        print(f"Worker {worker_id} entered")

        time.sleep(2)

        print(f"Worker {worker_id} leaving")


threads = []

for i in range(5):

    thread = threading.Thread(
        target=worker,
        args=(i,)
    )

    threads.append(thread)
    thread.start()


for thread in threads:
    thread.join()

print("All workers finished")