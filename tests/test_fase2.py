import unittest
from app import create_app, db
from app.models import Empresa, Usuario, Cliente, Veiculo, Peca, Servico

class Fase2TestCase(unittest.TestCase):
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
        
        # Setup Empresas e Usuários de teste
        self.emp1 = Empresa(razao_social="Alpha Motors Ltda", nome_fantasia="Oficina Alpha Motors", nif="11.111.111/0001-11")
        db.session.add(self.emp1)
        db.session.flush()
        
        self.user1 = Usuario(empresa_id=self.emp1.id, nome="Carlos Alpha", email="carlos@alpha.com", papel="admin")
        self.user1.set_password("senha123")
        db.session.add(self.user1)

        self.emp2 = Empresa(razao_social="Beta Car Ltda", nome_fantasia="Oficina Beta Car", nif="22.222.222/0001-22")
        db.session.add(self.emp2)
        db.session.flush()
        
        self.user2 = Usuario(empresa_id=self.emp2.id, nome="Roberto Beta", email="roberto@beta.com", papel="admin")
        self.user2.set_password("senha123")
        db.session.add(self.user2)
        
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post('/auth/login', data={'email': email, 'senha': password}, follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)

    def test_clientes_crud_and_isolation(self):
        self.login('carlos@alpha.com', 'senha123')
        
        res = self.client.post('/clientes/novo', data={
            'nome': 'João Silva',
            'nif': '123.456.789-00',
            'telefone': '11999998888',
            'email': 'joao@gmail.com',
            'endereco': 'Rua das Flores, 123',
            'cidade': 'São Paulo',
            'observacoes': 'Cliente VIP'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        cliente_emp1 = Cliente.query.filter_by(nif='123.456.789-00').first()
        self.assertIsNotNone(cliente_emp1)
        self.assertEqual(cliente_emp1.empresa_id, self.emp1.id)
        cliente_id = cliente_emp1.id
        
        self.logout()
        self.login('roberto@beta.com', 'senha123')
        
        res_index = self.client.get('/clientes/')
        self.assertNotIn(b"123.456.789-00", res_index.data)
        
        res_detalhes = self.client.get(f'/clientes/{cliente_id}')
        self.assertEqual(res_detalhes.status_code, 404)
        
        res_edit = self.client.post(f'/clientes/{cliente_id}/editar', data={'nome': 'Hacker', 'nif': '123'}, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 404)

    def test_veiculos_crud_and_link_cliente(self):
        self.login('carlos@alpha.com', 'senha123')
        
        self.client.post('/clientes/novo', data={
            'nome': 'Maria Oliveira',
            'nif': '987.654.321-11'
        }, follow_redirects=True)
        
        cliente = Cliente.query.filter_by(nif='987.654.321-11').first()
        cliente_id = cliente.id

        res = self.client.post('/veiculos/novo', data={
            'cliente_id': cliente_id,
            'placa': 'ABC-1234',
            'marca': 'Toyota',
            'modelo': 'Corolla XEi 2.0',
            'ano_fabricacao': 2022,
            'ano_modelo': 2023,
            'cor': 'Prata',
            'combustivel': 'Flex',
            'km_atual': 35000
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        veiculo = Veiculo.query.filter_by(placa='ABC-1234').first()
        self.assertIsNotNone(veiculo)
        self.assertEqual(veiculo.cliente_id, cliente_id)
        self.assertEqual(veiculo.empresa_id, self.emp1.id)

    def test_pecas_estoque_margin_and_alerts(self):
        self.login('carlos@alpha.com', 'senha123')
        
        res = self.client.post('/pecas/nova', data={
            'codigo_referencia': 'FIL-001',
            'descricao': 'Filtro de Óleo Mann',
            'marca': 'Mann Filter',
            'unidade_medida': 'UN',
            'preco_custo': '25.00',
            'preco_venda': '50.00',
            'estoque_atual': '3',
            'estoque_minimo': '10',
            'localizacao': 'Prateleira A1'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        peca = Peca.query.filter_by(codigo_referencia='FIL-001').first()
        self.assertIsNotNone(peca)
        self.assertEqual(peca.preco_custo, 25.0)
        self.assertEqual(peca.preco_venda, 50.0)
        self.assertTrue(peca.estoque_baixo)

    def test_servicos_crud(self):
        self.login('carlos@alpha.com', 'senha123')
        
        res = self.client.post('/servicos/novo', data={
            'descricao': 'Alinhamento 3D e Balanceamento',
            'categoria': 'Geometria',
            'preco_padrao': '140.00',
            'tempo_estimado_minutos': '45'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        srv = Servico.query.filter_by(descricao='Alinhamento 3D e Balanceamento').first()
        self.assertIsNotNone(srv)
        self.assertEqual(srv.preco_padrao, 140.0)
        self.assertEqual(srv.tempo_estimado_minutos, 45)

if __name__ == '__main__':
    unittest.main()
