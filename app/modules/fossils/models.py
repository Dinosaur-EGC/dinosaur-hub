from app import db


class FossilFile(db.Model):
    __tablename__ = 'fossil_file'
    id = db.Column(db.Integer, primary_key=True)
    data_set_id = db.Column(db.Integer, db.ForeignKey("data_set.id"), nullable=False)
    fm_meta_data_id = db.Column(db.Integer, db.ForeignKey("fm_meta_data.id"))

    files = db.relationship("Hubfile", backref="fossil_file", lazy=True, cascade="all, delete")
    fm_meta_data = db.relationship("FMMetaData", uselist=False, backref="fossil_file", cascade="all, delete")

    def __repr__(self):
        return f'Fossils<{self.id}>'

class FossilMetaData(db.Model):
    __tablename__ = 'fossil_meta_data'
    id = db.Column(db.Integer, primary_key=True)
    csv_filename = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'FossilMetaData<{self.title}>'


