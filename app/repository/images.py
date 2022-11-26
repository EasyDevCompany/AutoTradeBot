from .base import RepositoryBase
from sqlalchemy import or_


from app.models.images import Images
from app.models.order import Order


class RepositoryImages(RepositoryBase[Images]):

    def get_assembled_or_in_work_images(self):
        return self._session.query(self._model).filter(
            or_(
                self._model.image_status == Images.ImageStatus.assembled,
                self._model.image_status == Images.ImageStatus.in_work,
            )
        ).all()

