"""Canned demo data. Mirrors samples/policy.pdf and the two bill images."""

from .models import AnalysisResponse, BillFields, Clause, Facts, Gap, LineItem, PolicyFields, Totals, Verdict

DISCLAIMER = (
    "Claim-It is an assistive demo, not legal, medical, or financial advice. "
    "Coverage outcomes are estimates. Verify every clause and document with your insurer before submitting."
)

TRANSCRIPTS = {
    "hi-IN": (
        "मेरी माँ सुनीता शर्मा, उम्र 54 साल, 24 अक्टूबर की रात सीढ़ियों से गिर गईं। "
        "दाहिनी कलाई की हड्डी टूट गई। हम उन्हें जयपुर के CityCare अस्पताल ले गए और उसी रात भर्ती कराया। "
        "27 अक्टूबर को छुट्टी मिली। पॉलिसी नंबर BSG-HS-2025-88421 है। सर्जरी हुई और रॉड डाली गई। "
        "बिल लगभग डेढ़ लाख रुपये का है। अस्पताल ने कहा कि पहले से मंज़ूरी नहीं ली गई, और डिस्चार्ज समरी अभी नहीं मिली है।"
    ),
    "en-IN": (
        "My mother Sunita Sharma, 54, fell down the stairs on the night of 24 October. She fractured her right wrist. "
        "We took her to CityCare Hospital in Jaipur and she was admitted the same night. She was discharged on 27 October. "
        "The policy number is BSG-HS-2025-88421. She had surgery and a rod was inserted. The bill is around one and a half lakh rupees. "
        "The hospital said pre-authorisation was not taken, and the discharge summary is not ready yet."
    ),
    "ta-IN": (
        "என் அம்மா சுனிதா சர்மா, வயது 54, அக்டோபர் 24 இரவு படிக்கட்டுகளில் இருந்து கீழே விழுந்தார். "
        "வலது மணிக்கட்டு எலும்பு முறிந்தது. ஜெய்ப்பூரில் உள்ள CityCare மருத்துவமனையில் அதே இரவு அனுமதிக்கப்பட்டார். "
        "அக்டோபர் 27 அன்று வெளியேறினார். பாலிசி எண் BSG-HS-2025-88421. அறுவை சிகிச்சை செய்யப்பட்டது. "
        "பில் சுமார் ஒன்றரை லட்ச ரூபாய். முன் அனுமதி எடுக்கவில்லை, டிஸ்சார்ஜ் சுருக்கம் இன்னும் கிடைக்கவில்லை."
    ),
    "te-IN": (
        "మా అమ్మ సునీతా శర్మ, వయస్సు 54, అక్టోబర్ 24 రాత్రి మెట్లు నుండి కింద పడిపోయారు. "
        "కుడి మణికట్టు ఎముక విరిగింది. జైపూర్‌లోని CityCare ఆసుపత్రికి తీసుకెళ్లి అదే రాత్రి చేర్చారు. "
        "అక్టోబర్ 27న డిశ్చార్జ్ అయ్యారు. పాలసీ నంబర్ BSG-HS-2025-88421. ఆపరేషన్ జరిగింది. "
        "బిల్లు దాదాపు ఒకటిన్నర లక్షలు. ముందస్తు అనుమతి తీసుకోలేదు, డిశ్చార్జ్ సమ్మరీ ఇంకా రాలేదు."
    ),
    "bn-IN": (
        "আমার মা সুনিতা শর্মা, বয়স ৫৪, ২৪ অক্টোবর রাতে সিঁড়ি থেকে পড়ে গেছেন। "
        "ডান হাতের কব্জির হাড় ভেঙেছে। জয়পুরের CityCare হাসপাতালে সেই রাতেই ভর্তি করেছি। "
        "২৭ অক্টোবর ছাড়া পেয়েছেন। পলিসি নম্বর BSG-HS-2025-88421। অপারেশন হয়েছে। "
        "বিল প্রায় দেড় লাখ টাকা। আগাম অনুমতি নেওয়া হয়নি, ডিসচার্জ সামারি এখনও পাইনি।"
    ),
}

