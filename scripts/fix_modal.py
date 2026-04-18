with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    ("document.getElementById('modal-overlay').classList.add('open')", "bsModal().show()"),
    ("document.getElementById('modal-overlay').classList.remove('open')", "bsModal().hide()"),
    ("document.getElementById('trip-modal-overlay').classList.add('open')", "bsTripModal().show()"),
    ("document.getElementById('trip-modal-overlay').classList.remove('open')", "bsTripModal().hide()"),
    ("document.getElementById('expense-modal-overlay').classList.add('open')", "bsExpenseModal().show()"),
    ("document.getElementById('expense-modal-overlay').classList.remove('open')", "bsExpenseModal().hide()"),
    ("document.getElementById('transit-overlay').classList.add('open')", "bsTransitSheet().show()"),
    ("document.getElementById('transit-overlay').classList.remove('open')", "bsTransitSheet().hide()"),
]

for old, new in replacements:
    content = content.replace(old, new)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("done")
