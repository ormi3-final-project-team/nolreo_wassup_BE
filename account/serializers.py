from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.core.validators import MinLengthValidator, MaxLengthValidator

from .models import CustomUser as User

class SignupSerializer(ModelSerializer):
    '''
    회원가입 serializer
    '''
    password = serializers.CharField(
        style={'input_type': 'password'}, 
        write_only=True,
        validators=[MinLengthValidator(8, '비밀번호는 8글자 이상 15글자 이하로 입력해주세요.'), MaxLengthValidator(15, '비밀번호는 8글자 이상 15글자 이하로 입력해주세요.')],
    )
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'nickname', 'password', 'password2', 'image']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        '''
        사용자 생성 메서드
        '''
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            nickname=validated_data['nickname'],
        )
        if validated_data.get('image'):
            user.image = validated_data['image']
        user.set_password(validated_data['password'])
        return user
    
    def validate_password(self, value):
        '''
        비밀번호 유효성 검사 메서드
        '''
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("비밀번호는 숫자를 포함해야 합니다.")
        
        if not any(char in '!@#$%^&*()_+' for char in value):
            raise serializers.ValidationError("비밀번호는 특수문자를 포함해야 합니다.")
        
        password2 = self.initial_data.get('password2')
        if value != password2:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return value