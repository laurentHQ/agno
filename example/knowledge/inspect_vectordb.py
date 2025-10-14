"""🔍 Inspect LanceDB Vector Database

This script helps you inspect and debug your LanceDB vector database to verify:
- Whether the database exists and has data
- Number of documents/chunks stored
- Sample data from the knowledge base
- Database schema and metadata

Usage:
    python inspect_vectordb.py
"""

import os
from pathlib import Path

try:
    import lancedb
    from agno.knowledge.embedder.openai import OpenAIEmbedder
    from agno.knowledge.knowledge import Knowledge
    from agno.vectordb.lancedb import LanceDb, SearchType
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Install dependencies: pip install agno lancedb openai")
    exit(1)


def inspect_lancedb():
    """Inspect the LanceDB vector database."""

    print("\n" + "="*80)
    print("🔍 LanceDB Vector Database Inspector")
    print("="*80 + "\n")

    # Database path
    db_path = "tmp/lancedb"
    table_name = "deep_knowledge_kb"

    # Check if database directory exists
    print(f"📁 Database Path: {db_path}")
    if not Path(db_path).exists():
        print(f"❌ Database directory does not exist!")
        print(f"   The knowledge base has not been initialized yet.")
        print(f"\n💡 Run 'python deep_knowledge.py' or 'python deep_knowledge_os.py' first to create it.\n")
        return

    print(f"✅ Database directory exists\n")

    # Connect to LanceDB directly
    print(f"🔗 Connecting to LanceDB...")
    try:
        db = lancedb.connect(db_path)
        print(f"✅ Connected successfully\n")
    except Exception as e:
        print(f"❌ Failed to connect: {e}\n")
        return

    # List all tables
    print(f"📊 Available Tables:")
    tables = db.table_names()
    if not tables:
        print(f"   ❌ No tables found in database")
        print(f"   The knowledge base exists but has no data.\n")
        return

    for i, tbl in enumerate(tables, 1):
        print(f"   {i}. {tbl}")
    print()

    # Check if our specific table exists
    if table_name not in tables:
        print(f"⚠️  Table '{table_name}' not found!")
        print(f"   Available tables: {', '.join(tables)}")
        print(f"   Check the table_name in your code.\n")
        return

    # Open the table
    print(f"📖 Opening table: {table_name}")
    try:
        table = db.open_table(table_name)
        print(f"✅ Table opened successfully\n")
    except Exception as e:
        print(f"❌ Failed to open table: {e}\n")
        return

    # Get table statistics
    print(f"📈 Table Statistics:")
    try:
        count = table.count_rows()
        print(f"   • Total rows/chunks: {count}")

        if count == 0:
            print(f"\n❌ Table is empty! No documents have been loaded.")
            print(f"\n💡 Possible reasons:")
            print(f"   1. Knowledge base initialization failed")
            print(f"   2. URL download failed")
            print(f"   3. Document processing/chunking failed")
            print(f"\n🔧 Try deleting and recreating:")
            print(f"   rm -rf {db_path}")
            print(f"   python deep_knowledge_os.py\n")
            return

        print(f"   • Table is populated ✅\n")

    except Exception as e:
        print(f"   ❌ Failed to get row count: {e}\n")
        return

    # Get schema
    print(f"🏗️  Table Schema:")
    try:
        schema = table.schema
        for field in schema:
            print(f"   • {field.name}: {field.type}")
        print()
    except Exception as e:
        print(f"   ❌ Failed to get schema: {e}\n")

    # Sample some data
    print(f"📄 Sample Data (first 3 rows):")
    try:
        sample = table.to_pandas().head(3)

        for idx, row in sample.iterrows():
            print(f"\n   Row {idx + 1}:")

            # Show text/content
            if 'content' in row:
                content = str(row['content'])[:200]
                print(f"   📝 Content: {content}...")
            elif 'text' in row:
                text = str(row['text'])[:200]
                print(f"   📝 Text: {text}...")

            # Show metadata if available
            if 'meta_data' in row and row['meta_data']:
                print(f"   🏷️  Metadata: {row['meta_data']}")
            elif 'metadata' in row and row['metadata']:
                print(f"   🏷️  Metadata: {row['metadata']}")

            # Show if vector exists
            if 'vector' in row:
                vec = row['vector']
                if vec is not None:
                    if hasattr(vec, '__len__'):
                        print(f"   🔢 Vector dimension: {len(vec)}")
                    else:
                        print(f"   🔢 Vector: exists")

        print()

    except Exception as e:
        print(f"   ❌ Failed to sample data: {e}\n")

    # Test search capability using Agno's Knowledge wrapper
    print(f"🔍 Testing Search Capability:")
    try:
        knowledge = Knowledge(
            vector_db=LanceDb(
                uri=db_path,
                table_name=table_name,
                search_type=SearchType.hybrid,
                embedder=OpenAIEmbedder(id="text-embedding-3-small"),
            ),
        )

        # Check if exists using Agno's method
        exists = knowledge.vector_db.exists()
        print(f"   • knowledge.vector_db.exists(): {exists}")

        if exists and count > 0:
            print(f"   ✅ Knowledge base is ready for searches!\n")
        else:
            print(f"   ⚠️  Knowledge base exists but may have issues\n")

    except Exception as e:
        print(f"   ❌ Failed to initialize Knowledge: {e}\n")

    # Summary
    print("="*80)
    print("📊 Summary:")
    print(f"   Database: {db_path}")
    print(f"   Table: {table_name}")
    print(f"   Total documents/chunks: {count}")
    print(f"   Status: {'✅ Ready' if count > 0 else '❌ Empty'}")
    print("="*80 + "\n")


def check_api_key():
    """Check if OpenAI API key is set."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Warning: OPENAI_API_KEY not set")
        print("   Set it with: export OPENAI_API_KEY='your-key'\n")
        return False
    print(f"✅ OPENAI_API_KEY is set (ends with: ...{api_key[-4:]})\n")
    return True


if __name__ == "__main__":
    check_api_key()
    inspect_lancedb()

    print("\n💡 Tips:")
    print("   • If empty, run: python deep_knowledge_os.py")
    print("   • To reset: rm -rf tmp/lancedb && python deep_knowledge_os.py")
    print("   • Check logs for download/embedding errors")
    print()
