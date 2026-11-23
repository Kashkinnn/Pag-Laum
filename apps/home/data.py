"""Curated static crisis hotlines, episode guides, and psychiatric center locations for Pag-Laum."""

CRISIS_HOTLINES = [
    {
        "id": "ncmh-1553",
        "name": "National Center for Mental Health (NCMH) Crisis Hotline",
        "region": "National 24/7",
        "category": "Mental Health Crisis",
        "availability": "24/7",
        "is_featured": True,
        "description": (
            "Free, confidential crisis counseling and mental health support across the Philippines, "
            "available day and night."
        ),
        "numbers": [
            {"label": "Luzon-Wide Landline (Toll-Free)", "phone": "1553", "dial": "1553"},
            {"label": "Globe / TM", "phone": "0917-899-8727", "dial": "+639178998727"},
            {"label": "Globe / TM Alt", "phone": "0966-351-4518", "dial": "+639663514518"},
            {"label": "Smart / Sun / TNT", "phone": "0908-639-2672", "dial": "+639086392672"},
        ],
    },
    {
        "id": "tawag-paglaum",
        "name": "Tawag Paglaum — Centro Bisaya",
        "region": "Visayas / Cebu",
        "category": "Suicide Prevention & Emotional Support",
        "availability": "24/7",
        "is_featured": True,
        "description": (
            "Visayas-focused emotional crisis intervention and suicide prevention hotline offering "
            "support in Bisaya, Tagalog, and English."
        ),
        "numbers": [
            {"label": "Smart / TNT", "phone": "0939-937-5433", "dial": "+639399375433"},
            {"label": "Smart / TNT Alt", "phone": "0939-936-5433", "dial": "+639399365433"},
            {"label": "Globe / TM", "phone": "0927-654-1629", "dial": "+639276541629"},
        ],
    },
    {
        "id": "hopeline-ph",
        "name": "Hopeline Philippines (Natasha Goulbourn Foundation)",
        "region": "National 24/7",
        "category": "Crisis & Suicide Prevention",
        "availability": "24/7",
        "is_featured": True,
        "description": (
            "Confidential phone-based counseling for individuals experiencing depression, overwhelming "
            "stress, or suicidal thoughts."
        ),
        "numbers": [
            {"label": "Landline", "phone": "(02) 8804-4673", "dial": "+63288044673"},
            {"label": "Globe / TM", "phone": "0917-558-4673", "dial": "+639175584673"},
            {"label": "Smart / TNT", "phone": "0918-873-4673", "dial": "+639188734673"},
        ],
    },
    {
        "id": "in-touch",
        "name": "In Touch Community Services Crisis Line",
        "region": "National 24/7",
        "category": "Emotional Crisis Counseling",
        "availability": "24/7",
        "is_featured": False,
        "description": (
            "Free, anonymous, and confidential emotional support staffed by trained volunteers for "
            "urgent mental distress."
        ),
        "numbers": [
            {"label": "Landline", "phone": "(02) 8893-7603", "dial": "+63288937603"},
            {"label": "Globe / TM", "phone": "0917-800-1123", "dial": "+639178001123"},
            {"label": "Smart / Sun", "phone": "0922-893-8944", "dial": "+639228938944"},
        ],
    },
    {
        "id": "vsmmc-cbs",
        "name": "VSMMC Center for Behavioral Sciences",
        "region": "Visayas / Cebu",
        "category": "Psychiatric Triage & Referral",
        "availability": "24/7 Emergency / Clinic Hours",
        "is_featured": False,
        "description": (
            "Direct hospital line for psychiatric emergency triage, consultation schedules, and "
            "in-patient psychiatric care in Cebu City."
        ),
        "numbers": [
            {"label": "Hospital Trunkline", "phone": "(032) 253-9891", "dial": "+63322539891"},
            {"label": "Behavioral Sciences Mobile", "phone": "0922-826-1025", "dial": "+639228261025"},
        ],
    },
    {
        "id": "manila-lifeline",
        "name": "Manila Lifeline Centre",
        "region": "Metro Manila",
        "category": "Counseling & Referral",
        "availability": "24/7",
        "is_featured": False,
        "description": (
            "Listening support and referral assistance for Metro Manila residents experiencing acute "
            "emotional crises or panic episodes."
        ),
        "numbers": [
            {"label": "Landline", "phone": "(02) 8969-1100", "dial": "+63289691100"},
            {"label": "Mobile", "phone": "0917-854-9191", "dial": "+639178549191"},
        ],
    },
    {
        "id": "emergency-911",
        "name": "Philippine National Emergency Hotline",
        "region": "Emergency",
        "category": "Immediate Life-Safety Emergency",
        "availability": "24/7",
        "is_featured": True,
        "description": (
            "Call immediately if there is an active physical injury, medical emergency, or immediate "
            "danger to life requiring emergency dispatch."
        ),
        "numbers": [
            {"label": "National Emergency", "phone": "911", "dial": "911"},
        ],
    },
]

