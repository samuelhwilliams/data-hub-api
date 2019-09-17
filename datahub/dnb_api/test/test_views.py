import json
from urllib.parse import urljoin

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.reverse import reverse

from datahub.company.models import Company, CompanyPermission
from datahub.company.test.factories import CompanyFactory
from datahub.core.test_utils import APITestMixin, create_test_user
from datahub.interaction.models import InteractionPermission
from datahub.metadata.models import Country

DNB_SEARCH_URL = urljoin(f'{settings.DNB_SERVICE_BASE_URL}/', 'companies/search/')


@pytest.mark.parametrize(
    'url',
    (
        reverse('api-v4:dnb-api:company-search'),
        reverse('api-v4:dnb-api:company-create'),
        reverse('api-v4:dnb-api:company-create-investigation'),
    ),
)
class TestDNBAPICommon(APITestMixin):
    """
    Test common functionality in company-search as well
    as company-create endpoints.
    """

    def test_post_no_feature_flag(self, requests_mock, url):
        """
        Test that POST fails with a 404 when the feature flag is unset.
        """
        requests_mock.post(DNB_SEARCH_URL)

        response = self.api_client.post(
            url,
            content_type='application/json',
        )

        assert response.status_code == 404
        assert requests_mock.called is False

    def test_unauthenticated_not_authorised(
        self,
        requests_mock,
        dnb_company_search_feature_flag,
        url,
    ):
        """
        Ensure that a non-authenticated request gets a 401.
        """
        requests_mock.post(DNB_SEARCH_URL)

        unauthorised_api_client = self.create_api_client()
        unauthorised_api_client.credentials(Authorization='foo')

        response = unauthorised_api_client.post(
            url,
            data={'foo': 'bar'},
        )

        assert response.status_code == 401
        assert requests_mock.called is False


