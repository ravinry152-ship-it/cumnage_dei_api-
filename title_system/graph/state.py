from typing import TypedDict, Optional

class DocumentState(TypedDict):
    document_id: int          # Django model ID
    image_path: str           # Path to image file
    extracted_text: Optional[str]
    parsed_json: Optional[dict]
    error: Optional[str]