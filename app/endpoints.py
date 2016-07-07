from flask import jsonify
from . import api, app
import registry
import subprocess
import os
from tempfile import NamedTemporaryFile
from decorators import asynchronous

CONSUL_ENDPOINT = app.config.get('CONSUL_ENDPOINT')
registry.connect(CONSUL_ENDPOINT)


@api.route('/clusters/<clusterid>', methods=['POST'])
#@asynchronous
def run_orchestrator(clusterid):
    app.logger.info('Request to launch orchestrator for cluster {}'
                    .format(clusterid))
    clusterdn = registry.dn_from(clusterid)
    cluster = registry.get_cluster(dn=clusterdn)
    # FIXME maybe there's a better way of obtaining the service and version (attributes of the cluster?)
    service_str = clusterdn.split('/')[2]
    version_str = clusterdn.split('/')[3]
    service = registry.get_product(service_str, version_str)
    orchestrator = service.orchestrator

    with NamedTemporaryFile(suffix='.py') as fabfile:
        fabfile.write(orchestrator)
        fabfile.flush()
        cluster.status = 'configuring'
        env = os.environ.copy()
        env['CLUSTERDN'] = clusterdn
        subprocess.call(['fab', '--fabfile', fabfile.name, 'start'], env=env)
        # TODO: Return the output of the process (this blocks too long)
        #proc = subprocess.Popen(
            #['fab', '--fabfile', fabfile.name, 'start'], env=env,
            #stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #proc.wait()
        #out, err = proc.communicate()
        #exit_status = proc.poll()
        #if exit_status == 0:
            #cluster.status = 'configured'
            #return jsonify({'status': 'configured', 'stdout': out, 'stderr': err}), 200
        #else:
            #cluster.status = 'error during configuration'
            #return jsonify({'status': 'error', 'stdout': out, 'stderr': err}), 400

    #return jsonify({'status': 'error', 'message': 'Unknown error in orchestrator'}), 400
    return '', 204


@api.route('/queue/<id>', methods=['GET'])
def get_async_job_status(id):
    """Get the status of an async request"""
    status = kv.get('queue/{}/status'.format(id))
    if status != 'pending':
        url = kv.get('queue/{}/url'.format(id))
        status = kv.get('queue/{}/status'.format(id))
        return (jsonify({'status': status, 'url': url}), 303,
                {'Location': url})
    return jsonify({'status': 'pending'}), 200
