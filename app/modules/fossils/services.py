from app.modules.fossils.repositories import FossilsMetaDataRepository, FossilsRepository
from core.services.BaseService import BaseService
from app.modules.hubfile.services import HubfileService


class FossilsService(BaseService):
    def __init__(self):
        super().__init__(FossilsRepository())
        self.hubfile_service = HubfileService()
    
    def count_fossils_files(self):
        return self.repository.count()

    def total_fossils_file_downloads(self):
        return self.hubfile_service.total_hubfile_downloads()

    def total_fossils_file_views(self):
        return self.hubfile_service.total_hubfile_views()
    
    class FossilsMetaDataService(BaseService):
        def __init__(self):
            super().__init__(FossilsMetaDataRepository())
