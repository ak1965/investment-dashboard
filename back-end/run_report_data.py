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



def query_investment_data():
    """
    Get investment data using raw SQL - with proper text() wrapper
    """
    app = create_app()
    
    
    with app.app_context():        
       
        raw_sql = text("""
        SELECT 
            
            investment as stock_name,
            SUM(units) as total_units,
            SUM(cost) as total_cost,
            SUM(value) as total_value,
            (SUM(value) - SUM(cost)) as profit_pounds,
            ((SUM(value) - SUM(cost)) / SUM(cost)) * 100 as percent_return
        FROM investments 
        GROUP BY investment
        ORDER BY profit_pounds DESC
        """)
        
        results = db.session.execute(raw_sql).fetchall()
        
        # print("=== INVESTMENT SUMMARY ===")
        # print(f"{'Stock':<40} {'Units':<10} {'Cost (£)':<12} {'Value (£)':<12} {'Profit (£)':<12} {'Return %':<10}")
        # print("-" * 100)
        
        # Convert results to list of dictionaries for easy handling
        data = []
        total_cost_all = 0
        total_value_all = 0
        
        for result in results:
            stock_data = {
                
                'stock_name': result.stock_name,
                'total_units': float(result.total_units or 0),
                'total_cost': float(result.total_cost or 0),
                'total_value': float(result.total_value or 0),
                'profit_pounds': float(result.profit_pounds or 0),
                'percent_return': float(result.percent_return or 0)
            }
            
            data.append(stock_data)
            total_cost_all += stock_data['total_cost']
            total_value_all += stock_data['total_value']
            
            # Print to console
            # print(f"{stock_data['stock_name'][:39]:<40} "
            #       f"{stock_data['total_units']:>9.2f} "
            #       f"{stock_data['total_cost']:>11.2f} "
            #       f"{stock_data['total_value']:>11.2f} "
            #       f"{stock_data['profit_pounds']:>11.2f} "
            #       f"{stock_data['percent_return']:>8.2f}%")
        
        # Calculate and print totals
        total_profit_all = total_value_all - total_cost_all
        total_return_all = (total_profit_all / total_cost_all * 100) if total_cost_all > 0 else 0
        
        # print("-" * 100)
        # print(f"{'TOTALS':<40} "
        #       f"{'':>10} "
        #       f"{total_cost_all:>11.2f} "
        #       f"{total_value_all:>11.2f} "
        #       f"{total_profit_all:>11.2f} "
        #       f"{total_return_all:>8.2f}%")
        
        return data, {
            'total_cost': total_cost_all,
            'total_value': total_value_all,
            'total_profit': total_profit_all,
            'total_return': total_return_all
        }

def generate_pdf_from_sql_data(output_filename="investment_report.pdf", investment_data=None, totals=None):
    """
    Generate PDF report using the raw SQL data
    """
    # Get data from SQL query
    if investment_data is None or totals is None:
        investment_data, totals = query_investment_data()
    
    
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
    
    # Title
    title = Paragraph("Investment Portfolio Report", title_style)
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
    
    summary_text = f"""
    <b>Portfolio Summary:</b><br/>
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
    
    # print(f"\nPDF Report Generated: {output_filename}")
    # print(f"Portfolio Value: £{totals['total_value']:,.2f}")
    # print(f"Total Profit/Loss: £{totals['total_profit']:,.2f}")
    # print(f"Overall Return: {totals['total_return']:.2f}%")
    
    return output_filename

def just_run_sql_query():
    """
    If you just want to see the SQL results without PDF
    """
    investment_data, totals = query_investment_data()
    
    # print(f"\nSummary:")
    # print(f"Total stocks: {len(investment_data)}")
    # print(f"Best performer: {investment_data[0]['stock_name']} (£{investment_data[0]['profit_pounds']:.2f})")
    # print(f"Worst performer: {investment_data[-1]['stock_name']} (£{investment_data[-1]['profit_pounds']:.2f})")
    
    return investment_data

if __name__ == '__main__':
    # Option 1: Just run the SQL query and see results
    # print("=== SQL QUERY RESULTS ===")
    # just_run_sql_query()
    
    # Option 2: Generate PDF report
    print("\n=== GENERATING PDF ===")
    pdf_file = generate_pdf_from_sql_data("my_investment_report.pdf")
    print(f"PDF saved as: {pdf_file}")