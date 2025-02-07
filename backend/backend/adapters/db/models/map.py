from backend.adapters.db.models.friend import map_friendships_table
from backend.adapters.db.models.user import map_users_table


def map_tables():
    map_users_table()
    map_friendships_table()
