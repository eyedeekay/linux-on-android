import connection
import binder
import constants
import StringIO
import threading
import weakref
import traceback
import Queue

DISPATCHERS_COUNT = 2
WAIT_TIMEOUT = 1

class SynchroCounter:
    def __init__(self):
        self.lock = threading.Lock()
        self.value = 1
    
    def next(self):
        self.lock.acquire()
        res = self.value
        self.value += 1
        self.lock.release()
        return res


class RILError(Exception):
    def __init__(self, id):
        self.id = id
    def __repr__(self):
        return 'RIL error: %d' % (self.id,)


class Response:
    def __init__(self, output_type):
        self.event = threading.Event()
        self.output_type = output_type
        self.error = None
    
    def receive(self, stream):
        self.result = self.output_type.read(stream)
        self.event.set()
        
    def error(self, error):
        self.error = error
        self.event.set()
        
    def wait(self):
        self.event.wait()
        
    def get(self):
        self.wait()
        if self.error is not None:
            raise RILError(self.error)
        return self.result


class RIL:
    def __init__(self, handler):
        self.conn = connection.RILDConnection()
        self.create_requests()
        self.serial_no = SynchroCounter()
        self.responses = {}
        self.responses_lock = threading.Lock()
        self.handler = weakref.ref(handler)
        self.create_requests()
        self.id_to_event = dict((ev.id, ev) \
            for ev in constants.events)
        self.start_dispatchers()
        
    def new_response(self, serial, output_type):
        response = Response(output_type)
        self.responses_lock.acquire()
        self.responses[serial] = weakref.ref(response)
        self.responses_lock.release()
        return response
        
    def create_requests(self):
        for request in constants.requests:
            self.create_request(request)
            
    def create_request(self, request):
        if request.input not in binder.types:
            print 'Type ' + request.input + ' not supported'
            print 'Skipping request', request
            return
        if request.output not in binder.types:
            print 'Type ' + request.output + ' not supported'
            print 'Skipping request', request
            return
        input_type = binder.types[request.input]
        output_type = binder.types[request.output]
        id = request.id

        def request_method(*args):
            serial_no = self.serial_no.next()
            stream = StringIO.StringIO()
            binder.Int.write(stream, id)
            binder.Int.write(stream, serial_no)
            input_type.write(stream, *args)
            message = stream.getvalue()
            stream.close()
            resp = self.new_response(serial_no, output_type)
            self.conn.output_queue.put(message)
            return resp

        self.__dict__[request.name] = request_method    


    def dispatcher(self):
        while not self.stop:
            try:
                message = self.conn.input_queue.get(True, WAIT_TIMEOUT)
            except Queue.Empty:
                continue
            stream = StringIO.StringIO(message)
            is_unsolicited, = binder.Int.read(stream)
            if is_unsolicited:
                self.process_unsolicited(stream)
            else:
                self.process_response(stream)
            stream.close()

    def process_unsolicited(self, stream):
        id, = binder.Int.read(stream)
        event = self.id_to_event[id]
        handler = self.handler.value
        if handler is not None and \
                self.event.name in handler.__dict__:
            if event.output in binder.types:
                args = binder.types[event.output].read(stream)
                handler.__dict__[name](*args)
            else:
                print 'Type', event.output, 'not implemented'
                print 'Skipping event', event 
        else:
            print 'Handler for', event.name, 'not implemented'
            print 'Skipping event', event 
                

    def process_response(self, stream):
        serial, = binder.Int.read(stream)
        error, = binder.Int.read(stream)
        
        self.responses_lock.acquire()
        if serial in sel.responses:
            resp = self.responses[serial]
            del self.responses[serial]
            wrong_serial = False
        else:
            wrong_serial = True
        self.responses_lock.release()
        
        if wrong_serial:
            print 'Unknown response id', serial
            return

        if resp is not None:
            if error != 0:
                resp.error(error)
            else:
                resp.receive(stream)
                

    def start_dispatchers(self):
        self.stop = False
        self.dispatchers = [threading.Thread(None, self.dispatcher) \
            for i in range(DISPATCHERS_COUNT)]
        for disp in self.dispatchers:
            disp.start()
        

    def stop_dispatchers(self):
        self.stop = True
        for disp in self.dispatchers:
            disp.join()


    def close(self):
        print 'Closing'
        self.conn.close()
        self.stop_dispatchers()


def example():
    class Handler:
        pass
    tmp = RIL(Handler())
    tmp.close()
    
if __name__=='__main__':
    example()
    print 'Example finished'

    
