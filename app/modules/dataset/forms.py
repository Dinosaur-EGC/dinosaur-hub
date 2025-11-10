from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import FieldList, FormField, SelectField, StringField, SubmitField, TextAreaField, RadioField
from wtforms.validators import URL, DataRequired, Optional
import re

from app.modules.dataset.models import PublicationType


class AuthorForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    affiliation = StringField("Affiliation")
    orcid = StringField("ORCID")
    gnd = StringField("GND")

    class Meta:
        csrf = False  # disable CSRF because is subform

    def get_author(self):
        return {
            "name": self.name.data,
            "affiliation": self.affiliation.data,
            "orcid": self.orcid.data,
        }


class FeatureModelForm(FlaskForm):
    uvl_filename = StringField("UVL Filename", validators=[DataRequired()])
    title = StringField("Title", validators=[Optional()])
    desc = TextAreaField("Description", validators=[Optional()])
    publication_type = SelectField(
        "Publication type",
        choices=[(pt.value, pt.name.replace("_", " ").title()) for pt in PublicationType],
        validators=[Optional()],
    )
    publication_doi = StringField("Publication DOI", validators=[Optional()])
    tags = StringField("Tags (separated by commas)")
    version = StringField("UVL Version")
    authors = FieldList(FormField(AuthorForm))

    class Meta:
        csrf = False  # disable CSRF because is subform

    def get_authors(self):
        return [author.get_author() for author in self.authors]

    def get_fmmetadata(self):
        return {
            "uvl_filename": self.uvl_filename.data,
            "title": self.title.data,
            "description": self.desc.data,
            "publication_type": self.publication_type.data,
            "publication_doi": self.publication_doi.data,
            "tags": self.tags.data,
            "uvl_version": self.version.data,
        }


class DataSetForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    desc = TextAreaField("Description", validators=[DataRequired()])
    publication_type = SelectField(
        "Publication type",
        choices=[(pt.value, pt.name.replace("_", " ").title()) for pt in PublicationType],
        validators=[DataRequired()],
    )
    publication_doi = StringField("Publication DOI", validators=[Optional()])
    dataset_doi = StringField("Dataset DOI", validators=[Optional()])
    tags = StringField("Tags (separated by commas)")
    authors = FieldList(FormField(AuthorForm))

    import_method = RadioField(
        'Model Source',
        choices=[
            ('manual', 'Manual File Upload'),
            ('zip', 'Upload ZIP Archive'),
            ('github', 'Import from GitHub')
        ],
        default='manual',
        validators=[DataRequired()]
    )

    # --- Campo para subir el ZIP ---
    zip_file = FileField(
        'ZIP Archive',
        validators=[
            Optional(),
            FileAllowed(['zip'], 'Only .zip files are allowed!')
        ]
    )
    
    # --- Campo para la URL de GitHub ---
    github_url = StringField(
        'GitHub Repository URL',
        validators=[
            Optional(),
            URL()
        ],
        render_kw={"placeholder": "https://github.com/user/repo"}
    )

    # --- Lista de Modelos Manuales ---
    feature_models = FieldList(FormField(FeatureModelForm), min_entries=0)

    submit = SubmitField("Submit")

    # --- Validación personalizada ---
    def validate(self, extra_validators=None):
        if not super(DataSetForm, self).validate(extra_validators):
            return False

        is_valid = True
        method = self.import_method.data

        if method == 'manual':
            if not self.feature_models.data:
                self.feature_models.errors.append('At least one feature model is required for manual upload.')
                is_valid = False
        
        elif method == 'zip':
            if not self.zip_file.data:
                self.zip_file.errors.append('A ZIP file is required for this import method.')
                is_valid = False

        elif method == 'github':
            if not self.github_url.data:
                self.github_url.errors.append('A GitHub URL is required for this import method.')
                is_valid = False
            elif not re.match(r'^https://github\.com/[^/]+/[^/]+/?$', self.github_url.data):
                self.github_url.errors.append('Invalid GitHub URL. Must be like https://github.com/user/repo')
                is_valid = False
        
        return is_valid

    def get_dsmetadata(self):

        publication_type_converted = self.convert_publication_type(self.publication_type.data)

        return {
            "title": self.title.data,
            "description": self.desc.data,
            "publication_type": publication_type_converted,
            "publication_doi": self.publication_doi.data,
            "dataset_doi": self.dataset_doi.data,
            "tags": self.tags.data,
        }

    def convert_publication_type(self, value):
        for pt in PublicationType:
            if pt.value == value:
                return pt.name
        return "NONE"

    def get_authors(self):
        return [author.get_author() for author in self.authors]

    def get_feature_models(self):
        return [fm.get_feature_model() for fm in self.feature_models]
