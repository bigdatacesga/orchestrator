from . import api, app
import registry
import subprocess
import os
from tempfile import NamedTemporaryFile

CONSUL_ENDPOINT = app.config.get('CONSUL_ENDPOINT')
registry.connect(CONSUL_ENDPOINT)


@api.route('/clusters/<clusterid>', methods=['POST'])
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

    #with NamedTemporaryFile() as f:
    with NamedTemporaryFile(suffix='.py', delete=False) as fabfile:
        fabfile.write(orchestrator)
        fabfile.flush()
        print fabfile.name
        cluster.status = 'configuring'
        env = os.environ.copy()
        env['CLUSTERDN'] = clusterdn
        subprocess.call(['fab', '--fabfile', fabfile.name, 'start'], env=env)
        cluster.status = 'configured'

    return '', 204