SPEECH = {
    "hi-IN": (
        "सुनीता जी, आपका दावा ज़्यादातर मान्य है, लेकिन पूरा नहीं। लगभग एक लाख इक्कीस हज़ार दो सौ तीस रुपये कवर हो सकते हैं। "
        "तीन चीज़ें बाकी हैं: डिस्चार्ज समरी, प्री-ऑथराइज़ेशन, और फार्मेसी बिल पर नाम सुधार। "
        "कृपया ये दस्तावेज़ अस्पताल से लेकर बीमा कंपनी को भेजें।"
    ),
    "en-IN": (
        "Sunita's claim is mostly valid, but it is not fully payable as submitted. About one lakh twenty-one thousand two hundred and thirty rupees may be covered. "
        "Three things are pending: the discharge summary, pre-authorisation, and a name correction on the pharmacy bill. "
        "Please collect these documents from the hospital and send them to the insurer."
    ),
    "ta-IN": (
        "சுனிதாவின் க்ளெய்ம் பெரும்பாலும் செல்லுபடியாகும், ஆனால் முழுமையாக திரும்பப் பெற முடியாது. "
        "சுமார் ஒரு லட்சத்து இருபத்தோரு ஆயிரத்து இருநூற்று முப்பது ரூபாய் கவர் ஆகலாம். "
        "டிஸ்சார்ஜ் சுருக்கம், முன் அனுமதி, மருந்துச் சீட்டில் பெயர் திருத்தம் ஆகியவை பாக்கி உள்ளன."
    ),
    "te-IN": (
        "సునీత గారి క్లెయిమ్ ఎక్కువగా చెల్లుబాటు అవుతుంది, కానీ పూర్తిగా రాదు. "
        "సుమారు ఒక లక్ష ఇరవై ఒక్క వేల రెండు వందల ముప్పై రూపాయలు కవర్ కావచ్చు. "
        "డిశ్చార్జ్ సమ్మరీ, ముందస్తు అనుమతి, ఫార్మసీ బిల్లులో పేరు సవరణ పెండింగ్‌లో ఉన్నాయి."
    ),
    "bn-IN": (
        "সুনিতার দাবি বেশিরভাগ বৈধ, তবে সম্পূর্ণ টাকা পাওয়া যাবে না। "
        "প্রায় এক লক্ষ একুশ হাজার দুইশত ত্রিশ টাকা কভার হতে পারে। "
        "ডিসচার্জ সামারি, আগাম অনুমতি এবং ফার্মেসি বিলে নাম সংশোধন বাকি আছে।"
    ),
}

CLAUSES = [
    Clause(id="C1", title="Room rent sub-limit", text="Room rent and boarding charges are payable up to 1% of the Sum Insured per day. Any amount above this cap is not payable."),
    Clause(id="C2", title="ICU sub-limit", text="ICU charges are payable at actuals up to 2% of the Sum Insured per day, subject to pre-authorisation."),
    Clause(id="C3", title="Consumables exclusion", text="Consumables such as gloves, syringes, surgical dressings, bandages, and non-medical items are excluded from coverage."),
    Clause(id="C4", title="Cosmetic exclusion", text="Cosmetic or aesthetic procedures are excluded unless medically necessary due to an accident and certified by the treating doctor."),
    Clause(id="C5", title="Accident cover", text="Accidental injury is covered from day one. Illness-related hospitalisation is subject to a 30-day waiting period."),
    Clause(id="C6", title="Non-network co-pay", text="A co-payment of 10% applies to the admissible claim amount at non-network hospitals."),
    Clause(id="C7", title="Pre-authorisation", text="Planned hospitalisation requires pre-authorisation at least 48 hours before admission. Emergency admissions must be notified to the insurer within 24 hours."),
    Clause(id="C8", title="Claim documents", text="Discharge summary, itemised hospital bill, pharmacy prescription, and government ID are required for claim submission."),
    Clause(id="C9", title="Pharmacy charges", text="Pharmacy charges are payable when prescribed by the treating doctor as part of the same hospitalisation."),
]


