# neo4j_config.py
import os
from neo4j import GraphDatabase

neo4j_password = os.environ.get('Vankhanh1.')
graphdb = GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "Vankhanh1."))
