"""
Removes user PII from OAuth2 models.
"""

from oauth2_provider.models import (
    AccessToken as DOTAccessToken,
    Application as DOTApplication,
    Grant as DOTGrant,
    RefreshToken as DOTRefreshToken,
)
from provider.oauth2.models import (
    AccessToken as DOPAccessToken,
    RefreshToken as DOPRefreshToken,
    Grant as DOPGrant,
)


class ModelRetirer(object):
    """
    Given a list of model names, provides methods for deleting instances of
    those models.
    """

    def __init__(self, models_to_retire):
        self._models_to_retire = models_to_retire

    def retire_user_by_id(self, user_id):
        for model in self._models_to_retire:
            self._delete_user_id_from(model=model, user_id=user_id)

    @staticmethod
    def _delete_user_id_from(model, user_id):
        """
        Deletes a user from a model by their user id.
        """
        user_query_results = model.objects.filter(user_id=user_id)

        if not user_query_results.exists():
            return False

        user_query_results.delete()
        return True


def retire_dot_oauth2_models(user):
    dot_models = [DOTAccessToken, DOTApplication, DOTGrant, DOTRefreshToken]
    ModelRetirer(dot_models).retire_user_by_id(user.id)


def retire_dop_oauth2_models(user):
    dop_models = [DOPAccessToken, DOPGrant, DOPRefreshToken]
    ModelRetirer(dop_models).retire_user_by_id(user.id)
