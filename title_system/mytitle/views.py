from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import CreateSystem, CRUD
from .serializers import CreateSystemSerializer, CRUDSerializer
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.tokens import RefreshToken
#from django.conf import settings
# from django.contrib.auth import authenticate, login
# from urllib3 import request
#==================================Register_API==============================
class Register(APIView) :
    permission_classes = [AllowAny] 
    authentication_classes = []
    def post(self , request , format =None) :
        try :
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            if not email or not password or not username :
                return Response({
                    'error': "Username, email, and password are required"
                }, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(username=username).exists():
                return Response({'error': 'គណនីនេះត្រូវបានចុះឈ្មោះរួចហេីយ'}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email=email).exists():
                return Response({'error': 'គណនីនេះធ្លាប់បានចុះឈ្មោះរួចហេីយ'}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.create_user(username=username, email=email, password=password)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        except Exception as e :
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#====================================Login_api======================================

class Login(APIView) :
    permission_classes = [AllowAny,] 
    def post(self , request , format=None) :
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password or not username :
            return Response({
                'error': "សូមបញ្ចូល Email និងលេខសម្ងាត់ និងឈ្មោះអ្នកប្រើប្រាស់ឪ្យបានត្រឹមត្រូវ"   
            }, status=status.HTTP_400_BAD_REQUEST)
        try :
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist :
            return Response({
                'error': "មិនមានគណនីប្រើប្រាស់អុីម៉ែលនេះទេ"
            }, status=status.HTTP_404_NOT_FOUND)
        if user_obj is not None :
            if user_obj.check_password(password):
                #login(request, user_obj)
                refresh = RefreshToken.for_user(user_obj)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'username': username
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': "ពាក្យសម្ងាត់ឬអុឺម៉ែលមិនត្រឹមត្រូវ"
                }, status=status.HTTP_400_BAD_REQUEST)
            
#====================================Login whit google======================================
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:8000/accounts/google/login/callback/" 
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user = User.objects.get(email=response.data['user']['email'])
            refresh = RefreshToken.for_user(user)
            response.data['refresh'] = str(refresh)
            response.data['access'] = str(refresh.access_token)
            response.data['username'] = user.username
        return response
    
# ====================================User Setup syatem======================================
class SetupSystem(APIView) :
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request, format = None):
        createsysyem = CreateSystem.objects.filter(user = request.user)
        serializer = CreateSystemSerializer(createsysyem, many= True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self , request, format = None) :
        if CreateSystem.objects.filter(user=request.user).exists():
            return Response(
                {"error": "អ្នកមានប្រព័ន្ធគ្រប់គ្រងរួចហើយ មិនអាចបង្កើតថ្មីបានទេ"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CreateSystemSerializer(data=request.data)
        if serializer.is_valid():
            # . បញ្ចូល user ទៅក្នុង serializer ដោយស្វ័យប្រវត្តិ
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#====================================User setup system detail======================================    
class SetupSystemDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            # ត្រូវឆែកទាំង ID និង ម្ចាស់ (User)
            return CreateSystem.objects.get(pk=pk, user=user)
        except CreateSystem.DoesNotExist:
            return None
        
    def get(self, request, pk, format=None):
        createsystem = self.get_object(pk, request.user)
        if not createsystem:
            return Response({'error': 'រកមិនឃើញប្រព័ន្ធ ឬអ្នកគ្មានសិទ្ធិ'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CreateSystemSerializer(createsystem)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        createsystem = self.get_object(pk, request.user)
        if not createsystem:
            return Response({'error': 'រកមិនឃើញប្រព័ន្ធ'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = CreateSystemSerializer(createsystem, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        createsystem = self.get_object(pk, request.user)
        if not createsystem:
            return Response({'error': 'រកមិនឃើញប្រព័ន្ធ'}, status=status.HTTP_404_NOT_FOUND)
        createsystem.delete()
        return Response({'message': 'បានលុបប្រព័ន្ធជោគជ័យ'}, status=status.HTTP_204_NO_CONTENT)
    
#====================================CURD data=========================================
class UserData(APIView) :
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self , request, format = None) :
        data = CRUD.objects.filter(user=request.user)
        serializer = CRUDSerializer(data, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #=========================Post data================================================
    def post(self, request):
        serializer = CRUDSerializer(data=request.data)
        if serializer.is_valid():
            try:
                #  ចាប់យក System របស់ User ដែលកំពុង Login
                user_system = request.user.system 
                
                #  រក្សាទុកដោយបញ្ចូល system និង user អូតូ
                serializer.save(system=user_system, user=request.user)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except CreateSystem.DoesNotExist:
                return Response(
                    {"error": "អ្នកត្រូវបង្កើត System ជាមុនសិន ទើបអាចបញ្ចូលទិន្នន័យបាន"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #========================Data detail=================================================
class UserDataDetail(APIView) :
        permission_classes = [IsAuthenticatedOrReadOnly]
        def get_object(self , pk) :
            try :
                return CRUD.objects.get(pk= pk)
            except CRUD.DoesNotExist :
                return None
            
        def get(self , request , pk , format = None) :
            userdata = self.get_object(pk)
            if not userdata :
                return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = CRUDSerializer(userdata)
            return Response(serializer.data)
        def put(self , request , pk , format = None) :
            userdata = self.get_object(pk)
            if not userdata :
                return Response({
                    'error' : 'data not found'

                }, status= status.HTTP_404_NOT_FOUND)
            serializer = CRUDSerializer(userdata, data = request.data)
            if serializer.is_valid() :
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        def delete(self, request, pk, format=None):
            userdata = self.get_object(pk)
            if not userdata:
                return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
            userdata.delete()
            return Response({'message': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)

