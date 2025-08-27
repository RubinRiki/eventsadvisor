# Export view classes so you can: from views import SearchView, DetailsView, ...
from .search_view import SearchView
from .details_view import DetailsView
from .charts_view import ChartsView
from .consult_view import ConsultView

__all__ = ["SearchView", "DetailsView", "ChartsView", "ConsultView"]
