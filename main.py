import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.graphics.shapes import Drawing, Rect, Circle, Polygon
from reportlab.graphics import renderPDF
from reportlab.lib.colors import red, silver, black, gray
import os


def draw_heart(canvas, x, y, size=10):
    d = Drawing(size, size)

    # Left circle
    d.add(Circle(size * 0.3, size * 0.7, size * 0.2, fillColor=red, strokeColor=red))
    # Right circle
    d.add(Circle(size * 0.7, size * 0.7, size * 0.2, fillColor=red, strokeColor=red))
    # Bottom triangle
    d.add(
        Polygon(
            points=[
                size * 0.1,
                size * 0.7,
                size * 0.5,
                size * 0.1,
                size * 0.9,
                size * 0.7,
            ],
            fillColor=red,
            strokeColor=red,
        )
    )

    # Render the heart onto the main canvas at position (x, y)
    renderPDF.draw(d, canvas, x, y)


def draw_sword(canvas, x, y, size=10):
    d = Drawing(size, size)

    # Blade (long rectangle)
    blade_width = size * 0.15
    blade_height = size * 0.65
    blade_x = (size - blade_width) / 2
    blade_y = size * 0.25
    d.add(
        Rect(
            blade_x,
            blade_y,
            blade_width,
            blade_height,
            fillColor=silver,
            strokeColor=black,
        )
    )

    # Tip (triangle)
    tip_height = size * 0.1
    d.add(
        Polygon(
            points=[
                size / 2,
                blade_y + blade_height + tip_height,
                blade_x,
                blade_y + blade_height,
                blade_x + blade_width,
                blade_y + blade_height,
            ],
            fillColor=silver,
            strokeColor=black,
        )
    )

    # Crossguard (horizontal line)
    crossguard_width = size * 0.6
    crossguard_height = size * 0.05
    guard_x = (size - crossguard_width) / 2
    guard_y = blade_y - crossguard_height / 2
    d.add(
        Rect(
            guard_x,
            guard_y,
            crossguard_width,
            crossguard_height,
            fillColor=gray,
            strokeColor=black,
        )
    )

    # Handle (short grip below guard)
    handle_height = size * 0.25
    handle_width = blade_width
    handle_x = blade_x
    handle_y = guard_y - handle_height
    d.add(
        Rect(
            handle_x,
            handle_y,
            handle_width,
            handle_height,
            fillColor=black,
            strokeColor=black,
        )
    )

    renderPDF.draw(d, canvas, x, y)


# Config
page_width, page_height = letter
margin = 0.25 * cm
cols, rows = 3, 3

card_width = (page_width - 2 * margin) / cols
card_height = (page_height - 2 * margin) / rows

header_height = 1 * cm
image_height = 5 * cm
footer_height = card_height - header_height - image_height

# Load cards
with open("cards.json") as f:
    cards = json.load(f)

# PDF
c = canvas.Canvas("cards_sheet.pdf", pagesize=letter)

for i, card in enumerate(cards):
    col = i % cols
    row = (i // cols) % rows
    if i > 0 and i % (cols * rows) == 0:
        c.showPage()

    x = margin + col * card_width
    y = page_height - margin - (row + 1) * card_height

    # Card border
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(2)
    c.rect(x, y, card_width, card_height)

    # === Section 1: Stat + Title ===
    stat_width = 1.5 * cm
    name_width = card_width - stat_width

    stat_text = card.get("stat", "5")
    name_text = card.get("title", "Untitled")

    # Stat box
    c.rect(x, y + card_height - header_height, stat_width, header_height)

    # Icon + Text sizing/alignment
    icon_size = 12
    text_size = 10
    padding_left = 3  # from left edge of stat box
    spacing = 6  # space between icon and number

    # Calculate vertical alignment
    icon_y = y + card_height - header_height / 2 - icon_size / 2 + 1
    text_y = y + card_height - header_height / 2 - text_size / 2 + 1

    # Draw icon + number
    number = "".join(filter(str.isdigit, stat_text))
    c.setFont("Helvetica-Bold", text_size)

    if card.get("team") == "slime":
        draw_sword(c, x + padding_left, icon_y, size=icon_size)
        c.drawString(x + padding_left + icon_size + spacing, text_y, number)
    else:
        draw_heart(c, x + padding_left, icon_y, size=icon_size)
        c.drawString(x + padding_left + icon_size + spacing, text_y, number)

    # Title box
    title_x = x + stat_width
    title_y = y + card_height - header_height
    c.rect(title_x, title_y, name_width, header_height)

    # Dynamically scale title font
    max_font_size = 12
    min_font_size = 5
    text_padding = 4  # pts
    for size in range(max_font_size, min_font_size - 1, -1):
        c.setFont("Helvetica-Bold", size)
        text_width = c.stringWidth(name_text, "Helvetica-Bold", size)
        if text_width < (name_width - text_padding):
            break
    # Center vertically
    text_y_offset = (header_height - size) / 2
    c.drawString(title_x + text_padding / 2, title_y + text_y_offset, name_text)

    # === Section 2: Image ===
    image_y = y + footer_height
    image_x = x
    image_w = card_width
    image_h = image_height

    # Draw image border
    c.rect(image_x, image_y, image_w, image_h)

    # Draw image inside with padding
    if "image" in card and os.path.exists(card["image"]):
        try:
            img = ImageReader(card["image"])
            padding = 0.3 * cm
            img_w = card_width - 2 * padding
            img_h = image_height - 2 * padding
            img_x = x + padding
            img_y = image_y + padding
            c.drawImage(
                img,
                img_x,
                img_y,
                width=img_w,
                height=img_h,
                preserveAspectRatio=True,
                anchor="c",
            )
        except Exception as e:
            print(f"Image error: {e}")

    # === Section 3: Effect + Filler ===
    effect_text = card.get("effect", "Special Ability")
    filler_text = card.get("filler", "Flavor text here.")

    text_x = x + 0.5 * cm
    text_y = y + 0.5 * cm

    c.setFont("Helvetica-Oblique", 8)
    c.drawString(text_x, text_y + 1.2 * cm, effect_text)
    c.setFont("Helvetica", 7)
    c.drawString(text_x, text_y + 0.6 * cm, filler_text)

c.save()
