import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

class AIProductivityAnalyzer:
    def __init__(self, db_name: str = "ai_productivity.db"):
        """Sistema de análisis de IA y productividad empresarial"""
        self.db_name = db_name
        self.init_database()
        self.populate_sample_data()
    
    def init_database(self):
        """Crea las tablas del sistema"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Tabla de empleados
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS empleados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    departamento TEXT NOT NULL,
                    cargo TEXT NOT NULL,
                    nivel_seniority TEXT CHECK(nivel_seniority IN ('Junior', 'Mid', 'Senior', 'Lead')),
                    fecha_ingreso DATE,
                    salario_base DECIMAL(10,2),
                    activo BOOLEAN DEFAULT 1
                )
            """)
            
            # Tabla de herramientas IA
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS herramientas_ia (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    proveedor TEXT,
                    costo_mensual DECIMAL(8,2),
                    fecha_implementacion DATE,
                    descripcion TEXT,
                    activa BOOLEAN DEFAULT 1
                )
            """)
            
            # Tabla de uso de herramientas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uso_herramientas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empleado_id INTEGER,
                    herramienta_id INTEGER,
                    fecha_uso DATE,
                    tiempo_uso_minutos INTEGER,
                    tareas_completadas INTEGER DEFAULT 1,
                    tiempo_ahorrado_minutos INTEGER,
                    calidad_output INTEGER CHECK(calidad_output BETWEEN 1 AND 5),
                    notas TEXT,
                    FOREIGN KEY (empleado_id) REFERENCES empleados (id),
                    FOREIGN KEY (herramienta_id) REFERENCES herramientas_ia (id)
                )
            """)
            
            # Tabla de métricas de productividad
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metricas_productividad (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empleado_id INTEGER,
                    fecha DATE,
                    horas_trabajadas DECIMAL(4,2),
                    tareas_completadas INTEGER,
                    calidad_promedio DECIMAL(3,2),
                    uso_ia_tiempo INTEGER DEFAULT 0,
                    satisfaccion_laboral INTEGER CHECK(satisfaccion_laboral BETWEEN 1 AND 5),
                    estres_nivel INTEGER CHECK(estres_nivel BETWEEN 1 AND 5),
                    FOREIGN KEY (empleado_id) REFERENCES empleados (id)
                )
            """)
            
            # Tabla de ROI de IA
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roi_ia (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    departamento TEXT,
                    herramienta_id INTEGER,
                    mes INTEGER,
                    año INTEGER,
                    costo_total DECIMAL(10,2),
                    tiempo_ahorrado_horas DECIMAL(8,2),
                    valor_tiempo_ahorrado DECIMAL(10,2),
                    incremento_calidad_porcentaje DECIMAL(5,2),
                    roi_porcentaje DECIMAL(6,2),
                    FOREIGN KEY (herramienta_id) REFERENCES herramientas_ia (id)
                )
            """)
            
            conn.commit()
    
    def populate_sample_data(self):
        """Llena la base de datos con datos de ejemplo"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Verificar si ya hay datos
            cursor.execute("SELECT COUNT(*) FROM empleados")
            if cursor.fetchone()[0] > 0:
                return
            
            # Empleados de ejemplo
            empleados = [
                ('Ana García', 'Marketing', 'Content Manager', 'Senior', '2022-01-15', 75000),
                ('Carlos López', 'Desarrollo', 'Senior Developer', 'Senior', '2021-06-01', 85000),
                ('María Rodríguez', 'Ventas', 'Sales Representative', 'Mid', '2023-03-10', 55000),
                ('Juan Martínez', 'RRHH', 'HR Specialist', 'Mid', '2022-09-20', 60000),
                ('Laura Fernández', 'Marketing', 'Graphic Designer', 'Junior', '2023-08-15', 45000),
                ('Pedro Sánchez', 'Desarrollo', 'Data Analyst', 'Mid', '2022-11-30', 70000),
                ('Isabel Torres', 'Operaciones', 'Operations Manager', 'Lead', '2020-04-12', 90000),
                ('Roberto Silva', 'Ventas', 'Sales Manager', 'Senior', '2021-02-28', 80000),
            ]
            
            cursor.executemany("""
                INSERT INTO empleados (nombre, departamento, cargo, nivel_seniority, fecha_ingreso, salario_base)
                VALUES (?, ?, ?, ?, ?, ?)
            """, empleados)
            
            # Herramientas IA
            herramientas = [
                ('ChatGPT Plus', 'Generación de Contenido', 'OpenAI', 20, '2023-01-01', 'Asistente IA para escritura y análisis'),
                ('Claude Pro', 'Análisis y Escritura', 'Anthropic', 20, '2023-06-01', 'IA conversacional avanzada'),
                ('GitHub Copilot', 'Programación', 'GitHub', 10, '2023-02-01', 'Asistente de código IA'),
                ('Midjourney', 'Diseño Gráfico', 'Midjourney', 30, '2023-04-01', 'Generación de imágenes IA'),
                ('Jasper', 'Marketing Content', 'Jasper AI', 49, '2023-03-15', 'Creación de contenido marketing'),
                ('Notion AI', 'Productividad', 'Notion', 10, '2023-05-01', 'Asistente de escritura en Notion'),
                ('Grammarly Premium', 'Escritura', 'Grammarly', 12, '2022-12-01', 'Corrección y mejora de textos'),
                ('DataRobot', 'Análisis de Datos', 'DataRobot', 200, '2023-07-01', 'Plataforma AutoML'),
            ]
            
            cursor.executemany("""
                INSERT INTO herramientas_ia (nombre, categoria, proveedor, costo_mensual, fecha_implementacion, descripcion)
                VALUES (?, ?, ?, ?, ?, ?)
            """, herramientas)
            
            conn.commit()
    
    def registrar_uso_ia(self, empleado_id: int, herramienta_id: int, 
                        tiempo_uso: int, tiempo_ahorrado: int, 
                        calidad: int, fecha: str = None) -> bool:
        """Registra el uso de una herramienta IA por un empleado"""
        if fecha is None:
            fecha = datetime.now().strftime('%Y-%m-%d')
        
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO uso_herramientas 
                    (empleado_id, herramienta_id, fecha_uso, tiempo_uso_minutos, 
                     tiempo_ahorrado_minutos, calidad_output)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (empleado_id, herramienta_id, fecha, tiempo_uso, tiempo_ahorrado, calidad))
                conn.commit()
                print(f"✅ Uso de IA registrado exitosamente")
                return True
        except Exception as e:
            print(f"❌ Error al registrar uso: {e}")
            return False
    
    def calcular_roi_departamento(self, departamento: str, mes: int, año: int) -> Dict:
        """Calcula el ROI de IA para un departamento específico"""
        with sqlite3.connect(self.db_name) as conn:
            query = """
                SELECT 
                    h.nombre as herramienta,
                    h.costo_mensual,
                    COUNT(u.id) as usos_totales,
                    AVG(u.tiempo_ahorrado_minutos) as tiempo_promedio_ahorrado,
                    SUM(u.tiempo_ahorrado_minutos) as tiempo_total_ahorrado,
                    AVG(u.calidad_output) as calidad_promedio,
                    AVG(e.salario_base) as salario_promedio
                FROM uso_herramientas u
                JOIN empleados e ON u.empleado_id = e.id
                JOIN herramientas_ia h ON u.herramienta_id = h.id
                WHERE e.departamento = ? 
                AND strftime('%m', u.fecha_uso) = ? 
                AND strftime('%Y', u.fecha_uso) = ?
                GROUP BY h.id, h.nombre, h.costo_mensual
            """
            
            df = pd.read_sql_query(query, conn, params=(departamento, f"{mes:02d}", str(año)))
            
            if df.empty:
                return {"error": "No hay datos para el período especificado"}
            
            # Cálculos de ROI
            resultados = []
            for _, row in df.iterrows():
                costo_hora_empleado = row['salario_promedio'] / (40 * 4)  # 40h/semana, 4 semanas/mes
                valor_tiempo_ahorrado = (row['tiempo_total_ahorrado'] / 60) * costo_hora_empleado
                roi_porcentaje = ((valor_tiempo_ahorrado - row['costo_mensual']) / row['costo_mensual']) * 100
                
                resultados.append({
                    'herramienta': row['herramienta'],
                    'costo_mensual': row['costo_mensual'],
                    'usos_totales': row['usos_totales'],
                    'horas_ahorradas': row['tiempo_total_ahorrado'] / 60,
                    'valor_tiempo_ahorrado': valor_tiempo_ahorrado,
                    'calidad_promedio': row['calidad_promedio'],
                    'roi_porcentaje': roi_porcentaje
                })
            
            return {
                'departamento': departamento,
                'mes': mes,
                'año': año,
                'herramientas': resultados,
                'roi_total': sum(h['roi_porcentaje'] for h in resultados) / len(resultados)
            }
    
    def generar_dashboard_productividad(self, empleado_id: int) -> Dict:
        """Genera métricas de productividad para un empleado"""
        with sqlite3.connect(self.db_name) as conn:
            # Datos básicos del empleado
            empleado_query = """
                SELECT nombre, departamento, cargo, nivel_seniority
                FROM empleados WHERE id = ?
            """
            empleado_info = pd.read_sql_query(empleado_query, conn, params=(empleado_id,))
            
            # Métricas de uso de IA (últimos 30 días)
            fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            uso_query = """
                SELECT 
                    h.nombre as herramienta,
                    COUNT(u.id) as veces_usado,
                    SUM(u.tiempo_uso_minutos) as tiempo_total_uso,
                    SUM(u.tiempo_ahorrado_minutos) as tiempo_total_ahorrado,
                    AVG(u.calidad_output) as calidad_promedio
                FROM uso_herramientas u
                JOIN herramientas_ia h ON u.herramienta_id = h.id
                WHERE u.empleado_id = ? AND u.fecha_uso >= ?
                GROUP BY h.id, h.nombre
                ORDER BY tiempo_total_ahorrado DESC
            """
            
            uso_ia = pd.read_sql_query(uso_query, conn, params=(empleado_id, fecha_inicio))
            
            # Cálculo de impacto
            tiempo_total_ahorrado = uso_ia['tiempo_total_ahorrado'].sum() if not uso_ia.empty else 0
            herramientas_usadas = len(uso_ia) if not uso_ia.empty else 0
            calidad_promedio = uso_ia['calidad_promedio'].mean() if not uso_ia.empty else 0
            
            return {
                'empleado': empleado_info.iloc[0].to_dict() if not empleado_info.empty else {},
                'periodo_analisis': f"Últimos 30 días (desde {fecha_inicio})",
                'metricas_ia': {
                    'herramientas_utilizadas': herramientas_usadas,
                    'tiempo_ahorrado_horas': round(tiempo_total_ahorrado / 60, 2),
                    'calidad_promedio': round(calidad_promedio, 2),
                    'eficiencia_score': min(100, (tiempo_total_ahorrado / 60) * 10)  # Score sobre 100
                },
                'detalle_herramientas': uso_ia.to_dict('records') if not uso_ia.empty else []
            }
    
    def obtener_tendencias_adopcion_ia(self) -> Dict:
        """Analiza las tendencias de adopción de IA en la empresa"""
        with sqlite3.connect(self.db_name) as conn:
            # Adopción por mes
            adopcion_query = """
                SELECT 
                    strftime('%Y-%m', fecha_uso) as mes,
                    COUNT(DISTINCT empleado_id) as usuarios_unicos,
                    COUNT(id) as usos_totales,
                    SUM(tiempo_ahorrado_minutos) as tiempo_ahorrado_total
                FROM uso_herramientas
                WHERE fecha_uso >= date('now', '-6 months')
                GROUP BY strftime('%Y-%m', fecha_uso)
                ORDER BY mes
            """
            
            # Adopción por departamento
            departamento_query = """
                SELECT 
                    e.departamento,
                    COUNT(DISTINCT u.empleado_id) as usuarios_ia,
                    COUNT(DISTINCT e.id) as total_empleados,
                    ROUND(COUNT(DISTINCT u.empleado_id) * 100.0 / COUNT(DISTINCT e.id), 2) as porcentaje_adopcion,
                    SUM(u.tiempo_ahorrado_minutos) as tiempo_ahorrado_total
                FROM empleados e
                LEFT JOIN uso_herramientas u ON e.id = u.empleado_id
                WHERE e.activo = 1
                GROUP BY e.departamento
                ORDER BY porcentaje_adopcion DESC
            """
            
            # Herramientas más populares
            herramientas_query = """
                SELECT 
                    h.nombre,
                    h.categoria,
                    COUNT(DISTINCT u.empleado_id) as usuarios_unicos,
                    COUNT(u.id) as usos_totales,
                    AVG(u.calidad_output) as calidad_promedio
                FROM herramientas_ia h
                JOIN uso_herramientas u ON h.id = u.herramienta_id
                GROUP BY h.id, h.nombre, h.categoria
                ORDER BY usuarios_unicos DESC
            """
            
            adopcion_mensual = pd.read_sql_query(adopcion_query, conn)
            adopcion_departamentos = pd.read_sql_query(departamento_query, conn)
            herramientas_populares = pd.read_sql_query(herramientas_query, conn)
            
            return {
                'adopcion_mensual': adopcion_mensual.to_dict('records'),
                'adopcion_por_departamento': adopcion_departamentos.to_dict('records'),
                'herramientas_mas_usadas': herramientas_populares.to_dict('records'),
                'resumen': {
                    'total_usuarios_ia': adopcion_departamentos['usuarios_ia'].sum(),
                    'total_empleados': adopcion_departamentos['total_empleados'].sum(),
                    'adopcion_global': round((adopcion_departamentos['usuarios_ia'].sum() / 
                                            adopcion_departamentos['total_empleados'].sum()) * 100, 2)
                }
            }
    
    def generar_reporte_ejecutivo(self) -> str:
        """Genera un reporte ejecutivo completo"""
        print("\n" + "="*60)
        print("📊 REPORTE EJECUTIVO - ANÁLISIS DE IA Y PRODUCTIVIDAD")
        print("="*60)
        
        tendencias = self.obtener_tendencias_adopcion_ia()
        
        print(f"\n🎯 RESUMEN EJECUTIVO:")
        print(f"   • Adopción Global de IA: {tendencias['resumen']['adopcion_global']}%")
        print(f"   • Empleados usando IA: {tendencias['resumen']['total_usuarios_ia']}/{tendencias['resumen']['total_empleados']}")
        
        print(f"\n📈 TOP DEPARTAMENTOS (Adopción de IA):")
        for i, dept in enumerate(tendencias['adopcion_por_departamento'][:3], 1):
            print(f"   {i}. {dept['departamento']}: {dept['porcentaje_adopcion']}% "
                  f"({dept['usuarios_ia']}/{dept['total_empleados']} empleados)")
        
        print(f"\n🛠️ HERRAMIENTAS MÁS UTILIZADAS:")
        for i, tool in enumerate(tendencias['herramientas_mas_usadas'][:3], 1):
            print(f"   {i}. {tool['nombre']} ({tool['categoria']})")
            print(f"      Usuarios: {tool['usuarios_unicos']} | Calidad: {tool['calidad_promedio']:.1f}/5")
        
        # ROI por departamento
        print(f"\n💰 ANÁLISIS ROI POR DEPARTAMENTO (Último mes):")
        mes_actual = datetime.now().month
        año_actual = datetime.now().year
        
        departamentos = ['Marketing', 'Desarrollo', 'Ventas']
        for dept in departamentos:
            roi_data = self.calcular_roi_departamento(dept, mes_actual, año_actual)
            if 'roi_total' in roi_data:
                print(f"   • {dept}: ROI {roi_data['roi_total']:.1f}%")
        
        print(f"\n🚀 RECOMENDACIONES:")
        print("   • Expandir capacitación en IA a departamentos con baja adopción")
        print("   • Implementar métricas de productividad más granulares")
        print("   • Considerar herramientas IA especializadas por departamento")
        
        return "Reporte generado exitosamente"

# Función principal para demostrar el sistema
def main():
    """Función principal de demostración"""
    print("🚀 Iniciando Sistema de Análisis de IA y Productividad...")
    
    # Crear instancia del sistema
    sistema = AIProductivityAnalyzer()
    
    # Generar algunos datos de uso de ejemplo
    import random
    from datetime import datetime, timedelta
    
    # Simular uso de IA en los últimos días
    for day in range(30):
        fecha = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
        for _ in range(random.randint(5, 15)):  # 5-15 usos por día
            empleado_id = random.randint(1, 8)
            herramienta_id = random.randint(1, 8)
            tiempo_uso = random.randint(15, 120)  # 15-120 minutos
            tiempo_ahorrado = random.randint(30, 180)  # 30-180 minutos ahorrados
            calidad = random.randint(3, 5)  # Calidad entre 3-5
            
            sistema.registrar_uso_ia(empleado_id, herramienta_id, tiempo_uso, 
                                   tiempo_ahorrado, calidad, fecha)
    
    # Mostrar dashboard de empleado
    print("\n" + "="*50)
    dashboard = sistema.generar_dashboard_productividad(1)
    print(f"📊 DASHBOARD DE PRODUCTIVIDAD - {dashboard['empleado']['nombre']}")
    print(f"Departamento: {dashboard['empleado']['departamento']}")
    print(f"Tiempo ahorrado: {dashboard['metricas_ia']['tiempo_ahorrado_horas']} horas")
    print(f"Score de eficiencia: {dashboard['metricas_ia']['eficiencia_score']}/100")
    
    # Generar reporte ejecutivo
    sistema.generar_reporte_ejecutivo()

if __name__ == "__main__":
    main()
