class DianService:

    @staticmethod
    def generar_xml(factura):

        return {
            "success": True,
            "factura": factura.id
        }

    @staticmethod
    def enviar_dian(xml):

        return {
            "success": True,
            "message": (
                "Documento enviado "
                "correctamente"
            )
        }