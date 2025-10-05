from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from api.models import Medicine, MedicineGroup, Supplier, Client, Sale

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_dashboard_report(request):
    # Créer la réponse HTTP avec le type PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rapport_dashboard_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'

    # Créer le document PDF
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Style personnalisé pour le titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=1
    )

    # Titre
    title = Paragraph("Rapport du Tableau de bord - Pharmacie Fadj-Ma", title_style)
    elements.append(title)

    # Date
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray,
        alignment=1
    )
    date_text = Paragraph(f"Généré le {timezone.now().strftime('%d/%m/%Y à %H:%M')}", date_style)
    elements.append(date_text)
    elements.append(Spacer(1, 1*cm))

    # Récupérer les données
    medicines = Medicine.objects.all()
    groups = MedicineGroup.objects.all()
    suppliers = Supplier.objects.all()
    clients = Client.objects.all()
    sales = Sale.objects.all()

    # Calculer les statistiques
    medicines_count = medicines.count()
    low_stock_count = medicines.filter(stock_quantity__lte=F('min_stock_alert')).count()
    medicines_available = medicines.filter(stock_quantity__gt=0).count()
    groups_count = groups.count()
    suppliers_count = suppliers.count()
    clients_count = clients.count()

    total_revenue = sum(sale.total_amount for sale in sales)
    total_quantity_sold = sum(
        item.quantity
        for sale in sales
        for item in sale.items.all()
    )

    # Section 1: Statistiques générales
    section_title = Paragraph("<b>Statistiques Générales</b>", styles['Heading2'])
    elements.append(section_title)
    elements.append(Spacer(1, 0.5*cm))

    # Tableau des statistiques
    data = [
        ['Indicateur', 'Valeur'],
        ['Total médicaments', str(medicines_count)],
        ['Médicaments disponibles', str(medicines_available)],
        ['Pénurie de médicaments', str(low_stock_count)],
        ['Groupes de médicaments', str(groups_count)],
        ['Fournisseurs', str(suppliers_count)],
        ['Clients', str(clients_count)],
    ]

    table = Table(data, colWidths=[10*cm, 5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 1*cm))

    # Section 2: Finances
    section_title = Paragraph("<b>Finances</b>", styles['Heading2'])
    elements.append(section_title)
    elements.append(Spacer(1, 0.5*cm))

    finance_data = [
        ['Indicateur', 'Valeur'],
        ['Revenu total', f'{total_revenue:,.0f} FCFA'],
        ['Nombre de ventes', str(sales.count())],
        ['Quantité vendue', str(total_quantity_sold)],
    ]

    finance_table = Table(finance_data, colWidths=[10*cm, 5*cm])
    finance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F39C12')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    elements.append(finance_table)
    elements.append(Spacer(1, 1*cm))

    # Section 3: Top 5 médicaments
    section_title = Paragraph("<b>Top 5 Médicaments (Stock le plus élevé)</b>", styles['Heading2'])
    elements.append(section_title)
    elements.append(Spacer(1, 0.5*cm))

    top_medicines = medicines.order_by('-stock_quantity')[:5]
    medicines_data = [['Nom', 'Stock', 'Prix de vente']]

    for med in top_medicines:
        medicines_data.append([
            med.name,
            str(med.stock_quantity),
            f'{med.selling_price:,.0f} FCFA'
        ])

    medicines_table = Table(medicines_data, colWidths=[8*cm, 3*cm, 4*cm])
    medicines_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    elements.append(medicines_table)

    # Pied de page
    elements.append(Spacer(1, 2*cm))
    footer = Paragraph(
        "<i>Propulsé par Red Team © 2024 - Pharmacie Fadj-Ma</i>",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=1)
    )
    elements.append(footer)

    # Construire le PDF
    doc.build(elements)

    return response