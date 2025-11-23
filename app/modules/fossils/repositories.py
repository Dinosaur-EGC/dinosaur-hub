from app.modules.fossils.models import Fossils
from core.repositories.BaseRepository import BaseRepository


class FossilsRepository(BaseRepository):
    def __init__(self):
        super().__init__(Fossils)
