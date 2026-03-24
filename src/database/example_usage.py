"""
EJEMPLO DE USO: Conexión y Subida de Datos
==========================================

Este archivo muestra cómo utilizar los módulos de DatabaseConnection,
FileUploader y ReportUploader para subir datos a PostgreSQL.

NOTA: Este es un archivo de referencia/ejemplo. No debe ejecutarse directamente
hasta que la base de datos esté configurada correctamente.
"""

from src.database.connection import DatabaseConnection
from src.database.uploads import FileUploader, ReportUploader
from datetime import datetime, timezone


# ==========================================
# 1. CONECTAR A LA BASE DE DATOS
# ==========================================
def example_basic_connection():
    """Ejemplo básico de conexión."""
    db = DatabaseConnection()
    
    # Conectar
    if db.connect():
        print("✓ Conexión exitosa")
    else:
        print("✗ Error de conexión")
        return
    
    # ... hacer operaciones ...
    
    # Desconectar
    db.disconnect()


# ==========================================
# 2. INSERTAR UN ARCHIVO (FILE)
# ==========================================
def example_insert_file():
    """Ejemplo de inserción de un archivo."""
    db = DatabaseConnection()
    db.connect()
    
    file_uploader = FileUploader(db)
    
    # Datos de un archivo
    file_data = {
        "id_file": 1,
        "id_source": 101,
        "name": "Reporte Mensual",
        "code": "RM-2024-03",
        "main_url": "https://example.com/files/report.pdf",
        "path": "/data/reports/2024/report.pdf",
        "type": "PDF",
        "specific_url": "https://example.com/specific/report",
        "alternate_url": "https://backup.example.com/report.pdf",
        "navigation_path": "/documentos/reportes/mensual",
        "publication_frequency": "Mensual",
        "priority": 1,
        "state": "Activo",
        "creation_date": datetime.now(timezone.utc),
        "update_date": datetime.now(timezone.utc),
        "observations": "Reporte de datos procesados",
        "updated_to": "2024-03-20",
        "last_file_path": "/data/reports/2024/report_v2.pdf",
        "last_file_url": "https://example.com/files/report_v2.pdf",
        "schedule_interval": "0 0 1 * *",  # Cron: primer día del mes
        "publication_date": "2024-03-20",
        "key_words": "finanzas, reportes, mensual",
        "section_path": "/reportes/finanzas",
        "short_name": "RM",
        "download_type": "direct"
    }
    
    # Insertar
    file_id = file_uploader.insert_file(file_data)
    if file_id:
        print(f"✓ Archivo insertado con ID: {file_id}")
    else:
        print("✗ Error al insertar archivo")
    
    db.disconnect()


# ==========================================
# 3. ACTUALIZAR UN ARCHIVO
# ==========================================
def example_update_file():
    """Ejemplo de actualización de un archivo."""
    db = DatabaseConnection()
    db.connect()
    
    file_uploader = FileUploader(db)
    
    # Datos a actualizar
    update_data = {
        "state": "Inactivo",
        "update_date": datetime.now(timezone.utc),
        "observations": "Archivo descontinuado"
    }
    
    # Actualizar archivo con ID 1
    success = file_uploader.update_file(file_id=1, file_data=update_data)
    if success:
        print("✓ Archivo actualizado correctamente")
    else:
        print("✗ Error al actualizar archivo")
    
    db.disconnect()


# ==========================================
# 4. UPSERT DE ARCHIVO (INSERT o UPDATE)
# ==========================================
def example_upsert_file():
    """Ejemplo de upsert (INSERT ... ON CONFLICT UPDATE)."""
    db = DatabaseConnection()
    db.connect()
    
    file_uploader = FileUploader(db)
    
    file_data = {
        "id_file": 5,
        "id_source": 105,
        "name": "Reporte Trimestral",
        "code": "RT-2024-Q1",
        "main_url": "https://example.com/tri/report.pdf",
        "path": "/data/reports/2024/trimestral.pdf",
        "type": "PDF",
        "publication_frequency": "Trimestral",
        "priority": 2,
        "state": "Activo",
        "creation_date": datetime.now(timezone.utc),
        "update_date": datetime.now(timezone.utc),
    }
    
    # Especificar qué campos actualizar si ya existe
    update_fields = ["name", "update_date", "state"]
    
    result = file_uploader.upsert_file(file_data, update_fields=update_fields)
    if result:
        print(f"✓ Archivo upsertado con ID: {result}")
    else:
        print("✗ Error en upsert")
    
    db.disconnect()


