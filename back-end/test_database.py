from app import create_app, db
from sqlalchemy import text  # Add this import

def test_database_connection():
    app = create_app()
    with app.app_context():
        # Check current database (wrap in text())
        result = db.session.execute(text("SELECT current_database();")).fetchone()
        print(f"Connected to database: {result[0]}")
        
        # List all tables (wrap in text())
        tables = db.session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)).fetchall()
        
        print("Available tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if andrews_curry exists and has data (wrap in text())
        try:
            result = db.session.execute(text("SELECT COUNT(*) FROM andrews_curry;")).fetchone()
            print(f"andrews_curry table has {result[0]} rows")
            
            # Show first few rows (wrap in text())
            rows = db.session.execute(text("SELECT * FROM andrews_curry LIMIT 3;")).fetchall()
            print("Sample data:")
            for row in rows:
                print(f"  {row}")
                
        except Exception as e:
            print(f"andrews_curry table error: {e}")

if __name__ == '__main__':
    test_database_connection()