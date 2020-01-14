"""
Test for asset XML generation / parsing.
"""

import unittest
from path import Path as path
from lxml import etree
from contracts import ContractNotRespected

from opaque_keys.edx.locator import CourseLocator
from xmodule.assetstore import AssetMetadata
from xmodule.modulestore.tests.test_assetstore import AssetStoreTestData


class TestAssetXml(unittest.TestCase):
    """
    Tests for storing/querying course asset metadata.
    """
    shard = 1

    def setUp(self):
        super(TestAssetXml, self).setUp()

        xsd_filename = "assets.xsd"

        self.course_id = CourseLocator('org1', 'course1', 'run1')

        self.course_assets = []
        for asset in AssetStoreTestData.all_asset_data:
            asset_dict = dict(zip(AssetStoreTestData.asset_fields[1:], asset[1:]))
            asset_md = AssetMetadata(self.course_id.make_asset_key('asset', asset[0]), **asset_dict)
            self.course_assets.append(asset_md)

        # Read in the XML schema definition and make a validator.
        xsd_path = path(__file__).realpath().parent / xsd_filename
        with open(xsd_path, 'r') as f:
            schema_root = etree.XML(f.read())
        schema = etree.XMLSchema(schema_root)
        self.xmlparser = etree.XMLParser(schema=schema)

    def test_export_single_asset_to_from_xml(self):
        """
        Export a single AssetMetadata to XML and verify the structure and fields.
        """
        asset_md = self.course_assets[0]
        root = etree.Element("assets")
        asset = etree.SubElement(root, "asset")
        asset_md.to_xml(asset)
        # If this line does *not* raise, the XML is valid.
        etree.fromstring(etree.tostring(root), self.xmlparser)
        new_asset_key = self.course_id.make_asset_key('tmp', 'tmp')
        new_asset_md = AssetMetadata(new_asset_key)
        new_asset_md.from_xml(asset)
        # Compare asset_md to new_asset_md.
        for attr in AssetMetadata.XML_ATTRS:
            if attr in AssetMetadata.XML_ONLY_ATTRS:
                continue
            orig_value = getattr(asset_md, attr)
            new_value = getattr(new_asset_md, attr)
            self.assertEqual(orig_value, new_value)

    def test_export_with_None_value(self):
        """
        Export and import a single AssetMetadata to XML with a None created_by field, without causing an exception.
        """
        asset_md = AssetMetadata(
            self.course_id.make_asset_key('asset', 'none_value'),
            created_by=None,
        )
        asset = etree.Element("asset")
        asset_md.to_xml(asset)
        asset_md.from_xml(asset)

    def test_export_all_assets_to_xml(self):
        """
        Export all AssetMetadatas to XML and verify the structure and fields.
        """
        root = etree.Element("assets")
        AssetMetadata.add_all_assets_as_xml(root, self.course_assets)
        # If this line does *not* raise, the XML is valid.
        etree.fromstring(etree.tostring(root), self.xmlparser)

    def test_wrong_node_type_all(self):
        """
        Ensure full asset sections with the wrong tag are detected.
        """
        root = etree.Element("glassets")
        with self.assertRaises(ContractNotRespected):
            AssetMetadata.add_all_assets_as_xml(root, self.course_assets)

    def test_wrong_node_type_single(self):
        """
        Ensure single asset blocks with the wrong tag are detected.
        """
        asset_md = self.course_assets[0]
        root = etree.Element("assets")
        asset = etree.SubElement(root, "smashset")
        with self.assertRaises(ContractNotRespected):
            asset_md.to_xml(asset)
