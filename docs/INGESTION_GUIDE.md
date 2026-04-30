# Zedchatbot Data Ingestion Guide 🇿🇲🦓

This guide explains how to add new official documents to your chatbot's knowledge base to make it smarter and more helpful for the Zambian community.

---

## 1. Where to Source Documents
To ensure the chatbot provides **trusted** information, only download documents from official `.gov.zm` or `.ac.zm` websites.

| Domain | Source Website | Document Types to Look For |
| :--- | :--- | :--- |
| **Tax** | [zra.org.zm](https://www.zra.org.zm) | Taxpayer Charter, E-service guides, TPIN manuals. |
| **Health** | [nhima.co.zm](https://www.nhima.co.zm) | Member handbooks, accredited facility lists. |
| **Education** | [exams-council.org.zm](https://www.exams-council.org.zm) | Candidate guidelines, registration procedures. |
| **University** | [unza.zm](https://www.unza.zm) | Student handbook, academic regulations, OAP guides. |
| **Legal** | [parliament.gov.zm](http://www.parliament.gov.zm) | Acts of Parliament (e.g., Public Health Act). |

---

## 2. The Ingestion Workflow

### **Step 1: Organize the Files**
Place your downloaded files into the correct subdirectory inside `data/raw/zm/`.
*   **Government info:** `data/raw/zm/government/`
*   **Education info:** `data/raw/zm/education/`
*   **Health info:** `data/raw/zm/health/`

### **Step 2: Clean the Vector Store (Hard Reset)**
To prevent duplicate answers and ensure the highest accuracy, clear the old database before re-indexing.
1.  **Stop the API server** (Close the terminal running `src/main.py`).
2.  **Run this command** in PowerShell:
    ```powershell
    Remove-Item -Recurse -Force vector_store/zm
    ```

### **Step 3: Run the Indexing Script**
Run the automated script to process your new files:
```powershell
python scripts/build_index.py
```
*The script will read all PDFs and TXT files, chunk them, and save them to the vector store.*

### **Step 4: Verify the New Knowledge**
1.  Start the server: `python src/main.py`
2.  Open your browser: `http://localhost:5500`
3.  Ask a question specifically about the new document you just added.

---

## 3. Supported Formats
The system currently supports:
*   **PDF (.pdf)**: Best for official manuals and handbooks.
*   **Text (.txt)**: Best for simple lists or small guides.

---

## 4. Tips for High Accuracy
*   **File Names:** Give your files clear names (e.g., `zra_tpin_guide_2024.pdf`).
*   **Text Quality:** If a PDF is just an image (cannot highlight text), the chatbot won't be able to read it. Use "Searchable" PDFs only.
*   **Small Chunks:** Our system automatically breaks large files into 500-character chunks to ensure the AI doesn't get overwhelmed.
