import datetime
import uuid
import factory

from django.utils.timezone import now

from datahub.company.test.factories import AdviserFactory, CompanyFactory, ContactFactory
from datahub.core.constants import Country, Sector
from datahub.core.test.factories import to_many_field

from datahub.omis.invoice.test.factories import InvoiceFactory
from datahub.omis.quote.test.factories import (
    AcceptedQuoteFactory, CancelledQuoteFactory, QuoteFactory
)

from ..constants import OrderStatus, VATStatus
from ..models import CancellationReason, ServiceType


class OrderFactory(factory.django.DjangoModelFactory):
    """Order factory."""

    id = factory.LazyFunction(uuid.uuid4)
    created_by = factory.SubFactory(AdviserFactory)
    modified_by = factory.SubFactory(AdviserFactory)
    company = factory.SubFactory(CompanyFactory)
    contact = factory.LazyAttribute(lambda o: ContactFactory(company=o.company))
    primary_market_id = Country.france.value.id
    sector_id = Sector.aerospace_assembly_aircraft.value.id
    description = factory.Faker('text')
    contacts_not_to_approach = factory.Faker('text')
    product_info = factory.Faker('text')
    further_info = factory.Faker('text')
    existing_agents = factory.Faker('text')
    permission_to_approach_contacts = factory.Faker('text')
    delivery_date = factory.LazyFunction(
        lambda: (now() + datetime.timedelta(days=60)).date()
    )
    contact_email = factory.Faker('email')
    contact_phone = '+44 (0)7123 123456'
    status = OrderStatus.draft
    po_number = factory.Faker('text', max_nb_chars=50)
    discount_value = factory.Faker('random_int', max=100)
    discount_label = factory.Faker('text', max_nb_chars=50)
    vat_status = VATStatus.eu
    vat_number = '0123456789'
    vat_verified = True
    billing_contact_name = factory.Faker('name')
    billing_email = factory.Faker('email')
    billing_phone = '+44 (0)444 123456'
    billing_address_1 = factory.Sequence(lambda n: f'Apt {n}.')
    billing_address_2 = factory.Sequence(lambda n: f'{n} Foo st.')
    billing_address_country_id = Country.united_kingdom.value.id
    billing_address_county = factory.Faker('text')
    billing_address_postcode = 'SW1A1AA'
    billing_address_town = 'London'

    @to_many_field
    def service_types(self):
        """
        Add support for setting service_types.
        If nothing specified when instantiating the object, the value returned by
        this method will be used by default.
        """
        return ServiceType.objects.filter(disabled_on__isnull=True).order_by('?')[:2]

    @to_many_field
    def assignees(self):
        """
        Add support for setting assignees.
        If nothing specified when instantiating the object, the value returned by
        this method will be used by default.
        """
        return OrderAssigneeFactory.create_batch(1, order=self)

    class Meta:
        model = 'order.Order'


class OrderWithOpenQuoteFactory(OrderFactory):
    """Order factory with an active quote."""

    quote = factory.SubFactory(QuoteFactory)
    status = OrderStatus.quote_awaiting_acceptance


class OrderWithCancelledQuoteFactory(OrderFactory):
    """Order factory with a cancelled quote."""

    quote = factory.SubFactory(CancelledQuoteFactory)


class OrderWithAcceptedQuoteFactory(OrderFactory):
    """Order factory with an accepted quote."""

    quote = factory.SubFactory(AcceptedQuoteFactory)
    invoice = factory.SubFactory(InvoiceFactory)
    status = OrderStatus.quote_accepted


class OrderCompleteFactory(OrderWithAcceptedQuoteFactory):
    """Factory for orders marked as paid."""

    status = OrderStatus.complete
    completed_on = factory.Faker('date_time')
    completed_by = factory.SubFactory(AdviserFactory)


class OrderCancelledFactory(OrderWithAcceptedQuoteFactory):
    """Factory for cancelled orders."""

    status = OrderStatus.cancelled
    cancelled_on = factory.Faker('date_time')
    cancelled_by = factory.SubFactory(AdviserFactory)
    cancellation_reason = factory.LazyFunction(CancellationReason.objects.first)


class OrderPaidFactory(OrderWithAcceptedQuoteFactory):
    """Factory for orders marked as paid."""

    status = OrderStatus.paid


class OrderSubscriberFactory(factory.django.DjangoModelFactory):
    """Order Subscriber factory."""

    id = factory.LazyFunction(uuid.uuid4)
    order = factory.SubFactory(OrderFactory)
    adviser = factory.SubFactory(AdviserFactory)

    class Meta:
        model = 'order.OrderSubscriber'


class OrderAssigneeFactory(factory.django.DjangoModelFactory):
    """Order Assignee factory."""

    id = factory.LazyFunction(uuid.uuid4)
    order = factory.SubFactory(OrderFactory)
    adviser = factory.SubFactory(AdviserFactory)
    estimated_time = factory.Faker('random_int', min=10, max=100)

    class Meta:
        model = 'order.OrderAssignee'


class HourlyRateFactory(factory.django.DjangoModelFactory):
    """HourlyRate factory."""

    id = factory.LazyFunction(uuid.uuid4)

    class Meta:
        model = 'order.HourlyRate'
