# Evidence of Results: Research Objective One
**Project:** ZedChatBot for African Community
**Researcher:** Francis Chileshe

This document provides the empirical results produced by the ZedChatBot RAG pipeline, demonstrating native multilingual support and accurate information retrieval from the curated Zambian knowledge base.

---

## Result 1: Government Services (Tax Calculation)
**Scenario:** A user asks for a tax calculation in Nyanja for a specific salary.
- **Input (Nyanja):** "Ndimagwira ntchito ndipo malipiro anga ndi K8,000 pamwezi. Kodi ndizilipira misonkho yanji?"
- **Retrieved Context:** `data/raw/zm/government/zra_tax_2024.txt` (K5,100 tax-free threshold).
- **Bot Output:** "Malinga ndi zomwe zaperekedwa... msonkho wake uwerengedwe motere: K5,100 yoyamba ndi yopanda msonkho. K2,900 yotsatira idzalipidwa msonkho ndi 30%. Tax = 870 ZMW. Net Income = 7,130 ZMW."
- **Verdict:** ✅ Correct data extraction and accurate mathematical reasoning in Nyanja.

---

## Result 2: Civic Identity (NRC Application)
**Scenario:** A user asks about requirements for a national ID card in Nyanja.
- **Input (Nyanja):** "Ndikufuna NRC, ndizofunika chiyani?"
- **Retrieved Context:** `data/raw/zm/government/nrc_passport_guide.txt`.
- **Bot Output:** "Kuti mulembetse NRC, muyenera kukhala ndi zaka 16 kapena kupitilira apo... muyenera kupita ndi wachibale kapena woyang'anira wovomerezeka... Mtengo wopereka koyamba ndi waulere."
- **Verdict:** ✅ Successfully identified the age and deponent requirements from official guidelines.

---

## Result 3: Utilities (ZESCO Emergency Tariffs)
**Scenario:** A user asks about current electricity costs in Nyanja.
- **Input (Nyanja):** "Kodi ZESCO imalipiritsa bwanji magetsi mu 2024?"
- **Retrieved Context:** `data/raw/zm/utilities/zesco_tariffs_2024.txt` (Nov 1, 2024 Emergency Rates).
- **Bot Output:** "Malinga ndi zolemba zathu... Mitengo yadzidzidziyi idayamba kugwira ntchito pa Novembala 1, 2024. Mtengo wa R1 (Lifeline) ndi K0.35 pa kWh."
- **Verdict:** ✅ Accurately retrieved the most recent 2024 emergency tariff data.

---

## Result 4: Health (Cholera Emergency Guidance)
**Scenario:** A user seeks urgent health advice in English.
- **Input (English):** "What should I do if I think I have Cholera?"
- **Retrieved Context:** `data/raw/zm/health/disease_guidance.txt`.
- **Bot Output:** "If you think you have Cholera, start Oral Rehydration Salts (ORS) or Salt and Sugar Solution (SSS) immediately. Then, report to the nearest health facility or Cholera Treatment Center (CTC) without delay."
- **Verdict:** ✅ Provided high-priority, life-saving information correctly.

---

## Result 5: Education (ECZ Results)
**Scenario:** A user asks how to check exam results in Bemba.
- **Input (Bemba):** "nshila nshi yakumwenamo ama results yama exam pa ECZ?"
- **Retrieved Context:** `data/raw/zm/education/ecz_results_guide.txt`.
- **Bot Output:** "Nga mulefwaya ukufwailisha... 1. Kabiyeni pa portal.exams-council.org.zm... 2. Saleni Isambililo (Grade 7, 9, nelyo 12)..."
- **Verdict:** ✅ Successfully provided the step-by-step digital process in Bemba.
