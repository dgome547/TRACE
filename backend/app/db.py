from neo4j import GraphDatabase
from neo4j_config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE

username1 = "userrrr"  # This is the value you want to insert

# Match the parameter name exactly (case-sensitive)
neo4j_create_statement = "CREATE (t:USER {userName: $userName})"

def executeQuery(statement, parameters):
    # Initialize the driver using credentials from your .env via neo4j_config
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            session.run(statement, parameters)  # Pass parameters correctly
    finally:
        driver.close()

# Ensure parameter name matches exactly
executeQuery(neo4j_create_statement, {"userName": username1})
