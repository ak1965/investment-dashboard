import csv
from datetime import datetime
from app import create_app, db
from app.models.financial import Investments

def populate_from_csv(full_path, portfolio_name):
    app = create_app()
    
    with app.app_context():
        # Skip the first 10 rows
        
        with open(full_path, 'r') as file:
            for _ in range(10):
                next(file)
            
            csv_reader = csv.DictReader(file)
            rows = list(csv_reader)
            
            for row in rows:
                # Skip empty rows or totals/footer rows
                if not row['Stock'] or row['Stock'] == 'Totals' or not row['Code']:
                    continue
                
                # Clean numeric values - remove commas
                def clean_numeric(value):
                    if value and value.strip():
                        return float(value.replace(',', ''))
                    return None
                
                statement = Investments(
                    investment=row['Stock'],
                    tracker_id=row['Code'],
                    units=clean_numeric(row['Units held']),
                    cost=clean_numeric(row['Cost (£)']),
                    value=clean_numeric(row['Value (£)']),
                    date_of_valuation=datetime.now(),
                    portfolio= portfolio_name
                )
                
                db.session.add(statement)
            
            db.session.commit()
            print(f"Successfully populated records")

# if __name__ == '__main__':
#     # filename = input("Enter filename (e.g., HL_ISA010825): ")
#     # portfolio_name = input("Enter portfolio name (e.g., ISA): ")
    
#     # full_path = f'C:/Users/AndrewKnott/Projects/Investments/{filename}.csv'
#     populate_from_csv(full_path, portfolio_name)