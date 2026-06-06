# dian_fe.py
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import hashlib
import os

class FacturaElectronicaDIAN:
    """Generador de factura electrónica según resolución DIAN 000165 de 2023"""
    
    def __init__(self):
        self.software_id = "TallerElOlam"
        self.software_pin = "123456"  # Cambiar por el PIN real
        self.nit_emisor = "1065619550"
        self.dv_emisor = "5"
        self.razon_social_emisor = "MOTOTALLER EL OLAM"
        self.nombre_comercial = "MOTOTALLER EL OLAM"
        
    def generar_factura(self, factura, detalles, productos):
        """
        Genera el XML de factura electrónica
        """
        # Crear raíz del documento
        root = ET.Element("Invoice", {
            "xmlns": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
            "xmlns:cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "xmlns:cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "xmlns:ds": "http://www.w3.org/2000/09/xmldsig#",
            "xmlns:ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            "xmlns:sts": "http://www.dian.gov.co/contratos/facturaelectronica/v1/Structures"
        })
        
        # ============ EXTENSIONES ============
        extensions = ET.SubElement(root, "ext:UBLExtensions")
        extension = ET.SubElement(extensions, "ext:UBLExtension")
        
        # Información del software de facturación
        content = ET.SubElement(extension, "ext:ExtensionContent")
        software_info = ET.SubElement(content, "sts:SoftwareProvider")
        ET.SubElement(software_info, "sts:SoftwareID").text = self.software_id
        ET.SubElement(software_info, "sts:SoftwarePin").text = self.software_pin
        
        # ============ INFORMACIÓN GENERAL ============
        ET.SubElement(root, "cbc:ProfileID").text = "DIAN 2.1"
        ET.SubElement(root, "cbc:ID").text = factura.folio
        ET.SubElement(root, "cbc:UUID").text = f"{factura.id}-{datetime.now().timestamp()}"
        ET.SubElement(root, "cbc:IssueDate").text = factura.fecha.strftime('%Y-%m-%d')
        ET.SubElement(root, "cbc:IssueTime").text = factura.fecha.strftime('%H:%M:%S-05:00')
        
        # Tipo de documento (1 = Factura de venta)
        ET.SubElement(root, "cbc:InvoiceTypeCode").text = "1"
        ET.SubElement(root, "cbc:DocumentCurrencyCode").text = "COP"
        
        # ============ EMISOR ============
        accounting_supplier = ET.SubElement(root, "cac:AccountingSupplierParty")
        party = ET.SubElement(accounting_supplier, "cac:Party")
        
        # Identificación del emisor
        party_id = ET.SubElement(party, "cac:PartyIdentification")
        ET.SubElement(party_id, "cbc:ID", {"schemeID": "31", "schemeName": "NIT"}).text = f"{self.nit_emisor}{self.dv_emisor}"
        
        # Nombre del emisor
        party_name = ET.SubElement(party, "cac:PartyName")
        ET.SubElement(party_name, "cbc:Name").text = self.razon_social_emisor
        
        # Dirección del emisor
        postal_address = ET.SubElement(party, "cac:PostalAddress")
        ET.SubElement(postal_address, "cbc:CountrySubentity").text = "Cesar"
        ET.SubElement(postal_address, "cbc:CityName").text = "Valledupar"
        ET.SubElement(postal_address, "cbc:AddressLine").text = "CR 26 13 52 BRR ENEAL"
        
        # Régimen tributario (No responsable de IVA - código 49)
        tax_scheme = ET.SubElement(party, "cac:PartyTaxScheme")
        ET.SubElement(tax_scheme, "cbc:RegistrationName").text = self.razon_social_emisor
        ET.SubElement(tax_scheme, "cbc:CompanyID").text = f"{self.nit_emisor}{self.dv_emisor}"
        tax_scheme_id = ET.SubElement(tax_scheme, "cac:TaxScheme")
        ET.SubElement(tax_scheme_id, "cbc:ID").text = "49"  # No responsable de IVA
        
        # Contacto
        contact = ET.SubElement(party, "cac:Contact")
        ET.SubElement(contact, "cbc:ElectronicMail").text = "matecari10@hotmail.com"
        ET.SubElement(contact, "cbc:Telephone").text = "3154541158"
        
        # ============ CLIENTE (ADQUIRIENTE) ============
        accounting_customer = ET.SubElement(root, "cac:AccountingCustomerParty")
        customer_party = ET.SubElement(accounting_customer, "cac:Party")
        
        # Identificación del cliente
        customer_id = ET.SubElement(customer_party, "cac:PartyIdentification")
        
        if factura.cliente_documento and factura.cliente_documento != "222222222222":
            # Cliente con NIT o CC
            doc_type = "31" if len(factura.cliente_documento) == 10 else "13"  # 31=NIT, 13=CC
            ET.SubElement(customer_id, "cbc:ID", {"schemeID": doc_type}).text = factura.cliente_documento
        else:
            # Consumidor final
            ET.SubElement(customer_id, "cbc:ID", {"schemeID": "31"}).text = "222222222222"
        
        # Nombre del cliente
        customer_name = ET.SubElement(customer_party, "cac:PartyName")
        ET.SubElement(customer_name, "cbc:Name").text = factura.cliente_nombre
        
        # ============ LÍNEAS DE FACTURA (PRODUCTOS) ============
        invoice_lines = ET.SubElement(root, "cac:InvoiceLine")
        
        for idx, detalle in enumerate(detalles, 1):
            inv_line = ET.SubElement(invoice_lines if idx == 1 else root, "cac:InvoiceLine")
            ET.SubElement(inv_line, "cbc:ID").text = str(idx)
            ET.SubElement(inv_line, "cbc:InvoicedQuantity", {"unitCode": "u"}).text = str(detalle.cantidad)
            ET.SubElement(inv_line, "cbc:LineExtensionAmount").text = f"{detalle.subtotal:.2f}"
            
            # Producto
            item = ET.SubElement(inv_line, "cac:Item")
            ET.SubElement(item, "cbc:Description").text = detalle.producto.nombre
            
            # Precio
            price = ET.SubElement(inv_line, "cac:Price")
            ET.SubElement(price, "cbc:PriceAmount").text = f"{detalle.precio_unitario:.2f}"
        
        # ============ TOTALES ============
        legal_monetary = ET.SubElement(root, "cac:LegalMonetaryTotal")
        ET.SubElement(legal_monetary, "cbc:LineExtensionAmount").text = f"{factura.subtotal:.2f}"
        ET.SubElement(legal_monetary, "cbc:TaxExclusiveAmount").text = f"{factura.subtotal:.2f}"
        ET.SubElement(legal_monetary, "cbc:TaxInclusiveAmount").text = f"{factura.total:.2f}"
        ET.SubElement(legal_monetary, "cbc:PayableAmount").text = f"{factura.total:.2f}"
        
        # ============ IMPUESTOS ============
        tax_total = ET.SubElement(root, "cac:TaxTotal")
        ET.SubElement(tax_total, "cbc:TaxAmount").text = f"{factura.iva:.2f}"
        
        subtotal_tax = ET.SubElement(tax_total, "cac:TaxSubtotal")
        ET.SubElement(subtotal_tax, "cbc:TaxAmount").text = f"{factura.iva:.2f}"
        
        tax_category = ET.SubElement(subtotal_tax, "cac:TaxCategory")
        tax_scheme_tax = ET.SubElement(tax_category, "cac:TaxScheme")
        
        # Para No responsable de IVA, código 49
        if factura.iva == 0:
            ET.SubElement(tax_scheme_tax, "cbc:ID").text = "49"
            ET.SubElement(tax_category, "cbc:Percent").text = "0"
        else:
            ET.SubElement(tax_scheme_tax, "cbc:ID").text = "1"  # IVA
            ET.SubElement(tax_category, "cbc:Percent").text = "19"
        
        # ============ GENERAR XML ============
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        return xml_str
    
    def guardar_xml(self, factura_id, xml_content):
        """Guarda el XML en la carpeta de facturas electrónicas"""
        os.makedirs('facturas_electronicas', exist_ok=True)
        filename = f'facturas_electronicas/fe_{factura_id}.xml'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        return filename