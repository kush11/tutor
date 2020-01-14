"""
Models for the dark-launching languages
"""
from config_models.models import ConfigurationModel
from django.db import models


class DarkLangConfig(ConfigurationModel):
    """
    Configuration for the dark_lang django app.
    """
    released_languages = models.TextField(
        blank=True,
        help_text="A comma-separated list of language codes to release to the public."
    )

    def __unicode__(self):
        return u"DarkLangConfig()"

    @property
    def released_languages_list(self):
        """
        ``released_languages`` as a list of language codes.

        Example: ['it', 'de-at', 'es', 'pt-br']
        """
        if not self.released_languages.strip():
            return []

        languages = [lang.lower().strip() for lang in self.released_languages.split(',')]
        # Put in alphabetical order
        languages.sort()
        return languages
