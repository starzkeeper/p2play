from backend.domain.common.base_enum import BaseStrEnum


class Map(BaseStrEnum):
    DUST2 = 'dust2'
    ANUBIS = 'anubis'
    MIRAGE = 'mirage'
    INFERNO = 'inferno'
    VERTIGO = 'vertigo'
    NUKE = 'nuke'
    ANCIENT = 'ancient'


IMAGE_MAPS = {
    Map.DUST2: 'https://example-bucket.s3.amazonaws.com/maps/dust2.jpg',
    Map.ANUBIS: 'https://example-bucket.s3.amazonaws.com/maps/anubis.jpg',
    Map.MIRAGE: 'https://example-bucket.s3.amazonaws.com/maps/mirage.jpg',
    Map.INFERNO: 'https://example-bucket.s3.amazonaws.com/maps/inferno.jpg',
    Map.VERTIGO: 'https://example-bucket.s3.amazonaws.com/maps/vertigo.jpg',
    Map.NUKE: 'https://example-bucket.s3.amazonaws.com/maps/nuke.jpg',
    Map.ANCIENT: 'https://example-bucket.s3.amazonaws.com/maps/ancient.jpg',
}
