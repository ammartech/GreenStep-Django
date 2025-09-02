from django.core.management.base import BaseCommand
from tracker.models import EmissionFactor

class Command(BaseCommand):
    help = 'Populate the database with common emission factors'

    def handle(self, *args, **options):
        # Clear existing emission factors to avoid duplicates
        self.stdout.write('Clearing existing emission factors...')
        EmissionFactor.objects.all().delete()

        # Transportation emission factors (kg CO2 per km)
        transport_factors = [
            {'name': 'Gasoline car (small)', 'unit': 'km', 'co2_per_unit': 0.15, 'description': 'Small gasoline vehicle under 1.4L engine'},
            {'name': 'Gasoline car (medium)', 'unit': 'km', 'co2_per_unit': 0.21, 'description': 'Medium gasoline vehicle 1.4-2.0L engine'},
            {'name': 'Gasoline car (large)', 'unit': 'km', 'co2_per_unit': 0.28, 'description': 'Large gasoline vehicle over 2.0L engine'},
            {'name': 'Electric car', 'unit': 'km', 'co2_per_unit': 0.05, 'description': 'Battery electric vehicle'},
            {'name': 'Bus (local)', 'unit': 'km', 'co2_per_unit': 0.089, 'description': 'Local public bus per passenger'},
            {'name': 'Train (local)', 'unit': 'km', 'co2_per_unit': 0.028, 'description': 'Local train or metro per passenger'},
            {'name': 'Domestic flight', 'unit': 'km', 'co2_per_unit': 0.255, 'description': 'Domestic flight per passenger'},
            {'name': 'Walking', 'unit': 'km', 'co2_per_unit': 0, 'description': 'Zero emissions transportation'},
            {'name': 'Cycling', 'unit': 'km', 'co2_per_unit': 0, 'description': 'Zero emissions transportation'},
        ]

        # Energy emission factors (kg CO2 per kWh)
        energy_factors = [
            {'name': 'Grid electricity', 'unit': 'kWh', 'co2_per_unit': 0.5, 'description': 'Average grid electricity mix'},
            {'name': 'Natural gas heating', 'unit': 'kWh', 'co2_per_unit': 0.18, 'description': 'Natural gas for home heating'},
            {'name': 'Solar electricity', 'unit': 'kWh', 'co2_per_unit': 0.04, 'description': 'Solar photovoltaic electricity'},
        ]

        # Food emission factors (kg CO2 per meal/item)
        food_factors = [
            {'name': 'Beef meal', 'unit': 'meal', 'co2_per_unit': 3.3, 'description': 'Meal containing beef (200g serving)'},
            {'name': 'Chicken meal', 'unit': 'meal', 'co2_per_unit': 0.9, 'description': 'Meal containing chicken (200g serving)'},
            {'name': 'Vegetarian meal', 'unit': 'meal', 'co2_per_unit': 0.4, 'description': 'Plant-based meal without meat'},
            {'name': 'Fast food meal', 'unit': 'meal', 'co2_per_unit': 2.8, 'description': 'Typical fast food burger meal'},
            {'name': 'Coffee', 'unit': 'cup', 'co2_per_unit': 0.21, 'description': 'Coffee with dairy milk'},
        ]

        # Digital emission factors (kg CO2 per hour/use)
        digital_factors = [
            {'name': 'Video streaming (HD)', 'unit': 'hour', 'co2_per_unit': 0.036, 'description': '1 hour of HD video streaming'},
            {'name': 'Video call', 'unit': 'hour', 'co2_per_unit': 0.021, 'description': '1 hour video conferencing call'},
            {'name': 'Web browsing', 'unit': 'hour', 'co2_per_unit': 0.0036, 'description': '1 hour general web browsing'},
            {'name': 'Gaming', 'unit': 'hour', 'co2_per_unit': 0.084, 'description': '1 hour gaming on console'},
        ]

        # Create all emission factors
        categories = [
            ('transport', transport_factors),
            ('energy', energy_factors),
            ('food', food_factors),
            ('digital', digital_factors)
        ]

        created_count = 0

        for category, factors in categories:
            for factor_data in factors:
                EmissionFactor.objects.create(
                    name=factor_data['name'],
                    category=category,
                    unit=factor_data['unit'],
                    co2_per_unit=factor_data['co2_per_unit'],
                    description=factor_data['description']
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {factor_data["name"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nEmission factors populated successfully!\n'
                f'Created: {created_count} factors\n'
                f'Total factors in database: {EmissionFactor.objects.count()}'
            )
        )
