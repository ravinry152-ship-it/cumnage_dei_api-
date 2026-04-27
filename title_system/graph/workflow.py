from langgraph.graph import StateGraph, END
from graph.state import DocumentState
from graph.nodes import ocr_node, parse_json_node, save_db_node, error_node

def should_continue(state: DocumentState) -> str:
    return "error" if state.get("error") else "continue"

def build_graph():
    workflow = StateGraph(DocumentState)

    # Add nodes
    workflow.add_node("ocr", ocr_node)
    workflow.add_node("parse_json", parse_json_node)
    workflow.add_node("save_db", save_db_node)
    workflow.add_node("error_handler", error_node)

    # Entry
    workflow.set_entry_point("ocr")

    # Edges
    workflow.add_conditional_edges(
        "ocr",
        should_continue,
        {"continue": "parse_json", "error": "error_handler"}
    )
    workflow.add_conditional_edges(
        "parse_json",
        should_continue,
        {"continue": "save_db", "error": "error_handler"}
    )
    workflow.add_conditional_edges(
        "save_db",
        should_continue,
        {"continue": END, "error": "error_handler"}
    )
    workflow.add_edge("error_handler", END)

    return workflow.compile()

# Singleton graph instance
document_graph = build_graph()