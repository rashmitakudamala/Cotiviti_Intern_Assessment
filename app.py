import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

if "cot_output" not in st.session_state:
    st.session_state.cot_output = ""

def on_case_change():
    st.session_state.cot_output = ""

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

st.set_page_config(page_title="HGARS - Cotiviti POC", page_icon="🏥", layout="wide")
st.title("🏥 Human-Guided Agentic Review System (HGARS)")
st.caption("Proof of Concept | Rashmita Kudamala | Indiana University Indianapolis")
st.markdown("---")

MOCK_CASES = {
    "Case 1: Complex Respiratory Discharge Audit": {
        "text": (
            "Patient is a 68-year-old female admitted with acute exacerbation of COPD and secondary "
            "pneumonia. Inpatient stay: 6 days. Last recorded vitals show fluctuating SpO2 (91–93% on "
            "room air). Home oxygen setup has not been confirmed by the supplier. Physical therapy note "
            "indicates patient requires maximum assistance for ambulation. Billing submitted under "
            "standard uncomplicated respiratory DRG; clinical timeline suggests high readmission risk."
        ),
        "fallback_steps": [
            "**Step 1 — Ingestion & Entity Extraction:** Parsed unstructured clinical note and scanned "
            "billing record. Extracted key entities: SpO2 range (91–93%), LOS (6 days), PT mobility "
            "score (max assistance), DRG code (standard respiratory, uncomplicated).",
            "**Step 2 — Pattern Recognition:** Identified conflicting signal — inpatient LOS and DRG "
            "code align with standard billing expectations, but PT assessment and unconfirmed oxygen "
            "procurement indicate incomplete discharge readiness.",
            "**Step 3 — Predictive Inference:** Modeled readmission probability using extracted "
            "trajectory features. Elevated risk flagged based on functional mobility deficit and "
            "unresolved home oxygen infrastructure.",
            "**Step 4 — TPO Recommendation:** Resource utilization pattern exceeds standard DRG "
            "allocation assumptions. Routing to human auditor for discharge deferral review and "
            "care management referral.",
        ],
        "metrics": {
            "Readmission Risk": "High (84%)",
            "Discharge Status": "Unsafe / Deferred",
            "Cost Tier": "Tier 3 — High Ops Focus",
        },
        "flags": [
            ("warning", "Home oxygen infrastructure not confirmed prior to discharge"),
            ("warning", "Functional mobility deficit misaligned with discharge destination"),
        ],
    },
    "Case 2: Prior Authorization Coding Discrepancy": {
        "text": (
            "Prior authorization request submitted for left total knee arthroplasty (ICD-10: Z47.1). "
            "Attached clinical documentation shows conservative management (physical therapy and NSAIDs) "
            "was attempted for only 3 weeks. Payer-provider contract clause 14.2 mandates a minimum of "
            "6 weeks of documented conservative therapy prior to surgical authorization clearance."
        ),
        "fallback_steps": [
            "**Step 1 — Ingestion & Entity Extraction:** Parsed prior authorization request and "
            "extracted structured contract metadata. Identified procedure code (ICD-10: Z47.1) and "
            "documented conservative therapy duration (3 weeks).",
            "**Step 2 — Pattern Recognition:** Mapped clause 14.2 requirement (minimum 6 weeks "
            "conservative therapy) against extracted EHR timeline. Duration mismatch detected: "
            "3 weeks documented vs. 6 weeks required.",
            "**Step 3 — Predictive Inference:** Classified request as non-compliant with payer "
            "contract terms. Shortfall calculated at 3 weeks below contractual threshold.",
            "**Step 4 — TPO Recommendation:** Flagged for pre-adjudication capture. Authorization "
            "denial recommended pending additional documentation or medical necessity override.",
        ],
        "metrics": {
            "Readmission Risk": "N/A (Pre-Op)",
            "Discharge Status": "Authorization Denied",
            "Cost Tier": "Tier 1 — Standard Claim",
        },
        "flags": [
            ("error", "Non-compliance: Payer Contract Clause 14.2 — conservative therapy minimum not met"),
            ("warning", "Duration shortfall: 3 weeks documented vs. 6 weeks required"),
        ],
    },
    "Case 3: ED Cost Forecasting — High-Frequency Utilizer": {
        "text": (
            "Patient is a 54-year-old male with three ED visits in the past 90 days for chest pain, "
            "dyspnea, and dizziness. No inpatient admissions. Discharge summaries indicate no acute "
            "cardiac findings across all three visits. No documented care management enrollment or "
            "follow-up primary care appointment scheduled. Billing submitted under ED evaluation and "
            "management codes (Level 4 and Level 5)."
        ),
        "fallback_steps": [
            "**Step 1 — Ingestion & Entity Extraction:** Parsed longitudinal ED encounter records "
            "across 3 visits. Extracted visit frequency (3 in 90 days), chief complaints (chest pain, "
            "dyspnea, dizziness), and billing code distribution (Level 4/5 E&M).",
            "**Step 2 — Pattern Recognition:** Identified high-frequency ED utilization pattern with "
            "no acute findings across all visits. Absence of care management enrollment and PCP "
            "follow-up flagged as upstream care access gap.",
            "**Step 3 — Predictive Inference:** Projected continued ED utilization cost at current "
            "rate. Downstream operational spend significantly exceeds cost of proactive care "
            "management intervention.",
            "**Step 4 — TPO Recommendation:** Flagging for care management program enrollment. "
            "Proactive outreach recommended to reduce avoidable ED utilization and associated "
            "operational cost burden.",
        ],
        "metrics": {
            "Readmission Risk": "Moderate (61%)",
            "Discharge Status": "Care Management Referral",
            "Cost Tier": "Tier 2 — Preventable Utilization",
        },
        "flags": [
            ("warning", "High-frequency ED utilizer — 3 visits in 90 days, no acute findings"),
            ("warning", "No care management enrollment or PCP follow-up documented"),
        ],
    },
}

