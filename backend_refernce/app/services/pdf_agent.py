import os
import base64
import io
from typing import Dict, Any, Optional, List
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import logging

logger = logging.getLogger(__name__)

class PDFAgent:
    def __init__(self):
        """Initialize the PDF Generation Agent"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        logger.info("PDF Agent initialized successfully")

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for professional documents"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=colors.darkblue
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leftIndent=0,
            rightIndent=0
        ))
        
        # Code style
        self.styles.add(ParagraphStyle(
            name='CodeStyle',
            parent=self.styles['Code'],
            fontSize=10,
            spaceAfter=12,
            leftIndent=20,
            rightIndent=20,
            fontName='Courier',
            backgroundColor=colors.lightgrey
        ))

    async def generate_pdf(self, content: str, title: str = "Generated Report", 
                          include_images: List[Dict] = None) -> Dict[str, Any]:
        """
        Generate a PDF document from text content
        
        Args:
            content: Text content to include in PDF
            title: Title of the document
            include_images: List of image data to include (optional)
            
        Returns:
            Dict containing PDF data, metadata, and status
        """
        try:
            # Create PDF in memory
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                                  topMargin=72, bottomMargin=18)
            
            # Build PDF content
            story = []
            
            # Add title
            story.append(Paragraph(title, self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Add generation timestamp
            timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            story.append(Paragraph(f"Generated on {timestamp}", self.styles['CustomSubtitle']))
            story.append(Spacer(1, 30))
            
            # Process content into paragraphs
            paragraphs = self._process_content(content)
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para, self.styles['CustomBody']))
                    story.append(Spacer(1, 12))
            
            # Add images if provided
            if include_images:
                story.append(Spacer(1, 20))
                story.append(Paragraph("Generated Images:", self.styles['CustomSubtitle']))
                story.append(Spacer(1, 12))
                
                for img_data in include_images:
                    try:
                        # Convert base64 image to ReportLab Image
                        img_bytes = base64.b64decode(img_data['image_data'])
                        img_buffer = io.BytesIO(img_bytes)
                        img = RLImage(img_buffer, width=4*inch, height=3*inch)
                        story.append(img)
                        story.append(Spacer(1, 12))
                    except Exception as e:
                        logger.warning(f"Could not add image to PDF: {str(e)}")
                        continue
            
            # Build PDF
            doc.build(story)
            
            # Get PDF data
            pdf_data = buffer.getvalue()
            buffer.close()
            
            # Convert to base64 for frontend
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"generated_report_{timestamp}.pdf"
            
            return {
                "success": True,
                "pdf_data": pdf_base64,
                "filename": filename,
                "title": title,
                "page_count": len(story),
                "generated_at": self._get_timestamp(),
                "file_size": len(pdf_data)
            }
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback": await self._generate_mock_pdf(content, title)
            }

    def _process_content(self, content: str) -> List[str]:
        """Process content into properly formatted paragraphs with structure rules"""
        # Split content into sections
        sections = content.split('\n\n')
        processed = []
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # Check if it's a heading (starts with # or **)
            if section.startswith('#') or section.startswith('**'):
                # Convert markdown-style headings to HTML with proper styling
                if section.startswith('###'):
                    section = f"<b><font color='darkblue'>{section[3:].strip()}</font></b>"
                elif section.startswith('##'):
                    section = f"<b><font color='darkblue' size='14'>{section[2:].strip()}</font></b>"
                elif section.startswith('#'):
                    section = f"<b><font color='darkblue' size='16'>{section[1:].strip()}</font></b>"
                elif section.startswith('**') and section.endswith('**'):
                    section = f"<b><font color='darkblue'>{section[2:-2].strip()}</font></b>"
            
            # Check if it's a list item
            elif section.startswith('- ') or section.startswith('* '):
                # Convert to HTML list with proper formatting
                lines = section.split('\n')
                list_items = []
                for line in lines:
                    if line.strip().startswith(('- ', '* ')):
                        item = line.strip()[2:].strip()
                        list_items.append(f"• {item}")
                section = '<br/>'.join(list_items)
            
            # Check if it's a numbered list
            elif section.startswith(('1. ', '2. ', '3. ', '4. ', '5. ')):
                lines = section.split('\n')
                numbered_items = []
                for line in lines:
                    if line.strip() and line.strip()[0].isdigit() and '. ' in line:
                        item = line.split('. ', 1)[1].strip()
                        numbered_items.append(f"• {item}")
                section = '<br/>'.join(numbered_items)
            
            # Check if it's code (indented or in backticks)
            elif section.startswith('    ') or '```' in section:
                # Format as code with background
                section = f"<font name='Courier' size='10'>{section}</font>"
            
            # Check if it's a data point or statistic
            elif any(keyword in section.lower() for keyword in ['%', 'percent', 'statistics', 'data', 'analysis']):
                # Highlight data points
                section = f"<b>{section}</b>"
            
            processed.append(section)
        
        return processed

    async def _generate_mock_pdf(self, content: str, title: str) -> Dict[str, Any]:
        """Generate a mock PDF response for testing"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"mock_report_{timestamp}.pdf"
        
        try:
            # Generate actual PDF even in mock mode
            pdf_data = await self.generate_pdf(content, title)
            if pdf_data["success"]:
                return {
                    "success": True,
                    "pdf_data": pdf_data["pdf_data"],
                    "filename": filename,
                    "title": title,
                    "generated_at": self._get_timestamp(),
                    "mock_mode": True
                }
        except Exception as e:
            logger.error(f"Error creating mock PDF: {str(e)}")
        
        return {
            "success": True,
            "pdf_data": None,  # Fallback to no PDF
            "filename": filename,
            "title": title,
            "generated_at": self._get_timestamp(),
            "mock_mode": True
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()

    async def get_pdf_info(self, pdf_data: str) -> Dict[str, Any]:
        """Get information about generated PDF"""
        try:
            if not pdf_data:
                return {"error": "No PDF data provided"}
            
            # Decode base64 to get PDF info
            pdf_bytes = base64.b64decode(pdf_data)
            
            return {
                "size_bytes": len(pdf_bytes),
                "format": "PDF",
                "generated_at": self._get_timestamp()
            }
        except Exception as e:
            return {"error": str(e)}

# Global instance
pdf_agent = PDFAgent()
