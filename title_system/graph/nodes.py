import base64
import json
from django.conf import settings
from langchain_groq import ChatGroq
import os
from langchain_core.messages import HumanMessage
llm_vision = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    api_key=os.environ.get("GROQ_API_KEY")
)
llm_text = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.environ.get("GROQ_API_KEY")
)

def update_document_status(doc_id: int, status: str, **kwargs):
    from mytitle.models import CRUD
    CRUD.objects.filter(id=doc_id).update(status=status, **kwargs)

# ── Node 2: Image → Text ──────────────────────────────
def ocr_node(state: dict) -> dict:
    print(f"OCR Node - Document #{state.get('document_id')}")
    doc_id = state.get('document_id')
    update_document_status(doc_id, 'processing')

    try:
        with open(state["image_path"], "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # Use the vision model here
        message = llm_vision.invoke([
            HumanMessage(content=[
                {"type": "text", "text": "Extract all text from this image. Output raw text only."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_data}"}
                },
            ])
        ])

        return {**state, "extracted_text": message.content}

    except Exception as e:
        # Crucial: return 'error' key so the graph can route to error_node
        return {**state, "error": f"OCR failed: {str(e)}"}


# ── Node 3: Text → JSON ───────────────────────────────
def parse_json_node(state: dict) -> dict:
    if "error" in state: return state
    print(f"Parse JSON Node - Document #{state['document_id']}")
    prompt = f"""
    Convert this text to valid JSON. 
    Expected Keys:
    - "name": (String) The name of the item or person
    - "price": (Number/Decimal) The cost or price
    - "village": (String) The location or village name

    Return ONLY valid JSON.
    Text:
    {state['extracted_text']}
    """
    try:
        # Use the text-optimized model for logic/structuring
        message = llm_text.invoke([
            HumanMessage(content=prompt)
        ])

        content = message.content.strip()
        # Remove potential Markdown fences
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        parsed = json.loads(content.strip())
        return {**state, "parsed_json": parsed}

    except Exception as e:
        return {**state, "error": f"Parse JSON failed: {str(e)}"}


# ── Node 4: Save to Django DB ─────────────────────────
def save_db_node(state: dict) -> dict:
    if "error" in state: return state
    
    try:
        from mytitle.models import CRUD
        data = state.get("parsed_json", {})
        
        # ទាញយកទិន្នន័យពី JSON មកដាក់ក្នុង Field នីមួយៗ
        CRUD.objects.filter(id=state['document_id']).update(
            name=data.get("name", "Unknown"),
            price=data.get("price", 0),
            village=data.get("village", "N/A"),
            status='success'
        )
        return state
    except Exception as e:
        return {**state, "error": f"Save DB failed: {str(e)}"}

# ── Node 5: Error Handler ─────────────────────────────
def error_node(state: dict) -> dict:
    error_msg = state.get('error', 'Unknown error')
    print(f"Error - Document #{state.get('document_id')}: {error_msg}")
    
    update_document_status(
        state['document_id'],
        'error',
        # Ensure your model has this field
        # error_message=error_msg 
    )
    return state