# app/models/usuario.py - VERSIÓN ACTUALIZADA
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 🔑 ID de Neon Auth para sincronización
    neon_auth_id = db.Column(db.String(50), unique=True, nullable=True)
    
    nombre = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default="mecanico")
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    movimientos = db.relationship("Movimiento", backref="usuario", lazy=True)
    facturas = db.relationship("Factura", backref="usuario", lazy=True)
    
    @property
    def password(self):
        raise AttributeError("Password is write-only")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "usuario": self.usuario,
            "email": self.email,
            "rol": self.rol,
            "activo": self.activo,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
    
    @classmethod
    def sync_from_neon(cls, neon_user):
        """Sincroniza o crea usuario desde Neon Auth"""
        user = cls.query.filter_by(neon_auth_id=neon_user.id).first()
        if not user:
            # Buscar por email como fallback
            user = cls.query.filter_by(email=neon_user.email).first()
        
        if not user:
            # Crear nuevo usuario
            user = cls(
                neon_auth_id=neon_user.id,
                nombre=neon_user.name or neon_user.email.split('@')[0],
                usuario=neon_user.email.split('@')[0],
                email=neon_user.email,
                rol=neon_user.metadata.get('rol', 'mecanico') if neon_user.metadata else 'mecanico',
                activo=not neon_user.banned if hasattr(neon_user, 'banned') else True
            )
            db.session.add(user)
            db.session.commit()
        else:
            # Actualizar información
            if user.neon_auth_id is None:
                user.neon_auth_id = neon_user.id
            if user.email != neon_user.email:
                user.email = neon_user.email
            db.session.commit()
        
        return user
    
    def __repr__(self):
        return f"<Usuario {self.usuario}>"