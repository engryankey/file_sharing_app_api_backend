from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# this class enables the jwt send these extra info with tokens when user logins
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data['name'] = self.user.first_name+" "+self.user.last_name
        data['email'] = self.user.email
        data['username'] = self.user.username
        data['isAdmin'] = self.user.is_staff
        
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
