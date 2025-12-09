from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from interfaces.email_interfaces import ITemplateEngine
from pathlib import Path


class Jinja2TemplateEngine(ITemplateEngine):
    """
    Motor de plantillas usando Jinja2
    (Single Responsibility: solo renderiza plantillas)
    """
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Inicializa el motor de plantillas
        
        Args:
            templates_dir: Directorio donde se encuentran las plantillas
        """
        self.templates_dir = Path(templates_dir)
        
        # Crear directorio si no existe
        self.templates_dir.mkdir(exist_ok=True)
        # Configurar Jinja2
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=True,  # Protección contra XSS
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def render(self, template_name: str, context: dict) -> str:
        """
        Renderiza una plantilla con el contexto dado
        
        Args:
            template_name: Nombre del archivo de plantilla (ej: "welcome.html")
            context: Diccionario con datos para la plantilla
            
        Returns:
            str: HTML renderizado
            
        Raises:
            TemplateNotFound: Si la plantilla no existe
        """
        try:
            template = self.env.get_template(template_name)
            print(template_name)
            print(self.templates_dir)
            return template.render(**context)
        except TemplateNotFound:
            raise FileNotFoundError(f"Template '{template_name}' not found in {self.templates_dir}")
    
    def list_templates(self) -> list:
        """Lista todas las plantillas disponibles"""
        return self.env.list_templates()



class SimpleTemplateEngine(ITemplateEngine):
    """
    Motor de plantillas simple usando str.format()
    Útil para plantillas muy básicas sin lógica compleja
    """
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
    
    def render(self, template_name: str, context: dict) -> str:
        """
        Renderiza una plantilla simple usando str.format()
        
        Args:
            template_name: Nombre del archivo de plantilla
            context: Diccionario con datos para la plantilla
            
        Returns:
            str: HTML renderizado
        """
        template_path = self.templates_dir / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template '{template_name}' not found in {self.templates_dir}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        return template_content.format(**context)