def policy(source_file: str = "policy.pdf") -> PolicyFields:
    return PolicyFields(
        policy_number="BSG-HS-2025-88421",
        insurer="Bharat Suraksha General Insurance",
        insured_name="Sunita Sharma",
        sum_insured=500000,
        policy_start_date="2025-04-01",
        policy_end_date="2026-03-31",
        clauses=CLAUSES,
        confidence=0.94,
        source_file=source_file,
    )


BILL_LINES = [
    LineItem(id="B1", description="Room rent (private room), 4 days x ₹7,500", amount=30000),
    LineItem(id="B2", description="ICU charges, 2 days x ₹9,000", amount=18000),
    LineItem(id="B3", description="Surgeon fees - ORIF right wrist", amount=45000),
    LineItem(id="B4", description="Anaesthesia charges", amount=8000),
    LineItem(id="B5", description="Medicines and IV fluids", amount=22500),
    LineItem(id="B6", description="Diagnostics - X-ray, CT scan, blood tests", amount=12000),
    LineItem(id="B7", description="Physiotherapy sessions", amount=6000),
    LineItem(id="B8", description="Consumables - gloves, dressings, surgical items", amount=7500),
    LineItem(id="B9", description="Pharmacy - painkillers and antibiotics", amount=3200),
    LineItem(id="B10", description="Pharmacy - calcium and vitamin D supplements", amount=1800),
    LineItem(id="B11", description="Pharmacy - bandage and crepe roll", amount=700),
]


def bill(source_file: str = "bill_printed.png") -> BillFields:
    return BillFields(
        patient_name="Sunita Sharma",
        hospital_name="CityCare Multispeciality Hospital, Jaipur",
        admission_date="2026-10-24",
        discharge_date="2026-10-27",
        bill_number="CC-2026-10427",
        line_items=BILL_LINES,
        total_amount=154700,
        confidence=0.81,
        source_file=source_file,
        warnings=["Handwritten pharmacy bill matched with lower confidence."],
    )


