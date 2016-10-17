from sqlalchemy import MetaData
from sqlalchemy_schemadisplay import create_schema_graph

# Database
host     = 'localhost'
engine   = 'sqlite'
database = 'database'
username = 'username'
password = 'password'

# General
data_types = True
indexes    = True


# Generation
dsn = engine + ':///Experiment-server.sqlite'

graph = create_schema_graph(
    metadata       = MetaData(dsn),
    show_datatypes = data_types,
    show_indexes   = indexes
)

graph.write_png('schema.png')
