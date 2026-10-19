import unittest
import tempfile
import os
import sqlite3


import salon
from salon import (
    init_db, add_service, get_services,
    add_client, get_clients,
    add_appointment, get_appointments,
)

class TestHairSalon(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
       
        cls._original_db = salon.DB_NAME
        cls._tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        salon.DB_NAME = cls._tmp.name
        init_db()


    @classmethod
    def tearDownClass(cls):
        salon.DB_NAME = cls._original_db
        if os.path.exists(cls._tmp.name):
            os.remove(cls._tmp.name)


   
    def test_01_add_service(self):
       
        before = len(get_services())


       
        add_service('Стрижка тестовая', 'Стрижка', 1500.0, 60)


       
        self.assertEqual(len(get_services()), before + 1)


   
    def test_02_get_services(self):
   
        add_service('Укладка тестовая', 'Укладка', 2000.0, 60)
   
        services = get_services()
     
        self.assertTrue(len(services) >= 1)


    def test_03_add_client(self):
     
        before = len(get_clients())

        add_client('Тестов Тест', '+7-900-000-00-01')
   
        self.assertEqual(len(get_clients()), before + 1)


   
    def test_04_add_appointment(self):
     
        add_service('Окрашивание тестовое', 'Окрашивание', 4500.0, 180)
        s = get_services('Окрашивание тестовое')[0]
        c = get_clients()[0]

        add_appointment(c[0], s[0], 1, 4500.0)

        self.assertTrue(len(get_appointments()) >= 1)


 
    def test_05_appointment_total(self):
     
        add_service('Маникюр тестовый', 'Ногти', 1200.0, 50)
        s = get_services('Маникюр тестовый')[0]
        c = get_clients()[0]

        total = 3 * s[3]  # 3 × 1200
        add_appointment(c[0], s[0], 3, total)

        self.assertEqual(get_appointments()[0][4], 3600.0)
      
 
    def test_06_search(self):
   
        add_service('Стрижка уникальная', 'Стрижка', 1500.0, 60)


   
        result = get_services('уникальная')


   
        self.assertTrue(len(result) >= 1)


   
    def test_07_duplicate_service(self):
 
        add_service('Дубль тестовый', 'Стрижка', 1000.0, 45)

        with self.assertRaises(sqlite3.IntegrityError):
            add_service('Дубль тестовый', 'Стрижка', 1000.0, 45)


if __name__ == '__main__':
    unittest.main(verbosity=2)
