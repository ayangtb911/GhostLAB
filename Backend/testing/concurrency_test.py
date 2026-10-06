import threading


counter = 0
lock = threading.Lock()


def increase_counter():
    global counter

    for _ in range(100000):

        with lock:
            counter += 1


thread1 = threading.Thread(target=increase_counter)
thread2 = threading.Thread(target=increase_counter)

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print("Final counter:", counter)