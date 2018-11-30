"""Module that defines entry point to the Protean Flask Application"""
import hashlib

from flask import Request, request, current_app, Blueprint

from protean.core.exceptions import UsecaseExecutionError
from protean.utils.importlib import perform_import
from protean.conf import active_config
from protean.context import context

from .views import APIResource
from ..utils import derive_tenant


class ProteanRequest(Request):
    """ Custom request object to store protean specific code"""
    payload = None


class Protean(object):
    """
    The main entry point for the application.
    You need to initialize it with a Flask Application.

    >>> app = Flask(__name__)
    >>> api = Protean(app)

    Alternatively, you can use :meth:`init_app` to set the Flask application
    after it has been constructed.

    :param app_or_bp: the Flask application or blueprint object.

    """

    def __init__(self, app_or_bp=None):
        self.app = None
        self.blueprint = None
        self.exception_handler = None
        self.viewsets = []

        if app_or_bp is not None:
            self.app = app_or_bp
            if isinstance(app_or_bp, Blueprint):
                self.blueprint = app_or_bp
            else:
                self.init_app(app_or_bp)

    def init_app(self, app):
        """Perform initialization actions with the given :class:`flask.Flask`
        object.

        :param app: The flask application object
        :type app: flask.Flask
        """
        # Update the request class for the app
        app.request_class = ProteanRequest

        # Manage the context information before/after request
        app.before_request(self._load_protean_context)
        app.after_request(self._cleanup_protean_context)

        # Register error handlers for the app
        app.register_error_handler(
            UsecaseExecutionError, self._handle_exception)
        self.exception_handler = perform_import(active_config.EXCEPTION_HANDLER)

        # Update the current configuration
        app.config.from_object(active_config)

    def register_viewset(self, view, endpoint, url, pk_name='identifier',
                         pk_type='string', additional_routes=None):
        """Register a Viewset

        Additional routes (apart from the standard five) can be specified via
            `additional_routes` argument. Note that the route names have to be
            the same as method names
        """
        view_func = view.as_view(endpoint)

        # add the custom routes to the app
        if additional_routes is None:
            additional_routes = list()
        for route in additional_routes:
            self.app.add_url_rule(
                '{}{}'.format(url, route), view_func=view_func)

        # Standard routes
        self.app.add_url_rule(url, defaults={pk_name: None},
                              view_func=view_func, methods=['GET', ])
        self.app.add_url_rule(url, view_func=view_func, methods=['POST', ])

        # Make sure that the url ends with a
        url = f'{url}/' if not url.endswith('/') else url
        self.app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk_name),
                              view_func=view_func,
                              methods=['GET', 'PUT', 'DELETE'])

    @staticmethod
    def _load_protean_context():
        """ Load the protean context with details from the request"""

        user_agent = request.headers.get('User-Agent', '')
        hashed_user_agent = hashlib.sha256(user_agent.encode())

        details = {
            'host_url': request.host_url,
            'url': request.url,
            'tenant_id': derive_tenant(request.url),
            'user_agent': user_agent,
            'user_agent_hash': hashed_user_agent.hexdigest(),
            'remote_addr': request.remote_addr
        }
        context.set_context(details)

    @staticmethod
    def _cleanup_protean_context(response):
        """ Cleanup the context on end of request"""
        context.cleanup()
        return response

    def _handle_exception(self, e):
        """ Handle Protean exceptions and return appropriate response """

        # Get the renderer from the view class
        renderer = perform_import(active_config.DEFAULT_RENDERER)
        if request.url_rule:
            view_func = current_app.view_functions[request.url_rule.endpoint]
            view_class = view_func.view_class
            if issubclass(view_class, APIResource):
                renderer = getattr(view_class, 'renderer', renderer)

        # If user has defined an exception handler then call that
        if self.exception_handler:
            code, data, headers = self.exception_handler(e)

        else:
            code = e.value[0].value
            data = e.value[1]
            headers = {}

        # Build the response and return it
        response = renderer(data, code, headers)
        return response
