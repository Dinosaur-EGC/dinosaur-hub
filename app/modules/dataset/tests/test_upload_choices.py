import io
import zipfile
import pytest
from unittest.mock import MagicMock, patch, mock_open
from app.modules.dataset.services import DataSetService
from app.modules.dataset.models import DataSet

class TestDatasetUploadChoices:

    @pytest.fixture
    def service(self):
        service = DataSetService()
        service.repository = MagicMock()
        service.dsmetadata_repository = MagicMock()
        service.author_repository = MagicMock()
        service.fossils_repository = MagicMock()
        service.fossils_metadata_repository = MagicMock()
        service.hubfilerepository = MagicMock()
        return service

    @pytest.fixture
    def mock_user(self):
        user = MagicMock()
        user.id = 1
        user.profile.name = "John"
        user.profile.surname = "Doe"
        user.profile.affiliation = "Dino University"
        user.profile.orcid = "0000-0000-0000-0000"
        user.temp_folder.return_value = "/tmp/mock_user_1"
        return user

    @pytest.fixture
    def mock_form(self):
        form = MagicMock()
        form.get_dsmetadata.return_value = {"title": "Test Dataset"}
        form.get_authors.return_value = []
        return form

    @pytest.fixture
    def mock_zip_file(self):
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('data.csv', 'col1,col2\n1,2')
            zf.writestr('ignored.txt', 'this should be ignored')
        output.seek(0)
        return output
    
    
    '''
    UPLOAD FROM ZIP
    '''

    def test_create_from_zip_success(self, service, mock_user, mock_form, mock_zip_file):
        mock_form.zip_file.data = mock_zip_file

        service.create = MagicMock()
        
        mock_dataset = MagicMock(spec=DataSet)
        mock_dataset.id = 10
        service.create.return_value = mock_dataset

        with patch("app.modules.dataset.services.os.makedirs"), \
             patch("app.modules.dataset.services.open", mock_open()) as mocked_file, \
             patch("app.modules.dataset.services.calculate_checksum_and_size", return_value=("md5hash", 123)), \
             patch("app.modules.dataset.services.os.path.exists", return_value=True):
            result_dataset = service.create_from_zip(mock_form, mock_user)

            assert result_dataset == service.create.return_value
            
            service.dsmetadata_repository.create.assert_called()
            service.author_repository.create.assert_called()
            
            mocked_file.assert_called()
            
            service.fossils_repository.create.assert_called()
            service.hubfilerepository.create.assert_called_with(
                commit=False, 
                name='data.csv', 
                checksum='md5hash', 
                size=123, 
                fossils_file_id=service.fossils_repository.create.return_value.id
            )

            service.repository.session.commit.assert_called_once()

    def test_create_from_zip_invalid_file(self, service, mock_user, mock_form):
        invalid_file = io.BytesIO(b"Not a zip file")
        mock_form.zip_file.data = invalid_file

        with pytest.raises(ValueError, match="not a valid ZIP"):
            service.create_from_zip(mock_form, mock_user)
    
        service.repository.session.rollback.assert_called_once()

    def test_create_from_zip_exception_handling(self, service, mock_user, mock_form, mock_zip_file):
        mock_form.zip_file.data = mock_zip_file
        service.dsmetadata_repository.create.side_effect = Exception("Database Error")

        with pytest.raises(Exception, match="Database Error"):
            service.create_from_zip(mock_form, mock_user)

        service.repository.session.rollback.assert_called_once()


    '''
    UPLOAD FROM GITHUB
    '''

    @patch("app.modules.dataset.services.requests.get")
    def test_create_from_github_success(self, mock_get, service, mock_user, mock_form, mock_zip_file):
        github_url = "https://github.com/user/repo"
        mock_form.github_url.data = github_url

        mock_response_api = MagicMock()
        mock_response_api.status_code = 200
        mock_response_api.json.return_value = {'default_branch': 'main'}
        
        mock_response_zip = MagicMock()
        mock_response_zip.status_code = 200
        mock_response_zip.content = mock_zip_file.getvalue()

        mock_get.side_effect = [mock_response_api, mock_response_zip]

        with patch("app.modules.dataset.services.os.makedirs"), \
             patch("app.modules.dataset.services.open", mock_open()), \
             patch("app.modules.dataset.services.calculate_checksum_and_size", return_value=("hash", 100)), \
             patch("app.modules.dataset.services.os.path.exists", return_value=True):

            service.create_from_github(mock_form, mock_user)

            mock_get.assert_any_call(
                "https://api.github.com/repos/user/repo", 
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            mock_get.assert_any_call(
                "https://github.com/user/repo/archive/refs/heads/main.zip", 
                stream=True
            )
            service.repository.session.commit.assert_called_once()