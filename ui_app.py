import streamlit as st
from aws_collector import collect_selected_services, format_data_for_llm
from qa_engine import query_aws_knowledgebase
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.stateful_button import button
import plotly.express as px
import json
import tempfile
from pathlib import Path

st.set_page_config(page_title="AWS Infra Explainer", layout="wide", page_icon="📊")

# Theme toggle
is_dark_mode = st.sidebar.toggle("🌗 Dark Mode")
if is_dark_mode:
    st.markdown("""
    <style>
        body { background-color: #1e1e1e; color: white; }
    </style>
    """, unsafe_allow_html=True)

# Header
with st.container():
    colored_header(
        label="AWS Infra Explainer",
        description="Query and visualize your AWS infrastructure using natural language.",
        color_name="violet-70"
    )

# Sidebar controls
st.sidebar.image("https://a.storyblok.com/f/165473/400x400/57f3c2a285/aws.png", width=120)
st.sidebar.title("Configuration Panel")

all_services = [
    'IAM', 'EC2', 'S3', 'Lambda', 'ELB', 'EKS', 'Route53',
    'CloudFormation', 'CodeBuild', 'CodePipeline', 'RDS', 'DynamoDB', 'Billing'
]

selected_services = st.sidebar.multiselect(
    "🧰 Choose services to inspect:", all_services, default=['EC2', 'IAM']
)

llm_model = st.sidebar.text_input("💬 Ollama LLM Model", value="qwen:0.5b")
embed_model = st.sidebar.text_input("📐 Embedding Model", value="nomic-embed-text")

# AWS Data Button
if st.sidebar.button("🚀 Collect AWS Data"):
    with st.spinner("🔍 Scanning selected AWS services and building knowledgebase..."):
        aws_data = collect_selected_services(selected_services)
        documents = format_data_for_llm(aws_data)
        st.session_state['docs'] = documents
        st.session_state['aws_raw'] = aws_data
        st.success("✅ AWS data collected and embedded into knowledgebase!")

# Tab layout
if 'docs' in st.session_state:
    tab1, tab2, tab3 = st.tabs(["🧠 Ask Questions", "📊 Service Summary", "🧾 Raw JSON"])

    with tab1:
        st.subheader("Ask your Infra Anything")
        user_q = st.text_input("Type your question about your AWS environment")

        if user_q:
            with st.spinner("💡 Thinking..."):
                answer = query_aws_knowledgebase(
                    query=user_q,
                    text_documents=st.session_state['docs'],
                    embed_model=embed_model,
                    llm_model=llm_model
                )
                st.markdown(f"""
                    <div style='padding:1rem; border-left: 5px solid #7b3fe4; background-color:#f6f2ff; border-radius: 8px;'>
                        <strong>Answer:</strong><br>{answer}
                    </div>
                    """, unsafe_allow_html=True)


    with tab2:
        st.subheader("📊 Service Overview")
        aws_data = st.session_state['aws_raw']
        if aws_data:
            service_counts = {svc: len(json.dumps(data)) for svc, data in aws_data.items() if isinstance(data, dict)}
            fig = px.bar(
                x=list(service_counts.keys()),
                y=list(service_counts.values()),
                labels={'x': 'Service', 'y': 'Data Size'},
                color=list(service_counts.keys()),
                title="Relative Data Collected per Service"
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Raw AWS JSON Dump")
        st.json(st.session_state['aws_raw'], expanded=False)

        with st.expander("📄 Export Options"):
            format_option = st.radio("Choose export format:", ["JSON", "HTML"], horizontal=True)
            if st.button("📥 Download Report"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format_option.lower()}") as tmp_file:
                    path = Path(tmp_file.name)
                    if format_option == "JSON":
                        path.write_text(json.dumps(st.session_state['aws_raw'], indent=2))
                    elif format_option == "HTML":
                        html_content = f"<html><body><pre>{json.dumps(st.session_state['aws_raw'], indent=2)}</pre></body></html>"
                        path.write_text(html_content)
                    st.success(f"{format_option} report is ready!")
                    st.download_button(
                        label=f"📎 Download {format_option} Report",
                        data=path.read_bytes(),
                        file_name=f"aws_report.{format_option.lower()}",
                        mime="application/json" if format_option == "JSON" else "text/html"
                    )
else:
    st.info("➡️ Use the sidebar to configure and collect AWS data.")
