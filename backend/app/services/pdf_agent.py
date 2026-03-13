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
        """Initialize the PDF Generation Agent with proper ReportLab styling"""
        self.styles = getSampleStyleSheet()
        self._setup_professional_styles()
        logger.info("PDF Agent initialized with clean styling")

    def _setup_professional_styles(self):
        """Setup professional paragraph styles following ReportLab best practices"""
        
        # Document Title - Only for main document title
        self.styles.add(ParagraphStyle(
            name='DocumentTitle',
            parent=self.styles['Normal'],
            fontSize=16,
            spaceAfter=18,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            leading=20
        ))
        
        # Section Heading - For major sections (bold but not excessive)
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            spaceBefore=14,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            leading=15
        ))
        
        # Subsection Heading - For minor sections (bold but smaller)
        self.styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            spaceBefore=10,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            leading=13
        ))
        
        # Normal Body Text - Main content (NOT bold)
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica',  # Regular Helvetica, NOT bold
            leading=12,
            leftIndent=0,
            rightIndent=0
        ))
        
        # List Item - For bullet points (NOT bold)
        self.styles.add(ParagraphStyle(
            name='ListItem',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica',  # Regular Helvetica, NOT bold
            leading=12,
            leftIndent=15,
            bulletIndent=5
        ))
        
        # Timestamp style
        self.styles.add(ParagraphStyle(
            name='TimestampText',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.grey,
            fontName='Helvetica-Oblique',
            leading=11
        ))

    async def generate_pdf(self, content: str, title: str = "Research Analysis Report", 
                          include_images: List[Dict] = None) -> Dict[str, Any]:
        """
        Generate a clean, professional PDF document
        
        Args:
            content: Text content to include in PDF
            title: Title of the document
            include_images: List of image data to include (optional)
            
        Returns:
            Dict containing PDF data, metadata, and status
        """
        try:
            # Create PDF in memory with A4 page size
            buffer = io.BytesIO()
            
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=0.75 * inch, 
                leftMargin=0.75 * inch, 
                topMargin=0.75 * inch, 
                bottomMargin=0.75 * inch
            )
            
            # Build PDF content
            story = []
            
            # Add document title
            if title and title.strip():
                story.append(Paragraph(title, self.styles['DocumentTitle']))
                story.append(Spacer(1, 12))
            
            # Add generation timestamp
            timestamp = datetime.now().strftime("%B %d, %Y")
            story.append(Paragraph(f"Generated on {timestamp}", self.styles['TimestampText']))
            story.append(Spacer(1, 20))
            
            # Process content into clean paragraphs
            paragraphs = self._process_content_clean(content)
            for para_text, style_name in paragraphs:
                if para_text.strip():
                    story.append(Paragraph(para_text, self.styles[style_name]))
                    # Add appropriate spacing based on content type
                    if style_name in ['SectionHeading', 'SubsectionHeading']:
                        story.append(Spacer(1, 8))
                    else:
                        story.append(Spacer(1, 4))
            
            # Add images if provided
            if include_images:
                story.append(Spacer(1, 20))
                story.append(Paragraph("Generated Images", self.styles['SectionHeading']))
                story.append(Spacer(1, 12))
                
                for img_data in include_images:
                    try:
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
            timestamp_filename = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"research_report_{timestamp_filename}.pdf"
            
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

    def _process_content_clean(self, content: str) -> List[tuple]:
        """
        Process content into clean paragraphs with appropriate styles
        NO HTML tags, NO excessive bold formatting
        """
        sections = content.split('\n\n')
        processed = []
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # Clean the section of markdown formatting first
            clean_section = self._clean_markdown(section)
            
            # Detect content type and assign appropriate style
            if section.startswith('# '):
                # Main heading - use section heading style
                clean_text = clean_section[2:].strip()
                processed.append((clean_text, 'SectionHeading'))
                
            elif section.startswith('## '):
                # Subsection heading
                clean_text = clean_section[3:].strip()
                processed.append((clean_text, 'SubsectionHeading'))
                
            elif section.startswith('### '):
                # Minor heading - treat as subsection
                clean_text = clean_section[4:].strip()
                processed.append((clean_text, 'SubsectionHeading'))
                
            elif section.startswith(('- ', '* ')):
                # List items - process each item separately
                lines = section.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith(('- ', '* ')):
                        clean_text = f"• {self._clean_markdown(line[2:].strip())}"
                        processed.append((clean_text, 'ListItem'))
                        
            elif section.startswith(('1. ', '2. ', '3. ', '4. ', '5. ')):
                # Numbered list - convert to bullets
                lines = section.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and line[0].isdigit() and '. ' in line:
                        clean_text = f"• {self._clean_markdown(line.split('. ', 1)[1].strip())}"
                        processed.append((clean_text, 'ListItem'))
                        
            else:
                # Regular paragraph - use body text style
                if clean_section:
                    processed.append((clean_section, 'CustomBodyText'))
        
        return processed

    def _clean_markdown(self, text: str) -> str:
        """Remove all markdown formatting to get clean text"""
        # Remove bold/italic markers
        text = text.replace('**', '').replace('*', '')
        text = text.replace('__', '').replace('_', '')
        
        # Remove code markers
        text = text.replace('`', '')
        
        # Remove heading markers
        text = text.replace('###', '').replace('##', '').replace('#', '')
        
        # Clean up extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()

    async def _generate_mock_pdf(self, content: str, title: str) -> Dict[str, Any]:
        """Generate a mock PDF response for testing"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"mock_report_{timestamp}.pdf"
        
        try:
            # Try to generate actual PDF even in mock mode
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
            "pdf_data": None,
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
