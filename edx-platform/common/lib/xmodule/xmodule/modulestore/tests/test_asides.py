"""
Tests for Asides
"""
from web_fragments.fragment import Fragment
from xblock.core import XBlockAside
from xblock.fields import Scope, String
from unittest import TestCase
from xmodule.modulestore.tests.utils import XmlModulestoreBuilder
from mock import patch


class AsideTestType(XBlockAside):
    """
    Test Aside type
    """
    FRAG_CONTENT = u"<p>Aside rendered</p>"

    content = String(default="default_content", scope=Scope.content)
    data_field = String(default="default_data", scope=Scope.settings)

    @XBlockAside.aside_for('student_view')
    def student_view_aside(self, block, context):  # pylint: disable=unused-argument
        """Add to the student view"""
        return Fragment(self.FRAG_CONTENT)


class TestAsidesXmlStore(TestCase):
    """
    Test Asides sourced from xml store
    """
    shard = 1

    @patch('xmodule.modulestore.xml.ImportSystem.applicable_aside_types', lambda self, block: ['test_aside'])
    @XBlockAside.register_temp_plugin(AsideTestType, 'test_aside')
    def test_xml_aside(self):
        """
        Check that the xml modulestore read in all the asides with their values
        """
        with XmlModulestoreBuilder().build(course_ids=['edX/aside_test/2012_Fall']) as (__, store):
            def check_block(block):
                """
                Check whether block has the expected aside w/ its fields and then recurse to the block's children
                """
                asides = block.runtime.get_asides(block)
                self.assertEqual(len(asides), 1, "Found {} asides but expected only test_aside".format(asides))
                self.assertIsInstance(asides[0], AsideTestType)
                category = block.scope_ids.block_type
                self.assertEqual(asides[0].data_field, "{} aside data".format(category))
                self.assertEqual(asides[0].content, "{} Aside".format(category.capitalize()))

                for child in block.get_children():
                    check_block(child)

            check_block(store.get_course(store.make_course_key('edX', "aside_test", "2012_Fall")))
