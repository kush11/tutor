# pylint:disable=missing-docstring
import factory

from student.tests.factories import UserFactory
from survey.models import SurveyAnswer, SurveyForm


class SurveyFormFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = SurveyForm

    name = 'Test Survey Form'
    form = '<form>First name:<input type="text" name="firstname"/></form>'


class SurveyAnswerFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = SurveyAnswer

    user = factory.SubFactory(UserFactory)
    form = factory.SubFactory(SurveyFormFactory)
