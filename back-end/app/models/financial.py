from app import db
from datetime import datetime
from sqlalchemy import text

class FinancialStatement(db.Model):
    __tablename__ = 'financial_statements'
    
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    company_name = db.Column(db.String(255))
    period_start = db.Column(db.Date)
    period_end = db.Column(db.Date)
    statement_type = db.Column(db.String(50))
    
    # Relationship to KPI metrics
    kpi_metrics = db.relationship('KPIMetric', backref='statement', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_name': self.file_name,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'company_name': self.company_name,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'statement_type': self.statement_type
        }

class KPIMetric(db.Model):
    __tablename__ = 'kpi_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    statement_id = db.Column(db.Integer, db.ForeignKey('financial_statements.id'), nullable=False)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Numeric(15, 2))
    metric_category = db.Column(db.String(50))
    calculation_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'statement_id': self.statement_id,
            'metric_name': self.metric_name,
            'metric_value': float(self.metric_value) if self.metric_value else None,
            'metric_category': self.metric_category,
            'calculation_date': self.calculation_date.isoformat() if self.calculation_date else None
        }



class Investments (db.Model):
    __tablename__ = 'investments'

    id = db.Column(db.Integer, primary_key=True)
    portfolio = db.Column(db.String(15), nullable=False)
    investment = db.Column(db.String(100), nullable=False)
    tracker_id = db.Column(db.String(15), nullable=False)
    units = db.Column(db.Numeric(15, 2))
    cost = db.Column(db.Numeric(15, 2))
    value = db.Column(db.Numeric(15, 2))
    date_of_valuation = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'portfolio': self.portfolio,
            'investment': self.investment,
            'tracker_id': self.tracker_id,
            'units': self.units,
            'cost': self.cost,
            'value': self.value,
            'valn_date': self.date_of_valuation
        }


    