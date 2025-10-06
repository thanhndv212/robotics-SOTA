import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List

from app.models import Lab, Paper


_COUNTRY_REGION_FALLBACK = {
    "United States": "North America",
    "USA": "North America",
    "Canada": "North America",
    "Mexico": "North America",
    "United Kingdom": "Europe",
    "UK": "Europe",
    "Germany": "Europe",
    "France": "Europe",
    "Switzerland": "Europe",
    "Sweden": "Europe",
    "Denmark": "Europe",
    "Italy": "Europe",
    "Spain": "Europe",
    "Portugal": "Europe",
    "Netherlands": "Europe",
    "Belgium": "Europe",
    "Norway": "Europe",
    "Finland": "Europe",
    "Austria": "Europe",
    "Poland": "Europe",
    "Czech Republic": "Europe",
    "Hungary": "Europe",
    "Greece": "Europe",
    "China": "Asia",
    "Japan": "Asia",
    "South Korea": "Asia",
    "Singapore": "Asia",
    "Taiwan": "Asia",
    "Hong Kong": "Asia",
    "India": "Asia",
    "Australia": "Oceania",
    "New Zealand": "Oceania",
}


def _to_list(value: Any) -> List[str]:
    """Safely coerce a potential JSON/text field to a list of strings."""

    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [
                    str(item).strip() for item in parsed if str(item).strip()
                ]
        except json.JSONDecodeError:
            # Fallback to comma-separated plain text
            return [part.strip() for part in value.split(",") if part.strip()]

    return []


def _simpson_diversity(counter: Counter) -> float:
    """Compute a normalized Simpson diversity index (0..1)."""

    total = sum(counter.values())
    if total == 0:
        return 0.0

    simpson = 1.0 - sum((count / total) ** 2 for count in counter.values())
    return round(simpson, 3)


def _group_by_region(countries: Iterable[str]) -> Counter:
    """Group countries into high-level regions via a lightweight mapping."""

    region_counter: Counter = Counter()

    for country in countries:
        if not country:
            continue

        region = _COUNTRY_REGION_FALLBACK.get(country, "Other")
        region_counter[region] += 1

    return region_counter


def summarize_labs(labs: Iterable[Lab]) -> Dict[str, Any]:
    """Return aggregate statistics about labs."""

    lab_list: List[Lab] = list(labs)

    by_type = Counter((lab.lab_type or "independent") for lab in lab_list)
    by_country = Counter((lab.country or "Unknown") for lab in lab_list)
    by_institution = Counter(
        (lab.institution or "Unknown") for lab in lab_list
    )

    focus_counter: Counter = Counter()
    focus_by_country: Dict[str, Counter] = defaultdict(Counter)

    now = datetime.utcnow()
    recent_cutoff = now - timedelta(days=30)
    updated_last_30 = 0
    created_last_30 = 0

    for lab in lab_list:
        areas = (
            lab.focus_areas_list
            if hasattr(lab, "focus_areas_list")
            else _to_list(lab.focus_areas)
        )
        for area in areas:
            focus_counter[area] += 1
            if lab.country:
                focus_by_country[lab.country][area] += 1

        created_at = getattr(lab, "created_at", None)
        updated_at = getattr(lab, "updated_at", None) or created_at
        if created_at and created_at >= recent_cutoff:
            created_last_30 += 1
        if updated_at and updated_at >= recent_cutoff:
            updated_last_30 += 1

    regions = _group_by_region(lab.country for lab in lab_list)

    return {
        "total": len(lab_list),
        "by_type": dict(by_type),
        "total_countries": len(
            [country for country in by_country if country != "Unknown"]
        ),
        "countries": [
            {"country": country, "count": count}
            for country, count in by_country.most_common(12)
        ],
        "top_institutions": [
            {"institution": institution, "count": count}
            for institution, count in by_institution.most_common(12)
        ],
        "focus_counter": dict(focus_counter),
        "focus_by_country": {
            country: dict(counter)
            for country, counter in focus_by_country.items()
        },
        "regions": [
            {"region": region, "count": count}
            for region, count in regions.most_common()
        ],
        "recent_activity": {
            "created_last_30_days": created_last_30,
            "updated_last_30_days": updated_last_30,
        },
        "recent": [
            {
                "id": lab.id,
                "name": lab.name,
                "institution": lab.institution,
                "updated_at": (
                    lab.updated_at.isoformat() if lab.updated_at else None
                ),
            }
            for lab in sorted(
                lab_list,
                key=lambda item: (
                    item.updated_at or item.created_at or datetime.min
                ),
                reverse=True,
            )[:10]
        ],
    }


