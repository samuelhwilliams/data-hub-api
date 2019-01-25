from uuid import uuid4

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.urls import reverse
from rest_framework import status

from datahub.company.test.factories import CompanyFactory, ContactFactory
from datahub.core.admin import get_change_url
from datahub.core.test_utils import AdminTestMixin, random_obj_for_model
from datahub.interaction.models import CommunicationChannel, Interaction
from datahub.interaction.test.factories import CompanyInteractionFactory
from datahub.metadata.models import Service, Team


class TestInteractionAdmin(AdminTestMixin):
    """
    Tests for interaction admin.

    TODO: these tests will be removed once the migration from contact to contacts is complete.
    """

    def test_add(self):
        """Test that adding an interaction also sets the contacts field."""
        company = CompanyFactory()
        contact = ContactFactory()
        communication_channel = random_obj_for_model(CommunicationChannel)

        url = reverse(admin_urlname(Interaction._meta, 'add'))
        data = {
            'id': uuid4(),
            'kind': Interaction.KINDS.interaction,
            'communication_channel': communication_channel.pk,
            'subject': 'whatever',
            'date_0': '2018-01-01',
            'date_1': '00:00:00',
            'dit_adviser': self.user.pk,
            'company': company.pk,
            'contact': contact.pk,
            'service': random_obj_for_model(Service).pk,
            'dit_team': random_obj_for_model(Team).pk,
            'was_policy_feedback_provided': False,
        }
        response = self.client.post(url, data, follow=True)

        assert response.status_code == status.HTTP_200_OK

        assert Interaction.objects.count() == 1
        interaction = Interaction.objects.first()

        assert interaction.contact == contact
        assert list(interaction.contacts.all()) == [contact]

    def test_update_contact_to_non_null(self):
        """
        Test that updating an interaction with a non-null contact also sets the contacts
        field.
        """
        interaction = CompanyInteractionFactory(contacts=[])
        new_contact = ContactFactory(company=interaction.company)

        url = get_change_url(interaction)
        data = {
            # Unchanged values
            'id': interaction.pk,
            'kind': Interaction.KINDS.interaction,
            'communication_channel': interaction.communication_channel.pk,
            'subject': interaction.subject,
            'date_0': interaction.date.date().isoformat(),
            'date_1': interaction.date.time().isoformat(),
            'dit_adviser': interaction.dit_adviser.pk,
            'company': interaction.company.pk,
            'service': interaction.service.pk,
            'dit_team': interaction.dit_team.pk,
            'was_policy_feedback_provided': interaction.was_policy_feedback_provided,
            'policy_feedback_notes': interaction.policy_feedback_notes,
            'policy_areas': [],
            'policy_issue_types': [],
            'event': '',

            # Changed values
            'contact': new_contact.pk,
        }
        response = self.client.post(url, data=data, follow=True)

        assert response.status_code == status.HTTP_200_OK

        interaction.refresh_from_db()
        assert interaction.contact == new_contact
        assert list(interaction.contacts.all()) == [new_contact]

    def test_update_contact_to_null(self):
        """Test that updating an interaction with a null contact clears the contacts field."""
        interaction = CompanyInteractionFactory(contacts=[])

        url = get_change_url(interaction)
        data = {
            # Unchanged values
            'id': interaction.pk,
            'kind': Interaction.KINDS.interaction,
            'communication_channel': interaction.communication_channel.pk,
            'subject': interaction.subject,
            'date_0': interaction.date.date().isoformat(),
            'date_1': interaction.date.time().isoformat(),
            'dit_adviser': interaction.dit_adviser.pk,
            'company': interaction.company.pk,
            'service': interaction.service.pk,
            'dit_team': interaction.dit_team.pk,
            'was_policy_feedback_provided': interaction.was_policy_feedback_provided,
            'policy_feedback_notes': interaction.policy_feedback_notes,
            'policy_areas': [],
            'policy_issue_types': [],
            'event': '',

            # Changed values
            'contact': '',
        }
        response = self.client.post(url, data=data, follow=True)

        assert response.status_code == status.HTTP_200_OK

        interaction.refresh_from_db()
        assert interaction.contact is None
        assert interaction.contacts.count() == 0