from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import FinancialYear
from ledger.models import LedgerData
from stock.models import StockData
from ratelist.models import RatelistData
from orderlist.models import Order
from django.db import transaction
import datetime

class Command(BaseCommand):
    help = 'Migrate data from date-suffixed users to main user with FinancialYear'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Simulate migration without changes')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # 1. Identify Target Users pattern: name@YYYY-YYYY
        users = User.objects.filter(username__contains='@')
        
        for user in users:
            if '@' not in user.username:
                continue
            
            # Extract basic info
            try:
                base_username, year_part = user.username.split('@', 1)
            except ValueError:
                self.stdout.write(self.style.WARNING(f"Skipping user {user.username}: Invalid format (no split)"))
                continue
                
            # Validate year part YYYY-YYYY
            try:
                start_year_str, end_year_str = year_part.split('-')
                start_year = int(start_year_str)
                end_year = int(end_year_str)
            except ValueError:
                self.stdout.write(self.style.WARNING(f"Skipping user {user.username}: Invalid year format {year_part}"))
                continue
            
            # 2. Get/Create Financial Year
            start_date = datetime.date(start_year, 4, 1)
            end_date = datetime.date(end_year, 3, 31)
            
            fy, created = FinancialYear.objects.get_or_create(
                start_date=start_date, 
                end_date=end_date
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Financial Year: {fy}"))
            
            # 3. Get Base User
            try:
                base_user = User.objects.get(username=base_username)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Base user {base_username} not found for {user.username}"))
                continue
                
            self.stdout.write(f"Migrating {user.username} -> {base_user.username} for FY {fy}")
            
            # 4. Check for constraints
            # LedgerData has (user, l_r_no) unique constraint effectively.
            # We must ensure we don't collide with existing data in base_user.
            # Since we removed the constraint in models, we are technically safe from DB error,
            # but we will have duplicates if base_user already has data for same LR.
            # However, base_user usually contains CURRENT year data. 
            # Migrating OLD data (2021) should be fine as LR numbers reset or are different?
            # User said: "create uder for new fincial year with same name and update old with @year"
            # So `cash-center` has 2024-2025 data. `cash-center@2023-2024` has old data.
            # Merging them: `cash-center` gets 2023 data. 
            # 2023 LR=1 vs 2024 LR=1. They collide on (user, LR).
            # But we differentiate by FY now.
            
            if not dry_run:
                with transaction.atomic():
                   # Ledger
                   count_ledger = LedgerData.objects.filter(user=user).update(user=base_user, financial_year=fy)
                   self.stdout.write(f"  Migrated {count_ledger} Ledger entries")
                   
                   # Order
                   count_order = Order.objects.filter(user=user).update(user=base_user, financial_year=fy)
                   self.stdout.write(f"  Migrated {count_order} Orders")
                   
                   # Stock
                   count_stock = StockData.objects.filter(user=user).update(user=base_user, financial_year=fy)
                   self.stdout.write(f"  Migrated {count_stock} Stock entries")
                   
                   # Ratelist
                   count_ratelist = RatelistData.objects.filter(user=user).update(user=base_user, financial_year=fy)
                   self.stdout.write(f"  Migrated {count_ratelist} Ratelist entries")

                   # Deactivate old user
                   user.is_active = False
                   user.save()
            
        # 5. Handle "Current" data for users (base users)
        # Identify users who have unassigned data
        # We assume unassigned data belongs to the CURRENT financial year relative to today
        today = datetime.date.today()
        # Fiscal year start: If today is after April 1st, Start Year = Today.year. Else Start Year = Today.year - 1
        if today.month >= 4:
            current_start_year = today.year
            current_end_year = today.year + 1
        else:
            current_start_year = today.year - 1
            current_end_year = today.year
            
        current_start_date = datetime.date(current_start_year, 4, 1)
        current_end_date = datetime.date(current_end_year, 3, 31)
        
        current_fy, created = FinancialYear.objects.get_or_create(
            start_date=current_start_date,
            end_date=current_end_date
        )
        if created:
             self.stdout.write(self.style.SUCCESS(f"Created Current Financial Year: {current_fy}"))
             
        # Update logic: Find all data where financial_year is NULL and assign current_fy
        if not dry_run:
            with transaction.atomic():
                count_ledger = LedgerData.objects.filter(financial_year__isnull=True).update(financial_year=current_fy)
                if count_ledger > 0:
                    self.stdout.write(f"  Assigned {count_ledger} orphan Ledger entries to Current FY {current_fy}")
                
                count_order = Order.objects.filter(financial_year__isnull=True).update(financial_year=current_fy)
                if count_order > 0:
                    self.stdout.write(f"  Assigned {count_order} orphan Orders to Current FY {current_fy}")

                count_stock = StockData.objects.filter(financial_year__isnull=True).update(financial_year=current_fy)
                if count_stock > 0:
                    self.stdout.write(f"  Assigned {count_stock} orphan Stock entries to Current FY {current_fy}")

                count_ratelist = RatelistData.objects.filter(financial_year__isnull=True).update(financial_year=current_fy)
                if count_ratelist > 0:
                     self.stdout.write(f"  Assigned {count_ratelist} orphan Ratelist entries to Current FY {current_fy}")
