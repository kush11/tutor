"""
Simple test to ensure that modulestore base classes remain abstract
"""
from unittest import TestCase

from xmodule.modulestore import ModuleStoreRead, ModuleStoreWrite


class AbstractionTest(TestCase):
    """
    Tests that the ModuleStore objects are properly abstracted
    """
    shard = 1

    def test_cant_instantiate_abstract_class(self):
        self.assertRaises(TypeError, ModuleStoreRead)  # Cannot be instantiated due to explicit abstraction
        self.assertRaises(TypeError, ModuleStoreWrite)
