"""
Models for configuration of Block Structures.
"""
from django.db.models import IntegerField
from config_models.models import ConfigurationModel


class BlockStructureConfiguration(ConfigurationModel):
    """
    Configuration model for Block Structures.
    """
    DEFAULT_PRUNE_KEEP_COUNT = 5
    DEFAULT_CACHE_TIMEOUT_IN_SECONDS = 60 * 60 * 24  # 24 hours

    class Meta(object):
        app_label = 'block_structure'
        db_table = 'block_structure_config'

    num_versions_to_keep = IntegerField(blank=True, null=True, default=DEFAULT_PRUNE_KEEP_COUNT)
    cache_timeout_in_seconds = IntegerField(blank=True, null=True, default=DEFAULT_CACHE_TIMEOUT_IN_SECONDS)

    def __unicode__(self):
        return u"BlockStructureConfiguration: num_versions_to_keep: {}, cache_timeout_in_seconds: {}".format(
            self.num_versions_to_keep,
            self.cache_timeout_in_seconds,
        )