SYSTEM_PROMPT = """You are a clinical AI agent for a healthcare payer analytics platform analyzing \
medical records and billing data for Treatment, Payment & Operations (TPO).

Given the clinical or billing text provided, generate exactly 4 chain-of-thought reasoning steps.

Format EACH step exactly as:
**Step N — Step Name:** Reasoning here.

The 4 steps must cover:
1. Ingestion & Entity Extraction — extract key clinical entities, billing codes, and operational data points
2. Pattern Recognition — identify clinical risk patterns, compliance mismatches, or operational anomalies
3. Predictive Inference — perform risk or compliance classification based on extracted patterns
4. TPO Recommendation — specific recommendation for treatment, payment adjudication, or operational routing

Be specific to the exact text provided. Use precise clinical and healthcare operations terminology. \
Keep each step to 2-3 sentences. Output only the 4 steps, no preamble or closing remarks."""

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️ HGARS Configuration Panel")
st.sidebar.info(
    "Demonstrates multi-step agentic inference, TPO pattern recognition, "
    "and a structured human-in-the-loop validation checkpoint."
)
selected = st.sidebar.selectbox(
    "Select TPO Scenario:",
    list(MOCK_CASES.keys()),
    key="selected_case",
    on_change=on_case_change,
)

case = MOCK_CASES[selected]

st.sidebar.markdown("---")
st.sidebar.markdown("**System Status**")
st.sidebar.success("Agent Engine: Online")
st.sidebar.success("Human Validation: Active")

api_key = os.environ.get("GROQ_API_KEY", "")
use_real_llm = GROQ_AVAILABLE and bool(api_key)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**LLM Mode:** {'🟢 Groq / Llama 3.3' if use_real_llm else '🟡 Simulation'}")

# ── Layout ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1. Ingest Clinical & Billing Records")
    input_text = st.text_area(
        "Multimodal Input Workspace (Clinical notes, ICD codes, Contract terms):",
        value=case["text"],
        height=220,
    )
    trigger = st.button("Trigger Agentic Reasoning Pipeline", use_container_width=True)

    if trigger:
        with st.spinner("Running agentic reasoning pipeline..."):
            if use_real_llm:
                try:
                    client = Groq(api_key=api_key)
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"Clinical/Billing Text:\n\n{input_text}"},
                        ],
                        max_tokens=700,
                        temperature=0.2,
                    )
                    st.session_state.cot_output = response.choices[0].message.content
                except Exception:
                    st.session_state.cot_output = "\n\n".join(case["fallback_steps"])
            else:
                st.session_state.cot_output = "\n\n".join(case["fallback_steps"])

    if st.session_state.cot_output:
        st.subheader("2. Chain-of-Thought Reasoning")
        st.markdown(st.session_state.cot_output)
        st.success("Agentic analysis complete. Output routed to human validation checkpoint.")

with col2:
    st.subheader("3. Structured Inference Outputs")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div style="background:#1a2332;border-left:4px solid #e05252;
        padding:14px;border-radius:6px;text-align:center;">
        <div style="color:#aaa;font-size:11px;margin-bottom:6px;">READMISSION RISK</div>
        <div style="color:#e05252;font-size:17px;font-weight:700;">
        {case["metrics"]["Readmission Risk"]}</div></div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div style="background:#1a2332;border-left:4px solid #f0c040;
        padding:14px;border-radius:6px;text-align:center;">
        <div style="color:#aaa;font-size:11px;margin-bottom:6px;">DISCHARGE / AUTH STATUS</div>
        <div style="color:#f0c040;font-size:17px;font-weight:700;">
        {case["metrics"]["Discharge Status"]}</div></div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div style="background:#1a2332;border-left:4px solid #4fc3f7;
        padding:14px;border-radius:6px;text-align:center;">
        <div style="color:#aaa;font-size:11px;margin-bottom:6px;">TPO COST TIER</div>
        <div style="color:#4fc3f7;font-size:17px;font-weight:700;">
        {case["metrics"]["Cost Tier"]}</div></div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### Compliance & Clinical Flags")
    for flag_type, flag_text in case["flags"]:
        if flag_type == "error":
            st.error(flag_text)
        else:
            st.warning(flag_text)

    st.markdown("---")
    st.subheader("4. Human Auditor Validation Checkpoint")
    st.write("Review the agent reasoning chain and select a resolution action:")
    action = st.radio(
        "Auditor Resolution:",
        [
            "Approve Agent Findings & Auto-Adjudicate",
            "Override — Route to Medical Director",
            "Flag for Secondary Audit Review",
        ],
    )
    st.text_area(
        "Auditor Comments (Optional):",
        placeholder="Enter clinical or operational justification...",
    )
    if st.button("Confirm & Submit Resolution", type="primary", use_container_width=True):
        st.success(f"Resolution confirmed. Action logged: **{action}**")
        st.info("Submission recorded in HGARS operational tracking log.")