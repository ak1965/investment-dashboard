from app import create_app, db
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from sqlalchemy import text
from populate_data import populate_from_csv
import csv
from app.models.financial import Investments

def import_csv_to_database(filename, portfolio_name):
    """
    Import CSV file to database - complete function
    """
    app = create_app()
    
    with app.app_context():
        # Create table if it doesn't exist
        db.create_all()
        print("Database tables created/verified")
        
        # Build full path to CSV file
        full_path = f'C:/Users/AndrewKnott/Projects/Investments/{filename}'
        print(f"Opening file: {full_path}")
        
        try:
            # Skip the first 10 rows (header information)
            with open(full_path, 'r') as file:
                for _ in range(10):
                    next(file)
                
                csv_reader = csv.DictReader(file)
                rows = list(csv_reader)
                print(f"Found {len(rows)} rows in CSV")
                
                imported_count = 0
                
                for row in rows:
                    # Skip empty rows or totals/footer rows
                    if not row['Stock'] or row['Stock'] == 'Totals' or not row['Code']:
                        continue
                    
                    # Clean numeric values - remove commas
                    def clean_numeric(value):
                        if value and value.strip():
                            return float(value.replace(',', ''))
                        return None
                    
                    # Create investment record
                    statement = Investments(
                        investment=row['Stock'],
                        tracker_id=row['Code'],
                        units=clean_numeric(row['Units held']),
                        cost=clean_numeric(row['Cost (£)']),
                        value=clean_numeric(row['Value (£)']),
                        date_of_valuation=datetime.now(),
                        portfolio=portfolio_name
                    )
                    
                    db.session.add(statement)
                    imported_count += 1
                
                # Commit all records at once
                db.session.commit()
                print(f"Successfully imported {imported_count} investment records to database")
                
                return {
                    'success': True,
                    'imported_count': imported_count,
                    'filename': filename,
                    'portfolio': portfolio_name
                }
                
        except FileNotFoundError:
            error_msg = f"File not found: {full_path}"
            print(error_msg)
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            db.session.rollback()  # Rollback on error
            error_msg = f"Error importing CSV: {str(e)}"
            print(error_msg)
            return {'success': False, 'error': error_msg}



def query_investment_data(selected_date=None):
    """
    Query investment data from database with optional date filter
    
    Args:
        selected_date: Date filter in YYYY-MM-DD format (optional)
    
    Returns:
        tuple: (investment_data, totals)
    """
    # Import your database and model - adjust these imports to match your actual structure
    # Look at your existing working imports in your Flask app and copy them here
   
    
    try:
        # Build base query
        query = db.session.query(Investments)
        
        # Apply date filter if provided
        if selected_date:
            # Convert string date to datetime for comparison
            from datetime import datetime
            target_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            
            # Filter by date (assuming date_of_valuation is stored as datetime)
            query = query.filter(
                db.func.date(Investments.date_of_valuation) == target_date
            )
        
        # Execute query
        investments = query.all()
        
        # Group by investment name and sum up units, costs, and values
        investment_dict = {}
        
        for inv in investments:
            stock_name = inv.investment
            cost = float(inv.cost or 0)
            value = float(inv.value or 0)
            units = float(inv.units or 0)
            
            if stock_name not in investment_dict:
                investment_dict[stock_name] = {
                    'total_units': 0,
                    'total_cost': 0,
                    'total_value': 0
                }
            
            investment_dict[stock_name]['total_units'] += units
            investment_dict[stock_name]['total_cost'] += cost
            investment_dict[stock_name]['total_value'] += value
        
        # Convert to list format and calculate profits/returns
        investment_data = []
        total_cost = 0
        total_value = 0
        
        for stock_name, data in investment_dict.items():
            cost = data['total_cost']
            value = data['total_value']
            profit = value - cost
            percent_return = (profit / cost * 100) if cost > 0 else 0
            
            investment_data.append({
                'stock_name': stock_name,
                'total_units': data['total_units'],
                'total_cost': cost,
                'total_value': value,
                'profit_pounds': profit,
                'percent_return': percent_return
            })
            
            total_cost += cost
            total_value += value
        
        # Calculate totals
        total_profit = total_value - total_cost
        total_return = (total_profit / total_cost * 100) if total_cost > 0 else 0
        
        totals = {
            'total_cost': total_cost,
            'total_value': total_value,
            'total_profit': total_profit,
            'total_return': total_return
        }
        
        return investment_data, totals
        
    except Exception as e:
        print(f"Error querying investment data: {str(e)}")
        raise

