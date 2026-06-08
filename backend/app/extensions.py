from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_caching import Cache
from celery import Celery
from flask_socketio import SocketIO
import logging

db = SQLAlchemy()
jwt = JWTManager()
celery = Celery()
celery.set_default() 
cache = Cache()
socketio = SocketIO(cors_allowed_origins="*", manage_session=False)
logger = logging.getLogger(__name__)

api = Api(version='1.0.0',
        title='🏥 Enterprise Hospital Management System (HMS) Core API',
        description='''### Enterprise-Grade Operational Engine & Clinical Integration Layer

Welcome to the official developer and integrator documentation for the Hospital Management System (HMS) Core API. This service layer operates as the central coordination system, orchestrating clinical databases, scheduling registries, identity management, and inventory logistics under strict transactional controls.

---

### 🛡️ Regulatory Compliance & Data Security (HIPAA & PHI)
This API is engineered to align with **HIPAA (Health Insurance Portability and Accountability Act)** security standards. All endpoints handling Protected Health Information (PHI) implement stringent access constraints and auditing controls:
* **Role-Based Access Control (RBAC):** Cryptographically signed JSON Web Tokens (JWT) enforce discrete permission tiers across Administrative, Clinical (Physicians/Nurses), and Patient roles.
* **Clinical Data Isolation:** Strict query boundaries prevent unauthorized exposure of diagnoses, clinical records, and vital stats.
* **Audit Trails:** Transaction logs capture access, updates, and creation of medical records to ensure complete transparency.

---

### 📋 API Subsystems & Capabilities

#### 1. Identity & Access Management (IAM)
* **Authentication:** Secure cookie-based and header-based authentication with cryptographically secure password reset verification pipelines.
* **Onboarding & Licensing:** Multi-stage application processing for healthcare practitioners (Doctors/Nurses) including credential review and state license verification.

#### 2. Clinical Data Systems (CDS)
* **Medical Records:** Standardized record registry tracking clinical diagnoses, doctor treatment prescriptions, and historical consult logs.
* **Patient Vitals Registry:** Real-time nursing observation logs capturing critical parameters (Systolic/Diastolic Blood Pressure, Blood Sugar levels, Pulse Rate, Temperature, and Respiration Rate).

#### 3. Scheduling & Care Registry
* **Temporal Alignment:** All appointment structures, observation timelines, and clinician shift logs are strictly serialized and evaluated under the **Asia/Kolkata (India Standard Time - IST)** zone to guarantee scheduling integrity.
* **Resource Optimization:** Automated validation checks prevent scheduling conflicts, overlapping clinical shifts, or past-date consultations.

#### 4. Pharmacy Inventory & Order Logistics
* **Formulary Controls:** Active catalog management for pharmaceuticals, complete with category tags, stock levels, and safety thresholds.
* **Order Processing:** State-driven fulfillment workflow for medical orders and prescription distribution.

---

### 🔑 Authentication Guide
To interface with protected endpoints via this documentation console:
1. Obtain an authorization token via `/auth/login`.
2. Click the **Authorize** lock button in the upper right.
3. Input your token in the Value field exactly as: `Bearer <your_jwt_token>`.
4. Click **Authorize** to bind the headers to all subsequent requests.

*Note: In web client environments, session state is managed via secure, HttpOnly, SameSite cookies to protect against Cross-Site Scripting (XSS).*''',
        authorizations={
            'Bearer Auth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': "Input your JWT token in the format: Bearer <your_token_here>"
            }
        },
        security='Bearer Auth',
        contact='api-integrations@mediflow.hms.org',
        contact_email='api-integrations@mediflow.hms.org',
        license='Proprietary (All Rights Reserved)',
        doc='/docs')