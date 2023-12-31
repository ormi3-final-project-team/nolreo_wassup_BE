from django.test import TestCase
from rest_framework.test import APIClient

from lodging.models import Lodging, SubLocation, MainLocation
from traffic.models import Bus, Train, RentalCar
from .models import Pick

class TestPickLodging(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 메인 지역 생성
        main_location = MainLocation.objects.create(
            address='테스트 숙소 주소'
        )

        # 서브 지역 생성
        sub_location = SubLocation.objects.create(
            main_location=main_location, 
            address='테스트 숙소 상세주소'
        )

        # 숙소 생성
        for _ in range(1, 6):
            Lodging.objects.create(
                name='테스트 숙소',
                intro='테스트 숙소 소개',
                notice='테스트 숙소 주의사항',
                info='테스트 숙소 정보',
                sub_location=sub_location,
            )
        
        # 사용자 생성 & 로그인
        data = {
            'email': 'test@gmail.com',
            'username': 'test',
            'nickname': 'test',
            'password': 'testtest1@',
            'password2': 'testtest1@',
        }
        self.client.post(
            '/account/signup/', 
            data,
            format='multipart')
        data = {
            'email': 'test@gmail.com',
            'password': 'testtest1@',
        }
        response = self.client.post(
            '/account/login/',
            data,
            format='json')
        self.access_token = response.data['access']

    def test_pick_lodging_create(self):
        '''
        숙소 찜 생성 테스트
        1. 미로그인 상태에서 숙소 찜 생성 요청 테스트
        2. 로그인 상태에서 숙소 찜 생성 요청 테스트
        3. 중복 생성 요청 테스트
        '''
        print('-- 숙소 찜 생성 테스트 BEGIN --')
        # 미로그인 상태에서 숙소 찜 생성 요청
        data = {
            'lodging': 1,
            'pick_type': 'LG',
            'user': 1,
        }
        response = self.client.post(
            '/pick/lodging/',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], '로그인이 필요합니다.')

        # 로그인 상태에서 숙소 찜 생성 요청
        response = self.client.post(
            '/pick/lodging/',
            data=data,
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['lodging'], 1)
        self.assertEqual(response.data['pick_type'], 'LG')
        self.assertEqual(Pick.objects.all().count(), 1)

        # 중복 생성 요청
        response = self.client.post(
            '/pick/lodging/',
            data=data,
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], '이미 찜한 숙소입니다.')
        print('-- 숙소 찜 생성 테스트 END --')

    def test_pick_lodging_list(self):
        '''
        숙소 찜 리스트 조회 테스트
        1. 미로그인 상태에서 숙소 찜 리스트 조회 요청 테스트
        2. 로그인 상태에서 본인 숙소 찜 리스트 조회 요청 테스트
        '''
        print('-- 숙소 찜 리스트 조회 테스트 BEGIN --')
        data = {
            'user':1,
            'pick_type': 'LG',
        }
        for i in range(1, 6):
            self.client.post(
                '/pick/lodging/',
                data={
                    'lodging': i,
                    'pick_type': 'LG',
                    'user': 1,},
                HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
                format='json')
        # 미로그인 상태에서 숙소 찜 리스트 조회 요청
        response = self.client.get(
            '/pick/lodging/',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], '로그인이 필요합니다.')

        # 로그인 상태에서 본인 숙소 찜 리스트 조회 요청
        response = self.client.get(
            '/pick/lodging/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)
        print('-- 숙소 찜 리스트 조회 테스트 END --')

    def test_pick_lodging_delete(self):
        '''
        숙소 찜 삭제 테스트
        1. 미로그인 상태에서 숙소 찜 삭제 요청 테스트
        2. 존재하지 않는 숙소 찜 삭제 요청 테스트
        3. 다른 사용자의 숙소 찜 삭제 요청 테스트
        4. 로그인 상태에서 본인 숙소 찜 삭제 요청 테스트
        '''
        print('-- 숙소 찜 삭제 테스트 BEGIN --')
        data = {
            'user':1,
            'pick_type': 'LG',
        }
        for i in range(1, 6):
            self.client.post(
                '/pick/lodging/',
                data={
                    'lodging': i,
                    'pick_type': 'LG',
                    'user': 1,},
                HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
                format='json')
            
        # 미로그인 상태에서 숙소 찜 삭제 요청
        response = self.client.delete(
            '/pick/lodging/1/',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], '로그인이 필요합니다.')

        # 존재하지 않는 숙소 찜 삭제 요청
        response = self.client.delete(
            '/pick/lodging/10/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], '해당 숙소를 찜한 기록이 없습니다.')

        # 다른 사용자의 숙소 찜 삭제 요청
        # 사용자 생성 & 로그인
        data = {
            'email': 'test1@gmail.com',
            'username': 'test',
            'nickname': 'test1',
            'password': 'testtest1@',
            'password2': 'testtest1@',
        }
        self.client.post(
            '/account/signup/', 
            data,
            format='json')
        data = {
            'email': 'test1@gmail.com',
            'password': 'testtest1@',
        }
        response = self.client.post(
            '/account/login/',
            data,
            format='json')
        access = response.data['access']
        response = self.client.delete(
            '/pick/lodging/1/',
            HTTP_AUTHORIZATION=f'Bearer {access}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], '해당 숙소를 찜한 기록이 없습니다.')

        # 로그인 상태에서 본인 숙소 찜 삭제 요청
        response = self.client.delete(
            '/pick/lodging/1/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Pick.objects.all().count(), 4)
        print('-- 숙소 찜 삭제 테스트 END --')


class TestPickBus(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 버스 생성
        for i in range(1, 6):
            Bus.objects.create(
                depart_point = '서울',
                dest_point = '부산',
                depart_time = f'2023-12-15 12:20:00',
                arrival_time = f'2023-12-15 15:20:00',
                num = f'{1234 + i}',
                price = '10000',
            )
        
        # 사용자 생성 & 로그인
        data = {
            'email': 'test@gmail.com',
            'username': 'test',
            'nickname': 'test',
            'password': 'testtest1@',
            'password2': 'testtest1@',
        }
        self.client.post(
            '/account/signup/', 
            data,
            format='multipart')
        data = {
            'email': 'test@gmail.com',
            'password': 'testtest1@',
        }
        response = self.client.post(
            '/account/login/',
            data,
            format='json')
        self.access_token = response.data['access']

    def test_pick_bus_create(self):
        '''
        버스 찜 생성 테스트
        1. 미로그인 상태에서 버스 찜 생성 요청 테스트
        2. 로그인 상태에서 버스 찜 생성 요청 테스트
        3. 중복 생성 요청 테스트
        '''
        print('-- 버스 찜 생성 테스트 BEGIN --')
        # 미로그인 상태에서 버스 찜 생성 요청
        data = {
            'bus': 1,
            'pick_type': 'BU',
            'user': 1,
        }
        response = self.client.post(
            '/pick/bus/',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], '로그인이 필요합니다.')

        # 로그인 상태에서 버스 찜 생성 요청
        response = self.client.post(
            '/pick/bus/',
            data=data,
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['bus'], 1)
        self.assertEqual(response.data['pick_type'], 'BU')
        self.assertEqual(Pick.objects.all().count(), 1)

        # 중복 생성 요청
        response = self.client.post(
            '/pick/bus/',
            data=data,
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], '이미 찜한 버스입니다.')
        print('-- 버스 찜 생성 테스트 END --')

    def test_pick_bus_list(self):
        '''
        버스 찜 리스트 조회 테스트
        1. 미로그인 상태에서 버스 찜 리스트 조회 요청 테스트
        2. 로그인 상태에서 본인 버스 찜 리스트(찜 목록이 있는 경우) 조회 요청 테스트
        3. 로그인 상태에서 본인 버스 찜 리스트(찜 목록이 없는 경우) 조회 요청 테스트
        '''
        print('-- 버스 찜 리스트 조회 테스트 BEGIN --')
        data = {
            'user':1,
            'pick_type': 'BU',
        }
        for i in range(1, 6):
            self.client.post(
                '/pick/bus/',
                data={
                    'bus': i,
                    'pick_type': 'BU',
                    'user': 1,},
                HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
                format='json')
        # 미로그인 상태에서 버스 찜 리스트 조회 요청
        response = self.client.get(
            '/pick/bus/',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], '로그인이 필요합니다.')

        # 로그인 상태에서 본인 버스 찜 리스트(찜 목록이 있는 경우) 조회 요청
        response = self.client.get(
            '/pick/bus/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

        # 로그인 상태에서 본인 버스 찜 리스트(찜 목록이 없는 경우) 조회 요청
        data = {
            'email': 'test1@gmail.com',
            'username': 'test',
            'nickname': 'test1',
            'password': 'testtest1@',
            'password2': 'testtest1@',
        }
        self.client.post(
            '/account/signup/', 
            data,
            format='json')
        data = {
            'email': 'test1@gmail.com',
            'password': 'testtest1@',
        }
        response = self.client.post(
            '/account/login/',
            data,
            format='json')
        access = response.data['access']
        response = self.client.get(
            '/pick/bus/',
            HTTP_AUTHORIZATION=f'Bearer {access}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
        print('-- 버스 찜 리스트 조회 테스트 END --')

    def test_pick_bus_delete(self):
        '''
        버스 찜 삭제 테스트
        1. 미로그인 상태에서 버스 찜 삭제 요청 테스트
        2. 존재하지 않는 버스 찜 삭제 요청 테스트
        3. 다른 사용자의 버스 찜 삭제 요청 테스트
        4. 로그인 상태에서 본인 버스 찜 삭제 요청 테스트
        '''
        print('-- 버스 찜 삭제 테스트 BEGIN --')
        data = {
            'user':1,
            'pick_type': 'BU',
        }
        for i in range(1, 6):
            self.client.post(
                '/pick/bus/',
                data={
                    'bus': i,
                    'pick_type': 'BU',
                    'user': 1,},
                HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
                format='json')
            
        # 미로그인 상태에서 버스 찜 삭제 요청
        response = self.client.delete(
            '/pick/bus/1/',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], '로그인이 필요합니다.')

        # 존재하지 않는 버스 찜 삭제 요청
        response = self.client.delete(
            '/pick/bus/10/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], '해당 버스를 찜한 기록이 없습니다.')

        # 다른 사용자의 버스 찜 삭제 요청
        # 사용자 생성 & 로그인
        data = {
            'email': 'test1@gmail.com',
            'username': 'test',
            'nickname': 'test1',
            'password': 'testtest1@',
            'password2': 'testtest1@',
        }
        self.client.post(
            '/account/signup/', 
            data,
            format='json')
        data = {
            'email': 'test1@gmail.com',
            'password': 'testtest1@',
        }
        response = self.client.post(
            '/account/login/',
            data,
            format='json')
        access = response.data['access']
        response = self.client.delete(
            '/pick/bus/1/',
            HTTP_AUTHORIZATION=f'Bearer {access}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], '해당 버스를 찜한 기록이 없습니다.')

        # 로그인 상태에서 본인 버스 찜 삭제 요청
        response = self.client.delete(
            '/pick/bus/1/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Pick.objects.all().count(), 4)
        print('-- 버스 찜 삭제 테스트 END --')


class TestPickTrain(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 기차 생성
        for i in range(1, 6):
            Train.objects.create(
                depart_point = '서울',
                dest_point = '부산',
                depart_time = f'2023-12-15 12:{i + 20}:00',
                arrival_time = f'2023-12-15 15:{i + 20}:00',
                num = f'{1234 + i}',
                price = '10000',
            )
        
        # 사용자 생성 & 로그인
        data = {
            'email': 'test@gmail.com',
            'username': 'test',
            'nickname': 'test',
            'password': 'testtest1@',
            'password2': 'testtest1@',
        }
        self.client.post(
            '/account/signup/', 
            data,
            format='multipart')
        data = {
            'email': 'test@gmail.com',
            'password': 'testtest1@',
        }
        response = self.client.post(
            '/account/login/',
            data,
            format='json')
        self.access_token = response.data['access']

    def test_pick_train_create(self):
        '''
        기차 찜 생성 테스트
        1. 미로그인 상태에서 기차 찜 생성 요청 테스트
        2. 로그인 상태에서 기차 찜 생성 요청 테스트
        3. 중복 생성 요청 테스트
        '''
        print('-- 기차 찜 생성 테스트 BEGIN --')
        # 미로그인 상태에서 기차 찜 생성 요청
        data = {
            'train': 1,
            'pick_type': 'TR',
            'user': 1,
        }
        response = self.client.post(
            '/pick/train/',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], '로그인이 필요합니다.')

        # 로그인 상태에서 기차 찜 생성 요청
        response = self.client.post(
            '/pick/train/',
            data=data,
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['train'], 1)
        self.assertEqual(response.data['pick_type'], 'TR')
        self.assertEqual(Pick.objects.all().count(), 1)

        # 중복 생성 요청
        response = self.client.post(
            '/pick/train/',
            data=data,
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], '이미 찜한 기차입니다.')
        print('-- 기차 찜 생성 테스트 END --')
    
    def test_pick_train_list(self):
        '''
        기차 찜 리스트 조회 테스트
        1. 미로그인 상태에서 기차 찜 리스트 조회 요청 테스트
        2. 로그인 상태에서 본인 기차 찜 리스트(찜 목록이 있는 경우) 조회 요청 테스트
        3. 로그인 상태에서 본인 기차 찜 리스트(찜 목록이 없는 경우) 조회 요청 테스트
        '''
        print('-- 기차 찜 리스트 조회 테스트 BEGIN --')
        data = {
            'user':1,
            'pick_type': 'TR',
        }
        for i in range(1, 6):
            self.client.post(
                '/pick/train/',
                data={
                    'train': i,
                    'pick_type': 'TR',
                    'user': 1,},
                HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
                format='json')
        # 미로그인 상태에서 기차 찜 리스트 조회 요청
        response = self.client.get(
            '/pick/train/',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], '로그인이 필요합니다.')

        # 로그인 상태에서 본인 기차 찜 리스트(찜 목록이 있는 경우) 조회 요청
        response = self.client.get(
            '/pick/train/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

        # 로그인 상태에서 본인 기차 찜 리스트(찜 목록이 없는 경우) 조회 요청
        data = {
            'email': 'test1@gmail.com',
            'username': 'test',
            'nickname': 'test1',
            'password': 'testtest1@',
            'password2': 'testtest1@',
        }
        self.client.post(
            '/account/signup/', 
            data,
            format='json')
        data = {
            'email': 'test1@gmail.com',
            'password': 'testtest1@',
        }
        response = self.client.post(
            '/account/login/',
            data,
            format='json')
        access = response.data['access']
        response = self.client.get(
            '/pick/train/',
            HTTP_AUTHORIZATION=f'Bearer {access}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
        print('-- 기차 찜 리스트 조회 테스트 END --')

    def test_pick_train_delete(self):
        '''
        기차 찜 삭제 테스트
        1. 미로그인 상태에서 기차 찜 삭제 요청 테스트
        2. 존재하지 않는 기차 찜 삭제 요청 테스트
        3. 다른 사용자의 기차 찜 삭제 요청 테스트
        4. 로그인 상태에서 본인 기차 찜 삭제 요청 테스트
        '''
        print('-- 기차 찜 삭제 테스트 BEGIN --')
        data = {
            'user':1,
            'pick_type': 'TR',
        }
        for i in range(1, 6):
            self.client.post(
                '/pick/train/',
                data={
                    'train': i,
                    'pick_type': 'TR',
                    'user': 1,},
                HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
                format='json')
            
        # 미로그인 상태에서 기차 찜 삭제 요청
        response = self.client.delete(
            '/pick/train/1/',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], '로그인이 필요합니다.')

        # 존재하지 않는 기차 찜 삭제 요청
        response = self.client.delete(
            '/pick/train/10/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], '해당 기차를 찜한 기록이 없습니다.')

        # 다른 사용자의 기차 찜 삭제 요청
        # 사용자 생성 & 로그인
        data = {
            'email': 'test1@gmail.com',
            'username': 'test',
            'nickname': 'test1',
            'password': 'testtest1@',
            'password2': 'testtest1@',
        }
        self.client.post(
            '/account/signup/', 
            data,
            format='json')
        data = {
            'email': 'test1@gmail.com',
            'password': 'testtest1@',
        }
        response = self.client.post(
            '/account/login/',
            data,
            format='json')
        access = response.data['access']
        response = self.client.delete(
            '/pick/train/1/',
            HTTP_AUTHORIZATION=f'Bearer {access}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], '해당 기차를 찜한 기록이 없습니다.')

        # 로그인 상태에서 본인 기차 찜 삭제 요청
        response = self.client.delete(
            '/pick/train/1/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Pick.objects.all().count(), 4)
        print('-- 기차 찜 삭제 테스트 END --')


class TestPickRentalCar(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 렌터카 생성
        for i in range(1, 6):
            RentalCar.objects.create(
                model = '소나타',
                area = '서울',
                num = f'{12341 + i}',
                price = '10000',
            )
        
        # 사용자 생성 & 로그인
        data = {
            'email': 'test@gmail.com',
            'username': 'test',
            'nickname': 'test',
            'password': 'testtest1@',
            'password2': 'testtest1@',
        }
        self.client.post(
            '/account/signup/', 
            data,
            format='multipart')
        data = {
            'email': 'test@gmail.com',
            'password': 'testtest1@',
        }
        response = self.client.post(
            '/account/login/',
            data,
            format='json')
        self.access_token = response.data['access']

    def test_pick_rental_car_create(self):
        '''
        렌트카 찜 생성 테스트
        1. 미로그인 상태에서 렌트카 찜 생성 요청 테스트
        2. 로그인 상태에서 렌트카 찜 생성 요청 테스트
        3. 중복 생성 요청 테스트
        '''
        print('-- 렌트카 찜 생성 테스트 BEGIN --')
        # 미로그인 상태에서 렌트카 찜 생성 요청
        data = {
            'rental_car': 1,
            'pick_type': 'RC',
            'user': 1,
        }
        response = self.client.post(
            '/pick/rental_car/',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], '로그인이 필요합니다.')

        # 로그인 상태에서 렌트카 찜 생성 요청
        response = self.client.post(
            '/pick/rental_car/',
            data=data,
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['rental_car'], 1)
        self.assertEqual(response.data['pick_type'], 'RC')
        self.assertEqual(Pick.objects.all().count(), 1)

        # 중복 생성 요청
        response = self.client.post(
            '/pick/rental_car/',
            data=data,
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], '이미 찜한 렌트카입니다.')
        print('-- 렌트카 찜 생성 테스트 END --')

    def test_pick_rental_car_list(self):
        '''
        렌트카 찜 리스트 조회 테스트
        1. 미로그인 상태에서 렌트카 찜 리스트 조회 요청 테스트
        2. 로그인 상태에서 본인 렌트카 찜 리스트(찜 목록이 있는 경우) 조회 요청 테스트
        3. 로그인 상태에서 본인 렌트카 찜 리스트(찜 목록이 없는 경우) 조회 요청 테스트
        '''
        print('-- 렌트카 찜 리스트 조회 테스트 BEGIN --')
        data = {
            'user':1,
            'pick_type': 'RC',
        }
        for i in range(1, 6):
            self.client.post(
                '/pick/rental_car/',
                data={
                    'rental_car': i,
                    'pick_type': 'RC',
                    'user': 1,},
                HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
                format='json')
        # 미로그인 상태에서 렌트카 찜 리스트 조회 요청
        response = self.client.get(
            '/pick/rental_car/',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], '로그인이 필요합니다.')

        # 로그인 상태에서 본인 렌트카 찜 리스트(찜 목록이 있는 경우) 조회 요청
        response = self.client.get(
            '/pick/rental_car/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

        # 로그인 상태에서 본인 렌트카 찜 리스트(찜 목록이 없는 경우) 조회 요청
        data = {
            'email': 'test1@gmail.com',
            'username': 'test',
            'nickname': 'test1',
            'password': 'testtest1@',
            'password2': 'testtest1@',
        }
        self.client.post(
            '/account/signup/', 
            data,
            format='json')
        data = {
            'email': 'test1@gmail.com',
            'password': 'testtest1@',
        }
        response = self.client.post(
            '/account/login/',
            data,
            format='json')
        access = response.data['access']
        response = self.client.get(
            '/pick/rental_car/',
            HTTP_AUTHORIZATION=f'Bearer {access}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
        print('-- 렌트카 찜 리스트 조회 테스트 END --')

    def test_pick_rental_car_delete(self):
        '''
        렌트카 찜 삭제 테스트
        1. 미로그인 상태에서 렌트카 찜 삭제 요청 테스트
        2. 존재하지 않는 렌트카 찜 삭제 요청 테스트
        3. 다른 사용자의 렌트카 찜 삭제 요청 테스트
        4. 로그인 상태에서 본인 렌트카 찜 삭제 요청 테스트
        '''
        print('-- 렌트카 찜 삭제 테스트 BEGIN --')
        data = {
            'user':1,
            'pick_type': 'RC',
        }
        for i in range(1, 6):
            self.client.post(
                '/pick/rental_car/',
                data={
                    'rental_car': i,
                    'pick_type': 'RC',
                    'user': 1,},
                HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
                format='json')
            
        # 미로그인 상태에서 렌트카 찜 삭제 요청
        response = self.client.delete(
            '/pick/rental_car/1/',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], '로그인이 필요합니다.')

        # 존재하지 않는 렌트카 찜 삭제 요청
        response = self.client.delete(
            '/pick/rental_car/10/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], '해당 렌트카를 찜한 기록이 없습니다.')

        # 다른 사용자의 렌트카 찜 삭제 요청
        # 사용자 생성 & 로그인
        data = {
            'email': 'test1@gmail.com',
            'username': 'test',
            'nickname': 'test1',
            'password': 'testtest1@',
            'password2': 'testtest1@',
        }
        self.client.post(
            '/account/signup/', 
            data,
            format='json')
        data = {
            'email': 'test1@gmail.com',
            'password': 'testtest1@',
        }
        response = self.client.post(
            '/account/login/',
            data,
            format='json')
        access = response.data['access']
        response = self.client.delete(
            '/pick/rental_car/1/',
            HTTP_AUTHORIZATION=f'Bearer {access}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], '해당 렌트카를 찜한 기록이 없습니다.')

        # 로그인 상태에서 본인 렌트카 찜 삭제 요청
        response = self.client.delete(
            '/pick/rental_car/1/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            data=data,
            format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Pick.objects.all().count(), 4)
        print('-- 렌트카 찜 삭제 테스트 END --')

class TestPick(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # 사용자 생성 & 로그인
        data = {
            'email': 'test@gmail.com',
            'username': 'test',
            'nickname': 'test',
            'password': 'testtest1@',
            'password2': 'testtest1@',
        }
        self.client.post(
            '/account/signup/', 
            data,
            format='multipart')
        data = {
            'email': 'test@gmail.com',
            'password': 'testtest1@',
        }
        response = self.client.post(
            '/account/login/',
            data,
            format='json')
        self.access_token = response.data['access']

        # 메인 지역 생성
        main_location = MainLocation.objects.create(
            address='테스트 숙소 주소'
        )

        # 서브 지역 생성
        sub_location = SubLocation.objects.create(
            main_location=main_location, 
            address='테스트 숙소 상세주소'
        )

        # 숙소 생성
        for _ in range(1, 6):
            Lodging.objects.create(
                name='테스트 숙소',
                intro='테스트 숙소 소개',
                notice='테스트 숙소 주의사항',
                info='테스트 숙소 정보',
                sub_location=sub_location,
            )

        # 숙소 찜 생성
        data = {
            'user':1,
            'pick_type': 'LG',
        }
        for i in range(1, 6):
            self.client.post(
                '/pick/lodging/',
                data={
                    'lodging': i,
                    'pick_type': 'LG',
                    'user': 1,},
                HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
                format='json')

        # 버스 생성
        for i in range(1, 6):
            Bus.objects.create(
                depart_point = '서울',
                dest_point = '부산',
                depart_time = f'2023-12-15 12:20:00',
                arrival_time = f'2023-12-15 15:20:00',
                num = f'{1234 + i}',
                price = '10000',
            )

        # 버스 찜 생성
        data = {
            'user':1,
            'pick_type': 'BU',
        }
        for i in range(1, 6):
            self.client.post(
                '/pick/bus/',
                data={
                    'bus': i,
                    'pick_type': 'BU',
                    'user': 1,},
                HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
                format='json')

        # 기차 생성
        for i in range(1, 6):
            Train.objects.create(
                depart_point = '서울',
                dest_point = '부산',
                depart_time = f'2023-12-15 12:{i + 20}:00',
                arrival_time = f'2023-12-15 15:{i + 20}:00',
                num = f'{1234 + i}',
                price = '10000',
            )

        # 기차 찜 생성
        data = {
            'user':1,
            'pick_type': 'TR',
        }
        for i in range(1, 6):
            self.client.post(
                '/pick/train/',
                data={
                    'train': i,
                    'pick_type': 'TR',
                    'user': 1,},
                HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
                format='json')

        # 렌터카 생성
        for i in range(1, 6):
            RentalCar.objects.create(
                model = '소나타',
                area = '서울',
                num = f'{12341 + i}',
                price = '10000',
            )

        # 렌터카 찜 생성
        data = {
            'user':1,
            'pick_type': 'RC',
        }
        for i in range(1, 6):
            self.client.post(
                '/pick/rental_car/',
                data={
                    'rental_car': i,
                    'pick_type': 'RC',
                    'user': 1,},
                HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
                format='json')
        

    def test_pick_list(self):
        '''
        전체 찜 목록 테스트
        '''
        print('-- 전체 찜 목록 테스트 BEGIN --')
        # 전체 찜 목록 정상 조회
        response = self.client.get(
            '/pick/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 20)
        print('-- 전체 찜 목록 테스트 END --')