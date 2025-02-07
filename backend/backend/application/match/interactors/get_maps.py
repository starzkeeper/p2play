from dataclasses import dataclass

from backend.application.common.interactor import Interactor
from backend.domain.common.game_schema import IMAGE_MAPS, Map


@dataclass
class MapsOutputDTO:
    maps: dict[str, str]


class GetMaps(Interactor[None, MapsOutputDTO]):
    def __init__(self):
        pass

    async def __call__(self, data: None = None) -> MapsOutputDTO:
        maps_dict = {str(map_enum): IMAGE_MAPS[map_enum] for map_enum in Map}
        return MapsOutputDTO(maps=maps_dict)
