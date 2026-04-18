from .auth import auth_ns

def register_routes(api):
    """
    Registers all namespaces with the RestX API object.
    """
    api.add_namespace(auth_ns, path='/auth')
