from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os
from io import BytesIO
from datetime import datetime
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    try:
        # Handle absolute URLs
        if uri.startswith('http://') or uri.startswith('https://'):
            return uri
            
        # Handle data URIs
        if uri.startswith('data:'):
            return uri
            
        # Handle media files
        if uri.startswith(settings.MEDIA_URL):
            path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, '', 1))
            
        # Handle static files
        elif uri.startswith(settings.STATIC_URL):
            path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, '', 1))
            
        # Handle other paths (relative to project root)
        else:
            path = os.path.join(settings.BASE_DIR, uri.lstrip('/'))
        
        # Normalize path and verify existence
        path = os.path.abspath(os.path.normpath(path))
        
        if os.path.exists(path):
            return path
        else:
            logger.warning(f"Resource not found: {uri}")
            return uri  # Fallback to original URI
            
    except Exception as e:
        logger.error(f"Error processing URI {uri}: {str(e)}")
        return uri  # Always return the original URI as fallback

def render_to_pdf(template_src, context_dict=None):
    if context_dict is None:
        context_dict = {}

    try:
        # Step 1: Render template
        template = get_template(template_src)
        html = template.render(context_dict)

        # DEBUG: Print rendered HTML to confirm it's valid
        with open("transcript_debug_output.html", "w", encoding="utf-8") as f:
            f.write(html)

        result = BytesIO()

        # Step 2: Generate PDF
        pdf = pisa.pisaDocument(
            BytesIO(html.encode("UTF-8")),
            dest=result,
            encoding='UTF-8',
            link_callback=link_callback
        )

        if not pdf.err:
            return result.getvalue()
        else:
            raise Exception(f"PDF generation error: {pdf.err}")

    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}", exc_info=True)
        raise Exception(f"Failed to generate PDF: {str(e)}")


def generate_pdf_response(pdf_content, filename_prefix, student):
    """
    Helper to create proper PDF response
    """
    if not pdf_content:
        return HttpResponse("Error: Empty PDF content", status=500)
        
    try:
        filename = f"{slugify(student.name)}_{filename_prefix}_{datetime.now().strftime('%Y%m%d')}.pdf"
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        logger.error(f"Error creating PDF response: {str(e)}")
        return HttpResponse(f"Error creating PDF response: {str(e)}", status=500)

def generate_transcript_pdf(request, student):
    """
    Consolidated PDF generation function with all safety checks
    """
    try:
        # Your existing data preparation code here
        # ...
        
        context = {
            'student': student,
            # ... other context data
        }
        
        pdf_content = render_to_pdf('students/transcript_template.html', context)
        return generate_pdf_response(pdf_content, "transcript", student)
        
    except Exception as e:
        logger.error(f"Transcript generation failed: {str(e)}")
        return HttpResponse(f"Error generating transcript: {str(e)}", status=500)


# utils.py
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points in kilometers using Haversine formula
    """
    R = 6371  # Earth radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2) * math.sin(dlat/2)+ 
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
        math.sin(dlon/2) * math.sin(dlon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c