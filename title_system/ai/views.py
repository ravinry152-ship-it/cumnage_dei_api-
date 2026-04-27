from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from mytitle.models import CRUD
from mytitle.serializers import CRUDSerializer
from graph.workflow import document_graph
import threading

def run_graph_background(document_id: int, image_path: str):
    """Run LangGraph in background thread"""
    document_graph.invoke({
        "document_id": document_id,
        "image_path": image_path,
        "extracted_text": None,
        "parsed_json": None,
        "error": None
    })

class DocumentUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = CRUDSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Save document record
        doc = serializer.save()

        # Run graph in background (non-blocking)
        thread = threading.Thread(
            target=run_graph_background,
            args=(doc.id, doc.image.path)
        )
        thread.start()

        return Response({
            "message": "Image uploaded successfully. Processing started.",
            "document_id": doc.id,
            "status": doc.status
        }, status=status.HTTP_202_ACCEPTED)


# class DocumentResultView(APIView):
#     """GET /api/documents/<id>/result/"""

#     def get(self, request, pk):
#         try:
#             doc = CRUD.objects.get(pk=pk)
#         except CRUD.DoesNotExist:
#             return Response({"error": "Document not found"}, status=404)

#         serializer = CRUDSerializer(doc)
#         return Response(serializer.data)


# class DocumentListView(APIView):
#     """GET /api/documents/"""

#     def get(self, request):
#         docs = CRUD.objects.all().order_by('-created_at')
#         serializer = CRUDSerializer(docs, many=True)
#         return Response(serializer.data)