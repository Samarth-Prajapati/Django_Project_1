from django.db import models
import calendar
from datetime import date

# Create your models here.

class ActiveManager(models.Manager):
    """Manager that returns only active records"""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class Resource(models.Model):
    """
    Stores resource (developer/employee) data for a specific year and month.
    Working days are auto-calculated (Mon–Fri + 1st Saturday) unless provided.
    """

    resource_name = models.CharField(
        max_length=100,
        help_text="Enter the full name of the resource"
    )

    year = models.PositiveIntegerField(
        help_text="Enter the year manually (e.g., 2025)"
    )

    month = models.PositiveSmallIntegerField(
        choices=[(i, calendar.month_name[i]) for i in range(1, 13)],
        help_text="Enter the month manually (1–12)"
    )

    working_days = models.FloatField(
        null=True,
        blank=True,
        help_text="Leave blank to auto-calculate (Mon–Fri + 1st Saturday)"
    )

    present_day = models.FloatField(
        default=0,
        help_text="Days resource was present"
    )

    present_hours = models.FloatField(
        default=0,
        help_text="Auto-calculated as present_day × 8 hours if not set"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    counting = models.FloatField(default=0, help_text="Counting value")
    is_active = models.BooleanField(default=True, help_text="For soft deletion")

    # Managers
    objects = models.Manager()  # Default manager for admin and migrations
    active_objects = ActiveManager()  # Manager for active records only

    class Meta:
        db_table = 'resources'
        ordering = ['-year', '-month', 'resource_name']
        verbose_name = 'Resource'
        verbose_name_plural = 'Resources'

    def __str__(self):
        return f"{self.resource_name} - {calendar.month_name[self.month]} {self.year}"

    def save(self, *args, **kwargs):
        # Auto-calculate working days if not set
        if not self.working_days:
            self.working_days = self.get_working_days(self.year, self.month)

        # Auto-calculate present hours based on present_day (always recalculate)
        if self.present_day:
            self.present_hours = self.present_day * 8
        else:
            self.present_hours = 0

        super().save(*args, **kwargs)

    @staticmethod
    def get_working_days(year, month):
        """
        Calculates working days (Mon–Fri + 1st Saturday) for a given year and month.
        """
        if year is None or month is None:
            return 0
            
        _, num_days = calendar.monthrange(year, month)
        first_day = calendar.monthrange(year, month)[0]
        first_saturday = (5 - first_day) % 7 + 1
        if first_saturday > num_days:
            first_saturday = None

        working_days = 0
        for day in range(1, num_days + 1):
            weekday = (first_day + day - 1) % 7
            if weekday < 5:
                working_days += 1

        if first_saturday:
            working_days += 1

        return working_days

    def get_working_days_for_display(self):
        if self.year is None or self.month is None:
            return "0 days (year/month not set)"
        wd = self.get_working_days(self.year, self.month)
        return f"{wd} days ({calendar.month_name[self.month]} {self.year})"

    def soft_delete(self):
        """Soft delete the resource"""
        self.is_active = False
        self.save()

    def restore(self):
        """Restore soft deleted resource"""
        self.is_active = True
        self.save()