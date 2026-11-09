import os
from datetime import datetime, timezone

from pymongo import MongoClient
from dotenv import load_dotenv


# ==========================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("MONGODB_DATABASE")


if not MONGODB_URI:
    raise ValueError("MONGODB_URI is missing in .env file")

if not DATABASE_NAME:
    raise ValueError("MONGODB_DATABASE is missing in .env file")


# ==========================================
# 2. CONNECT TO MONGODB ATLAS
# ==========================================

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=10000
)

db = client[DATABASE_NAME]


# ==========================================
# 3. CREATE DATABASE COLLECTIONS
# ==========================================

research_collection = db["research_ideas"]

papers_collection = db["research_papers"]

analysis_collection = db["analysis_history"]


# ==========================================
# 4. SAVE RESEARCH PAPER DETAILS
# ==========================================

def save_paper(filename, page_count, chunk_count):

    document = {
        "filename": filename,
        "page_count": page_count,
        "chunk_count": chunk_count,
        "uploaded_at": datetime.now(timezone.utc)
    }

    result = papers_collection.insert_one(document)

    return result.inserted_id


# ==========================================
# 5. SAVE RESEARCH IDEA
# ==========================================

def save_research_idea(idea):

    document = {
        "research_idea": idea,
        "created_at": datetime.now(timezone.utc)
    }

    result = research_collection.insert_one(document)

    return result.inserted_id


# ==========================================
# 6. SAVE AI-GENERATED ANALYSIS
# ==========================================

def save_analysis(idea, analysis, sources):

    document = {
        "research_idea": idea,
        "analysis": analysis,
        "sources": sources,
        "created_at": datetime.now(timezone.utc)
    }

    result = analysis_collection.insert_one(document)

    return result.inserted_id


# ==========================================
# 7. GET ALL UPLOADED PAPERS
# ==========================================

def get_uploaded_papers():

    papers = list(
        papers_collection.find().sort(
            "uploaded_at", -1
        )
    )

    return papers


# ==========================================
# 8. GET ANALYSIS HISTORY
# ==========================================

def get_analysis_history():

    history = list(
        analysis_collection.find().sort(
            "created_at", -1
        )
    )

    return history


# ==========================================
# 9. GET TOTAL COUNTS
# ==========================================

def get_database_statistics():

    return {
        "total_papers": papers_collection.count_documents({}),
        "total_ideas": research_collection.count_documents({}),
        "total_analyses": analysis_collection.count_documents({})
    }


# ==========================================
# 10. TEST MONGODB CONNECTION
# ==========================================

def test_connection():

    try:

        client.admin.command("ping")

        print("\n================================")
        print(" MONGODB CONNECTION SUCCESSFUL")
        print("================================")

        print("Database:", DATABASE_NAME)

        print("\nCollections Ready:")

        print("1. research_ideas")
        print("2. research_papers")
        print("3. analysis_history")

        print("\nMongoDB is ready for ResearchIQ!")

        return True

    except Exception as error:

        print("\nMongoDB Connection Failed!")
        print("Error:", error)

        return False


# ==========================================
# 11. RUN CONNECTION TEST
# ==========================================

if __name__ == "__main__":

    test_connection()