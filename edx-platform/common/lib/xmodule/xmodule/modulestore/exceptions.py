"""
Exceptions thrown by KeyStore objects
"""


class ItemNotFoundError(Exception):
    pass


class ItemWriteConflictError(Exception):
    pass


class MultipleCourseBlocksFound(Exception):
    """
    Raise this exception when Iterating over the course blocks return multiple course blocks.
    """
    pass


class MultipleLibraryBlocksFound(Exception):
    """
    Raise this exception when Iterating over the library blocks return multiple library blocks.
    """
    pass


class InsufficientSpecificationError(Exception):
    pass


class OverSpecificationError(Exception):
    pass


class InvalidLocationError(Exception):
    pass


class NoPathToItem(Exception):
    pass


class ReferentialIntegrityError(Exception):
    """
    An incorrect pointer to an object exists. For example, 2 parents point to the same child, an
    xblock points to a nonexistent child (which probably raises ItemNotFoundError instead depending
    on context).
    """
    pass


class DuplicateItemError(Exception):
    """
    Attempted to create an item which already exists.
    """
    def __init__(self, element_id, store=None, collection=None):
        super(DuplicateItemError, self).__init__()
        self.element_id = element_id
        self.store = store
        self.collection = collection

    def __str__(self, *args, **kwargs):
        """
        Print info about what's duplicated
        """
        return "{store}[{collection}] already has {element_id} ({exception})".format(
            store=self.store,
            collection=self.collection,
            element_id=self.element_id,
            exception=Exception.__str__(self, *args, **kwargs),
        )


class VersionConflictError(Exception):
    """
    The caller asked for either draft or published head and gave a version which conflicted with it.
    """
    def __init__(self, requestedLocation, currentHeadVersionGuid):
        super(VersionConflictError, self).__init__(u'Requested {}, but current head is {}'.format(
            requestedLocation,
            currentHeadVersionGuid
        ))


class DuplicateCourseError(Exception):
    """
    An attempt to create a course whose id duplicates an existing course's
    """
    def __init__(self, course_id, existing_entry):
        """
        existing_entry will have the who, when, and other properties of the existing entry
        """
        super(DuplicateCourseError, self).__init__(
            u'Cannot create course {}, which duplicates {}'.format(course_id, existing_entry)
        )
        self.course_id = course_id
        self.existing_entry = existing_entry


class InvalidBranchSetting(Exception):
    """
    Raised when the process' branch setting did not match the required setting for the attempted operation on a store.
    """
    def __init__(self, expected_setting, actual_setting):
        super(InvalidBranchSetting, self).__init__(u"Invalid branch: expected {} but got {}".format(expected_setting, actual_setting))
        self.expected_setting = expected_setting
        self.actual_setting = actual_setting
