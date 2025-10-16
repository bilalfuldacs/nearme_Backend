"""
Management command to populate predefined event categories
Run: python manage.py populate_categories
"""
from django.core.management.base import BaseCommand
from myapp.models import Category


class Command(BaseCommand):
    help = 'Populate event categories with predefined data'

    def handle(self, *args, **kwargs):
        """Create all predefined categories"""
        
        categories_data = [
            # Social & Networking
            {
                'name': 'Networking',
                'description': 'Professional networking events, meetups, and business connections',
                'icon': '🤝'
            },
            {
                'name': 'Social Gathering',
                'description': 'Casual social events, parties, and get-togethers',
                'icon': '🎉'
            },
            
            # Sports & Fitness
            {
                'name': 'Sports',
                'description': 'Sports tournaments, games, and athletic competitions',
                'icon': '⚽'
            },
            {
                'name': 'Fitness & Wellness',
                'description': 'Yoga, gym sessions, running clubs, and health activities',
                'icon': '🏃'
            },
            {
                'name': 'Outdoor Adventures',
                'description': 'Hiking, camping, climbing, and outdoor activities',
                'icon': '🏕️'
            },
            
            # Arts & Culture
            {
                'name': 'Music & Concerts',
                'description': 'Live music, concerts, DJ nights, and musical performances',
                'icon': '🎵'
            },
            {
                'name': 'Arts & Crafts',
                'description': 'Painting, pottery, DIY workshops, and creative activities',
                'icon': '🎨'
            },
            {
                'name': 'Theater & Performances',
                'description': 'Theater shows, stand-up comedy, dance performances',
                'icon': '🎭'
            },
            {
                'name': 'Film & Photography',
                'description': 'Movie screenings, film festivals, photography exhibitions',
                'icon': '📸'
            },
            
            # Education & Learning
            {
                'name': 'Workshops & Classes',
                'description': 'Educational workshops, skill-building classes, and training sessions',
                'icon': '📚'
            },
            {
                'name': 'Tech & Innovation',
                'description': 'Hackathons, coding workshops, tech meetups, and innovation events',
                'icon': '💻'
            },
            {
                'name': 'Business & Career',
                'description': 'Business conferences, career fairs, professional development',
                'icon': '💼'
            },
            {
                'name': 'Science & Education',
                'description': 'Science fairs, lectures, seminars, and academic events',
                'icon': '🔬'
            },
            
            # Food & Drink
            {
                'name': 'Food & Dining',
                'description': 'Food festivals, cooking classes, restaurant events, tastings',
                'icon': '🍽️'
            },
            {
                'name': 'Wine & Beer Tasting',
                'description': 'Wine tastings, brewery tours, cocktail workshops',
                'icon': '🍷'
            },
            
            # Community & Volunteering
            {
                'name': 'Community Service',
                'description': 'Volunteer work, charity events, community clean-ups',
                'icon': '🤲'
            },
            {
                'name': 'Environmental',
                'description': 'Beach clean-ups, tree planting, sustainability events',
                'icon': '🌱'
            },
            {
                'name': 'Fundraising & Charity',
                'description': 'Charity galas, fundraisers, donation drives',
                'icon': '❤️'
            },
            
            # Family & Kids
            {
                'name': 'Family & Kids',
                'description': 'Family-friendly events, kids activities, playdates',
                'icon': '👨‍👩‍👧‍👦'
            },
            
            # Special Interests
            {
                'name': 'Gaming & Esports',
                'description': 'Video game tournaments, board game nights, esports events',
                'icon': '🎮'
            },
            {
                'name': 'Book Clubs & Literature',
                'description': 'Book readings, author meetups, literary discussions',
                'icon': '📖'
            },
            {
                'name': 'Fashion & Beauty',
                'description': 'Fashion shows, beauty workshops, styling events',
                'icon': '👗'
            },
            {
                'name': 'Pets & Animals',
                'description': 'Pet meetups, adoption events, animal welfare activities',
                'icon': '🐾'
            },
            
            # Travel & Tourism
            {
                'name': 'Travel & Tourism',
                'description': 'Travel meetups, group trips, cultural tours',
                'icon': '✈️'
            },
            
            # Spiritual & Wellness
            {
                'name': 'Spirituality & Religion',
                'description': 'Meditation sessions, religious gatherings, spiritual retreats',
                'icon': '🧘'
            },
            
            # Seasonal & Holidays
            {
                'name': 'Holiday & Seasonal',
                'description': 'Christmas parties, Halloween events, seasonal celebrations',
                'icon': '🎄'
            },
            
            # Other
            {
                'name': 'Other',
                'description': 'Events that don\'t fit into other categories',
                'icon': '📌'
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created category: {category.name}')
                )
            else:
                # Update existing category
                category.description = cat_data['description']
                category.icon = cat_data['icon']
                category.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated category: {category.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Done! Created {created_count} new categories, updated {updated_count} existing categories.'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f'Total categories: {Category.objects.count()}')
        )

