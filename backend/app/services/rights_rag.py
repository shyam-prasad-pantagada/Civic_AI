"""Civic_AI Citizen Rights RAG Service.

Implements legal question retrieval and explanation with mandatory citations
(SPEC.md Section 3.3).
Retrieves relevant sections from central Acts (India Code) and state regulations.
If no statutory match is found in RAG, delegates to dynamic_rights_llm for
up-to-date non-statutory guidance.
All methods accept a `lang` parameter.
"""

from datetime import datetime, timezone
import logging
import re
from typing import Any, Dict, List, Optional
from app.models.schemas import Citation, RightsResponse
from app.services.dynamic_rights_llm import generate_dynamic_rights_guidance

logger = logging.getLogger("Civic_AI.RightsRAG")

# Official statutory database curated from India Code (indiacode.nic.in) and state law departments
STATUTORY_KNOWLEDGEBASE: List[Dict[str, Any]] = [
    {
        "id": "TENANCY_EVICTION",
        "keywords": ["landlord", "evict", "eviction", "tenant", "rent", "lease", "deposit", "notice to vacate"],
        "topic": "Tenancy & Tenant Protection Against Forceful Eviction",
        "jurisdiction": "Central",
        "act_name": "Model Tenancy Act, 2021",
        "section": "Section 21 (Protection Against Eviction) & Section 22",
        "url": "https://mohua.gov.in/upload/uploadfiles/files/Model_Tenancy_Act_English.pdf",
        "summary": "A landlord cannot forcefully evict a tenant or cut essential utilities (water, electricity) without due process. Eviction requires formal statutory notice and a decree from the designated Rent Authority / Court.",
        "rights": [
            "You cannot be evicted forcefully or locked out without a formal order from the Rent Authority or Rent Court under Section 21 of the Model Tenancy Act (https://mohua.gov.in).",
            "The landlord cannot withhold or cut off essential supplies (electricity, water, elevator) under any circumstances (Section 20 & 22).",
            "You are entitled to a mandatory notice period before any eviction proceeding can be initiated.",
        ],
        "actions": [
            "Request all eviction notices and communications from your landlord in writing.",
            "Continue paying the lawful agreed rent and retain all rent receipts or digital transaction records.",
            "If your landlord threatens illegal eviction or cuts off water/power, file an urgent petition before the local Rent Authority / Sub-Divisional Magistrate.",
        ],
        "remedies": [
            "Local Rent Court / Rent Authority under District Collector (https://mohua.gov.in)",
            "National Legal Services Authority (NALSA) Helpline: 15100 (https://nalsa.gov.in) for free legal representation",
            "Nearest Local Police Station if physical intimidation or illegal lock-out occurs (https://services.india.gov.in)",
        ],
    },
    {
        "id": "MH_TENANCY",
        "keywords": ["maharashtra", "mumbai", "pune", "rent control", "landlord", "eviction", "pagdi"],
        "topic": "Maharashtra Tenant Protection",
        "jurisdiction": "MH",
        "act_name": "Maharashtra Rent Control Act, 1999",
        "section": "Section 15 (Relief Against Forfeiture) & Section 16",
        "url": "https://indiacode.nic.in/handle/123456789/2289",
        "summary": "Under Maharashtra Rent Control Act, no ejectment suit can be entertained so long as the tenant pays or is ready and willing to pay standard rent and permitted increases.",
        "rights": [
            "Protection from eviction as long as standard rent is duly tendered under Section 15 (https://indiacode.nic.in/handle/123456789/2289).",
            "Right to approach the Small Causes Court in Mumbai or Civil Court in districts.",
        ],
        "actions": [
            "Tender rent by registered post or bank transfer if the landlord refuses receipt.",
            "File a regular declaratory suit or injunction in the Small Causes Court.",
        ],
        "remedies": [
            "Maharashtra State Legal Services Authority (MSLSA) - Helpline: 15100 (https://legalservices.maharashtra.gov.in)",
            "Court of Small Causes, Mumbai (https://bombayhighcourt.nic.in)",
        ],
    },
    {
        "id": "CONSUMER_RIGHTS",
        "keywords": ["consumer", "defective", "refund", "warranty", "deficiency", "fraud", "e-commerce", "cheat"],
        "topic": "Consumer Protection and Right to Refund/Replacement",
        "jurisdiction": "Central",
        "act_name": "Consumer Protection Act, 2019",
        "section": "Section 2(7) (Consumer Definition) & Section 35",
        "url": "https://consumeraffairs.nic.in/acts-and-rules/consumer-protection",
        "summary": "Consumers have the statutory right to seek redressal against unfair trade practices, defective goods, or deficiency in service directly before District Consumer Commissions without requiring an advocate.",
        "rights": [
            "Right to be protected against unfair trade practices and false or misleading advertisements under Consumer Protection Act, 2019 (https://consumeraffairs.nic.in).",
            "Right to file a complaint directly online via e-Daakhil (https://edaakhil.nic.in) without hiring a lawyer.",
            "Right to claim full refund, replacement, and compensation for mental agony and financial loss.",
        ],
        "actions": [
            "Send a formal written notice / grievance email to the seller/service provider with tax invoice and evidence.",
            "Call the National Consumer Helpline at 1915 or register an online complaint at https://consumerhelpline.gov.in.",
            "File a formal statutory complaint online on the e-Daakhil portal (https://edaakhil.nic.in) before your District Consumer Commission.",
        ],
        "remedies": [
            "National Consumer Helpline (NCH): Call 1915 or visit https://consumerhelpline.gov.in",
            "District Consumer Disputes Redressal Commission (DCDRC) via e-Daakhil portal (https://edaakhil.nic.in)",
            "Department of Consumer Affairs, Government of India (https://consumeraffairs.nic.in)",
        ],
    },
    {
        "id": "RTI_RIGHTS",
        "keywords": ["rti", "right to information", "information", "government delay", "file not moving", "bribe", "public authority"],
        "topic": "Right to Information from Public Authorities",
        "jurisdiction": "Central",
        "act_name": "Right to Information Act, 2005",
        "section": "Section 6 (Request for Information) & Section 7 (Disposal of Request)",
        "url": "https://rti.gov.in",
        "summary": "Every Indian citizen has the statutory right to request records, files, reasons for decisions, and inspection of works from any central or state government public authority with a statutory deadline of 30 days.",
        "rights": [
            "Right to obtain certified copies of government files, tender documents, inspection records, and official memos (https://rti.gov.in).",
            "Mandatory statutory response timeframe: 30 calendar days (48 hours if information concerns life or personal liberty).",
            "Fee is capped at Rs 10 for central departments, and completely free of charge for Below Poverty Line (BPL) citizens.",
        ],
        "actions": [
            "Submit an online RTI application via https://rtionline.gov.in (for Central ministries) or state RTI portals.",
            "Draft a concise, specific query asking for records rather than explanations or legal opinions.",
            "If no reply is received within 30 days or information is falsely rejected, file a First Appeal within 30 days.",
        ],
        "remedies": [
            "National RTI Online Portal: https://rtionline.gov.in",
            "Central Information Commission (CIC): https://cic.gov.in",
            "First Appellate Authority (FAA) of the respective government department",
        ],
    },
    {
        "id": "DOMESTIC_VIOLENCE",
        "keywords": ["domestic violence", "husband", "in-laws", "abuse", "beating", "women harassment", "maintenance", "marital"],
        "topic": "Protection of Women from Domestic Violence",
        "jurisdiction": "Central",
        "act_name": "Protection of Women from Domestic Violence Act, 2005",
        "section": "Section 12, Section 18 (Protection Orders) & Section 19 (Residence Orders)",
        "url": "https://wcd.nic.in/act/protection-women-domestic-violence-act-2005",
        "summary": "Aggrieved women have the absolute right to reside in the shared household, obtain protection orders against violence, receive emergency maintenance, and get free legal representation from legal aid cells.",
        "rights": [
            "Right to live in the shared household without being thrown out or dispossessed under Section 19 (https://wcd.nic.in).",
            "Right to immediate judicial protection orders against threats, stalking, or violence (Section 18).",
            "Right to free medical care, safe shelter home accommodation, and free legal aid from NALSA (https://nalsa.gov.in).",
        ],
        "actions": [
            "Call the 24x7 Women's Helpline at 181 or Emergency Helpline at 112 immediately in case of physical threat.",
            "Approach the local Protection Officer (PO) designated in every district or service provider NGO.",
            "File an application under Section 12 before the Judicial Magistrate of First Class (JMFC).",
        ],
        "remedies": [
            "Women in Distress National Helpline: 181 / 1091 (https://wcd.nic.in)",
            "National Commission for Women (NCW) Helpline: 7827170170 (https://ncw.nic.in)",
            "National Legal Services Authority (NALSA) Free Legal Aid Panel: 15100 (https://nalsa.gov.in)",
        ],
    },
    {
        "id": "SENIOR_CITIZEN_RIGHTS",
        "keywords": ["senior citizen", "elderly", "parents", "maintenance", "property transfer", "children not looking after"],
        "topic": "Maintenance & Welfare of Senior Citizens",
        "jurisdiction": "Central",
        "act_name": "Maintenance and Welfare of Parents and Senior Citizens Act, 2007",
        "section": "Section 4 (Maintenance) & Section 23 (Transfer of Property Void)",
        "url": "https://socialjustice.gov.in/writereaddata/UploadFile/Annexure-X635996105048250000.pdf",
        "summary": "Parents and senior citizens aged 60+ who are unable to maintain themselves can claim maintenance from adult children/heirs. Property gifted to children with expectation of care can be declared void if children neglect them.",
        "rights": [
            "Right to claim monthly maintenance from children or legal heirs through a fast-track Maintenance Tribunal (https://socialjustice.gov.in).",
            "Under Section 23, property gifted to children can be legally cancelled by the Sub-Divisional Magistrate (SDM) if basic needs are denied.",
            "Right to life, security, and subsidized healthcare in government hospitals.",
        ],
        "actions": [
            "Submit a simple written application before the Sub-Divisional Magistrate (SDM) / Maintenance Tribunal.",
            "Call Elderline at 14567 (https://elderline.dosje.gov.in) for immediate assistance, counseling, and rescue.",
            "No advocate is necessary to represent you before the Maintenance Tribunal.",
        ],
        "remedies": [
            "National Elderline Helpline: 14567 (https://elderline.dosje.gov.in)",
            "Sub-Divisional Magistrate (SDM) / Maintenance Tribunal in your district",
            "Department of Social Justice and Empowerment (https://socialjustice.gov.in)",
        ],
    },
    {
        "id": "MINIMUM_WAGES",
        "keywords": ["salary", "unpaid", "wages", "minimum wage", "employer", "worker", "contractor", "deduction"],
        "topic": "Worker Protection Against Unpaid Wages & Underpayment",
        "jurisdiction": "Central",
        "act_name": "Code on Wages, 2019 / Minimum Wages Act, 1948",
        "section": "Section 12 (Payment of Minimum Rates of Wages)",
        "url": "https://labour.gov.in/code-on-wages-2019",
        "summary": "No employer or contractor can pay less than the statutory minimum wage rates fixed by central/state government. Unlawful deductions and refusal of overtime compensation are punishable under law.",
        "rights": [
            "Right to receive full notified minimum wages on or before the 7th or 10th of each calendar month (https://labour.gov.in).",
            "Right to overtime wages at double the ordinary wage rate for work exceeding statutory working hours.",
            "Prohibition of unauthorized wage deductions without statutory authorization.",
        ],
        "actions": [
            "Maintain proof of working days, attendance logs, punch cards, and bank statements.",
            "Submit a formal claim petition before the Labour Commissioner / Authority under the Minimum Wages Act.",
            "Report non-payment to the Ministry of Labour grievance portal (https://samadhan.labour.gov.in).",
        ],
        "remedies": [
            "Office of the Assistant Labour Commissioner (Central / State)",
            "Ministry of Labour Samadhan Portal: https://samadhan.labour.gov.in",
            "Shram Suvidha Portal: https://shramsuvidha.gov.in",
        ],
    },
    {
        "id": "RTI_APPEALS",
        "keywords": ["rti appeal", "first appeal", "second appeal", "cic", "information commission", "cpo penalty", "appeal delay"],
        "topic": "RTI First Appeal & Second Appeal Procedures and Penalties",
        "jurisdiction": "Central",
        "act_name": "Right to Information Act, 2005",
        "section": "Section 19 (Appeals) & Section 20 (Penalties)",
        "url": "https://rti.gov.in",
        "summary": "If information is not received within 30 days or is aggrieved by decision of CPIO, a citizen can file a First Appeal within 30 days to the First Appellate Authority. If still aggrieved, a Second Appeal lies before Central/State Information Commission within 90 days. PIOs face a penalty of Rs 250 per day up to Rs 25,000 for mala fide denial.",
        "rights": [
            "Right to file First Appeal within 30 days without fee under Section 19(1) of RTI Act, 2005 (https://rti.gov.in).",
            "First Appellate Authority must dispose of appeal within 30 days (extendable to max 45 days for recorded reasons).",
            "Right to approach Central Information Commission (CIC) in Second Appeal under Section 19(3) if First Appeal fails.",
            "Penalty of Rs 250/day up to Rs 25,000 against delinquent PIOs under Section 20.",
        ],
        "actions": [
            "Draft First Appeal addressed to First Appellate Authority citing original RTI registration number and date.",
            "Submit online through https://rtionline.gov.in for Central Public Authorities.",
            "If no decision within 45 days, prepare Second Appeal before CIC (https://cic.gov.in).",
        ],
        "remedies": [
            "Central Information Commission: https://cic.gov.in",
            "National RTI Online Portal: https://rtionline.gov.in",
            "Department of Personnel and Training (DoPT): https://dopt.gov.in",
        ],
    },
    {
        "id": "ZERO_FIR_POLICE",
        "keywords": ["fir", "zero fir", "police refusal", "jurisdiction", "police station", "crime report", "refuse complaint"],
        "topic": "Mandatory Registration of FIR and Zero FIR",
        "jurisdiction": "Central",
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023 / Code of Criminal Procedure, 1973",
        "section": "Section 173 (Information in Cognizable Cases / Zero FIR)",
        "url": "https://mha.gov.in",
        "summary": "Every police station is mandated by law to register a Zero FIR for any cognizable offence irrespective of territorial jurisdiction, and forward it to the jurisdictional station. Refusal by a police officer to register an FIR is punishable under Section 166A of IPC / BNS.",
        "rights": [
            "Right to have a Zero FIR registered at ANY police station irrespective of territorial location (https://mha.gov.in).",
            "Right to receive a free certified copy of the registered FIR immediately without delay.",
            "Women reporting sexual offences have the right to record statements before a female officer at their residence.",
            "Refusal by police to record an FIR in cognizable cases is a criminal offence under Section 166A.",
        ],
        "actions": [
            "Demand registration of a Zero FIR with immediate transfer to the appropriate police station.",
            "If Station House Officer (SHO) refuses, send written complaint by registered post to Superintendent of Police (SP) or Commissioner.",
            "File an application under Section 156(3) / BNSS before the Judicial Magistrate to direct police investigation.",
        ],
        "remedies": [
            "National Emergency Helpline: 112 (https://services.india.gov.in)",
            "Ministry of Home Affairs (MHA) Citizen Portal: https://mha.gov.in",
            "National Legal Services Authority (NALSA) 24x7 Legal Aid: 15100 (https://nalsa.gov.in)",
        ],
    },
    {
        "id": "ECOMMERCE_CONSUMER_REFUND",
        "keywords": ["ecommerce", "e-commerce", "amazon", "flipkart", "online shopping", "refund delay", "return refused", "seller"],
        "topic": "E-Commerce Consumer Grievance & Refund Timelines",
        "jurisdiction": "Central",
        "act_name": "Consumer Protection (E-Commerce) Rules, 2020 / Consumer Protection Act, 2019",
        "section": "Rule 5 & Rule 6 (Liabilities of Marketplace and Inventory E-Commerce Entities)",
        "url": "https://consumeraffairs.nic.in",
        "summary": "E-commerce entities must acknowledge consumer grievances within 48 hours and redress them within one month. Unilateral cancellation of orders, refusal of legitimate returns, or withholding refunds for defective or non-conforming goods is strictly prohibited.",
        "rights": [
            "Mandatory acknowledgment of consumer complaints by e-commerce platforms within 48 hours (https://consumeraffairs.nic.in).",
            "Full refund entitlement within statutory timeline if goods delivered are defective, damaged, or significantly delayed.",
            "No platform can impose arbitrary cancellation charges after order confirmation unless borne by seller.",
        ],
        "actions": [
            "File a complaint with the e-commerce Grievance Officer whose details must be published on the platform.",
            "Register ticket on National Consumer Helpline (NCH) by dialing 1915 or through https://consumerhelpline.gov.in.",
            "File an e-Daakhil consumer petition for refund plus compensation (https://edaakhil.nic.in).",
        ],
        "remedies": [
            "National Consumer Helpline (NCH): Call 1915 or WhatsApp 8800001915 (https://consumerhelpline.gov.in)",
            "e-Daakhil Online Consumer Court: https://edaakhil.nic.in",
            "Central Consumer Protection Authority (CCPA): https://consumeraffairs.nic.in",
        ],
    },
    {
        "id": "MATERNITY_BENEFIT",
        "keywords": ["maternity", "maternity leave", "pregnancy", "female worker", "paid leave", "creche", "terminated pregnancy"],
        "topic": "Maternity Benefits & Paid Leave Protection for Women Employees",
        "jurisdiction": "Central",
        "act_name": "Maternity Benefit Act, 1961 (Amended 2017)",
        "section": "Section 5 (Right to Payment of Maternity Benefit) & Section 12",
        "url": "https://labour.gov.in",
        "summary": "Every woman employee who has worked for at least 80 days in the preceding 12 months is entitled to 26 weeks of fully paid maternity leave. Dismissal or service termination during maternity leave is illegal and punishable.",
        "rights": [
            "Entitlement to 26 weeks of paid maternity leave for up to two surviving children under Section 5 (https://labour.gov.in).",
            "Complete legal prohibition on dismissal or termination of employment during maternity leave under Section 12.",
            "Right to mandatory crèche facility in establishments with 50 or more employees.",
            "Medical bonus of Rs 3,500 if pre-natal confinement and post-natal care is not provided free of charge by employer.",
        ],
        "actions": [
            "Submit written notice to employer specifying expected delivery date and start of maternity leave.",
            "If employer refuses paid leave or terminates employment, file a complaint with the Inspector under the Maternity Benefit Act.",
            "Approach the State Labour Commissioner or file an industrial dispute petition.",
        ],
        "remedies": [
            "Office of the Chief Labour Commissioner (Central) / State Labour Commissioner (https://labour.gov.in)",
            "National Commission for Women (NCW): https://ncw.nic.in",
            "Samadhan Portal: https://samadhan.labour.gov.in",
        ],
    },
]


