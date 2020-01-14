"""Admin forms for Course Entitlements"""
from django import forms
from django.contrib import admin
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey

from xmodule.modulestore.django import modulestore

from .models import CourseEntitlement, CourseEntitlementPolicy, CourseEntitlementSupportDetail


@admin.register(CourseEntitlement)
class CourseEntitlementAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'uuid',
                    'course_uuid',
                    'created',
                    'modified',
                    'expired_at',
                    'mode',
                    'enrollment_course_run',
                    'order_number')
    raw_id_fields = ('enrollment_course_run', 'user',)
    search_fields = ('user__username', 'uuid', 'course_uuid', 'mode', 'order_number')


class CourseEntitlementSupportDetailForm(forms.ModelForm):
    """Form for adding entitlement support details, exists mostly for testing purposes"""
    def __init__(self, *args, **kwargs):
        super(CourseEntitlementSupportDetailForm, self).__init__(*args, **kwargs)

        if self.data.get('unenrolled_run'):
            try:
                self.data['unenrolled_run'] = CourseKey.from_string(self.data['unenrolled_run'])
            except InvalidKeyError:
                raise forms.ValidationError("No valid CourseKey for id {}!".format(self.data['unenrolled_run']))

    def clean_course_id(self):
        """Cleans course id and attempts to make course key from string version of key"""
        course_id = self.cleaned_data['unenrolled_run']
        try:
            course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            raise forms.ValidationError("Cannot make a valid CourseKey from id {}!".format(course_id))

        if not modulestore().has_course(course_key):
            raise forms.ValidationError("Cannot find course with id {} in the modulestore".format(course_id))

        return course_key

    class Meta:
        fields = '__all__'
        model = CourseEntitlementSupportDetail


@admin.register(CourseEntitlementSupportDetail)
class CourseEntitlementSupportDetailAdmin(admin.ModelAdmin):
    """
    Registration of CourseEntitlementSupportDetail for Django Admin
    """
    list_display = ('entitlement',
                    'support_user',
                    'comments',
                    'unenrolled_run')
    raw_id_fields = ('unenrolled_run', 'support_user',)
    form = CourseEntitlementSupportDetailForm


class CourseEntitlementPolicyForm(forms.ModelForm):
    """ Form for creating custom course entitlement policies. """
    def __init__(self, *args, **kwargs):
        super(CourseEntitlementPolicyForm, self).__init__(*args, **kwargs)
        self.fields['site'].required = False
        self.fields['mode'].required = False

    class Meta:
        fields = '__all__'
        model = CourseEntitlementPolicy


@admin.register(CourseEntitlementPolicy)
class CourseEntitlementPolicyAdmin(admin.ModelAdmin):
    """
    Registration of CourseEntitlementPolicy for Django Admin
    """
    list_display = ('expiration_period',
                    'refund_period',
                    'regain_period',
                    'mode',
                    'site')
    form = CourseEntitlementPolicyForm