def summarize_papers(papers: Iterable[Paper]) -> Dict[str, Any]:
    """Return aggregate statistics about papers."""

    paper_list: List[Paper] = list(papers)
    today = datetime.utcnow().date()

    by_venue = Counter((paper.venue or "Unknown") for paper in paper_list)
    by_year = Counter()
    research_counter: Counter = Counter()

    recent_cutoff = today - timedelta(days=30)
    last_30_days = 0

    recent_entries: List[Dict[str, Any]] = []

    for paper in paper_list:
        # Track publication year distribution
        if paper.publication_date:
            by_year[paper.publication_date.year] += 1
            if paper.publication_date >= recent_cutoff:
                last_30_days += 1

        # Collect research areas
        for area in _to_list(paper.research_areas):
            research_counter[area] += 1

        # Build payload for up to 10 most recent
        recent_entries.append(
            {
                "id": paper.id,
                "title": paper.title,
                "lab_id": paper.lab_id,
                "publication_date": (
                    paper.publication_date.isoformat()
                    if paper.publication_date
                    else None
                ),
                "venue": paper.venue,
                "citation_count": paper.citation_count,
            }
        )

    recent_entries.sort(
        key=lambda item: item["publication_date"] or "1970-01-01",
        reverse=True,
    )

    return {
        "total": len(paper_list),
        "last_30_days": last_30_days,
        "top_venues": [
            {"venue": venue, "count": count}
            for venue, count in by_venue.most_common(10)
        ],
        "top_research_areas": [
            {"name": name, "count": count}
            for name, count in research_counter.most_common(12)
        ],
        "timeline": [
            {"year": year, "count": count}
            for year, count in sorted(
                by_year.items(),
                key=lambda item: item[0],
                reverse=True,
            )
        ],
        "recent": recent_entries[:10],
    }


def summarize_focus_areas(lab_summary: Dict[str, Any]) -> Dict[str, Any]:
    """Transform focus area counters into UI-friendly structures."""

    raw_focus = lab_summary.get("focus_counter", {})
    focus_counter: Counter = Counter(raw_focus)
    total_focus_mentions = sum(focus_counter.values()) or 1

    top_focus = [
        {"name": name, "count": count}
        for name, count in focus_counter.most_common(15)
    ]

    heatmap = []
    for country, counter in lab_summary.get("focus_by_country", {}).items():
        entries = sorted(
            counter.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:5]
        heatmap.append(
            {
                "country": country,
                "focus": [
                    {"name": name, "count": count} for name, count in entries
                ],
            }
        )

    return {
        "top": top_focus,
        "diversity_index": _simpson_diversity(focus_counter),
        "share": [
            {
                "name": item["name"],
                "percent": round(
                    (item["count"] / total_focus_mentions) * 100,
                    2,
                ),
            }
            for item in top_focus
        ],
        "heatmap": heatmap,
    }


def build_lab_summary_payload(labs: Iterable[Lab]) -> Dict[str, Any]:
    """Compose a lab-focused analytics payload for API responses."""

    lab_summary = summarize_labs(labs)
    focus_summary = summarize_focus_areas(lab_summary)

    return {
        "total": lab_summary["total"],
        "by_type": lab_summary["by_type"],
        "total_countries": lab_summary["total_countries"],
        "top_countries": lab_summary["countries"],
        "top_institutions": lab_summary["top_institutions"],
        "regions": lab_summary["regions"],
        "recently_updated": lab_summary["recent"],
        "recent_activity": lab_summary["recent_activity"],
        "focus": {
            "top": focus_summary["top"],
            "diversity_index": focus_summary["diversity_index"],
            "share": focus_summary["share"],
            "heatmap": focus_summary["heatmap"],
        },
    }


def build_dashboard_overview(
    labs: Iterable[Lab],
    papers: Iterable[Paper],
) -> Dict[str, Any]:
    """Compose a holistic dashboard response for the frontend."""

    lab_summary = summarize_labs(labs)
    paper_summary = summarize_papers(papers)
    focus_summary = summarize_focus_areas(lab_summary)

    return {
        "meta": {
            "generated_at": datetime.utcnow().isoformat(),
            "lab_count": lab_summary["total"],
            "paper_count": paper_summary["total"],
        },
        "labs": {
            key: value
            for key, value in lab_summary.items()
            if key not in {"focus_counter", "focus_by_country"}
        },
        "papers": paper_summary,
        "focus_areas": focus_summary,
        "geography": {
            "regions": lab_summary["regions"],
            "countries": lab_summary["countries"],
        },
    }