def analysis(language: str = "hi-IN") -> AnalysisResponse:
    verdicts = [
        Verdict(line_id="B1", line_description="Room rent (private room), 4 days x ₹7,500", amount=30000, verdict="partially_covered", covered_amount=20000, confidence=0.96, clause_id="C1", clause_text=CLAUSES[0].text, reasoning="The 1% daily cap is ₹5,000. For 4 days the payable room rent is ₹20,000, so ₹10,000 is above the sub-limit."),
        Verdict(line_id="B2", line_description="ICU charges, 2 days x ₹9,000", amount=18000, verdict="covered", covered_amount=18000, confidence=0.93, clause_id="C2", clause_text=CLAUSES[1].text, reasoning="ICU cost is within the 2% daily cap of ₹10,000 per day for 2 days."),
        Verdict(line_id="B3", line_description="Surgeon fees - ORIF right wrist", amount=45000, verdict="covered", covered_amount=45000, confidence=0.95, clause_id="C5", clause_text=CLAUSES[4].text, reasoning="The surgery was required because of an accidental fracture, covered from day one."),
        Verdict(line_id="B4", line_description="Anaesthesia charges", amount=8000, verdict="covered", covered_amount=8000, confidence=0.9, clause_id="C5", clause_text=CLAUSES[4].text, reasoning="Anaesthesia is part of the accident-related surgical treatment."),
        Verdict(line_id="B5", line_description="Medicines and IV fluids", amount=22500, verdict="covered", covered_amount=22500, confidence=0.88, clause_id="C5", clause_text=CLAUSES[4].text, reasoning="In-patient medicines are part of the accident treatment."),
        Verdict(line_id="B6", line_description="Diagnostics - X-ray, CT scan, blood tests", amount=12000, verdict="covered", covered_amount=12000, confidence=0.92, clause_id="C5", clause_text=CLAUSES[4].text, reasoning="Diagnostics were required to diagnose and treat the fracture."),
        Verdict(line_id="B7", line_description="Physiotherapy sessions", amount=6000, verdict="covered", covered_amount=6000, confidence=0.84, clause_id="C5", clause_text=CLAUSES[4].text, reasoning="Post-operative physiotherapy is part of the accident recovery."),
        Verdict(line_id="B8", line_description="Consumables - gloves, dressings, surgical items", amount=7500, verdict="not_covered", covered_amount=0, confidence=0.97, clause_id="C3", clause_text=CLAUSES[2].text, reasoning="The policy explicitly excludes gloves, dressings, bandages, and non-medical consumables."),
        Verdict(line_id="B9", line_description="Pharmacy - painkillers and antibiotics", amount=3200, verdict="covered", covered_amount=3200, confidence=0.86, clause_id="C9", clause_text=CLAUSES[8].text, reasoning="Prescribed pharmacy items used during the same hospitalisation are payable."),
        Verdict(line_id="B10", line_description="Pharmacy - calcium and vitamin D supplements", amount=1800, verdict="unclear", covered_amount=0, confidence=0.52, clause_id="C9", clause_text=CLAUSES[8].text, reasoning="Coverage depends on a doctor's prescription, which has not been uploaded."),
        Verdict(line_id="B11", line_description="Pharmacy - bandage and crepe roll", amount=700, verdict="not_covered", covered_amount=0, confidence=0.9, clause_id="C3", clause_text=CLAUSES[2].text, reasoning="Bandages and dressings are listed as excluded consumables."),
    ]
    gaps = [
        Gap(id="G1", title="Discharge summary is missing", detail="Clause C8 requires a discharge summary for every claim. The narration also says the hospital has not issued it yet.", severity="high", action="Request the discharge summary and final itemised bill from the hospital medical records desk."),
        Gap(id="G2", title="Pre-authorisation not obtained", detail="Clause C7 requires emergency admissions to be notified within 24 hours. The narration says no pre-authorisation was taken.", severity="high", action="Contact the insurer/TPA helpline now, share the admission details, and ask for late-notification guidance."),
        Gap(id="G3", title="Patient name mismatch", detail="The policy names 'Sunita Sharma', while the handwritten pharmacy bill says 'Sunita S.'.", severity="medium", action="Ask the pharmacy for a corrected bill in the full name, or attach an identity proof linking both names."),
        Gap(id="G4", title="Pharmacy prescription is missing", detail="Clause C9 covers pharmacy charges only when prescribed. The calcium and vitamin D items are therefore unclear.", severity="medium", action="Upload the doctor's prescription for all pharmacy purchases."),
        Gap(id="G5", title="Government ID proof not uploaded", detail="Clause C8 lists government ID as a required claim document.", severity="low", action="Attach Aadhaar, PAN, or passport with the name matching the policy."),
    ]
    return AnalysisResponse(
        facts=Facts(
            patient_name="Sunita Sharma",
            hospital_name="CityCare Multispeciality Hospital, Jaipur",
            incident_date="2026-10-24",
            claim_type="Accident - fractured right wrist",
            summary="Sunita Sharma, 54, fell down the stairs on 24 October 2026 and fractured her right wrist. She was admitted to CityCare Hospital the same night, operated on, and discharged on 27 October 2026.",
        ),
        verdicts=verdicts,
        gaps=gaps,
        totals=Totals(billed=154700, admissible=134700, copay_percent=10, copay_amount=13470, covered=121230, patient_pay=33470),
        summary=(
            "This is a valid accident claim, but it is not fully payable as submitted. Room rent exceeds the 1% daily cap by ₹10,000, "
            "consumables and dressings are excluded, and a 10% non-network co-pay applies. Two high-priority documents are missing "
            "(discharge summary and pre-authorisation), and the pharmacy bill has a name mismatch. Fix these before submitting."
        ),
        mode="mock",
        disclaimer=DISCLAIMER,
    )
