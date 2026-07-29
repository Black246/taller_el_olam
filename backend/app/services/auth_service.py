# app/services/auth_service.py
from app.extensions import db
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models.usuario import Usuario
from app.services.neon_auth_service import NeonAuthService
from app.core.exceptions import AuthorizationException, ValidationException

class AuthService:
    
    @staticmethod
    def register_user(nombre, email, password, rol='mecanico'):
        """
        Registrar usuario usando Neon Auth + BD local
        
        Args:
            nombre: Nombre completo
            email: Correo electrónico
            password: Contraseña
            rol: Rol del usuario (admin, mecanico)
        
        Returns:
            dict: Token de acceso y datos del usuario
        """
        try:
            # 1. Registrar en Neon Auth
            neon_user = NeonAuthService.sign_up(
                email=email,
                password=password,
                name=nombre,
                metadata={'rol': rol}
            )
            
            # 2. Guardar en tu base de datos local
            user = Usuario(
                nombre=nombre,
                usuario=email.split('@')[0],
                email=email,
                rol=rol,
                activo=True
            )
            user.password = password  # Guarda el hash en tu BD
            db.session.add(user)
            db.session.commit()
            
            # 3. Generar token JWT
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            raise ValidationException(f"Error al registrar usuario: {str(e)}")
    
    @staticmethod
    def login(usuario, password):
        """
        Login con Neon Auth + BD local
        
        Args:
            usuario: Nombre de usuario o email
            password: Contraseña
        
        Returns:
            dict: Token de acceso y datos del usuario
        """
        # 1. Buscar usuario en tu BD local
        user = Usuario.query.filter(
            (Usuario.usuario == usuario) | (Usuario.email == usuario),
            Usuario.activo == True
        ).first()
        
        if not user:
            raise AuthorizationException("Usuario no encontrado")
        
        if not user.check_password(password):
            raise AuthorizationException("Contraseña incorrecta")
        
        # 2. Sincronizar con Neon Auth (login opcional)
        try:
            neon_result = NeonAuthService.sign_in(
                email=user.email,
                password=password
            )
            # El usuario está autenticado en Neon Auth
            print(f"✅ Usuario autenticado en Neon Auth: {neon_result.get('user', {}).get('id')}")
        except Exception as e:
            # Si falla Neon Auth, solo loguear pero permitir login
            print(f"⚠️ Error en Neon Auth: {e}")
        
        # 3. Generar token JWT
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }
    
    @staticmethod
    def obtener_usuario(user_id):
        """Obtener usuario por ID desde BD local"""
        usuario = db.session.get(Usuario, user_id)
        if not usuario:
            raise ValidationException("Usuario no encontrado")
        return usuario
    
    @staticmethod
    def cambiar_rol(user_id, nuevo_rol):
        """Cambiar rol de usuario - solo admin"""
        user = AuthService.obtener_usuario(user_id)
        user.rol = nuevo_rol
        db.session.commit()
        return user.to_dict()