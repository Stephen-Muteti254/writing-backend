def paginate_query(query, page, limit):
    page = max(int(page) if page else 1, 1)
    limit = max(int(limit) if limit else 10, 1)
    items = query.offset((page-1)*limit).limit(limit).all()
    total = query.order_by(None).count()
    total_pages = (total + limit - 1) // limit
    return items, {"total": total, "page": page, "limit": limit, "total_pages": total_pages}