EPISODE_GUIDES = [
    {
        "id": "panic-attack",
        "title": "Panic Attack & Acute Anxiety",
        "category": "Anxiety",
        "urgency": "Immediate Calm",
        "duration": "3–5 mins",
        "summary": (
            "When your heart races, chest tightens, or breathing feels shallow, your nervous system "
            "is in a temporary alarm state. These steps help signal safety to your body."
        ),
        "steps": [
            {
                "title": "Pause and plant your feet",
                "detail": "Sit down if you can. Press both feet flat against the floor and notice the solid surface supporting your weight.",
            },
            {
                "title": "Lengthen your exhale",
                "detail": "Breathe in gently through your nose for 4 seconds, pause for 2 seconds, and breathe out slowly through pursed lips for 6 seconds.",
            },
            {
                "title": "Drop your shoulders & unclench your jaw",
                "detail": "Let your shoulders fall away from your ears and rest your tongue gently on the roof of your mouth.",
            },
            {
                "title": "Use cool water or temperature contrast",
                "detail": "Splash cool water on your face or hold a cold glass in your hands to trigger your body's natural calming reflex.",
            },
            {
                "title": "Remind yourself it will pass",
                "detail": "Tell yourself: 'This feeling is uncomfortable, not dangerous. Panic peaks and fades within minutes.'",
            },
        ],
        "reassurance": "You are safe right now. Take one slow breath at a time.",
    },
    {
        "id": "sensory-grounding",
        "title": "5-4-3-2-1 Sensory Grounding",
        "category": "Grounding",
        "urgency": "Reset Focus",
        "duration": "2–4 mins",
        "summary": (
            "Pull your mind out of spiraling thoughts, flashbacks, or dissociation by naming real, "
            "neutral things around you right now."
        ),
        "steps": [
            {
                "title": "Notice 5 things you can see",
                "detail": "Look slowly around the room and name five shapes, colors, or ordinary objects (like a chair, window, or wall texture).",
            },
            {
                "title": "Notice 4 things you can physically feel",
                "detail": "Touch the fabric of your shirt, the cool surface of a desk, your hair, or the floor beneath your shoes.",
            },
            {
                "title": "Notice 3 things you can hear",
                "detail": "Listen for subtle ambient sounds—an electric fan, distant traffic, birds outside, or your own breathing.",
            },
            {
                "title": "Notice 2 things you can smell",
                "detail": "Notice soap, clean air, coffee, or a comforting scent nearby. Move closer to something fresh if needed.",
            },
            {
                "title": "Notice 1 steady truth or taste",
                "detail": "Take a sip of water or say aloud one calm truth: 'I am here in this room, and I am taking care of myself.'",
            },
        ],
        "reassurance": "Your senses bring you back to the present moment where you can take the next small step.",
    },
    {
        "id": "dark-thoughts",
        "title": "Overwhelming Dark Thoughts & Crisis De-escalation",
        "category": "Crisis Safety",
        "urgency": "Urgent Safety",
        "duration": "Immediate",
        "summary": (
            "When thoughts feel unbearable or unsafe, focus purely on getting through the next 15 minutes "
            "and putting distance between yourself and anything harmful."
        ),
        "steps": [
            {
                "title": "Create immediate physical distance",
                "detail": "Move away from any sharp objects, medications, balconies, or items you could use to hurt yourself. Go to a well-lit shared room if possible.",
            },
            {
                "title": "Do not stay completely alone with the thought",
                "detail": "Call a crisis hotline (1553 or 0939-937-5433) or message a trusted friend or relative and say: 'I'm having a hard time and need company.'",
            },
            {
                "title": "Delay major decisions for 24 hours",
                "detail": "Make a gentle deal with yourself to hold on just for the next hour. Intense emotional storms shift when given time and support.",
            },
            {
                "title": "Focus on one physical anchor",
                "detail": "Drink a glass of water, wrap yourself in a blanket, or sit near another person even if you don't feel ready to explain everything.",
            },
            {
                "title": "Go to the nearest emergency psychiatric center if unsafe",
                "detail": "Use the Psychiatric Centers Map in Pag-Laum to locate the nearest 24/7 behavioral health emergency room or dial 911.",
            },
        ],
        "reassurance": "Your life has value, even when pain makes everything feel heavy. Help is ready to listen without judgment.",
    },
    {
        "id": "depressive-episode",
        "title": "Depressive Episode & Heavy Low Energy",
        "category": "Low Mood",
        "urgency": "Gentle Care",
        "duration": "5–10 mins",
        "summary": (
            "During deep sadness or numbness, even tiny tasks can feel exhausting. Shrink expectations "
            "down to gentle, compassionate micro-steps."
        ),
        "steps": [
            {
                "title": "Lower the bar to one tiny action",
                "detail": "Forget the full to-do list. Pick just one micro-care step: sitting up in bed, opening a curtain, or drinking half a glass of water.",
            },
            {
                "title": "Nourish without pressure",
                "detail": "If cooking feels impossible, eat something simple like crackers, fruit, bread, or warm soup—any nourishment counts.",
            },
            {
                "title": "Get 2 minutes of natural light or fresh air",
                "detail": "Stand near an open window or step outside briefly. Natural light helps gently regulate mood and sleep signals.",
            },
            {
                "title": "Silence harsh self-criticism",
                "detail": "Speak to yourself the way you would to a tired friend: 'I'm carrying a lot right now, and resting is not laziness.'",
            },
            {
                "title": "Send a low-effort check-in",
                "detail": "Text someone safe even a single message like 'Low energy today, just checking in' so you stay gently connected.",
            },
        ],
        "reassurance": "Doing one small thing today is more than enough.",
    },
    {
        "id": "helping-someone",
        "title": "Helping Someone Experiencing an Episode",
        "category": "Caregiver Guide",
        "urgency": "Supportive Action",
        "duration": "Ongoing",
        "summary": (
            "If a friend, classmate, or family member is panicking or in distress, your calm presence "
            "matters far more than having perfect answers."
        ),
        "steps": [
            {
                "title": "Stay calm and speak softly",
                "detail": "Use a warm, steady tone and simple sentences. Avoid crowding them or raising your voice.",
            },
            {
                "title": "Validate without arguing or minimizing",
                "detail": "Say: 'I'm right here with you. You don't have to rush.' Avoid phrases like 'Just calm down' or 'Others have it worse.'",
            },
            {
                "title": "Ask what feels helpful right now",
                "detail": "Offer concrete choices: 'Would you like water, a quieter space, or for me to breathe slowly with you?'",
            },
            {
                "title": "Assess immediate safety gently",
                "detail": "If they mention wanting to harm themselves, stay with them, keep hazardous items away, and call a crisis hotline together.",
            },
            {
                "title": "Connect to professional support",
                "detail": "Help them dial a 24/7 hotline or accompany them to the nearest psychiatric emergency unit using the Pag-Laum Centers Map.",
            },
        ],
        "reassurance": "Sitting beside someone in the dark is one of the most powerful acts of care.",
    },
]

