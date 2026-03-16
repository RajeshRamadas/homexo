from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from properties.models import Property, PropertyTag
from agents.models import Agent


class PropertyModelTestCase(TestCase):
    """Test cases for Property model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.property = Property.objects.create(
            title='Test Property',
            description='A test property description',
            listing_type='buy',
            property_type='apartment',
            price=5000000,
            bedrooms=3,
            bathrooms=2,
            area_sqft=1500,
            city='Mumbai',
            locality='Andheri',
            owner=self.user,
            status='active'
        )

    def test_property_creation(self):
        """Test that property is created correctly."""
        self.assertEqual(self.property.title, 'Test Property')
        self.assertEqual(self.property.listing_type, 'buy')
        self.assertEqual(self.property.owner, self.user)
        self.assertEqual(self.property.status, 'active')

    def test_display_price(self):
        """Test display_price property formatting."""
        display = self.property.display_price
        # Property price is ₹5000000 (₹50 lakh)
        self.assertIn('L', display)
        self.assertIn('₹', display)

    def test_property_slug_generation(self):
        """Test that slug is auto-generated."""
        self.assertIsNotNone(self.property.slug)
        self.assertTrue(len(self.property.slug) > 0)

    def test_property_str_method(self):
        """Test string representation of property."""
        expected = f"{self.property.title} — {self.property.locality}, {self.property.city}"
        self.assertEqual(str(self.property), expected)


class PropertyViewsTestCase(TestCase):
    """Test cases for Property views."""

    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.property = Property.objects.create(
            title='Test Property',
            description='A test property',
            listing_type='buy',
            property_type='apartment',
            price=5000000,
            bedrooms=3,
            bathrooms=2,
            area_sqft=1500,
            city='Mumbai',
            locality='Andheri',
            owner=self.user,
            status='active'
        )

    def test_property_list_view(self):
        """Test property list view is accessible."""
        response = self.client.get(reverse('properties:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Property')

    def test_property_detail_view(self):
        """Test property detail view is accessible."""
        response = self.client.get(
            reverse('properties:detail', kwargs={'slug': self.property.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Property')


class PropertyAPITestCase(TestCase):
    """Test cases for Property API endpoints."""

    def setUp(self):
        """Set up test data and API client."""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.property = Property.objects.create(
            title='API Test Property',
            description='A test property for API',
            listing_type='buy',
            property_type='villa',
            price=10000000,
            bedrooms=4,
            bathrooms=3,
            area_sqft=2500,
            city='Bengaluru',
            locality='Whitefield',
            owner=self.user,
            status='active'
        )

    def test_property_api_list(self):
        """Test property API list endpoint."""
        response = self.client.get('/api/v1/properties/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue('results' in data)

    def test_property_api_detail(self):
        """Test property API detail endpoint."""
        response = self.client.get(f'/api/v1/properties/{self.property.slug}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['title'], 'API Test Property')
        self.assertEqual(data['city'], 'Bengaluru')
