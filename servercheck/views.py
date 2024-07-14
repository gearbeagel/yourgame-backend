from rest_framework.decorators import api_view
from rest_framework.response import Response


# Create your views here.
@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'Yippie!'})


@api_view(['GET'])
def username(request):
    if request.user.is_authenticated:
        user = request.user.username
    else:
        user = "Anonymous"
    return Response({"user": user})