PSYCHIATRIC_CENTERS = [
    {
        "id": "vsmmc-cbs",
        "name": "Vicente Sotto Memorial Medical Center — Center for Behavioral Sciences",
        "city": "Cebu City",
        "region": "Visayas / Cebu",
        "address": "B. Rodriguez St, Sambag II, Cebu City, 6000 Cebu",
        "phone": "(032) 253-9891",
        "dial": "+63322539891",
        "hours": "24/7 Psychiatric Emergency & Outpatient Mon–Fri (8:00 AM – 4:00 PM)",
        "services": ["24/7 Emergency Triage", "Outpatient Psychiatry", "In-patient Care", "Crisis Counseling"],
        "lat": 10.3075,
        "lng": 123.8919,
        "emergency_available": True,
    },
    {
        "id": "cduh-psych",
        "name": "Cebu Doctors' University Hospital — Behavioral Sciences",
        "city": "Cebu City",
        "region": "Visayas / Cebu",
        "address": "Osmeña Blvd, Capitol Site, Cebu City, 6000 Cebu",
        "phone": "(032) 255-5555",
        "dial": "+63322555555",
        "hours": "24/7 Emergency Department & Scheduled Psychiatric Consultations",
        "services": ["Emergency Evaluation", "Psychiatric Consultation", "Psychological Assessment"],
        "lat": 10.3143,
        "lng": 123.8924,
        "emergency_available": True,
    },
    {
        "id": "chong-hua-mh",
        "name": "Chong Hua Hospital — Mental Health & Psychiatry Unit",
        "city": "Cebu City",
        "region": "Visayas / Cebu",
        "address": "Don Mariano Cui St, Fuente Osmeña, Cebu City, 6000 Cebu",
        "phone": "(032) 255-8000",
        "dial": "+63322558000",
        "hours": "24/7 ER Support & Daily Outpatient Clinics",
        "services": ["24/7 Emergency Support", "Adult & Adolescent Psychiatry", "Therapy Referrals"],
        "lat": 10.3114,
        "lng": 123.8915,
        "emergency_available": True,
    },
    {
        "id": "ncmh-mandaluyong",
        "name": "National Center for Mental Health (NCMH)",
        "city": "Mandaluyong City",
        "region": "Metro Manila",
        "address": "Nueve de Pebrero St, Mauway, Mandaluyong, 1553 Metro Manila",
        "phone": "(02) 8531-9001",
        "dial": "+63285319001",
        "hours": "24/7 Acute Crisis & Emergency Services",
        "services": ["24/7 Psychiatric ER", "In-patient & Outpatient", "Crisis Intervention", "Pharmacy"],
        "lat": 14.5818,
        "lng": 121.0442,
        "emergency_available": True,
    },
    {
        "id": "pgh-psychiatry",
        "name": "UP–Philippine General Hospital — Psychiatry & Behavioral Medicine",
        "city": "Manila",
        "region": "Metro Manila",
        "address": "Taft Ave, Ermita, Manila, 1000 Metro Manila",
        "phone": "(02) 8554-8400",
        "dial": "+63285548400",
        "hours": "24/7 Emergency Room & Outpatient Psychiatry Clinics",
        "services": ["24/7 ER Psychiatry", "Outpatient Consultations", "Child & Adolescent Care"],
        "lat": 14.5778,
        "lng": 120.9857,
        "emergency_available": True,
    },
    {
        "id": "wvmc-iloilo",
        "name": "Western Visayas Medical Center — Psychiatry Department",
        "city": "Iloilo City",
        "region": "Visayas / Cebu",
        "address": "Q. Abeto St, Mandurriao, Iloilo City, 5000 Iloilo",
        "phone": "(033) 321-2841",
        "dial": "+63333212841",
        "hours": "24/7 Emergency Triage & Weekday Outpatient Clinics",
        "services": ["Emergency Triage", "Outpatient Psychiatry", "Community Mental Health"],
        "lat": 10.7155,
        "lng": 122.5484,
        "emergency_available": True,
    },
    {
        "id": "spmc-ipbm-davao",
        "name": "SPMC — Institute of Psychiatry and Behavioral Medicine (IPBM)",
        "city": "Davao City",
        "region": "Mindanao",
        "address": "J.P. Laurel Ave, Bajada, Davao City, 8000 Davao del Sur",
        "phone": "(082) 227-2731",
        "dial": "+63822272731",
        "hours": "24/7 Psychiatric Emergency & Outpatient Services",
        "services": ["24/7 Crisis Stabilization", "In-patient & Outpatient", "Counseling"],
        "lat": 7.0983,
        "lng": 125.6197,
        "emergency_available": True,
    },
]

# Maps each CrisisHotline slug to its receiving PsychiatricCenter slug (One-to-Many relationship).
HOTLINE_CENTER_REFERRALS = {
    "ncmh-1553": "ncmh-mandaluyong",
    "hopeline-ph": "ncmh-mandaluyong",
    "tawag-paglaum": "vsmmc-cbs",
    "vsmmc-cbs": "vsmmc-cbs",
    "in-touch": "pgh-psychiatry",
    "manila-lifeline": "pgh-psychiatry",
    "emergency-911": "spmc-ipbm-davao",
}