# ==========================================
# 5. INSERTAR UN REPORTE (REPORT)
# ==========================================
def example_insert_report():
    """Ejemplo de inserción de un reporte."""
    db = DatabaseConnection()
    db.connect()
    
    report_uploader = ReportUploader(db)
    
    report_data = {
        "id_report": 1,
        "id_file": 1,  # Referencia al archivo
        "name": "Resumen Ejecutivo",
        "publication_data": "Datos de publicación",
        "publication_frequency": "Mensual",
        "creation_date": datetime.now(timezone.utc),
        "update_date": datetime.now(timezone.utc),
        "observations": "Reporte generado automáticamente",
        "code": "RE-2024-03",
        "path": "/data/reports/resumen.xlsx",
        "converted_report_path": "/data/reports/resumen_converted.csv",
        "converted_to": datetime.now(timezone.utc),
        "key_words": "ejecutivo, resumen, finanzas",
        "type": "XLSX",
        "isActive": True,
        "storage_table": "reports_2024",
        "file_extension": "xlsx",
        "replacement_table": "reports_archive",
        "compare_dates": False,
        "page_number": 1,
        "decimal_separator": ",",
        "conversion_factor": 1,
        "migrated_to": datetime.now(timezone.utc),
        "load_scope": "complete",
        "text_normalization": True
    }
    
    # Insertar
    report_id = report_uploader.insert_report(report_data)
    if report_id:
        print(f"✓ Reporte insertado con ID: {report_id}")
    else:
        print("✗ Error al insertar reporte")
    
    db.disconnect()


# ==========================================
# 6. ACTUALIZAR UN REPORTE
# ==========================================
def example_update_report():
    """Ejemplo de actualización de un reporte."""
    db = DatabaseConnection()
    db.connect()
    
    report_uploader = ReportUploader(db)
    
    update_data = {
        "isActive": False,
        "update_date": datetime.now(timezone.utc),
        "observations": "Reporte finalizado"
    }
    
    success = report_uploader.update_report(report_id=1, report_data=update_data)
    if success:
        print("✓ Reporte actualizado correctamente")
    else:
        print("✗ Error al actualizar reporte")
    
    db.disconnect()


# ==========================================
# 7. BATCH INSERT DE ARCHIVOS
# ==========================================
def example_batch_insert_files():
    """Ejemplo de inserción en batch de múltiples archivos."""
    db = DatabaseConnection()
    db.connect()
    
    file_uploader = FileUploader(db)
    
    # Lista de múltiples archivos
    files_list = [
        {
            "id_file": 10,
            "id_source": 110,
            "name": "Archivo 1",
            "code": "A1",
            "main_url": "https://example.com/a1.pdf",
            "path": "/data/a1.pdf",
            "type": "PDF",
            "priority": 1,
            "state": "Activo",
            "creation_date": datetime.now(timezone.utc),
            "update_date": datetime.now(timezone.utc),
        },
        {
            "id_file": 11,
            "id_source": 111,
            "name": "Archivo 2",
            "code": "A2",
            "main_url": "https://example.com/a2.pdf",
            "path": "/data/a2.pdf",
            "type": "PDF",
            "priority": 2,
            "state": "Activo",
            "creation_date": datetime.now(timezone.utc),
            "update_date": datetime.now(timezone.utc),
        },
    ]
    
    successful, failed = file_uploader.batch_insert_files(files_list)
    print(f"✓ Insertados: {successful}, ✗ Fallidos: {failed}")
    
    db.disconnect()


# ==========================================
# 8. BATCH INSERT DE REPORTES
# ==========================================
def example_batch_insert_reports():
    """Ejemplo de inserción en batch de múltiples reportes."""
    db = DatabaseConnection()
    db.connect()
    
    report_uploader = ReportUploader(db)
    
    reports_list = [
        {
            "id_report": 10,
            "id_file": 10,
            "name": "Reporte Archivo 1",
            "code": "RA1",
            "path": "/data/reporte1.xlsx",
            "type": "XLSX",
            "isActive": True,
            "creation_date": datetime.now(timezone.utc),
            "update_date": datetime.now(timezone.utc),
        },
        {
            "id_report": 11,
            "id_file": 11,
            "name": "Reporte Archivo 2",
            "code": "RA2",
            "path": "/data/reporte2.xlsx",
            "type": "XLSX",
            "isActive": True,
            "creation_date": datetime.now(timezone.utc),
            "update_date": datetime.now(timezone.utc),
        },
    ]
    
    successful, failed = report_uploader.batch_insert_reports(reports_list)
    print(f"✓ Insertados: {successful}, ✗ Fallidos: {failed}")
    
    db.disconnect()


# ==========================================
# 9. QUERIES PERSONALIZADAS
# ==========================================
def example_custom_queries():
    """Ejemplo de queries personalizadas usando fetch_one y fetch_all."""
    db = DatabaseConnection()
    db.connect()
    
    # Obtener un archivo específico
    query = "SELECT * FROM file WHERE id_file = %s;"
    result = db.fetch_one(query, (1,))
    if result:
        print(f"✓ Archivo encontrado: {result}")
    
    # Obtener todos los archivos activos
    query = "SELECT id_file, name, state FROM file WHERE state = %s;"
    results = db.fetch_all(query, ("Activo",))
    print(f"✓ Archivos activos: {len(results)}")
    for file in results:
        print(f"  - {file['name']} ({file['id_file']})")
    
    db.disconnect()


if __name__ == "__main__":
    # Ejecutar ejemplos
    print("EJEMPLOS DE USO - DATABASE")
    print("=" * 50)
    
    # Descomentar el ejemplo que desees probar
    # example_basic_connection()
    # example_insert_file()
    # example_update_file()
    # example_upsert_file()
    # example_insert_report()
    # example_update_report()
    # example_batch_insert_files()
    # example_batch_insert_reports()
    # example_custom_queries()
