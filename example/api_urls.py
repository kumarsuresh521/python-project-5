'''
WooClub Api
'''
import importlib

from django.conf import settings
from django.conf.urls import include, url


class ApiUrl(object):
    '''
    Api Urls
    '''
    @staticmethod
    def api_default_urls():
        ''' Default Urls '''
        urlpatterns = []
        for app in settings.LOCAL_APPS:
            app_module = importlib.import_module(app)
            for version in settings.APP_VERSION:
                try:
                    api_urls_exists = importlib.util.find_spec(
                        '{}.{}.apiurls'.format(app, version))
                    if api_urls_exists:
                        urlpatterns.append(url(r'' + app_module.__name__ + '/', include(
                            '{}.{}.apiurls'.format(app, version))))
                except ImportError:
                    api_urls_exists = importlib.util.find_spec(
                        '%s.apiurls' % app)
                    if api_urls_exists:
                        urlpatterns.append(url(r'' + app_module.__name__ + '/', include(
                            '{}.apiurls'.format(app))))

        return urlpatterns

    @staticmethod
    def web_default_urls():
        ''' Default Urls '''
        urlpatterns = []
        for app in settings.LOCAL_APPS:
            app_module = importlib.import_module(app)
            for version in settings.APP_VERSION:
                try:
                    api_urls_exists = importlib.util.find_spec(
                        '{}.{}.weburls'.format(app, version))
                    if api_urls_exists:
                        urlpatterns.append(url(r'' + app_module.__name__ + '/', include(
                            '{}.{}.weburls'.format(app, version))))
                except ImportError:
                    api_urls_exists = importlib.util.find_spec(
                        '%s.weburls' % app)
                    if api_urls_exists:
                        urlpatterns.append(url(r'' + app_module.__name__ + '/', include(
                            '{}.weburls'.format(app))))

        return urlpatterns
    @property
    def api_urls(self):
        '''Urls '''
        return self.api_default_urls(), 'api', 'api'

    @property
    def web_urls(self):
        '''Urls '''
        return self.web_default_urls(), 'web', 'web'

apiurls = ApiUrl()
