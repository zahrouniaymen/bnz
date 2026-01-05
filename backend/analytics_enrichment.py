"""
New analytics CRUD functions for M54 enrichment
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
from datetime import datetime, timedelta
from typing import List, Optional
from backend import models, schemas


def get_user_performance(db: Session, user_id: int, period: str) -> Optional[models.UserPerformanceMetrics]:
    """Get performance metrics for a specific user and period"""
    return db.query(models.UserPerformanceMetrics).filter(
        models.UserPerformanceMetrics.user_id == user_id,
        models.UserPerformanceMetrics.period == period
    ).first()


def get_team_performance(db: Session, period: str) -> List[dict]:
    """Get performance metrics for all team members in a period with user names"""
    metrics = db.query(models.UserPerformanceMetrics).filter(
        models.UserPerformanceMetrics.period == period
    ).all()
    
    # Enrich with user names
    result = []
    for metric in metrics:
        user = db.query(models.User).filter(models.User.id == metric.user_id).first()
        metric_dict = {
            'user_id': metric.user_id,
            'user_name': user.full_name if user else f'User {metric.user_id}',
            'period': metric.period,
            'offers_handled': metric.offers_handled,
            'avg_processing_time_hours': metric.avg_processing_time_hours,
            'success_rate': metric.success_rate,
            'current_workload': metric.current_workload,
            'accepted_count': metric.accepted_count,
            'declined_count': metric.declined_count
        }
        result.append(metric_dict)
    
    return result


def calculate_workflow_timing_stats(db: Session, year: int):
    """Calculate timing statistics for each workflow phase"""
    # Get all workflow steps for the year
    steps = db.query(models.WorkflowStep).join(models.Offer).filter(
        models.Offer.year_stats == year
    ).all()
    
    # Group by department and calculate stats
    stats_by_phase = {}
    for step in steps:
        phase = step.department
        if phase not in stats_by_phase:
            stats_by_phase[phase] = {
                'durations': [],
                'bottlenecks': 0,
                'total': 0
            }
        
        stats_by_phase[phase]['total'] += 1
        if step.actual_duration_minutes:
            stats_by_phase[phase]['durations'].append(step.actual_duration_minutes / 60)
        if step.bottleneck_flag:
            stats_by_phase[phase]['bottlenecks'] += 1
    
    # Format results
    results = []
    for phase, data in stats_by_phase.items():
        durations = data['durations']
        results.append({
            'phase': phase,
            'avg_duration_hours': sum(durations) / len(durations) if durations else 0,
            'min_duration_hours': min(durations) if durations else 0,
            'max_duration_hours': max(durations) if durations else 0,
            'bottleneck_count': data['bottlenecks'],
            'total_steps': data['total']
        })
    
    return results


def get_bottleneck_alerts(db: Session, threshold_hours: float = 48):
    """Get offers that are stuck in workflow phases"""
    # Find workflow steps that exceed threshold
    alerts = []
    stuck_steps = db.query(models.WorkflowStep).filter(
        models.WorkflowStep.status == 'in_progress',
        models.WorkflowStep.bottleneck_flag == True
    ).all()
    
    for step in stuck_steps:
        if step.offer and step.actual_duration_minutes:
            duration_hours = step.actual_duration_minutes / 60
            if duration_hours > threshold_hours:
                alerts.append({
                    'offer_id': step.offer.id,
                    'offer_number': step.offer.offer_number or f"#{step.offer.id}",
                    'client_name': step.offer.client.name if step.offer.client else "Unknown",
                    'phase': step.department,
                    'duration_hours': duration_hours,
                    'threshold_hours': threshold_hours,
                    'assigned_user': step.assigned_user.full_name if step.assigned_user else None
                })
    
    return alerts


def calculate_seasonal_trends(db: Session, year: int):
    """Calculate monthly trends and seasonal patterns"""
    # Get monthly aggregates
    monthly_data = db.query(
        func.strftime('%Y-%m', models.Offer.mail_date).label('month'),
        func.count(models.Offer.id).label('total'),
        func.sum(case((models.Offer.status == 'ACCETTATA', 1), else_=0)).label('accepted'),
        func.sum(case((models.Offer.status == 'DECLINATA', 1), else_=0)).label('declined'),
        func.avg(models.Offer.offer_amount).label('avg_value')
    ).filter(
        models.Offer.year_stats == year
    ).group_by('month').all()
    
    trends = []
    for row in monthly_data:
        trends.append({
            'month': row.month,
            'total_offers': row.total,
            'accepted': row.accepted,
            'declined': row.declined,
            'avg_value': row.avg_value or 0,
            'prediction_next_month': None  # TODO: Implement prediction logic
        })
    
    return trends


def calculate_client_loyalty(db: Session, year: int):
    """Calculate loyalty metrics for all clients"""
    clients = db.query(models.Client).all()
    
    loyalty_data = []
    for client in clients:
        # Get offers for this client in the year
        offers = db.query(models.Offer).filter(
            models.Offer.client_id == client.id,
            models.Offer.year_stats == year
        ).all()
        
        if not offers:
            continue
        
        new_items = sum(1 for o in offers if o.is_new_item)
        reorders = len(offers) - new_items
        total = len(offers)
        
        # Get last order date
        last_order = max((o.order_date for o in offers if o.order_date), default=None)
        
        loyalty_data.append({
            'client_id': client.id,
            'client_name': client.name,
            'loyalty_score': client.loyalty_score,
            'new_items_count': new_items,
            'reorder_count': reorders,
            'total_offers': total,
            'reorder_percentage': (reorders / total * 100) if total > 0 else 0,
            'last_order_date': last_order
        })
    
    # Sort by loyalty score descending
    loyalty_data.sort(key=lambda x: x['loyalty_score'], reverse=True)
    
    return loyalty_data
