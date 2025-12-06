from sqlalchemy import func

from app.modules.fossils.models import FossilsFile, FossilsMetaData
from core.repositories.BaseRepository import BaseRepository


class FossilsRepository(BaseRepository):
    def __init__(self):
        super().__init__(FossilsFile)

    def count_feature_models(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0

class FossilsMetaDataRepository(BaseRepository):
    def __init__(self):
        super().__init__(FossilsMetaData)
