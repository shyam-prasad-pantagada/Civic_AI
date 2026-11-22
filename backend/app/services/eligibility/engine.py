"""Civic_AI Deterministic Scheme Eligibility Engine & Public Scheme Directory.

Evaluates citizen profiles against structured scheme eligibility rules
using pure Python logic (SPEC.md Section 3.2).
CRITICAL ARCHITECTURAL CONSTRAINT:
- ZERO LLM calls in decision making. Decisions are 100% deterministic.
- The LLM may only explain the result, never decide.
Returns: 'eligible' | 'not_eligible' | 'need_more_info' plus the exact deciding rule.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple
from app.models.schemas import CitizenProfile, SchemeMatchResult

logger = logging.getLogger("Civic_AI.EligibilityEngine")

# Comprehensive repository of Central and State Schemes with strict deterministic rules
SCHEMES_REGISTRY: List[Dict[str, Any]] = [
    # =========================================================================
    # CENTRAL GOVERNMENT SCHEMES
    # =========================================================================
    {
        "scheme_id": "PM-KISAN",
        "scheme_name": "Pradhan Mantri Kisan Samman Nidhi",
        "state": "Central",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "category": "farmer",
        "benefit_type": "Cash / DBT",
        "summary": "Direct income support of Rs 6,000 per year provided to landholding farmer families in three equal quarterly installments of Rs 2,000.",
        "benefits": [
            "Financial benefit of Rs 6,000 per year in 3 equal installments of Rs 2,000 directly into Aadhaar-seeded bank account.",
            "100% Central Government funded with automated Direct Benefit Transfer (DBT)."
        ],
        "eligibility_criteria": [
            "Applicant must be a citizen of India and an active small/marginal farmer.",
            "Family must hold cultivable landholding up to 5.0 acres.",
            "Annual family income must not exceed Rs 3,00,000."
        ],
        "exclusions": [
            "Institutional landholders.",
            "Farmer families with one or more members holding constitutional posts or serving as ministers/MPs/MLAs.",
            "Serving or retired officers and employees of Central/State Government ministries and PSEs.",
            "All persons who paid income tax in the last assessment year."
        ],
        "documents_needed": [
            "Aadhaar Card with mobile linking",
            "Land ownership documents (Khatoni / Record of Rights / 7/12 extract)",
            "Active Bank Passbook with NPCI Aadhaar seeding"
        ],
        "how_to_apply": "Register online at https://pmkisan.gov.in using 'New Farmer Registration' with Aadhaar authentication or visit the nearest Common Service Centre (CSC).",
        "official_link": "https://pmkisan.gov.in",
        "rules": {
            "category_required": "farmer",
            "max_land_holding_acres": 5.0,
            "max_income": 300000,
        },
    },
    {
        "scheme_id": "PM-JAY",
        "scheme_name": "Ayushman Bharat - PM Jan Arogya Yojana",
        "state": "Central",
        "scheme_type": "integrated",
        "applicable_states": [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
            "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
            "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
            "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
            "West Bengal", "Chandigarh", "Delhi", "Jammu and Kashmir", "Ladakh", "Puducherry"
        ],
        "state_apply_links": [
            {"state": "Maharashtra (MJPJAY)", "url": "https://www.jeevandayee.gov.in"},
            {"state": "Gujarat (PMJAY-MA)", "url": "https://pmjay.gujarat.gov.in"},
            {"state": "Karnataka (Arogya Karnataka)", "url": "https://arogya.karnataka.gov.in"},
            {"state": "Uttar Pradesh", "url": "https://ayushmanup.in"}
        ],
        "ministry": "Ministry of Health & Family Welfare / National Health Authority",
        "category": "health",
        "benefit_type": "Insurance / Healthcare",
        "summary": "Flagship health protection scheme providing cashless health coverage of up to Rs 5 Lakh per family per year for secondary and tertiary care hospitalization.",
        "benefits": [
            "Cashless health insurance cover of up to Rs 5,00,000 per family per year.",
            "Covers up to 3 days of pre-hospitalization and 15 days of post-hospitalization expenses including medicines and diagnostics.",
            "Completely portable across 28,000+ public and empanelled private hospitals nationwide."
        ],
        "eligibility_criteria": [
            "Families identified in the Socio-Economic Caste Census (SECC 2011) or registered on NFSA ration card databases.",
            "Households with annual family income up to Rs 2,50,000.",
            "No restrictions on family size, age, or gender."
        ],
        "exclusions": [
            "Government employees covered under CGHS/ECHS or corporate insurance.",
            "Families owning motorized 3/4 wheelers or mechanized agricultural equipment.",
            "Households with any income tax paying member."
        ],
        "documents_needed": [
            "Aadhaar Card of all family members",
            "Ration Card (NFSA / BPL / Antyodaya)",
            "Income Certificate or SECC confirmation"
        ],
        "how_to_apply": "Check your name online at https://pmjay.gov.in ('Am I Eligible') or visit an Ayushman Arogya Mandir / nearest empanelled hospital with Aadhaar and Ration Card to generate Ayushman Card.",
        "official_link": "https://pmjay.gov.in",
        "direct_apply_url": "https://pmjay.gov.in",
        "rules": {
            "max_income": 250000,
        },
    },
    {
        "scheme_id": "NSAP-IGNOAPS",
        "scheme_name": "Indira Gandhi National Old Age Pension Scheme",
        "state": "Central",
        "ministry": "Ministry of Rural Development",
        "category": "senior",
        "benefit_type": "Cash / DBT",
        "summary": "Monthly non-contributory social security pension for destitute senior citizens aged 60 and above living below the poverty line.",
        "benefits": [
            "Monthly central pension of Rs 200 (ages 60-79) or Rs 500 (age 80+), topped up by respective State Governments to Rs 1,000-2,500/month.",
            "Direct credit into recipient's savings account or postal bank account every month."
        ],
        "eligibility_criteria": [
            "Citizen aged 60 years or above.",
            "Must belong to a household living Below Poverty Line (BPL) with annual income <= Rs 1,00,000.",
            "Must have limited or no family financial support."
        ],
        "exclusions": [
            "Individuals receiving regular pensions from Central/State Government, Armed Forces, or EPF.",
            "Non-BPL senior citizens."
        ],
        "documents_needed": [
            "Aadhaar Card",
            "Age Proof (Birth Certificate / Voter ID / School Leaving Certificate)",
            "BPL Card or Valid Income Certificate (<= Rs 1 Lakh)",
            "Bank Passbook seeded with Aadhaar"
        ],
        "how_to_apply": "Apply through your local Block Development Office (BDO) / Municipal Ward or online via https://nsap.nic.in.",
        "official_link": "https://nsap.nic.in",
        "rules": {
            "min_age": 60,
            "max_income": 100000,
        },
    },
    {
        "scheme_id": "PM-SVANIDHI",
        "scheme_name": "PM Street Vendor's AtmaNirbhar Nidhi",
        "state": "Central",
        "ministry": "Ministry of Housing & Urban Affairs",
        "category": "entrepreneur",
        "benefit_type": "Credit / Subsidy",
        "summary": "Micro-credit loan facility providing collateral-free working capital starting at Rs 10,000 to urban street vendors, hawkers, and informal traders.",
        "benefits": [
            "Initial collateral-free working capital loan up to Rs 10,000 for 1-year tenure.",
            "Subsequent enhanced tranches up to Rs 20,000 and Rs 50,000 on timely repayments.",
            "7% interest subsidy credited directly to bank account on scheduled repayments.",
            "Cashback incentives up to Rs 100/month on digital transactions."
        ],
        "eligibility_criteria": [
            "Street vendors, hawkers, thela-walas, and small daily traders operating in urban areas.",
            "Minimum age 18 years.",
            "Possession of Certificate of Vending / ID card issued by Urban Local Body or Letter of Recommendation (LoR)."
        ],
        "exclusions": [
            "Commercial shop owners with formal registered retail outlets.",
            "Vendors operating exclusively in non-urbanized rural agricultural jurisdictions."
        ],
        "documents_needed": [
            "Aadhaar Card",
            "Voter ID / Certificate of Vending / ULB Letter of Recommendation",
            "Active Bank Account with UPI linkage"
        ],
        "how_to_apply": "Apply online at https://pmsvanidhi.mohua.gov.in or through Urban Local Body / CSC with mobile-linked Aadhaar.",
        "official_link": "https://pmsvanidhi.mohua.gov.in",
        "rules": {
            "residence_required": "urban",
            "min_age": 18,
            "occupation_required": ["vendor", "hawker", "trader", "self-employed"],
        },
    },
    {
        "scheme_id": "DISABILITY-PENSION",
        "scheme_name": "National Disability Pension Scheme (IGNDPS)",
        "state": "Central",
        "ministry": "Ministry of Social Justice and Empowerment / MoRD",
        "category": "disabled",
        "benefit_type": "Cash / DBT",
        "summary": "Social assistance monthly pension provided to individuals with severe or multiple disabilities belonging to BPL households.",
        "benefits": [
            "Monthly financial pension of Rs 300 to Rs 2,500 (varies by state top-up contribution).",
            "Assistive device subsidies and priority access to rehabilitation schemes."
        ],
        "eligibility_criteria": [
            "Age between 18 and 59 years (transfers to senior pension at 60).",
            "Certified disability percentage of 40% or higher (severe disability 80%+ receives enhanced benefits).",
            "Household annual income <= Rs 1,20,000."
        ],
        "exclusions": [
            "Disability percentage below 40%.",
            "Beneficiaries receiving regular disability pensions from formal government employer funds."
        ],
        "documents_needed": [
            "Unique Disability ID (UDID) Card / Medical Board Disability Certificate",
            "Aadhaar Card",
            "BPL Ration Card or Income Certificate",
            "Bank Passbook"
        ],
        "how_to_apply": "Apply online at https://nsap.nic.in or register on the Swavlamban UDID portal at https://swavlambancard.gov.in, or visit the District Social Welfare Office.",
        "official_link": "https://nsap.nic.in",
        "rules": {
            "min_age": 18,
            "min_disability_percentage": 40.0,
            "max_income": 120000,
        },
    },
    {
        "scheme_id": "PMMVY",
        "scheme_name": "Pradhan Mantri Matru Vandana Yojana",
        "state": "Central",
        "ministry": "Ministry of Women and Child Development",
        "category": "woman",
        "benefit_type": "Cash / DBT",
        "summary": "Direct maternity cash incentive of Rs 5,000 (first child) and Rs 6,000 (second child if girl) to compensate wage loss and ensure nutrition.",
        "benefits": [
            "Rs 5,000 in two installments for the first live birth upon ANC registration and institutional birth.",
            "Rs 6,000 in a single installment for the second live birth if the child is a girl.",
            "Promotes child immunization, maternal nutrition, and institutional delivery."
        ],
        "eligibility_criteria": [
            "Pregnant women and lactating mothers aged 19 years and above.",
            "Family annual income up to Rs 2,50,000.",
            "Holding EWS, BPL, MGNREGA job card, or PM-JAY card."
        ],
        "exclusions": [
            "Women in regular employment with Central or State Governments or Public Sector Undertakings.",
            "Women who receive similar maternity benefits under any other legal statute."
        ],
        "documents_needed": [
            "Mother's and Husband's Aadhaar Card",
            "Mother and Child Protection (MCP) Card with ANC records",
            "Child Birth Certificate (for 2nd installment)",
            "Aadhaar-seeded bank account details"
        ],
        "how_to_apply": "Apply through the local Anganwadi Centre (AWC) or online on the PMMVY Citizen Portal at https://pmmvy.wcd.gov.in.",
        "official_link": "https://pmmvy.wcd.gov.in",
        "rules": {
            "gender_required": "female",
            "min_age": 19,
            "max_income": 250000,
        },
    },
    {
        "scheme_id": "PMAY-U",
        "scheme_name": "Pradhan Mantri Awas Yojana - Urban",
        "state": "Central",
        "ministry": "Ministry of Housing & Urban Affairs",
        "category": "housing",
        "benefit_type": "Subsidy / In-Kind",
        "summary": "Affordable housing mission providing interest subsidies and direct financial assistance of up to Rs 2.67 Lakh for building or buying a pucca house in urban areas.",
        "benefits": [
            "Direct subsidy of up to Rs 2,67,000 on home loan interest under Credit Linked Subsidy Scheme (CLSS).",
            "Central assistance of Rs 1.5 Lakh per house for Beneficiary-led individual construction (BLC).",
            "Mandates female headship / co-ownership in title deed."
        ],
        "eligibility_criteria": [
            "Beneficiary family must not own a pucca house anywhere in India.",
            "EWS household (income up to Rs 3,00,000) or LIG (income Rs 3,00,001 to Rs 6,00,000).",
            "Urban resident in statutory towns as per Census 2011."
        ],
        "exclusions": [
            "Families already owning a permanent pucca house.",
            "Beneficiaries who have previously availed any central housing assistance."
        ],
        "documents_needed": [
            "Aadhaar Card of all family members",
            "Income Certificate / Salary Slip / ITR",
            "Land ownership records or property agreement in urban town",
            "Bank statement of last 6 months"
        ],
        "how_to_apply": "Apply online at https://pmaymis.gov.in or visit the nearest Common Service Centre (CSC) / Urban Local Body office.",
        "official_link": "https://pmaymis.gov.in",
        "rules": {
            "residence_required": "urban",
            "max_income": 600000,
        },
    },
    {
        "scheme_id": "SUKANYA-SAMRIDDHI",
        "scheme_name": "Sukanya Samriddhi Yojana (SSY)",
        "state": "Central",
        "ministry": "Ministry of Finance / Ministry of Women & Child Development",
        "category": "woman",
        "benefit_type": "Savings / Subsidy",
        "summary": "High-interest government-backed small savings scheme designed for the higher education and marriage fund of girl children with tax-free returns under Section 80C.",
        "benefits": [
            "Attractive sovereign-backed interest rate (currently 8.2% p.a., compounded annually).",
            "Triple tax exemption: contribution, interest earned, and maturity proceeds are 100% tax-free under Section 10(11D).",
            "Minimum deposit of just Rs 250 per financial year up to Rs 1.5 Lakh."
        ],
        "eligibility_criteria": [
            "Girl child aged 0 to 10 years at the time of account opening.",
            "Opened by legal parents or guardians (maximum 2 accounts per family, or 3 in case of twin girls)."
        ],
        "exclusions": [
            "Male child.",
            "Girls above 10 years of age at the time of opening account."
        ],
        "documents_needed": [
            "Birth Certificate of Girl Child",
            "Identity Proof of Parent/Guardian (Aadhaar / Voter ID / PAN)",
            "Address proof of Parent/Guardian",
            "Passport size photos of child and guardian"
        ],
        "how_to_apply": "Open account at any Post Office or authorized commercial bank branch (SBI, PNB, BoB, etc.) or check details at https://www.indiapost.gov.in.",
        "official_link": "https://www.indiapost.gov.in",
        "rules": {
            "gender_required": "female",
            "max_age": 10,
        },
    },
    {
        "scheme_id": "PM-MUDRA",
        "scheme_name": "Pradhan Mantri MUDRA Yojana (PMMY)",
        "state": "Central",
        "ministry": "Ministry of Finance / Department of Financial Services",
        "category": "entrepreneur",
        "benefit_type": "Credit / Loan",
        "summary": "Institutional collateral-free micro-business loans up to Rs 10-20 Lakh for non-corporate, non-farm small and micro enterprises in Shishu, Kishor, and Tarun categories.",
        "benefits": [
            "Shishu loans up to Rs 50,000 for starting micro-enterprises.",
            "Kishor loans from Rs 50,001 up to Rs 5 Lakh for expanding business.",
            "Tarun loans up to Rs 10 Lakh (extended to Rs 20 Lakh in Budget 2024 for previous borrowers).",
            "Zero collateral or processing fee for Shishu loans."
        ],
        "eligibility_criteria": [
            "Any Indian citizen aged 18 years or above with a viable non-farm business proposal in manufacturing, trading, or services.",
            "Small shopkeepers, artisans, fruit vendors, repair shops, small industries."
        ],
        "exclusions": [
            "Defaulters with existing unpaid bank loans.",
            "Corporate entities or large commercial enterprises."
        ],
        "documents_needed": [
            "Aadhaar Card / Voter ID / PAN Card",
            "Business registration / Shop & Establishment proof",
            "Bank statements for the last 6 months",
            "Quotation of machinery/items to be purchased"
        ],
        "how_to_apply": "Apply online on the Udyamimitra portal at https://www.udyamimitra.in or submit loan application to any public or private commercial bank.",
        "official_link": "https://www.mudra.org.in",
        "rules": {
            "min_age": 18,
            "occupation_required": ["entrepreneur", "vendor", "trader", "artisan", "self-employed"],
        },
    },
    {
        "scheme_id": "ATAL-PENSION",
        "scheme_name": "Atal Pension Yojana (APY)",
        "state": "Central",
        "ministry": "Ministry of Finance / PFRDA",
        "category": "worker",
        "benefit_type": "Pension / DBT",
        "summary": "Guaranteed monthly pension scheme of Rs 1,000 to Rs 5,000 for unorganized sector workers, starting at age 60 with government co-contribution.",
        "benefits": [
            "Guaranteed minimum pension of Rs 1,000, Rs 2,000, Rs 3,000, Rs 4,000, or Rs 5,000 per month from age 60 until death.",
            "Same pension amount continues to spouse upon subscriber's demise; entire corpus returned to nominee.",
            "Extremely low monthly auto-debit contributions starting at Rs 42/month."
        ],
        "eligibility_criteria": [
            "Any Indian citizen aged 18 to 40 years.",
            "Must possess an active bank account with auto-debit facility.",
            "Annual family income <= Rs 3,00,000."
        ],
        "exclusions": [
            "Any citizen who is or has been an income tax payer as per Finance Ministry rules.",
            "Persons aged 40+ years at registration."
        ],
        "documents_needed": [
            "Aadhaar Card",
            "Bank savings account with mobile number linked",
            "Nominee details"
        ],
        "how_to_apply": "Apply through your bank branch, net banking portal, or through the Protean PFRDA portal at https://www.pfrda.org.in.",
        "official_link": "https://www.npscra.nsdl.co.in/scheme-details.php",
        "rules": {
            "min_age": 18,
            "max_age": 40,
            "max_income": 300000,
        },
    },
    {
        "scheme_id": "PM-UJJWALA",
        "scheme_name": "Pradhan Mantri Ujjwala Yojana 2.0",
        "state": "Central",
        "ministry": "Ministry of Petroleum and Natural Gas",
        "category": "woman",
        "benefit_type": "In-Kind / Subsidy",
        "summary": "Free LPG cooking gas connection along with free first refill and hotplate stove provided to adult women from low-income households.",
        "benefits": [
            "100% free LPG connection with zero deposit fee.",
            "Free first 14.2 kg LPG cylinder refill and two-burner LPG stove.",
            "Direct subsidy of Rs 300 per cylinder for up to 12 refills per year."
        ],
        "eligibility_criteria": [
            "Adult woman aged 18 years or above belonging to an eligible poor household.",
            "No active LPG connection in the same household.",
            "Annual household income <= Rs 2,00,000."
        ],
        "exclusions": [
            "Households already possessing an active domestic LPG connection."
        ],
        "documents_needed": [
            "Aadhaar Card of adult female applicant and adult family members",
            "Ration Card / Family composition certificate",
            "Bank Passbook with Aadhaar seeding"
        ],
        "how_to_apply": "Apply online at https://www.pmuy.gov.in or submit application form at your nearest Indane / Bharatgas / HP Gas distributorship.",
        "official_link": "https://www.pmuy.gov.in",
        "rules": {
            "gender_required": "female",
            "min_age": 18,
            "max_income": 200000,
        },
    },
    {
        "scheme_id": "PMS-SC-ST",
        "scheme_name": "Post-Matric Scholarship for SC/ST Students",
        "state": "Central",
        "ministry": "Ministry of Social Justice & Empowerment / MoTA",
        "category": "student",
        "benefit_type": "Cash / DBT",
        "summary": "Centrally sponsored scholarship covering 100% compulsory non-refundable fees and monthly maintenance allowance for post-secondary education of SC/ST students.",
        "benefits": [
            "Complete tuition fee reimbursement directly to recognized institution.",
            "Annual academic allowance and maintenance allowance up to Rs 13,500 directly to student's bank account."
        ],
        "eligibility_criteria": [
            "Enrolled in recognized Class 11, Class 12, ITI, Diploma, Undergraduate, or Postgraduate degree courses.",
            "Must belong to Scheduled Caste (SC) or Scheduled Tribe (ST) category.",
            "Total annual family income must not exceed Rs 2,50,000."
        ],
        "exclusions": [
            "Students failing to advance or students studying corresponding stage twice.",
            "Family income exceeding Rs 2.5 Lakh per annum."
        ],
        "documents_needed": [
            "Aadhaar Card",
            "Caste Certificate issued by designated Tehsildar / Sub-Divisional Magistrate",
            "Income Certificate (<= Rs 2.5 Lakh)",
            "College Admission Fee Receipt and Previous Exam Marksheet"
        ],
        "how_to_apply": "Apply online via the National Scholarship Portal (NSP) at https://scholarships.gov.in or respective state scholarship portals.",
        "official_link": "https://scholarships.gov.in",
        "rules": {
            "category_required": "student",
            "max_income": 250000,
        },
    },

    # =========================================================================
    # STATE: MAHARASHTRA (MH)
    # =========================================================================
    {
        "scheme_id": "MH-LADKI-BAHIN",
        "scheme_name": "Mukhyamantri Majhi Ladki Bahin Yojana",
        "state": "MH",
        "ministry": "Women & Child Development Department, Maharashtra",
        "category": "woman",
        "benefit_type": "Cash / DBT",
        "summary": "Direct monthly financial support of Rs 1,500 deposited into bank accounts of eligible women aged 21-65 to ensure financial independence and nutritional support.",
        "benefits": [
            "Direct cash benefit of Rs 1,500 every month (Rs 18,000 per year) via Aadhaar-enabled DBT.",
            "Covers married, widowed, divorced, deserted, and destitute women."
        ],
        "eligibility_criteria": [
            "Female permanent resident of Maharashtra aged between 21 and 65 years.",
            "Annual combined family income must not exceed Rs 2,50,000.",
            "Aadhaar-seeded active bank savings account in Maharashtra."
        ],
        "exclusions": [
            "Family member paying Income Tax.",
            "Family member employed as a regular/permanent employee in Government or local bodies.",
            "Family owning a 4-wheeler motor vehicle (excluding tractors)."
        ],
        "documents_needed": [
            "Aadhaar Card",
            "Maharashtra Domicile Certificate / 15-year Ration Card / School Leaving Certificate",
            "Income Certificate (<= Rs 2.5 Lakh)",
            "Bank Passbook linked to Aadhaar"
        ],
        "how_to_apply": "Apply online via Nari Shakti Doot mobile app or through the official portal at https://ladkibahin.maharashtra.gov.in or at local Gram Panchayat / Anganwadi / Ward offices.",
        "official_link": "https://ladkibahin.maharashtra.gov.in",
        "rules": {
            "state_required": "MH",
            "gender_required": "female",
            "min_age": 21,
            "max_age": 65,
            "max_income": 250000,
        },
    },
    {
        "scheme_id": "MH-SHETKARI-SANMAN",
        "scheme_name": "Namo Shetkari Mahasanman Nidhi Yojana",
        "state": "MH",
        "ministry": "Department of Agriculture, Maharashtra",
        "category": "farmer",
        "benefit_type": "Cash / DBT",
        "summary": "State top-up scheme providing additional Rs 6,000 per year to farmers in Maharashtra, bringing total annual support to Rs 12,000 alongside PM-KISAN.",
        "benefits": [
            "Additional state cash grant of Rs 6,000 per year in 3 installments of Rs 2,000 directly into farmer bank accounts.",
            "Total benefit of Rs 12,000/year when paired with central PM-KISAN."
        ],
        "eligibility_criteria": [
            "Resident farmer in Maharashtra.",
            "Must be an active, verified beneficiary of PM-KISAN in Maharashtra.",
            "Landholding up to 5 acres with annual income <= Rs 3,00,000."
        ],
        "exclusions": [
            "Same exclusion criteria as PM-KISAN (taxpayers, constitutional post holders, institutional land)."
        ],
        "documents_needed": [
            "Aadhaar Card",
            "PM-KISAN Registration ID",
            "Land 7/12 extract and 8-A records",
            "Aadhaar-linked Bank Passbook"
        ],
        "how_to_apply": "Automatic enrollment for verified PM-KISAN beneficiaries in Maharashtra or check status at https://krishi.maharashtra.gov.in.",
        "official_link": "https://krishi.maharashtra.gov.in",
        "rules": {
            "state_required": "MH",
            "category_required": "farmer",
            "max_income": 300000,
            "max_land_holding_acres": 5.0,
        },
    },
    {
        "scheme_id": "MH-SANJAY-GANDHI",
        "scheme_name": "Sanjay Gandhi Niradhar Anudan Yojana",
        "state": "MH",
        "ministry": "Social Justice & Special Assistance Department, Maharashtra",
        "category": "senior",
        "benefit_type": "Cash / DBT",
        "summary": "Financial monthly pension of Rs 1,500 for destitute persons, blind, disabled, and senior citizens with no breadwinner in Maharashtra.",
        "benefits": [
            "Rs 1,500 per month for single beneficiary, or Rs 2,000 per month if family has two or more beneficiaries."
        ],
        "eligibility_criteria": [
            "Resident of Maharashtra for at least 15 years.",
            "Age 65+ or persons with 40%+ disability, destitute widows, or orphans.",
            "Annual family income <= Rs 50,000."
        ],
        "exclusions": [
            "Persons with major sons earning sufficient income to support them.",
            "Persons receiving state/central government employee pensions."
        ],
        "documents_needed": [
            "Age certificate / Birth proof",
            "Maharashtra Domicile proof (15 years)",
            "Income certificate issued by Tehsildar (<= Rs 50,000)",
            "Aadhaar Card and Bank details"
        ],
        "how_to_apply": "Apply through the local Tehsildar office or online on Aaple Sarkar portal at https://aaplesarkar.mahaonline.gov.in.",
        "official_link": "https://sjsa.maharashtra.gov.in",
        "rules": {
            "state_required": "MH",
            "min_age": 65,
            "max_income": 50000,
        },
    },

    # =========================================================================
    # STATE: KARNATAKA (KA)
    # =========================================================================
    {
        "scheme_id": "KA-GRUHA-LAKSHMI",
        "scheme_name": "Karnataka Gruha Lakshmi Scheme",
        "state": "KA",
        "ministry": "Department of Women & Child Development, Karnataka",
        "category": "woman",
        "benefit_type": "Cash / DBT",
        "summary": "Financial guarantee scheme providing Rs 2,000 every month to the woman head of every eligible household in Karnataka.",
        "benefits": [
            "Monthly cash grant of Rs 2,000 directly credited via DBT to the woman head's bank account."
        ],
        "eligibility_criteria": [
            "Woman registered as the head of family in Antyodaya, BPL, or APL ration cards in Karnataka.",
            "Permanent resident of Karnataka aged 18 years or above."
        ],
        "exclusions": [
            "Women heads or their husbands who are income tax payers or GST payers.",
            "Government employees."
        ],
        "documents_needed": [
            "Aadhaar Card of the woman head and her spouse",
            "Ration Card with woman listed as head",
            "Bank passbook seeded with Aadhaar"
        ],
        "how_to_apply": "Register at Karnataka One, Grama One, Bapuji Seva Kendra, or online on the Seva Sindhu portal at https://sevasindhu.karnataka.gov.in.",
        "official_link": "https://sevasindhu.karnataka.gov.in",
        "rules": {
            "state_required": "KA",
            "gender_required": "female",
            "min_age": 18,
        },
    },
    {
        "scheme_id": "KA-YUVA-NIDHI",
        "scheme_name": "Karnataka Yuva Nidhi Scheme",
        "state": "KA",
        "ministry": "Skill Development, Entrepreneurship and Livelihood Dept, Karnataka",
        "category": "student",
        "benefit_type": "Cash / DBT",
        "summary": "Unemployment assistance of Rs 3,000/month for degree holders and Rs 1,500/month for diploma holders who graduated in Karnataka and remain unemployed.",
        "benefits": [
            "Rs 3,000 per month for unemployed graduates.",
            "Rs 1,500 per month for unemployed diploma holders.",
            "Paid for up to 2 years or until employment/self-employment is secured."
        ],
        "eligibility_criteria": [
            "Karnataka domicile student who passed degree/diploma in the designated academic year.",
            "Unemployed for at least 180 days (6 months) post graduation.",
            "Not enrolled in higher education."
        ],
        "exclusions": [
            "Students continuing further studies.",
            "Employed in government or private sector.",
            "Recipients of apprentice stipends."
        ],
        "documents_needed": [
            "Aadhaar Card",
            "Degree / Diploma Passing Certificate and Final Marksheet",
            "Karnataka Domicile Certificate",
            "Aadhaar-seeded bank passbook"
        ],
        "how_to_apply": "Apply online on the Seva Sindhu portal at https://sevasindhugs.karnataka.gov.in or through Karnataka One centres.",
        "official_link": "https://sevasindhuservices.karnataka.gov.in",
        "rules": {
            "state_required": "KA",
            "min_age": 20,
            "max_age": 30,
        },
    },
    {
        "scheme_id": "KA-SHAKTI",
        "scheme_name": "Shakti Free Bus Travel for Women",
        "state": "KA",
        "ministry": "Transport Department, Karnataka",
        "category": "woman",
        "benefit_type": "In-Kind / Service",
        "summary": "Free public bus travel for all domicile women and girl students across Karnataka in ordinary and express KSRTC, BMTC, NWKRTC, and KKRTC buses.",
        "benefits": [
            "100% free travel across Karnataka in non-AC government buses.",
            "Saves women up to Rs 1,500-2,500 per month in transit expenses."
        ],
        "eligibility_criteria": [
            "All women, transwomen, and girl students who are residents of Karnataka.",
            "No income or age restriction."
        ],
        "exclusions": [
            "Luxury, sleeper, and AC bus services (e.g., Airavat, Flybus, Rajahamsa).",
            "Inter-state travel outside Karnataka borders."
        ],
        "documents_needed": [
            "Any Government ID with Karnataka residential address (Aadhaar / Voter ID / Driving License)"
        ],
        "how_to_apply": "Show your valid Karnataka residential ID to the bus conductor to receive a zero-fare ticket, or apply for Shakti Smart Card on https://sevasindhu.karnataka.gov.in.",
        "official_link": "https://ksrtc.karnataka.gov.in",
        "rules": {
            "state_required": "KA",
            "gender_required": "female",
        },
    },

    # =========================================================================
    # STATE: DELHI (DL)
    # =========================================================================
    {
        "scheme_id": "DL-LADLI",
        "scheme_name": "Delhi Ladli Scheme",
        "state": "DL",
        "ministry": "Department of Women & Child Development, GNCTD",
        "category": "student",
        "benefit_type": "Cash / Subsidy",
        "summary": "Financial support of Rs 11,000 at birth and milestone deposits of Rs 5,000 at Classes 1, 6, 9, 10, and 12 to promote girl child education.",
        "benefits": [
            "Rs 11,000 upon institutional birth in Delhi.",
            "Rs 5,000 at each educational milestone: Class 1, Class 6, Class 9, Class 10, Class 12.",
            "Accumulated fund with interest is paid to girl upon reaching age 18 and passing Class 10."
        ],
        "eligibility_criteria": [
            "Girl child born in Delhi with 3+ years Delhi residency proof of parents.",
            "Family annual income must not exceed Rs 1,00,000.",
            "Enrolled in a recognized school in Delhi."
        ],
        "exclusions": [
            "Family income exceeding Rs 1 Lakh per annum.",
            "Dropouts from school."
        ],
        "documents_needed": [
            "Birth Certificate of Girl Child",
            "Delhi Domicile proof (3+ years Voter ID / Electricity bill)",
            "Income Certificate (<= Rs 1 Lakh)",
            "School Admission Verification Slip"
        ],
        "how_to_apply": "Apply through the school principal or Department of Women and Child Development on the e-District Delhi portal at https://edistrict.delhigovt.nic.in.",
        "official_link": "https://wcd.delhi.gov.in",
        "rules": {
            "state_required": "DL",
            "gender_required": "female",
            "max_income": 100000,
        },
    },
    {
        "scheme_id": "DL-OLD-AGE-PENSION",
        "scheme_name": "Delhi Financial Assistance to Senior Citizens",
        "state": "DL",
        "ministry": "Department of Social Welfare, GNCTD",
        "category": "senior",
        "benefit_type": "Cash / DBT",
        "summary": "Monthly pension of Rs 2,000 (ages 60-69) and Rs 2,500 (ages 70+) provided directly to destitute and low-income senior citizens in Delhi.",
        "benefits": [
            "Rs 2,000 per month for seniors aged 60-69 years.",
            "Rs 2,500 per month for seniors aged 70 years and above.",
            "Additional Rs 500/month for SC/ST/Minority seniors."
        ],
        "eligibility_criteria": [
            "Resident of Delhi for at least 5 years preceding application.",
            "Age 60 years or above.",
            "Family annual income <= Rs 1,00,000 from all sources."
        ],
        "exclusions": [
            "Seniors receiving pension from Central Government, MCD, NDMC, or defense."
        ],
        "documents_needed": [
            "Aadhaar Card",
            "Age proof (Voter ID / Birth certificate / Passport)",
            "5-year Delhi residence proof",
            "Bank account in Delhi with Aadhaar linkage"
        ],
        "how_to_apply": "Apply online on the Delhi e-District portal at https://edistrict.delhigovt.nic.in.",
        "official_link": "https://socialwelfare.delhi.gov.in",
        "rules": {
            "state_required": "DL",
            "min_age": 60,
            "max_income": 100000,
        },
    },
    {
        "scheme_id": "DL-POWER-SUBSIDY",
        "scheme_name": "Delhi Electricity Consumption Subsidy Scheme",
        "state": "DL",
        "ministry": "Power Department, GNCTD",
        "category": "housing",
        "benefit_type": "In-Kind / Subsidy",
        "summary": "100% electricity subsidy for monthly consumption up to 200 units, and 50% subsidy (up to Rs 800) for consumption between 201 and 400 units.",
        "benefits": [
            "Zero electricity bill (100% free) for domestic households using up to 200 units per month.",
            "50% subsidy for consumption between 201 to 400 units."
        ],
        "eligibility_criteria": [
            "Domestic electricity connection in Delhi (BSES Rajdhani, BSES Yamuna, TPDDL, or NDMC).",
            "Active opt-in consent for subsidy."
        ],
        "exclusions": [
            "Commercial or industrial electricity meters.",
            "Monthly consumption exceeding 400 units."
        ],
        "documents_needed": [
            "Electricity CA (Consumer Account) Number",
            "Aadhaar Card / Mobile number"
        ],
        "how_to_apply": "Opt-in by sending 'Hi' via WhatsApp to 7011311111 or visiting the Delhi discom portals (BSES/Tata Power) or https://delhi.gov.in.",
        "official_link": "https://delhi.gov.in",
        "rules": {
            "state_required": "DL",
            "residence_required": "urban",
        },
    },

    # =========================================================================
    # STATE: UTTAR PRADESH (UP)
    # =========================================================================
    {
        "scheme_id": "UP-KANYA-SUMANGALA",
        "scheme_name": "Mukhyamantri Kanya Sumangala Yojana",
        "state": "UP",
        "ministry": "Women and Child Development Department, Uttar Pradesh",
        "category": "woman",
        "benefit_type": "Cash / DBT",
        "summary": "Monetary assistance of up to Rs 25,000 provided across six developmental milestones from girl child's birth to undergraduate admission in UP.",
        "benefits": [
            "Total financial package of Rs 25,000 (enhanced from Rs 15,000) deposited directly into bank account in 6 phases.",
            "Phase 1: Rs 5,000 at birth; Phase 2: Rs 2,000 upon vaccination; Phase 3-5: Rs 3,000-5,000 at school grades; Phase 6: Rs 7,000 on degree admission."
        ],
        "eligibility_criteria": [
            "Resident of Uttar Pradesh with valid domicile.",
            "Family annual income up to Rs 3,00,000.",
            "Maximum two girl children per family."
        ],
        "exclusions": [
            "Family income exceeding Rs 3,00,000.",
            "More than two girl children (unless second delivery is twins)."
        ],
        "documents_needed": [
            "Birth Certificate of Girl Child",
            "UP Domicile Certificate",
            "Income Certificate (<= Rs 3 Lakh)",
            "Bank Passbook seeded with Aadhaar"
        ],
        "how_to_apply": "Apply online on the official portal at https://mksy.up.gov.in or visit the Block Development Office.",
        "official_link": "https://mksy.up.gov.in",
        "rules": {
            "state_required": "UP",
            "gender_required": "female",
            "max_income": 300000,
        },
    },

    # =========================================================================
    # STATE: TAMIL NADU (TN)
    # =========================================================================
    {
        "scheme_id": "TN-PUDHUMAI-PENN",
        "scheme_name": "Moovalur Ramamirtham Ammaiyar Higher Education Scheme (Pudhumai Penn)",
        "state": "TN",
        "ministry": "Social Welfare and Women Empowerment Department, Tamil Nadu",
        "category": "student",
        "benefit_type": "Cash / DBT",
        "summary": "Monthly incentive of Rs 1,000 deposited into female students' bank accounts throughout their undergraduate degree, ITI, or diploma courses.",
        "benefits": [
            "Rs 1,000 every month directly credited via DBT until completion of degree/diploma.",
            "Drastically reduces female college drop-out rates."
        ],
        "eligibility_criteria": [
            "Girl students who studied Classes 6 to 12 in Tamil Nadu Government schools.",
            "Currently enrolled in higher education (B.A., B.Sc., B.E., MBBS, Diploma, ITI).",
            "Permanent resident of Tamil Nadu."
        ],
        "exclusions": [
            "Students who completed schooling in private un-aided schools.",
            "Distance education or non-recognized institutions."
        ],
        "documents_needed": [
            "School EMIS (Educational Management Information System) ID",
            "Aadhaar Card",
            "College Admission ID and Bonafide Certificate",
            "Student Bank Passbook"
        ],
        "how_to_apply": "Apply online on the official Pudhumai Penn portal at https://pudhumaipenn.tn.gov.in through college nodal officers.",
        "official_link": "https://pudhumaipenn.tn.gov.in",
        "rules": {
            "state_required": "TN",
            "gender_required": "female",
            "category_required": "student",
        },
    },
    {
        "scheme_id": "TN-MAGALIR-URIMAI",
        "scheme_name": "Kalaignar Magalir Urimai Thittam",
        "state": "TN",
        "ministry": "Special Programme Implementation Department, Tamil Nadu",
        "category": "woman",
        "benefit_type": "Cash / DBT",
        "summary": "Basic income entitlement of Rs 1,000 per month provided to 1.15+ crore women heads of eligible households in Tamil Nadu.",
        "benefits": [
            "Rs 1,000 every month (Rs 12,000 per year) credited via DBT to women heads of family."
        ],
        "eligibility_criteria": [
            "Female head of household aged 21 years and above.",
            "Family annual income <= Rs 2,50,000.",
            "Family landholding <= 5 acres wetland or 10 acres dryland; domestic electricity usage <= 3,600 units/year."
        ],
        "exclusions": [
            "Income tax payers and GST-registered traders.",
            "Government servants, pensioners, and elected representatives."
        ],
        "documents_needed": [
            "Aadhaar Card",
            "Smart Ration Card (NFSA)",
            "Electricity Consumer Number",
            "Bank Passbook"
        ],
        "how_to_apply": "Apply through special camp registration organised by Revenue Department or check status at https://kmut.tn.gov.in.",
        "official_link": "https://kmut.tn.gov.in",
        "rules": {
            "state_required": "TN",
            "gender_required": "female",
            "min_age": 21,
            "max_income": 250000,
        },
    },

    # =========================================================================
    # STATE: WEST BENGAL (WB)
    # =========================================================================
    {
        "scheme_id": "WB-LAKSHMIR-BHANDAR",
        "scheme_name": "Lakshmir Bhandar Scheme",
        "state": "WB",
        "ministry": "Department of Women & Child Development and Social Welfare, West Bengal",
        "category": "woman",
        "benefit_type": "Cash / DBT",
        "summary": "Basic income support providing Rs 1,000/month for General category and Rs 1,200/month for SC/ST women heads of households in West Bengal.",
        "benefits": [
            "Rs 1,200 per month for SC/ST women.",
            "Rs 1,000 per month for General category women.",
            "Transferred directly into recipient's bank account every month."
        ],
        "eligibility_criteria": [
            "Female resident of West Bengal aged 25 to 60 years.",
            "Enrolled in Swasthya Sathi health scheme."
        ],
        "exclusions": [
            "Permanent employees of Central/State Government, municipalities, or panchayats.",
            "Women receiving regular government pensions."
        ],
        "documents_needed": [
            "Swasthya Sathi Card",
            "Aadhaar Card",
            "Caste Certificate (for SC/ST enhanced payment)",
            "Bank Passbook"
        ],
        "how_to_apply": "Apply through Duare Sarkar camps or submit form at Block Development Office / Municipal office.",
        "official_link": "https://wb.gov.in",
        "rules": {
            "state_required": "WB",
            "gender_required": "female",
            "min_age": 25,
            "max_age": 60,
        },
    },

    # =========================================================================
    # STATE: RAJASTHAN (RJ)
    # =========================================================================
    {
        "scheme_id": "RJ-CHIRANJEEVI",
        "scheme_name": "Mukhyamantri Ayushman Arogya (Chiranjeevi) Yojana",
        "state": "RJ",
        "ministry": "Medical, Health & Family Welfare Department, Rajasthan",
        "category": "health",
        "benefit_type": "Insurance / Healthcare",
        "summary": "Universal health insurance scheme in Rajasthan offering cashless inpatient treatment of up to Rs 25 Lakh per family per year in empanelled hospitals.",
        "benefits": [
            "Cashless treatment up to Rs 25,00,000 per family per year.",
            "Includes accidental insurance coverage up to Rs 10 Lakh.",
            "Covers organ transplants and advanced tertiary medical procedures."
        ],
        "eligibility_criteria": [
            "Permanent resident families of Rajasthan with Jan Aadhaar Card.",
            "Free for NFSA, SECC, small farmers, and contractual workers; nominal premium of Rs 850/year for other families."
        ],
        "exclusions": [
            "Central/State Government employees covered under RGHS."
        ],
        "documents_needed": [
            "Jan Aadhaar Card / Jan Aadhaar Registration Slip",
            "Aadhaar Card of all family members"
        ],
        "how_to_apply": "Register online via SSO ID on https://chiranjeevi.rajasthan.gov.in or at any E-Mitra kiosk across Rajasthan.",
        "official_link": "https://chiranjeevi.rajasthan.gov.in",
        "rules": {
            "state_required": "RJ",
        },
    },

    # =========================================================================
    # STATE: ANDHRA PRADESH (AP)
    # =========================================================================
    {
        "scheme_id": "AP-RYTHU-BHAROSA",
        "scheme_name": "YSR Rythu Bharosa - PM KISAN",
        "state": "AP",
        "ministry": "Department of Agriculture, Andhra Pradesh",
        "category": "farmer",
        "benefit_type": "Cash / DBT",
        "summary": "Financial support of Rs 13,500 per year provided to farmer families (including tenant farmers) in three installments before cropping seasons.",
        "benefits": [
            "Rs 13,500 per year directly to farmer accounts (Rs 7,500 in May, Rs 4,000 in October, Rs 2,000 in January).",
            "Includes eligible tenant farmers and RoFR forest cultivators."
        ],
        "eligibility_criteria": [
            "Resident cultivator or registered tenant farmer in Andhra Pradesh.",
            "Landholding up to 5 acres with annual income <= Rs 3,00,000."
        ],
        "exclusions": [
            "Same exclusion rules as PM-KISAN (income taxpayers, constitutional postholders)."
        ],
        "documents_needed": [
            "Aadhaar Card",
            "Pattadar Passbook / CCRC (Crop Cultivator Rights Certificate for tenant farmers)",
            "Aadhaar-seeded Bank Account"
        ],
        "how_to_apply": "Register at the local Rythu Bharosa Kendra (RBK) / Village Secretariat or online at https://ysrrythubharosa.ap.gov.in.",
        "official_link": "https://ysrrythubharosa.ap.gov.in",
        "rules": {
            "state_required": "AP",
            "category_required": "farmer",
            "max_income": 300000,
            "max_land_holding_acres": 5.0,
        },
    },

    # =========================================================================
    # STATE: KERALA (KL)
    # =========================================================================
    {
        "scheme_id": "KL-KASP",
        "scheme_name": "Karunya Arogya Suraksha Padhathi (KASP)",
        "state": "KL",
        "ministry": "Health & Family Welfare Department, Kerala",
        "category": "health",
        "benefit_type": "Insurance / Healthcare",
        "summary": "Comprehensive health insurance scheme in Kerala offering Rs 5 Lakh per family per year for secondary and tertiary healthcare in empanelled hospitals.",
        "benefits": [
            "Cashless health cover of Rs 5,00,000 per family per year.",
            "Covered in 200+ public and private empanelled hospitals across Kerala."
        ],
        "eligibility_criteria": [
            "Resident of Kerala belonging to BPL or vulnerable category (Pink and Yellow ration card holders).",
            "Family annual income <= Rs 2,50,000."
        ],
        "exclusions": [
            "Government employees and pensioners covered under MEDISEP."
        ],
        "documents_needed": [
            "Ration Card (Pink or Yellow priority card)",
            "Aadhaar Card of all family members"
        ],
        "how_to_apply": "Check eligibility at any empanelled hospital KASP helpdesk or online at https://sha.kerala.gov.in.",
        "official_link": "https://sha.kerala.gov.in",
        "rules": {
            "state_required": "KL",
            "max_income": 250000,
        },
    },
]


class EligibilityEngine:
    """Pure deterministic scheme eligibility evaluation engine for Civic_AI."""

    _cached_schemes: Optional[List[Dict[str, Any]]] = None
    _cached_mtime: float = 0.0

    def get_all_schemes(self) -> List[Dict[str, Any]]:
        """Return all schemes from persistent data/schemes.json merged with in-memory registry."""
        import json
        from pathlib import Path

        possible_paths = [
            Path(__file__).resolve().parents[4] / "data" / "schemes.json",
            Path.cwd() / "data" / "schemes.json",
            Path(__file__).resolve().parents[3] / "data" / "schemes.json",
        ]
        target_path = None
        for p in possible_paths:
            if p.exists():
                target_path = p
                break

        if target_path:
            try:
                curr_mtime = target_path.stat().st_mtime
                if self._cached_schemes is not None and self._cached_mtime == curr_mtime:
                    return self._cached_schemes

                schemes_dict = {s["scheme_id"].upper(): dict(s) for s in SCHEMES_REGISTRY}
                with open(target_path, "r", encoding="utf-8") as f:
                    file_schemes = json.load(f)
                    for s in file_schemes:
                        sid = s.get("scheme_id", "").upper()
                        if sid:
                            if sid in schemes_dict:
                                merged = dict(schemes_dict[sid])
                                merged.update(s)
                                if "rules" not in s and "rules" in schemes_dict[sid]:
                                    merged["rules"] = schemes_dict[sid]["rules"]
                                schemes_dict[sid] = merged
                            else:
                                if "rules" not in s:
                                    s["rules"] = {}
                                schemes_dict[sid] = s

                # Try loading rich translation overrides from data/scheme_translations_cache.json
                cache_file = target_path.parent / "scheme_translations_cache.json"
                if cache_file.exists():
                    try:
                        with open(cache_file, "r", encoding="utf-8") as cf:
                            t_cache = json.load(cf)
                        for tk, tv in t_cache.items():
                            parts = tk.split("_")
                            if len(parts) >= 2:
                                tsid = parts[0].upper()
                                tlang = parts[1].lower()
                                if tsid in schemes_dict:
                                    if "translations" not in schemes_dict[tsid]:
                                        schemes_dict[tsid]["translations"] = {}
                                    if tlang not in schemes_dict[tsid]["translations"]:
                                        schemes_dict[tsid]["translations"][tlang] = {}
                                    schemes_dict[tsid]["translations"][tlang].update(tv)
                    except Exception as e:
                        logger.warning("Could not merge scheme_translations_cache.json: %s", e)

                for s in schemes_dict.values():
                    if not s.get("direct_apply_url"):
                        s["direct_apply_url"] = s.get("official_link") or s.get("official_url") or s.get("source_url") or "https://www.india.gov.in"
                    if not s.get("official_link"):
                        s["official_link"] = s.get("direct_apply_url") or "https://www.india.gov.in"
                    if not s.get("official_url"):
                        s["official_url"] = s.get("official_link")
                    if not s.get("source_url"):
                        s["source_url"] = s.get("official_link")
                    if not s.get("scheme_type"):
                        s["scheme_type"] = "central" if s.get("state") == "Central" else "state"
                    if not s.get("applicable_states"):
                        s["applicable_states"] = ["All India"] if (s["scheme_type"] == "central" or s.get("state") == "Central") else [s.get("state", "State")]
                    if "state_apply_links" not in s:
                        s["state_apply_links"] = []

                self._cached_schemes = list(schemes_dict.values())
                self._cached_mtime = curr_mtime
                return self._cached_schemes
            except Exception as e:
                logger.warning("Could not read schemes.json from %s: %s", target_path, e)

        if self._cached_schemes is not None:
            return self._cached_schemes
        return SCHEMES_REGISTRY

    def get_schemes_directory(
        self,
        search: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        scheme_type: Optional[str] = None,
        level: Optional[str] = None,
        state: Optional[str] = None,
        category: Optional[str] = None,
        benefit_type: Optional[str] = None,
        lang: str = "en",
        page: Optional[int] = None,
        page_size: int = 24,
    ) -> Any:
        """Query and filter the structured public welfare scheme repository."""
        import math
        import sqlite3
        from pathlib import Path

        results = []
        clean_search = (search or "").strip().lower()
        clean_jurisdiction = (jurisdiction or "all").strip().lower()
        clean_scheme_type = (scheme_type or "").strip().lower() if scheme_type and scheme_type.lower() != "all" else None
        clean_level = (level or "").strip().lower() if level and level.lower() != "all" else None
        clean_state = (state or "").strip().upper() if state and state.upper() != "ALL" else None
        clean_category = (category or "").strip().lower() if category and category.lower() != "all" else None
        clean_benefit = (benefit_type or "").strip().lower() if benefit_type and benefit_type.lower() != "all" else None

        # Check SQLite FTS5 index for rapid keyword search if available
        fts_matching_ids: Optional[Set[str]] = None
        if clean_search:
            db_candidates = [
                Path(__file__).resolve().parents[4] / "data" / "civic_ai.db",
                Path.cwd() / "data" / "civic_ai.db",
                Path(__file__).resolve().parents[3] / "data" / "civic_ai.db",
            ]
            db_path = next((p for p in db_candidates if p.exists()), None)
            if db_path:
                try:
                    with sqlite3.connect(db_path, timeout=2.0) as conn:
                        cur = conn.cursor()
                        # Sanitize query for FTS5
                        safe_q = re.sub(r'[^a-zA-Z0-9\u0900-\u0D7F]+', ' ', clean_search).strip()
                        if safe_q:
                            fts_query = f"{safe_q}*"
                            rows = cur.execute("SELECT scheme_id FROM schemes_fts WHERE schemes_fts MATCH ?", (fts_query,)).fetchall()
                            if rows:
                                fts_matching_ids = {r[0].upper() for r in rows}
                except Exception as e:
                    logger.debug("SQLite FTS5 query bypassed: %s", e)

        for scheme in self.get_all_schemes():
            sid = scheme.get("scheme_id", "").upper()
            scheme_state = scheme.get("state", "Central")
            is_central = scheme_state == "Central"
            stype = (scheme.get("scheme_type") or ("central" if is_central else "state")).lower()
            slevel = (scheme.get("level") or ("Central" if is_central else "State")).lower()

            # 1. Governance Classification Filter (central, state, integrated, multi_state)
            if clean_scheme_type:
                if clean_scheme_type == "state" and stype not in ("state", "local"):
                    continue
                elif clean_scheme_type != "state" and stype != clean_scheme_type:
                    continue

            # 1b. Level filter
            if clean_level:
                if clean_level == "central" and not is_central:
                    continue
                if clean_level == "state" and is_central:
                    continue

            # 1c. Legacy Jurisdiction filter
            if clean_jurisdiction == "central" and not is_central:
                continue
            if clean_jurisdiction == "state" and is_central:
                continue

            # 2. State filter (when a specific state is chosen, include that state's schemes + central schemes if jurisdiction != 'state')
            if clean_state and clean_state != "CENTRAL":
                applicable = [s.upper() for s in scheme.get("applicable_states", [])]
                if clean_jurisdiction == "state":
                    if scheme_state.upper() != clean_state and clean_state not in applicable:
                        continue
                else:
                    # 'all' jurisdiction: show selected state + central schemes
                    if not is_central and scheme_state.upper() != clean_state and clean_state not in applicable:
                        continue
            elif clean_state == "CENTRAL" and not is_central:
                continue

            # 3. Category filter
            if clean_category and scheme.get("category", "").lower() != clean_category:
                continue

            # 4. Benefit type filter
            if clean_benefit:
                scheme_benefit = scheme.get("benefit_type", "").lower()
                if clean_benefit not in scheme_benefit:
                    continue

            # 5. Search query matching
            if clean_search:
                if fts_matching_ids is not None:
                    if sid not in fts_matching_ids:
                        continue
                else:
                    benefits_str = " ".join(scheme.get("benefits") or [])
                    eligibility_str = " ".join(scheme.get("eligibility_criteria") or [])
                    search_text = (
                        f"{scheme.get('scheme_id', '')} "
                        f"{scheme.get('scheme_name', '')} "
                        f"{scheme.get('ministry', '')} "
                        f"{scheme.get('summary', '')} "
                        f"{benefits_str} "
                        f"{eligibility_str} "
                        f"{scheme.get('category', '')}"
                    ).lower()

                    # Also search inside multilingual translations if present
                    translations = scheme.get("translations", {})
                    trans_text = " ".join(
                        f"{t.get('scheme_name', '')} {t.get('summary', '')}"
                        for t in translations.values()
                        if isinstance(t, dict)
                    ).lower()

                    if clean_search not in search_text and clean_search not in trans_text:
                        continue

            # Localize scheme content if lang != 'en'
            if lang and lang != "en":
                trans = scheme.get("translations", {}).get(lang) if isinstance(scheme.get("translations"), dict) else None
                if not trans or (trans.get("scheme_name") == scheme.get("scheme_name") and lang != "en"):
                    from app.services.eligibility.translator import scheme_translator
                    cached = scheme_translator.get_cached_translation(scheme.get("scheme_id", ""), lang)
                    if cached:
                        trans = cached

                if trans and isinstance(trans, dict):
                    loc_scheme = dict(scheme)
                    loc_scheme["original_scheme_name"] = scheme.get("scheme_name", "")
                    if trans.get("scheme_name"):
                        loc_scheme["scheme_name"] = trans["scheme_name"]
                    if trans.get("summary"):
                        loc_scheme["summary"] = trans["summary"]
                    if trans.get("benefits"):
                        loc_scheme["benefits"] = trans["benefits"]
                    if trans.get("eligibility_criteria"):
                        loc_scheme["eligibility_criteria"] = trans["eligibility_criteria"]
                    if trans.get("exclusions"):
                        loc_scheme["exclusions"] = trans["exclusions"]
                    if trans.get("documents_required"):
                        loc_scheme["documents_required"] = trans["documents_required"]
                    if trans.get("documents_needed"):
                        loc_scheme["documents_needed"] = trans["documents_needed"]
                    if trans.get("application_steps"):
                        loc_scheme["application_steps"] = trans["application_steps"]
                    if trans.get("nodal_authority"):
                        loc_scheme["nodal_authority"] = trans["nodal_authority"]
                        loc_scheme["ministry"] = trans["nodal_authority"]
                    elif trans.get("ministry"):
                        loc_scheme["ministry"] = trans["ministry"]
                        loc_scheme["nodal_authority"] = trans["ministry"]
                    results.append(loc_scheme)
                    continue

            results.append(scheme)

        if page is not None:
            p = max(1, page)
            ps = max(1, min(page_size, 100))
            total = len(results)
            total_pages = max(1, math.ceil(total / ps))
            start_idx = (p - 1) * ps
            end_idx = start_idx + ps
            items = results[start_idx:end_idx]
            return {
                "items": items,
                "total": total,
                "page": p,
                "page_size": ps,
                "total_pages": total_pages,
            }

        return results

    def get_scheme_by_id(self, scheme_id: str, lang: str = "en") -> Optional[Dict[str, Any]]:
        """Retrieve single scheme policy specification by ID with optional localization."""
        clean_id = scheme_id.strip().upper()
        for scheme in self.get_all_schemes():
            if scheme.get("scheme_id", "").upper() == clean_id:
                if lang and lang != "en":
                    trans = scheme.get("translations", {}).get(lang) if isinstance(scheme.get("translations"), dict) else None
                    if not trans:
                        from app.services.eligibility.translator import scheme_translator
                        trans = scheme_translator.get_cached_translation(clean_id, lang)
                    if trans and isinstance(trans, dict):
                        loc_scheme = dict(scheme)
                        loc_scheme["original_scheme_name"] = scheme.get("scheme_name", "")
                        if trans.get("scheme_name"):
                            loc_scheme["scheme_name"] = trans["scheme_name"]
                        if trans.get("summary"):
                            loc_scheme["summary"] = trans["summary"]
                        if trans.get("benefits"):
                            loc_scheme["benefits"] = trans["benefits"]
                        if trans.get("eligibility_criteria"):
                            loc_scheme["eligibility_criteria"] = trans["eligibility_criteria"]
                        if trans.get("exclusions"):
                            loc_scheme["exclusions"] = trans["exclusions"]
                        if trans.get("documents_required"):
                            loc_scheme["documents_required"] = trans["documents_required"]
                        if trans.get("application_steps"):
                            loc_scheme["application_steps"] = trans["application_steps"]
                        if trans.get("nodal_authority"):
                            loc_scheme["nodal_authority"] = trans["nodal_authority"]
                            loc_scheme["ministry"] = trans["nodal_authority"]
                        elif trans.get("ministry"):
                            loc_scheme["ministry"] = trans["ministry"]
                            loc_scheme["nodal_authority"] = trans["ministry"]
                        return loc_scheme
                return scheme
        return None
        for scheme in self.get_all_schemes():
            if scheme.get("scheme_id", "").upper() == clean_id:
                return scheme
        return None

    def evaluate_scheme(
        self,
        profile: CitizenProfile,
        scheme: Dict[str, Any],
        lang: str = "en",
    ) -> SchemeMatchResult:
        """Deterministically evaluate a single scheme against a citizen profile.

        Zero LLM calls. Returns status: 'eligible' | 'not_eligible' | 'need_more_info'.
        """
        rules = scheme.get("rules", {})
        scheme_id = scheme["scheme_id"]
        scheme_name = scheme["scheme_name"]

        # Check State restriction
        state_req = rules.get("state_required")
        if state_req:
            if not profile.state:
                return self._need_more_info(
                    scheme, "state", f"Requires state residency in {state_req}."
                )
            if profile.state.upper() != state_req.upper():
                return SchemeMatchResult(
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    status="not_eligible",
                    deciding_rule=f"profile.state == '{state_req}'",
                    explanation=f"This scheme is exclusive to residents of state {state_req}. Your profile indicates '{profile.state}'.",
                    benefits=scheme.get("benefits", []),
                    documents_needed=scheme.get("documents_needed", []),
                    how_to_apply=scheme.get("how_to_apply", ""),
                    official_link=scheme.get("official_link", ""),
                    last_verified=datetime.now(timezone.utc),
                )

        # Check Gender restriction
        gender_req = rules.get("gender_required")
        if gender_req:
            if not profile.gender:
                return self._need_more_info(
                    scheme, "gender", f"Requires gender: {gender_req}."
                )
            if profile.gender.lower() != gender_req.lower():
                return SchemeMatchResult(
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    status="not_eligible",
                    deciding_rule=f"profile.gender == '{gender_req}'",
                    explanation=f"This scheme is exclusively designed for {gender_req} applicants.",
                    benefits=scheme.get("benefits", []),
                    documents_needed=scheme.get("documents_needed", []),
                    how_to_apply=scheme.get("how_to_apply", ""),
                    official_link=scheme.get("official_link", ""),
                    last_verified=datetime.now(timezone.utc),
                )

        # Check Minimum Age
        min_age = rules.get("min_age")
        if min_age is not None:
            if profile.age is None:
                return self._need_more_info(
                    scheme, "age", f"Requires minimum age of {min_age} years."
                )
            if profile.age < min_age:
                return SchemeMatchResult(
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    status="not_eligible",
                    deciding_rule=f"profile.age >= {min_age}",
                    explanation=f"Applicant age ({profile.age}) is below the mandatory minimum age of {min_age} years.",
                    benefits=scheme.get("benefits", []),
                    documents_needed=scheme.get("documents_needed", []),
                    how_to_apply=scheme.get("how_to_apply", ""),
                    official_link=scheme.get("official_link", ""),
                    last_verified=datetime.now(timezone.utc),
                )

        # Check Maximum Age
        max_age = rules.get("max_age")
        if max_age is not None:
            if profile.age is None:
                return self._need_more_info(
                    scheme, "age", f"Requires maximum age of {max_age} years."
                )
            if profile.age > max_age:
                return SchemeMatchResult(
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    status="not_eligible",
                    deciding_rule=f"profile.age <= {max_age}",
                    explanation=f"Applicant age ({profile.age}) exceeds the maximum eligibility limit of {max_age} years.",
                    benefits=scheme.get("benefits", []),
                    documents_needed=scheme.get("documents_needed", []),
                    how_to_apply=scheme.get("how_to_apply", ""),
                    official_link=scheme.get("official_link", ""),
                    last_verified=datetime.now(timezone.utc),
                )

        # Check Category (e.g. farmer)
        category_req = rules.get("category_required")
        if category_req:
            if not profile.category:
                return self._need_more_info(
                    scheme, "category", f"Requires category: {category_req}."
                )
            if profile.category.lower() != category_req.lower():
                return SchemeMatchResult(
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    status="not_eligible",
                    deciding_rule=f"profile.category == '{category_req}'",
                    explanation=f"Requires applicant category to be '{category_req}'. Your profile specifies '{profile.category}'.",
                    benefits=scheme.get("benefits", []),
                    documents_needed=scheme.get("documents_needed", []),
                    how_to_apply=scheme.get("how_to_apply", ""),
                    official_link=scheme.get("official_link", ""),
                    last_verified=datetime.now(timezone.utc),
                )

        # Check Landholding Limit (for farmer schemes)
        max_land = rules.get("max_land_holding_acres")
        if max_land is not None:
            if profile.land_holding_acres is None:
                return self._need_more_info(
                    scheme, "land_holding_acres", f"Requires landholding details (<= {max_land} acres)."
                )
            if profile.land_holding_acres > max_land:
                return SchemeMatchResult(
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    status="not_eligible",
                    deciding_rule=f"land_holding_acres <= {max_land}",
                    explanation=f"Landholding ({profile.land_holding_acres} acres) exceeds the marginal/small farmer ceiling of {max_land} acres.",
                    benefits=scheme.get("benefits") or [],
                    documents_needed=scheme.get("documents_needed") or [],
                    how_to_apply=scheme.get("how_to_apply", ""),
                    official_link=scheme.get("official_link", ""),
                    last_verified=datetime.now(timezone.utc),
                )

        # Check Disability Percentage
        min_disability = rules.get("min_disability_percentage")
        if min_disability is not None:
            if profile.disability_percentage is None:
                return self._need_more_info(
                    scheme, "disability_percentage", f"Requires certified disability percentage (>= {min_disability}%)."
                )
            if profile.disability_percentage < min_disability:
                return SchemeMatchResult(
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    status="not_eligible",
                    deciding_rule=f"disability_percentage >= {min_disability}",
                    explanation=f"Certified disability percentage ({profile.disability_percentage}%) is below the statutory threshold of {min_disability}%.",
                    benefits=scheme.get("benefits") or [],
                    documents_needed=scheme.get("documents_needed") or [],
                    how_to_apply=scheme.get("how_to_apply", ""),
                    official_link=scheme.get("official_link", ""),
                    last_verified=datetime.now(timezone.utc),
                )

        # Check Maximum Income Limit
        max_income = rules.get("max_income")
        if max_income is not None:
            if profile.annual_income is None:
                return self._need_more_info(
                    scheme, "annual_income", f"Requires annual household income verification (<= Rs {max_income:,})."
                )
            if profile.annual_income > max_income:
                return SchemeMatchResult(
                    scheme_id=scheme_id,
                    scheme_name=scheme_name,
                    status="not_eligible",
                    deciding_rule=f"annual_income <= {max_income}",
                    explanation=f"Annual family income (Rs {profile.annual_income:,.0f}) exceeds the statutory income ceiling of Rs {max_income:,}.",
                    benefits=scheme.get("benefits") or [],
                    documents_needed=scheme.get("documents_needed") or [],
                    how_to_apply=scheme.get("how_to_apply", ""),
                    official_link=scheme.get("official_link", ""),
                    last_verified=datetime.now(timezone.utc),
                )

        # If all deterministic checks pass -> ELIGIBLE
        state_rule = f"state == '{state_req}' and " if state_req else ""
        income_str = f"income <= {max_income}" if max_income else "demographic_match"
        deciding_rule = f"{state_rule}{income_str}"
        explanation = (
            f"You meet all statutory requirements for {scheme_name} based on your verified demographic profile."
        )

        return SchemeMatchResult(
            scheme_id=scheme_id,
            scheme_name=scheme_name,
            status="eligible",
            deciding_rule=deciding_rule,
            explanation=explanation,
            scheme_type=scheme.get("scheme_type", "central"),
            applicable_states=scheme.get("applicable_states", ["All India"]),
            nodal_authority=scheme.get("nodal_authority", scheme.get("ministry", "")),
            application_mode=scheme.get("application_mode", "online"),
            direct_apply_url=scheme.get("direct_apply_url") or scheme.get("official_link", ""),
            state_apply_links=scheme.get("state_apply_links", []),
            official_source_links=scheme.get("official_source_links", []),
            benefits=scheme.get("benefits") or [],
            documents_needed=scheme.get("documents_needed") or [],
            how_to_apply=scheme.get("how_to_apply", ""),
            official_link=scheme.get("official_link", ""),
            last_verified=datetime.now(timezone.utc),
        )

    def _need_more_info(
        self, scheme: Dict[str, Any], missing_field: str, reason: str
    ) -> SchemeMatchResult:
        """Helper to construct need_more_info response."""
        return SchemeMatchResult(
            scheme_id=scheme["scheme_id"],
            scheme_name=scheme["scheme_name"],
            status="need_more_info",
            deciding_rule=f"requires({missing_field})",
            explanation=f"Cannot evaluate eligibility definitively: {reason}",
            scheme_type=scheme.get("scheme_type", "central"),
            applicable_states=scheme.get("applicable_states", ["All India"]),
            nodal_authority=scheme.get("nodal_authority", scheme.get("ministry", "")),
            application_mode=scheme.get("application_mode", "online"),
            direct_apply_url=scheme.get("direct_apply_url") or scheme.get("official_link", ""),
            state_apply_links=scheme.get("state_apply_links", []),
            official_source_links=scheme.get("official_source_links", []),
            benefits=scheme.get("benefits") or [],
            documents_needed=scheme.get("documents_needed") or [],
            how_to_apply=scheme.get("how_to_apply", ""),
            official_link=scheme.get("official_link", ""),
            last_verified=datetime.now(timezone.utc),
        )

    def evaluate_all(
        self,
        profile: CitizenProfile,
        state_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        lang: str = "en",
    ) -> Tuple[List[SchemeMatchResult], List[Dict[str, Any]]]:
        """Evaluate all eligible schemes for a citizen profile with zero LLM decisions."""
        results: List[SchemeMatchResult] = []
        missing_attributes_set = set()

        for scheme in self.get_all_schemes():
            # Apply state filtering if specified
            scheme_state = scheme.get("state")
            if state_filter and state_filter != "Central":
                if scheme_state != "Central" and scheme_state.upper() != state_filter.upper():
                    continue

            # Apply category filtering if specified
            if category_filter and category_filter != "all" and scheme.get("category") != category_filter:
                continue

            match_res = self.evaluate_scheme(profile, scheme, lang=lang)
            results.append(match_res)

            if match_res.status == "need_more_info":
                rule_text = match_res.deciding_rule
                if "requires(" in rule_text:
                    attr = rule_text.split("requires(")[1].split(")")[0]
                    missing_attributes_set.add(attr)

        # Generate adaptive follow-up questions
        follow_up_questions = []
        question_map = {
            "annual_income": {
                "attribute": "annual_income",
                "question": "What is your approximate annual household income in Rupees?",
                "type": "number",
                "placeholder": "e.g. 150000",
            },
            "age": {
                "attribute": "age",
                "question": "What is your current age in years?",
                "type": "number",
                "placeholder": "e.g. 62",
            },
            "gender": {
                "attribute": "gender",
                "question": "What is your gender?",
                "type": "select",
                "options": ["female", "male", "other"],
            },
            "land_holding_acres": {
                "attribute": "land_holding_acres",
                "question": "How many acres of cultivable agricultural land do you own?",
                "type": "number",
                "placeholder": "e.g. 2.5",
            },
            "disability_percentage": {
                "attribute": "disability_percentage",
                "question": "What is your certified percentage of disability (if applicable)?",
                "type": "number",
                "placeholder": "e.g. 40",
            },
            "state": {
                "attribute": "state",
                "question": "Which state or union territory are you a permanent resident of?",
                "type": "select",
                "options": [
                    "Central", "AP", "AR", "AS", "BR", "CG", "GA", "GJ", "HR", "HP",
                    "JH", "KA", "KL", "MP", "MH", "MN", "ML", "MZ", "NL", "OD",
                    "PB", "RJ", "SK", "TN", "TS", "TR", "UP", "UK", "WB",
                    "AN", "CH", "DN", "DL", "JK", "LA", "LD", "PY"
                ],
            },
        }

        for attr in missing_attributes_set:
            if attr in question_map:
                follow_up_questions.append(question_map[attr])

        return results, follow_up_questions


eligibility_engine = EligibilityEngine()
