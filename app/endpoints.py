from flask import jsonify
from . import api, app
import registry
import subprocess
import os
from tempfile import NamedTemporaryFile
import threading

CONSUL_ENDPOINT = app.config.get('CONSUL_ENDPOINT')
registry.connect(CONSUL_ENDPOINT)


@api.route('/clusters/<clusterid>', methods=['POST'])
#@asynchronous
def run_orchestrator(clusterid):
    app.logger.info('Request to launch orchestrator for cluster {}'
                    .format(clusterid))
    clusterdn = registry.dn_from(clusterid)
    cluster = registry.get_cluster(dn=clusterdn)
    product_str = clusterdn.split('/')[2]
    version_str = clusterdn.split('/')[3]
    product = registry.get_product(product_str, version_str)
    orchestrator = product.orchestrator

    def configure_cluster():
        with NamedTemporaryFile(suffix='.py') as fabfile:
            fabfile.write(orchestrator)
            fabfile.flush()
            cluster.status = 'configuring'
            env = os.environ.copy()
            env['CLUSTERDN'] = clusterdn
            # If we do not care about the output
            #subprocess.call(['fab', '--fabfile', fabfile.name, 'start'], env=env)
            # Save the output of the process in the registry
            proc = subprocess.Popen(
                ['fab', '--fabfile', fabfile.name, 'start'], env=env,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait()
            out, err = proc.communicate()
            exit_status = proc.poll()
            cluster.orchestrator_stdout = out
            cluster.orchestrator_stderr = err
            if exit_status == 0:
                #cluster.status = 'configured'
                # Since this is the last step the status is ready
                cluster.status = 'ready'
            else:
                cluster.status = 'error during configuration'

    t = threading.Thread(target=configure_cluster)
    t.daemon = True
    t.start()
    return '', 204
