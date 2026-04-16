"""
Medical knowledge ingest script.
Run once to populate Pinecone with medical guidelines.

Usage:
    cd backend
    python -m app.rag.ingest
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.rag.retriever import ingest_medical_documents

# Sample Indian medical guidelines — extend with real PubMed / NHM docs
SAMPLE_DOCUMENTS = [
    {
        "text": "Malaria treatment protocol India: For uncomplicated P. vivax malaria in adults, administer Chloroquine 10mg/kg on Day 1 and Day 2, then 5mg/kg on Day 3. Add Primaquine 0.25mg/kg/day for 14 days. For P. falciparum, use Artemisinin-based Combination Therapy (ACT). Perform RDT before initiating treatment.",
        "source": "NHM India — Malaria Treatment Guidelines 2023",
        "metadata": {"disease": "malaria", "type": "treatment_protocol"},
    },
    {
        "text": "Acute Respiratory Infection (ARI) management at PHC level: Assess respiratory rate. Classify as Pneumonia if RR ≥50/min in infants or ≥40/min in children 1-5 years. Treat with Amoxicillin 40mg/kg/day in 2 divided doses for 5 days. Refer immediately if SpO2 <94%, severe chest indrawing, or inability to feed.",
        "source": "IMNCI Guidelines — Integrated Management of Childhood Illness",
        "metadata": {"disease": "ARI", "type": "treatment_protocol"},
    },
    {
        "text": "Diarrhea management ORS protocol: Prepare ORS with 1 litre clean water. Give 50-100ml/kg over 3-4 hours for some dehydration. Continue breastfeeding. Zinc supplementation: 20mg/day for 14 days in children under 5. Do not use antibiotics routinely. Refer for IV fluids if severe dehydration, bloody stool, or unable to drink.",
        "source": "NHM India — Diarrheal Disease Guidelines",
        "metadata": {"disease": "diarrhea", "type": "treatment_protocol"},
    },
    {
        "text": "Tuberculosis identification: Suspect TB in patients with cough >2 weeks, fever, night sweats, and weight loss. Collect sputum for AFB smear. In children with negative smear, use Mantoux test and chest X-ray. Refer all suspected TB cases to DOTS centre for RNTCP registration and Category I treatment.",
        "source": "RNTCP — National TB Elimination Programme India",
        "metadata": {"disease": "tuberculosis", "type": "diagnosis_protocol"},
    },
    {
        "text": "Hypertension management at PHC: Screen all adults >30 years. Diagnose if BP ≥140/90 on 2 readings. First-line treatment: Amlodipine 5mg once daily. Add Losartan 50mg if BP uncontrolled. Emergency referral if BP >180/120 with symptoms of headache, vision changes, chest pain or confusion (hypertensive urgency).",
        "source": "NHM India — Hypertension Management Protocol",
        "metadata": {"disease": "hypertension", "type": "treatment_protocol"},
    },
    {
        "text": "Diabetes management type 2 at PHC: Screen high-risk patients with fasting glucose. Diagnose if FPG ≥126mg/dL on 2 occasions. Start Metformin 500mg BD with meals. Add Glipizide if HbA1c >7.5% after 3 months. Refer for foot ulcers, retinopathy screening, nephropathy, or HbA1c >9% unresponsive to oral therapy.",
        "source": "NHM India — Diabetes Management Guidelines",
        "metadata": {"disease": "diabetes", "type": "treatment_protocol"},
    },
    {
        "text": "Dengue fever recognition and management: Suspect dengue in febrile patients in endemic areas with retro-orbital headache, myalgia, rash. Perform NS1 antigen test in first 5 days. Monitor CBC for thrombocytopenia (platelets <100,000). Warning signs requiring hospitalization: abdominal pain, persistent vomiting, bleeding, rapid deterioration. Give paracetamol only — avoid aspirin and ibuprofen.",
        "source": "NVBDCP — National Dengue Control Programme India",
        "metadata": {"disease": "dengue", "type": "management_protocol"},
    },
    {
        "text": "Skin conditions common in India: Scabies — intense nocturnal itching, burrows between fingers, wrists, genitalia. Treat with Permethrin 5% cream applied whole body for 8-14 hours. Treat all household contacts simultaneously. Tinea infections — ringworm pattern, treat with topical Clotrimazole 1% for 4 weeks. Refer for extensive involvement or immunocompromised patients.",
        "source": "NLEP — National Leprosy and Skin Programme Guidelines",
        "metadata": {"disease": "skin", "type": "treatment_protocol"},
    },
]


if __name__ == "__main__":
    print("Ingesting medical documents into Pinecone...")
    try:
        index = ingest_medical_documents(SAMPLE_DOCUMENTS)
        print(f"Successfully ingested {len(SAMPLE_DOCUMENTS)} documents")
        print("You can now add more documents by extending SAMPLE_DOCUMENTS")
        print("Real sources to add: PubMed abstracts, NHM guidelines PDFs, WHO clinical handbooks")
    except Exception as e:
        print(f"Ingest failed: {e}")
        print("Make sure PINECONE_API_KEY and OPENAI_API_KEY are set in .env")
