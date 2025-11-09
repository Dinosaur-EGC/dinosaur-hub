from app.modules.profile.repositories import UserProfileRepository
from core.services.BaseService import BaseService


class UserProfileService(BaseService):
    def __init__(self):
        super().__init__(UserProfileRepository())

    def update_profile(self, user_profile_id, form):
        if form.validate():
            updated_instance = self.update(user_profile_id, **form.data)
            return updated_instance, None

        return None, form.errors

    def get_user_profile(self, user_id):
        from app.modules.auth.models import User
        user = User.query.get(user_id)
        if user:
            return user.profile
        return None
