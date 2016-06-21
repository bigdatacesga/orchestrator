from flask import jsonify, g
from . import api, app
import registry
from .decorators import restricted

#from .configuration_registry import registry

CONSUL_ENDPOINT = app.config.get('CONSUL_ENDPOINT')
registry.connect(CONSUL_ENDPOINT)

@api.route('/clusters/<clusterid>', methods=['PUT'])
@restricted(role='ROLE_USER')
def run_orquestrator(clusterid):
    clusterdn = registry.dn_from(clusterid)
    instance = registry.get_cluster_instance(dn=clusterdn)
    # FIXME maybe there's a better way of obtaining the service and version (attributes of the cluster?)
    service_str = clusterdn.split('/')[2]
    version_str = clusterdn.split('/')[3]
    service = registry.get_service_template(service_str, version_str)
    orquestrator = service.orquestrator

    import os

    os.environ['INSTANCE'] = str(instance)
    os.environ['REGISTRY'] = app.config.get('CONSUL_ENDPOINT')
    os.environ['OP'] = "start"
    # FIXME understand if globals or locals have something to do with how the exec behaves
    # https://docs.python.org/3/library/functions.html#globals
    # Just pass the same argument twice
    exec(orquestrator, globals(), globals())
    #exec (orquestrator, locals(), locals())

    # os.environ['OP'] = "stop"
    # exec orquestrator
    #
    # os.environ['OP'] = "status"
    # exec orquestrator
    #
    # os.environ['OP'] = "restart"
    # exec orquestrator

    return jsonify({'code': orquestrator})
