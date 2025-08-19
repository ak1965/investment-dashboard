from flask import Blueprint, jsonify, request
from app import db
from app.models.financial import FinancialStatement, KPIMetric, CurryHouse 
from datetime import datetime
from sqlalchemy import text
from run_report_data import query_investment_data,populate_from_csv
from flask import send_file
import os
from app.models.financial import Investments

api = Blueprint('api', __name__, url_prefix='/api')

# GET: Retrieve all financial statements
@api.route('/statements', methods=['GET'])
def get_statements():
    try:
        statements = FinancialStatement.query.all()
        return jsonify({
            'success': True,
            'data': [stmt.to_dict() for stmt in statements],
            'count': len(statements)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# GET: Retrieve KPI metrics for a specific statement
@api.route('/statements/<int:statement_id>/kpis', methods=['GET'])
def get_kpis(statement_id):
    try:
        kpis = KPIMetric.query.filter_by(statement_id=statement_id).all()
        return jsonify({
            'success': True,
            'data': [kpi.to_dict() for kpi in kpis],
            'count': len(kpis)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# POST: Add a new financial statement
@api.route('/statements', methods=['POST'])
def add_statement():
    try:
        data = request.get_json()
        
        new_statement = FinancialStatement(
            file_name=data.get('file_name'),
            company_name=data.get('company_name'),
            period_start=datetime.strptime(data.get('period_start'), '%Y-%m-%d').date() if data.get('period_start') else None,
            period_end=datetime.strptime(data.get('period_end'), '%Y-%m-%d').date() if data.get('period_end') else None,
            statement_type=data.get('statement_type')
        )
        
        db.session.add(new_statement)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Financial statement added successfully',
            'data': new_statement.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# POST: Add a new KPI metric
@api.route('/kpis', methods=['POST'])
def add_kpi():
    try:
        data = request.get_json()
        
        new_kpi = KPIMetric(
            statement_id=data.get('statement_id'),
            metric_name=data.get('metric_name'),
            metric_value=data.get('metric_value'),
            metric_category=data.get('metric_category')
        )
        
        db.session.add(new_kpi)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'KPI metric added successfully',
            'data': new_kpi.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# GET: Dashboard summary data
@api.route('/dashboard', methods=['GET'])
def dashboard_summary():
    try:
        total_statements = FinancialStatement.query.count()
        total_kpis = KPIMetric.query.count()
        
        # Get recent statements
        recent_statements = FinancialStatement.query.order_by(
            FinancialStatement.upload_date.desc()
        ).limit(5).all()
        
        # Get profitability KPIs
        profit_kpis = KPIMetric.query.filter_by(
            metric_category='profitability'
        ).limit(5).all()
        
        return jsonify({
            'success': True,
            'summary': {
                'total_statements': total_statements,
                'total_kpis': total_kpis,
                'recent_statements': [stmt.to_dict() for stmt in recent_statements],
                'recent_kpis': [kpi.to_dict() for kpi in profit_kpis]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/restaurants', methods=['GET'])
def get_curry_house():
    try:
        # Debug: Check if table exists before querying
        table_check = db.session.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'andrews_curry'
        """)).fetchone()
        
        if not table_check:
            return jsonify({'error': 'andrews_curry table not found'}), 500
        
        print("Table exists, attempting query...")    
        statements = CurryHouse.query.all()
        print(f"Query successful, found {len(statements)} records")
        
        return jsonify({
            'success': True,
            'data': [stmt.to_dict() for stmt in statements],
            'count': len(statements)
        })
    except Exception as e:
        print(f"Error in get_curry_house: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/restaurants/<int:restaurant_id>', methods=['DELETE'])
def delete_curry_house(restaurant_id):
    try:
        # Find the restaurant by ID
        restaurant = CurryHouse.query.get(restaurant_id)
        
        if not restaurant:
            return jsonify({
                'success': False, 
                'error': 'Restaurant not found'
            }), 404
        
        # Delete the restaurant
        db.session.delete(restaurant)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Restaurant with ID {restaurant_id} deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()  # Important: rollback on error
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500
    

@api.route('/curry', methods=['POST'])
def add_curry_house():
    try:
        data = request.get_json()
        
        new_statement = CurryHouse(
            name=data.get('restaurant'),
            location=data.get('location'),
            website=data.get('website'),
            score=data.get('score')
        )

        
        
        db.session.add(new_statement)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Curry House added successfully',
            'data': new_statement.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

import os
from flask import jsonify



@api.route('/investment-files', methods=['GET'])
def get_investment_files():
    try:
        directory = r'C:\Users\AndrewKnott\Projects\Investments'
        files = []
        
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                if filename.endswith('.csv'):
                    files.append({
                        'name': filename,
                        'path': os.path.join(directory, filename)
                    })
        
        return jsonify({
            'success': True,
            'files': files,
            'count': len(files)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500  

@api.route('/process-investment', methods=['POST'])
def process_investment_file():
    try:
        print("=== Starting process_investment_file ===")
        data = request.get_json()
        print(f"Received data: {data}")
        
        selected_file = data.get('filename')
        portfolio_name = data.get('portfolio', 'Shares')
        selected_date_str = data.get('date')
        
        print(f"Filename: {selected_file}")
        print(f"Portfolio: {portfolio_name}")
        print(f"Date string: {selected_date_str}")
        
        if not selected_file:
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not selected_date_str:
            return jsonify({'success': False, 'error': 'No date selected'}), 400
        
        # Convert string date to date object
        from datetime import datetime
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        print(f"Parsed date: {selected_date}")
        
        # Build full path
        full_path = f'C:/Users/AndrewKnott/Projects/Investments/{selected_file}'
        print(f"Full path: {full_path}")
        
        # Import and call function
        from populate_data import populate_from_csv
        print("About to call populate_from_csv")
        populate_from_csv(full_path, portfolio_name, selected_date)
        print("populate_from_csv completed successfully")
        
        return jsonify({
            'success': True,
            'message': f'Successfully processed {selected_file}',
            'data': {
                'file_processed': selected_file,
                'portfolio': portfolio_name,
                'date_processed': selected_date_str
            }
        })
        
    except Exception as e:
        print(f"ERROR in process_investment_file: {str(e)}")
        print(f"ERROR type: {type(e).__name__}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# @api.route('/generate-pdf', methods=['GET'])
# def generate_pdf_report():
#     try:
#         print("Generating PDF from database data...")
        
#         # Specify full path for PDF
#         pdf_filename = f"investment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
#         pdf_full_path = os.path.join(r'C:\Users\AndrewKnott\Projects\Investments', pdf_filename)
        
#         from run_report_data import generate_pdf_from_sql_data
#         pdf_path = generate_pdf_from_sql_data(pdf_full_path)  # Pass full path
        
#         print(f"PDF generated at: {pdf_path}")  # Debug print
        
#         # Check if file exists
#         if not os.path.exists(pdf_path):
#             raise FileNotFoundError(f"PDF was not created at {pdf_path}")
        
#         return send_file(
#             pdf_path,
#             as_attachment=True,
#             download_name=pdf_filename,
#             mimetype='application/pdf'
#         )
        
#     except Exception as e:
#         print(f"Error generating PDF: {str(e)}")
#         import traceback
#         traceback.print_exc()  # This will show the full error
#         return jsonify({'success': False, 'error': str(e)}), 500
    
@api.route('/investment-history/<string:company_name>', methods=['GET'])
def get_investment_history(company_name):
    try:
        # Query your database for the specific company's valuations over time
        history = db.session.query(
            Investments.date_of_valuation,
            Investments.value
        ).filter(
            Investments.investment == company_name
        ).order_by(
            Investments.date_of_valuation
        ).all()
        
        # Format the data for the frontend
        formatted_data = []
        for record in history:
            # Handle both datetime and date objects
            if hasattr(record.date_of_valuation, 'date'):
                # It's a datetime object
                date_str = record.date_of_valuation.date().strftime('%Y-%m-%d')
            else:
                # It's already a date object
                date_str = record.date_of_valuation.strftime('%Y-%m-%d')
            
            formatted_data.append({
                'date': date_str,
                'value': float(record.value) if record.value else 0
            })
        
        return jsonify({
            'success': True,
            'company': company_name,
            'data': formatted_data
        })
        
    except Exception as e:
        print(f"Error in get_investment_history: {e}")  # Debug line
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/companies', methods=['GET'])
def get_companies():
    try:
        # Get unique company names from your investments table
        companies = db.session.query(Investments.investment).distinct().all()
        
        # Extract company names from query result
        company_list = [company[0] for company in companies if company[0]]
        
        return jsonify({
            'success': True,
            'companies': sorted(company_list)  # Sort alphabetically
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/stock-data/<string:symbol>', methods=['GET'])
def get_stock_data(symbol):
    try:
        # Your Alpha Vantage API key
        api_key = "153TPL2JUDBYVGSH"  # Replace with your actual key
        
        # Optional: Get period from query parameters (default to 100 days)
        outputsize = request.args.get('outputsize', 'compact')  # 'compact' or 'full'
        
        # Alpha Vantage API URL
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': outputsize,
            'apikey': api_key
        }
        
        print(f"Fetching stock data for: {symbol}")
        
        # Make API request
        response = requests.get(url, params=params)
        data = response.json()
        
        # Check for API errors
        if "Error Message" in data:
            return jsonify({
                'success': False, 
                'error': f'Invalid symbol: {symbol}'
            }), 400
        
        if "Note" in data:
            return jsonify({
                'success': False, 
                'error': 'API rate limit exceeded. Try again in a minute.'
            }), 429
        
        # Extract time series data
        time_series_key = "Time Series (Daily)"
        if time_series_key not in data:
            return jsonify({
                'success': False, 
                'error': 'No data available for this symbol'
            }), 404
        
        time_series = data[time_series_key]
        
        # Format data for frontend
        formatted_data = []
        for date_str, daily_data in time_series.items():
            formatted_data.append({
                'date': date_str,
                'open': float(daily_data['1. open']),
                'high': float(daily_data['2. high']),
                'low': float(daily_data['3. low']),
                'close': float(daily_data['4. close']),
                'volume': int(daily_data['5. volume'])
            })
        
        # Sort by date (newest first)
        formatted_data.sort(key=lambda x: x['date'], reverse=True)
        
        # Get metadata
        metadata = data.get("Meta Data", {})
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'data': formatted_data,
            'metadata': {
                'symbol': metadata.get('2. Symbol', symbol),
                'last_refreshed': metadata.get('3. Last Refreshed', ''),
                'timezone': metadata.get('5. Time Zone', 'US/Eastern')
            },
            'count': len(formatted_data)
        })
        
    except requests.RequestException as e:
        return jsonify({
            'success': False, 
            'error': f'API request failed: {str(e)}'
        }), 500
    except Exception as e:
        print(f"Error in get_stock_data: {e}")
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500
    
# Add this new endpoint to your Flask API
@api.route('/unique-dates', methods=['GET'])
def get_unique_dates():
    """
    Returns unique valuation dates from the investments table
    """
    try:
        # Query to get unique dates, ordered by date descending (most recent first)
        unique_dates = db.session.query(
            db.func.date(Investments.date_of_valuation).label('date')
        ).distinct().order_by(
            db.func.date(Investments.date_of_valuation).desc()
        ).all()
        
        # Convert to list of date strings
        dates_list = [date.date.strftime('%Y-%m-%d') for date in unique_dates]
        
        return jsonify({
            'success': True,
            'dates': dates_list
        })
        
    except Exception as e:
        print(f"Error fetching unique dates: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Update your existing generate-pdf endpoint to accept date parameter
@api.route('/generate-pdf', methods=['GET'])
def generate_pdf_report():
    try:
        # Get optional date parameter
        selected_date = request.args.get('date')  # Format: YYYY-MM-DD
        
        print(f"Generating PDF from database data for date: {selected_date or 'all dates'}...")
        
        # Specify full path for PDF
        date_suffix = f"_{selected_date}" if selected_date else "_all"
        pdf_filename = f"investment_report{date_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_full_path = os.path.join(r'C:\Users\AndrewKnott\Projects\Investments', pdf_filename)
        
        from run_report_data import generate_pdf_from_sql_data
        
        # Pass the selected date to the PDF generation function
        pdf_path = generate_pdf_from_sql_data(pdf_full_path, selected_date=selected_date)
        
        print(f"PDF generated at: {pdf_path}")
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF was not created at {pdf_path}")
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=pdf_filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

