"""Labeled corpus for training the Digital Arrest / financial-scam classifier.

The corpus is synthetic but modeled on real Indian 'digital arrest', KYC,
courier/parcel, and impersonation scam scripts reported to NCRB / I4C, plus
genuine call/message transcripts. It is intentionally diverse so the TF-IDF +
logistic-regression pipeline learns discriminative phrases rather than memorising.
"""

# scam_type labels for multi-class awareness
DIGITAL_ARREST = "digital_arrest"
COURIER = "courier_parcel"
KYC = "kyc_bank"
INVESTMENT = "investment"
IMPERSONATION = "govt_impersonation"
LEGIT = "legit"

# (text, is_scam, scam_type)
CORPUS = [
    # ---- Digital arrest scams (CBI/ED/Customs/Police impersonation) ----
    ("This is Inspector Sharma from CBI Mumbai. A parcel in your name contains illegal drugs and passports. You are under digital arrest. Do not disconnect this video call or hang up.", 1, DIGITAL_ARREST),
    ("Sir your Aadhaar number is linked to a money laundering case registered by ED. You must stay on this call and transfer funds to a verification account to prove your innocence.", 1, DIGITAL_ARREST),
    ("We are from Cyber Crime Branch. Your bank account is used for terror financing. Keep your camera on. You cannot tell anyone. This is a confidential digital custody.", 1, DIGITAL_ARREST),
    ("A case has been filed against you in the Supreme Court. Customs department seized a courier with your name. Pay the settlement amount now or we will send police to arrest you.", 1, DIGITAL_ARREST),
    ("You are speaking with the Narcotics Control Bureau. A FedEx parcel from you to Taiwan had 400 grams MDMA. You must join a Skype video interrogation immediately and not leave the room.", 1, DIGITAL_ARREST),
    ("I am connecting you to the arresting officer. You will be under surveillance for 24 hours. Transfer your savings to the RBI safe custody account and it will be refunded after verification.", 1, DIGITAL_ARREST),
    ("Your phone number will be blocked by TRAI in 2 hours due to illegal activity. Press 9 to talk to a police officer about the FIR against you.", 1, DIGITAL_ARREST),
    ("This is a call from the Delhi Police headquarters. Your identity was used in a human trafficking case. Do a full financial disclosure by screen sharing your net banking.", 1, DIGITAL_ARREST),
    ("Madam you are now in virtual custody. Any attempt to contact family or police is a criminal offence. Follow my instructions and download the AnyDesk application right now.", 1, DIGITAL_ARREST),
    ("The judge has issued a non-bailable warrant. To convert to bail you must deposit the security amount to the government account I share on WhatsApp within one hour.", 1, DIGITAL_ARREST),

    # ---- Courier / parcel ----
    ("This is FedEx customer care. Your parcel is held at customs and contains prohibited items. Pay a customs clearance fee to release it or face legal action.", 1, COURIER),
    ("Your DHL package to Cambodia was seized. To avoid a police case, verify your bank details and pay the penalty online now.", 1, COURIER),
    ("Blue Dart courier: illegal SIM cards found in your parcel. Press 1 to connect to Mumbai crime branch to resolve this case.", 1, COURIER),

    # ---- KYC / bank ----
    ("Dear customer your account will be suspended today. Update your KYC by clicking this link and entering your net banking password and OTP.", 1, KYC),
    ("Your SBI account is blocked. Call this number and share the OTP we sent to reactivate it immediately or lose access permanently.", 1, KYC),
    ("PAN card not updated with bank. Your account frozen. Verify Aadhaar OTP now to unfreeze, otherwise 25000 rupees penalty.", 1, KYC),
    ("This is your bank security team. We detected fraud on your card. To block it, confirm your 16 digit card number, CVV and the OTP.", 1, KYC),
    ("Congratulations your credit card reward points 9800 are expiring today. Redeem now by sharing OTP and card expiry to claim cashback.", 1, KYC),

    # ---- Investment / task ----
    ("Join our VIP telegram group for guaranteed 30 percent daily returns on crypto. Deposit 10000 and withdraw 50000 tomorrow, limited slots.", 1, INVESTMENT),
    ("Work from home part time job. Just like YouTube videos and earn 5000 daily. First recharge 2000 to activate your earning wallet.", 1, INVESTMENT),
    ("Your trading account shows 8 lakh profit. To withdraw you must first pay 12 percent income tax to this account, then funds release instantly.", 1, INVESTMENT),

    # ---- Govt impersonation / misc ----
    ("You have won 25 lakh in the KBC lottery. To claim the prize pay the GST processing fee of 18500 to this UPI id today only.", 1, IMPERSONATION),
    ("Income Tax Department: refund of 15400 pending. Verify account by entering card details on this secure link to receive the refund.", 1, IMPERSONATION),
    ("Electricity bill not paid, your power will be disconnected tonight at 9pm. Call this officer immediately and pay via the app he tells you.", 1, IMPERSONATION),
    ("Your electricity connection will be cut. Message from BSES. Contact 8XXXXXXXXX now to update meter or pay pending dues online.", 1, IMPERSONATION),

    # ---- Legit calls / messages ----
    ("Hi this is Rahul from Zomato, your order of two paneer wraps is arriving in five minutes, please share the OTP with the delivery partner at the door.", 0, LEGIT),
    ("Hello, calling from Apollo Pharmacy regarding your prescription refill, it is ready for pickup any time this week at the MG Road branch.", 0, LEGIT),
    ("Reminder from your dentist: your appointment is tomorrow at 4 pm. Reply YES to confirm or call the clinic to reschedule.", 0, LEGIT),
    ("Hi beta, it's mummy. Reached the station safely. Bring the umbrella when you come to pick me up, it looks like rain.", 0, LEGIT),
    ("This is the housing society office. Your maintenance receipt for June has been emailed. Please collect the parking sticker from the gate.", 0, LEGIT),
    ("Amazon: your order has been shipped and will be delivered by Tuesday. Track it in the app. No action needed from your side.", 0, LEGIT),
    ("Hey, are we still on for the movie at 7? I booked the tickets already, meet you at the mall food court.", 0, LEGIT),
    ("Your electricity bill of 1240 rupees is generated. Pay via the official BESCOM app or website before the 15th to avoid late fee.", 0, LEGIT),
    ("Good morning sir, this is Priya from HDFC relationship team. Just a courtesy call, no action needed, feel free to visit the branch for any query.", 0, LEGIT),
    ("Your PNR 4821 is confirmed, coach B4 seat 32, train departs New Delhi at 16:25. Have a safe journey.", 0, LEGIT),
    ("Team, the sprint review is moved to 3 pm in the main conference room. Please update your Jira tickets before then.", 0, LEGIT),
    ("Hi, this is Dr. Mehta's clinic. Your blood test reports are normal. No follow up needed. Stay hydrated.", 0, LEGIT),
    ("Swiggy: your refund of 220 for the cancelled order has been initiated to your original payment method within 5 days.", 0, LEGIT),
    ("Hello, I'm calling about the flat you listed on the portal. Is it still available for rent? Can we schedule a visit this weekend?", 0, LEGIT),
    ("Your OTP for login is 449213. Do not share it with anyone. Bank staff will never ask for this. This message is for your awareness.", 0, LEGIT),
]


def get_training_data():
    texts = [c[0] for c in CORPUS]
    labels = [c[1] for c in CORPUS]
    types = [c[2] for c in CORPUS]
    return texts, labels, types
