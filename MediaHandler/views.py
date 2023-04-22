from django.conf import settings
from django.http import FileResponse
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView


class GetFile(APIView):

    def get(self, request, file_name, folder):
        try:
            absolute_path = settings.MEDIA_ROOT + '/' + folder + '/' + file_name
            response = FileResponse(open(absolute_path, 'rb'), as_attachment=True)
        except Exception:
            raise NotFound('File does not exist')
        return response


