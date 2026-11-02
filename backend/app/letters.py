from .models import ClaimForm

NOTE = {
    "hi-IN": "नोट: यह पत्र Claim-It द्वारा तैयार एक सहायक ड्राफ्ट है। यह कानूनी या वित्तीय सलाह नहीं है। कृपया सभी विवरण अपनी बीमा कंपनी से जाँच लें।",
    "ta-IN": "குறிப்பு: இந்த கடிதம் Claim-It மூலம் தயாரிக்கப்பட்ட உதவி வரைவு. இது சட்ட அல்லது நிதி ஆலோசனை அல்ல. அனைத்து விவரங்களையும் உங்கள் காப்பீட்டு நிறுவனத்திடம் சரிபார்க்கவும்.",
    "te-IN": "గమనిక: ఈ లేఖ Claim-It ద్వారా తయారు చేసిన సహాయక ముసాయిదా. ఇది చట్టపరమైన లేదా ఆర్థిక సలహా కాదు. అన్ని వివరాలను మీ బీమా సంస్థతో నిర్ధారించుకోండి.",
    "bn-IN": "নোট: এই চিঠিটি Claim-It দ্বারা তৈরি একটি সহায়ক খসড়া। এটি আইনি বা আর্থিক পরামর্শ নয়। সমস্ত তথ্য আপনার বিমা সংস্থার সাথে যাচাই করুন।",
    "en-IN": "Note: This letter is an assistive draft prepared by Claim-It. It is not legal or financial advice. Verify every detail with your insurer.",
}


def _amount(value: float) -> str:
    return f"{value:,.0f}"


def draft_letter(language: str, form: ClaimForm) -> str:
    lang = language if language in NOTE else "en-IN"
    a = _amount(form.claim_amount)
    if lang == "hi-IN":
        body = f"""सेवा में,
दावा विभाग,
{form.insurer}

विषय: पॉलिसी {form.policy_number} के अंतर्गत स्वास्थ्य बीमा दावा

महोदय/महोदया,

मैं, {form.patient_name}, पॉलिसी {form.policy_number} के अंतर्गत {form.hospital_name} में {form.admission_date} से {form.discharge_date} तक हुए अस्पताल में भर्ती होने का दावा प्रस्तुत कर रहा/रही हूँ। कुल दावा राशि ₹{a} है।

यह भर्ती एक दुर्घटना के कारण हुई थी। मैंने अस्पताल का आइटम-वाइज बिल, फार्मेसी बिल, पॉलिसी की प्रति और पहचान पत्र संलग्न किया है। कृपया दावे को संसाधित करें और यदि कोई अतिरिक्त दस्तावेज़ चाहिए तो मुझे सूचित करें।

भवदीय,
{form.patient_name}
{form.phone}
{form.address}

{NOTE[lang]}"""
    elif lang == "ta-IN":
        body = f"""பெறுநர்:
க்ளெயிம் துறை,
{form.insurer}

பொருள்: பாலிசி {form.policy_number} கீழ் சுகாதார காப்பீட்டு க்ளெயிம்

அன்புள்ள ஐயா/மேடம்,

நான், {form.patient_name}, பாலிசி {form.policy_number} கீழ் {form.hospital_name} மருத்துவமனையில் {form.admission_date} முதல் {form.discharge_date} வரை அனுமதிக்கப்பட்ட சிகிச்சைக்கான க்ளெயிமை சமர்ப்பிக்கிறேன். மொத்த க்ளெயிம் தொகை ₹{a}.

இந்த அனுமதி ஒரு விபத்தின் காரணமாக ஏற்பட்டது. மருத்துவமனையின் பொருள் வாரியான பில், மருந்தக பில், பாலிசி நகல் மற்றும் அடையாள சான்று இணைக்கப்பட்டுள்ளன. தயவுசெய்து க்ளெயிமை பரிசீலித்து, கூடுதல் ஆவணங்கள் தேவைப்பட்டால் எனக்கு தெரிவிக்கவும்.

இப்படிக்கு,
{form.patient_name}
{form.phone}
{form.address}

{NOTE[lang]}"""
    elif lang == "te-IN":
        body = f"""సేవలో,
క్లెయిమ్ విభాగం,
{form.insurer}

విషయం: పాలసీ {form.policy_number} కింద ఆరోగ్య బీమా క్లెయిమ్

గౌరవనీయులకు,

నేను, {form.patient_name}, పాలసీ {form.policy_number} కింద {form.hospital_name} ఆసుపత్రిలో {form.admission_date} నుండి {form.discharge_date} వరకు చేరిన చికిత్సకు క్లెయిమ్ సమర్పిస్తున్నాను. మొత్తం క్లెయిమ్ మొత్తం ₹{a}.

ఈ ఆసుపత్రి చేరిక ప్రమాదం కారణంగా జరిగింది. ఆసుపత్రి అంశాల వారీ బిల్లు, ఫార్మసీ బిల్లులు, పాలసీ ప్రతి మరియు గుర్తింపు పత్రం జత చేయబడ్డాయి. దయచేసి క్లెయిమ్‌ను పరిశీలించి, అదనపు పత్రాలు అవసరమైతే నాకు తెలియజేయండి.

భవదీయులు,
{form.patient_name}
{form.phone}
{form.address}

{NOTE[lang]}"""
    elif lang == "bn-IN":
        body = f"""প্রেরক:
দাবি বিভাগ,
{form.insurer}

বিষয়: পলিসি {form.policy_number} এর অধীনে স্বাস্থ্য বিমা দাবি

মহোদয়/মহোদয়া,

আমি, {form.patient_name}, পলিসি {form.policy_number} এর অধীনে {form.hospital_name} হাসপাতালে {form.admission_date} থেকে {form.discharge_date} পর্যন্ত ভর্তি থাকার দাবি পেশ করছি। মোট দাবির পরিমাণ ₹{a}।

এই ভর্তি একটি দুর্ঘটনার কারণে হয়েছিল। হাসপাতালের আইটেম-ভিত্তিক বিল, ফার্মেসি বিল, পলিসির কপি এবং পরিচয়পত্র সংযুক্ত করেছি। অনুগ্রহ করে দাবিটি প্রক্রিয়া করুন এবং অতিরিক্ত নথি প্রয়োজন হলে আমাকে জানান।

বিনীত,
{form.patient_name}
{form.phone}
{form.address}

{NOTE[lang]}"""
    else:
        body = f"""To,
The Claims Department,
{form.insurer}

Subject: Health insurance claim under policy {form.policy_number}

Dear Sir/Madam,

I, {form.patient_name}, am submitting a claim for hospitalisation at {form.hospital_name} from {form.admission_date} to {form.discharge_date} under policy {form.policy_number}. The total amount claimed is Rs. {a}.

The hospitalisation was due to an accident. I have attached the itemised hospital bill, pharmacy bills, policy copy, and identity proof. Please process the claim and let me know if any further documents are required.

Yours sincerely,
{form.patient_name}
{form.phone}
{form.address}

{NOTE[lang]}"""
    return body
