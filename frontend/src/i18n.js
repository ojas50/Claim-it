export const LANGUAGES = [
  { code: "hi-IN", label: "हिन्दी", english: "Hindi" },
  { code: "ta-IN", label: "தமிழ்", english: "Tamil" },
  { code: "te-IN", label: "తెలుగు", english: "Telugu" },
  { code: "bn-IN", label: "বাংলা", english: "Bengali" },
  { code: "en-IN", label: "English", english: "English" },
];

export const STEPS = ["Narrate", "Documents", "Coverage", "Claim", "Reply"];

export const SAMPLE_NARRATION = {
  "hi-IN": `मेरी माँ सुनीता शर्मा, उम्र 54 साल, 24 अक्टूबर की रात सीढ़ियों से गिर गईं। दाहिनी कलाई की हड्डी टूट गई। हम उन्हें जयपुर के CityCare अस्पताल ले गए और उसी रात भर्ती कराया। 27 अक्टूबर को छुट्टी मिली। पॉलिसी नंबर BSG-HS-2025-88421 है। सर्जरी हुई और रॉड डाली गई। बिल लगभग डेढ़ लाख रुपये का है। अस्पताल ने कहा कि पहले से मंज़ूरी नहीं ली गई, और डिस्चार्ज समरी अभी नहीं मिली है।`,
  "en-IN": `My mother Sunita Sharma, 54, fell down the stairs on the night of 24 October. She fractured her right wrist. We took her to CityCare Hospital in Jaipur and she was admitted the same night. She was discharged on 27 October. The policy number is BSG-HS-2025-88421. She had surgery and a rod was inserted. The bill is around one and a half lakh rupees. The hospital said pre-authorisation was not taken, and the discharge summary is not ready yet.`,
};

export const SPEECH_FALLBACK = {
  "hi-IN": `सुनीता जी, आपका दावा ज़्यादातर मान्य है, लेकिन पूरा नहीं। लगभग एक लाख इक्कीस हज़ार दो सौ तीस रुपये कवर हो सकते हैं। तीन चीज़ें बाकी हैं: डिस्चार्ज समरी, प्री-ऑथराइज़ेशन, और फार्मेसी बिल पर नाम सुधार। कृपया ये दस्तावेज़ अस्पताल से लेकर बीमा कंपनी को भेजें।`,
  "ta-IN": `சுனிதாவின் க்ளெய்ம் பெரும்பாலும் செல்லுபடியாகும், ஆனால் முழுமையாக திரும்பப் பெற முடியாது. சுமார் ஒரு லட்சத்து இருபத்தோரு ஆயிரத்து இருநூற்று முப்பது ரூபாய் கவர் ஆகலாம். டிஸ்சார்ஜ் சுருக்கம், முன் அனுமதி, மருந்துச் சீட்டில் பெயர் திருத்தம் ஆகியவை பாக்கி உள்ளன.`,
  "te-IN": `సునీత గారి క్లెయిమ్ ఎక్కువగా చెల్లుబాటు అవుతుంది, కానీ పూర్తిగా రాదు. సుమారు ఒక లక్ష ఇరవై ఒక్క వేల రెండు వందల ముప్పై రూపాయలు కవర్ కావచ్చు. డిశ్చార్జ్ సమ్మరీ, ముందస్తు అనుమతి, ఫార్మసీ బిల్లులో పేరు సవరణ పెండింగ్‌లో ఉన్నాయి.`,
  "bn-IN": `সুনিতার দাবি বেশিরভাগ বৈধ, তবে সম্পূর্ণ টাকা পাওয়া যাবে না। প্রায় এক লক্ষ একুশ হাজার দুইশত ত্রিশ টাকা কভার হতে পারে। ডিসচার্জ সামারি, আগাম অনুমতি এবং ফার্মেসি বিলে নাম সংশোধন বাকি আছে।`,
  "en-IN": `Sunita's claim is mostly valid, but it is not fully payable as submitted. About one lakh twenty-one thousand two hundred and thirty rupees may be covered. Three things are pending: the discharge summary, pre-authorisation, and a name correction on the pharmacy bill. Please collect these documents from the hospital and send them to the insurer.`,
};

export const VERDICT_LABELS = {
  covered: "Covered",
  partially_covered: "Partly covered",
  not_covered: "Not covered",
  unclear: "Needs review",
};

export function money(value) {
  const n = Number(value || 0);
  return `₹${n.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

export function prettyDate(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}
