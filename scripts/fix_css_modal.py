"""
Remove old modal overlay CSS that conflicts with Bootstrap Offcanvas.
The HTML overlays are gone; these rules keep the modals permanently off-screen.
"""
import re

with open("style.css", "r", encoding="utf-8") as f:
    css = f.read()

# ── Blocks to remove entirely ────────────────────────────────────────
remove_blocks = [
    # old itinerary modal overlay + modal
    r"/\* ── modal overlay[^*]*\*+/[\s\S]*?#modal-overlay\.open #modal \{ transform: translateY\(0\); \}",
    # old trip modal overlay + modal
    r"/\* ── trip modal[^*]*\*+/[\s\S]*?#trip-modal-overlay\.open #trip-modal \{ transform: translateY\(0\); \}",
    # old expense modal overlay + modal
    r"/\* ── expense modal[^*]*\*+/[\s\S]*?#expense-modal-overlay\.open #expense-modal \{ transform: translateY\(0\); \}",
    # old transit overlay + transit-sheet (transform only; keep title/subtitle classes that follow)
    r"#transit-overlay \{[\s\S]*?#transit-overlay\.open #transit-sheet \{ transform: translateY\(0\); \}",
]

for pat in remove_blocks:
    css, n = re.subn(pat, "", css, flags=re.MULTILINE)
    print(f"  removed {n} match(es) for pattern starting with: {pat[:40]!r}")

# Also remove old form classes that Bootstrap replaces (keep .modal-handle)
old_form_classes = [
    r"\.form-group \{[^}]+\}\n?",
    r"\.form-label \{[^}]+\}\n?",
    r"\.form-input,[^{]+\{[^}]+\}\n?",
    r"\.form-input:focus,[^{]+\{[^}]+\}\n?",
    r"\.form-textarea \{[^}]+\}\n?",
    r"\.form-row \{[^}]+\}\n?",
    r"\.btn-row \{[^}]+\}\n?",
    # .btn — Bootstrap defines this; our override causes layout issues
    r"\.btn \{[^}]+\}\n?",
    r"\.btn:active \{[^}]+\}\n?",
    # .btn-primary / .btn-secondary — let Bootstrap own these
    r"\.btn-primary \{[^}]+\}\n?",
    r"\.btn-secondary \{[^}]+\}\n?",
]

for pat in old_form_classes:
    css, n = re.subn(pat, "", css, flags=re.MULTILINE)
    if n:
        print(f"  removed form class {n} match(es): {pat[:40]!r}")

# Clean up excessive blank lines
css = re.sub(r"\n{4,}", "\n\n\n", css)

with open("style.css", "w", encoding="utf-8") as f:
    f.write(css)

print("done")
