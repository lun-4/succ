HH_API = 'https://hypnohub.net'


class TagType:
    """Hypnohub tag types"""
    GENERAL = 0
    ARTIST = 1
    COPYRIGHT = 3
    CHARACTER = 4
    CIRCLE = 5
    FAULT = 6
    REVIEW = 69

# get them to hydrus namespaces
NAMESPACES = {
    TagType.ARTIST: 'creator:',
    TagType.COPYRIGHT: 'copyright:',
    TagType.CHARACTER: 'character:',
    TagType.REVIEW: 'review:'
}
