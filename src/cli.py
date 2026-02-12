"""
Command-line interface for DocGen
"""

import click
import logging
from pathlib import Path
from config import (
    PROJECT_ROOT, DEFAULT_SLIDES, DEFAULT_TEMPLATE, DEFAULT_TONE
)
from content_generator import ContentGenerator
from template_manager import TemplateManager
from presentation_builder import PresentationBuilder
from orchestrator import PresentationOrchestrator, ContentMapper
from branded_template import BrandedTemplateHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """DocGen: AI-Powered Presentation Generator"""
    pass


@cli.command()
@click.option(
    '--topic',
    prompt='Presentation topic',
    help='Main topic for the presentation'
)
@click.option(
    '--slides',
    type=int,
    default=DEFAULT_SLIDES,
    help=f'Number of slides (default: {DEFAULT_SLIDES})'
)
@click.option(
    '--template',
    type=click.Choice(['corporate']),
    default=DEFAULT_TEMPLATE,
    help=f'Template to use (default: {DEFAULT_TEMPLATE})'
)
@click.option(
    '--audience',
    default=None,
    help='Target audience for presentation'
)
@click.option(
    '--tone',
    type=click.Choice(['professional', 'casual', 'technical']),
    default=DEFAULT_TONE,
    help=f'Tone of presentation (default: {DEFAULT_TONE})'
)
@click.option(
    '--output',
    type=click.Path(),
    default=None,
    help='Output file path (default: output/<topic>.pptx)'
)
def generate(topic, slides, template, audience, tone, output):
    """Generate a presentation from a topic"""
    
    try:
        # Validate input
        if not topic or len(topic.strip()) < 10:
            click.echo(
                click.style(
                    "Error: Topic must be at least 10 characters",
                    fg='red'
                )
            )
            return
        
        if not 3 <= slides <= 20:
            click.echo(
                click.style(
                    f"Error: Slides must be between 3 and 20",
                    fg='red'
                )
            )
            return
        
        click.echo(
            click.style(
                f"🚀 Generating presentation: '{topic}'",
                fg='cyan',
                bold=True
            )
        )
        
        # Initialize components
        content_gen = ContentGenerator()
        template_mgr = TemplateManager(PROJECT_ROOT / "templates")
        content_map = ContentMapper(
            template_mgr.get_template_constraints(template)
        )
        
        # Try to load branded template
        branded_handler = None
        branded_template_path = PROJECT_ROOT / "templates" / "accenture_template.pptx"
        if branded_template_path.exists():
            try:
                click.echo("📐 Using branded Accenture template...")
                branded_handler = BrandedTemplateHandler(branded_template_path)
            except Exception as e:
                logger.warning(f"Could not load branded template: {e}")
        
        # Create orchestrator
        orchestrator = PresentationOrchestrator(
            content_generator=content_gen,
            template_manager=template_mgr,
            presentation_builder=PresentationBuilder,
            content_mapper=content_map,
            branded_template_handler=branded_handler
        )
        
        # Generate presentation
        result_path = orchestrator.generate(
            topic=topic,
            num_slides=slides,
            template_name=template,
            audience=audience,
            tone=tone,
            use_branded_template=branded_handler is not None
        )
        
        click.echo(
            click.style(
                f"\n✅ Presentation generated successfully!",
                fg='green',
                bold=True
            )
        )
        click.echo(f"📁 Saved to: {result_path}")
        
    except Exception as e:
        click.echo(
            click.style(
                f"❌ Error: {str(e)}",
                fg='red',
                bold=True
            )
        )
        logger.exception("Generation failed")
        raise click.ClickException(str(e))


@cli.command()
def templates():
    """List available templates"""
    
    try:
        template_mgr = TemplateManager(PROJECT_ROOT / "templates")
        available = template_mgr.get_available_templates()
        
        if not available:
            click.echo("No templates available")
            return
        
        click.echo("\nAvailable Templates:")
        click.echo("-" * 30)
        for template_name in available:
            config = template_mgr.load_template(template_name)
            description = config.get('template', {}).get('description', 'N/A')
            click.echo(f"  • {template_name}: {description}")
        
        click.echo()
        
    except Exception as e:
        click.echo(
            click.style(
                f"Error: {str(e)}",
                fg='red'
            )
        )


@cli.command()
@click.option(
    '--template',
    type=click.Choice(['corporate']),
    default='corporate'
)
def info(template):
    """Show template information"""
    
    try:
        template_mgr = TemplateManager(PROJECT_ROOT / "templates")
        config = template_mgr.load_template(template)
        
        click.echo(f"\nTemplate: {config['template']['name']}")
        click.echo(f"Description: {config['template']['description']}")
        click.echo(f"\nColor Scheme:")
        for color_name, color_value in config['theme']['colors'].items():
            click.echo(f"  {color_name}: {color_value}")
        
        click.echo(f"\nSlide Layouts:")
        for layout_name in config['slide_layouts'].keys():
            click.echo(f"  • {layout_name}")
        
        click.echo()
        
    except Exception as e:
        click.echo(
            click.style(
                f"Error: {str(e)}",
                fg='red'
            )
        )


if __name__ == '__main__':
    cli()
