from django.db import models


class CreateAndUpdateModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=False)
    last_updated_at = models.DateTimeField(auto_now=False)


class OnOffModel(models.Model):
    class Meta:
        abstract = True

    first_timestamp = models.DateTimeField(auto_now_add=False)
    last_timestamp = models.DateTimeField(auto_now=False)
    on = models.BooleanField(default=True)

    @property
    def off(self):
        return not self.on
