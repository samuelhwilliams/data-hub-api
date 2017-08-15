from django.conf import settings
from elasticsearch_dsl import Date, DocType, String

from .. import dict_utils
from .. import dsl_utils
from ..models import MapDBModelToDict


class Order(DocType, MapDBModelToDict):
    """Elasticsearch representation of Order model."""

    id = String(index='not_analyzed')
    reference = String(analyzer='lowercase_keyword_analyzer')
    company = dsl_utils._id_name_mapping()
    contact = dsl_utils._contact_mapping('contact')
    created_by = dsl_utils._contact_mapping('created_by')
    created_on = Date()
    primary_market = dsl_utils._id_name_mapping()
    sector = dsl_utils._id_name_mapping()
    description = String()
    contacts_not_to_approach = String()
    delivery_date = Date()
    service_types = dsl_utils._id_name_mapping()

    MAPPINGS = {
        'id': str,
        'company': dict_utils._id_name_dict,
        'contact': dict_utils._contact_dict,
        'created_by': dict_utils._contact_dict,
        'primary_market': dict_utils._id_name_dict,
        'sector': dict_utils._id_name_dict,
        'service_types': lambda col: [dict_utils._id_name_dict(c) for c in col.all()],
    }

    IGNORED_FIELDS = (
        'modified_by',
        'subscribers',
        'assignees',
        'modified_on',
        'product_info',
        'further_info',
        'existing_agents',
        'permission_to_approach_contacts',
    )

    SEARCH_FIELDS = []

    class Meta:
        """Default document meta data."""

        index = settings.ES_INDEX
        doc_type = 'order'