def generate_pdf_from_sql_data(output_filename="investment_report.pdf", investment_data=None, totals=None, selected_date=None):
    """
    Generate PDF report using the raw SQL data
    
    Args:
        output_filename: Name of the output PDF file
        investment_data: Pre-fetched investment data (optional)
        totals: Pre-calculated totals (optional)
        selected_date: Date filter in YYYY-MM-DD format (optional)
    """
    # Get data from SQL query with optional date filter
    if investment_data is None or totals is None:
        investment_data, totals = query_investment_data(selected_date)
    
    # Create PDF
    doc = SimpleDocTemplate(output_filename, pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Title with date information
    if selected_date:
        title_text = f"Investment Portfolio Report - {selected_date}"
    else:
        title_text = "Investment Portfolio Report - All Dates"
    
    title = Paragraph(title_text, title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Date
    date_style = ParagraphStyle('DateStyle', parent=styles['Normal'], fontSize=10, alignment=1)
    date_para = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style)
    story.append(date_para)
    story.append(Spacer(1, 30))
    
    # Create table data - headers
    table_data = [
        ['Stock', 'Units', 'Cost (£)', 'Value (£)', 'Profit (£)', '% Return']
    ]
    
    # Add data rows
    for item in investment_data:
        table_data.append([
            # Truncate long stock names for PDF
            item['stock_name'][:35] + '...' if len(item['stock_name']) > 35 else item['stock_name'],
            f"{item['total_units']:,.1f}",
            f"{item['total_cost']:,.2f}",
            f"{item['total_value']:,.2f}",
            f"{item['profit_pounds']:,.2f}",
            f"{item['percent_return']:.1f}%"
        ])
    
    # Add totals row
    table_data.append([
        'TOTAL',
        '',
        f"{totals['total_cost']:,.2f}",
        f"{totals['total_value']:,.2f}",
        f"{totals['total_profit']:,.2f}",
        f"{totals['total_return']:.1f}%"
    ])
    
    # Create table
    table = Table(table_data, colWidths=[2.8*inch, 0.7*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
    
    # Style table
    table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 8),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Numbers right-aligned
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # Stock names left-aligned
        
        # Totals row
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 9),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightblue]),
        
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    # Color code profits/losses
    for i, item in enumerate(investment_data, 1):
        if item['profit_pounds'] < 0:
            # Red for losses
            table.setStyle(TableStyle([
                ('TEXTCOLOR', (4, i), (5, i), colors.red),
            ]))
        else:
            # Green for profits
            table.setStyle(TableStyle([
                ('TEXTCOLOR', (4, i), (5, i), colors.green),
            ]))
    
    story.append(table)
    
    # Summary
    story.append(Spacer(1, 30))
    summary_style = ParagraphStyle('SummaryStyle', parent=styles['Normal'], fontSize=12, spaceAfter=10)
    
    profitable_count = len([x for x in investment_data if x['profit_pounds'] > 0])
    losing_count = len([x for x in investment_data if x['profit_pounds'] < 0])
    
    # Add date information to summary
    date_info = f"Report Date: {selected_date}<br/>" if selected_date else "Report: All Historical Data<br/>"
    
    summary_text = f"""
    <b>Portfolio Summary:</b><br/>
    {date_info}
    Total Stocks: {len(investment_data)}<br/>
    Profitable: {profitable_count}<br/>
    Loss-making: {losing_count}<br/>
    Overall Portfolio Return: {totals['total_return']:.2f}%<br/>
    Total Profit/Loss: £{totals['total_profit']:,.2f}
    """
    
    summary = Paragraph(summary_text, summary_style)
    story.append(summary)
    
    # Build PDF
    doc.build(story)
    
    return output_filename




if __name__ == '__main__':
    # Option 1: Just run the SQL query and see results
    # print("=== SQL QUERY RESULTS ===")
    # just_run_sql_query()
    
    # Option 2: Generate PDF report
    print("\n=== GENERATING PDF ===")
    pdf_file = generate_pdf_from_sql_data("my_investment_report.pdf")
    print(f"PDF saved as: {pdf_file}")