Big Data Orquestrator REST API
======================

Installation
------------

    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt
    python wsgi.py


The Big Data Orquestratoor API has been designed using a microservices architecture which simplifies its deployment and
allows for better scalability. After a cluster instance has been registered and launched, the orquestrator kicks in
and configures the cluster using the orquestrator from the service template

Test with:

```
curl -X PUT http://127.0.0.1:5000/bigdata/api/v1/clusters/instances--test--mpi--1__0--7
curl -X PUT http://127.0.0.1:5000/bigdata/api/v1/clusters/<clusterid>
```