class TestDNBCompanySearchAPI(APITestMixin):
    """
    DNB Company Search view test case.
    """

    @override_settings(DNB_SERVICE_BASE_URL=None)
    def test_post_no_dnb_setting(self, dnb_company_search_feature_flag):
        """
        Test that we get an ImproperlyConfigured exception when the DNB_SERVICE_BASE_URL setting
        is not set.
        """
        with pytest.raises(ImproperlyConfigured):
            self.api_client.post(
                reverse('api-v4:dnb-api:company-search'),
                data={},
            )

    @pytest.mark.parametrize(
        'content_type,expected_status_code',
        (
            (None, status.HTTP_406_NOT_ACCEPTABLE),
            ('text/html', status.HTTP_406_NOT_ACCEPTABLE),
        ),
    )
    def test_content_type(
        self,
        dnb_company_search_feature_flag,
        requests_mock,
        dnb_response_non_uk,
        content_type,
        expected_status_code,
    ):
        """
        Test that 406 is returned if Content Type is not application/json.
        """
        requests_mock.post(
            DNB_SEARCH_URL,
            status_code=status.HTTP_200_OK,
            json=dnb_response_non_uk,
        )

        response = self.api_client.post(
            reverse('api-v4:dnb-api:company-search'),
            content_type=content_type,
        )

        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        'request_data,response_status_code,upstream_response_content,response_data',
        (
            pytest.param(
                b'{"arg": "value"}',
                200,
                b'{"results":[{"duns_number":"9999999"}]}',
                {
                    'results': [
                        {
                            'dnb_company': {'duns_number': '9999999'},
                            'datahub_company': None,
                        },
                    ],
                },
                id='successful call to proxied API with company that cannot be hydrated',
            ),
            pytest.param(
                b'{"arg": "value"}',
                200,
                b'{"results":[{"duns_number":"1234567"}, {"duns_number":"7654321"}]}',
                {
                    'results': [
                        {
                            'dnb_company': {'duns_number': '1234567'},
                            'datahub_company': {
                                'id': '6083b732-b07a-42d6-ada4-c8082293285b',
                                'latest_interaction': None,
                            },
                        },
                        {
                            'dnb_company': {'duns_number': '7654321'},
                            'datahub_company': {
                                'id': '6083b732-b07a-42d6-ada4-c99999999999',
                                'latest_interaction': {
                                    'id': '6083b732-b07a-42d6-ada4-222222222222',
                                    'date': '2019-08-01',
                                    'created_on': '2019-08-01T16:00:00Z',
                                    'subject': 'Meeting with Joe Bloggs',
                                },
                            },
                        },
                    ],
                },
                id='successful call to proxied API with company that can be hydrated',
            ),
            pytest.param(
                b'{"arg": "value"}',
                400,
                b'{"error":"msg"}',
                {'error': 'msg'},
                id='proxied API returns a bad request',
            ),
            pytest.param(
                b'{"arg": "value"}',
                500,
                b'{"error":"msg"}',
                {'error': 'msg'},
                id='proxied API returns a server error',
            ),
        ),
    )
    def test_post(
        self,
        dnb_company_search_feature_flag,
        dnb_company_search_datahub_companies,
        requests_mock,
        request_data,
        response_status_code,
        upstream_response_content,
        response_data,
    ):
        """
        Test for POST proxy.
        """
        requests_mock.post(
            DNB_SEARCH_URL,
            status_code=response_status_code,
            content=upstream_response_content,
            headers={'content-type': 'application/json'},
        )

        user = create_test_user(
            permission_codenames=[
                CompanyPermission.view_company,
                InteractionPermission.view_all,
            ],
        )
        api_client = self.create_api_client(user=user)

        url = reverse('api-v4:dnb-api:company-search')
        response = api_client.post(
            url,
            data=request_data,
            content_type='application/json',
        )

        assert response.status_code == response_status_code
        assert response.json() == response_data
        assert requests_mock.last_request.body == request_data

    @pytest.mark.parametrize(
        'response_status_code,upstream_response_content,response_data,permission_codenames',
        (
            pytest.param(
                200,
                b'{"results":[{"duns_number":"7654321"}]}',
                {
                    'results': [
                        # latest_interaction is omitted, because the user does not have permission
                        # to view interactions
                        {
                            'dnb_company': {'duns_number': '7654321'},
                            'datahub_company': {
                                'id': '6083b732-b07a-42d6-ada4-c99999999999',
                            },
                        },
                    ],
                },
                [CompanyPermission.view_company],
                id=(
                    'successful call to proxied API with company that can be hydrated '
                    'and user that has no interaction permissions'
                ),
            ),
            pytest.param(
                403,
                b'{"error":"msg"}',
                {'detail': 'You do not have permission to perform this action.'},
                [InteractionPermission.view_all],
                id='user missing view_company permission should get a 403',
            ),
            pytest.param(
                200,
                b'{"results":[{"duns_number":"7654321"}]}',
                {
                    'results': [
                        # latest_interaction is None, because the user does not have permission
                        # to view interactions
                        {
                            'dnb_company': {'duns_number': '7654321'},
                            'datahub_company': {
                                'id': '6083b732-b07a-42d6-ada4-c99999999999',
                                'latest_interaction': {
                                    'id': '6083b732-b07a-42d6-ada4-222222222222',
                                    'date': '2019-08-01',
                                    'created_on': '2019-08-01T16:00:00Z',
                                    'subject': 'Meeting with Joe Bloggs',
                                },
                            },
                        },
                    ],
                },
                [CompanyPermission.view_company, InteractionPermission.view_all],
                id=(
                    'user with both view_company and view_all_interaction permissions should get '
                    'a fully hydrated response'
                ),
            ),
        ),
    )
    def test_post_permissions(
        self,
        dnb_company_search_feature_flag,
        dnb_company_search_datahub_companies,
        requests_mock,
        response_status_code,
        upstream_response_content,
        response_data,
        permission_codenames,
    ):
        """
        Test for POST proxy permissions.
        """
        requests_mock.post(
            DNB_SEARCH_URL,
            status_code=response_status_code,
            content=upstream_response_content,
        )
        user = create_test_user(permission_codenames=permission_codenames)
        api_client = self.create_api_client(user=user)

        url = reverse('api-v4:dnb-api:company-search')
        response = api_client.post(
            url,
            content_type='application/json',
        )

        assert response.status_code == response_status_code
        assert json.loads(response.content) == response_data


