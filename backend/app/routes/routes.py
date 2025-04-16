from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os, csv
from app.routes import ml_routes

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# This is the router FastAPI is looking for in main.py
router = APIRouter()

router.include_router(ml_routes.router)

# Connect to Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

@router.get("/")
def read_root():
    return {"message": "FastAPI is running!"}

@router.get("/api/projects/simple_tree")
def get_simple_tree():
    try:
        query = """
        MATCH (p:Project)-[:HAS_SCAN]->(s:Scan)
        RETURN p.name AS project, collect(s.name) AS scans
        """
        with driver.session() as session:
            results = session.run(query)
            return {record["project"]: record["scans"] for record in results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
