COMMENT_WEIGHT = 0.5


def signal_score(points: int, num_comments: int) -> float:
    """페인포인트 신호 강도. points + comments × 0.5"""
    return points + num_comments * COMMENT_WEIGHT


def sort_by_signal(hits: list[dict]) -> list[dict]:
    return sorted(
        hits,
        key=lambda h: signal_score(h.get("points") or 0, h.get("num_comments") or 0),
        reverse=True,
    )
