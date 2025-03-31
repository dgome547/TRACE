
from neo4j import GraphDatabase
from neo4j_config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE

nodename = "userrrr"  # This is the value you want to insert

# Correctly formatted parameterized query
neo4j_create_statement = "CREATE (t:Transaction {transaction_name: $transaction_name})"

def execute_transaction(statement, parameters):
    # Initialize the driver using credentials from your .env via neo4j_config
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            session.run(statement, parameters)  # Pass parameters correctly
    finally:
        driver.close()

# Execute the transaction with the correct parameter format
execute_transaction(neo4j_create_statement, {"transaction_name": nodename})
