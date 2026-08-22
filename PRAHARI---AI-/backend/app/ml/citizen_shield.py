"""Citizen Fraud Shield — multi-channel conversational risk assessment.

A citizen (via WhatsApp / IVR / app) describes a suspicious call, message, or
payment request. The shield reuses the scam detector for the core verdict, then
wraps it in guided, plain-language advice, a reporting pathway (NCRB 1930 / I4C),
and localised advisory snippets in 12 Indian languages — tuned for a very low
false-positive rate as required by the evaluation.
"""
from __future__ import annotations

from app.ml.scam_detector import detector
from app.services import gemini

LANG_NAMES = {
    "en": "English", "hi": "Hindi", "bn": "Bengali", "te": "Telugu",
    "mr": "Marathi", "ta": "Tamil", "gu": "Gujarati", "kn": "Kannada",
    "ml": "Malayalam", "pa": "Punjabi", "or": "Odia", "as": "Assamese",
}

SHIELD_SYSTEM = (
    "You are Prahari Fraud Shield, a calm, trustworthy assistant that protects "
    "Indian citizens from digital-arrest scams, financial fraud, and phishing. "
    "You are given a message the citizen received and a verdict from a fraud-"
    "detection engine. NEVER contradict the engine's risk band. Reply in 3-4 "
    "short, plain sentences a worried non-technical person can act on. Be "
    "reassuring but direct. If risk is high, tell them clearly NOT to pay or "
    "share OTP, and to call 1930. Do not invent facts about the specific case."
)


def _ai_reply(message: str, verdict, band: str, language: str):
    """Optional Gemini-generated conversational reply grounded in the verdict."""
    if not gemini.is_enabled():
        return None
    lang = LANG_NAMES.get(language, "English")
    indicators = ", ".join(i["label"] for i in verdict.indicators) or "none detected"
    prompt = (
        f"Citizen's message: \"{message}\"\n\n"
        f"Fraud engine verdict:\n"
        f"- Risk band: {band}\n"
        f"- Risk score: {verdict.risk_score:.0%}\n"
        f"- Likely scam type: {verdict.scam_type_label}\n"
        f"- Detected indicators: {indicators}\n\n"
        f"Write your reply ENTIRELY in {lang}. Keep it to 3-4 short sentences."
    )
    return gemini.generate(prompt, system=SHIELD_SYSTEM, temperature=0.5, max_tokens=400)

# Guided safety steps by verdict band
GUIDED_STEPS = {
    "critical": [
        "STOP. Do not pay, transfer money, or share any OTP/PIN/card details.",
        "No real police, CBI, ED or court conducts arrests over a video call. 'Digital arrest' does not exist in Indian law.",
        "Disconnect the call immediately and do NOT call back the number.",
        "Call the National Cyber Crime Helpline 1930 right now to report and freeze any transaction.",
        "Tell a family member — scammers rely on isolating you.",
    ],
    "high": [
        "Do not share OTP, passwords, or card details with anyone on this call/message.",
        "Independently verify: contact the bank/agency using the number on their official website — not the number that contacted you.",
        "Do not click links or install any app (AnyDesk/TeamViewer) they ask for.",
        "If money was already sent, call 1930 within the golden hour to block it.",
    ],
    "elevated": [
        "Be cautious. Legitimate organisations never demand urgent payment or OTP over a call.",
        "Verify the sender through official channels before acting.",
        "Do not share personal or financial information.",
    ],
    "low": [
        "This looks routine, but never share OTPs or passwords with anyone.",
        "If anything feels off, verify through the organisation's official app or helpline.",
    ],
}

REPORT_PATHWAY = {
    "helpline": "1930 (National Cyber Crime Helpline)",
    "portal": "https://cybercrime.gov.in",
    "email_note": "Preserve screenshots, the caller number, and any UPI/account IDs as evidence.",
}

