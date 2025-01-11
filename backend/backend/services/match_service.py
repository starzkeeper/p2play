from backend.repositories.match_repository import MatchRepository
from backend.schemas.game_schema import IMAGE_MAPS, Map
from backend.schemas.response_schema import DefaultApiResponse, ApiStatus


class MatchService:
    def __init__(self, match_repository: MatchRepository) -> None:
        self.match_repository = match_repository

    @staticmethod
    async def get_all_maps():
        res = [{"name": map, 'image': IMAGE_MAPS[map]} for map in Map]
        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message=res
        )

    async def get_match(self, user_id: str):
        res = await self.match_repository.get_match(user_id)
        return DefaultApiResponse(
            status=ApiStatus.SUCCESS,
            message=res
        )

    async def ban_map(self, user, map_name):

