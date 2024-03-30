def watchlist_count(request):
    count = 0
    if request.user.is_authenticated:
        count = request.user.watchlist.count()
    return {'watchlist_count': count}