# Short advisory in 12 official languages (verdict-agnostic core warning).
ADVISORY_I18N = {
    "en": "Never share your OTP or PIN. No agency arrests you over a video call. Report fraud to 1930.",
    "hi": "अपना OTP या PIN कभी साझा न करें। कोई भी एजेंसी वीडियो कॉल पर गिरफ्तार नहीं करती। धोखाधड़ी की सूचना 1930 पर दें।",
    "bn": "আপনার OTP বা PIN কখনও শেয়ার করবেন না। কোনো সংস্থা ভিডিও কলে গ্রেপ্তার করে না। প্রতারণার অভিযোগ 1930-এ জানান।",
    "te": "మీ OTP లేదా PIN ఎప్పుడూ షేర్ చేయవద్దు. వీడియో కాల్‌లో ఏ సంస్థా అరెస్ట్ చేయదు. మోసాన్ని 1930కి రిపోర్ట్ చేయండి.",
    "mr": "तुमचा OTP किंवा PIN कधीही शेअर करू नका. कोणतीही संस्था व्हिडिओ कॉलवर अटक करत नाही. फसवणुकीची तक्रार 1930 वर करा.",
    "ta": "உங்கள் OTP அல்லது PIN-ஐ பகிர வேண்டாம். எந்த அமைப்பும் வீடியோ அழைப்பில் கைது செய்யாது. மோசடியை 1930-க்கு தெரிவிக்கவும்.",
    "gu": "તમારો OTP કે PIN ક્યારેય શેર ન કરો. કોઈ સંસ્થા વીડિયો કૉલ પર ધરપકડ કરતી નથી. છેતરપિંડીની ફરિયાદ 1930 પર કરો.",
    "kn": "ನಿಮ್ಮ OTP ಅಥವಾ PIN ಅನ್ನು ಹಂಚಿಕೊಳ್ಳಬೇಡಿ. ಯಾವುದೇ ಸಂಸ್ಥೆ ವಿಡಿಯೊ ಕರೆಯಲ್ಲಿ ಬಂಧಿಸುವುದಿಲ್ಲ. ವಂಚನೆಯನ್ನು 1930ಗೆ ವರದಿ ಮಾಡಿ.",
    "ml": "നിങ്ങളുടെ OTP അല്ലെങ്കിൽ PIN പങ്കിടരുത്. ഒരു ഏജൻസിയും വീഡിയോ കോളിൽ അറസ്റ്റ് ചെയ്യില്ല. തട്ടിപ്പ് 1930-ൽ റിപ്പോർട്ട് ചെയ്യുക.",
    "pa": "ਆਪਣਾ OTP ਜਾਂ PIN ਕਦੇ ਸਾਂਝਾ ਨਾ ਕਰੋ। ਕੋਈ ਏਜੰਸੀ ਵੀਡੀਓ ਕਾਲ 'ਤੇ ਗ੍ਰਿਫ਼ਤਾਰ ਨਹੀਂ ਕਰਦੀ। ਧੋਖਾਧੜੀ ਦੀ ਰਿਪੋਰਟ 1930 'ਤੇ ਕਰੋ।",
    "or": "ଆପଣଙ୍କ OTP କିମ୍ବା PIN କେବେ ଶେୟାର କରନ୍ତୁ ନାହିଁ। କୌଣସି ସଂସ୍ଥା ଭିଡିଓ କଲରେ ଗିରଫ କରେ ନାହିଁ। ଠକେଇ 1930ରେ ରିପୋର୍ଟ କରନ୍ତୁ।",
    "as": "আপোনাৰ OTP বা PIN কেতিয়াও শ্বেয়াৰ নকৰিব। কোনো সংস্থাই ভিডিঅ' কলত গ্ৰেপ্তাৰ নকৰে। প্ৰতাৰণা 1930ত অভিযোগ কৰক।",
}


def assess(message: str, language: str = "en", channel: str = "whatsapp") -> dict:
    verdict = detector.analyze(message)
    band = verdict.risk_band
    steps = GUIDED_STEPS.get(band, GUIDED_STEPS["elevated"])

    if band in ("critical", "high"):
        headline = "⚠️ HIGH FRAUD RISK — This looks like a scam."
        verdict_label = "SCAM / FRAUD LIKELY"
    elif band == "elevated":
        headline = "⚠️ Be careful — some warning signs detected."
        verdict_label = "SUSPICIOUS"
    else:
        headline = "✅ Low risk — but stay alert."
        verdict_label = "LIKELY SAFE"

    ai_reply = _ai_reply(message, verdict, band, language)

    return {
        "channel": channel,
        "verdict": verdict_label,
        "risk_score": verdict.risk_score,
        "risk_band": band,
        "scam_type": verdict.scam_type_label,
        "headline": headline,
        "why": verdict.explanation,
        "indicators": [i["label"] for i in verdict.indicators],
        "guided_steps": steps,
        "report": REPORT_PATHWAY,
        "advisory_localized": ADVISORY_I18N.get(language, ADVISORY_I18N["en"]),
        "language": language,
        "ai_reply": ai_reply,
        "ai_powered": ai_reply is not None,
        "disclaimer": "Automated guidance. When in doubt, call 1930 or visit cybercrime.gov.in.",
    }


SUPPORTED_LANGUAGES = [
    {"code": k, "name": n} for k, n in [
        ("en", "English"), ("hi", "हिन्दी"), ("bn", "বাংলা"), ("te", "తెలుగు"),
        ("mr", "मराठी"), ("ta", "தமிழ்"), ("gu", "ગુજરાતી"), ("kn", "ಕನ್ನಡ"),
        ("ml", "മലയാളം"), ("pa", "ਪੰਜਾਬੀ"), ("or", "ଓଡ଼ିଆ"), ("as", "অসমীয়া"),
    ]
]
