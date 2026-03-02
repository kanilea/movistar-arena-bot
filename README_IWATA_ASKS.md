# Iwata Asks Complete Archive Scraper

Script para descargar y archivar todas las entrevistas de Iwata Asks del sitio oficial de Nintendo.

## 📋 Qué hace este script

- ✅ Extrae automáticamente todas las entrevistas de [iwataasks.nintendo.com](https://iwataasks.nintendo.com/)
- ✅ Descarga todas las imágenes de las entrevistas
- ✅ Genera un documento Markdown completo
- ✅ Genera un documento HTML con estilos
- ✅ Guarda los datos brutos en JSON
- ✅ Organiza todo en carpetas ordenadas

## 🚀 Instalación

### 1. Instalar Python
Asegúrate de tener Python 3.6+ instalado:
```bash
python --version
```

### 2. Instalar dependencias
```bash
pip install requests beautifulsoup4 markdown
```

O si tienes pip3:
```bash
pip3 install requests beautifulsoup4 markdown
```

## 🏃‍♂️ Cómo usarlo

### Opción 1: Ejecutar directamente
```bash
python iwata_asks_scraper.py
```

### Opción 2: Si usas Python 3
```bash
python3 iwata_asks_scraper.py
```

## 📁 Estructura de salida
Al ejecutarse, creará la siguiente estructura:
```
iwata_asks_archive/
├── images/                    # Todas las imágenes descargadas
├── Iwata_Asks_Complete_Archive.md    # Documento Markdown
├── Iwata_Asks_Complete_Archive.html   # Documento HTML
└── interviews_data.json       # Datos brutos en JSON
```

## ⏱️ Tiempo de ejecución
- **Duración estimada:** 10-30 minutos (depende de la cantidad de entrevistas)
- **Pausas automáticas:** 1 segundo entre peticiones para ser respetuoso con el servidor

## 📌 Características principales

### Documento Markdown
- Título y metadata completa
- Todas las entrevistas numeradas
- Enlaces a las fuentes originales
- Imágenes con texto alternativo
- Contenido formateado y legible

### Documento HTML
- Diseño limpio y responsivo
- Estilos CSS incluidos
- Imágenes optimizadas
- Navegación fácil entre entrevistas
- Colores temáticos de Nintendo

### Datos JSON
- Estructura completa de cada entrevista
- URLs de imágenes
- Metadatos de extracción
- Ideal para análisis o procesamiento adicional

## 🔧 Personalización

### Cambiar carpetas
Edita estas líneas en el script:
```python
self.base_url = "https://iwataasks.nintendo.com"
self.output_dir = "iwata_asks_archive"
```

### Modificar estilos HTML
Edita el CSS dentro del método `generate_html_document()`.

### Ajustar tiempos de espera
Modifica esta línea:
```python
time.sleep(1)  # Cambia el número de segundos
```

## 🚨 Notas importantes

- **Uso responsable**: El script incluye pausas automáticas para no sobrecargar el servidor de Nintendo
- **Conexión necesaria**: Requiere conexión a internet estable
- **Contenido público**: Todo el contenido es de acceso público y propiedad de Nintendo
- **Backup recomendado**: Guarda una copia del archivo generado

## 📊 Resultado esperado

Al completar, tendrás:
- **Documento completo** con todas las entrevistas de Satoru Iwata
- **Imágenes locales** para visualización offline
- **Múltiples formatos** (Markdown, HTML, JSON)
- **Archivo permanente** de este contenido valioso

## 🐛 Solución de problemas

### Error de conexión
- Verifica tu conexión a internet
- Intenta ejecutarlo más tarde (servidor temporalmente no disponible)

### Imagen no descarga
- Algunas imágenes pueden tener protección
- Losplaceholders se mantienen en el documento

### Problemas de encoding
- El script usa encoding UTF-8 para caracteres especiales
- Si tienes problemas, intenta abrir el archivo con un editor que soporte UTF-8

## 📜 Acerca de Iwata Asks

**Iwata Asks** fue una serie de entrevistas realizadas por el fallecido presidente de Nintendo, Satoru Iwata, donde hablaba con los desarrolladores sobre el proceso creativo detrás de los juegos y hardware de Nintendo.

**Plataformas cubiertas:**
- Wii U
- Nintendo 3DS
- Wii
- Nintendo DS

**Tipos de contenido:**
- Entrevistas de desarrollo
- Detrás de cámaras
- Conceptos de diseño
- Historias de desarrollo

---

**Creado para preservación digital del contenido de Nintendo**  
*Este contenido es propiedad de Nintendo y se distribuye con fines de archivo.*