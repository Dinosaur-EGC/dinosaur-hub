from app.modules.fossils.repositories import FossilsRepository
from core.services.BaseService import BaseService


class FossilsService(BaseService):
    def __init__(self):
        super().__init__(FossilsRepository())
