"""
Code to delete rows from a table within a Django mgmt command using best practices.
"""

import logging
import time
from django.core.management.base import CommandError, BaseCommand
from django.db import transaction

log = logging.getLogger(__name__)


def delete_rows(model_mgr,
                table_name,
                primary_id_name,
                chunk_size,
                sleep_between):
    """
    Deletes *ALL* rows from table, chunking the deletes to avoid long table/row locks.

    Args:
        model_mgr (django.db.models.manager.Manager): Django ORM mgr for the table's model.
        table_name (str): Name of table from which to delete all rows.
        primary_id_name (str): Name of primary ID autoincrement column from table.
        chunk_size (int): Number of rows to delete in each transaction.
        sleep_between (float): Number of seconds to sleep between transactions.
    """
    if chunk_size <= 0:
        raise CommandError('Only positive chunk size is allowed ({}).'.format(chunk_size))
    if sleep_between < 0:
        raise CommandError('Only non-negative sleep between seconds is allowed ({}).'.format(sleep_between))

    # The "as id" below fools Django raw query into thinking the primary key is being queried.
    # It's necessary because Django will throw an exception if the raw SQL does not query the primary key.
    min_max_ids = model_mgr.raw(
        'SELECT MIN({}) as id, MAX({}) as max_id FROM {}'.format(primary_id_name, primary_id_name, table_name)
    )[0]
    min_id = min_max_ids.id
    max_id = min_max_ids.max_id
    if not min_id or not max_id:
        log.info("No data exists in table %s - skipping.", table_name)
        return
    log.info(
        "STARTED: Deleting around %s rows with chunk size of %s and %s seconds between chunks.",
        max_id - min_id + 1, chunk_size, sleep_between
    )

    lower_id = min_id
    while lower_id <= max_id:
        deletions_now = min(chunk_size, max_id - lower_id + 1)
        upper_id = lower_id + deletions_now
        log.info("Deleting around %s rows between ids %s and %s...", deletions_now, lower_id, upper_id)
        with transaction.atomic():
            # xss-lint: disable=python-wrap-html
            delete_sql = 'DELETE FROM {} WHERE {} >= {} AND {} < {}'.format(
                table_name, primary_id_name, lower_id, primary_id_name, upper_id
            )
            log.info(delete_sql)
            try:
                list(model_mgr.raw(delete_sql))
            except TypeError:
                # The list() above is simply to get the RawQuerySet to be evaluated.
                # Without evaluation, the raw DELETE SQL will *not* actually execute.
                # But - it will cause a "TypeError: 'NoneType' object is not iterable" to be ignored.
                pass
        lower_id += deletions_now
        log.info("Sleeping %s seconds...", sleep_between)
        time.sleep(sleep_between)
    log.info("FINISHED: Deleted at most %s rows total.", max_id - min_id + 1)


class BaseDeletionCommand(BaseCommand):
    """
    Base command used to delete all rows from a table.
    """
    # Default maximum number of rows to delete in a single transaction.
    DEFAULT_CHUNK_SIZE = 10000

    # Default seconds to sleep between chunked deletes of rows.
    DEFAULT_SLEEP_BETWEEN_DELETES = 0

    def add_arguments(self, parser):
        parser.add_argument(
            '--chunk_size',
            default=self.DEFAULT_CHUNK_SIZE,
            type=int,
            help='Maximum number of rows to delete in each DB transaction. Choose this value carefully to avoid DB outages!'
        )
        parser.add_argument(
            '--sleep_between',
            default=self.DEFAULT_SLEEP_BETWEEN_DELETES,
            type=float,
            help='Seconds to sleep between chunked delete of rows.'
        )

    def handle(self, *args, **options):
        """
        Deletes rows, chunking the deletes to avoid long table/row locks.
        """
        return (
            options.get('chunk_size', self.DEFAULT_CHUNK_SIZE),
            options.get('sleep_between', self.DEFAULT_SLEEP_BETWEEN_DELETES)
        )
