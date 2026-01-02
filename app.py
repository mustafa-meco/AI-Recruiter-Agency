import streamlit as st
import asyncio
import os
from agents.orchestrator import OrchestratorAgent
import json

st.set_page_config(
    page_title="AI Recruiter Agency",
    page_icon="💼",
    layout="wide"
)

# Custom CSS for a premium look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    .stExpander {
        border: 1px solid #30363d;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .success-text {
        color: #2ea043;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

async def main():
    st.title("💼 AI Recruiter Agency")
    st.markdown("### Streamline your recruitment process with AI-powered agents")

    with st.sidebar:
        st.header("Settings")
        model = st.selectbox("Select Model", ["llama3.2", "llama3.1", "mistral"], index=0)
        st.info("Ensure Ollama is running locally with the selected model.")

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    if uploaded_file is not None:
        # Save the uploaded file temporarily
        temp_dir = "uploads"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if st.button("Process Application"):
            orchestrator = OrchestratorAgent()
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Stage 1: Extraction
                status_text.text("Extracting data from resume...")
                progress_bar.progress(20)
                
                # We need to call the orchestrator's process_application
                # Since agents use async run, we need to handle it properly
                result = await orchestrator.process_application({"file_path": file_path})
                
                progress_bar.progress(100)
                status_text.text("Processing complete!")
                st.success("Successfully processed application!")

                # Display Results
                col1, col2 = st.columns(2)

                with col1:
                    st.header("Candidate Profile")
                    with st.expander("Extracted Data", expanded=True):
                        st.json(result.get("extracted_data", {}))
                    
                    with st.expander("Skills Analysis", expanded=True):
                        st.write(result.get("analysis_results", {}).get("skills_analysis", "No analysis available"))

                with col2:
                    st.header("Recruitment Insights")
                    with st.expander("Job Matches", expanded=True):
                        matches = result.get("job_matches", {}).get("matched_jobs", [])
                        if matches:
                            for match in matches:
                                st.markdown(f"**{match['title']}** - Score: `{match['match_score']}` ({match['location']})")
                        else:
                            st.write("No matches found.")

                    with st.expander("Screening Report", expanded=True):
                        st.write(result.get("screening_results", {}).get("screening_report", "No report available"))

                st.divider()
                st.header("✨ Final Recommendation")
                recommendation = result.get("recommendations", {}).get("final_recommendation", "No recommendation")
                st.info(recommendation)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                # Clean up the file if needed
                pass

if __name__ == "__main__":
    asyncio.run(main())
