from app.models.job import Type

SHORTS = "/shorts/"

def get_video_type(url: str) -> Type:
    if SHORTS in url:
        return Type.SHORT
    return Type.VIDEO