class RightsRAGService:
    """Rights and legal explanations RAG retrieval service for Civic_AI."""

    async def query_rights(
        self,
        question: str,
        state: Optional[str] = None,
        lang: str = "en",
    ) -> RightsResponse:
        """Answer citizen rights inquiry via statutory RAG, falling back to dynamic LLM guidance."""
        clean_q = question.strip().lower()
        if not clean_q:
            raise ValueError("Query question cannot be empty.")

        # 1. Search statutory knowledgebase first
        best_match = None
        max_score = 0

        for entry in STATUTORY_KNOWLEDGEBASE:
            score = 0
            if state and entry["jurisdiction"] != "Central":
                if entry["jurisdiction"].upper() == state.upper():
                    score += 2
                else:
                    continue  # Avoid cross-state leakage

            for kw in entry["keywords"]:
                if kw in clean_q:
                    score += 1

            if score > max_score:
                max_score = score
                best_match = entry

        # 2. If not matched in statutory RAG, call dynamic_rights_llm
        if not best_match or max_score == 0:
            dynamic_response = await generate_dynamic_rights_guidance(
                question=question,
                state=state,
                lang=lang,
            )
            if dynamic_response is not None:
                return dynamic_response

            return RightsResponse(
                question=question,
                your_rights=[
                    "Not Directly Under Statutory Law: I could not locate a standalone statutory Act specifically covering this inquiry in the indexed civic repository, and live AI guidance is currently unavailable."
                ],
                what_you_can_do=[
                    "Consult your local State Legal Services Authority (SLSA) or District Legal Services Authority (DLSA) for free verified advice.",
                    "File a formal query or grievance on the National Legal Aid portal.",
                ],
                where_to_complain_or_get_free_help=[
                    "National Legal Services Authority (NALSA) Toll-Free Legal Aid Helpline: 15100",
                    "Nearest District Legal Services Authority (DLSA) at the District Court Complex",
                    "Supreme Court Legal Services Committee (sclsc.nic.in)",
                ],
                citations=[],
                has_official_source=False,
                lang=lang,
            )

        # 3. Statutory match found
        citation = Citation(
            act_name=best_match["act_name"],
            section=best_match["section"],
            url=best_match["url"],
        )

        return RightsResponse(
            question=question,
            your_rights=best_match["rights"],
            what_you_can_do=best_match["actions"],
            where_to_complain_or_get_free_help=best_match["remedies"],
            citations=[citation],
            has_official_source=True,
            lang=lang,
        )

    def get_all_topics(self) -> List[Dict[str, Any]]:
        """Return all curated statutory topics in the knowledgebase."""
        return STATUTORY_KNOWLEDGEBASE


rights_rag_service = RightsRAGService()
