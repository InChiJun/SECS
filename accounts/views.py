import json

import bcrypt
import jwt

from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.http import JsonResponse
from SECS.settings import SECRET_KEY

from .models import User


# -- Login
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    # post 로 받은 request 데이터를 인자로 받는다
    def post(self, request):
        data = request.POST
        try:
            # request로 받아온 email 값이 존재한다면
            if User.objects.filter(email=data['email']).exists():
                # user 객체를 새로 만든다. User 데이터 중 email=data['email']인 데이터를 새로운 객체로 만든다
                user = User.objects.get(email=data['email'])
                user_password = user.password.encode('utf-8')

                # 비밀번호를 인코딩 한 값과 현재 DB에 저장된 암호화된 값을 비교한다
                if bcrypt.checkpw(data['password'].encode('utf-8'), user_password):
                    # 비밀번호가 맞다면 토큰을 발행하고, 토큰 값에는 email(PK)을 넣어 발행한다
                    token = jwt.encode({'email': user.email}, SECRET_KEY, algorithm="HS256")
                    request.session['token'] = token
                    # return 시 JsonResponse에 Access token을 넣는다
                    return render(request, 'main.html', {'email': user.email})
                else:
                    return JsonResponse({'message': '비밀번호가 틀렸습니다.'}, json_dumps_params={'ensure_ascii': False},
                                        status=401)
            else:
                return JsonResponse({'message': 'ID가 존재하지 않습니다.'}, json_dumps_params={'ensure_ascii': False},
                                    status=400)

        except KeyError as e:
            return JsonResponse({'message': e.args}, status=400)


def logout(request):
    if 'token' in request.session:
        del request.session['token']
        return redirect('http://127.0.0.1:8000/')
    else:
        return JsonResponse({'message': '로그인 상태가 아닙니다.'}, json_dumps_params={'ensure_ascii': False},
                            status=400)


# -- SignUp
class SignUpView(View):
    def get(self, request):
        return render(request, 'signUp.html')

    # post 방식으로 요청할 경우 회원가입한다
    def post(self, request):
        data = request.POST
        if data['password'] == data['confirm_password']:
            # 암호화되지 않은 비밀번호를 따로 저장한다
            password_not_hashed = data['password']
            # bcrypt를 사용하여 비밀번호를 암호화한다
            hashed_password = bcrypt.hashpw(password_not_hashed.encode('utf-8'), bcrypt.gensalt())

            try:
                # User 테이블에 저장한다
                User(
                    name=data['name'],
                    email=data['email'],
                    password=hashed_password.decode('utf-8')  # 암호화된 비밀번호 저장
                ).save()

                return render(request, 'signUp_done.html')

            except KeyError:
                return JsonResponse({'message': 'INVALID_KEYS'}, json_dumps_params={'ensure_ascii': False}, status=400)
        else:
            return render(request, 'signUp.html', {'ERROR': '비밀번호가 일치하지 않습니다'})