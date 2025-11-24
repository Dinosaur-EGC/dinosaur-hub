from app import db


class FossilsFile(db.Model):
    __tablename__ = 'fossils_file'
    id = db.Column(db.Integer, primary_key=True)
    data_set_id = db.Column(db.Integer, db.ForeignKey("data_set.id"), nullable=False)

    fossils_meta_data_id = db.Column(db.Integer, db.ForeignKey("fossils_meta_data.id"))

    files = db.relationship("Hubfile", backref="fossils_file", lazy=True, cascade="all, delete")
    fossils_meta_data = db.relationship("FossilsMetaData", uselist=False, backref="fossils_file", cascade="all, delete")

    def __repr__(self):
        return f'Fossils<{self.id}>'

class FossilsMetaData(db.Model):
    __tablename__ = 'fossils_meta_data'
    id = db.Column(db.Integer, primary_key=True)
    csv_filename = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)

    publication_doi = db.Column(db.String(120))
    tags = db.Column(db.String(120))

    def __repr__(self):
        return f'FossilsMetaData<{self.title}>'


