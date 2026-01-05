from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
from typing import List, Dict
import backend.models as models
import backend.schemas as schemas
from datetime import datetime

def get_monthly_evolution(db: Session, year: int) -> List[schemas.MonthlyEvolution]:
    """Calculate monthly stats for a specific year"""
    # SQLite friendly month extraction
    
    # Number of requests (all offers created/received in that year)
    requests = db.query(
        func.strftime('%m', models.Offer.mail_date).label('month'),
        func.count(models.Offer.id).label('count')
    ).filter(models.Offer.year_stats == year).group_by(func.strftime('%m', models.Offer.mail_date)).all()

    # Proposed (all except pending registration)
    proposed = db.query(
        func.strftime('%m', models.Offer.mail_date).label('month'),
        func.count(models.Offer.id).label('count')
    ).filter(
        models.Offer.year_stats == year,
        models.Offer.status != models.OfferStatus.PENDING_REGISTRATION
    ).group_by(func.strftime('%m', models.Offer.mail_date)).all()

    # Accepted (using offer_amount as order value fallback)
    accepted = db.query(
        func.strftime('%m', models.Offer.mail_date).label('month'),
        func.count(models.Offer.id).label('count'),
        func.sum(models.Offer.offer_amount).label('value')
    ).filter(
        models.Offer.year_stats == year,
        models.Offer.status == models.OfferStatus.ACCETTATA
    ).group_by(func.strftime('%m', models.Offer.mail_date)).all()
    
    # Declined/Not accepted
    declined = db.query(
        func.strftime('%m', models.Offer.mail_date).label('month'),
        func.count(models.Offer.id).label('count')
    ).filter(
        models.Offer.year_stats == year,
        models.Offer.status.in_([models.OfferStatus.DECLINATA, models.OfferStatus.NON_ACCETTATA])
    ).group_by(func.strftime('%m', models.Offer.mail_date)).all()

    # Aggregate by month
    months_data = {}
    for i in range(1, 13):
        months_data[i] = {
            "month": datetime(year, i, 1).strftime('%B'),
            "year": year,
            "requests": 0,
            "proposed": 0,
            "accepted": 0,
            "declined": 0,
            "total_value": 0.0,
            "order_value": 0.0
        }

    for r in requests: 
        if r.month: months_data[int(r.month)]["requests"] = r.count
    for p in proposed: 
        if p.month: months_data[int(p.month)]["proposed"] = p.count
    for a in accepted:
        if a.month:
            months_data[int(a.month)]["accepted"] = a.count
            months_data[int(a.month)]["order_value"] = float(a.value or 0)
    for d in declined: 
        if d.month: months_data[int(d.month)]["declined"] = d.count

    return [schemas.MonthlyEvolution(**v) for v in months_data.values()]


def get_comparison_data(db: Session, years: List[int]) -> Dict[str, List[dict]]:
    """Get aggregated stats for multiple years for comparison charts"""
    metrics = {
        "requests": [],
        "declined": [],
        "proposed": [],
        "accepted": [],
        "order_value": []
    }
    
    # Prepare 12 buckets for each metric
    for k in metrics:
        metrics[k] = [{"month": datetime(2000, i, 1).strftime('%B')} for i in range(1, 13)]
        for item in metrics[k]:
            for y in years:
                item[str(y)] = 0

    for year in years:
        # 1. Requests
        data = db.query(
            func.strftime('%m', models.Offer.mail_date).label('m'), 
            func.count(models.Offer.id).label('c')
        ).filter(models.Offer.year_stats == year).group_by(func.strftime('%m', models.Offer.mail_date)).all()
        for r in data: 
            if r.m: metrics["requests"][int(r.m)-1][str(year)] = r.c
            
        # 2. Declined
        data = db.query(
            func.strftime('%m', models.Offer.mail_date).label('m'), 
            func.count(models.Offer.id).label('c')
        ).filter(
            models.Offer.year_stats == year, 
            models.Offer.status.in_([models.OfferStatus.DECLINATA, models.OfferStatus.NON_ACCETTATA])
        ).group_by(func.strftime('%m', models.Offer.mail_date)).all()
        for r in data: 
            if r.m: metrics["declined"][int(r.m)-1][str(year)] = r.c

        # 3. Proposed
        data = db.query(
            func.strftime('%m', models.Offer.mail_date).label('m'), 
            func.count(models.Offer.id).label('c')
        ).filter(
            models.Offer.year_stats == year, 
            models.Offer.status != models.OfferStatus.PENDING_REGISTRATION
        ).group_by(func.strftime('%m', models.Offer.mail_date)).all()
        for r in data: 
            if r.m: metrics["proposed"][int(r.m)-1][str(year)] = r.c

        # 4. Accepted
        data = db.query(
            func.strftime('%m', models.Offer.mail_date).label('m'), 
            func.count(models.Offer.id).label('c')
        ).filter(
            models.Offer.year_stats == year, 
            models.Offer.status == models.OfferStatus.ACCETTATA
        ).group_by(func.strftime('%m', models.Offer.mail_date)).all()
        for r in data: 
            if r.m: metrics["accepted"][int(r.m)-1][str(year)] = r.c

        # 5. Value (using offer_amount)
        data = db.query(
            func.strftime('%m', models.Offer.mail_date).label('m'), 
            func.sum(models.Offer.offer_amount).label('v')
        ).filter(
            models.Offer.year_stats == year, 
            models.Offer.status == models.OfferStatus.ACCETTATA
        ).group_by(func.strftime('%m', models.Offer.mail_date)).all()
        for r in data: 
            if r.m: metrics["order_value"][int(r.m)-1][str(year)] = float(r.v or 0)
            
    return metrics


