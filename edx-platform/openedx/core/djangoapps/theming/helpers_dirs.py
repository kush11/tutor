"""
Code which dynamically discovers comprehensive themes. Deliberately uses no Django settings,
as the discovery happens during the initial setup of Django settings.
"""
import os
from path import Path


def get_theme_base_dirs_from_settings(theme_dirs=None):
    """
    Return base directories that contains all the themes.

    Example:
        >> get_theme_base_dirs_from_settings('/edx/app/ecommerce/ecommerce/themes')
        ['/edx/app/ecommerce/ecommerce/themes']

    Returns:
         (List of Paths): Base theme directory paths
    """
    theme_base_dirs = []
    if theme_dirs:
        theme_base_dirs.extend([Path(theme_dir) for theme_dir in theme_dirs])
    return theme_base_dirs


def get_themes_unchecked(themes_dirs, project_root=None):
    """
    Returns a list of all themes known to the system.

    Args:
        themes_dirs (list): Paths to themes base directory
        project_root (str): (optional) Path to project root
    Returns:
        List of themes known to the system.
    """
    themes_base_dirs = [Path(themes_dir) for themes_dir in themes_dirs]
    # pick only directories and discard files in themes directory
    themes = []
    for themes_dir in themes_base_dirs:
        themes.extend([Theme(name, name, themes_dir, project_root) for name in get_theme_dirs(themes_dir)])

    return themes


def get_theme_dirs(themes_dir=None):
    """
    Returns theme dirs in given dirs
    Args:
        themes_dir (Path): base dir that contains themes.
    """
    return [_dir for _dir in os.listdir(themes_dir) if is_theme_dir(themes_dir / _dir)]


def is_theme_dir(_dir):
    """
    Returns true if given dir contains theme overrides.
    A theme dir must have subdirectory 'lms' or 'cms' or both.

    Args:
        _dir: directory path to check for a theme

    Returns:
        Returns true if given dir is a theme directory.
    """
    theme_sub_directories = {'lms', 'cms'}
    return bool(os.path.isdir(_dir) and theme_sub_directories.intersection(os.listdir(_dir)))


def get_project_root_name_from_settings(project_root):
    """
    Return root name for the current project

    Example:
        >> get_project_root_name()
        'lms'
        # from studio
        >> get_project_root_name()
        'cms'

    Args:
        project_root (str): Root directory of the project.

    Returns:
        (str): component name of platform e.g lms, cms
    """
    root = Path(project_root)
    if root.name == "":
        root = root.parent
    return root.name


class Theme(object):
    """
    class to encapsulate theme related information.
    """
    name = ''
    theme_dir_name = ''
    themes_base_dir = None
    project_root = None

    def __init__(self, name='', theme_dir_name='', themes_base_dir=None, project_root=None):
        """
        init method for Theme

        Args:
            name: name if the theme
            theme_dir_name: directory name of the theme
            themes_base_dir: directory path of the folder that contains the theme
        """
        self.name = name
        self.theme_dir_name = theme_dir_name
        self.themes_base_dir = themes_base_dir
        self.project_root = project_root

    def __eq__(self, other):
        """
        Returns True if given theme is same as the self
        Args:
            other: Theme object to compare with self

        Returns:
            (bool) True if two themes are the same else False
        """
        return (self.theme_dir_name, self.path) == (other.theme_dir_name, other.path)

    def __hash__(self):
        return hash((self.theme_dir_name, self.path))

    def __unicode__(self):
        return u"<Theme: {name} at '{path}'>".format(name=self.name, path=self.path)

    def __repr__(self):
        return self.__unicode__()

    @property
    def path(self):
        """
        Get absolute path of the directory that contains current theme's templates, static assets etc.

        Returns:
            Path: absolute path to current theme's contents
        """
        return Path(self.themes_base_dir) / self.theme_dir_name / get_project_root_name_from_settings(self.project_root)

    @property
    def template_path(self):
        """
        Get absolute path of current theme's template directory.

        Returns:
            Path: absolute path to current theme's template directory
        """
        return Path(self.theme_dir_name) / get_project_root_name_from_settings(self.project_root) / 'templates'

    @property
    def template_dirs(self):
        """
        Get a list of all template directories for current theme.

        Returns:
            list: list of all template directories for current theme.
        """
        return [
            self.path / 'templates',
        ]
