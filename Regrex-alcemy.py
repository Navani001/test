# -----------------------------
# 3. Parse coordinates
# -----------------------------

word_coords = []

for item in str(coord_string).split("|"):

    values = [float(x) for x in item.split(",")]

    if len(values) == 4:
        word_coords.append(values)


# -----------------------------
# 4. Open PDF
# -----------------------------

pdf = fitz.open("your.pdf")

# PDF page numbers are 0-based
page = pdf[page_number - 1]


# -----------------------------
# 5. Render ONLY this page
# -----------------------------

zoom = 2

pix = page.get_pixmap(
    matrix=fitz.Matrix(zoom, zoom),
    alpha=False
)

image = Image.open(
    io.BytesIO(pix.tobytes("png"))
)

image_width, image_height = image.size


# -----------------------------
# 6. Display page
# -----------------------------

fig, ax = plt.subplots(
    figsize=(14, 18)
)

ax.imshow(image)


# -----------------------------
# 7. Draw WORD boxes
# -----------------------------

for i, coord in enumerate(word_coords):

    x1, y1, x2, y2 = coord

    # normalized -> image coordinates
    x = x1 * image_width
    y = y1 * image_height

    width = (x2 - x1) * image_width
    height = (y2 - y1) * image_height

    rect = patches.Rectangle(
        (x, y),
        width,
        height,
        linewidth=1,
        edgecolor="red",
        facecolor="none"
    )

    ax.add_patch(rect)

    # Word number
    ax.text(
        x,
        y,
        str(i + 1),
        fontsize=7,
        color="red",
        backgroundcolor="white"
    )


# -----------------------------
# 8. Show
# -----------------------------

ax.set_xlim(0, image_width)
ax.set_ylim(image_height, 0)
ax.axis("off")

plt.tight_layout()
plt.show()

pdf.close()
