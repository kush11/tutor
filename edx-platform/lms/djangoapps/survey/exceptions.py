"""
Specialized exceptions for the Survey Djangoapp
"""


class SurveyFormNotFound(Exception):
    """
    Thrown when a SurveyForm is not found in the database
    """
    pass


class SurveyFormNameAlreadyExists(Exception):
    """
    Thrown when a SurveyForm is created but that name already exists
    """
    pass
