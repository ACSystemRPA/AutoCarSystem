import unittest
from app import create_app, db
from app.models import Empresa, Usuario

class Fase1TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret'
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_company_registration_and_login(self):
        # Register new company
        res = self.client.post('/auth/register', data={
            'razao_social': 'Auto Center Premium Ltda',
            'nome_fantasia': 'Auto Center Premium',
            'cnpj': '33.333.333/0001-33',
            'nome': 'Admin Master',
            'email': 'admin@premium.com',
            'senha': 'Password@123',
            'confirmar_senha': 'Password@123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Verify company and user in DB
        empresa = Empresa.query.filter_by(cnpj='33.333.333/0001-33').first()
        self.assertIsNotNone(empresa)
        self.assertEqual(empresa.razao_social, 'Auto Center Premium Ltda')

        user = Usuario.query.filter_by(email='admin@premium.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.empresa_id, empresa.id)
        self.assertTrue(user.check_password('Password@123'))

        # Login
        login_res = self.client.post('/auth/login', data={
            'email': 'admin@premium.com',
            'senha': 'Password@123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Auto Center Premium', login_res.data)

    def test_auth_protection(self):
        # Access protected route without login
        res = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/auth/login', res.headers['Location'])

if __name__ == '__main__':
    unittest.main()
