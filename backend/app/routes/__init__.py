from .auth import auth_ns
from .doctor import doctor_ns

def register_routes(api):
    """
    Registers all namespaces with the RestX API object.
    """
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(doctor_ns, path='/doctors')
