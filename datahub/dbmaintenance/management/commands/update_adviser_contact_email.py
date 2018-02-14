import reversion

from datahub.company.models import Advisor
from datahub.dbmaintenance.utils import parse_email, parse_uuid
from ..base import CSVBaseCommand


class Command(CSVBaseCommand):
    """Command to update the contact_email for advisers."""

    def add_arguments(self, parser):
        """Define extra arguments."""
        super().add_arguments(parser)
        parser.add_argument(
            '--simulate',
            action='store_true',
            default=False,
            help='If True it only simulates the command without saving the changes.',
        )

    def _process_row(self, row, simulate=False, **options):
        """Process one single row."""
        pk = parse_uuid(row['id'])
        contact_email = parse_email(row['contact_email'])
        adviser = Advisor.objects.get(pk=pk)

        if adviser.contact_email == contact_email:
            return

        adviser.contact_email = contact_email

        if simulate:
            return

        with reversion.create_revision():
            adviser.save(update_fields=('contact_email',))
            reversion.set_comment('Loaded contact email from spreadsheet.')