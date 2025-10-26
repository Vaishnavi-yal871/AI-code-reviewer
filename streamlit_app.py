import streamlit as st
import subprocess
import tempfile
import json
from radon.complexity import cc_visit
from radon.metrics import mi_visit

st.set_page_config(page_title="AI Code Reviewer", page_icon="🤖", layout="wide")

st.title("🤖 AI Code Reviewer & Formatter")
st.write("Upload or paste your Python code, and get automatic linting, formatting, and complexity analysis.")

# ---- Input Section ----
code_input = st.text_area("✍️ Paste your Python code below:", height=300)
uploaded_file = st.file_uploader("📂 Or upload a Python file", type=["py"])

if uploaded_file:
    code_input = uploaded_file.read().decode("utf-8")

if st.button("🔍 Analyze / Format ▶"):
    if not code_input.strip():
        st.warning("Please provide some Python code first.")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as temp:
            temp.write(code_input)
            temp_path = temp.name

        # ---- Run Flake8 ----
        flake8_result = subprocess.run(
            ["flake8", temp_path],
            capture_output=True,
            text=True
        ).stdout.strip() or "✅ No style issues found!"

        # ---- Run Black (formatting) ----
        subprocess.run(["black", "--quiet", temp_path])
        with open(temp_path, "r", encoding="utf-8") as f:
            formatted_code = f.read()

        # ---- Run Radon (Complexity + Maintainability) ----
        cc_result = cc_visit(code_input)
        mi_score = mi_visit(code_input, True)
        complexity_report = [
            {"name": f.name, "complexity": f.complexity} for f in cc_result
        ]

        # ---- Show Results ----
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⚠️ Flake8 Style Warnings")
            st.code(flake8_result, language="text")

            st.subheader("📄 Original Code")
            st.code(code_input, language="python")

        with col2:
            st.subheader("✨ Black Formatted Code")
            st.code(formatted_code, language="python")

            st.subheader("📊 Radon Metrics")
            st.json({
                "Maintainability Index": round(mi_score, 2),
                "Cyclomatic Complexity": complexity_report
            })

        # ---- Summary ----
        st.divider()
        st.subheader("💡 Suggestions:")
        if "E501" in flake8_result:
            st.write("- Lines too long → break into smaller chunks.")
        if "E302" in flake8_result:
            st.write("- Missing blank lines between functions.")
        if len(cc_result) > 0:
            high_complex = [f for f in cc_result if f.complexity > 10]
            if high_complex:
                st.write(f"- {len(high_complex)} function(s) are too complex → consider splitting them.")
        st.write("✅ Use consistent naming and add docstrings for clarity.")

        # ---- Export Report ----
        report = {
            "flake8": flake8_result,
            "mi_score": mi_score,
            "complexity": complexity_report,
            "suggestio
