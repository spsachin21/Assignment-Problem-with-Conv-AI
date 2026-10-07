from pathlib import Path
import re
import streamlit as st

DOC_FILE = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "optimization_model.md"
)


def show_model():

    text = DOC_FILE.read_text(encoding="utf-8")

    # Split into normal markdown and display math blocks
    parts = re.split(r"\\\[(.*?)\\\]", text, flags=re.DOTALL)

    # Even indices -> Markdown
    # Odd indices  -> LaTeX

    for i, part in enumerate(parts):

        part = part.strip()

        if not part:
            continue

        if i % 2 == 0:
            st.markdown(part)

        else:
            st.latex(part)