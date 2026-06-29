# Human-Guided Agentic Review System (HGARS)
### Cotiviti Intern Assessment - Clinical Decision Making & Pattern Recognition

**Rashmita Kudamala | Indiana University Indianapolis**

---

## Overview
A proof-of-concept Streamlit application demonstrating an agentic AI framework
for Treatment, Payment, and Operations (TPO) use cases in healthcare. The system
simulates a human-guided agentic review pipeline that ingests clinical and billing
documentation, generates chain-of-thought reasoning using a large language model,
and routes structured outputs to a human auditor for final validation.

## TPO Scenarios Demonstrated
- **Case 1:** Complex respiratory discharge audit — readmission risk classification
- **Case 2:** Prior authorization coding discrepancy — payer contract compliance
- **Case 3:** ED cost forecasting — high-frequency utilizer pattern detection

## Architecture
- **LLM:** Groq API (Llama 3.3 70B) for dynamic chain-of-thought reasoning
- **Frontend:** Streamlit
- **Fallback:** Simulation mode if API unavailable

## Setup & Run

1. Clone the repository:

```bash
   git clone https://github.com/rashmitakudamala/Cotiviti_Intern_Assessment.git
   cd Cotiviti_Intern_Assessment
```

2. Install dependencies:

```bash
   pip install -r requirements.txt
```

3. Create a `.env` file in the project root:

```
   GROQ_API_KEY=your_groq_api_key_here
```


4. Run the application:

```bash
   streamlit run app.py
```

## Repository Structure
```
Cotiviti_Intern_Assessment/
├── app.py                                              # Main Streamlit application
├── requirements.txt                                    # Python dependencies
├── .gitignore                                          # Git ignore rules
├── README.md                                           # Project documentation
├── INTERN_Rashmita_Kudamala_Indiana_University_Indianapolis.docx   # Written report
├── Intern_Cotiviti_HGARS_Presentation_Rashmita_Kudamala.pptx      # Slide presentation
└── INTERN_Rashmita_Kudamala_Indiana_University_Indianapolis.mp4    # Video recording
```           

## Note on Data Usage
All clinical cases use synthetic, mock data. No real patient data is used.
