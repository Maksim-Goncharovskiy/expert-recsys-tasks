from app.database import db_manager
from .svdpp_recsys import SVDppRecSys, ColdStartError


recsys = SVDppRecSys(db_manager=db_manager, n_epochs=15, lr_alpha=1.0)