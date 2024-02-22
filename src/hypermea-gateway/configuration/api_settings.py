from hypermea.core.settings_manager import SettingsManager

DEFAULT_CURIES_NAMESPACE_URI = 'uri://hypermea.com'
# note: this is used to emit a warning if the default curies namespace was not overridden

PREFIX = 'GW'
SETTINGS = SettingsManager.instance()
SETTINGS.set_prefix_description(PREFIX, 'Settings for hypermea-gateway')
SETTINGS.create(PREFIX, {
    'CURIES_NAMESPACE_URI':  DEFAULT_CURIES_NAMESPACE_URI
})