def get_reasons_stats(db: Session, year: int) -> schemas.ReasonsAnalysis:
    """Analyze reasons for declining/not accepting"""
    # Declined Reasons
    declined_q = db.query(
        models.Offer.declined_reason,
        func.count(models.Offer.id)
    ).filter(
        models.Offer.year_stats == year,
        models.Offer.status == models.OfferStatus.DECLINATA
    ).group_by(models.Offer.declined_reason).all()
    
    total_declined = sum(c for r, c in declined_q)
    declined_stats = []
    for reason, count in declined_q:
        if reason:
            declined_stats.append(schemas.ReasonStat(
                reason=reason.value,
                count=count,
                percentage=(count / total_declined * 100) if total_declined > 0 else 0
            ))

    # Not Accepted Reasons (text based)
    not_accepted_q = db.query(
        models.Offer.not_accepted_reason,
        func.count(models.Offer.id)
    ).filter(
        models.Offer.year_stats == year,
        models.Offer.status == models.OfferStatus.NON_ACCETTATA
    ).group_by(models.Offer.not_accepted_reason).all()

    total_na = sum(c for r, c in not_accepted_q)
    na_stats = []
    for reason, count in not_accepted_q:
        if reason:
            na_stats.append(schemas.ReasonStat(
                reason=reason,
                count=count,
                percentage=(count / total_na * 100) if total_na > 0 else 0
            ))
            
    return schemas.ReasonsAnalysis(
        declined_reasons=declined_stats,
        not_accepted_reasons=na_stats
    )


def get_client_ranking(db: Session, year: int) -> List[schemas.ClientRanking]:
    """Get top clients for the year with detailed stats"""
    ranking = db.query(
        models.Client.name,
        func.count(models.Offer.id).label('requests'),
        func.sum(case((models.Offer.status != models.OfferStatus.PENDING_REGISTRATION, 1), else_=0)).label('proposed'),
        func.sum(case((models.Offer.status == models.OfferStatus.ACCETTATA, 1), else_=0)).label('accepted'),
        func.sum(case((models.Offer.status == models.OfferStatus.DECLINATA, 1), else_=0)).label('declined'),
        func.sum(case((models.Offer.status == models.OfferStatus.NON_ACCETTATA, 1), else_=0)).label('not_accepted'),
        func.sum(case((models.Offer.status == models.OfferStatus.ACCETTATA, models.Offer.offer_amount), else_=0)).label('total_value')
    ).join(models.Offer).filter(
        models.Offer.year_stats == year
    ).group_by(models.Client.name).order_by(func.sum(case((models.Offer.status == models.OfferStatus.ACCETTATA, models.Offer.offer_amount), else_=0)).desc()).limit(50).all()

    result = []
    for r in ranking:
        result.append(schemas.ClientRanking(
            client_name=r.name,
            requests=r.requests,
            proposed=r.proposed,
            accepted=r.accepted,
            declined=r.declined,
            not_accepted=r.not_accepted,
            total_value=float(r.total_value or 0),
            success_rate=(r.accepted / r.requests * 100) if r.requests > 0 else 0
        ))
    return result


def get_sector_distribution(db: Session, year: int) -> List[Dict]:
    """Calculate revenue and offer count per business sector"""
    data = db.query(
        models.Client.sector,
        func.count(models.Offer.id).label('count'),
        func.sum(models.Offer.offer_amount).label('value')
    ).join(models.Offer).filter(
        models.Offer.year_stats == year
    ).group_by(models.Client.sector).all()

    return [
        {
            "sector": d.sector or "Altro",
            "count": d.count,
            "value": float(d.value or 0)
        } for d in data
    ]


def get_new_vs_reorder_stats(db: Session, year: int) -> Dict:
    """Compare New Article vs Re-order (Riordine) stats"""
    data = db.query(
        models.Offer.is_new_item,
        func.count(models.Offer.id).label('count'),
        func.sum(models.Offer.offer_amount).label('value')
    ).filter(
        models.Offer.year_stats == year
    ).group_by(models.Offer.is_new_item).all()

    stats = {"new": {"count": 0, "value": 0.0}, "reorder": {"count": 0, "value": 0.0}}
    
    for item in data:
        key = "new" if item.is_new_item else "reorder"
        stats[key]["count"] = item.count
        stats[key]["value"] = float(item.value or 0)
        
    return stats
