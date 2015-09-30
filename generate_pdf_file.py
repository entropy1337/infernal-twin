from reportlab.platypus import PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle,Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import datetime
 

styles = getSampleStyleSheet()
i = datetime.datetime.now()
filename=i.isoformat()

doc = SimpleDocTemplate(str(filename)+".pdf", pagesize=letter)
parts = []



class create_pdf:
	
	
		
	def add_pdf_text(self, finding_name, phase, findings, risk_level, category_level, PoC_notes):
		
		
		
		
		data = [
		    [Paragraph(finding_name, styles["Normal"]), Paragraph(phase, styles["Normal"])],
		    [Paragraph(findings, styles["Normal"]), Paragraph('Risk Level', styles["Normal"]), Paragraph('Category', styles["Normal"])],
		    [Paragraph('Proof of Concept', styles["Normal"]), Paragraph(risk_level, styles["Normal"]), Paragraph(category_level, styles["Normal"])],
		    [Paragraph(PoC_notes, styles["Normal"])],
		    [Paragraph('======================================================================================================================', styles["Normal"])],
		    ]
		
		
		
		
		
		table = Table(data, [3 * inch, 1.5 * inch, inch])
		table_with_style = Table(data, [5 * inch, 1.5 * inch, inch])
		table_with_style.setStyle(TableStyle([
		    ('FONT', (0, 0), (-1, -1), 'Helvetica'),
		    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
		    ('FONT', (0, 0), (-1, 1), 'Helvetica-Bold'),
		    ('FONTSIZE', (0, 0), (-1, -1), 8),
		    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
		    ('BOX', (0, 0), (-1, 0), 0.25, colors.green),
		    ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
		]))
		#~ parts.append(table)
		Story = Spacer(1, 0.5 * inch)
		
		parts.append(Story)
		
		parts.append(table_with_style)
	
	
	#~ add_pdf_text('1','1','1','1','1','1')
	
	def create_final(self):
		doc.build(parts)
	

