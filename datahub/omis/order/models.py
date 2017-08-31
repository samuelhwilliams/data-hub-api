import uuid

from django.conf import settings
from django.db import models, transaction
from django.utils.crypto import get_random_string
from django.utils.timezone import now

from datahub.company.models import Advisor, Company, Contact
from datahub.core.models import BaseModel, BaseOrderedConstantModel, DisableableModel

from datahub.metadata.models import Country, Sector, Team
from datahub.omis.core.utils import generate_reference
from datahub.omis.quote.models import Quote

from . import validators


class ServiceType(BaseOrderedConstantModel, DisableableModel):
    """
    Order service type.
    E.g. 'Validated contacts', 'Event', 'Market Research'
    """


class Order(BaseModel):
    """
    Details regarding an OMIS Order.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    reference = models.CharField(max_length=100)

    company = models.ForeignKey(
        Company,
        related_name="%(class)ss",  # noqa: Q000
        on_delete=models.PROTECT,
    )
    contact = models.ForeignKey(
        Contact,
        related_name="%(class)ss",  # noqa: Q000
        on_delete=models.PROTECT
    )

    primary_market = models.ForeignKey(
        Country,
        related_name="%(class)ss",  # noqa: Q000
        null=True,
        on_delete=models.SET_NULL
    )
    sector = models.ForeignKey(
        Sector,
        related_name='+',
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    service_types = models.ManyToManyField(
        ServiceType,
        related_name="%(class)ss",  # noqa: Q000
        blank=True
    )
    description = models.TextField(
        blank=True,
        help_text='Description of the work needed.'
    )
    contacts_not_to_approach = models.TextField(
        blank=True,
        help_text='Are there contacts that DIT should not approach?'
    )

    delivery_date = models.DateField(blank=True, null=True)

    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=254, blank=True)

    quote = models.OneToOneField(
        Quote,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    # legacy fields, only meant to be used in readonly mode as reference
    product_info = models.TextField(
        blank=True, editable=False,
        help_text='Legacy field. What is the product?'
    )
    further_info = models.TextField(
        blank=True, editable=False,
        help_text='Legacy field. Further information.'
    )
    existing_agents = models.TextField(
        blank=True, editable=False,
        help_text='Legacy field. Details of any existing agents.'
    )
    permission_to_approach_contacts = models.TextField(
        blank=True, editable=False,
        help_text='Legacy field. Can DIT speak to the contacts?'
    )

    def __str__(self):
        """Human-readable representation"""
        return self.reference

    @classmethod
    def generate_reference(cls):
        """
        :returns: a random unused reference of form:
            <(3) letters><(3) numbers>/<year> e.g. GEA962/16
        :raises RuntimeError: if no reference can be generated.
        """
        def gen():
            year_suffix = now().strftime('%y')
            return '{letters}{numbers}/{year}'.format(
                letters=get_random_string(length=3, allowed_chars='ACEFHJKMNPRTUVWXY'),
                numbers=get_random_string(length=3, allowed_chars='123456789'),
                year=year_suffix
            )

        return generate_reference(model=cls, gen=gen)

    def save(self, *args, **kwargs):
        """
        Like the django save but it creates a reference if it doesn't exist.
        """
        if not self.reference:
            self.reference = self.generate_reference()
        return super().save(*args, **kwargs)

    def get_datahub_frontend_url(self):
        """Return the url to the Data Hub frontend order page."""
        return f'{settings.DATAHUB_FRONTEND_BASE_URL}/omis/{self.pk}'

    @transaction.atomic
    def generate_quote(self, quote_data):
        """
        Generate a quote for this order if possible or raise

        :raises rest_framework.exceptions.ValidationError: in case of validation error
        :raises datahub.omis.core.exceptions.Conflict: in case of errors with the state of the
            current order
        :raises RuntimeError: after trying max_retries times without being able to generate a
            valid value for the quote reference
        """
        for validator in [
            validators.OrderDetailsFilledInValidator(),
            validators.NoOtherActiveQuoteExistsValidator()
        ]:
            validator.set_instance(self)
            validator()

        quote = Quote.objects.create(
            **quote_data,
            reference=Quote.generate_reference(self),
            content=Quote.generate_content(self)
        )
        self.quote = quote
        self.save()


class OrderSubscriber(BaseModel):
    """
    A subscribed adviser receives notifications when new changes happen to an Order.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='subscribers'
    )
    adviser = models.ForeignKey(
        Advisor, on_delete=models.CASCADE, related_name='+'
    )

    def __str__(self):
        """Human-readable representation"""
        return f'{self.order} – {self.adviser}'

    class Meta:  # noqa: D101
        ordering = ['created_on']
        unique_together = (
            ('order', 'adviser'),
        )


class OrderAssignee(BaseModel):
    """
    An adviser assigned to an Order and responsible for deliverying the final report(s).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='assignees')
    adviser = models.ForeignKey(Advisor, on_delete=models.PROTECT, related_name='+')
    team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.SET_NULL)

    estimated_time = models.IntegerField(default=0, help_text='Estimated time in minutes.')
    is_lead = models.BooleanField(default=False)

    class Meta:  # noqa: D101
        ordering = ['created_on']
        unique_together = (
            ('order', 'adviser'),
        )

    def __init__(self, *args, **kwargs):
        """
        Keep the original adviser value so that we can see if it changes when saving.
        """
        super().__init__(*args, **kwargs)
        self.__adviser = self.adviser

    def __str__(self):
        """Human-readable representation"""
        return (
            f'{"" if self.is_lead else "Not "}Lead Assignee '
            f'{self.adviser} for order {self.order}'
        )

    def save(self, *args, **kwargs):
        """
        Makes sure that the adviser cannot be changed after creation.
        When creating a new instance, it also denormalises `team` and `country` for
        future-proofing reasons, that is, if an adviser moves to another team in the future
        we don't want to change history.
        """
        if not self._state.adding and self.__adviser != self.adviser:
            raise ValueError("Updating the value of adviser isn't allowed.")

        if self._state.adding:
            self.team = self.adviser.dit_team
            if self.team:
                self.country = self.team.country

        super().save(*args, **kwargs)

        self.__adviser = self.adviser
