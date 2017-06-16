"""Investment views."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from datahub.core.mixins import ArchivableViewSetMixin
from datahub.core.viewsets import CoreViewSetV3
from datahub.investment.models import InvestmentProject, IProjectDocument
from datahub.investment.serializers import (
    IProjectAuditSerializer, IProjectRequirementsSerializer, IProjectSerializer,
    IProjectTeamSerializer, IProjectValueSerializer
)


class IProjectViewSet(ArchivableViewSetMixin, CoreViewSetV3):
    """Investment project views.

    This is a subset of the fields on an InvestmentProject object.
    """

    serializer_class = IProjectSerializer
    queryset = InvestmentProject.objects.select_related(
        'archived_by',
        'investment_type',
        'phase',
        'investor_company',
        'intermediate_company',
        'client_relationship_manager',
        'referral_source_adviser',
        'referral_source_activity',
        'referral_source_activity_website',
        'referral_source_activity_marketing',
        'fdi_type',
        'non_fdi_type',
        'sector'
    ).prefetch_related(
        'client_contacts',
        'business_activities'
    )
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('investor_company_id',)

    def get_view_name(self):
        """Returns the view set name for the DRF UI."""
        return 'Investment projects'

    @detail_route(methods=['post'])
    def document(self, request, *args, **kwargs):
        project = self.get_object()
        doc = IProjectDocument.create_from_declaration_request(
            project, request.data['field'], request.data['filename'],
        )
        return Response({
            'created': True,
        })


class IProjectAuditViewSet(CoreViewSetV3):
    """Investment Project audit views."""

    serializer_class = IProjectAuditSerializer
    queryset = InvestmentProject.objects.all()

    def get_view_name(self):
        """Returns the view set name for the DRF UI."""
        return 'Investment project audit log'


class IProjectValueViewSet(CoreViewSetV3):
    """Investment project value views.

    This is a subset of the fields on an InvestmentProject object.
    """

    serializer_class = IProjectValueSerializer
    queryset = InvestmentProject.objects.select_related('average_salary')

    def get_view_name(self):
        """Returns the view set name for the DRF UI."""
        return 'Investment project values'


class IProjectRequirementsViewSet(CoreViewSetV3):
    """Investment project requirements views.

    This is a subset of the fields on an InvestmentProject object.
    """

    serializer_class = IProjectRequirementsSerializer
    queryset = InvestmentProject.objects.prefetch_related(
        'competitor_countries',
        'uk_region_locations',
        'strategic_drivers'
    )

    def get_view_name(self):
        """Returns the view set name for the DRF UI."""
        return 'Investment project requirements'


class IProjectTeamViewSet(CoreViewSetV3):
    """Investment project team views.

    This is a subset of the fields on an InvestmentProject object.
    """

    serializer_class = IProjectTeamSerializer
    queryset = InvestmentProject.objects.select_related(
        'project_manager',
        'project_manager__dit_team',
        'project_assurance_adviser',
        'project_assurance_adviser__dit_team'
    )

    def get_view_name(self):
        """Returns the view set name for the DRF UI."""
        return 'Investment project teams'
