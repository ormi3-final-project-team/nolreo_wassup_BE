from django.test import TestCase
from rest_framework.test import APIClient

from account.models import CustomUser as User
from traffic.models import Bus

class TestBusCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # 버스 데이터 생성
        for i in range(10):
            Bus.objects.create(
                depart_point = '서울',
                dest_point = '부산',
                depart_time = f'2024-12-15 12:{i + 20}:00',
                arrival_time = f'2024-12-15 15:{i + 20}:00',
                num = f'{1234 + i}',
                price = '10000',
            )

    def admin(self):
        '''
        관리자 생성
        '''
        user = User.objects.create_superuser(
            email='test@gmail.com',
            username='test',
            nickname='test',
            password='testtest1@',
        )
        # 로그인
        response = self.client.post(
            '/account/login/',
            {'email': 'test@gmail.com',
            'password': 'testtest1@'},
            format='json')
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        user.save()
        return user
    
    def user(self):
        '''
        사용자 생성
        '''
        user = User.objects.create_user(
            email='test1@gmail.com',
            username='test1',
            nickname='test2',
            password='testtest1@',
        )
        # 로그인
        response = self.client.post(
            '/account/login/',
            {'email': 'test1@gmail.com',
            'password': 'testtest1@'},
            format='json')
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        user.save()
        return user

    def test_bus_create_admin(self):
        '''
        버스 생성 테스트(관리자)
        '''
        print('-- 버스 생성 테스트(관리자) BEGIN --')
        # 정상 처리 테스트
        self.admin()
        bus_data = {
            'depart_point': '서울',
            'dest_point': '부산',
            'depart_time': '2024-12-12 12:00:00',
            'arrival_time': '2024-12-12 15:00:00',
            'num': '2234',
            'price': '10000',
        }
        response = self.client.post('/traffic/bus/', bus_data, format='json')
        self.assertEqual(response.status_code, 201)
        # 비정상 처리 테스트 - 출발지와 도착지가 같을 경우
        bus_data = {
            'depart_point': '서울',
            'dest_point': '서울',
            'depart_time': '2023-12-12 12:00:00',
            'arrival_time': '2023-12-12 15:00:00',
            'num': '1234',
            'price': '10000',
        }
        response = self.client.post('/traffic/bus/', bus_data, format='json')
        self.assertEqual(response.status_code, 400)
        # 비정상 처리 테스트 - 출발시간이 도착시간보다 늦을 경우
        bus_data = {
            'depart_point': '서울',
            'dest_point': '부산',
            'depart_time': '2023-12-12 16:00:00',
            'arrival_time': '2023-12-12 15:00:00',
            'num': '1234',
            'price': '10000',
        }
        response = self.client.post('/traffic/bus/', bus_data, format='json')
        self.assertEqual(response.status_code, 400)
        # 비정상 처리 테스트 - 출발시간이 현재시간보다 빠를 경우
        current_time = '2023-12-12 10:00:00'
        bus_data = {
            'depart_point': '서울',
            'dest_point': '서울',
            'depart_time': '2023-12-12 09:00:00',
            'arrival_time': '2023-12-12 15:00:00',
            'num': '1234',
            'price': '10000',
        }
        response = self.client.post('/traffic/bus/', bus_data, format='json')
        self.assertEqual(response.status_code, 400)
        # 비정상 처리 테스트 - 도착시간이 현재시간보다 빠를 경우
        current_time = '2023-12-12 10:00:00'
        bus_data = {
            'depart_point': '서울',
            'dest_point': '부산',
            'depart_time': '2023-12-12 09:00:00',
            'arrival_time': '2023-12-12 09:30:00',
            'num': '1234',
            'price': '10000',
        }
        response = self.client.post('/traffic/bus/', bus_data, format='json')
        self.assertEqual(response.status_code, 400)
        # 비정상 처리 테스트 - 출발시간이 현재시간과 같을 경우
        current_time = '2023-12-12 10:00:00'
        bus_data = {
            'depart_point': '서울',
            'dest_point': '부산',
            'depart_time': '2023-12-12 10:00:00',
            'arrival_time': '2023-12-12 10:30:00',
            'num': '1234',
            'price': '10000',
        }
        response = self.client.post('/traffic/bus/', bus_data, format='json')
        self.assertEqual(response.status_code, 400)
        # 비정상 처리 테스트 - 도착시간이 현재시간과 같을 경우
        current_time = '2023-12-12 10:00:00'
        bus_data = {
            'depart_point': '서울',
            'dest_point': '부산',
            'depart_time': '2023-12-12 09:00:00',
            'arrival_time': '2023-12-12 10:00:00',
            'num': '1234',
            'price': '10000',
        }
        response = self.client.post('/traffic/bus/', bus_data, format='json')
        self.assertEqual(response.status_code, 400)
        print('-- 버스 생성 테스트(관리자) END --')

    def test_bus_create_user(self):
        '''
        버스 생성 테스트(일반 사용자)
        '''
        print('-- 버스 생성 테스트(일반 사용자) BEGIN --')
        # 비정상 처리 테스트(일반 사용자가 버스 생성 시도)
        self.user()
        bus_data = {
            'depart_point': '서울',
            'dest_point': '부산',
            'depart_time': '2023-12-15 12:00:00',
            'arrival_time': '2023-12-15 15:00:00',
            'num': '1234',
            'price': '10000',
        }
        response = self.client.post('/traffic/bus/', bus_data, format='json')
        self.assertEqual(response.status_code, 403)

        print('-- 버스 생성 테스트(일반 사용자) END --')
    
    def test_bus_list(self):
        '''
        버스 리스트 테스트
        '''
        print('-- 버스 리스트 테스트 BEGIN --')
        # 정상 처리 테스트
        response = self.client.get('/traffic/bus/', format='json')
        self.assertEqual(response.status_code, 200)
        print('-- 버스 리스트 테스트 END --')

    def test_bus_destroy_admin(self):
        '''
        버스 삭제 테스트(관리자)
        '''
        print('-- 버스 삭제 테스트(관리자) BEGIN --')
        # 정상 처리 테스트
        self.admin()
        response = self.client.delete('/traffic/bus/1/', format='json')
        self.assertEqual(response.status_code, 204)
        # 비정상 처리 테스트 - 존재하지 않는 버스 삭제 시도
        response = self.client.delete('/traffic/bus/100/', format='json')
        self.assertEqual(response.status_code, 404)
        print('-- 버스 삭제 테스트(관리자) END --')
    
    def test_bus_destroy_user(self):
        '''
        버스 삭제 테스트(일반 사용자)
        '''
        print('-- 버스 삭제 테스트(일반 사용자) BEGIN --')
        # 비정상 처리 테스트 - 일반 사용자가 버스 삭제 시도
        self.user()
        response = self.client.delete('/traffic/bus/1/', format='json')
        self.assertEqual(response.status_code, 403)
        print('-- 버스 삭제 테스트(일반 사용자) END --')

    def test_bus_retrieve(self):
        '''
        버스 조회 테스트
        '''
        print('-- 버스 조회 테스트 BEGIN --')
        # 정상 처리 테스트
        response = self.client.get('/traffic/bus/1/', format='json')
        self.assertEqual(response.status_code, 200)
        # 비정상 처리 테스트 - 존재하지 않는 버스 조회 시도
        response = self.client.get('/traffic/bus/100/', format='json')
        self.assertEqual(response.status_code, 404)
        print('-- 버스 조회 테스트 END --')

    def test_bus_update_admin(self):
        '''
        버스 수정 테스트(관리자)
        '''
        print('-- 버스 수정 테스트(관리자) BEGIN --')
        # 정상 처리 테스트
        self.admin()
        bus_data = {
            'depart_point': '서울',
            'dest_point': '대구',
            'depart_time': '2024-12-16 12:00:00',
            'arrival_time': '2024-12-16 15:00:00',
            'num': '1234',
            'price': '10000',
        }
        response = self.client.put('/traffic/bus/1/', bus_data, format='json')
        self.assertEqual(response.status_code, 200)
        # 비정상 처리 테스트 - 존재하지 않는 버스 수정 시도
        response = self.client.put('/traffic/bus/100/', bus_data, format='json')
        self.assertEqual(response.status_code, 404)
        print('-- 버스 수정 테스트(관리자) END --')

    def test_bus_update_user(self):
        '''
        버스 수정 테스트(일반 사용자)
        '''
        print('-- 버스 수정 테스트(일반 사용자) BEGIN --')
        # 비정상 처리 테스트 - 일반 사용자가 버스 수정 시도
        self.user()
        response = self.client.get('/traffic/bus/1/', format='json')
        bus_data = {
            'depart_point': '서울',
            'dest_point': '부산',
            'depart_time': '2023-12-15 12:00:00',
            'arrival_time': '2023-12-15 15:00:00',
            'num': '1234',
            'price': '10000',
        }
        response = self.client.put('/traffic/bus/1/', bus_data, format='json')
        self.assertEqual(response.status_code, 403)
        print('-- 버스 수정 테스트(일반 사용자) END --')