class TestDNBCompanyCreateAPI(APITestMixin):
    """
    DNB Company Create view test case.
    """

    def _assert_companies_same(self, company, dnb_company):
        """
        Check whether the given DataHub company is the same as the given DNB company.
        """
        country = Country.objects.filter(
            iso_alpha2_code=dnb_company['address_country'],
        ).first()

        company_number = (
            dnb_company['registration_numbers'][0].get('registration_number')
            if country.iso_alpha2_code == 'GB' else None
        )

        [company.pop(k) for k in ('id', 'created_on', 'modified_on')]

        assert company == {
            'name': dnb_company['primary_name'],
            'trading_names': dnb_company['trading_names'],
            'address': {
                'country': {
                    'id': str(country.id),
                    'name': country.name,
                },
                'line_1': dnb_company['address_line_1'],
                'line_2': dnb_company['address_line_2'],
                'town': dnb_company['address_town'],
                'county': dnb_company['address_county'],
                'postcode': dnb_company['address_postcode'],
            },
            'registered_address': None,
            'reference_code': '',
            'uk_based': (dnb_company['address_country'] == 'GB'),
            'duns_number': dnb_company['duns_number'],
            'company_number': company_number,
            'number_of_employees': dnb_company['employee_number'],
            'is_number_of_employees_estimated': dnb_company['is_employees_number_estimated'],
            'employee_range': None,
            'turnover': float(dnb_company['annual_sales']),
            'is_turnover_estimated': dnb_company['is_annual_sales_estimated'],
            'turnover_range': None,
            'website': f'http://{dnb_company["domain"]}',
            'business_type': None,
            'description': None,
            'global_headquarters': None,
            'headquarter_type': None,
            'sector': None,
            'uk_region': None,
            'vat_number': '',
            'archived': False,
            'archived_by': None,
            'archived_documents_url_path': '',
            'archived_on': None,
            'archived_reason': None,
            'export_experience_category': None,
            'export_to_countries': [],
            'future_interest_countries': [],
            'one_list_group_global_account_manager': None,
            'one_list_group_tier': None,
            'transfer_reason': '',
            'transferred_by': None,
            'transferred_to': None,
            'transferred_on': None,
            'contacts': [],
            'pending_dnb_investigation': False,
        }

    @override_settings(DNB_SERVICE_BASE_URL=None)
    def test_post_no_dnb_setting(self, dnb_company_search_feature_flag):
        """
        Test that we get an ImproperlyConfigured exception when the DNB_SERVICE_BASE_URL setting
        is not set.
        """
        with pytest.raises(ImproperlyConfigured):
            self.api_client.post(
                reverse('api-v4:dnb-api:company-search'),
                data={'duns_number': '12345678'},
            )

    def test_post_non_uk(
        self,
        requests_mock,
        dnb_company_search_feature_flag,
        dnb_response_non_uk,
    ):
        """
        Test create-company endpoint for a non-uk company.
        """
        requests_mock.post(
            DNB_SEARCH_URL,
            json=dnb_response_non_uk,
        )

        response = self.api_client.post(
            reverse('api-v4:dnb-api:company-create'),
            data={
                'duns_number': 123456789,
            },
        )

        assert response.status_code == status.HTTP_200_OK

        company = response.json()
        dnb_company = dnb_response_non_uk['results'].pop()
        self._assert_companies_same(company, dnb_company)

        datahub_company = Company.objects.filter(
            duns_number=company['duns_number'],
        ).first()
        assert datahub_company is not None
        assert datahub_company.created_by == self.user
        assert datahub_company.modified_by == self.user

    def test_post_uk(
        self,
        requests_mock,
        dnb_company_search_feature_flag,
        dnb_response_uk,
    ):
        """
        Test create-company endpoint for a UK company.
        """
        requests_mock.post(
            DNB_SEARCH_URL,
            json=dnb_response_uk,
        )

        response = self.api_client.post(
            reverse('api-v4:dnb-api:company-create'),
            data={
                'duns_number': 123456789,
            },
        )

        assert response.status_code == status.HTTP_200_OK

        company = response.json()
        dnb_company = dnb_response_uk['results'].pop()
        self._assert_companies_same(company, dnb_company)

        datahub_company = Company.objects.filter(
            duns_number=company['duns_number'],
        ).first()
        assert datahub_company is not None
        assert datahub_company.created_by == self.user
        assert datahub_company.modified_by == self.user

    @pytest.mark.parametrize(
        'data',
        (
            {'duns_number': None},
            {'duns_number': 'foobarbaz'},
            {'duns_number': '12345678'},
            {'duns_number': '1234567890'},
            {'not_duns_number': '123456789'},
        ),
    )
    def test_post_invalid(
        self,
        dnb_company_search_feature_flag,
        data,
    ):
        """
        Test that a query without `duns_number` returns 400.
        """
        response = self.api_client.post(
            reverse('api-v4:dnb-api:company-create'),
            data=data,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        'results, expected_status_code, expected_message',
        (
            ([], 400, 'Cannot find a company with duns_number: 123456789'),
            (['foo', 'bar'], 502, 'Multiple companies found with duns_number: 123456789'),
        ),
    )
    def test_post_none_or_multiple_companies_found(
        self,
        requests_mock,
        dnb_company_search_feature_flag,
        results,
        expected_status_code,
        expected_message,
    ):
        """
        Test if a given `duns_number` gets anything other than a single company
        from dnb-service, the create-company endpoint returns a 400.

        """
        requests_mock.post(
            DNB_SEARCH_URL,
            json={'results': results},
        )

        response = self.api_client.post(
            reverse('api-v4:dnb-api:company-create'),
            data={
                'duns_number': 123456789,
            },
        )

        assert response.status_code == expected_status_code
        assert response.json()['detail'] == expected_message

    @pytest.mark.parametrize(
        'missing_required_field, expected_error',
        (
            ('primary_name', {'name': ['This field may not be null.']}),
            ('trading_names', {'trading_names': ['This field may not be null.']}),
            ('duns_number', {'duns_number': ['This field may not be null.']}),
            ('address_line_1', {'address': {'line_1': ['This field may not be null.']}}),
            ('address_line_2', {'address': {'line_2': ['This field may not be null.']}}),
            ('address_town', {'address': {'town': ['This field may not be null.']}}),
            ('address_county', {'address': {'county': ['This field may not be null.']}}),
            ('address_postcode', {'address': {'postcode': ['This field may not be null.']}}),
            ('address_country', {'address': {'country': ['Must be a valid UUID.']}}),
        ),
    )
    def test_post_missing_required_fields(
        self,
        requests_mock,
        dnb_company_search_feature_flag,
        dnb_response_uk,
        missing_required_field,
        expected_error,
    ):
        """
        Test if dnb-service returns a company with missing required fields,
        the create-company endpoint returns 400.
        """
        dnb_response_uk['results'][0].pop(missing_required_field)
        requests_mock.post(
            DNB_SEARCH_URL,
            json=dnb_response_uk,
        )

        response = self.api_client.post(
            reverse('api-v4:dnb-api:company-create'),
            data={
                'duns_number': 123456789,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected_error

    def test_post_existing(
        self,
        dnb_company_search_feature_flag,
    ):
        """
        Test if create-company endpoint returns 400 if the company with the given
        duns_number already exists in DataHub.
        """
        duns_number = 123456789
        CompanyFactory(duns_number=duns_number)

        response = self.api_client.post(
            reverse('api-v4:dnb-api:company-create'),
            data={
                'duns_number': duns_number,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            'duns_number': [
                f'Company with duns_number: {duns_number} already exists in DataHub.'],
        }

    def test_post_invalid_country(
        self,
        requests_mock,
        dnb_company_search_feature_flag,
        dnb_response_uk,
    ):
        """
        Test if create-company endpoint returns 400 if the company is based in a country
        that does not exist in DataHub.
        """
        dnb_response_uk['results'][0]['address_country'] = 'FOO'
        requests_mock.post(
            DNB_SEARCH_URL,
            json=dnb_response_uk,
        )

        response = self.api_client.post(
            reverse('api-v4:dnb-api:company-create'),
            data={
                'duns_number': 123456789,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        'status_code',
        (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.HTTP_502_BAD_GATEWAY,
        ),
    )
    def test_post_dnb_service_error(
        self,
        requests_mock,
        dnb_company_search_feature_flag,
        status_code,
    ):
        """
        Test if create-company endpoint returns 400 if the company is based in a country
        that does not exist in DataHub.
        """
        requests_mock.post(
            DNB_SEARCH_URL,
            status_code=status_code,
        )

        response = self.api_client.post(
            reverse('api-v4:dnb-api:company-create'),
            data={
                'duns_number': 123456789,
            },
        )

        assert response.status_code == status.HTTP_502_BAD_GATEWAY

    @pytest.mark.parametrize(
        'permissions',
        (
            [],
            [CompanyPermission.add_company],
            [CompanyPermission.view_company],
        ),
    )
    def test_post_no_permission(
        self,
        requests_mock,
        dnb_company_search_feature_flag,
        dnb_response_uk,
        permissions,
    ):
        """
        Create-company endpoint should return 403 if the user does not
        have the necessary permissions.
        """
        requests_mock.post(
            DNB_SEARCH_URL,
            json=dnb_response_uk,
        )

        user = create_test_user(permission_codenames=permissions)
        api_client = self.create_api_client(user=user)
        response = api_client.post(
            reverse('api-v4:dnb-api:company-create'),
            data={
                'duns_number': 123456789,
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDNBCompanyCreateInvestigationAPI(APITestMixin):
    """
    Tests for dnb-company-create-investigation endpoint.
    """

    @pytest.mark.parametrize(
        'investigation_override',
        (
            {},
            {'telephone_number': None},
            {'website': None},
        ),
    )
    def test_post(
            self,
            dnb_company_search_feature_flag,
            investigation_payload,
            investigation_override,
    ):
        """
        Test if we can post the unhappy path data to create a
        Company record with `pending_dnb_investigation` set to
        True.
        """
        payload = {
            **investigation_payload,
            **investigation_override,
        }
        response = self.api_client.post(
            reverse('api-v4:dnb-api:company-create-investigation'),
            data=payload,
        )

        assert response.status_code == status.HTTP_200_OK

        company = Company.objects.get(
            pk=response.json()['id'],
        )
        assert company.pending_dnb_investigation
        assert company.created_by == self.user
        assert company.modified_by == self.user
        assert company.name == payload['name']
        assert company.website == payload['website']
        assert company.dnb_investigation_data == {
            'telephone_number': payload['telephone_number'],
        }
        assert company.address_1 == payload['address']['line_1']
        assert company.address_2 == payload['address']['line_2']
        assert company.address_town == payload['address']['town']
        assert company.address_county == payload['address']['county']
        assert company.address_postcode == payload['address']['postcode']
        assert str(company.address_country.id) == payload['address']['country']['id']
        assert str(company.business_type.id) == payload['business_type']
        assert str(company.sector.id) == payload['sector']
        assert str(company.uk_region.id) == payload['uk_region']

    @pytest.mark.parametrize(
        'investigation_override, expected_error',
        (
            # Website and telephone_number cannot both be null
            (
                {'website': None, 'telephone_number': None},
                {'non_field_errors': ['Either website or telephone_number must be provided.']},
            ),
            # If website is specified, it should be a valid URL
            (
                {'website': 'test'},
                {'website': ['Enter a valid URL.']},
            ),
            # Other fields that are required and enforced by CompanySerializer
            (
                {'name': None},
                {'name': ['This field may not be null.']},
            ),
            (
                {'business_type': None},
                {'business_type': ['This field is required.']},
            ),
            (
                {'address': None},
                {'address': ['This field may not be null.']},
            ),
            (
                {'sector': None},
                {'sector': ['This field is required.']},
            ),
            (
                {'uk_region': None},
                {'uk_region': ['This field is required.']},
            ),
        ),
    )
    def test_post_invalid(
            self,
            dnb_company_search_feature_flag,
            investigation_payload,
            investigation_override,
            expected_error,
    ):
        """
        Test if we post invalid data to the create-company-investigation
        endpoint, we get an error.
        """
        payload = {
            **investigation_payload,
            **investigation_override,
        }
        response = self.api_client.post(
            reverse('api-v4:dnb-api:company-create-investigation'),
            data=payload,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected_error

    @pytest.mark.parametrize(
        'permissions',
        (
            [],
            [CompanyPermission.add_company],
            [CompanyPermission.view_company],
        ),
    )
    def test_post_no_permission(
        self,
        dnb_company_search_feature_flag,
        permissions,
    ):
        """
        Create-company-investigation endpoint should return 403 if the user does not
        have the necessary permissions.
        """
        user = create_test_user(permission_codenames=permissions)
        api_client = self.create_api_client(user=user)
        response = api_client.post(
            reverse('api-v4:dnb-api:company-create-investigation'),
            data={},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
