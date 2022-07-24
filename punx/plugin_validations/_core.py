"""
Python plugin loading system.

# from: https://gist.github.com/will-hart/5899567
# a simple Python plugin loading system
# see: http://stackoverflow.com/questions/14510286/plugin-architecture-plugin-manager-vs-inspecting-from-plugins-import
"""

# import imp
# import pathlib


# def install_user_plugin(plugin_file):
#     """
#     Install plugin(s) from a Python file.
#     Potentially dangerous since this is an import of a user-created file.
#     """
#     plugin = pathlib.Path(plugin_file).absolute()
#     if not plugin.exists():
#         raise FileExistsError(plugin_file)

#     module_name = plugin.stem

#     fp, path, desc = imp.find_module(module_name, [str(plugin.parent)])
#     imp.load_module(module_name, fp, path, desc)


class PluginMounter(type):
    """
    Register and initiate all plugins subclassed from PluginBase.
    Acts as a metaclass which creates anything inheriting from PluginBase.
    A plugin mount point derived from:
    http://martyalchin.com/2008/jan/10/simple-plugin-framework/
    """

    def __init__(cls, name, bases, attrs):
        """Called when a PluginBase derived class is imported."""

        if not hasattr(cls, 'plugins'):
            # Called when the metaclass is first instantiated
            cls.plugins = []
        else:
            # Called when a plugin class is imported
            cls._enroll(cls)

    def _enroll(cls, plugin):
        """Add the plugin to the plugin list and perform any registration logic"""

        # create a plugin instance and store it
        instance = plugin()

        # save the plugin reference
        cls.plugins.append(instance)

        # apply plugin logic as defined by the plugin
        instance.register()

    def register(self):
        raise NotImplementedError(
            "MUST define 'register()' method in subclass."
        )


class ValidationPluginBase(metaclass=PluginMounter):
    """A plugin which must provide a `register()` method."""

    def __str__(self):
        return f"Validator: {self.__class__.__name__}"

    def action(self):
        """
        The `action()` method describes the plugin's action(s).
        """
        raise NotImplementedError(
            "MUST define 'action()' method in subclass."
        )
