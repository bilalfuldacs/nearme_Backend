from django.core.management.base import BaseCommand
from myapp.models import Review, Event, User
from django.db import transaction
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Populate database with dummy reviews for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting to populate reviews...'))
        
        # Sample review comments
        positive_comments = [
            "Amazing event! The host was very professional and organized.",
            "Excellent experience! Would definitely attend more events from this host.",
            "Great atmosphere and well-managed event. Highly recommend!",
            "The host was friendly and made sure everyone had a good time.",
            "Outstanding event! Everything was perfect from start to finish.",
            "Best event I've attended in a while. The host really knows what they're doing.",
            "Wonderful experience! The host was attentive to all guests.",
            "Loved every minute of it! Will definitely come back for more.",
            "Professional and fun event. The host exceeded expectations.",
            "Fantastic organization and great vibes throughout the event.",
        ]
        
        good_comments = [
            "Good event overall. Had a great time!",
            "Nice experience. The host did a good job organizing.",
            "Enjoyed the event. Would attend again.",
            "Solid event with good organization.",
            "Pretty good! Minor issues but overall positive.",
            "Good atmosphere and friendly host.",
            "Enjoyable event with nice people.",
            "Well organized and fun event.",
        ]
        
        neutral_comments = [
            "It was okay. Could have been better organized.",
            "Average experience. Nothing special but not bad either.",
            "Decent event but had some room for improvement.",
            "It was fine. Met my basic expectations.",
            "Not bad, but I've been to better events.",
        ]
        
        negative_comments = [
            "Event could have been better organized.",
            "Had some issues with the event management.",
            "Not what I expected. Needs improvement.",
            "Disappointing experience. Host needs to work on organization.",
        ]
        
        try:
            with transaction.atomic():
                # Get all events and users
                events = list(Event.objects.all())
                users = list(User.objects.all())
                
                if not events:
                    self.stdout.write(self.style.ERROR('No events found! Please create some events first.'))
                    return
                
                if len(users) < 2:
                    self.stdout.write(self.style.ERROR('Need at least 2 users (1 host + 1 reviewer)! Please create more users.'))
                    return
                
                # Clear existing reviews
                deleted_count = Review.objects.all().delete()[0]
                self.stdout.write(self.style.WARNING(f'Deleted {deleted_count} existing reviews'))
                
                reviews_created = 0
                
                # For each event, create random reviews
                for event in events:
                    host = event.organizer_id
                    
                    # Get potential reviewers (all users except the host)
                    potential_reviewers = [u for u in users if u.id != host.id]
                    
                    if not potential_reviewers:
                        continue
                    
                    # Random number of reviews per event (1-5)
                    num_reviews = random.randint(1, min(5, len(potential_reviewers)))
                    
                    # Select random reviewers
                    reviewers = random.sample(potential_reviewers, num_reviews)
                    
                    for reviewer in reviewers:
                        # Generate rating (weighted toward positive)
                        rating_weights = [1, 2, 5, 15, 25]  # More likely to get 4-5 stars
                        rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]
                        
                        # Select comment based on rating
                        if rating == 5:
                            comment = random.choice(positive_comments)
                        elif rating == 4:
                            comment = random.choice(good_comments)
                        elif rating == 3:
                            comment = random.choice(neutral_comments)
                        else:
                            comment = random.choice(negative_comments)
                        
                        # Random created date (within last 60 days)
                        days_ago = random.randint(1, 60)
                        created_at = datetime.now() - timedelta(days=days_ago)
                        
                        # Create review
                        review = Review.objects.create(
                            event=event,
                            host=host,
                            reviewer=reviewer,
                            rating=rating,
                            comment=comment,
                            created_at=created_at
                        )
                        reviews_created += 1
                        
                        self.stdout.write(
                            f'✓ Created review: {reviewer.name} → {event.title[:30]} ({rating}⭐)'
                        )
                
                self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {reviews_created} reviews!'))
                
                # Show statistics
                from django.db.models import Avg, Count
                
                self.stdout.write(self.style.SUCCESS('\n📊 Host Statistics:'))
                hosts = User.objects.filter(organized_events__isnull=False).distinct()
                
                for host in hosts:
                    host_reviews = Review.objects.filter(host=host)
                    if host_reviews.exists():
                        stats = host_reviews.aggregate(
                            avg_rating=Avg('rating'),
                            total_reviews=Count('id')
                        )
                        self.stdout.write(
                            f'   {host.name}: ⭐ {stats["avg_rating"]:.1f} ({stats["total_reviews"]} reviews)'
                        )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            import traceback
            traceback.print_exc()

