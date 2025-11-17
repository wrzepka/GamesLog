def has_uppercase(str):
    for char in str:
        if char.isupper():
            return True
    return False


def has_number(str):
    for char in str:
        if char.isdigit():
            return True
    return False


def has_special(str):
    if not str.isalnum():
        return True
    return False

def summarize_games(games_json):
    data = []

    for game in games_json:
        rating = game.get('total_rating') if game.get('total_rating') is not None else None
        cover = game.get('cover') if game.get('cover') is not None else None

        img_id = None
        if cover is not None:
            img_id = cover.get('image_id')

        if rating is not None:
            rating = int(round(rating))

        data.append({
            'id': game['id'],
            'name': game['name'],
            'rating': rating,
            'img_id': img_id
        })

    return data