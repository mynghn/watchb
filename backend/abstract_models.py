from django.db import models
from django.db.models.fields import Field


class TimestampModel(models.Model):
    class Meta:
        abstract = True

    timestamp = models.DateTimeField(auto_now_add=True)


class CreateAndUpdateModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OnOffModel(models.Model):
    class Meta:
        abstract = True

    first_timestamp = models.DateTimeField(auto_now_add=True)
    last_timestamp = models.DateTimeField(auto_now=True)
    on = models.BooleanField(default=True)

    @property
    def off(self):
        return not self.on


class UpdateHistoryModel(TimestampModel):
    class Meta:
        abstract = True

    is_active = models.BooleanField(default=True)

    @classmethod
    def get_latest_record(cls, **queryset_kwargs) -> models.Model:
        return cls.objects.filter(**queryset_kwargs).latest("timestamp")

    def _deactivate_former_records(self):
        for record in self.__class__.objects.filter(
            {
                f.name: getattr(self, f.name)
                for f in self._meta.get_fields()
                if isinstance(f, Field)
            }
        ):
            if record != self:
                record.is_active = False
                record.save(update_fields=["is_active"])

    def save(self, *args, **kwargs) -> None:
        """Override default save() method to deactivate all the former records"""
        saved_instance = super(UpdateHistoryModel, self).save(*args, **kwargs)
        self._deactivate_former_records()
        return saved_instance
