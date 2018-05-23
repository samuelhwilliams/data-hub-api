from typing import Sequence

from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.utils.timezone import now

from datahub.core.exceptions import DataHubException

_registry = {}


class _ReportMeta(type):
    """
    Metaclass for report definitions.

    Used to auto-register report definitions.
    """

    def __new__(mcs, name, bases, namespace, **kwargs):  # noqa: N804
        """
        Creates the metaclass instance.

        Called whenever a subclass of Report is defined.
        """
        is_abstract = namespace.pop('abstract', False)
        cls = type.__new__(mcs, name, bases, namespace)
        if not is_abstract:
            cls.register()
        return cls


class Report(metaclass=_ReportMeta):
    """
    Base class for reports.

    See QuerySetReport for reports based on a QuerySet.
    """

    id: str = None
    name: str = None
    model: Model = None
    permissions_required: Sequence = None
    field_titles: dict = None
    filename_template = '{name} - {today}'
    abstract = True

    _required_attrs = (
        'id',
        'name',
        'model',
        'permissions_required',
        'field_titles',
    )

    @classmethod
    def register(cls):
        """Called on class declaration to register the report."""
        cls._validate_attrs()
        _registry[cls.id] = cls()

    def check_permission(self, user):
        """Checks whether the user has permission for this report."""
        return user.has_perms(self.permissions_required)

    def get_filename(self):
        """Gets the filename (excluding extension) to use for the report."""
        today = now().date().isoformat()
        return self.filename_template.format(name=self.name, today=today)

    def rows(self):
        """Returns an iterator of the rows for this report."""
        raise NotImplementedError

    @classmethod
    def _validate_attrs(cls):
        missing_attrs = [attr for attr in cls._required_attrs if getattr(cls, attr, None) is None]
        if missing_attrs:
            raise DataHubException(f'Required report attributes {missing_attrs} not set')


class QuerySetReport(Report):
    """Base class for reports based on a QuerySet."""

    queryset = None
    abstract = True

    _required_attrs = (
        *Report._required_attrs,
        'queryset',
    )

    def rows(self):
        """Returns an iterator of the rows for this report."""
        return self.queryset.values(*self.field_titles.keys()).iterator()


def get_reports_by_model(user):
    """
    Returns a dictionary mapping models to list of reports.

    Only reports that the user is allowed to access are returned.
    """
    reports_by_model = {}

    for report in _registry.values():
        if report.check_permission(user):
            reports_for_model = reports_by_model.setdefault(report.model, [])
            reports_for_model.append(report)

    return reports_by_model


def report_exists(report_id):
    """Checks if a report exists."""
    return report_id in _registry


def get_report_by_id(report_id, user):
    """
    Gets a report instance for using its ID.

    If the user does not have the correct permission for the report, PermissionDenied is raised.
    """
    report = _registry[report_id]
    if not report.check_permission(user):
        raise PermissionDenied
    return report
