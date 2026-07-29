# app/services/neon_auth_service.py
import requests
import os
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models.usuario import Usuario
from app.extensions import db
from app.core.exceptions import AuthorizationException, ValidationException

class NeonAuthService:
    """Servicio para interactuar con Neon Data API + Auth"""
    
    @classmethod
    def _get_base_url(cls):
        """Obtener URL base de la API de datos"""
        project_id = os.getenv('NEON_PROJECT_ID')
        database_id = os.getenv('NEON_DATABASE_ID')
        return f"https://api.neon.tech/v2/projects/{project_id}/databases/{database_id}"
    
    @classmethod
    def _get_headers(cls):
        """Obtener headers para las peticiones a Neon API"""
        api_key = os.getenv('NEON_API_KEY')
        if not api_key:
            raise ValueError("❌ NEON_API_KEY no configurada en variables de entorno")
        
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    
    @classmethod
    def sign_up(cls, email, password, name=None, metadata=None):
        """
        Registrar un nuevo usuario en Neon Auth
        
        Args:
            email: Correo electrónico del usuario
            password: Contraseña
            name: Nombre del usuario (opcional)
            metadata: Metadatos adicionales como rol (opcional)
        
        Returns:
            dict: Datos del usuario creado
        """
        try:
            # Endpoint de registro en Neon Data API
            url = f"{cls._get_base_url()}/auth/sign-up"
            
            payload = {
                'email': email,
                'password': password,
                'name': name or email.split('@')[0],
                'metadata': metadata or {'rol': 'mecanico'}
            }
            
            response = requests.post(
                url,
                headers=cls._get_headers(),
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                error = response.json()
                raise ValidationException(f"Error en Neon Auth: {error.get('message', 'Error desconocido')}")
                
        except requests.exceptions.RequestException as e:
            raise ValidationException(f"Error de conexión con Neon Auth: {str(e)}")
    
    @classmethod
    def sign_in(cls, email, password):
        """
        Autenticar usuario con Neon Auth
        
        Args:
            email: Correo electrónico
            password: Contraseña
        
        Returns:
            dict: Datos del usuario y sesión
        """
        try:
            url = f"{cls._get_base_url()}/auth/sign-in"
            
            payload = {
                'email': email,
                'password': password
            }
            
            response = requests.post(
                url,
                headers=cls._get_headers(),
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error = response.json()
                raise AuthorizationException(f"Error de autenticación: {error.get('message', 'Credenciales inválidas')}")
                
        except requests.exceptions.RequestException as e:
            raise AuthorizationException(f"Error de conexión con Neon Auth: {str(e)}")
    
    @classmethod
    def get_user(cls, user_id):
        """
        Obtener información de un usuario por ID
        
        Args:
            user_id: ID del usuario en Neon Auth
        
        Returns:
            dict: Datos del usuario
        """
        try:
            url = f"{cls._get_base_url()}/auth/users/{user_id}"
            
            response = requests.get(
                url,
                headers=cls._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error = response.json()
                raise ValidationException(f"Error al obtener usuario: {error.get('message', 'Usuario no encontrado')}")
                
        except requests.exceptions.RequestException as e:
            raise ValidationException(f"Error de conexión con Neon Auth: {str(e)}")
    
    @classmethod
    def query_sql(cls, sql, params=None):
        """
        Ejecutar consulta SQL a través de la Data API
        
        Args:
            sql: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)
        
        Returns:
            dict: Resultados de la consulta
        """
        try:
            url = f"{cls._get_base_url()}/sql"
            
            payload = {
                'sql': sql,
                'params': params or {}
            }
            
            response = requests.post(
                url,
                headers=cls._get_headers(),
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error = response.json()
                raise ValidationException(f"Error al ejecutar SQL: {error.get('message', 'Error desconocido')}")
                
        except requests.exceptions.RequestException as e:
            raise ValidationException(f"Error de conexión con Neon API: {str(e)}")