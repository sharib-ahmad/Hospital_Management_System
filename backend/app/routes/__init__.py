from .auth import auth_ns
from .doctor import doctor_ns
from .application import application_ns
from .department import department_ns
from .nurse import nurse_ns
from .patient import patient_ns
from .appointment import appointment_ns

def register_routes(api):
    """
    Registers all namespaces with the RestX API object.
    """
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(department_ns, path='/departments')
    api.add_namespace(application_ns, path='/applications')
    api.add_namespace(doctor_ns, path='/doctors')
    api.add_namespace(nurse_ns, path='/nurses')
    api.add_namespace(patient_ns, path='/patients')
    api.add_namespace(appointment_ns, path='/appointments')