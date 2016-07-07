import functools
import uuid
import threading
from flask import request, make_response, g, jsonify, url_for, \
                  copy_current_request_context
from . import app
import kvstore


CONSUL_ENDPOINT = app.config.get('CONSUL_ENDPOINT')
kv = kvstore.Client(CONSUL_ENDPOINT)

def asynchronous(f):
    """Run the request asyncronously

    Inital response:
        - Status code 202 Accepted
        - Location header with the URL of a job resource.

    Job running:
        - A GET request to the job returns 202

    Job finished:
        - Status code 303 See Other
        - Location header points to the newly created resource

    The client then needs to send a DELETE request to the task resource to
    remove it from the system.
    """
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        id = uuid.uuid4().hex
        kv.set('queue/{}/status'.format(id), 'pending')

        @copy_current_request_context
        def job():
            response = make_response(f(*args, **kwargs))
            status_code = response.status_code
            if status_code == 201:
                kv.set('queue/{}/status'.format(id), 'registered')
            else:
                kv.set('queue/{}/status'.format(id), 'error')
            kv.set('queue/{}/status_code'.format(id), status_code)
            kv.set('queue/{}/url'.format(id), response.headers['Location'])

        job = threading.Thread(target=job)
        job.start()
        location = url_for('api.get_async_job_status', id=id, _external=True)
        return jsonify({'url': location}), 202, {
            'Location': location}

    return decorator
