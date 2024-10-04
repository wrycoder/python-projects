import threading, time, unittest

#
# TODO: test handling of ZeroDivisionError
#

MAX_WAIT = .8
MED_WAIT = .5
MIN_WAIT = .025
ERROR_MESSAGE = "Well, that sucked"

class MyThread(threading.Thread):
    """A simple thread subclass"""

    def __init__(self, seconds):
        threading.Thread.__init__(self)
        self.time_to_live = seconds

    def run(self):
        time.sleep(self.time_to_live)
        print(f"Thread {threading.get_native_id()} finished")

def standalone_function(counter: int, name, soreness=True, baldness=False):
    time.sleep(counter)
    print(f"standalone_function for {name} now exiting. " + \
          f"Soreness: {soreness}. " + \
          f"Baldness: {baldness}");

class IcebergException(Exception):
    def __init__(self, message):
        super().__init__(message)

def erroneous_function():
    raise IcebergException(ERROR_MESSAGE)

class TestClassBasedThreading(unittest.TestCase):
    def test_my_thread(self):
        thread1 = MyThread(MAX_WAIT)
        with self.assertRaises(RuntimeError,
                        msg="Thread should not have started yet"):
            thread1.join()
        thread1.start()
        thread1.join(MAX_WAIT / 2)
        self.assertTrue(thread1.is_alive(),
                        msg="Thread should still be alive")
        thread1.join()
        self.assertFalse(thread1.is_alive(), 
                        msg="Thread should be dead")

class TestFunctionBasedThreading(unittest.TestCase):
    def test_three_stooges(self):
        t1 = threading.Thread(group=None,
            target=standalone_function, 
            args=[MAX_WAIT, 'larry'],
            daemon=True)
        t2 = threading.Thread(group=None,
            target=standalone_function, 
            args=[MED_WAIT, 'moe'],
            kwargs={'baldness': False, 'soreness': False})
        t3 = threading.Thread(group=None,
            target=standalone_function, 
            args=[MIN_WAIT, 'curly'],
            kwargs={'baldness': True, 'soreness': True})
        with self.assertRaises(RuntimeError,
                        msg="Thread should not have started yet"):
            t1.join()
        t1.start()
        t1.join(MAX_WAIT / 2)
        self.assertTrue(t1.is_alive(),
                        msg="larry's thread should still be alive")
        self.assertTrue(t1.daemon,
                        msg="larry should be a daemon")
        self.assertTrue(t1.native_id > 0,
                        msg="larry should have a valid ID")
        t1.join()
        self.assertFalse(t1.is_alive(),
                        msg="larry's thread should be dead")
        t2.start()
        t2.join(MED_WAIT / 2)
        self.assertTrue(t2.is_alive(),
                        msg="moe's thread should still be alive")
        t2.join()
        self.assertFalse(t2.is_alive(),
                        msg="moe's thread should be dead")
        t3.start()
        t3.join()
        self.assertFalse(t3.is_alive(),
                        msg="curly's thread should be dead")

class TestExceptHook(unittest.TestCase):
    def setUp(self):
        self.last_error_type = None
        self.last_error = None
        self.last_traceback = None

    def special_exception_handler(self, args):
        self.last_error_type = args[0]
        self.last_error = args[1]
        self.last_traceback = args[2]
        
    def test_disastrous_error(self):
        threading.excepthook = self.special_exception_handler
        rms_titanic = threading.Thread(group=None,
                                       target=erroneous_function)
        self.assertTrue(self.last_error_type == None,
            msg="There should be no exception yet")
        self.assertTrue(self.last_traceback == None,
            msg="There should not be a traceback yet")
        rms_titanic.start()
        self.assertEqual(self.last_error_type, IcebergException,
            msg="Last error should have been an IcebergException")
        self.assertEqual(self.last_error.args[0], ERROR_MESSAGE,
            msg=f"Last error message should say {ERROR_MESSAGE} \n" + \
                f"Instead, it says {self.last_error.args[0]}")
        self.assertFalse(self.last_traceback == None,
            msg="There should be a traceback")


if __name__ == "__main__":
    unittest.main()

